---
name: starsim-dev-diseases
description: Use when creating, configuring, or customizing disease models in Starsim — including SIR, SIS, SEIR, custom diseases, and multi-disease simulations.
---

# Starsim Disease Modeling

Diseases are the cornerstone of almost any Starsim analysis. Starsim provides built-in disease templates (SIR, SIS) and a class hierarchy for building custom disease models. All diseases define states (compartments like susceptible, infected, recovered), manage transitions between those states each timestep, and optionally handle transmission across contact networks. This reference covers the disease class architecture, key methods, common implementation patterns, and anti-patterns to avoid.

## Class hierarchy

| Class | Inherits from | Transmission | Use case |
|-------|---------------|-------------|----------|
| `ss.Disease` | `ss.Module` | No | Non-communicable diseases (NCDs), conditions without person-to-person spread |
| `ss.Infection` | `ss.Disease` | Yes (via `infect()`) | All communicable/infectious diseases |
| `ss.SIR` | `ss.Infection` | Yes | Susceptible-Infected-Recovered model |
| `ss.SIS` | `ss.Infection` | Yes | Susceptible-Infected-Susceptible model (no lasting immunity) |
| `ss.SEIR` | `ss.SIR` | Yes | Susceptible-Exposed-Infectious-Recovered model (adds a latent, non-infectious period) |

Almost all diseases should inherit from `ss.Infection` or one of its subclasses like `ss.SIR`. Only use `ss.Disease` directly for non-communicable conditions that do not spread between agents. `ss.Infection` handles network-based transmission automatically -- it loops over agents in each network, applies network- and disease-specific betas, and manages per-agent susceptibility and transmissibility multipliers. This means you almost never need to write your own transmission logic.

The typical inheritance path for a custom communicable disease is: inherit from `ss.SIR` (or `ss.SIS`) to get built-in states and transitions for free, then add or override what you need. This is far less error-prone than building from `ss.Infection` directly.

## Key methods

| Method | Purpose | When to override |
|--------|---------|------------------|
| `define_pars()` | Declare disease parameters with defaults | Always, in `__init__` for custom diseases |
| `update_pars()` | Apply user-supplied parameter overrides | Always, in `__init__` after `define_pars` |
| `define_states()` | Initialize disease states (BoolState, FloatArr) | Always for custom diseases adding new states |
| `set_prognoses(uids, sources)` | Set outcomes for newly infected agents; calls `set_infection()` then `set_progression()` | When you need to change both at once |
| `set_infection(uids)` | Make the agents infected/infectious right now | To delay infectiousness (as `ss.SEIR` does) |
| `set_progression(uids)` | Schedule recovery, death, and any later stages | To add or reschedule downstream stages |
| `clear_infection(uids)` | Clear the infection states on recovery or death | When `infected` is derived rather than a plain state |
| `step_state()` | Update state transitions each timestep | When adding new state transitions |
| `step_die(uids)` | Handle agent deaths (reset custom states) | When disease has custom states |
| `define_aliases()` | Define a state name that resolves to another state or a callable | To derive a compartment from others |
| `infect()` | Handle transmission logic | **Rarely** -- use the built-in version |

### Method call order during a timestep

Each simulation timestep, the disease methods are called in this order:

1. `infect()` -- identifies new infections via network transmission (do not override unless necessary)
2. `set_prognoses(uids, sources)` -- called for each newly infected agent to schedule their future state transitions (e.g., when they recover, when they die)
3. `step_state()` -- processes scheduled state transitions for the current timestep (e.g., infected agents whose recovery time has arrived move to recovered)
4. `step_die(uids)` -- called for agents who die this timestep; resets disease states so dead agents are cleaned up properly

Understanding this order is critical: `set_prognoses` is forward-looking (it schedules future events using `ti_*` timing arrays), while `step_state` is the executor that checks those scheduled times against the current timestep and performs the transitions.

Since Starsim v3.6.0, `ss.SIR.set_prognoses()` splits into two overridable halves, so a subclass can change one without reimplementing the other:

- `set_infection(uids)` -- make the agents infected/infectious now (this is what `ss.SEIR` delays by the latent period).
- `set_progression(uids)` -- schedule recovery, death, and any further stages, relative to the onset of infectiousness.

**Migration:** an `ss.Infection` subclass that overrides `set_prognoses()` must call `super().set_prognoses(uids, sources)`. Since v3.6.0 the base class records `new_infections` as infections happen rather than reconstructing them afterwards from `ti_infected`, so an override that skips `super()` leaves `new_infections`, `cum_infections` and `incidence` permanently zero.

## Built-in diseases

The simplest way to use a disease is with a built-in template. Key parameters shared by `ss.SIR` and `ss.SIS`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `beta` | float or dict | 0.1 | Transmission probability per contact. Can be a dict keyed by network name for network-specific values |
| `dur_inf` | distribution | `ss.lognorm_ex(6)` | Duration of infectiousness (in simulation time units, typically years) |
| `init_prev` | float | 0.01 | Initial prevalence -- fraction of the population infected at simulation start |
| `p_death` | float or distribution | 0.01 | Probability of death while infected (vs. recovery) |

When `beta` is a dict, it maps network names to transmission probabilities, allowing different rates over different contact networks. For example, `beta={'random': 0.1, 'mf': 0.05}` applies different betas to the random and male-female networks.

```python
import starsim as ss

# Basic SIR with explicit parameters
sir = ss.SIR(dur_inf=10, beta=0.2, init_prev=0.4, p_death=0.2)
sim = ss.Sim(n_agents=2_000, diseases=sir, networks='random')
sim.run()
sim.plot()

# Access results programmatically
print(sim.results.sir.n_infected)   # Time series of infected count
print(sim.results.sir.n_susceptible)
sir.results  # Also accessible directly from the disease object
```

For `ss.SIS`, the key difference is that there is no recovered state -- agents return to susceptible after their infectious period ends, allowing reinfection.

```python
# SIS model -- agents can be reinfected
sis = ss.SIS(dur_inf=5, beta=0.15, init_prev=0.1, p_death=0.05)
sim = ss.Sim(n_agents=2_000, diseases=sis, networks='random')
sim.run()
sim.plot()
```

### The disease library (`ss.library`)

Beyond the templates above, Starsim ships a library of specific diseases and networks. As of v3.5.0 its contents are exported at the library's top level, so either path works:

```python
import starsim.library as ssl

ssl.Measles()                     # Or ss.library.Measles(), or ss.library.diseases.Measles()
ss.library.HouseholdNet()         # Or ss.library.networks.HouseholdNet()
```

Note these are not exported into the `ss` namespace itself — `ss.Measles` does not exist. `ssl.Measles`, `ssl.Cholera` and `ssl.Ebola` all subclass `ss.SEIR` as of v3.6.0.

### SEIR and the infected/infectious distinction

`ss.SEIR` extends `ss.SIR` with a latent, non-infectious exposed state:

```python
seir = ss.SEIR(beta=ss.peryear(0.5), dur_exp=ss.years(1), dur_inf=ss.years(2))
sim = ss.Sim(n_agents=2_000, diseases=seir, networks='random')
sim.run()
```

Its compartment naming is the part to get right, and it applies to any latent-period model:

| Attribute | Meaning |
|-----------|---------|
| `exposed` | The literal E compartment: infected but **not** transmitting |
| `infectious` | The literal I compartment: currently transmitting |
| `infected` | Derived as E plus I — "has the infection", whether or not yet transmitting |
| `ti_exposed` | Time of acquisition |
| `ti_infectious` | Time of becoming infectious |
| `ti_infected` | **Not defined** for `ss.SEIR` — accessing it raises `AttributeError`, since it is too easily confused with `ti_infectious` |

So `n_infected` and `prevalence` include latent infections, while transmission depends on `infectious` alone. For `ss.SIR` the two coincide, and `infectious` is simply an alias of `infected`.

