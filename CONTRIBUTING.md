# Contributing to Starsim-AI

Thank you for your interest in contributing! This project provides AI plugins, skills, and tools for the [Starsim](https://starsim.org) disease modeling framework.

## How to contribute

### Reporting issues

Open an issue on [GitHub](https://github.com/starsimhub/starsim_ai/issues) with a clear description of the problem or suggestion.

### Adding or improving skills

1. Fork the repository and create a feature branch.
2. Skills live in `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`.
3. Follow the existing skill format (YAML frontmatter + markdown body).
4. Test your skill by installing the plugin locally in Claude Code.
5. Open a pull request with a description of what the skill does and why.

### Adding a new plugin

1. Create a directory under `plugins/<plugin-name>/`.
2. Add a `.claude-plugin/plugin.json` manifest.
3. Add the plugin to `.claude-plugin/marketplace.json` in the root.
4. Include a `README.md` in the plugin directory.

### Code changes

- Python code should follow standard Python conventions.
- Keep internal scripts in `internal/` — these are not user-facing.
- Update `CHANGELOG.md` when making user-visible changes.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
