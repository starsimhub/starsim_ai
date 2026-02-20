---
name: starsim-modeling
description: Use when the user is building, configuring, or debugging a Starsim simulation — including defining diseases, networks, interventions, demographics, analyzers, or connectors.
version: 0.1.0
---

# Starsim Modeling

You are helping the user build agent-based disease models with [Starsim](https://github.com/starsimhub/starsim).

## When to activate

- User asks to create or modify a `ss.Sim`, `ss.Disease`, `ss.Network`, `ss.Intervention`, or related class
- User asks about Starsim parameters, modules, or simulation structure
- User is debugging a Starsim model run or output

## Key concepts

- **Sim**: The top-level simulation container (`ss.Sim`). Accepts `diseases`, `networks`, `demographics`, `interventions`, `analyzers`, and `connectors`.
- **Diseases**: e.g. `ss.SIR`, `ss.SIS`, `ss.HIV`, `ss.Cholera`. Defined with transmission rates (`beta`) and duration parameters.
- **Networks**: Define contact structure. e.g. `ss.RandomNet`, `ss.MFNet`, `ss.EmbeddingNet`.
- **Interventions**: Modify the simulation mid-run. e.g. `ss.Vx` (vaccination), `ss.RoutineDelivery`, `ss.CampaignDelivery`.
- **Demographics**: Birth and death modules. e.g. `ss.Births`, `ss.Deaths`.
- **Analyzers**: Collect and process results. e.g. `ss.Analyzer`.
- **Connectors**: Link diseases/networks together. e.g. `ss.Connector`.

## Approach

1. Use the starsim MCP tools (if available) to look up current API signatures and examples.
2. If MCP tools are unavailable, use Context7 (`/starsimhub/starsim`) for up-to-date docs.
3. Start simple — get a minimal working simulation, then layer in complexity.
4. Prefer Starsim's built-in modules over custom implementations where possible.

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
