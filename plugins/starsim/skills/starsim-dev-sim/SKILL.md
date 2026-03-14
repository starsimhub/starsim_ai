---
name: starsim-dev-sim
description: Use when configuring the Sim object, People, parameters, partial runs, or understanding the simulation execution order.
---

# Sim, People, and Parameters

The `Sim` class orchestrates every Starsim simulation: it initializes modules, controls execution order, and collects results. `People` holds all agent states (age, sex, alive, disease states). Parameters are defined with `define_pars()` and updated with `update_pars()`, using distribution objects that support callable values for age- or time-dependent behavior.

## Creating and Initializing a Sim

When you create a sim with `sim = ss.Sim()`, the resulting object is mostly empty with a few pre-set defaults. Most initialization happens when `sim.init()` is called (which `sim.run()` does automatically). Initialization performs these steps:

1. Validates parameters
2. Adds a `Time` module (`sim.t`) that handles timestep conversions
3. Adds `People` to the sim (creates default people with age/sex structure if not supplied)
4. Adds parameters and results from each `Module` to the sim, and adds states from each module to `People`
5. Initializes all distributions contained within parameters or states

You can pass parameters as keyword arguments or as a dict:

```python
import starsim as ss

# Keyword style
sim = ss.Sim(diseases='sir', networks='random', start=2000, stop=2050)

# Dict style (useful for reuse across scenarios)
pars = dict(start=2000, stop=2050, diseases='sis', networks='random', verbose=0)
sim = ss.Sim(pars, interventions=my_intervention)
```

## Key Classes

| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `ss.Sim` | Run simulation, manage modules | `diseases`, `networks`, `demographics`, `interventions`, `start`, `stop`, `n_agents`, `verbose` |
| `ss.People` | Store agent states and arrays | `n_agents`, `age_data`, `extra_states` |
| `ss.BoolState` | Boolean per-agent state | `name`, `default` |
| `ss.FloatArr` | Numeric per-agent array | `name`, `default`, `label` |
| `ss.Loop` | Internal execution plan (via `sim.loop`) | Access with `to_df()`, `plot()` |

## Sim Execution Order

This is the step order on every timestep. Understanding it is critical for writing correct modules and interventions.

```
 1. start_step        -- Advance RNGs
 2. Demographics      -- Births, aging, background death
 3. Disease.step_state -- Disease progression (BEFORE transmission)
 4. Connectors        -- Multi-disease interactions
 5. Networks          -- Update contacts
 6. Interventions     -- Vaccines, treatment, screening
 7. Disease.step      -- Transmission
 8. People.step_die   -- Reconcile deaths across all modules
 9. Results           -- Update result arrays
10. Analyzers         -- Custom analysis
11. finish_step       -- Cleanup
```

Disease has two separate calls: `step_state` (progression, e.g. infected to recovered) runs before transmission in `step`. This means interventions that modify `rel_trans` will affect transmission in the same timestep.

**Why this order matters:** Consider a woman infected with pre-symptomatic COVID who, in a single day, starts developing symptoms, takes a COVID test, moves house, and becomes pregnant. Starsim orders her day as: (1) become pregnant (demographics), (2) develop symptoms (disease state), (3) move house (network), (4) transmit COVID to contacts in her *new* household (disease transmission), (5) get tested (intervention/analyzer). Demographics run first so that mother-to-child transmission is captured -- if a woman becomes pregnant and acquires malaria in the same month, the effects of malaria on pregnancy are modeled. Networks update before transmission so that new partnerships can transmit immediately, which is especially important for sexually transmitted infections.

**Timestep flexibility:** Starsim allows different modules to run at different timesteps. For example, demographics might update yearly while disease modules update monthly or daily. The `Loop` class manages scheduling each module at its correct frequency.

Example from the SIR `step_state`:

```python
def step_state(self):
    """Progress infectious -> recovered"""
    recovered = (self.infected & (self.ti_recovered <= self.ti)).uids
    self.infected[recovered] = False
    self.susceptible[recovered] = True
    self.update_immunity()
```

### Inspecting the execution plan

After initializing a sim, inspect what runs and when:

```python
sim = ss.Sim(diseases='sir', networks='random', demographics=True)
sim.init()
sim.loop.to_df()   # DataFrame of every step
sim.loop.plot()     # Visual timeline
```

## Patterns

### Basic sim creation and run

String shorthand names like `'sir'`, `'sis'`, `'random'` are resolved to their full class equivalents (`ss.SIR()`, `ss.SIS()`, `ss.RandomNet()`). Use explicit class instances when you need to configure parameters.

```python
import starsim as ss

# String shorthand -- uses all defaults
sim = ss.Sim(diseases='sis', networks='random')
sim.run()

# Explicit classes -- configure parameters
sim = ss.Sim(
    diseases=ss.SIS(beta=0.05, init_prev=0.02),
    networks=ss.RandomNet(n_contacts=4),
    start=2000,
    stop=2050,
    n_agents=5000,
    verbose=0,
)
sim.run()
sim.plot()
```

Multiple diseases and networks can be passed as lists:

```python
sim = ss.Sim(
    diseases=[ss.SIR(beta=0.1), ss.SIS(beta=0.05)],
    networks=[ss.RandomNet(), ss.MFNet()],
)
```

### Labeling sims

Use `sim.label` to identify simulations in plots and when running multiple scenarios:

```python
sim = ss.Sim(diseases='sir', networks='random', label='Baseline')
sim.run()
sim.plot()  # Title includes 'Baseline'
```

Labels can be set at creation or modified later (e.g., before branching):

```python
for beta in [0.01, 0.05]:
    s = base_sim.copy()
    s.label = f'beta={beta}'
```

### Verbose control

Control how often progress is printed:

```python
sim.run(verbose=1)      # Every timestep
sim.run(verbose=0.1)    # Every 10 timesteps
sim.run(verbose=1/12)   # ~Yearly for monthly timesteps
sim.run(verbose=1/365)  # ~Yearly for daily timesteps
sim.run(verbose=-1)     # Only on completion
```

### Partial runs and branching

Run a sim partway, then copy and branch into scenarios. This avoids re-simulating a shared burn-in period. Common use cases for `sim.run(until=)`:

- Run a burn-in period once, then copy and test multiple intervention scenarios
- Inspect the mid-run state of a simulation interactively
- Modify simulation state before continuing (though an `Intervention` is usually cleaner)

Note: copying a simulation can sometimes take almost as much time as running it, so time savings are greatest with long burn-in periods or many scenarios.

```python
import starsim as ss

base_sim = ss.Sim(
    diseases='sis', networks='random',
    start=2000, stop=2100, verbose=False,
)
base_sim.run(until=2030)

sims = []
betas = [0.01, 0.02, 0.05, 0.10]
for beta in betas:
    sim = base_sim.copy()
    sim.diseases.sis.pars.beta = beta
    sim.label = f'beta={beta}'
    sims.append(sim)

msim = ss.parallel(sims)
msim.plot()
```

You can also branch with different interventions:

```python
class sis_vaccine(ss.Intervention):
    def __init__(self, start=2040, eff=1.0):
        super().__init__()
        self.start = start
        self.eff = eff

    def step(self):
        sis = self.sim.diseases.sis
        if sis.now == self.start:
            sis.rel_trans[:] *= 1 - self.eff

pars = dict(start=2000, stop=2050, diseases='sis', networks='random', verbose=0)
sim = ss.Sim(pars, interventions=sis_vaccine())
sim.run(until=2039)

sims = []
for eff in [0.0, 0.2, 0.5, 0.8, 1.0]:
    s = sim.copy()
    s.label = f'Efficacy={eff}'
    s.interventions[0].eff = eff
    sims.append(s)

sims = ss.parallel(sims)
sims.plot()
```

## People

### Default states

Every `People` instance comes with these built-in states:

| State | Type | Description |
|-------|------|-------------|
| `alive` | `State` (bool) | Whether agent is alive |
| `female` | `State` (bool) | Whether agent is female |
| `age` | `FloatArr` | Agent age |
| `ti_dead` | `FloatArr` | Time of death (NaN if alive) |
| `scale` | `FloatArr` | Number of real people each agent represents (default 1) |

