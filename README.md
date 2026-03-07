# Starsim-AI

This repository contains AI agents, skills, and tools for working with [Starsim](https://starsim.org), the agent-based disease modeling framework.


## Plugins

This repo contains two Claude Code plugins, installable via the built-in marketplace:

- **starsim-ai** (`plugins/starsim/`) — Starsim and Sciris MCP tools and modeling skills
- **disease-modeling** (`plugins/disease_modeling/`) — General disease modeling skills and tools

### Claude Code

To install, add this repo as a marketplace inside Claude Code:

| Method | Instructions |
|--------|-------------|
| **CLI** | Run `/plugin marketplace add https://github.com/starsimhub/starsim_ai` |
| **VS Code extension** | `/plugin` → Manage plugins → Marketplaces → Add from `https://github.com/starsimhub/starsim_ai` |

Then install either or both plugins from the **Discover** tab (`/plugin`).

### Outside of Claude Code

Although these plugins were built for Claude Code, they will work with any LLM via [OpenSkills](https://github.com/numman-ali/openskills).

## Skills

### Starsim

The **Starsim-AI** plugin includes the following skills:

| Skill | Purpose |
|-------|---------|
| [`starsim-dev`](plugins/starsim/skills/starsim-dev/SKILL.md) | Router — dispatches to topic-specific skills |
| [`starsim-dev-intro`](plugins/starsim/skills/starsim-dev-intro/SKILL.md) | Getting started with Starsim basics and architecture |
| [`starsim-dev-sim`](plugins/starsim/skills/starsim-dev-sim/SKILL.md) | Configuring the Sim object, People, and parameters |
| [`starsim-dev-diseases`](plugins/starsim/skills/starsim-dev-diseases/SKILL.md) | Creating and customizing disease models (SIR, SIS, SEIR, etc.) |
| [`starsim-dev-networks`](plugins/starsim/skills/starsim-dev-networks/SKILL.md) | Contact networks and mixing pools |
| [`starsim-dev-demographics`](plugins/starsim/skills/starsim-dev-demographics/SKILL.md) | Births, deaths, pregnancy, and population dynamics |
| [`starsim-dev-interventions`](plugins/starsim/skills/starsim-dev-interventions/SKILL.md) | Vaccination, screening, treatment, and custom interventions |
| [`starsim-dev-connectors`](plugins/starsim/skills/starsim-dev-connectors/SKILL.md) | Disease-disease interactions in multi-disease models |
| [`starsim-dev-analyzers`](plugins/starsim/skills/starsim-dev-analyzers/SKILL.md) | Custom result collection and analysis |
| [`starsim-dev-distributions`](plugins/starsim/skills/starsim-dev-distributions/SKILL.md) | Probability distributions and sampling |
| [`starsim-dev-calibration`](plugins/starsim/skills/starsim-dev-calibration/SKILL.md) | Model calibration with Optuna and Bayesian methods |
| [`starsim-dev-run`](plugins/starsim/skills/starsim-dev-run/SKILL.md) | Running multiple sims, scenarios, and parallelization |
| [`starsim-dev-time`](plugins/starsim/skills/starsim-dev-time/SKILL.md) | Dates, durations, rates, and time conversions |
| [`starsim-dev-indexing`](plugins/starsim/skills/starsim-dev-indexing/SKILL.md) | Arrays, UIDs, boolean states, and agent indexing |
| [`starsim-dev-random`](plugins/starsim/skills/starsim-dev-random/SKILL.md) | Common random numbers and reproducibility |
| [`starsim-dev-nonstandard`](plugins/starsim/skills/starsim-dev-nonstandard/SKILL.md) | Compartmental (ODE) models and general-purpose ABMs |
| [`starsim-dev-profiling`](plugins/starsim/skills/starsim-dev-profiling/SKILL.md) | Performance profiling and debugging |
| [`starsim-style-python`](plugins/starsim/skills/starsim-style-python/SKILL.md) | Python code style conventions |
| [`starsim-style-docs`](plugins/starsim/skills/starsim-style-docs/SKILL.md) | Documentation style (docstrings, READMEs, tutorials) |
| [`starsim-style-philosophy`](plugins/starsim/skills/starsim-style-philosophy/SKILL.md) | Starsim design philosophy |
| [`starsim-style-tests`](plugins/starsim/skills/starsim-style-tests/SKILL.md) | Testing conventions |
| [`sciris-utilities`](plugins/starsim/skills/sciris-utilities/SKILL.md) | Sciris utilities (file I/O, parallelization, data structures) |
| [`stisim-modeling`](plugins/starsim/skills/stisim-modeling/SKILL.md) | STIsim — STI disease modeling (HIV, syphilis, etc.) |

### Disease modeling

The **Disease-Modeling** plugin was trained on Harvard's *[Introduction to Infectious Disease Modeling](https://hsph.harvard.edu/research/communicable-disease-ccdd/resources/id-modeling/)* course. It includes the following skills:

| Skill | Purpose |
|-------|---------|
| [`basic_epi_modeling`](plugins/disease_modeling/skills/basic_epi_modeling/SKILL.md) | Foundational concepts — disease burden, transmission routes, compartmental model selection |
| [`sir-models`](plugins/disease_modeling/skills/sir-models/SKILL.md) | SIR compartmental models, R0, epidemic curves, ODE solvers |
| [`sir-elaborations`](plugins/disease_modeling/skills/sir-elaborations/SKILL.md) | SEIR, MSIR, SIRS, age structure, contact matrices, multi-strain dynamics |
| [`vaccination`](plugins/disease_modeling/skills/vaccination/SKILL.md) | Vaccination modeling — herd immunity, efficacy types, waning immunity, pulse/ring strategies |
| [`vectors`](plugins/disease_modeling/skills/vectors/SKILL.md) | Vector-borne and waterborne disease models (Ross-MacDonald, SIWR, multi-strain) |
| [`parameter-estimation`](plugins/disease_modeling/skills/parameter-estimation/SKILL.md) | Model fitting — least squares, MLE, Bayesian inference, calibration |
| [`surveillance`](plugins/disease_modeling/skills/surveillance/SKILL.md) | Surveillance data, nowcasting, forecasting, genomic epidemiology |


## MCP servers

### Automatic MCP servers

Starsim is available on [Context7](https://context7.com):

https://context7.com/starsimhub/starsim

It is also available on [GitMCP](https://gitmcp.io):

https://gitmcp.io/starsimhub/starsim


### Manual MCP usage

> [!WARNING]
> Manual MCP servers may not be up to date; GitMCP or Context7 is recommended.

Built on [mcp_pack](https://github.com/krosenfeld-IDM/mcp-pack).

Copy the following into `settings.json`, or into `mcp.json` for VS Code, Cursor, Claude, etc.:
```
    "mcp": {
        "servers": {
            "starsim": {
                "type": "sse",
                "url": "http://mcp.starsim.org:8001"
            },
            "sciris": {
                "type": "sse",
                "url": "http://mcp.starsim.org:8002"
            }
        }
    }
```

These agents should now be available to your IDE.

To use these tools in Claude Code, you can also use the following commands:
```
claude mcp add --transport sse starsim http://mcp.starsim.org:8001/sse
claude mcp add --transport sse sciris http://mcp.starsim.org:8002/sse
```

## Repo structure

- `deploy_mcp_pack`: Scripts for manually deploying the Starsim MCP server
- `internal`: Scripts used for creating the AI tools (not for the user)
- `plugins`: Claude Code skills and plugins