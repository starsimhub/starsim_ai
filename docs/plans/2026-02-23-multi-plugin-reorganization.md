# Multi-Plugin Reorganization Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reorganize the repository to support two Claude Code plugins (starsim + disease_modeling) under a single root marketplace.

**Architecture:** Move the marketplace definition to the repo root so `/plugin marketplace add` points at the repo itself. Each plugin lives in its own subdirectory with independent `plugin.json`, skills, MCP config, etc. The root `.claude-plugin/` contains only `marketplace.json` (the root is a marketplace, not a plugin).

**Tech Stack:** Claude Code plugin system, JSON config files, git

---

## Current Structure

```
starsim_ai/
├── claude_plugin/
│   ├── .claude-plugin/
│   │   ├── plugin.json          # Plugin manifest (name: "starsim-ai")
│   │   └── marketplace.json     # Marketplace catalog (source: "./")
│   ├── .mcp.json                # MCP servers (context7)
│   ├── .claude/
│   │   └── settings.local.json  # Enabled MCP servers
│   ├── skills/                  # 7 skills
│   └── README.md
```

## Target Structure

```
starsim_ai/
├── .claude-plugin/
│   └── marketplace.json         # Root marketplace listing BOTH plugins
├── starsim_plugin/
│   ├── .claude-plugin/
│   │   └── plugin.json          # starsim-ai plugin manifest
│   ├── .mcp.json
│   ├── .claude/
│   │   └── settings.local.json
│   ├── skills/                  # All 7 existing skills
│   └── README.md
├── disease_modeling_plugin/
│   ├── .claude-plugin/
│   │   └── plugin.json          # disease-modeling plugin manifest
│   └── skills/                  # Empty for now
```

---

### Task 1: Move Marketplace to Root and Rename Plugin Directory

**Files:**
- Move: `claude_plugin/.claude-plugin/marketplace.json` -> `.claude-plugin/marketplace.json`
- Rename: `claude_plugin/` -> `starsim_plugin/`

**Step 1: Create root `.claude-plugin/` and git mv marketplace.json to it**

```bash
mkdir -p .claude-plugin
git mv claude_plugin/.claude-plugin/marketplace.json .claude-plugin/marketplace.json
```

**Step 2: Rename `claude_plugin/` to `starsim_plugin/`**

```bash
git mv claude_plugin starsim_plugin
```

After this, `starsim_plugin/.claude-plugin/` contains only `plugin.json` (correct).

**Step 3: Edit `.claude-plugin/marketplace.json` to update source paths and add second plugin**

Update from:

```json
"source": "./"
```

to the full updated content:

```json
{
  "name": "starsim-marketplace",
  "owner": {
    "name": "StarsimHub"
  },
  "metadata": {
    "description": "Starsim-aware AI skills and MCP tools"
  },
  "plugins": [
    {
      "name": "starsim-ai",
      "source": "./starsim_plugin",
      "description": "Starsim and Sciris MCP tools and modeling skills",
      "version": "0.1.0",
      "keywords": ["starsim", "sciris", "disease-modeling", "epidemiology"]
    },
    {
      "name": "disease-modeling",
      "source": "./disease_modeling_plugin",
      "description": "General disease modeling skills and tools",
      "version": "0.1.0",
      "keywords": ["disease-modeling", "epidemiology", "compartmental-models"]
    }
  ]
}
```

**Step 4: Verify `starsim_plugin/.claude-plugin/plugin.json` is correct**

The existing content is already correct (name: "starsim-ai"). No changes needed:

```json
{
  "name": "starsim-ai",
  "version": "0.1.0",
  "description": "Starsim-aware AI skills and MCP tools for agent-based disease modeling",
  "author": {
    "name": "StarsimHub"
  },
  "repository": "https://github.com/starsimhub/starsim_ai",
  "license": "MIT",
  "keywords": ["starsim", "sciris", "disease-modeling", "epidemiology"]
}
```

**Step 5: Verify all other files inside `starsim_plugin/` are intact**

Confirm these exist and are unchanged:
- `starsim_plugin/.mcp.json`
- `starsim_plugin/.claude/settings.local.json`
- `starsim_plugin/skills/` (all 7 skill directories)

**Step 6: Commit**

```bash
git add -A
git commit -m "refactor: move marketplace to root, rename claude_plugin to starsim_plugin"
```

---

### Task 2: Create `disease_modeling_plugin/`

**Files:**
- Copy+edit: `starsim_plugin/.claude-plugin/plugin.json` -> `disease_modeling_plugin/.claude-plugin/plugin.json`
- Create: `disease_modeling_plugin/skills/README.md`

**Step 1: Create directory structure and copy plugin.json from starsim_plugin**

```bash
mkdir -p disease_modeling_plugin/.claude-plugin
mkdir -p disease_modeling_plugin/skills
cp starsim_plugin/.claude-plugin/plugin.json disease_modeling_plugin/.claude-plugin/plugin.json
```

**Step 2: Edit `disease_modeling_plugin/.claude-plugin/plugin.json`**

