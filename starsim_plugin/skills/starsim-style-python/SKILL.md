---
name: starsim-style-python
description: Use when writing, reviewing, or editing Python code for Starsim projects to ensure it follows Starsim's Python style conventions. Also use when the user asks to check code against the Starsim style guide's Python section.
---

# Starsim Style — Python

Check and enforce the [Starsim Python style guide](https://github.com/starsimhub/styleguide/blob/main/2_python.md). Starsim follows Google's Python style guide with specific house exceptions documented below.

## When to activate

- **Proactively**: when writing or editing Python code in a Starsim project. Apply the guidelines below naturally.
- **On review**: when the user asks to check code against the Starsim style guide. Run the review checklist and report violations using the format at the bottom of this skill.

## Review checklist

When invoked directly for review, check each item against the target code:

1. **No type annotations** — Function signatures must not have type annotations. Type information belongs in docstrings, e.g. `start_day (int/str/date)`.
   *Reference: 2_python.md §2.21 — "Do not use type annotations."*

2. **Line length pragmatism** — Lines >80 chars are acceptable when breaking would be worse. Long line comments are fine and must not be broken across lines. But needlessly long lines should be shortened by using more concise variable names.
   *Reference: 2_python.md §3.2 — "Think of lines >80 characters as bad, but breaking a line as being equally bad."*

3. **Vertical alignment** — Consecutive similar lines (e.g., assignments, dict entries, flow updates) should be vertically aligned to highlight semantic similarities and make bugs visible.
   *Reference: 2_python.md §3.6 — "You should use spaces to vertically align tokens."*

4. **Proportional blank lines** — Use more blank lines between larger blocks. Two blank lines between methods if methods contain internal blank lines. Three blank lines between large classes (>500 lines).
   *Reference: 2_python.md §3.5 — "Always use (at least) one extra blank line between levels as within a level."*

5. **Explicit return** — Every function and method should end with an explicit `return` statement, even if returning `None` (use `return`, not `return None`). Prefer `return self` to enable chaining.
   *Reference: 2_python.md §3.5 — "return statements should be used at the end of each function and method."*

6. **f-strings** — Use f-strings for string formatting. Use concatenation when simpler (e.g., `a + b` rather than `f'{a}{b}'`). Never use `.format()` or `%`.
   *Reference: 2_python.md §3.10 — "Always use f-strings or addition."*

7. **Logical import order** — Imports ordered: stdlib → numeric (numpy before pandas) → plotting → internal. Second-order sorting is logical (by dependency level), not alphabetical.
   *Reference: 2_python.md §3.13 — "Imports should be ordered logically rather than alphabetically."*

8. **Short memorable names** — Variable names should be short but memorable. Meaning should be clear from the name plus its comment or docstring, not the name alone. Avoid both excessive verbosity (`vaccination_probability`) and cryptic abbreviations (`vp`).
   *Reference: 2_python.md §3.16 — "Names should be as short as they can be while being memorable."*

9. **Function-like class naming** — Classes that users interact with like functions (e.g., interventions created once and not subclassed) should use lowercase function naming: `ss.vaccinate_prob()`, not `ss.VaccinateProb()`.
   *Reference: 2_python.md §3.16 — "If an object is technically a class but is used more like a function, it should be named as if it were a function."*

10. **Explicit .keys()** — Using `for key in obj.keys()` is acceptable and preferred when it improves clarity about the object's type.
    *Reference: 2_python.md §2.8 — "It's fine to use for key in obj.keys() instead of for key in obj."*

## Guidelines

### Type annotations: use docstrings instead

Starsim prioritizes input flexibility — functions accept scalars, lists, arrays, dates as strings, etc. Type annotations can't express this cleanly. Put type info in docstrings instead:

```python
# Good: type info in docstring
def count_days(self, start_day, end_day):
    """ Count days between start and end relative to sim time

    Args:
        start_day (int/str/date): The day to start counting
        end_day   (int/str/date): The day to stop counting

    Returns:
        elapsed (int): Number of whole days between start and end
    """
    return self.day(end_day) - self.day(start_day)

# Bad: type annotations can't express the flexibility
def count_days(self, start_day: typing.Union[None, str, int, dt.date], ...):
    ...
```

### Line length and comments

Lines over 80 characters are a tradeoff — breaking them is equally bad. Long line comments are fine because they're read rarely but scrolled past constantly:

```python
# Good: slightly over 80 chars but readable
foo_bar(self, width, height, color='black', design=None, x='foo', emphasis=None)

# Bad: the cost of breaking is too high
foo_bar(self, width, height, color='black', design=None, x='foo',
        emphasis=None)

# Good: long line comment is fine
foo_bar(self, width, height) # Note the difference with bar_foo(), which does not perform the opposite operation
```

If a line is too long, first ask if variable names can be more concise rather than breaking the line.

### Vertical alignment (semantic indenting)

Align consecutive similar lines to make differences (and bugs) jump out:

```python
# Good: bug on line 4 is immediately visible
self.flows['new_infectious']  += self.check_infectious()
self.flows['new_symptomatic'] += self.check_symptomatic()
self.flows['new_severe']      += self.check_symptomatic()  # Bug! Should be check_severe()
self.flows['new_critical']    += self.check_critical()

# Good: aligned assignments with comments
test_prob  = 0.1 # Per-day testing probability
vax_prob   = 0.3 # Per-campaign vaccination probability
trace_prob = 0.8 # Per-contact probability of being traced

# Bad: excessive alignment (too much whitespace)
t                = 0
omicron_vax_prob = dict(low=0.05, high=0.1)
```

Use judgment — alignment helps for blocks of 3+ similar lines, but becomes harmful when it requires egregious whitespace.

### Multiline statements

Sometimes acceptable for short, semantically parallel blocks:

```python
# OK: parallel structure is clear
if foo: bar(foo)
else:   baz(foo)

# OK
try:    bar(foo)
except: pass

# Bad: too much logic hidden in alignment
try:               bar(foo)
except ValueError: baz(foo)
```

### Naming conventions

Names should be consistent with the libraries Starsim interacts with (NumPy, Matplotlib):

```python
# Good: matches Matplotlib convention
figsize = (10, 8)

# Bad: Google style but inconsistent with Matplotlib
fig_size = (10, 8)
```

Use short names with comments for context:

```python
# Good
vax_prob = 0.3 # Per-campaign vaccination probability

# Bad: too verbose
vaccination_probability = 0.3

# Bad: too cryptic
vp = 0.3
```

### Import ordering

```python
# Good: logical ordering by dependency level
import os
import shutil
import numpy as np
import pandas as pd
import pylab as pl
import seaborn as sns
from .covasim import defaults as cvd
from .covasim import plotting as cvpl
```

Note: Starsim uses `import pylab as pl` rather than `import matplotlib.pyplot as plt` (shorter to type, functionally identical).

## Proposing changes

When reporting a violation in review mode, use this format:

```
**Style issue**: <what's wrong>
**Rule**: <checklist item number and name>
**Reference**: starsimhub/styleguide 2_python.md §<section> — "<quoted rule>"
**Current code**:
    <original>
**Proposed fix**:
    <fixed version>
```
