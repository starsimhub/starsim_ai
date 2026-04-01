---
name: Project Scorer
description: The Project Scorer skill scores a software project against IDM engineering quality tiers (1–3) across quality, usability, and safety metrics. Use this skill when the user asks to "score my project", "check engineering quality", "evaluate code quality", "assess tier compliance", "run project scorer", or invokes /project-improver:project-scorer. Also use proactively when the user says "how good is this code?" or "what improvements does this project need?".
argument-hint: "[project_path_or_github_url] [tier]"
allowed-tools: Read, Glob, Grep, Bash, Write, Agent, WebFetch
---

Score a software project against the IDM engineering quality guidelines and write an `engineering_score.md` report.

Skill version: 1.2_2026.03.31

## Step 0: Record Start Time

Before doing anything else, run the following bash command and save the result as `START_EPOCH`:

```bash
date +%s
```

This will be used in Step 7 to compute elapsed time.

## Step 1: Parse Arguments

The user provides two arguments:
- **project**: path to a local directory OR a GitHub URL (e.g., `https://github.com/org/repo`). Default: current working directory.
- **tier**: integer 1, 2, or 3. Default: 2.

**Tier definitions (brief)**:
- Tier 1: Software library or DPG used by many people for many years
- Tier 2: Small-scale project used by multiple people or projects
- Tier 3: One-off/exploratory code used by one person

**If a GitHub URL is given**: Use `gh repo clone <url> /tmp/project-scorer-$(date +%s)` to clone to a temporary directory. Set `project` to that path.

## Step 2: Read the Scoring Schema

Read the full schema from:
`$CLAUDE_PLUGIN_ROOT/skills/project-scorer/scoring-schema.yaml`

This file contains:
- Category weights (quality 40%, usability 40%, safety 20%)
- Per-metric weights within each category
- Tier-specific rubrics with 0/mid/10 anchor descriptions
- N/A metrics for each tier (Tier 3: `powerful` and `accessible` are N/A)

## Step 3: Dispatch Sub-Agents in Parallel

Launch all three agents **simultaneously** using the Agent tool with `subagent_type: "general-purpose"`:

### quality-scorer prompt:
```
You are the quality-scorer agent for the project-improver plugin.

Project path: <project>
Tier: <tier>

Score the three QUALITY metrics for this project: correct, clear, concise.

Metric weights (within-category, for JSON output):
- correct: 7 (fail_on_serious: true — set score=0, failed=true if serious scientific bugs or fundamental correctness issues found)
- clear: 2
- concise: 1

Tier <tier> rubric for quality (from IDM scoring schema):
<paste the tier's quality rubric from the schema here>

Instructions:
1. Explore the project: read key source files, check for tests, inspect structure, naming, docstrings, code organization, duplication. Determine the main programming language(s) used.
2. Run e.g. `find <project> -name "*.py"` to discover files for a project in Python.
3. Check for test files: look for test_*.py, *_test.py, tests/ directory, testthat/ for R. Check if tests are clear enough to double as documentation.
4. For Tier 1: check for CI/CD config (.github/workflows/, .travis.yml, etc.).
5. For Tier 1: check whether code is hard to misuse (correct usage is easiest; incorrect usage raises warnings).
6. Look for obvious bugs, scientific errors, or suspicious logic. Check for evidence of peer review or validation.
7. Score each metric as an integer 0–10.

Return ONLY a JSON object (no other text):
{
  "correct": {"score": <int>, "weight": 7, "reason": "<1-2 concrete sentences>"},
  "clear":   {"score": <int>, "weight": 2, "reason": "<1-2 concrete sentences>"},
  "concise": {"score": <int>, "weight": 1, "reason": "<1-2 concrete sentences>"},
  "failed":  <true if serious correctness issue found, else false>
}
```

