---
name: starsim-dev-distributions
description: Use when working with probability distributions in Starsim — including creating distributions, sampling, dynamic parameters, and using distributions in custom modules.
---

# Starsim Distributions

Starsim wraps statistical distributions in a framework that supports per-agent sampling, dynamic (callable) parameters, and common random numbers (CRN) for low-variance comparisons between simulations. All distributions are created once (typically in `__init__`), initialized automatically by the framework, and then sampled via `rvs(uids)` or filtered via `filter(mask)` during simulation steps. One key advantage of Starsim distributions over raw numpy/scipy calls is that they enable low-variance comparison between simulations through CRN -- each agent gets its own reproducible random stream keyed by UID.

## Available distributions

| Distribution | Starsim constructor | Key parameters | Description |
|---|---|---|---|
| Random | `ss.random()` | (none) | Uniform float in [0, 1] |
| Uniform | `ss.uniform()` | `low`, `high` | Uniform float in [low, high] |
| Normal | `ss.normal()` | `loc`, `scale` | Gaussian with mean `loc` and std `scale` |
| Lognormal (implicit) | `ss.lognormal_im()` | `mean`, `sigma` | Lognormal specified by underlying normal's mean and sigma |
| Lognormal (explicit) | `ss.lognormal_ex()` | `mean`, `std` | Lognormal specified by the distribution's own mean and std |
| Exponential | `ss.expon()` | `scale` | Exponential with mean = `scale` (i.e. 1/lambda) |
| Poisson | `ss.poisson()` | `lam` | Poisson with rate `lam` |
| Negative Binomial | `ss.nbinom()` | `n`, `p` | Negative binomial (n successes, probability p) |
| Weibull | `ss.weibull()` | `c`, `loc`, `scale` | Weibull minimum; `c` = shape, `scale` = lambda |
| Gamma | `ss.gamma()` | `a`, `loc`, `scale` | Gamma; `a` = shape, `scale` = theta |
| Beta | `ss.beta_dist()` | `a`, `b` | Beta distribution with shape params a and b |
| Constant | `ss.constant()` | `v` | Fixed value; useful for testing and fixed params |
| Random Integer | `ss.randint()` | `low`, `high` | Uniform random integer in [low, high) |
| Bernoulli | `ss.bernoulli()` | `p` | Binary outcome with probability `p`; most common for decisions |
| Choice | `ss.choice()` | `a`, `p` | Random selection from list `a` with optional probs `p` |
| Histogram | `ss.histogram()` | `values`, `bins`, `density`, `data` | Sample from an empirical histogram |

Note: `ss.beta_dist()` uses the name `beta_dist` (not `beta`) to avoid collision with the `beta` transmission parameter. You can also create custom distributions by extending the `Dist` class from Starsim. The `ss.choice()` distribution only supports fixed parameters (not dynamic callables).

## Choosing the right distribution

- **Binary decisions** (infection, vaccination, death): `ss.bernoulli(p=...)` -- by far the most common. Use `filter()` to get UIDs of agents where the trial succeeds.
- **Durations** (infection length, incubation period): `ss.lognormal_ex(mean=..., std=...)` or `ss.weibull(c=..., scale=...)`. Use `ss.dur()` to specify durations in human-readable units, e.g. `ss.lognorm_ex(mean=ss.dur(6))`.
- **Counts** (number of contacts): `ss.poisson(lam=...)` or `ss.nbinom(n=..., p=...)`.
- **Continuous values** (viral load, antibody levels): `ss.normal()`, `ss.gamma()`, `ss.beta_dist()`.
- **Fixed values** (debugging, placeholders): `ss.constant(v=...)`.
- **Empirical data**: `ss.histogram(data=...)` to sample from observed data.

## Patterns

### Creating and initializing distributions

Create distributions with `ss.<dist>(...)`. Outside a simulation, pass `strict=False` to avoid warnings. Inside modules, distributions are initialized automatically by the framework.

```python
import starsim as ss
import numpy as np

# Standalone (outside a module)
d = ss.normal(name="My normal", loc=0, scale=1, strict=False)
print(d)

# Inside a module, create in __init__ -- no strict flag needed
# self.define_pars(dur_inf=ss.lognormal_ex(mean=6, std=2))
```

### Sampling with rvs(uids)

Always pass agent UIDs or a boolean mask to `rvs()`. This enables dynamic parameters and CRN support. Passing UIDs means each agent gets a deterministic random draw keyed to their identity, which is essential for reproducibility and CRN-based comparisons.