### The Arr class and dynamic arrays

Starsim uses custom `Arr` classes (not plain NumPy arrays) for all per-agent data. The two fundamental types are `BoolState` (boolean) and `FloatArr` (numeric -- no int/float distinction). These are optimized for three things common to agent-based models:

1. **Dynamic growth**: As births add agents, arrays grow automatically without costly concatenation
2. **Smart indexing**: Dead agents remain in arrays (for post-mortem analysis) but are automatically excluded from operations like `.mean()`, `.sum()`, iteration
3. **Stochastic initialization**: States can be initialized from distributions (e.g., sex drawn as Bernoulli)

The `Arr` class supports standard NumPy-like arithmetic: sums, means, boolean operations, indexing with UID arrays, and broadcasting.

### UIDs and active agents

Each agent has a `uid` (universal identifier) corresponding to its position in the array. Starsim tracks `auids` (active UIDs) for agents still alive/participating. Dead agents stay in arrays but are excluded from most operations automatically.

```python
sim = ss.Sim(n_agents=1000, diseases='sir', networks='random',
             demographics=True, verbose=False)
sim.run()

ppl = sim.people
print('Agents alive:', len(ppl))
print('Max UID:', ppl.uid.max())
print('Raw array size:', len(ppl.uid.raw))  # Includes dead agents
print('Mean age (alive only):', ppl.age.mean())
```

### Creating custom people

Rather than relying on `Sim` to create people automatically, you can create `People` separately and pass them in. This is useful for specifying a particular age/sex distribution or adding custom attributes.

```python
import starsim as ss

# Equivalent to ss.Sim(n_agents=1000)
people = ss.People(1000)
sim = ss.Sim(people=people)
```

Use `copy_inputs=False` when passing a pre-built `People` object to avoid an unnecessary deep copy (which can be slow for large populations).

Supply age distribution data from a CSV to match a specific country:

```python
import pandas as pd
import starsim as ss

age_data = pd.read_csv('nigeria_age.csv')
ppl = ss.People(n_agents=10_000, age_data=age_data)
sim = ss.Sim(people=ppl, copy_inputs=False).init()
ppl.plot_ages()
```

### Adding custom states with extra_states

Custom states let you track additional per-agent attributes beyond the defaults. The `default` can be a static value, a callable that receives `n` (population size) and returns an array, or a distribution.

```python
import numpy as np
import starsim as ss

# Boolean state with callable default
def urban_function(n):
    return np.random.choice([True, False], p=[0.5, 0.5], size=n)

urban = ss.BoolState('urban', default=urban_function)
ppl = ss.People(10, extra_states=urban)
sim = ss.Sim(people=ppl)
sim.init()  # Essential: this triggers state sampling
print(f'Urban agents: {np.count_nonzero(sim.people.urban)}')
```

You can pass multiple extra states as a list:

```python
extra = [
    ss.BoolState('urban', default=urban_function),
    ss.FloatArr('income', default=50_000),
]
ppl = ss.People(1000, extra_states=extra)
```

Note that `sim.init()` (or `sim.run()`) must be called before states are populated. Before initialization, the state arrays are empty.

### Module-added states

When modules (diseases, demographics, etc.) are added to a sim, their states are automatically registered on `People` under the module name. You do not need to define these states manually -- the module handles it.

```python
sim = ss.Sim(people=ss.People(30), diseases=ss.SIS(init_prev=0.1),
             networks=ss.RandomNet())
sim.run()

# Access disease states through people.<module_name>.<state>
print(f'Infected: {sim.people.sis.infected.sum()}')
print(f'Susceptible: {sim.people.sis.susceptible.sum()}')
```

Standard array operations work on these states since `Arr` supports NumPy-like arithmetic:

```python
# Boolean filtering
infected_uids = sim.people.sis.infected.uids
ages_of_infected = sim.people.age[infected_uids]

# Combined boolean operations
young_infected = sim.people.sis.infected & (sim.people.age < 20)
```

### Inspecting people

Export all agent data to a DataFrame:

```python
df = sim.people.to_df()
df.disp()
```

The DataFrame is useful for summary statistics and visualization:

