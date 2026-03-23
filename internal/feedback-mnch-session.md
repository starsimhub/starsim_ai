# Feedback: MNCH Implementation Session (2026-03-14)

Lessons learned from implementing stillbirth/miscarriage/NND classification and congenital framework in starsim. These should inform skill updates.

## Mistakes Made

### 1. `modules=` vs `custom=` for non-standard modules (starsim-dev-sim, starsim-dev-demographics)

**What happened**: Used `modules=ss.FetalHealth()` in sim construction. Since v3.2.0, non-standard modules go via `custom=`.

**Fix for skills**: The `starsim-dev-sim` skill should document that `custom=` is the correct kwarg for modules that don't fit standard types (diseases, interventions, demographics, networks, connectors, analyzers). The `modules=` argument still works but auto-relocates.

### 2. ~~Module instances cannot be shared across sims~~ (starsim-dev-sim, starsim-style-tests)

**What happened**: Tried `demog = [ss.Pregnancy(...), ss.Deaths(...)]` and passed the same list to three different sims. Something else went wrong, but we initially blamed module sharing.

**Correction**: This is actually fine — `copy_inputs=True` by default, so starsim deep-copies module instances when initializing. No skill update needed.

### 3. Misleading naming (starsim-style-python)

**What happened**: Named a connector `fetal_tx` when it actually applies disease *damage* to fetal health. "tx" implies treatment. Should have been `fetal_infection` (the thing that connects a disease to fetal damage).

**Lesson**: The style guide says names should be "short but memorable." Memorable includes *not being misleading*. A connector that orchestrates damage from infection should reference "infection" not "treatment" in its name.

### 4. Manual time conversion instead of starsim API (starsim-dev-time)

**What happened**: Used `self.sim.people.age[uids] * 365.25` to convert years to days. Should have used `ss.years(self.sim.people.age[uids]).days`.

**Fix for skills**: Add to `starsim-dev-time`:
```python
# WRONG — manual conversion, fragile
age_days = sim.people.age[uids] * 365.25

# RIGHT — starsim time API, works with arrays
age_days = ss.years(sim.people.age[uids]).days
```

### 5. Stochastic comparison without tolerance (starsim-style-tests)

**What happened**: Compared birth weights across different sims with `assert bw_treated > bw_disease`. With different random streams (fresh module instances per sim), this can fail by small margins. Fixed with `assert bw_treated > bw_disease * (1 - rtol)` where `rtol = 0.05`.

**Note**: The test style guide already mentions generous tolerances, but could emphasize that *directional* comparisons (not just equality) need tolerance too.

### 6. `.values` on starsim arrays (starsim-dev-indexing)

**What happened**: Used `fh.birth_weight[born].values` in plotting code. `ss.Arr` objects *do* have `.values` (like pandas), but indexing an `Arr` with UIDs returns a plain NumPy array (which doesn't have `.values`).

**Fix for skills**: Add to `starsim-dev-indexing`:
```python
# WRONG — indexing with UIDs already returns a plain numpy array
data = arr[uids].values  # AttributeError: numpy array has no .values

# RIGHT — just use the indexed result directly
data = arr[uids]
```

### 7. Removing imports still needed by remaining code (general)

**What happened**: When moving `test_fetal_health` out of `test_demographics.py`, also removed `import matplotlib.pyplot as plt` — but `test_nigeria` still uses `plt`. General lesson: when refactoring, check that remaining code doesn't depend on things being removed.

### 8. Lambda vs named function for readability (starsim-style-python)

**What happened**: Used `demog = lambda: [ss.Pregnancy(...), ss.Deaths(...)]` which was confusing to the user. A named `def demog()` is clearer and more debuggable.

**Lesson**: Starsim style prefers clarity. Lambdas are fine for simple expressions but not for multi-line module construction.

## Skills That Need Updates

1. **starsim-dev-sim**: Document `custom=` kwarg
2. **starsim-dev-time**: Add array time conversion pattern (`ss.years(array).days`)
3. **starsim-dev-indexing**: Note that UID-indexing returns plain numpy (no `.values`)
4. **starsim-dev-demographics**: Reference docs for pregnancy loss classification, NND detection, FetalHealth, congenital framework
5. **starsim-dev-diseases**: Reference docs for generic congenital framework
6. **starsim-style-tests**: Note directional comparison tolerances