Change the fields to match the new plugin:
- `"name"`: `"starsim-ai"` -> `"disease-modeling"`
- `"description"`: -> `"General disease modeling skills and tools"`
- `"keywords"`: -> `["disease-modeling", "epidemiology", "compartmental-models"]`

Result:

```json
{
  "name": "disease-modeling",
  "version": "0.1.0",
  "description": "General disease modeling skills and tools",
  "author": {
    "name": "StarsimHub"
  },
  "repository": "https://github.com/starsimhub/starsim_ai",
  "license": "MIT",
  "keywords": ["disease-modeling", "epidemiology", "compartmental-models"]
}
```

**Step 3: Add `README.md` to `skills/` directory**

```markdown
# Disease Modeling Skills

Skills for this plugin will be added here.
```

**Step 4: Commit**

```bash
git add disease_modeling_plugin/
git commit -m "feat: add empty disease-modeling plugin scaffold"
```

---

### Task 3: Update `starsim_plugin/README.md`

**Files:**
- Modify: `starsim_plugin/README.md`

**Step 1: Update the README to reflect the new structure**

Key changes:
- Installation path changes: marketplace is now at repo root, not `claude_plugin/`
- Update the "Plugin structure" ASCII tree
- Mention the multi-plugin setup

Updated content:

```markdown
# Starsim Plugin

A Claude Code plugin that provides Starsim and Sciris MCP tools and modeling skills.

## What's included

- **MCP servers** - Connects to the hosted Starsim and Sciris documentation servers, giving Claude access to up-to-date API docs and examples.
- **starsim-modeling skill** - Activates when building Starsim simulations (diseases, networks, interventions, etc.).
- **sciris-utilities skill** - Activates when using Sciris utilities (file I/O, parallelization, data structures, etc.).

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
starsim_plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── .mcp.json                # MCP server definitions (context7)
├── skills/
│   ├── starsim-modeling/
│   │   └── SKILL.md         # Starsim simulation guidance
│   ├── sciris-utilities/
│   │   └── SKILL.md         # Sciris utility guidance
│   ├── starsim-style-docs/
│   │   └── SKILL.md         # Documentation style
│   ├── starsim-style-philosophy/
│   │   └── SKILL.md         # Design philosophy
│   ├── starsim-style-python/
│   │   └── SKILL.md         # Python code style
│   ├── starsim-style-tests/
│   │   └── SKILL.md         # Testing conventions
│   └── stisim-modeling/
│       └── SKILL.md         # STI disease modeling
└── README.md
```
```

**Step 2: Commit**

```bash
git add starsim_plugin/README.md
git commit -m "docs: update starsim plugin README for new repo layout"
```

---

### Task 4: Update Root `README.md`

**Files:**
- Modify: `README.md`

**Step 1: Update the root README to reflect multi-plugin structure**

Add a section describing the two plugins and the new installation path. Specifically:
- Mention both plugins
- Update the marketplace add path from `claude_plugin/` to repo root
- Brief description of each plugin

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update root README for multi-plugin layout"
```

---

### Task 5: Update Root `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the Repository Structure section**

Change references from `claude_plugin/` to the new layout:
- `starsim_plugin/` - Starsim-specific Claude Code plugin
- `disease_modeling_plugin/` - General disease modeling plugin (WIP)

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for multi-plugin layout"
```

---

## Review: Issues and Considerations

### Installation Path Change (Breaking)

The marketplace add path changes from:
```
/plugin marketplace add /path/to/starsim_ai/claude_plugin
```
to:
```
/plugin marketplace add /path/to/starsim_ai
```

Anyone who previously installed the plugin will need to **re-add the marketplace** at the new path. The old path will stop working because `marketplace.json` will no longer exist at `starsim_plugin/.claude-plugin/`.

### Root `.claude-plugin/` Has No `plugin.json`

This is intentional and correct. The repo root is a **marketplace**, not a plugin. Only `marketplace.json` belongs at root. Each plugin has its own `plugin.json` in its own `.claude-plugin/` directory. This matches the Claude Code convention: marketplace.json lists plugins via `source` paths; each plugin is self-contained.

### `disease_modeling_plugin` Is Empty

The new plugin has a valid manifest but no skills, MCP servers, or other components. This is fine — installing an empty plugin won't break anything, but it also won't do anything. Consider whether to list it in `marketplace.json` now (discoverable but empty) or add it later when it has content.

### MCP Config Stays in `starsim_plugin/`

The `.mcp.json` (context7 server) and `.claude/settings.local.json` remain inside `starsim_plugin/`. If the disease modeling plugin needs MCP servers later, it gets its own `.mcp.json`. No sharing is needed.

### Skills Won't Move Between Plugins

All 7 existing skills stay in `starsim_plugin/`. If any skills should eventually live in `disease_modeling_plugin/` instead (e.g., skills that are about general disease modeling rather than starsim-specific), that would be a separate future task.

### No Functional Changes

This is purely a reorganization. No skills, MCP servers, or plugin behavior changes. Everything that worked before will work after (once the marketplace is re-added at the new path).
