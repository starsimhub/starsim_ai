---
name: Project Fixer
description: The Project Fixer skill reads recommendations from a engineering_score.md report and implements prioritized improvements to the project. Use this skill when the user asks to "fix my project", "implement the recommendations", "improve my project score", "apply engineering fixes", or invokes /project-improver:project-fixer. Also use when the user says "now fix it" after running the project scorer.
argument-hint: "[project_path]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

Read recommendations from `engineering_score.md` and implement prioritized improvements to the project.

Skill version: 1.2_2026.03.31

## Step 1: Find and Read the Score Report

1. If the user provided a `project_path`, look for `engineering_score.md` in that directory.
2. Otherwise, look in the current working directory.
3. If the file does not exist, stop and tell the user:
   > "No `engineering_score.md` found. Please run `/project-improver:project-scorer` first to generate the report."

Read the full contents of `engineering_score.md` — particularly the **Recommendations** and **Full Results** sections.

## Step 2: Create a Prioritized Implementation Plan

Parse the recommendations and classify each as:

| Category | What it means |
|----------|---------------|
| **Can implement now** | File additions, code edits, config files, docstrings, README improvements, `.gitignore`, `LICENSE` |
| **Requires human input** | Writing tutorials, user guides, scientific validation, publishing to PyPI/CRAN, setting up CI/CD (you can scaffold, but the user must configure credentials) |
| **Cannot implement** | Fundamental redesigns, decisions about what the code should do, acquiring data licenses |

Present the plan to the user **before making any changes**:

```
## Implementation Plan

### Will implement automatically:
1. [Metric: clear] Add docstrings to 5 public functions in model.py (quick)
2. [Metric: accessible] Add MIT LICENSE file (quick)
3. [Metric: reproducible] Add version pinning to requirements.txt (quick)
4. [Metric: documented] Expand README with installation and usage sections (medium)
5. [Metric: concise] Refactor duplicated data loading code into a helper function (medium)

### Will scaffold (you complete):
6. [Metric: correct] Create tests/ directory with pytest structure and 3 example tests (medium)
   → You'll need to fill in the test logic and expected values
7. [Metric: accessible] Create pyproject.toml for pip installability (medium)
   → You'll need to fill in the project description and verify metadata

### Cannot implement (human effort required):
- [Metric: documented] Write a full tutorial notebook — requires domain knowledge
- [Metric: correct] Add CI/CD pipeline — requires GitHub repository secrets setup
- [Metric: correct] Validate scientific correctness — requires domain expert review

Estimated score improvement: +12 to +18 points (depending on test coverage achieved)

Proceed? (yes/no)
```

Wait for the user to confirm before making any changes.

## Step 3: Implement Approved Changes

Work through the "Will implement" items **one at a time**, in priority order (impact = score × weight, highest first).

### Before each change:
- State what you are about to do in one sentence
- Read the relevant file(s) before editing them

### For each type of fix:

#### Adding a LICENSE file
Use the MIT license template with the current year and repo/author name from the README or git config:
```
MIT License

Copyright (c) <year> <author>

Permission is hereby granted, free of charge, to any person obtaining a copy...
[full MIT text]
```

#### Adding/improving docstrings (Python)
Follow NumPy/Google docstring style. For a function:
```python
def function_name(param1, param2):
    """Short one-line description.

    Parameters
    ----------
    param1 : type
        Description of param1.
    param2 : type
        Description of param2.

    Returns
    -------
    type
        Description of return value.
    """
```

#### Adding/improving docstrings (R)
Use roxygen2 style:
```r
#' Short one-line description.
#'
#' @param param1 Description of param1.
#' @param param2 Description of param2.
#' @return Description of return value.
#' @export
#' @examples
#' result <- function_name(1, 2)
```

#### Adding version pins to requirements.txt
Read the current `requirements.txt`. For each unpinned dependency (e.g., `numpy`), add a lower-bound pin based on the current commonly-used version. Use `>=` not `==` to avoid over-pinning:
```
numpy>=1.24
pandas>=2.0
scipy>=1.11
```

#### Scaffolding a test file (Python)
Create `tests/test_<module>.py`:
```python
"""Tests for <module>."""
import pytest
# TODO: import from your module
# from mymodule import MyClass, my_function


class TestMyFunction:
    """Tests for my_function."""

    def test_basic(self):
        """TODO: Test basic expected behavior."""
        # result = my_function(...)
        # assert result == expected
        pass

    def test_edge_case(self):
        """TODO: Test edge case."""
        pass
```
Also create `tests/__init__.py` (empty) and check for a `pytest.ini` or add to `pyproject.toml`.

#### Scaffolding a pyproject.toml
```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.backends.legacy:build"

[project]
name = "<project-name>"
version = "0.1.0"  # TODO: update to current version
description = "<TODO: one-line description>"
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.9"
dependencies = [
    # TODO: list your dependencies here
]

[project.urls]
Repository = "<TODO: GitHub URL>"
```

#### Improving README
Add missing sections. A Tier 3 (one-off) README needs at minimum:
- `## Overview` — what the project does (1–3 sentences)
- `## Installation` — how to set it up
- `## Usage` — how to run it (minimal example)

A Tier 1 and 2 README additionally needs:
- `## Requirements`
- `## Project structure` — brief description of key files/folders
- `## Contributing` (Tier 1 library)

#### Fixing code duplication
Identify the duplicate code, extract it into a well-named helper function, and replace the duplicates with calls to that function. Only refactor when it clearly improves readability — do not create unnecessary abstractions.

## Step 4: Handle Trade-offs

If implementing one recommendation would negatively impact another metric, **stop and ask the user** before proceeding:

> "Implementing [recommendation A] (e.g., adding strict type validation) would make the API less flexible, potentially lowering the `powerful` score. How would you like to proceed?
> - (a) Proceed with stricter validation (prioritize simplicity/safety)
> - (b) Skip this recommendation (preserve flexibility)
> - (c) Implement a middle ground (add validation but make it optional via a flag)"

## Step 5: Report What Was Done

After completing all feasible changes, provide a concise summary:

```
## Changes Made

✅ Added MIT LICENSE
✅ Added docstrings to 7 functions in model.py and utils.py
✅ Updated requirements.txt with version pins
✅ Expanded README with Installation, Usage, and Project Structure sections
✅ Scaffolded tests/test_model.py (fill in test logic to complete)

⏭ Skipped: user guide (human effort required)
⏭ Skipped: CI/CD pipeline (human effort required — see README for setup instructions)

Estimated score impact: quality.clear +2, usability.documented +2, safety.reproducible +2, usability.accessible +3

Re-run `/project-improver:project-scorer` to get an updated score.
```

## Notes

- Only make changes that are clearly safe and reversible. If a change could break existing functionality, note it and ask the user to verify.
- Do not rewrite working code just to make it "better" — focus strictly on the recommendations.
- If the project is R-based, adapt all Python-specific patterns to R equivalents.
- If the `failed` flag is `true` in the score report, prioritize the failure-causing metric first and be explicit about what was done to address it.
