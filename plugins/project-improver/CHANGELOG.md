# Changelog

This document tracks updates to the Project-Improver plugin.

## Version 1.2 (2026.03.31)
- Synced with engineering quality guidelines v1.2 (2026.03.26).
- Terminology: "APIs" → "UIs" (scripts/classes/functions) throughout skills, agents, and scoring schema.
- Quality.correct: added peer review, tests-as-documentation, and misuse prevention to Tier 1 rubric and quality-scorer agent checklist.
- Quality.concise: added nuance about not introducing large dependencies for trivial savings; minimal duplication now Tier 1 only.
- Usability.simple: removed "clear what UIs to interact with" (moved to documented).
- Usability.powerful: added composition concept alongside subclassing; minor rewordings.
- Usability.performant: reordered rubric (algorithms first); added "frequently run" qualifier to parallelization.
- Usability.documented: restructured — "clear what UIs to interact with" now first item; "runnable examples" in docstrings; docs for multiple expertise levels.
- Usability.accessible: reordered; AI optimization now Tier 1 only.
- Safety.reproducible: reordered priorities — dependencies first, seeds second, semantic versioning third, PyPI/CRAN fourth.
- Tier 3: clear now requires "author and at least one other person"; reproducible adds "(except data in some cases)".
- Tier 2: updated documented rubric to include "clear what UIs to use"; updated reproducible rubric for seeds and versioning.

## Version 1.1 (2026.03.23)
- Fixed tier numbering throughout to match guidelines: Tier 1 = library/DPG (most requirements), Tier 3 = one-off/exploratory (fewest requirements).
- Updated scoring schema: swapped tier1/tier3 rubric blocks and corrected `na_for_tiers` from `[1]` to `[3]` for `powerful` and `accessible` metrics.
- Added "no magic numbers" (explicit assumptions with sources) to the `correct` metric rubric and quality-scorer agent checklist.
- Added parallelization of slow (>30s) tasks to the `performant` metric rubric and usability-scorer agent checklist.
- Added style guide compliance and documentation of approach tradeoffs to the `documented` metric rubric and usability-scorer agent checklist.

## Version 0.1 (2026.03.19)
- Initial version.