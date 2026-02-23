---
name: starsim-style-philosophy
description: Use when writing, reviewing, or editing Starsim code to ensure it follows the Starsim design philosophy. Also use when the user asks to check code against the Starsim style guide's philosophy section.
---

# Starsim Style — Design Philosophy

Check and enforce the [Starsim design philosophy](https://github.com/starsimhub/styleguide/blob/main/1_philosophy.md). The core principle: **"Common tasks should be simple; uncommon tasks should still be possible."**

## When to activate

- **Proactively**: when writing or editing Starsim library code, interventions, or user-facing APIs. Apply the guidelines below naturally.
- **On review**: when the user asks to check code against the Starsim style guide. Run the review checklist and report violations using the format at the bottom of this skill.

## Review checklist

When invoked directly for review, check each item against the target code:

1. **Simple common tasks** — Can the most common use case be done in one or two lines? If the user has to write boilerplate to do something routine, simplify the API.
   *Reference: 1_philosophy.md — "Common tasks should be simple"*

2. **Flexible inputs** — Does the code accept multiple input types (list, array, scalar) where a user could reasonably provide any of them? Convert automatically rather than raising a type error.
   *Reference: 1_philosophy.md — "Be as flexible as possible with user inputs. If a user could only mean one thing, do that."*

3. **Sensible defaults** — Does every keyword argument have a sensible default value? Users shouldn't have to specify parameters they don't care about.
   *Reference: 1_philosophy.md — "If there's a 'sensible' default value for something, use it."*

4. **Nothing hard-coded** — Are values that a user might want to change exposed as keyword arguments with defaults, rather than buried as literals in the function body?
   *Reference: 1_philosophy.md — "Hard-code as little as possible. Rather than defining a variable at the top of the function, make it a keyword argument with a default value."*

5. **Pass kwargs through** — Where a function wraps another (e.g., JSON serialization, plotting), does it accept and forward `**kwargs` so users can pass options to the underlying library?
   *Reference: 1_philosophy.md — "Pass keyword arguments where possible — e.g., to_json(..., **kwargs)"*

6. **Clear scientific logic** — Is the scientific logic easy to follow? If "good science" conflicts with "good coding style," the science should win.
   *Reference: 1_philosophy.md — "Ensure the logic, especially the scientific logic, of the code is as clear as possible."*

7. **Generous comments** — Are there enough comments, especially for scientific logic, parameter choices, and numbers from papers? Every number from a paper should cite the paper.
   *Reference: 1_philosophy.md — "Err on the side of more comments. If you use a number that came from a scientific paper, please for the love of all that is precious put a link to that paper in a comment."*

8. **Audience-appropriate complexity** — Does the code avoid "advanced" Python features (lambda functions, dunder overrides, deep class hierarchies) unless truly necessary? The audience is scientists, not software developers.
   *Reference: 1_philosophy.md — "Use these 'advanced features' only as a last resort."*

## Guidelines

### The audience is scientists

Starsim users are scientists who want tools that *just work*. They may not be comfortable with advanced Python, and they shouldn't have to be. Commands should be short, obvious, and chainable:

```python
# Good: simple, chainable
sim = ss.Sim(diseases=ss.SIR()).run().plot()

# Bad: requires understanding of internals
sim = ss.Sim()
sim.configure(disease_module=ss.SIR(transmission_rate=0.1))
sim.initialize()
sim.execute()
sim.generate_plots(output_format='screen')
```

### The workload equation

The total work your code creates is:

*W = sum over each person p of (u + n*r + m*e)*

- *u* = ramp-up time to understand the code
- *n* = number of reads, *r* = time per read
- *m* = number of edits, *e* = time per edit

Common mistakes: overemphasizing your own experience (*p=0*) over others, and overemphasizing edit time (*e*) over ramp-up time (*u*) and read time (*r*). Code is read far more than it is written — optimize for the reader.

### Flexibility over strictness

Accept whatever the user gives you and make it work:

```python
# Good: accept multiple types, convert internally
def set_days(self, days):
    days = sc.toarray(days)  # Handles int, list, array, etc.
    ...

# Bad: force the user to provide a specific type
def set_days(self, days: np.ndarray):
    ...
```

### Defaults and keyword arguments

Expose tunable values as kwargs with defaults — never bury them:

```python
# Good: user CAN customize but doesn't HAVE to
def test_prob(self, prob=0.1, sensitivity=0.95, loss_prob=0.0, **kwargs):
    ...

# Bad: hard-coded values the user can't change
def test_prob(self, prob):
    sensitivity = 0.95  # Buried
    loss_prob = 0.0     # Buried
    ...
```

## Proposing changes

When reporting a violation in review mode, use this format:

```
**Style issue**: <what's wrong>
**Rule**: <checklist item number and name>
**Reference**: starsimhub/styleguide 1_philosophy.md — "<quoted rule>"
**Current code**:
    <original>
**Proposed fix**:
    <fixed version>
```