### usability-scorer prompt:
```
You are the usability-scorer agent for the project-improver plugin.

Project path: <project>
Tier: <tier>

Score the five USABILITY metrics: simple, powerful, performant, documented, accessible.

Metric weights (within-category, for JSON output):
- simple: 3
- powerful: 2  (N/A for Tier 3 — omit from JSON if tier=3)
- performant: 2
- documented: 2
- accessible: 1  (N/A for Tier 3 — omit from JSON if tier=3)

Tier <tier> rubric for usability (from IDM scoring schema):
<paste the tier's usability rubric from the schema here>

Instructions:
1. Explore the project: read README files, check for tutorials/docs, inspect public UIs (scripts/classes/functions — main entry points, function signatures, defaults), look for error handling.
2. Check if it is clear what UIs the user is supposed to interact with.
3. Check for docstrings on public functions/classes — do they include runnable examples?
4. Check for obvious performance anti-patterns (nested loops over large arrays, no vectorization). Check if algorithms are appropriate for their tasks.
5. For accessible: check if code is on GitHub (public if possible), look for LICENSE file, check setup.py/pyproject.toml/DESCRIPTION for installability.
6. Score each non-N/A metric as an integer 0–10. Omit N/A metrics entirely.

Return ONLY a JSON object (no other text). Include only non-N/A metrics:
{
  "simple":     {"score": <int>, "weight": 3, "reason": "<1-2 concrete sentences>"},
  "powerful":   {"score": <int>, "weight": 2, "reason": "<1-2 concrete sentences>"},  // omit if N/A
  "performant": {"score": <int>, "weight": 2, "reason": "<1-2 concrete sentences>"},
  "documented": {"score": <int>, "weight": 2, "reason": "<1-2 concrete sentences>"},
  "accessible": {"score": <int>, "weight": 1, "reason": "<1-2 concrete sentences>"}   // omit if N/A
}
```

### safety-scorer prompt:
```
You are the safety-scorer agent for the project-improver plugin.

Project path: <project>
Tier: <tier>

Score the two SAFETY metrics: compliant, reproducible.

Metric weights (within-category, for JSON output):
- compliant: 6  (fail_on_serious: true — set score=0, failed=true if serious violations found)
- reproducible: 4

Tier <tier> rubric for safety (from IDM scoring schema):
<paste the tier's safety rubric from the schema here>

Instructions:
1. Check for exposed secrets: scan for .env files, hardcoded API keys/tokens/passwords using grep patterns like (api_key|secret|password|token)\s*=\s*['\"][^'"]{8,}.
2. Check for LICENSE file and identify license type.
3. Inspect dependency files (pyproject.toml, DESCRIPTION, requirements.txt, setup.py, renv.lock) for restrictive licenses (GPL, AGPL, proprietary).
4. Check dependency specification: are dependencies specified in pyproject.toml or DESCRIPTION? Are versions pinned?
5. Check random seed handling: if random numbers are used, do same seeds give identical results?
6. For Tier 1 and 2: check version control — git tags, semantic versioning.
7. For Tier 1: check if package is on PyPI/CRAN, look for CHANGELOG.
8. Score each metric as an integer 0–10.

Return ONLY a JSON object (no other text):
{
  "compliant":    {"score": <int>, "weight": 6, "reason": "<1-2 concrete sentences>"},
  "reproducible": {"score": <int>, "weight": 4, "reason": "<1-2 concrete sentences>"},
  "failed": <true if serious compliance violation found, else false>
}
```

**Important**: Before dispatching, replace `<project>`, `<tier>`, and `<paste ... rubric here>` with actual values from Step 1 and Step 2.

## Step 4: Compute Overall Score

After all three agents return results, calculate:

```python
# Within-category scores (0-10 each)
quality_weights = {"correct": 7, "clear": 2, "concise": 1}
usability_weights = {"simple": 3, "powerful": 2, "performant": 2, "documented": 2, "accessible": 1}
safety_weights = {"compliant": 6, "reproducible": 4}

# For N/A metrics (omitted from JSON): exclude from both numerator and denominator
quality_raw    = sum(score * w for m, w in quality_weights.items()   if m in quality_results)   / sum(w for m, w in quality_weights.items()   if m in quality_results)
usability_raw  = sum(score * w for m, w in usability_weights.items() if m in usability_results) / sum(w for m, w in usability_weights.items() if m in usability_results)
safety_raw     = sum(score * w for m, w in safety_weights.items()    if m in safety_results)    / sum(w for m, w in safety_weights.items()    if m in safety_results)

# Category scores out of 100 (for the summary table)
quality_score   = round(quality_raw   * 10)
usability_score = round(usability_raw * 10)
safety_score    = round(safety_raw    * 10)

# Overall score: category weights are 40%, 40%, 20% of a 0-100 scale
overall_score = round(quality_raw * 4 + usability_raw * 4 + safety_raw * 2)
```

Set `failed: true` in the final JSON if either `quality.correct.failed` or `safety.compliant.failed` is true.

