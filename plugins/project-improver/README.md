# Project-Improver

A Claude Code plugin that scores and improves scientific research code against the [IDM Software Engineering Quality Guidelines](https://github.com/InstituteforDiseaseModeling).

## Features

- **Project Scorer** (`/project-improver:project-scorer`): Evaluates a project across 10 metrics in three categories (quality, usability, safety) and produces a scored report with recommendations.
- **Project Fixer** (`/project-improver:project-fixer`): Reads the score report and implements prioritized, feasible improvements automatically.

## Quality Tiers

| Tier | Description | Example |
|------|-------------|---------|
| 1 | Software library | Starsim, FPsim, LASER |
| 2 | Small-scale project | A model calibrated to one country |
| 3 | One-off / exploratory | A script to plot simulation outputs |

## Scoring Metrics

| Category (weight) | Metric | Within-category weight |
|---|---|---|
| **Quality (40%)** | Correct | 70% |
| | Clear | 20% |
| | Concise | 10% |
| **Usability (40%)** | Simple | 30% |
| | Powerful | 20% |
| | Performant | 20% |
| | Documented | 20% |
| | Accessible | 10% |
| **Safety (20%)** | Compliant | 60% |
| | Reproducible | 40% |

**Failure conditions**: `quality.correct` and `safety.compliant` can trigger a FAIL (score=0) if serious violations are found (e.g., scientific bugs, exposed secrets).

## Usage

### Score a project

```
/project-improver:project-scorer                    # score current directory at tier 2
/project-improver:project-scorer . 3                # score current directory at tier 3
/project-improver:project-scorer /path/to/repo 1    # score a local path at tier 1
/project-improver:project-scorer https://github.com/org/repo 2   # score a GitHub repo
```

Output: `engineering_score.md` written to the project directory.

### Fix a project

```
/project-improver:project-fixer                     # fix current directory
/project-improver:project-fixer /path/to/repo       # fix a specific path
```

Requires `engineering_score.md` to exist (run the scorer first).

## Output Format

The scorer writes `engineering_score.md` with:
- **Summary**: plain-language overview of results
- **Recommendations**: concrete, prioritized, actionable steps
- **Full Results**: complete JSON with per-metric scores, weights, and reasons

## Installation

```bash
# From the starsim-ai marketplace: https://github.com/starsimhub/starsim_ai
# Add to .claude-plugin/marketplace.json or install via Claude Code settings
```

## Updating

1. Download the engineering quality guidelines document as `admin/engineering_quality_guidelines.md`.
2. Copy `admin/update_prompt.md` into Claude and run.