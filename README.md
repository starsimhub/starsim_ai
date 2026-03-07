# Starsim-AI

This repository contains AI agents, skills, and tools for working with [Starsim](https://starsim.org), the agent-based disease modeling framework.


## Plugins and skills

This repo contains two Claude Code plugins, installable via the built-in marketplace:

- **starsim-ai** (`plugins/starsim/`) — Starsim and Sciris MCP tools and modeling skills
- **disease-modeling** (`plugins/disease_modeling/`) — General disease modeling skills and tools

To install, add this repo as a marketplace inside Claude Code:

*From Claude Code CLI:*
```
/plugin marketplace add https://github.com/starsimhub/starsim_ai
```

*Or from the Claude Code extension:*
`/plugin` > Manage plugins > Marketplaces > Add from https://github.com/starsimhub/starsim_ai

Then install either plugin from the **Discover** tab (`/plugin`).

### Outside of Claude Code

Although these plugins were built for Claude Code, they will work with any LLM via [OpenSkills](https://github.com/numman-ali/openskills).

### Skills

The **starsim-ai** plugin includes the following skills:

| Skill | Purpose |
|-------|---------|
| `starsim-dev` | Router — dispatches to topic-specific skills |
| `starsim-dev-intro` | Getting started with Starsim basics and architecture |
| `starsim-dev-sim` | Configuring the Sim object, People, and parameters |
| `starsim-dev-diseases` | Creating and customizing disease models (SIR, SIS, SEIR, etc.) |
| `starsim-dev-networks` | Contact networks and mixing pools |
| `starsim-dev-demographics` | Births, deaths, pregnancy, and population dynamics |
| `starsim-dev-interventions` | Vaccination, screening, treatment, and custom interventions |
| `starsim-dev-connectors` | Disease-disease interactions in multi-disease models |
| `starsim-dev-analyzers` | Custom result collection and analysis |
| `starsim-dev-distributions` | Probability distributions and sampling |
| `starsim-dev-calibration` | Model calibration with Optuna and Bayesian methods |
| `starsim-dev-run` | Running multiple sims, scenarios, and parallelization |
| `starsim-dev-time` | Dates, durations, rates, and time conversions |
| `starsim-dev-indexing` | Arrays, UIDs, boolean states, and agent indexing |
| `starsim-dev-random` | Common random numbers and reproducibility |
| `starsim-dev-nonstandard` | Compartmental (ODE) models and general-purpose ABMs |
| `starsim-dev-profiling` | Performance profiling and debugging |
| `starsim-style-python` | Python code style conventions |
| `starsim-style-docs` | Documentation style (docstrings, READMEs, tutorials) |
| `starsim-style-philosophy` | Starsim design philosophy |
| `starsim-style-tests` | Testing conventions |
| `sciris-utilities` | Sciris utilities (file I/O, parallelization, data structures) |
| `stisim-modeling` | STIsim — STI disease modeling (HIV, syphilis, etc.) |

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