## Step 5: Assemble Full Results

Construct the result object with this exact schema:

```yaml
project: <project_path>
tier: <tier>
overall_score: <0-100>
failed: <true|false>
quality:
  correct:
    score: <0-10>
    weight: 7
    reason: "..."
  clear:
    score: <0-10>
    weight: 2
    reason: "..."
  concise:
    score: <0-10>
    weight: 1
    reason: "..."
usability:
  simple:
    score: <0-10>
    weight: 3
    reason: "..."
  powerful:
    score: <0-10>
    weight: 2
    reason: "..."
  performant:
    score: <0-10>
    weight: 2
    reason: "..."
  documented:
    score: <0-10>
    weight: 2
    reason: "..."
  accessible:
    score: <0-10>
    weight: 1
    reason: "..."
safety:
  compliant:
    score: <0-10>
    weight: 6
    reason: "..."
  reproducible:
    score: <0-10>
    weight: 4
    reason: "..."
```

Give N/A metrics (Tier 3: `powerful`, `accessible`) a score of 10.

## Step 6: Generate Recommendations

Before writing the file, synthesize 3–8 concrete, actionable recommendations ranked by impact (score × weight). Each recommendation should:
- Name the specific metric it improves
- Be specific and implementable (e.g., "Add a `tests/` directory with pytest tests for the three main functions" not "add tests")
- Note if it is quick (minutes), medium (hours), or large (days) effort
- Note if it cannot be automated (e.g., "Write a user guide" — human effort required)

## Step 7: Write engineering_score.md

Write this file to the **project directory** (not the current working directory if different).

Before writing, compute the following:
- **Date**: run `date +%Y-%m-%d` to get the current date.
- **Time spent**: run `date +%s` to get `END_EPOCH`, then compute `END_EPOCH - START_EPOCH` (recorded in Step 0). Format as an integer number of seconds.

```markdown
# Project Engineering Score

**Project**: `<project_path>`
**Tier**: <tier> (<tier name>)
**Overall Score**: <overall_score>/100
**Status**: <PASS or FAIL — FAIL if failed=true>
**Date**: <YYYY-MM-DD>
**Time spent**: <seconds>s

## Summary

| Category | Score | Weight |
| -- | -- | -- |
| Quality | <quality_score>/100 | 40% |
| Usability | <usability_score>/100 | 40% |
| Safety | <safety_score>/100 | 20% |
| **Total** | **<overall_score>/100** | 100% |

| Metric | Score | Notes |
| -- | -- | -- |
| correct | <score>/10 | <brief reason> |
| clear | <score>/10 | <brief reason> |
| concise | <score>/10 | <brief reason> |
| simple | <score>/10 | <brief reason> |
| powerful | <score>/10 | <brief reason> |
| performant | <score>/10 | <brief reason> |
| documented | <score>/10 | <brief reason> |
| accessible | <score>/10 | <brief reason> |
| compliant | <score>/10 | <brief reason> |
| reproducible | <score>/10 | <brief reason> |

<2–4 sentences plain-language summary. Mention the strongest areas and the biggest gaps.
If failed=true, clearly state which metric caused the failure and why.>

## Recommendations

<Numbered list of 3–8 recommendations, most impactful first. For each:>
1. **[Metric] — [Title]** *(effort: quick/medium/large; automated: yes/no)*
   <One concrete sentence describing exactly what to do.>

## Full Results

```yaml
<the assembled YAML>
```
```

## Notes

- **General scoring principle**: If no specific improvements can be identified for a metric, score 10/10. If scoring below 10, always list the specific improvements that would raise the score. Don't dock points for theoretical issues — only for concrete, observable problems.
- **Skip large and binary files**: Do not read files larger than 100 KB, or files with extensions `.csv`, `.pdf`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.svg`, `.ico`, `.tiff`, `.webp`. These are too large or not human-readable source code.
- If the project is very large, focus on a representative sample: main source files, entry points, README, tests, and CI config.
- For R projects: look for `DESCRIPTION`, `R/`, `tests/testthat/`, `vignettes/`, `man/` directories.
- For Python projects: look for `pyproject.toml`, `setup.py`, `src/`, `tests/`, `.github/`.
- Scientific correctness (quality.correct) is the most heavily weighted metric (28/100 points). Pay particular attention to this.
- If `failed=true`, still complete the full report — the recommendations should include how to address the failure.
