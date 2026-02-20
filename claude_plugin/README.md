# Claude Starsim Plugin

A Claude Code plugin that provides Starsim and Sciris MCP tools and modeling skills.

## What's included

- **MCP servers** - Connects to the hosted Starsim and Sciris documentation servers, giving Claude access to up-to-date API docs and examples.
- **starsim-modeling skill** - Activates when building Starsim simulations (diseases, networks, interventions, etc.).
- **sciris-utilities skill** - Activates when using Sciris utilities (file I/O, parallelization, data structures, etc.).

## Installation

Inside Claude Code, add this repo as a local marketplace, then install the plugin:

1. **Add the marketplace** (run inside Claude Code):
   ```
   /plugin marketplace add /path/to/starsim_ai/claude_plugin
   ```

2. **Install the plugin** (run inside Claude Code):
   ```
   /plugin install starsim-ai
   ```

   Or use the interactive UI — run `/plugin`, go to the **Discover** tab, and install from there.

3. **Verify** — run `/mcp` to confirm the `starsim` and `sciris` MCP servers are listed.

## Plugin structure

```
claude_plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── .mcp.json                # MCP server definitions (starsim + sciris)
├── skills/
│   ├── starsim-modeling/
│   │   └── SKILL.md         # Starsim simulation guidance
│   └── sciris-utilities/
│       └── SKILL.md         # Sciris utility guidance
└── README.md
```
