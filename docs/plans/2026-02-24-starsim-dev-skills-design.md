# Design: Starsim Development Skills

**Date:** 2026-02-24
**Status:** Approved

## Goal

Create 16 practical reference skills for the Starsim plugin, each distilled from Starsim's tutorial and user guide notebooks. Skills are optimized for Claude Code to generate correct Starsim Python code.

## Decisions

- **Content style:** Reference-style (pattern-based, not tutorial narrative)
- **Word target:** ~3000 words per skill (flexible based on topic depth)
- **Existing skill:** Rename `starsim-modeling` to `starsim-dev` as a lightweight dispatcher/index
- **Location:** `plugins/starsim/skills/<skill-name>/SKILL.md`

## File Structure

```
plugins/starsim/skills/
  starsim-dev/SKILL.md              # Dispatcher (renamed from starsim-modeling)
  starsim-dev-intro/SKILL.md        # 1
  starsim-dev-sim/SKILL.md          # 2
  starsim-dev-demographics/SKILL.md # 3
  starsim-dev-diseases/SKILL.md     # 4
  starsim-dev-networks/SKILL.md     # 5
  starsim-dev-interventions/SKILL.md# 6
  starsim-dev-analyzers/SKILL.md    # 7
  starsim-dev-connectors/SKILL.md   # 8
  starsim-dev-run/SKILL.md          # 9
  starsim-dev-calibration/SKILL.md  # 10
  starsim-dev-distributions/SKILL.md# 11
  starsim-dev-indexing/SKILL.md     # 12
  starsim-dev-nonstandard/SKILL.md  # 13
  starsim-dev-profiling/SKILL.md    # 14
  starsim-dev-random/SKILL.md       # 15
  starsim-dev-time/SKILL.md         # 16
```

## Skill Template

Each SKILL.md follows this structure:

```markdown
---
name: starsim-dev-<topic>
description: Use when <specific trigger condition>
---

# <Topic Title>

<2-3 sentence practical summary>

## Key classes

| Class | Purpose | Key parameters |
|-------|---------|---------------|
| `ss.X` | ... | `param1`, `param2` |

## Patterns

### Pattern: <Common task>
` ` `python
# Working code example
` ` `

## Anti-patterns

` ` `python
# WRONG: explanation
bad_code()

# RIGHT: explanation
good_code()
` ` `

## Quick reference
- `ss.X.method()` — what it does
```

Not every section is required for every skill. Sections scale to topic complexity.

## Dispatcher Skill (starsim-dev)

The renamed `starsim-dev/SKILL.md` serves as an index that routes to specialized skills:

- Lightweight (~200 words)
- Table mapping topics to skill names and trigger conditions
- Retains the minimal SIR example from the original skill
- Broad description triggers it for any general Starsim question

## Source Notebook Mapping

| # | Skill | Source notebooks |
|---|-------|-----------------|
| 1 | starsim-dev-intro | tutorials/t1_intro.ipynb, tutorials/t2_model.ipynb, user_guide/basics_model.ipynb |
| 2 | starsim-dev-sim | user_guide/basics_sim.ipynb, user_guide/basics_people.ipynb, user_guide/basics_parameters.ipynb |
| 3 | starsim-dev-demographics | tutorials/t3_demographics.ipynb, user_guide/modules_demographics.ipynb |
| 4 | starsim-dev-diseases | tutorials/t4_diseases.ipynb, user_guide/modules_diseases.ipynb |
| 5 | starsim-dev-networks | tutorials/t5_networks.ipynb, user_guide/modules_networks.ipynb |
| 6 | starsim-dev-interventions | tutorials/t6_interventions.ipynb, user_guide/modules_interventions.ipynb |
| 7 | starsim-dev-analyzers | user_guide/modules_analyzers.ipynb |
| 8 | starsim-dev-connectors | user_guide/modules_connectors.ipynb |
| 9 | starsim-dev-run | user_guide/workflows_run.ipynb |
| 10 | starsim-dev-calibration | user_guide/workflows_calibration.ipynb, user_guide/workflows_sir_calibration.ipynb |
| 11 | starsim-dev-distributions | user_guide/advanced_distributions.ipynb |
| 12 | starsim-dev-indexing | user_guide/advanced_indexing.ipynb |
| 13 | starsim-dev-nonstandard | user_guide/advanced_nonstandard.ipynb |
| 14 | starsim-dev-profiling | user_guide/advanced_profiling.ipynb |
| 15 | starsim-dev-random | user_guide/advanced_random.ipynb |
| 16 | starsim-dev-time | user_guide/advanced_time.ipynb |

## Implementation Approach

For each skill:
1. Read the source notebook(s)
2. Extract: classes, parameters, working code patterns, common pitfalls
3. Distill into the reference-style template
4. Write to `plugins/starsim/skills/<name>/SKILL.md`

Skills can be written in parallel batches since they are independent.

The dispatcher skill (`starsim-dev`) is written last, after all 16 skills exist, so the routing table accurately reflects the descriptions.