```python
import matplotlib.pyplot as plt
plt.scatter(df['sis.ti_recovered'], df['sis.immunity'])
plt.xlabel('Time of recovery')
plt.ylabel('Immunity')
plt.show()
```

Inspect a single agent by UID (returns all attributes as a dict-like view):

```python
sim.people.person(10)  # All attributes for agent with uid=10
```

## Parameters

### The define_pars / update_pars pattern

Modules define default parameter formats in `__init__` using `define_pars()`, then accept user overrides via `update_pars()`. The purpose of `define_pars()` is to set the ground truth format for parameters. When users enter their own parameter values, `update_pars()` checks them for consistency with the original format. This is especially important for Bernoulli distributions, which are type-locked.

```python
class MySIR(ss.SIR):
    def __init__(self, **kwargs):
        super().__init__()
        self.define_pars(
            beta       = ss.peryear(0.1),
            init_prev  = ss.bernoulli(p=0.01),
            dur_inf    = ss.lognorm_ex(mean=ss.years(6)),
            p_death    = ss.bernoulli(p=0.01),
        )
        self.update_pars(**kwargs)

        self.define_states(
            ss.BoolState('susceptible', default=True, label='Susceptible'),
            ss.BoolState('infected', label='Infectious'),
            ss.BoolState('recovered', label='Recovered'),
            ss.FloatArr('ti_infected', label='Time of infection'),
            ss.FloatArr('ti_recovered', label='Time of recovery'),
            ss.FloatArr('ti_dead', label='Time of death'),
            ss.FloatArr('rel_sus', default=1.0, label='Relative susceptibility'),
            ss.FloatArr('rel_trans', default=1.0, label='Relative transmission'),
            reset=True,
        )
```

Note the `define_states()` call alongside `define_pars()`. States are the per-agent arrays that track disease progression. The `reset=True` flag means "do not inherit any states from the parent class -- define them fresh." Each state becomes accessible as `sim.people.<module_name>.<state_name>` after initialization.

### Distribution types

| Distribution | Usage | Notes |
|-------------|-------|-------|
| `ss.bernoulli(p=0.01)` | Binary outcomes (infection, death) | Type-locked: cannot change to another distribution type |
| `ss.peryear(0.1)` | Per-year rate (auto-converts to per-timestep) | Common for beta; handles timestep conversion automatically |
| `ss.lognorm_ex(mean=X)` | Lognormal parameterized by mean (not log-mu) | Use for durations; more intuitive than raw lognormal |
| `ss.normal(loc=X)` | Normal distribution | General purpose; `loc` is mean, `scale` is std |
| `ss.years(N)` | Convert N years to sim time units | Use inside distributions for timestep-independent durations |

`ss.peryear` is especially important: it automatically converts a per-year rate to per-timestep probability based on the sim's `dt`. For example, `ss.peryear(0.1)` with monthly timesteps (`dt=1/12`) converts to approximately `0.1/12` per step. This means your model parameters stay human-readable regardless of timestep resolution.

`ss.lognorm_ex` takes `mean` instead of the log-space `mu` parameter, which is more intuitive for epidemiological parameters like "mean duration of infection is 6 years."

### Updating parameters

Users can pass plain numbers for Bernoulli parameters -- Starsim wraps them automatically:

```python
sir1 = MySIR(p_death=0.02)                   # Scalar -> auto-wrapped as bernoulli(p=0.02)
sir2 = MySIR(p_death=ss.bernoulli(p=0.2))    # Explicit distribution
```

Non-Bernoulli distributions can be changed to a different distribution type:

```python
sir3 = MySIR(dur_inf=ss.normal(4))  # OK: lognorm_ex -> normal
```

### Callable parameters (age/time-dependent)

Any distribution parameter can accept a callable with signature `lambda self, sim, uids: ...`. This enables age-dependent, time-dependent, or state-dependent behavior.

```python
import starsim as ss

sir = ss.SIR(dur_inf=ss.normal(loc=ss.years(10)))
sir.pars.dur_inf.set(loc=lambda self, sim, uids: sim.people.age[uids] / 10)

sim = ss.Sim(n_agents=20_000, dur=10, diseases=sir, networks='random')
sim.run()
```

