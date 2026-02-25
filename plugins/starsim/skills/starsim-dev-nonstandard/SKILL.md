---
name: starsim-dev-nonstandard
description: Use when building non-standard Starsim models — including compartmental (ODE-style) models, general-purpose ABMs, or models that don't use the standard disease/network framework.
---

# Nonstandard Starsim Models Reference

Starsim's modular architecture supports more than agent-based disease modeling. By subclassing `ss.Module` directly, you can build compartmental (ODE-style) disease models using scalar state variables, or general-purpose agent-based models (e.g., wealth transfer, ecology) that have nothing to do with infectious disease. This reference covers the patterns for both use cases, including results tracking, custom plotting, and interventions that modify agent properties.

## Key Classes

| Class | Purpose | When to Use |
|-------|---------|-------------|
| `ss.Module` | Base class for any custom model logic | Compartmental models, general-purpose ABMs, any non-disease module |
| `ss.Intervention` | Modifies simulation state at specific times | School closures, policy changes, time-varying parameter shifts |
| `ss.Analyzer` | Collects custom data each timestep without modifying state | Age-stratified tracking, custom histograms |
| `ss.Result` | Declares a named time-series output for a module | Tracking compartment sizes, custom metrics |
| `ss.Sim` | Assembles and runs the model | All simulations |

## Patterns

### Pattern 1: Compartmental SIS Model

For simple disease dynamics where agent-level detail is unnecessary, inherit from `ss.Module` and use scalar state variables instead of per-agent arrays. This avoids the overhead of the `Infection` class, networks, and per-agent state tracking. A three-state compartmental model runs as fast as an ABM with three agents -- roughly 20x faster than the equivalent agent-based SIS.

```python
import starsim as ss
import sciris as sc
import matplotlib.pyplot as plt

class CompSIS(ss.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self.define_pars(
            beta = ss.peryear(0.8),
            init_prev = 0.01,        # Scalar, not a distribution
            recovery = ss.peryear(0.1),
            waning = ss.peryear(0.05),
            imm_boost = 1.0,
        )
        self.update_pars(**kwargs)

        # Scalar state variables instead of per-agent arrays
        self.N = 0
        self.S = 0
        self.I = 0
        self.immunity = 0
        return

    def init_post(self):
        """Finish initialization after sim is set up"""
        super().init_post()
        self.N = len(self.sim.people)
        i0 = self.pars.init_prev
        self.S = self.N * (1 - i0)
        self.I = self.N * i0
        self.immunity = i0
        return

    @property
    def rel_sus(self):
        return 1 - self.immunity

    def step(self):
        """Disease transmission logic each timestep"""
        self.immunity *= (1 - self.pars.waning.to_prob())
        infected = (self.S * self.I / self.N) * (self.pars.beta.to_prob()) * self.rel_sus
        recovered = self.I * self.pars.recovery.to_prob()
        net = infected - recovered
        self.S -= net
        self.I += net
        self.immunity += infected / self.N * self.pars.imm_boost
        return

    def init_results(self):
        """Initialize results"""
        super().init_results()
        self.define_results(
            ss.Result('S', label='Susceptible'),
            ss.Result('I', label='Infectious'),
        )
        return

    def update_results(self):
        """Store the current state"""
        super().update_results()
        self.results['S'][self.ti] = self.S
        self.results['I'][self.ti] = self.I
        return

    def plot(self):
        """Default plot for SIS model"""
        fig = plt.figure()
        res = self.results
        kw = dict(lw=2, alpha=0.7)
        for rkey in ['S', 'I']:
            plt.plot(res.timevec, res[rkey], label=res[rkey].label, **kw)
        plt.legend(frameon=False)
        plt.xlabel('Time')
        plt.ylabel('Number of people')
        plt.ylim(bottom=0)
        sc.boxoff()
        sc.commaticks()
        plt.show()
        return fig

# Run the compartmental simulation
csim = ss.Sim(diseases=CompSIS(), dur=100, dt=0.1, verbose=0.01)
csim.run()
csim.diseases.compsis.plot()
```

Key points in this pattern:

- **`init_post()`**: Use this for any setup that depends on the sim being initialized (e.g., reading `len(self.sim.people)`). Do not put sim-dependent logic in `__init__`.
- **`define_results()` + `update_results()`**: Declare result channels with `ss.Result` in `init_results()`, then write to them each timestep in `update_results()` using `self.ti` (the current time index).
- **`.to_prob()`**: Converts per-year rates to per-timestep probabilities. Always use this on rate parameters (`ss.peryear(...)`) so the model handles any `dt` correctly.
- **Scalar parameters**: Use plain floats for `init_prev`, `recovery`, etc. instead of distributions, since there are no individual agents to sample from.
- **Placed in `diseases=`**: Even though this is not a standard disease, passing it via `diseases=` is fine. The module slot only determines update order.