**Migration (v3.6.0):** in `ss.SEIR` and its library subclasses (`ssl.Measles`, `ssl.Cholera`, `ssl.Ebola`), code that read `infected`/`n_infected` to mean "currently transmitting" must use `infectious`/`n_infectious`, and code that scheduled events off `ti_infected` must use `ti_infectious` (or `ti_exposed` for the time of acquisition). `ssl.Cholera.dur_exp2inf` and `ssl.Ebola.dur_exp2symp` are both now `dur_exp`.

## Implementation patterns

### Pattern 1: Extending an existing disease

The simplest customization is to inherit from a built-in disease and override specific methods. Always use `define_pars()` to declare new parameters with defaults, then `update_pars()` to accept user overrides via `pars` dict and `**kwargs`.

```python
import starsim as ss

class MyCustomSIR(ss.SIR):
    def __init__(self, pars=None, **kwargs):
        super().__init__()
        # Add custom parameters with defaults
        self.define_pars(
            my_param=0.5,
            custom_dur=ss.lognorm_ex(2.0),
        )
        self.update_pars(pars, **kwargs)

    def set_prognoses(self, uids, sources=None):
        """ Custom progression: call parent first, then modify """
        super().set_prognoses(uids, sources)
        # Example: make some fraction have longer infection
        long_inf = self.pars.my_param  # Use custom parameter
        # Additional custom logic here
```

The pattern is always: call `super().__init__()` first, then `define_pars()`, then `update_pars()`. This ensures the parent class sets up its internal structures before you add to them, and that user-supplied parameter values override your defaults.

### Pattern 2: Adding new states (SIRS with waning immunity)

