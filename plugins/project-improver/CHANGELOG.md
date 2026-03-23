# Changelog

This document tracks updates to the Project-Improver plugin.

## Version v1.1_2026.03.23
- Fixed tier numbering throughout to match guidelines: Tier 1 = library/DPG (most requirements), Tier 3 = one-off/exploratory (fewest requirements).
- Updated scoring schema: swapped tier1/tier3 rubric blocks and corrected `na_for_tiers` from `[1]` to `[3]` for `powerful` and `accessible` metrics.
- Added "no magic numbers" (explicit assumptions with sources) to the `correct` metric rubric and quality-scorer agent checklist.
- Added parallelization of slow (>30s) tasks to the `performant` metric rubric and usability-scorer agent checklist.
- Added style guide compliance and documentation of approach tradeoffs to the `documented` metric rubric and usability-scorer agent checklist.

## Version 0.1.0 (2026.03.19)
- Initial version.