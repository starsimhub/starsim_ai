Your task is to update the Project-Improver plugin (comprising the Project-Scorer and Project-Fixer skills and agents) based on updates to the engineering quality guidelines.

1. The engineering quality guidelines document ("guidelines doc") is in `$ROOT/plugins/project-improver/engineering_quality_guidelines.md`, where `$ROOT` is the Starsim-AI root folder.
2. Read the guidelines doc and check for updates since the plugin was last updated (in `plugin.json`). 2a. If there are no updates, exit. 2b. If there are updates, make a list of these changes.
3. Create a version tag from the version number and date: if "Version 1.1 | 2026.03.23" is in the guidelines doc, set the version in `plugin.json` to "v1.1_2026.03.23", and also include "Skill version: v1.1_2026.03.23" at the end of the introduction of each of the individual SKILL.md files.
4. Update the skills, agents, and any other necessary files based on the list of changes in the guidelines document.
5. Verify that every metric and tier described in the current version of the guidelines doc is covered in the scoring schema and agent prompts.
6. Update the changelog (`$ROOT/plugins/project-improver/CHANGELOG.md`) with key changes made (no more than 5-10 points max, 1 or 2 is fine).