```python
sim = ss.Sim(n_agents=10).init()
d_sim = ss.randint(name="Example", low=-10, high=10)
d_sim.init(sim=sim)  # Done automatically inside the framework

# Pass a list of agent UIDs (preferred)
draws = d_sim.rvs([3, 5, 2, 9, 4])
print(f"Draws for agents 3, 5, 2, 9, and 4: {draws}")

# Pass a boolean mask (equally valid)
mask = sim.people.age < 25
draws_mask = d_sim.rvs(mask)
print(f"Draws for agents under 25: {draws_mask}")

# Sample for all agents
draws_all = d_sim.rvs(sim.people.uid)
print(f"Draws for all agents: {draws_all}")
```

The return value is always a numpy array with one sample per agent in the input UIDs or mask.

### Filtering with filter(mask)

For Bernoulli and choice distributions, `filter()` samples the distribution and returns the UIDs where the outcome is True (or matches). This is the standard pattern for selecting which agents undergo a transition. Internally, `filter()` calls `rvs()` on the given UIDs, then returns only those UIDs where the draw was True.

`filter()` accepts either a boolean mask or an array of UIDs:

```python
# In a module step() method:
novx = self.vaccinated == False  # Boolean mask
vx_uids = self.pars.p_vx.filter(novx)  # Returns UIDs where Bernoulli sample is True
self.vaccinated[vx_uids] = True

# Equivalently, with a uid array:
uid_array = ss.uids(novx)
vx_uids = self.pars.p_vx.filter(uid_array)
```

This is the workhorse method for probabilistic decisions in Starsim. Almost every intervention, disease progression, and demographic event uses `filter()` with a Bernoulli distribution.

### Visualization

Plot a histogram of samples from any distribution using `plot_hist()`. This draws `n` samples and plots them with the specified number of bins. The method returns the samples so you can inspect them further.

```python
d = ss.normal(loc=0, scale=1, strict=False)
rvs = d.plot_hist(n=1000, bins=30)
```

After running a simulation, inspect a module's distribution to verify it produces the expected shape. This is particularly useful when checking that parameter overrides or dynamic parameters are behaving correctly:

```python
sim = ss.Sim(n_agents=100, diseases=ss.SIR(), networks='random')
sim.run()
rvs = sim.diseases.sir.pars.dur_inf.plot_hist()
```

Important: always access distributions via `sim.diseases.<name>.pars` (not from the original variable) because Starsim copies modules during initialization. The original variable does not have the simulation context and may not produce meaningful samples.

### Extracting statistics

Access the underlying scipy distribution via the `.dist` property. This gives you the full scipy `rv_frozen` object, so all scipy statistical methods are available:

```python
d = ss.normal(loc=0, scale=1, strict=False)
underlying_dist = d.dist
print("Mean:", underlying_dist.mean())
print("Standard Deviation:", underlying_dist.std())
print("95% Interval:", underlying_dist.ppf([0.025, 0.975]))
```

This is useful for sanity-checking distribution parameters before running a simulation, or for reporting distribution summaries in analysis output.

### Setting and updating parameters

Many Starsim modules expose distributions as parameters that users can customize. For example, `ss.SIR` has three distribution parameters:

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `init_prev` | `ss.bernoulli(p=0.01)` | Initial prevalence (who starts infected) |
| `dur_inf` | `ss.lognorm_ex(mean=ss.dur(6))` | Duration of infection |
| `p_death` | `ss.bernoulli(p=0.01)` | Probability of death given infection |

There are two ways to change these. First, use `.set()` to update a single parameter on an existing distribution:

```python
sir = ss.SIR()
sir.pars.p_death.set(p=0.5)  # Update death probability to 50%
```

Second, replace a distribution entirely at construction time by passing a new distribution as a keyword argument:

```python
sir = ss.SIR(
    init_prev=ss.bernoulli(p=0.15),          # 15% initial prevalence
    dur_inf=ss.weibull(c=2, loc=1, scale=2), # Weibull-distributed duration
)
```

Both approaches work. Use `.set()` when you want to tweak one parameter of the default distribution. Use replacement when you want a completely different distribution shape.

### Dynamic parameters

Any distribution parameter can be set to a callable instead of a scalar. This is one of Starsim's most powerful features -- it lets the same distribution produce different values for different agents based on their attributes, the current simulation time, or any other state.

The callable receives three arguments and must return an array of length `len(uids)` or a scalar (which applies uniformly to all agents in this call):

```python
def set_p_by_age(self, sim, uids):
    """Children under 15 have 25% infection probability, adults 10%."""
    p = np.full(len(uids), fill_value=0.10)  # Default 10%
    p[sim.people.age < 15] = 0.25            # 25% for children
    return p

sir = ss.SIR(
    init_prev=ss.bernoulli(p=set_p_by_age),
)
sim = ss.Sim(n_agents=10, diseases=[sir], dur=30)
sim.run()
```

The callable signature is always `(self, sim, uids)` where:
- `self` -- the module that owns the distribution
- `sim` -- the simulation object (access `sim.people`, `sim.ti`, `sim.dt`, etc.)
- `uids` -- array of agent UIDs being processed

