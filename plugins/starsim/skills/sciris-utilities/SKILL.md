---
name: sciris-utilities
description: Use when the user is working with Sciris utilities — including file I/O, date handling, parallelization, profiling, plotting helpers, or data structures like odict and dataframe.
---

# Sciris Utilities

You are helping the user work with [Sciris](https://github.com/sciris/sciris), a library of utility functions commonly used alongside Starsim and other scientific Python projects. These instructions were written for Sciris version 3.2.7 on 2026-02-19.

## When to activate

- User asks about Sciris functions (`sc.*`)
- User needs file I/O (`sc.save`, `sc.load`, `sc.makefilepath`)
- User needs date/time utilities, parallelization, profiling, or plotting helpers
- User is working with `sc.odict`, `sc.dataframe`, or other Sciris data structures

## Key modules

- **sc.save / sc.load**: Save and load Python objects (pickle-based, with compression).
- **sc.odict**: Ordered dict accessible by index or key.
- **sc.dataframe**: Lightweight dataframe with dict-like access.
- **sc.parallelize**: Easy parallel execution of functions.
- **sc.timer / sc.profile**: Profiling and timing utilities.
- **sc.daterange / sc.date / sc.daydiff**: Date manipulation.
- **sc.mergedicts**: Merge multiple dicts with conflict handling.
- **sc.prettyobj**: Base class that gives objects a nice `__repr__`.
- **sc.options**: Global options for Sciris behavior.

## Approach

1. Use the sciris MCP tools (if available) to look up current API signatures and examples.
2. If MCP tools are unavailable, use Context7 for up-to-date docs.
3. Prefer Sciris built-ins over reimplementing common patterns (e.g. use `sc.parallelize` instead of manual `multiprocessing`).

## Common patterns

```python
import sciris as sc

# Save/load
sc.save('results.obj', data)
data = sc.load('results.obj')

# Parallel execution
def run_sim(seed):
    sim = make_sim(seed)
    sim.run()
    return sim.summary()

results = sc.parallelize(run_sim, [0, 1, 2, 3])

# Timing
with sc.timer():
    expensive_operation()

# Ordered dict
d = sc.odict(a=1, b=2, c=3)
d[0]  # Access by index: 1
```