The callable receives `self` (the distribution), `sim` (the simulation), and `uids` (array of agent UIDs being sampled). It must return a value or array broadcastable to the UIDs. Using this pattern, any parameter can depend on anything the sim is aware of, including time, agent age, sex, or health attributes.

Example -- age-dependent duration produces more infections in younger people (shorter recovery means less time infectious, but age-scaling creates interesting dynamics):

```python
import matplotlib.pyplot as plt
import starsim as ss

sir = ss.SIR(dur_inf=ss.normal(loc=ss.years(10)))
sir.pars.dur_inf.set(loc=lambda self, sim, uids: sim.people.age[uids] / 10)
sim = ss.Sim(n_agents=20_000, dur=10, diseases=sir, networks='random')
sim.run()

# Visualize age distribution of infections
ages = sim.people.age[:]
infected_ages = ages[sim.diseases.sir.infected]
plt.hist(infected_ages, bins=range(0, 100, 5))
plt.xlabel('Age')
plt.ylabel('Number infected')
plt.show()
```

Example -- time-dependent transmission rate:

```python
sir = ss.SIR(beta=ss.peryear(0.1))
sir.pars.beta.set(p=lambda self, sim, uids: 0.2 if sim.year < 2030 else 0.05)
```

## Accessing Results

After running a simulation, results are available via `sim.results` and per-module:

```python
sim = ss.Sim(diseases='sir', networks='random', demographics=True, verbose=False)
sim.run()

# People-level results
print('Cumulative births:', sim.results.births.cumulative[-1])
print('Cumulative deaths:', sim.results.cum_deaths[-1])

# Disease-level results
print('New infections (last step):', sim.results.sir.new_infections[-1])
```

Use `sim.plot()` to get a default multi-panel figure of key results. Individual result arrays can be plotted manually for custom visualizations.

## Anti-patterns

**Do not call `sim.init()` manually unless exploring.**

```python
# WRONG -- unnecessary manual init before run
sim = ss.Sim(diseases='sir', networks='random')
sim.init()  # Not needed; run() does this automatically
sim.run()

# RIGHT -- just run
sim = ss.Sim(diseases='sir', networks='random')
sim.run()

# OK -- manual init for inspection only
sim = ss.Sim(diseases='sir', networks='random')
sim.init()
print(sim.loop.to_df())  # Inspect execution plan
# Then run separately if needed
sim.run()
```

**Do not mix default access and `.raw` carelessly.**

```python
ppl = sim.people

# Default access: only alive agents
print(ppl.age.mean())      # Mean age of alive agents
print(len(ppl))             # Count of alive agents

# .raw access: ALL agents including dead
print(len(ppl.uid.raw))     # Total agents ever created (alive + dead)
print(ppl.age.raw.mean())   # Mean age including dead -- usually not what you want
```

Use `.raw` only when you explicitly need dead/removed agents, such as for post-mortem analysis or validating total population accounting.

**Do not reuse module instances across multiple sims.** Starsim modules (diseases, demographics, interventions, etc.) are mutated during `sim.init()` — they get bound to a specific sim, their states are initialized, distributions are seeded, etc. Passing the same module instances to multiple sims will cause failures or incorrect results.

```python
# WRONG — modules are mutated during init, can't be reused
demog = [ss.Pregnancy(), ss.Deaths()]
sim1 = ss.Sim(demographics=demog).run()
sim2 = ss.Sim(demographics=demog).run()  # Fails or gives wrong results

# RIGHT — use a factory function to create fresh instances
def make_demog():
    return [ss.Pregnancy(), ss.Deaths()]

sim1 = ss.Sim(demographics=make_demog()).run()
sim2 = ss.Sim(demographics=make_demog()).run()
```

**Use `custom=` for non-standard modules, not `modules=`.** Since v3.2.0, modules that don't fit standard types (diseases, interventions, demographics, networks, connectors, analyzers) should be passed via `custom=`. The `modules=` argument still works but auto-relocates modules to the appropriate attribute.

```python
# Preferred
sim = ss.Sim(custom=ss.FetalHealth())

# Also works but less explicit
sim = ss.Sim(modules=ss.FetalHealth())
```

