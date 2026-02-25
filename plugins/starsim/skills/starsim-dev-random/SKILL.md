---
name: starsim-dev-random
description: Use when working with random number generation in Starsim — including Common Random Numbers (CRN), distribution usage patterns, and reproducibility.
---

# Starsim Random Number Reference

Starsim implements Common Random Numbers (CRN), a technique that assigns each agent its own deterministic random number stream for each decision. This eliminates "stochastic branching" noise -- the problem where changing one agent's behavior inadvertently changes every other agent's random draws. CRN enables noise-free comparison of scenarios so that differences in outcomes reflect only the intended parameter or intervention changes.

For technical details, see: [Klein et al., "Noise-free comparison of stochastic agent-based simulations using common random numbers." arXiv:2409.02086 (2024).](https://arxiv.org/abs/2409.02086)

## Key Concepts

| Concept | Description |
|---------|-------------|
| CRN (Common Random Numbers) | Each agent gets the same random draw for the same decision across simulations, regardless of what other agents do. Enabled by default. |
| `ss.options.single_rng` | When `False` (default), CRN is active with per-agent streams. When `True`, all agents share one PRNG (legacy mode, stochastic branching occurs). |
| Stochastic branching | The problem CRN solves: with a single PRNG, removing or adding one agent shifts the random number sequence for all subsequent agents. |
| `rand_seed` | Sim-level seed for reproducibility. Same seed + same config = identical results. |
| `dist.rvs(uids)` | Draw random values for specific agents identified by UIDs. CRN ensures agent N always gets the same draw for this distribution. |
| `dist.filter(uids)` | For Bernoulli/choice distributions, returns the subset of UIDs where the trial succeeded. |
| Dynamic callable | A function `(self, sim, uids) -> array` passed as a distribution parameter, evaluated fresh each step. |

## Patterns

### CRN is on by default -- no setup needed

CRN is the default behavior. You only need to take action if you want to disable it (which you almost never should).

```python
import starsim as ss

# CRN is active by default (ss.options.single_rng = False)
sim = ss.Sim(diseases='sir', networks='random', rand_seed=42)
sim.run()
```

### The fishing example: why CRN matters

This module demonstrates the problem CRN solves. Each agent independently decides whether to go fishing and whether they catch a fish. Agents do not interact. Banning one agent from fishing should have zero effect on other agents.

```python
import starsim as ss

class Fishing(ss.Module):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            p_fishing = ss.bernoulli(p=0.5),
            p_catch = ss.bernoulli(p=0.2),
            banned_uids = [],
        )
        self.update_pars(pars=pars, **kwargs)
        self.define_states(
            ss.BoolState('fish_caught', default=0)
        )
        return

    def step(self):
        going_fishing_uids = self.pars.p_fishing.filter()
        going_fishing_uids = going_fishing_uids.remove(self.pars.banned_uids)
        catch_uids = self.pars.p_catch.filter(going_fishing_uids)
        self.fish_caught[catch_uids] = self.fish_caught[catch_uids] + 1
        return
```

Without CRN (`single_rng=True`), banning agent 0 changes which random numbers every other agent receives, producing nonsensical differences. With CRN (default), banning agent 0 only affects agent 0 -- all other agents behave identically.

```python
pars = dict(n_agents=20, start=ss.days(0), dur=ss.days(1), rand_seed=42)

# WITHOUT CRN -- demonstrates the stochastic branching problem
ss.options.single_rng = True
simA = ss.Sim(modules=Fishing(), **pars)
simA.run()
simB = ss.Sim(modules=Fishing(banned_uids=[0]), **pars)
simB.run()
# Result: Different agents catch fish in A vs B -- wrong!

# WITH CRN (default) -- correct behavior
ss.options.single_rng = False
simA = ss.Sim(modules=Fishing(), **pars)
simA.run()
simB = ss.Sim(modules=Fishing(banned_uids=[1]), **pars)
simB.run()
# Result: Only agent 1's outcomes differ -- correct!
```

### Create distributions once in `__init__`

Distributions must be created once and reused. Each distribution maintains its own CRN state.

```python
class MyModule(ss.Module):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            p_event = ss.bernoulli(p=0.3),
            dur_event = ss.lognormal(mean=5, std=1),
        )
        self.update_pars(pars=pars, **kwargs)
        return
```

### Pass UIDs or masks to `rvs()`, never scalar counts

CRN works by mapping random draws to specific agent UIDs. Passing a scalar integer loses this mapping.

```python
def step(self):
    all_uids = self.sim.people.auids

    # CORRECT: pass UIDs -- each agent gets its deterministic draw
    values = self.pars.dur_event.rvs(all_uids)

    # CORRECT: pass a boolean mask
    mask = (self.infected) & (self.ti >= self.ti_next_event)
    values = self.pars.dur_event.rvs(mask)
```

### Use `filter()` for Bernoulli and choice decisions

`filter()` returns the UIDs where the Bernoulli trial succeeded, which is more convenient than calling `rvs()` and comparing.

```python
def step(self):
    going_fishing_uids = self.pars.p_fishing.filter()          # test all agents
    catch_uids = self.pars.p_catch.filter(going_fishing_uids)  # test subset
```

### Use dynamic callables for time-varying parameters

When distribution parameters change each step (e.g., age-dependent probabilities), pass a callable instead of updating the parameter manually.

```python
def dynamic_p(self, sim, uids):
    p = np.full_like(uids, fill_value=0.5, dtype=float)
    p[sim.people.age[uids] < 18] = 0.1
    return p

class MyModule(ss.Module):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            p_event = ss.bernoulli(p=dynamic_p),
        )
        self.update_pars(pars=pars, **kwargs)
        return

    def step(self):
        # dynamic_p is called automatically with current sim state
        event_uids = self.pars.p_event.filter(mask)
```

### One distribution per decision

Each stochastic decision in your model needs its own distribution object to maintain independent CRN streams.

```python
class MyDisease(ss.Module):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        self.define_pars(
            p_infection = ss.bernoulli(p=0.1),   # one dist for infection
            p_death = ss.bernoulli(p=0.02),       # separate dist for death
            dur_inf = ss.lognormal(mean=10, std=2),  # separate dist for duration
        )
        self.update_pars(pars=pars, **kwargs)
        return
```

## Anti-Patterns

**This is the most critical section. Violating these patterns will silently break CRN and produce incorrect results.**

### WRONG: Pass scalar count to `rvs()`

```python
# WRONG -- destroys CRN mapping; draws are not tied to agent UIDs
all_uids = self.sim.people.auids
values = self.dist.rvs(len(all_uids))

# CORRECT -- pass UIDs directly
values = self.dist.rvs(all_uids)
```

Passing `len(all_uids)` generates the right number of draws but assigns them to agents by position, not by UID. If agents are added or removed, the mapping shifts and CRN breaks.

### WRONG: Use `np.random` directly

```python
# WRONG -- bypasses CRN entirely
values = np.random.rand(len(all_uids))

# CORRECT -- use Starsim distributions
values = self.pars.my_uniform.rvs(all_uids)
```

Any call to `np.random` draws from a shared global PRNG with no per-agent mapping. This introduces stochastic branching noise.

### WRONG: Create new distributions every step

```python
# WRONG -- new distribution each step loses CRN state
def step(self):
    new_dist = ss.bernoulli(p=0.5)
    values = new_dist.rvs(all_uids)

# CORRECT -- create once in __init__, reuse in step
def __init__(self, pars=None, **kwargs):
    super().__init__()
    self.define_pars(p_event=ss.bernoulli(p=0.5))
    self.update_pars(pars=pars, **kwargs)

def step(self):
    values = self.pars.p_event.rvs(all_uids)
```

Each distribution object maintains its own PRNG slot. Creating a new one each step breaks the CRN mapping entirely.

### WRONG: Reuse one distribution for multiple decisions

```python
# WRONG -- same distribution used for two different decisions
my_bernoulli = ss.bernoulli(p=0)
my_bernoulli.set(p=p_infection)
infected_uids = my_bernoulli.filter()
my_bernoulli.set(p=p_die)
died_uids = my_bernoulli.filter()

# CORRECT -- separate distribution per decision
self.define_pars(
    p_infection = ss.bernoulli(p=p_infection),
    p_death = ss.bernoulli(p=p_die),
)
infected_uids = self.pars.p_infection.filter()
died_uids = self.pars.p_death.filter()
```

A single distribution object has one CRN slot. Calling it twice per step means the second call consumes the next step's random numbers, corrupting all future draws.

### WRONG: Call `dist.set()` every step instead of using dynamic callables

```python
# WRONG -- manually overriding parameters each step
def step(self):
    my_p_vec = np.full(self.sim.n, fill_value=0.5)
    my_p_vec[self.sim.people.age < 18] = 0.1
    self.pars.my_dist.set(p=my_p_vec)
    uids = self.pars.my_dist.filter(mask)

# CORRECT -- use a dynamic callable
def dynamic_p(self, sim, uids):
    p = np.full_like(uids, fill_value=0.5, dtype=float)
    p[sim.people.age[uids] < 18] = 0.1
    return p

# In __init__:
self.define_pars(my_dist=ss.bernoulli(p=dynamic_p))
```

Using `set()` every step works but is fragile and harder to maintain. Dynamic callables receive the current UIDs automatically and integrate cleanly with CRN.

### WRONG: Call `rvs()` in a loop over individual agents

```python
# WRONG -- N separate calls, each drawing one value
for uid in all_uids:
    value = self.dist.rvs(uid)

# CORRECT -- single vectorized call
values = self.dist.rvs(all_uids)
```

Beyond being slow, per-agent loops can disrupt CRN ordering. Always batch into a single vectorized call.

### WRONG: Set `single_rng = True` without a specific reason

```python
# WRONG -- disables CRN, reintroduces stochastic branching
ss.options.single_rng = True

# CORRECT -- leave the default (False) for CRN
# ss.options.single_rng = False  # this is the default
```

The only reason to set `single_rng = True` is for benchmarking or demonstrating the stochastic branching problem.

## Quick Reference

| Task | Code |
|------|------|
| Check CRN is enabled | `assert ss.options.single_rng == False` |
| Disable CRN (legacy mode) | `ss.options.single_rng = True` |
| Create Bernoulli distribution | `ss.bernoulli(p=0.3)` |
| Create lognormal distribution | `ss.lognormal(mean=5, std=1)` |
| Draw values for agents | `dist.rvs(uids)` |
| Draw values with boolean mask | `dist.rvs(mask)` |
| Filter Bernoulli successes | `uids = dist.filter()` or `dist.filter(subset_uids)` |
| Dynamic parameter (callable) | `ss.bernoulli(p=lambda self, sim, uids: compute_p(sim, uids))` |
| Set seed for reproducibility | `ss.Sim(..., rand_seed=42)` |
| Define dist in module `__init__` | `self.define_pars(p_event=ss.bernoulli(p=0.5))` |
| One dist per decision | Separate `ss.bernoulli()` for infection, death, recovery, etc. |
| Vectorized draw (not loop) | `values = dist.rvs(all_uids)` -- never loop over individual UIDs |