### Pattern 2: School Closure Intervention

Interventions that modify `rel_sus` and `rel_trans` on disease modules can simulate policy changes like school closures. This pattern targets agents by age and applies changes at specific simulation times.

```python
import numpy as np
import starsim as ss
import matplotlib.pyplot as plt

class close_schools(ss.Intervention):
    """Reduce susceptibility and transmissibility of children"""
    def __init__(self, start=50, stop=80, reduction=0.5):
        super().__init__()
        self.start = start
        self.stop = stop
        self.reduction = reduction
        return

    def step(self):
        disease = self.sim.diseases[0]
        children = self.sim.people.age < 20
        if self.now == self.start:
            disease.rel_sus[children] *= 1 - self.reduction
            disease.rel_trans[children] *= 1 - self.reduction
        elif self.now == self.stop:
            disease.rel_sus[children] = 1.0
            disease.rel_trans[children] = 1.0
        return
```

Key points:

- **`self.now`**: The current simulation time, used to check when to activate/deactivate the intervention.
- **`self.sim.diseases[0]`**: Access the first disease module by index. You can also use `self.sim.diseases.sir` by name.
- **`rel_sus` / `rel_trans`**: Per-agent arrays on disease modules that scale susceptibility and transmissibility. Multiply to reduce; reset to 1.0 to restore.
- **Boolean indexing**: `self.sim.people.age < 20` produces a boolean mask for selecting agents by age.

### Pattern 3: Custom Analyzer for Age-Stratified Tracking

Analyzers collect data without modifying simulation state. Use `init_pre()` for setup that needs access to `self.sim`.

```python
class infections_by_age(ss.Analyzer):
    """Count infections by age group each timestep"""
    def __init__(self, age_bins=(0, 20, 40, 100)):
        super().__init__()
        self.age_bins = age_bins
        self.mins = age_bins[:-1]
        self.maxes = age_bins[1:]
        self.hist = {k: [] for k in self.mins}
        return

    def init_pre(self, sim):
        super().init_pre(sim)
        self.infections = np.zeros(len(self.sim.people.age))
        return

    def step(self):
        age = self.sim.people.age
        disease = self.sim.diseases[0]
        for min, max in zip(self.mins, self.maxes):
            mask = (age >= min) & (age < max)
            self.hist[min].append(disease.infected[mask].sum())
        return
```

### Pattern 4: General-Purpose ABM (Wealth Model)

For models unrelated to disease, subclass `ss.Module` and use numpy arrays for agent properties. The wealth model shows agents transferring units of wealth each timestep.

```python
import numpy as np
import starsim as ss
import matplotlib.pyplot as plt

class WealthModel(ss.Module):
    """A simple wealth transfer model"""

    def init_post(self, bins=10):
        """Define custom model attributes after sim init"""
        super().init_post()
        self.npts = len(self.sim)
        self.n_agents = len(self.sim.people)
        self.wealth = np.ones(self.n_agents)
        self.bins = np.arange(bins + 1)
        self.wealth_dist = np.zeros((self.npts, len(self.bins) - 1))
        return

    def step(self):
        """Transfer wealth between agents"""
        self.wealth_hist()
        givers = self.wealth > 0
        receivers = np.random.choice(self.sim.people.uid, size=givers.sum())
        self.wealth[givers] -= 1
        for receive in receivers:
            self.wealth[receive] += 1
        return

    def wealth_hist(self):
        """Calculate the wealth histogram"""
        ti = self.sim.ti
        self.wealth_dist[ti, :], _ = np.histogram(self.wealth, bins=self.bins)
        return

    def plot(self):
        """Plot final wealth distribution"""
        plt.figure()
        plt.bar(self.bins[:-1], self.wealth_dist[-1, :])
        plt.title('Wealth distribution at final time point')
        plt.xlabel('Wealth')
        plt.ylabel('Number of agents')
        plt.show()
        return

# Create and run
wealth = WealthModel()
sim = ss.Sim(
    n_agents=100,
    start=0,
    stop=100,
    demographics=wealth,  # General modules can go in any slot
    copy_inputs=False,     # Lets us access wealth object after run
)
sim.run()
wealth.plot()
```

Key points:

- **Module placement**: General-purpose modules can be passed via `demographics=`, `diseases=`, or `modules=`. The slot determines update order within the timestep (demographics runs first, then diseases, etc.). Choose whichever is appropriate for your use case.
- **`copy_inputs=False`**: By default, `ss.Sim` deep-copies all input objects. Set `copy_inputs=False` when you need to access the original module object's state after the run (e.g., `wealth.plot()` on the same object you passed in).
- **Numpy arrays for agent properties**: Use `np.ones(n_agents)` and similar for per-agent state. Access agent UIDs via `self.sim.people.uid`.
- **Custom `plot()` method**: Define a `plot()` method on your module for convenient visualization. Call it via `sim.demographics.wealthmodel.plot()` or on the original object if `copy_inputs=False`.

## Combining a Full Model

The school closure example shows how to combine a standard ABM disease with custom interventions and analyzers:

```python
import pandas as pd
import starsim as ss

sim = ss.Sim(
    people=ss.People(n_agents=20_000, age_data=pd.read_csv('age_data.csv')),
    diseases=dict(
        type='sir',
        init_prev=0.001,
        beta=ss.perday(1/100),
        dur_inf=ss.days(20.0),
    ),
    networks='random',
    interventions=close_schools(start=50, stop=80, reduction=0.5),
    analyzers=infections_by_age(),
    start=ss.days(0),
    dur=ss.days(300),
    dt=ss.days(1.0),
    verbose=False,
)
sim.run()
sim.analyzers.infections_by_age.plot()
```

## Anti-Patterns and Gotchas

**Do not** put sim-dependent logic in `__init__`. The sim does not exist yet during `__init__`. Use `init_post()` (for modules) or `init_pre(sim)` (for analyzers/interventions) instead:

```python
# WRONG -- self.sim is not available in __init__
class Bad(ss.Module):
    def __init__(self):
        super().__init__()
        self.N = len(self.sim.people)  # Error: self.sim is None

# CORRECT -- use init_post
class Good(ss.Module):
    def init_post(self):
        super().init_post()
        self.N = len(self.sim.people)
```

**Do not** forget `super().init_post()` / `super().init_results()` / `super().update_results()`. Omitting the super call will break the module initialization chain.

**Do not** use raw rates as probabilities. Always convert with `.to_prob()`:

```python
# WRONG -- treats per-year rate as per-step probability
infected = S * I / N * self.pars.beta

# CORRECT -- converts rate to probability for current dt
infected = S * I / N * self.pars.beta.to_prob()
```

**Do not** assume `copy_inputs=False` is the default. If you create a module, pass it to `Sim()`, run, and then try to read state from the original object, you will see the pre-run state unless you set `copy_inputs=False`:

```python
# WRONG -- wealth object is a copy; original is unchanged
wealth = WealthModel()
sim = ss.Sim(demographics=wealth)
sim.run()
wealth.wealth  # Still all ones -- this is the original, not the copy

# CORRECT
sim = ss.Sim(demographics=wealth, copy_inputs=False)
sim.run()
wealth.wealth  # Now contains post-run state
```

**Do not** forget that compartmental models still need a `People` object. Even though agents are not individually tracked, `ss.Sim` creates `People` and `len(self.sim.people)` gives the population size for compartmental math.

**Do not** use networks with compartmental models. Compartmental models handle transmission via scalar math, not network contacts. Adding a network is unnecessary overhead.

## Quick Reference

| Task | Code |
|------|------|
| Inherit for custom module | `class MyModel(ss.Module)` |
| Define parameters | `self.define_pars(beta=ss.peryear(0.8))` |
| Post-init setup | Override `init_post(self)`, call `super().init_post()` |
| Declare results | `self.define_results(ss.Result('S', label='Susceptible'))` |
| Store result each step | `self.results['S'][self.ti] = self.S` |
| Convert rate to probability | `self.pars.beta.to_prob()` |
| Access sim time index | `self.ti` or `self.sim.ti` |
| Access current time | `self.now` or `self.sim.t.now()` |
| Access population size | `len(self.sim.people)` |
| Access agent UIDs | `self.sim.people.uid` |
| Access agent ages | `self.sim.people.age` |
| Modify susceptibility | `disease.rel_sus[mask] *= 0.5` |
| Modify transmissibility | `disease.rel_trans[mask] *= 0.5` |
| Place module in sim | `ss.Sim(demographics=mod)` or `diseases=` or `modules=` |
| Keep reference to module | `ss.Sim(..., copy_inputs=False)` |
| Access module post-run | `sim.diseases.compsis.results` |
| Run compartmental model | `ss.Sim(diseases=CompSIS(), dur=100, dt=0.1)` |
| Per-year rate parameter | `ss.peryear(0.8)` |
| Per-day rate parameter | `ss.perday(1/100)` |
| Duration in days | `ss.days(20.0)` |
