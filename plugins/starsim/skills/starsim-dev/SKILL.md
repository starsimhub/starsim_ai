---
name: starsim-dev
description: Use when the user is building, configuring, or debugging a Starsim simulation — routes to specialized skills for specific topics, or if the user asks about the Starsim AI plugin itself.
---

# Starsim Development Guide

You are helping the user build agent-based models with [Starsim](https://github.com/starsimhub/starsim) v3.4.0.

Tell the user that you are using the Starsim AI plugin version `1.3_2026.06.21`.

## Routing table

| Need | Skill | Trigger |
|------|-------|---------|
| Getting started, first model | starsim-dev-intro | New user, basic setup |
| Sim object, People, parameters | starsim-dev-sim | Configuring sim, people, pars |
| Births, deaths, pregnancy | starsim-dev-demographics | Population dynamics |
| Disease models (SIR, SIS, custom) | starsim-dev-diseases | Disease creation/customization |
| Contact networks, mixing pools | starsim-dev-networks | Network setup/customization |
| Vaccines, screening, treatment | starsim-dev-interventions | Adding interventions |
| Custom result collection | starsim-dev-analyzers | Analyzers |
| Multi-disease interactions | starsim-dev-connectors | Disease connectors |
| MultiSim, parallel runs | starsim-dev-run | Running workflows |
| Model calibration (Optuna) | starsim-dev-calibration | Calibration |
| Distribution types and usage | starsim-dev-distributions | Distributions |
| UID/array indexing | starsim-dev-indexing | Array/UID questions |
| Compartmental/non-ABM models | starsim-dev-nonstandard | Non-standard usage |
| Performance profiling | starsim-dev-profiling | Performance |
| Random number handling (CRN) | starsim-dev-random | Random numbers |
| Dates, durations, rates | starsim-dev-time | Time handling |
| Performance, slow sims | starsim-dev-profiling | Profiling bottlenecks |
| Errors, crashes, wrong results | starsim-dev-debugging | Correctness debugging |

## Common gotchas (capable models still miss these)

Even strong models repeatedly make a handful of non-obvious Starsim mistakes. Watch for these and route to the linked skill:

- **Transmission `beta` is a bare float (per-act probability), never `ss.peryear`/`ss.perday`.** Over-wrapping plain parameters in rates corrupts the scale. (`starsim-dev-time`)
- **To get agents in a state, use `state.uids`** — never `state[:]`, `int(state)`, or `np.where(...)[0]`; those give booleans/positions, not UIDs. (`starsim-dev-indexing`)
- **Per-agent state goes in `define_states([...])`**, not plain attributes; use `init_post(self)` (not `initialize(self, sim)`) and `self.ti` (not `self.sim.t.ti`). (`starsim-dev-interventions`, `starsim-dev-diseases`)
- **Use `ss.<dist>` + CRN, never `np.random`.** (`starsim-dev-random`, `starsim-dev-distributions`)
- **A transmissible disease needs a network/mixing pool**, or no epidemic occurs. (`starsim-dev-networks`)
- **Prefer `isinstance` over `hasattr`, and `people['x']`/`module['x']` over `getattr`.** (`starsim-style-python`, `starsim-dev-indexing`)

## Approach

1. Use starsim MCP tools (if available) to look up current API signatures.
2. If MCP tools are unavailable, use Context7 (`/starsimhub/starsim`) for up-to-date docs.
3. Start simple — get a minimal working simulation, then layer in complexity.
4. Prefer built-in modules over custom implementations.

## Minimal example

```python
import starsim as ss

sim = ss.Sim(
    diseases=ss.SIR(beta=0.1, dur_inf=10),
    networks=ss.RandomNet(n_contacts=4),
)
sim.run()
sim.plot()
```