**Do not modify parameters after `sim.init()` expecting re-sampling.** Distributions are sampled during initialization. Changing a parameter value after `init()` affects only future samples (e.g., for newly born agents), not already-initialized agent states. If you need to change behavior mid-run, use an intervention or modify the state arrays directly.

**Do not change Bernoulli distributions to other types.**

```python
# WRONG -- will raise an error
sir = MySIR(p_death=ss.lognorm_ex(4))  # p_death was defined as bernoulli

# RIGHT -- pass a scalar (auto-wrapped) or another bernoulli
sir = MySIR(p_death=0.02)
sir = MySIR(p_death=ss.bernoulli(p=0.02))

# OK -- non-Bernoulli distributions CAN be changed
sir = MySIR(dur_inf=ss.normal(4))  # dur_inf was defined as lognorm_ex
```

Bernoulli distributions are type-locked because they have unique methods like `filter()` that other distributions lack. Other distribution types (lognormal, normal, etc.) can be freely swapped.

## Common Patterns Summary

| Task | Code |
|------|------|
| Create sim with defaults | `ss.Sim(diseases='sir', networks='random')` |
| Set population size | `ss.Sim(n_agents=10_000)` |
| Set time range | `ss.Sim(start=2000, stop=2050)` |
| Add demographics | `ss.Sim(demographics=True)` or `ss.Sim(demographics=ss.Pregnancy())` |
| Partial run | `sim.run(until=2030)` |
| Branch scenarios | `sim2 = sim.copy(); sim2.run()` |
| Parallel runs | `ss.parallel([sim1, sim2, sim3])` |
| Inspect execution | `sim.init(); sim.loop.to_df()` |
| People to DataFrame | `sim.people.to_df()` |
| Single agent info | `sim.people.person(uid)` |
| Access disease state | `sim.people.sir.infected` |
| Custom people state | `ss.People(n, extra_states=ss.BoolState('name', default=fn))` |
| Callable parameter | `dist.set(loc=lambda self, sim, uids: ...)` |

## Quick Reference

```python
import numpy as np
import starsim as ss

# --- Sim creation and running ---
sim = ss.Sim(diseases='sir', networks='random', n_agents=10_000)
sim.run()
sim.plot()

# Partial run + branch into scenarios
sim = ss.Sim(diseases='sis', networks='random', start=2000, stop=2100)
sim.run(until=2050)
s2 = sim.copy()
s2.diseases.sis.pars.beta = 0.05
s2.run()

# Parallel execution of multiple sims
sims = [ss.Sim(diseases='sir', networks='random', label=f'beta={b}')
        for b in [0.01, 0.05, 0.1]]
msim = ss.parallel(sims)
msim.plot()

# --- Execution inspection ---
sim = ss.Sim(diseases='sir', networks='random', demographics=True)
sim.init()
sim.loop.to_df()    # Full execution plan as DataFrame
sim.loop.plot()     # Visual timeline of all module steps

# --- People inspection ---
sim.people.to_df()           # All agent data as DataFrame
sim.people.person(0)         # Single agent's full attribute set
len(sim.people)              # Number of alive agents
len(sim.people.uid.raw)      # Total agents ever created (alive + dead)
sim.people.age.mean()        # Mean age (alive only, automatic)

# --- Custom states on People ---
urban = ss.BoolState('urban', default=lambda n: np.random.rand(n) > 0.5)
ppl = ss.People(1000, extra_states=urban)
sim = ss.Sim(people=ppl)
sim.init()

# --- Disease module states ---
sim.people.sir.infected.sum()        # Count of currently infected
sim.people.sir.infected.uids         # UIDs of infected agents
sim.people.sir.ti_recovered          # Time of recovery array

# --- Callable parameters ---
sir = ss.SIR(dur_inf=ss.normal(loc=ss.years(10)))
sir.pars.dur_inf.set(loc=lambda self, sim, uids: sim.people.age[uids] / 10)

# --- Results after running ---
sim.results.sir.new_infections       # Array of new infections per timestep
sim.results.births.cumulative[-1]    # Total births over simulation
```
