# Changelog

This document tracks releases across all plugins in the Starsim-AI repository.

## starsim-ai v1.5 (2026.08.28)
- Skills updated from Starsim v3.4.0 to **v3.6.0**:
  - `starsim-dev-random`: `ss.options.single_rng` was removed in v3.5.0; documented `ss.options.crn` (note the reversed polarity) and when disabling CRN is defensible.
  - `starsim-dev-networks`: `ss.RandomNet` is now fast and approximate; documented `ss.RandomExactNet` (exact degree) and `ss.RandomSafeNet` (CRN-safe) and when to pick each.
  - `starsim-dev-diseases`: `ss.SEIR` is now built in, so the hand-rolled SEIR example was replaced with an SIRS/waning-immunity one. Added the infected/infectious distinction, the `set_infection()`/`set_progression()` split, `define_aliases()`, `plot_states`, and the `ss.library` namespace.
  - `starsim-dev-time`: `float()` on a timepar now raises; documented `.value`/`.years`/`.to_dt()`, rate conversion with `.to()`, and the `ss.prob` cross-unit conversion fix.
  - `starsim-dev-sim` and `starsim-dev-profiling`: added `people_results=False`, `sim.run(profile=True)`, and `People.n_alive` vs `len(people)` (the pre-v3.6.0 `prevalence` understatement).
  - `starsim-dev-indexing`: `ss.uids()` now rejects non-integers; added `ss.Arr.isin()`.
  - `starsim-dev-demographics`: `ss.Births` accepts a `Time` column; noted the `ss.Pregnancy` `slot_scale` default change.
  - `starsim-style-tests`: added guidance on regenerating regression baselines across Starsim versions.
- Removed the PostToolUse anti-pattern hook (it invoked `python3` directly, which is not portable). The anti-patterns themselves remain documented in `skills/starsim-dev/starsim-antipatterns.md` and are used by the `starsim-dev` router.

## starsim-ai v1.4 (2026.07.07)
- Anti-pattern check hook is now scoped to Starsim projects only (detected via a `starsim` import or a project manifest naming `starsim`), so it stays silent when editing unrelated Python.
- Anti-pattern matching now ignores comments and string literals, so patterns like `np.random` only trigger on real code.

## starsim-ai v1.3 (2026.06.21)
- New `starsim-dev-debugging` skill for diagnosing simulation errors, silent failures (no epidemic, wrong scale), and reproducibility issues.
- Added a PostToolUse anti-pattern check hook that flags common Starsim mistakes (e.g. `np.random`, wrong lifecycle hooks, UID-vs-position confusion) as non-blocking advisories, with an accompanying `starsim-antipatterns.md` reference.
- Added `AGENTS.md` documenting plugin conventions for agents.
- Expanded and refined many skills from user and MNCH implementation-session feedback — including indexing, interventions, calibration, distributions, time, networks, run, and sim.
- Broadened the array-indexing anti-pattern to also cover `np.asarray` wrapping.
- Softened guidance around `np.random` to recommend Starsim distributions where practical rather than prohibiting it outright.

## starsim-ai v1.2 (2026.02.25)
- 23 modeling and style skills for Starsim development.
- Sciris utilities skill.
- STIsim modeling skill.
- MCP server integration via mcp_pack.

## project-improver v1.2 (2026.03.31)
- See [plugins/project-improver/CHANGELOG.md](plugins/project-improver/CHANGELOG.md) for detailed changes.

## disease-modeling v0.1.0 (2026.02.23)
- Initial release with 7 skills from Harvard's Introduction to Infectious Disease Modeling course.
- Skills: basic_epi_modeling, sir-models, sir-elaborations, vaccination, vectors, parameter-estimation, surveillance.
