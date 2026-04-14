# Starsim Plugin

A Claude Code plugin that provides Starsim and Sciris MCP tools and modeling skills.

## What's included

- **MCP servers** - Connects to the hosted Starsim and Sciris documentation servers, giving Claude access to up-to-date API docs and examples.
- **starsim-dev skills** - 16 topic-specific skills for Starsim development (diseases, networks, interventions, calibration, etc.) plus a router skill that dispatches to the right one.
- **starsim-style skills** - 4 skills covering Starsim code style, documentation, testing, and design philosophy.
- **sciris-utilities skill** - Activates when using Sciris utilities (file I/O, parallelization, data structures, etc.).
- **stisim-modeling skill** - Activates when building STIsim simulations (HIV, syphilis, chlamydia, etc.).

## Installation

Inside Claude Code, add the starsim_ai repo as a local marketplace, then install the plugin:

1. **Add the marketplace** (run inside Claude Code):
   ```
   /plugin marketplace add /path/to/starsim_ai
   ```

2. **Install the plugin** (run inside Claude Code):
   ```
   /plugin install starsim-ai
   ```

   Or use the interactive UI — run `/plugin`, go to the **Discover** tab, and install from there.

3. **Verify** — run `/mcp` to confirm the `starsim` and `sciris` MCP servers are listed.

## Plugin structure

```
plugins/starsim/
├── .claude-plugin/
│   └── plugin.json                  # Plugin manifest
├── .claude/
│   └── settings.local.json          # Plugin settings
├── .mcp.json                        # MCP server definitions (context7)
├── skills/
│   ├── starsim-dev/
│   │   └── SKILL.md                 # Dev router — dispatches to topic skills
│   ├── starsim-dev-intro/
│   │   └── SKILL.md                 # Getting started and architecture
│   ├── starsim-dev-sim/
│   │   └── SKILL.md                 # Sim, People, and parameters
│   ├── starsim-dev-diseases/
│   │   └── SKILL.md                 # Disease models (SIR, SIS, SEIR, etc.)
│   ├── starsim-dev-networks/
│   │   └── SKILL.md                 # Contact networks and mixing pools
│   ├── starsim-dev-demographics/
│   │   └── SKILL.md                 # Births, deaths, pregnancy
│   ├── starsim-dev-interventions/
│   │   └── SKILL.md                 # Vaccination, screening, treatment
│   ├── starsim-dev-connectors/
│   │   └── SKILL.md                 # Disease-disease interactions
│   ├── starsim-dev-analyzers/
│   │   └── SKILL.md                 # Custom result collection
│   ├── starsim-dev-distributions/
│   │   └── SKILL.md                 # Probability distributions
│   ├── starsim-dev-calibration/
│   │   └── SKILL.md                 # Model calibration (Optuna, Bayesian)
│   ├── starsim-dev-run/
│   │   └── SKILL.md                 # MultiSim, parallel runs, scenarios
│   ├── starsim-dev-time/
│   │   └── SKILL.md                 # Dates, durations, rates
│   ├── starsim-dev-indexing/
│   │   └── SKILL.md                 # Arrays, UIDs, agent indexing
│   ├── starsim-dev-random/
│   │   └── SKILL.md                 # Common random numbers, reproducibility
│   ├── starsim-dev-nonstandard/
│   │   └── SKILL.md                 # Compartmental/ODE and general ABMs
│   ├── starsim-dev-profiling/
│   │   └── SKILL.md                 # Performance profiling and debugging
│   ├── starsim-style-python/
│   │   └── SKILL.md                 # Python code style
│   ├── starsim-style-docs/
│   │   └── SKILL.md                 # Documentation style
│   ├── starsim-style-philosophy/
│   │   └── SKILL.md                 # Design philosophy
│   ├── starsim-style-tests/
│   │   └── SKILL.md                 # Testing conventions
│   ├── sciris-utilities/
│   │   └── SKILL.md                 # Sciris utility guidance
│   └── stisim-modeling/
│       └── SKILL.md                 # STI disease modeling
└── README.md
```
