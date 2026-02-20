---
name: starsim-style-tests
description: Use when writing, reviewing, or editing tests for Starsim projects to ensure they follow Starsim testing conventions. Also use when the user asks to check test code against the Starsim style guide's testing section.
---

# Starsim Style — Tests

Check and enforce the [Starsim testing style guide](https://github.com/starsimhub/styleguide/blob/main/3_tests.md). The overriding principle: **tests should be runnable both by pytest and as standalone scripts.**

## When to activate

- **Proactively**: when writing or editing test files in a Starsim project. Apply the conventions below naturally.
- **On review**: when the user asks to check test code against the Starsim style guide. Run the review checklist and report violations using the format at the bottom of this skill.

## Review checklist

When invoked directly for review, check each item against the target code:

1. **Dual-mode execution** — The test file must work both as a pytest module and as a standalone script. There must be an `if __name__ == '__main__':` block that runs all tests with plotting enabled.
   *Reference: 3_tests.md — "tests should be runnable both by pytest and as standalone scripts"*

2. **@sc.timer() decorator** — Every test function should be decorated with `@sc.timer()` to print timing information.
   *Reference: 3_tests.md — "Test functions are typically decorated with @sc.timer()"*

3. **Module-level constants** — `do_plot`, `n_agents`, and `sc.options(interactive=False)` should be defined at the top of the file, not inside test functions.
   *Reference: 3_tests.md — "Define constants at the top of the file so they can be easily tuned"*

4. **Conditional plotting** — Plotting must be gated behind `if do_plot:`. Use `plt.figure()` before manual plotting to avoid drawing on a previous test's figure.
   *Reference: 3_tests.md — "Plotting should always be conditional, unless the plot itself is being tested"*

5. **Descriptive assertion messages** — Every `assert` must include a message string describing what was *expected*, not just what happened.
   *Reference: 3_tests.md — "Always include a descriptive message in assertions."*

6. **Float comparisons with tolerances** — Use `np.isclose()` or `np.allclose()` with explicit tolerances for floating-point comparisons. Comment the tolerance choice.
   *Reference: 3_tests.md — "For float comparisons, use np.isclose or np.allclose with explicit tolerances"*

7. **Test functions return objects** — Tests should return the "most interesting" object they create (typically the sim) so results can be inspected when run as a script.
   *Reference: 3_tests.md — "Tests typically return 'the most interesting' object they generate."*

8. **Scientific correctness testing** — Tests should check that epi dynamics go in the expected direction, not just that code runs without error. Vary a parameter and confirm the result changes as expected.
   *Reference: 3_tests.md — "test that the model behaves as epidemiologically expected, not just that code runs without errors"*

9. **Descriptive test names** — Name test functions `test_<feature>` where `<feature>` is descriptive. Avoid generic names like `test_api` or redundant suffixes like `test_sir_model`.
   *Reference: 3_tests.md — "Name test functions test_<feature>, where <feature> describes what is being tested"*

10. **Generous stochastic tolerances** — Use generous tolerances (`rtol=0.05` or more) for stochastic comparisons to avoid flaky tests with small populations.
    *Reference: 3_tests.md — "Use generous tolerances (rtol=0.05 or more) for stochastic comparisons to avoid flaky tests."*

## Guidelines

### Test file skeleton

Every test file should follow this structure:

```python
"""
Test <topic>
"""
import sciris as sc
import numpy as np
import starsim as ss
import matplotlib.pyplot as plt
import pytest

n_agents = 1_000
do_plot = False
sc.options(interactive=False) # Assume not running interactively


def make_sim():
    """ Helper to create a default sim for this test file """
    ...
    return sim


@sc.timer()
def test_feature(do_plot=do_plot):
    """ One-line description of what this test checks """
    sc.heading('Testing feature...')
    sim = make_sim()
    sim.run()
    assert sim.results.something > 0, 'Expected something to be positive'
    if do_plot:
        sim.plot()
    return sim


if __name__ == '__main__':
    do_plot = True
    sc.options(interactive=do_plot)
    T = sc.timer()

    sim = test_feature(do_plot=do_plot)

    T.toc()

    if do_plot:
        plt.show()
```

Key elements in order:
1. Module docstring
2. Imports
3. Module-level constants (`n_agents`, `do_plot`, `sc.options(interactive=False)`)
4. Helper functions (`make_sim()`, `make_sim_pars()`)
5. Test functions decorated with `@sc.timer()`, named `test_*`
6. `if __name__ == '__main__':` block

### TDD is encouraged

Write the test *before* the feature. Use it to brainstorm the API. The style guide puts it well: "You can trick yourself that you're doing cool design architecture instead of writing a boring test."

### Assertions

Always say what was *expected*:

```python
# Good
assert v0 <= v1, f'Expected prevalence to be lower with {par}={lo} than {par}={hi}, but {v0} > {v1}'
assert len(log) > 900, 'Expect almost everyone to be infected'

# Bad: no message
assert v0 <= v1
assert sim.results.n_alive[0] > 0
```

For floats, use tolerances and comment them:

```python
rtol = 0.2  # Generous to avoid random failures with small populations
assert np.isclose(data.n_alive.values[-1], sim.results.n_alive[-1], rtol=rtol), \
    'Final pop not within tolerance of data'
```

For expected exceptions:

```python
with pytest.raises(TypeError):
    sim = ss.Sim(diseases=True)
    sim.init()
```

### Scientific correctness pattern

Vary a parameter and check the result moves in the expected direction:

```python
par_effects = dict(
    beta    = [0.01, 0.99],
    dur_inf = [1, 8],
    p_death = [0.01, 0.1],
)

for par, (lo, hi) in par_effects.items():
    s0 = ss.Sim(**{par: lo}).run()
    s1 = ss.Sim(**{par: hi}).run()
    v0, v1 = s0.summary.prevalence, s1.summary.prevalence
    assert v0 <= v1, f'Expected higher {par} to increase prevalence'
```

### Agent counts

Use the smallest population that produces meaningful results:

- Unit tests: `100`–`1_000`
- Integration tests: `10_000`
- Use underscore separators for large numbers: `1_000`, `10_000`

## Proposing changes

When reporting a violation in review mode, use this format:

```
**Style issue**: <what's wrong>
**Rule**: <checklist item number and name>
**Reference**: starsimhub/styleguide 3_tests.md — "<quoted rule>"
**Current code**:
    <original>
**Proposed fix**:
    <fixed version>
```