Dynamic parameters can also use lambdas for simple cases:

```python
ss.bernoulli(p=lambda self, sim, uids: sim.people.age[uids] / 100.0)
```

You can also use `d.set(loc=callable)` to make a previously-fixed parameter dynamic:

```python
d = ss.normal(loc=0, scale=1)
d.set(loc=lambda self, sim, uids: sim.people.age[uids])  # Now loc varies by age
```

Dynamic parameters work with any distribution parameter (not just `p`). For example, a normal distribution whose mean shifts with simulation time:

```python
ss.normal(
    loc=lambda self, sim, uids: sim.year - 2000,  # Mean increases each year
    scale=1,
)
```

### Using distributions in custom modules

Create distributions in `__init__` using `define_pars()` or as instance attributes. Sample them in `step()` using `rvs(uids)` or `filter(mask)`. The key rule is: distributions are created once during initialization, never during step execution.

```python
class MyVx(ss.Intervention):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_states(
            ss.BoolState('vaccinated', label="Vaccinated", default=False)
        )
        self.define_pars(
            # Create a Bernoulli distribution as a module parameter.
            # The value p=0.1 is a default; users can override it.
            p_vx=ss.bernoulli(p=0.1, name="Vaccination Probability")
        )
        self.update_pars(pars=pars, **kwargs)

        # Distributions can also be created as plain attributes:
        # self.my_dist = ss.normal(loc=0, scale=1)

    def init_results(self):
        super().init_results()
        self.define_results(
            ss.Result('new_vx', dtype=int, label="Newly Vaccinated")
        )

    def step(self):
        novx = self.vaccinated == False  # Boolean mask of unvaccinated
        vx_uids = self.pars.p_vx.filter(novx)  # Bernoulli filter returns UIDs
        self.vaccinated[vx_uids] = True
        sim.diseases.sir.rel_sus[vx_uids] = 0.0
        self.results.new_vx[sim.ti] = len(vx_uids)
```

Users can then override `p_vx` with a dynamic callable at instantiation time, without modifying the source code of `MyVx`:

```python
def p_vx_func(self, sim, uids):
    # Only vaccinate on timestep 5
    if sim.ti != 5:
        return 0.0

    # Probability proportional to age (older = more likely)
    p = sim.people.age[uids] / 100.0
    p = p.clip(0.0, 1.0)
    return p

vx = MyVx(p_vx=ss.bernoulli(p=p_vx_func))
sim = ss.Sim(
    n_agents=1000, dur=10, dt=1, start=0,
    diseases=ss.SIR(),
    interventions=[vx],
    networks=ss.RandomNet(),
)
sim.run()
sim.plot('myvx')  # Plot the custom intervention results
```

This demonstrates the full power of the pattern: the module author provides a sensible default distribution, and the user replaces it with a dynamic callable that incorporates time-dependent and agent-dependent logic.

### The define_pars + filter pattern

This is the most common pattern for interventions and modules that make probabilistic decisions. It appears throughout Starsim's built-in modules (SIR's `init_prev`, `p_death`, etc.) and should be followed in all custom modules:

1. Declare a Bernoulli distribution as a parameter in `__init__` via `define_pars`.
2. In `step()`, build a boolean mask of eligible agents.
3. Call `self.pars.<dist>.filter(mask)` to get the UIDs that pass the probabilistic check.

```python
def __init__(self, pars=None, **kwargs):
    super().__init__()
    self.define_pars(
        p_vx=ss.bernoulli(p=0.1)
    )
    self.update_pars(pars, **kwargs)

def step(self):
    eligible = self.vaccinated == False
    selected = self.pars.p_vx.filter(eligible)
    # selected is a uid array of agents who "passed" the Bernoulli trial
    self.vaccinated[selected] = True
```

This pattern lets users override `p_vx` at instantiation with either a different fixed probability or a dynamic callable, without changing the module source code. For example: `MyModule(p_vx=ss.bernoulli(p=0.5))` or `MyModule(p_vx=ss.bernoulli(p=my_dynamic_func))`.

### Using rvs() for durations and continuous values

While `filter()` is for binary decisions, use `rvs()` when you need continuous samples -- durations, doses, viral loads, etc.:

```python
class MyDisease(ss.SIR):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            dur_exp=ss.lognormal_ex(mean=5, std=2),
        )
        self.update_pars(pars, **kwargs)

    def set_prognoses(self, uids, sources=None):
        super().set_prognoses(uids, sources)
        # Sample a duration for each newly infected agent
        dur_exp = self.pars.dur_exp.rvs(uids)  # Array of durations, one per uid
        self.ti_infected[uids] = self.ti + dur_exp
```

## Anti-patterns

