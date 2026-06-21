#!/usr/bin/env python3
"""PostToolUse hook: flag well-known Starsim anti-patterns in edited Python.

Runs after Edit/Write/MultiEdit. Scans only the *newly written* text for the
deterministic, pattern-matchable mistakes documented in
``skills/starsim-dev/starsim-antipatterns.md``. When it finds any, it emits a
non-blocking advisory back to Claude via ``additionalContext`` so the model can
self-correct at the moment the code is written — it never blocks the edit.

Each rule's ``id`` matches a row in the anti-patterns reference; keep them in sync.
The hook is intentionally fail-open: any error, non-Python file, or absent match
results in a clean (silent) exit so it can never disrupt a normal edit.
"""

import json
import re
import sys

# (id, compiled regex, message). Ordered high-confidence first.
# `id` mirrors skills/starsim-dev/starsim-antipatterns.md.
RULES = [
    (
        "np-random",
        re.compile(r"\b(?:np|numpy)\.random\b"),
        "uses `np.random` — Starsim sampling must go through an `ss.<dist>` (e.g. "
        "`ss.normal`, `ss.bernoulli`) to use the Common Random Number stream. "
        "See starsim-dev-random / starsim-dev-distributions.",
    ),
    (
        "beta-rate",
        re.compile(r"beta\s*=\s*ss\.(?:peryear|perday)\b"),
        "wraps transmission `beta` in a rate (`ss.peryear`/`ss.perday`). `beta` is a "
        "bare per-act probability float — pass it plain (e.g. `beta=0.1`). "
        "See starsim-dev-time.",
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


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # not JSON / no input — nothing to do

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {}) or {}

    file_path = tool_input.get("file_path", "") or ""
    if not file_path.endswith(".py"):
        return

    text = extract_new_text(tool_name, tool_input)
    if not text:
        return

    findings = []
    for rule_id, pattern, message in RULES:
        if pattern.search(text):
            findings.append(f"- [{rule_id}] {message}")

    if not findings:
        return

    advisory = (
        "Starsim anti-pattern check flagged the edit to "
        f"`{file_path}`:\n" + "\n".join(findings) + "\n\nReview these before "
        "continuing; fix any that apply. (Matches may include comments/strings — "
        "use judgment.)"
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
