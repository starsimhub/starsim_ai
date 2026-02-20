---
name: starsim-style-docs
description: Use when writing, reviewing, or editing documentation for Starsim projects — including docstrings, READMEs, tutorials, and API reference. Also use when the user asks to check documentation against the Starsim style guide.
---

# Starsim Style — Documentation

Check and enforce the [Starsim documentation style guide](https://github.com/starsimhub/styleguide/blob/main/4_documentation.md). The core principle: **good docs are succinct but comprehensive — people spend far more time reading docs than reading code.**

## When to activate

- **Proactively**: when writing docstrings, READMEs, or other documentation in a Starsim project. Apply the guidelines below naturally.
- **On review**: when the user asks to check documentation against the Starsim style guide. Run the review checklist and report violations using the format at the bottom of this skill.

## Review checklist

When invoked directly for review, check each item against the target code or project:

1. **Every public function/class/module has a docstring** — No public API should be undocumented.
   *Reference: 4_documentation.md — "Every public module, class, and function should have a docstring."*

2. **Google-style docstrings** — Docstrings must use Google style with Args, Returns, and ideally an Example section.
   *Reference: 4_documentation.md — "Use Google-style docstrings."*

3. **Type info in docstrings** — Parameter types should be documented in docstrings (not as type annotations). Use compact notation like `(int/str/date)`.
   *Reference: 4_documentation.md + 2_python.md §2.21 — types go in docstrings, not annotations*

4. **Usage examples in docstrings** — Docstrings should ideally include at least one usage example showing how to call the function.
   *Reference: 4_documentation.md — "Docstrings should include at least: a one-line summary, a description of parameters and return values, and ideally one usage example."*

5. **README essentials** — The repo-level README must include: what the package does, installation instructions, a quick usage example (<10 lines), project structure, and links to full docs.
   *Reference: 4_documentation.md — README should include "What the package does, Installation, Quick usage example, Project structure, Links"*

6. **Folder READMEs** — Every folder in the repo should have a README.md explaining why it exists and what it contains.
   *Reference: 4_documentation.md — "Every folder in the repo should have a README.md file — even if it's just one or two sentences."*

7. **Tutorials exist** — The project should have at least a "hello world" tutorial and one slightly more advanced tutorial, as Jupyter notebooks.
   *Reference: 4_documentation.md — "At minimum, try to provide: A 'hello world' tutorial, A slightly more advanced tutorial"*

8. **No Sphinx/rST** — Documentation should use MkDocs (with Material theme) or Quarto. Never Sphinx or reStructuredText.
   *Reference: 4_documentation.md — "Please do not use Sphinx or rST unless you hate yourself and others."*

## Guidelines

### Docstring format

Use Google-style docstrings with type info, aligned parameters, and an example:

```python
def count_days(self, start_day, end_day):
    """ Count days between start and end relative to "sim time"

    Args:
        start_day (int/str/date): The day to start counting
        end_day   (int/str/date): The day to stop counting

    Returns:
        elapsed (int): Number of whole days between start and end

    **Example**::

        sim.count_days(45, '2022-02-02')
    """
    return self.day(end_day) - self.day(start_day)
```

Note: vertically align parameter names and types when there are multiple parameters (consistent with the Python style guide's semantic indenting convention).

### README structure

A good repo-level README includes:

```markdown
# Project Name

Brief description of what the package does.

## Installation

pip install projectname

## Quick start

<minimal working example in under 10 lines>

## Project structure

- `projectname/` — Core library code
- `tests/` — Test suite
- `docs/` — Documentation source

## Links

- [Full documentation](https://...)
- [Issue tracker](https://...)
- [Contributing guide](CONTRIBUTING.md)
```

Additional repo-level files:
- **LICENSE** (MIT)
- **What's new / changelog**
- **Contributing guide**
- **Code of conduct**

### Documentation tools

- **MkDocs** (with [Material](https://squidfundamentals.com/mkdocs-material/) theme) — easier setup, less layout control
- **Quarto** — higher startup cost, more flexibility

Starsim itself uses Quarto; most Starsim models use MkDocs. Either way, docs live in `docs/` and produce a static website.

### API reference

Auto-generate from docstrings using:
- [quartodoc](https://machow.github.io/quartodoc/) for Quarto projects
- [mkdocstrings](https://mkdocstrings.github.io/) for MkDocs projects

Configure interlinks so cross-references to Python, NumPy, Pandas, and Sciris resolve automatically.

### Tutorials

Jupyter notebook-based tutorials are strongly encouraged. Structure:

1. **Hello world** — simplest possible working example with explanation
2. **Core workflow** — end-to-end demonstration of the main use case
3. **Progressive series** — for larger projects, build from basics to advanced topics

For complex projects, add a **user guide** progressing from concepts to practice:
1. Introduction — what the package is
2. Basics — core objects and how they fit together
3. Modules — detailed coverage of each subsystem
4. Workflows — common end-to-end tasks
5. Advanced topics — performance, edge cases, internals

## Proposing changes

When reporting a violation in review mode, use this format:

```
**Style issue**: <what's wrong>
**Rule**: <checklist item number and name>
**Reference**: starsimhub/styleguide 4_documentation.md — "<quoted rule>"
**Current code/docs**:
    <original>
**Proposed fix**:
    <fixed version>
```