**Do not create distributions inside `step()` or in loops.** Distributions should be created once in `__init__` (via `define_pars` or as attributes). Creating them every timestep wastes resources, breaks CRN tracking, and prevents the framework from properly initializing them. If you need time-varying behavior, use dynamic parameters (callables) instead.

```python
# WRONG -- creating a new distribution every step
def step(self):
    d = ss.bernoulli(p=0.1)  # Do not do this
    uids = d.filter(mask)

# RIGHT -- create once in __init__, use in step
def __init__(self):
    self.define_pars(p_vx=ss.bernoulli(p=0.1))

def step(self):
    uids = self.pars.p_vx.filter(mask)

# RIGHT -- use a dynamic parameter for time-varying behavior
def __init__(self):
    self.define_pars(p_vx=ss.bernoulli(p=lambda self, sim, uids: 0.1 if sim.ti < 5 else 0.5))
```

**Do not pass scalar counts to `rvs()`.** While `d.rvs(5)` technically works, it bypasses CRN and dynamic parameters. Always pass UIDs or a boolean mask. The only exception is exploratory use outside a simulation context (with `strict=False`).

```python
# Avoid in production code
draws = d.rvs(5)

# Prefer -- these support CRN and dynamic parameters
draws = d.rvs(sim.people.uid)
draws = d.rvs([3, 5, 2, 9, 4])
draws = d.rvs(sim.people.age < 25)
```

**Do not use `np.random` directly.** Calling `np.random.random()`, `np.random.choice()`, etc. breaks Starsim's CRN system because the draws are not tied to agent UIDs. Always use `ss.<dist>` instead.

```python
# WRONG -- breaks CRN
outcomes = np.random.random(len(uids)) < 0.5

# RIGHT -- preserves CRN
d = ss.bernoulli(p=0.5)
outcomes = d.filter(uids)
```

**Do not reuse one distribution instance for multiple independent decisions.** Each probabilistic decision should have its own distribution to maintain CRN independence. If two decisions share a distribution object, changing one decision's parameter would unintentionally affect the other.

```python
# WRONG -- same distribution for two different decisions
self.define_pars(p=ss.bernoulli(p=0.1))
# then using self.pars.p for both vaccination AND treatment

# RIGHT -- separate distributions for separate decisions
self.define_pars(
    p_vx=ss.bernoulli(p=0.1),
    p_treat=ss.bernoulli(p=0.3),
)
```

**Do not access distributions from the original variable after `sim.run()`.** Starsim copies modules during initialization. Access distributions from the sim object: `sim.diseases.sir.pars.dur_inf` rather than from the original `sir.pars.dur_inf`, which will not have the simulation context.

## Quick reference

```text
Creating distributions:
  ss.<dist>(param=value, name="...")     # Create a frozen distribution
  self.define_pars(key=ss.<dist>(...))   # As a module parameter (preferred)
  self.my_dist = ss.<dist>(...)          # As a module attribute (alternative)
  ss.<dist>(..., strict=False)           # Standalone use outside sim context

Sampling:
  d.rvs(uids)                           # Returns array of samples (one per uid)
  d.rvs(bool_mask)                       # Same, using a boolean mask
  d.filter(mask)                         # Bernoulli/choice: returns UIDs where True

Updating parameters:
  d.set(param=value)                     # Update parameter in-place
  d.set(param=callable)                  # Set dynamic parameter

Inspecting:
  d.plot_hist(n=1000, bins=30)           # Plot histogram of samples
  d.dist.mean()                          # Mean of underlying scipy distribution
  d.dist.std()                           # Standard deviation
  d.dist.ppf([0.025, 0.975])            # Percentiles / confidence intervals
  print(d)                               # String representation with parameters

Dynamic callable signature:
  def my_func(self, sim, uids):          # Always takes (self, sim, uids)
      return np.array(...)               # Length len(uids), or scalar

Lifecycle:
  1. Create in __init__  -->  define_pars(key=ss.bernoulli(p=0.1))
  2. Framework calls d.init(sim=sim) automatically
  3. Sample in step()    -->  self.pars.key.filter(mask) or .rvs(uids)

Common distributions by use case:
  ss.bernoulli(p=0.1)                    # Binary decisions (infection, vax, death)
  ss.lognormal_ex(mean=6, std=2)         # Durations (infection, incubation)
  ss.weibull(c=2, scale=3)              # Duration / survival analysis
  ss.normal(loc=0, scale=1)              # Symmetric continuous values
  ss.poisson(lam=5)                      # Count data (contacts per day)
  ss.constant(v=5)                       # Fixed value (testing / placeholder)
  ss.uniform(low=0, high=10)             # Uniform continuous range
  ss.randint(low=0, high=10)             # Uniform discrete range

Accessing after sim.run():
  sim.diseases.<name>.pars.<dist>        # Correct (initialized copy)
  original_var.pars.<dist>               # Wrong (uninitialized original)
```
