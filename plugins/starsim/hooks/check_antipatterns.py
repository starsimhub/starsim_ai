#!/usr/bin/env python3
"""PostToolUse hook: flag well-known Starsim anti-patterns in edited Python.

Runs after Edit/Write/MultiEdit. Scans only the *newly written* text for the
deterministic, pattern-matchable mistakes documented in
``skills/starsim-dev/starsim-antipatterns.md``. When it finds any, it emits a
non-blocking advisory back to Claude via ``additionalContext`` so the model can
self-correct at the moment the code is written — it never blocks the edit.

The hook is deliberately narrow so it only speaks up when relevant:

* **Scoped to Starsim projects.** It stays silent unless the edited file
  imports ``starsim`` or sits under a project manifest that names ``starsim``
  as a dependency — so editing unrelated Python elsewhere never triggers it.
* **Scoped to real code.** Comments and string literals are blanked out before
  matching, so an anti-pattern mentioned in a docstring or ``# comment`` does
  not fire.

Each rule's ``id`` matches a row in the anti-patterns reference; keep them in sync.
The hook is intentionally fail-open: any error, non-Python file, or absent match
results in a clean (silent) exit so it can never disrupt a normal edit.
"""

import io
import json
import os
import re
import sys
import tokenize

# (id, compiled regex, message). Ordered high-confidence first.
# `id` mirrors skills/starsim-dev/starsim-antipatterns.md.
RULES = [
    (
        "np-random",
        re.compile(r"\b(?:np|numpy)\.random\b"),
        "uses `np.random` — prefer routing Starsim sampling through an `ss.<dist>` (e.g. "
        "`ss.normal`, `ss.bernoulli`) where possible, to use the Common Random Number stream. "
        "See starsim-dev-random / starsim-dev-distributions.",
    ),
    (
        "beta-rate",
        re.compile(r"beta\s*=\s*ss\.(?:peryear|perday)\b"),
        "wraps transmission `beta` in a rate (`ss.peryear`/`ss.perday`). For the typical "
        "contact-network case `beta` is a bare per-contact probability — pass it plain "
        "(e.g. `beta=0.1`); a rate is only appropriate for a non-contact-based transmission "
        "route. Verify which you have. See starsim-dev-time.",
    ),
    (
        "old-initialize",
        re.compile(r"def\s+initialize\s*\(\s*self\s*,\s*sim\b"),
        "defines `initialize(self, sim)` — that lifecycle hook is wrong. Override "
        "`init_post(self)` for post-init setup. See starsim-dev-interventions / "
        "starsim-dev-diseases.",
    ),
    (
        "sim-t-ti",
        re.compile(r"\bself\.sim\.t\.ti\b"),
        "reads `self.sim.t.ti` — inside a module use `self.ti` instead. "
        "See starsim-dev-sim.",
    ),
    (
        "where-uids",
        re.compile(r"\bnp\.where\s*\("),
        "uses `np.where(...)` — if this selects agents in a boolean state, it returns "
        "positions, not UIDs. Use `state.uids` instead. See starsim-dev-indexing.",
    ),
    (
        "hasattr-getattr",
        re.compile(r"\b(?:hasattr|getattr)\s*\("),
        "uses `hasattr`/`getattr` — Starsim style prefers `isinstance(...)` and "
        "`people['x']` / `module['x']` dict access. See starsim-style-python.",
    ),
]


def extract_new_text(tool_name, tool_input):
    """Return the text that was newly written by this tool call."""
    if tool_name == "Write":
        return tool_input.get("content", "") or ""
    if tool_name == "Edit":
        return tool_input.get("new_string", "") or ""
    if tool_name == "MultiEdit":
        return "\n".join(
            e.get("new_string", "") or "" for e in tool_input.get("edits", [])
        )
    return ""


_IMPORT_RE = re.compile(r"^\s*(?:import\s+starsim|from\s+starsim\b)", re.M)
_MANIFESTS = ("pyproject.toml", "setup.cfg", "setup.py", "requirements.txt")


def is_starsim_context(file_path, cwd):
    """True if the edit is part of a Starsim project.

    Checks, in order: does the edited file import ``starsim``; then does any
    project manifest (``pyproject.toml`` etc.) walking up from the file — or the
    working directory — name ``starsim``. Silent (False) when no signal is found,
    which is the point: the hook should only speak up on Starsim code.
    """
    # 1. Strongest signal: the file itself imports starsim. Read from disk —
    #    PostToolUse runs after the write, so the full file (not just the diff)
    #    is available, which matters for Edits that don't touch the import line.
    try:
        with open(file_path, encoding="utf-8") as f:
            if _IMPORT_RE.search(f.read()):
                return True
    except Exception:
        pass

    # 2. Walk up from the file's directory (and cwd) for a manifest naming starsim.
    start_dirs = []
    for p in (file_path, cwd):
        if not p:
            continue
        p = os.path.abspath(p)
        start_dirs.append(os.path.dirname(p) if os.path.splitext(p)[1] else p)

    seen = set()
    for d in start_dirs:
        while d and d not in seen:
            seen.add(d)
            for m in _MANIFESTS:
                mp = os.path.join(d, m)
                if os.path.isfile(mp):
                    try:
                        with open(mp, encoding="utf-8") as f:
                            if re.search(r"\bstarsim\b", f.read(), re.I):
                                return True
                    except Exception:
                        pass
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    return False


def strip_noncode(text):
    """Blank out comments and string literals so matches only hit real code.

    Token spans are overwritten with spaces in place (newlines preserved) so
    code positions are unchanged and patterns like ``np.random`` still match.
    Falls back to a naive line-comment strip if the fragment won't tokenize.
    """
    try:
        line_start = [0]
        for ln in text.splitlines(keepends=True):
            line_start.append(line_start[-1] + len(ln))

        def offset(row, col):
            return line_start[row - 1] + col

        buf = list(text)
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            name = tokenize.tok_name[tok.type]
            if tok.type in (tokenize.COMMENT, tokenize.STRING) or name.startswith("FSTRING"):
                s = offset(tok.start[0], tok.start[1])
                e = offset(tok.end[0], tok.end[1])
                for i in range(s, min(e, len(buf))):
                    if buf[i] != "\n":
                        buf[i] = " "
        return "".join(buf)
    except Exception:
        return "\n".join(line.split("#", 1)[0] for line in text.splitlines())


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # not JSON / no input — nothing to do

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}
    cwd = payload.get("cwd", "") or ""

    file_path = tool_input.get("file_path", "") or ""
    if not file_path.endswith(".py"):
        return

    # Scope to Starsim projects only — stay silent on unrelated Python.
    if not is_starsim_context(file_path, cwd):
        return

    text = extract_new_text(tool_name, tool_input)
    if not text:
        return

    # Scope to real code — don't match anti-patterns named in comments/strings.
    text = strip_noncode(text)

    findings = []
    for rule_id, pattern, message in RULES:
        if pattern.search(text):
            findings.append(f"- [{rule_id}] {message}")

    if not findings:
        return

    advisory = (
        "Starsim anti-pattern check flagged the edit to "
        f"`{file_path}`:\n" + "\n".join(findings) + "\n\nReview these before "
        "continuing; fix any that apply."
    )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": advisory,
                }
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open — never disrupt an edit