`ss.SEIR` is built in as of Starsim v3.6.0 — do not hand-roll one (see [SEIR and the infected/infectious distinction](#seir-and-the-infectedinfectious-distinction) below). The worked example here is an SIRS model, which adds waning immunity so recovered agents return to susceptible. It shows the general shape of adding a state and a transition: a new parameter, a new `ti_` array, a `set_progression()` override to schedule the transition, and a `step_state()` override to execute it.

```python
import starsim as ss

class SIRS(ss.SIR):
    """ SIR with waning immunity: recovered agents return to susceptible """
    def __init__(self, pars=None, dur_imm=None, **kwargs):
        super().__init__()
        self.define_pars(
            dur_imm = ss.lognorm_ex(mean=ss.years(2)),  # How long immunity lasts
        )
        self.update_pars(pars, dur_imm=dur_imm, **kwargs)
        self.define_states(
            ss.FloatArr('ti_susceptible', label='Time of return to susceptible'),
        )
        return

    def set_progression(self, uids):
        """ Schedule recovery/death as usual, then schedule loss of immunity """
        super().set_progression(uids)
        rec = uids[self.ti_recovered.notnan[uids]]  # Agents who will recover rather than die
        self.ti_susceptible[rec] = self.ti_recovered[rec] + self.pars.dur_imm.rvs(rec)
        return

    def step_state(self):
        """ Do the usual SIR transitions, then wane immunity """
        super().step_state()
        waned = (self.recovered & (self.ti_susceptible <= self.ti)).uids
        self.recovered[waned] = False
        self.susceptible[waned] = True
        return


# Usage
sirs = SIRS(beta=ss.peryear(0.3), dur_inf=ss.years(1), p_death=0.05, dur_imm=ss.years(3))
sim = ss.Sim(n_agents=2_000, dur=ss.years(30), diseases=sirs, networks='random')
sim.run()
sim.plot()                   # Default sim-level plot
sim.diseases.sirs.plot()     # Disease-specific plot
```

Key design decisions:

1. **`__init__`**: Calls `super().__init__()` first, then adds `dur_imm` via `define_pars` and `ti_susceptible` via `define_states`. The parent `ss.SIR.__init__` already sets up `susceptible`, `infected`, `recovered`, `ti_infected`, `ti_recovered`, `ti_dead`, etc.

2. **`set_progression`** (not `set_prognoses`): calls `super()` to get the usual recovery/death scheduling, then schedules the extra stage on top. Only agents who will recover get a `ti_susceptible`; those scheduled to die keep `nan`, so they never wane.

3. **`step_state`**: calls `super().step_state()` so the SIR transitions happen normally, then moves agents whose immunity has expired back to susceptible. `(...).uids` converts the boolean mask to UIDs — never use `np.where`.

4. **`step_die`** is not overridden here, because no new *boolean* state was added; `ss.SIR.step_die()` already clears `susceptible`, `recovered` and the infection. Add an override as soon as you add a `BoolState` (see Pattern 3).

5. **Plotting**: `sim.diseases.sirs.plot()`, not `sirs.plot()` — the sim copies its modules at initialization, so the original object has no results. To show extra compartments, set the `plot_states` class attribute (see Pattern 4).

### Pattern 2b: State aliases

`define_aliases()` (v3.6.0) defines a state name that resolves to something else — either the name of another state, or a callable that derives it:

```python
self.define_aliases(infectious='infected')                                  # Alias of another state
self.define_aliases(asymptomatic=lambda self: self.infected & ~self.symptomatic)  # Derived, recomputed on access
```

A callable alias behaves like a read-only property: it is recomputed on each access, cannot be written to (assigning to it raises), and automatically generates an `n_<name>` result, just as a `BoolState` does. A string alias does not, since the state it points to is already counted under its own name. An alias is only consulted if the attribute isn't otherwise defined, so a subclass overrides it just by defining a state of the same name. Note that a lambda alias can't be saved with plain `pickle` (`sc.save()` and `ss.MultiSim` use `dill`, so they are fine) — use a module-level function or a property if plain pickling is required.

Any keyword arguments to `define_states()` other than `reset`, `lock` and `overwrite` are passed through to `define_aliases()`, which is how `ss.SEIR` derives `infected` from its two compartments:

```python
self.define_states(
    ss.BoolState('exposed', label='Exposed'),
    ss.BoolState('infectious', label='Infectious'),
    ss.FloatArr('ti_exposed', label='Time of exposure'),
    ss.FloatArr('ti_infectious', label='Time of becoming infectious'),
    reset = ['infected', 'infectious', 'ti_infected'],  # Drop the inherited SIR versions
    infected = lambda self: self.exposed | self.infectious,
)
```

`define_states(reset=...)` accepts a state or alias name (or a list of them) as well as `True`, so a subclass can replace or remove individual inherited states rather than all of them; removing a name without replacing it leaves it undefined, which is how `ss.SEIR` drops `ti_infected`.

**Migration (v3.6.0):** `define_states(check=False)` is replaced by `define_states(overwrite=True)`. `check=False` never actually replaced anything — it skipped the duplicate check but still appended, so initialization later failed with `Another result named "n_infected" already exists`. Also, `ss.Infection.infectious` is no longer a property but an alias of `infected`; reading it is unchanged, and overriding it with a property still works.

### Pattern 3: Custom death handling

When your disease adds custom boolean states, you **must** override `step_die()` to reset them when agents die. Without this, dead agents retain their disease state flags, which corrupts result counts and can cause downstream errors.

```python
def step_die(self, uids):
    """Always call super first, then reset all custom boolean states."""
    super().step_die(uids)
    self.exposed[uids] = False
    self.hospitalized[uids] = False
    self.my_custom_state[uids] = False
```

The `uids` argument contains the UIDs of agents dying this timestep (from any cause, not just this disease). The parent `step_die` handles resetting the built-in states (`infected`, `susceptible`, `recovered`), so you only need to handle your additions.

### Pattern 4: Custom plotting

To show extra compartments on the default `ss.SIR`-style plot, set the `plot_states` class attribute (v3.6.0) — it lists which results `plot()` draws, so a subclass that adds a compartment needs one line rather than a `plot()` override:

```python
class MyDisease(ss.SIR):
    plot_states = ['n_susceptible', 'n_infected', 'n_hospitalized', 'n_recovered']
```

This is how `ss.SEIR` shows its exposed compartment. Override `plot()` only when you need something the state list can't express (a second axis, shaded intervals, etc.). The pattern then uses `ss.options.context(show=False)` to prevent the parent plot from displaying prematurely, and returns the figure via `ss.return_fig(fig)`:

```python
import matplotlib.pyplot as plt

def plot(self):
    with ss.options.context(show=False):
        fig = super().plot()
        ax = plt.gca()
        # Add lines for each custom state
        for key in ['n_exposed', 'n_hospitalized']:
            res = self.results[key]
            ax.plot(res.timevec, res, label=res.label)
        plt.legend()
    return ss.return_fig(fig)
```

### Pattern 5: Custom states in detail

Use `define_states()` in `__init__` to add per-agent tracking arrays. There are two primary state types:

```python
# BoolState: tracks which agents are in a compartment
# Automatically creates a result counter (e.g., self.results.n_exposed)
ss.BoolState('exposed', label='Exposed')

# FloatArr: tracks continuous values per agent (timing, viral load, etc.)
# Used for scheduling transitions or tracking disease progression
ss.FloatArr('ti_exposed', label='Time of exposure')
ss.FloatArr('viral_load', label='Viral load')
```

States defined with `define_states` are automatically initialized for all agents and tracked as results. A `BoolState` named `'exposed'` produces `self.results.n_exposed` counting how many agents are in that state each timestep. A `FloatArr` named `'ti_exposed'` is available as `self.ti_exposed` and stores per-agent float values. The `ti_` prefix is a convention for timing arrays indicating when an agent entered or will enter a particular state.

You can define multiple states in a single call:

```python
self.define_states(
    ss.BoolState('exposed', label='Exposed'),
    ss.BoolState('hospitalized', label='Hospitalized'),
    ss.FloatArr('ti_exposed', label='Time of exposure'),
    ss.FloatArr('ti_hospitalized', label='Time of hospitalization'),
    ss.FloatArr('severity', label='Disease severity'),
)
```

### Pattern 6: Custom parameters with distributions

Use `define_pars()` to declare parameters and `update_pars()` to accept user overrides. Parameters can be scalars, distributions, or any Python object:

```python
def __init__(self, pars=None, **kwargs):
    super().__init__()
    self.define_pars(
        dur_exp=ss.lognorm_ex(0.5),     # Lognormal distribution (mean=0.5)
        p_severe=0.1,                     # Scalar probability
        custom_beta=ss.beta(a=2, b=5),   # Beta distribution
        age_threshold=50,                 # Scalar threshold
    )
    self.update_pars(pars, **kwargs)
```

This lets users override any parameter at instantiation:

```python
# Override exposure duration and severity probability
my_disease = MyDisease(dur_exp=ss.lognorm_ex(1.0), p_severe=0.3)

# Or via pars dict
my_disease = MyDisease(pars={'dur_exp': ss.lognorm_ex(1.0), 'p_severe': 0.3})
```

Distribution parameters are sampled per-agent using `.rvs(uids)` in `set_prognoses`:

```python
def set_prognoses(self, uids, sources=None):
    p = self.pars
    dur_exp = p.dur_exp.rvs(uids)  # Sample one value per agent
    is_severe = p.p_severe.rvs(uids)  # Boolean array (Bernoulli draw)
```

### Pattern 7: Relative susceptibility and transmissibility

Every `ss.Infection` has `rel_sus` and `rel_trans` float arrays (default value 1.0 for all agents) that scale per-agent susceptibility and transmissibility during transmission calculations. These are typically modified by connectors or interventions, not by the disease itself:

```python
# In a connector or intervention step() method:
ng = self.sim.people.gonorrhea
hiv = self.sim.people.hiv
p = self.pars

# People with low CD4 are more susceptible to gonorrhea
ng.rel_sus[hiv.cd4 < 500] = p.rel_sus_hiv    # e.g., 2.0
ng.rel_sus[hiv.cd4 < 200] = p.rel_sus_aids    # e.g., 5.0

# And more transmissible
ng.rel_trans[hiv.cd4 < 500] = p.rel_trans_hiv  # e.g., 2.0
ng.rel_trans[hiv.cd4 < 200] = p.rel_trans_aids  # e.g., 5.0
```

A value of 2.0 means twice as susceptible (or transmissible) as baseline. These arrays are reset each timestep, so connectors must set them every step.

### Pattern 8: Multi-disease simulations

Pass multiple diseases as a list to the sim. Use connectors -- modules that inherit from `ss.Module` and implement a `step()` method -- to mediate cross-disease interactions like cofactor effects:

```python
import starsim as ss

class SimpleHIVNG(ss.Module):
    """Connector: HIV increases gonorrhea susceptibility and transmissibility."""
    def __init__(self, pars=None, label='HIV-Gonorrhea', **kwargs):
        super().__init__()
        self.define_pars(
            rel_trans_hiv=2,
            rel_trans_aids=5,
            rel_sus_hiv=2,
            rel_sus_aids=5,
        )
        self.update_pars(pars, **kwargs)

    def step(self):
        """Modify gonorrhea rel_sus and rel_trans based on HIV status."""
        ng = self.sim.people.gonorrhea
        hiv = self.sim.people.hiv
        p = self.pars
        ng.rel_sus[hiv.cd4 < 500] = p.rel_sus_hiv
        ng.rel_sus[hiv.cd4 < 200] = p.rel_sus_aids
        ng.rel_trans[hiv.cd4 < 500] = p.rel_trans_hiv
        ng.rel_trans[hiv.cd4 < 200] = p.rel_trans_aids

# Build multi-disease sim with connector
sim = ss.Sim(
    n_agents=5_000,
    networks='mf',
    diseases=[SimpleHIVNG(), hiv, ng],
)
sim.run()
sim.plot('hiv')
sim.plot('gonorrhea')
```

Connectors are placed in the `diseases` list (or wherever ordering makes sense for the simulation step order). They are generic `ss.Module` instances, not disease subclasses. The connector's `step()` runs each timestep and can read or modify any disease state on any agent.

### Pattern 9: Congenital outcomes via mother-to-child transmission

The base `Infection` class provides a generic framework for congenital outcomes. Diseases opt in by defining `birth_outcome_keys` and `birth_outcomes` in pars, then calling `self.set_congenital()` at infection time. See `starsim_examples/mnch/` for complete working examples and the [starsim pregnancy docs](https://docs.starsim.org) for API details.

### Accessing results

After running a simulation, disease results are available via two equivalent paths:

```python
# Via the sim results object (keyed by disease name)
sim.results.sir.n_infected      # Time series: number of infected agents
sim.results.sir.n_susceptible   # Time series: number of susceptible agents
sim.results.sir.n_recovered     # Time series: number of recovered agents
sim.results.sir.new_infections  # Time series: new infections per timestep
sim.results.sir.new_deaths      # Time series: new deaths per timestep

# Via the disease object directly
sir.results.n_infected          # Same data

# Plotting
sim.plot()                      # Overall sim plot (all diseases)
sim.plot('sir')                 # Plot specific disease
sim.diseases.sir.plot()         # Disease-specific plot method

# Custom states are automatically tracked
sim.results.seir.n_exposed      # Any BoolState (or callable alias) gets an n_<name> result
sim.results.seir.n_infectious   # For ss.SEIR: the I compartment alone
sim.results.seir.n_infected     # For ss.SEIR: E plus I (derived), as is prevalence
```

Results have a `.timevec` attribute for the time axis and can be used directly in matplotlib calls or exported to numpy arrays.

## Anti-patterns

**Do not override `infect()`.** The built-in `infect()` method on `ss.Infection` correctly handles looping over agents in each network, applying network- and disease-specific transmission probabilities, managing agent transmissibility and susceptibility via `rel_trans` and `rel_sus`, and mixing pool logic. Writing your own transmission logic is error-prone and unnecessary in nearly all cases. To control which agents can transmit, define `infectious` as a state or alias of its own (as `ss.SEIR` does) rather than touching `infect()`.

**Must override `step_die()` when adding custom boolean states.** If your disease defines additional `BoolState` attributes (e.g., `exposed`, `hospitalized`), you must reset them in `step_die(uids)` by calling `super().step_die(uids)` and then setting each custom state to `False` for the dying UIDs. Failing to do this means dead agents retain their disease flags, corrupting compartment counts and potentially causing downstream logic errors.

**Do not hand-roll a latent period.** Use `ss.SEIR`, or subclass it. If you do need a custom staged progression, split the work the way `ss.SIR` does — `set_infection()` for "the agent is infected now" and `set_progression()` for everything scheduled afterwards — and schedule the later stages from `ti_infectious`, not from the time of acquisition. The classic bug is `ti_recovered = ti_infected + dur_inf` in a model with a latent period: the latent period then eats into the infectious period rather than delaying it.

**Inherit from `ss.Infection`, not `ss.Disease`.** Almost all communicable diseases need the transmission logic provided by `ss.Infection`. Only use `ss.Disease` directly for non-communicable conditions without person-to-person spread. In practice, most custom diseases should inherit from `ss.SIR` or `ss.SIS` rather than `ss.Infection` directly, to get built-in states, transitions, and result tracking for free.

**Always call `super().__init__()` before `define_pars` and `define_states`.** The parent class initializer sets up internal data structures that `define_pars` and `define_states` write into. Calling these methods before `super().__init__()` will raise errors or produce undefined behavior.

**Do not forget `return` at the end of `__init__`.** While Python does not require an explicit return in `__init__`, Starsim's convention includes it for clarity, and some internal tooling may rely on it.

**Use `self.ti` and `self.now`, not `self.sim.t.ti`.** Every module exposes its own timestep accessors: `self.ti` (timestep index), `self.now` (current date/time), and `self.dt`. Reach through `self.sim` only for things the module does not own (e.g. `self.sim.people`, `self.sim.diseases.other`).

**Use `init_post(self)` for init logic, not `initialize(self, sim)`.** If a disease needs setup after the sim is built, override `init_post(self)` (call `super().init_post()` first); `self.sim` is already linked, so it takes no `sim` argument. There is no `initialize(self, sim)` hook and no need for `setattribute`.

## Quick reference

```text
Class hierarchy:
  ss.Disease                         # Base (no transmission)
    ss.Infection                     # Adds infect() and network transmission
      ss.SIR                         # S-I-R with beta, dur_inf, p_death, init_prev
        ss.SEIR                      # S-E-I-R; adds dur_exp, exposed, infectious, ti_infectious
      ss.SIS                         # S-I-S (no recovered state, allows reinfection)

State types:
  ss.BoolState('name', label=...)    # Boolean per-agent state (auto-tracked in results)
  ss.FloatArr('name', label=...)     # Float per-agent array (timing, viral load, etc.)

Parameter management:
  self.define_pars(key=value, ...)   # Declare parameters with defaults in __init__
  self.update_pars(pars, **kwargs)   # Apply user overrides in __init__

Aliases (define_aliases / define_states kwargs):
  infectious = 'infected'            # String alias: resolves to another state
  infected = lambda self: ...        # Callable alias: derived, read-only, gets n_infected

Key methods to override:
  __init__(pars, **kwargs)           # Add pars via define_pars, states via define_states
  set_infection(uids)                # Make agents infected/infectious now
  set_progression(uids)              # Schedule recovery, death, and later stages
  clear_infection(uids)              # Clear infection states on recovery/death
  set_prognoses(uids, sources)       # Both of the above; call super() if overridden
  step_state()                       # Process scheduled transitions each timestep
  step_die(uids)                     # Reset custom boolean states on agent death
  plot_states = [...]                # Class attribute: which results plot() draws

Accessing results:
  sim.results.<disease>.n_infected   # Infected count time series
  sim.results.<disease>.new_infections  # New infections per step
  sim.results.<disease>.n_<state>    # Any BoolState auto-tracked
  sim.diseases.<disease>.plot()      # Disease-specific plot

Timestep execution order:
  1. infect()                        # Transmission (do not override)
  2. set_prognoses(uids, sources)    # Schedule outcomes for new infections
  3. step_state()                    # Execute scheduled transitions
  4. step_die(uids)                  # Clean up dying agents
```
