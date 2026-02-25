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

Almost all diseases should inherit from `ss.Infection` or one of its subclasses like `ss.SIR`. Only use `ss.Disease` directly for non-communicable conditions that do not spread between agents. `ss.Infection` handles network-based transmission automatically -- it loops over agents in each network, applies network- and disease-specific betas, and manages per-agent susceptibility and transmissibility multipliers. This means you almost never need to write your own transmission logic.

The typical inheritance path for a custom communicable disease is: inherit from `ss.SIR` (or `ss.SIS`) to get built-in states and transitions for free, then add or override what you need. This is far less error-prone than building from `ss.Infection` directly.

## Key methods

| Method | Purpose | When to override |
|--------|---------|------------------|
| `define_pars()` | Declare disease parameters with defaults | Always, in `__init__` for custom diseases |
| `update_pars()` | Apply user-supplied parameter overrides | Always, in `__init__` after `define_pars` |
| `define_states()` | Initialize disease states (BoolState, FloatArr) | Always for custom diseases adding new states |
| `set_prognoses(uids, sources)` | Set outcomes for newly infected agents | Almost always for custom diseases |
| `step_state()` | Update state transitions each timestep | When adding new state transitions |
| `step_die(uids)` | Handle agent deaths (reset custom states) | When disease has custom states |
| `infect()` | Handle transmission logic | **Rarely** -- use the built-in version |

### Method call order during a timestep

Each simulation timestep, the disease methods are called in this order:

1. `infect()` -- identifies new infections via network transmission (do not override unless necessary)
2. `set_prognoses(uids, sources)` -- called for each newly infected agent to schedule their future state transitions (e.g., when they recover, when they die)
3. `step_state()` -- processes scheduled state transitions for the current timestep (e.g., infected agents whose recovery time has arrived move to recovered)
4. `step_die(uids)` -- called for agents who die this timestep; resets disease states so dead agents are cleaned up properly

Understanding this order is critical: `set_prognoses` is forward-looking (it schedules future events using `ti_*` timing arrays), while `step_state` is the executor that checks those scheduled times against the current timestep and performs the transitions.

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

### Pattern 2: Adding new states (full SEIR example)

This is the complete, working SEIR implementation that adds an "exposed" (incubation) state to the SIR model. Exposed agents are infected and transmitting but have not yet progressed to the symptomatic infected state. This is one of the most common customizations in epidemiological modeling.

```python
import starsim as ss
import matplotlib.pyplot as plt

class SEIR(ss.SIR):
    def __init__(self, pars=None, *args, **kwargs):
        super().__init__()
        self.define_pars(
            dur_exp=ss.lognorm_ex(0.5),  # Duration of exposed period
        )
        self.update_pars(pars, **kwargs)

        # Additional states beyond the SIR ones
        self.define_states(
            ss.BoolState('exposed', label='Exposed'),
            ss.FloatArr('ti_exposed', label='Time of exposure'),
        )

    @property
    def infectious(self):
        """Both exposed and infected agents can transmit."""
        return self.infected | self.exposed

    def step_state(self):
        """Perform SIR updates, then progress exposed -> infected."""
        # Call parent to handle infected -> recovered and infected -> dead
        super().step_state()

        # Progress exposed -> infected when their scheduled time arrives
        infected = self.exposed & (self.ti_infected <= self.ti)
        self.exposed[infected] = False
        self.infected[infected] = True

    def step_die(self, uids):
        """Reset exposed state for dying agents."""
        super().step_die(uids)
        self.exposed[uids] = False

    def set_prognoses(self, uids, sources=None):
        """Schedule state transitions for newly infected agents."""
        super().set_prognoses(uids, sources)
        ti = self.ti

        # New agents enter exposed state (not directly infected)
        self.susceptible[uids] = False
        self.exposed[uids] = True
        self.ti_exposed[uids] = ti

        # Schedule future transitions with proper timing
        p = self.pars
        dur_exp = p.dur_exp.rvs(uids)         # Draw exposure durations
        self.ti_infected[uids] = ti + dur_exp  # When they become infected

        dur_inf = p.dur_inf.rvs(uids)         # Draw infection durations
        will_die = p.p_death.rvs(uids)        # Determine who dies
        self.ti_recovered[uids[~will_die]] = ti + dur_inf[~will_die]
        self.ti_dead[uids[will_die]] = ti + dur_inf[will_die]

    def plot(self):
        """Extend the default SIR plot with the exposed compartment."""
        with ss.options.context(show=False):
            fig = super().plot()
            ax = plt.gca()
            res = self.results.n_exposed
            ax.plot(res.timevec, res, label=res.label)
            plt.legend()
        return ss.return_fig(fig)


# Usage
seir = SEIR()
sim = ss.Sim(diseases=seir, networks='random')
sim.run()
sim.plot()                   # Default sim-level plot
sim.diseases.seir.plot()     # Disease-specific plot with exposed line
```

Key design decisions in the SEIR example explained in detail:

1. **`__init__`**: Calls `super().__init__()` first, then adds `dur_exp` parameter via `define_pars` and the `exposed`/`ti_exposed` states via `define_states`. The parent `ss.SIR.__init__` already sets up `susceptible`, `infected`, `recovered`, `ti_infected`, `ti_recovered`, `ti_dead`, etc.

2. **`infectious` property**: Returns `self.infected | self.exposed`, a boolean array union. The built-in `infect()` method queries `self.infectious` to determine which agents can transmit. By including exposed agents here, the existing transmission machinery automatically handles them without any changes to `infect()`.

3. **`step_state`**: Calls `super().step_state()` first so that the SIR transitions (infected-to-recovered, infected-to-dead) happen normally. Then it checks for exposed agents whose `ti_infected` has arrived and transitions them to infected. The check `self.ti_infected <= self.ti` compares the scheduled infection time against the current simulation time.

4. **`step_die`**: Resets the `exposed` boolean state for dying agents. This is mandatory -- without it, dead agents would still appear as "exposed" in result counts.

5. **`set_prognoses`**: This is the most complex override. It calls `super().set_prognoses()` first (which sets up the default SIR timing), then overwrites the timing to insert the exposure period. Newly infected agents enter the `exposed` state immediately, and `ti_infected` is set to `ti + dur_exp` (current time plus a random exposure duration). The recovery and death times are drawn from `dur_inf` and `p_death` distributions.

6. **`plot`**: Uses `ss.options.context(show=False)` to suppress immediate display, calls `super().plot()` to get the base SIR figure, then adds the exposed compartment line from `self.results.n_exposed`. The `ss.return_fig(fig)` call ensures proper display handling.

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

Override `plot()` to add custom compartments to the default disease plot. The pattern uses `ss.options.context(show=False)` to prevent the parent plot from displaying prematurely, then adds lines and returns the figure via `ss.return_fig(fig)`:

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
sim.results.seir.n_exposed      # Available if SEIR defined a BoolState('exposed')
```

Results have a `.timevec` attribute for the time axis and can be used directly in matplotlib calls or exported to numpy arrays.

## Anti-patterns

**Do not override `infect()`.** The built-in `infect()` method on `ss.Infection` correctly handles looping over agents in each network, applying network- and disease-specific transmission probabilities, managing agent transmissibility and susceptibility via `rel_trans` and `rel_sus`, and mixing pool logic. Writing your own transmission logic is error-prone and unnecessary in nearly all cases. Instead, override the `infectious` property to control which agents can transmit.

**Must override `step_die()` when adding custom boolean states.** If your disease defines additional `BoolState` attributes (e.g., `exposed`, `hospitalized`), you must reset them in `step_die(uids)` by calling `super().step_die(uids)` and then setting each custom state to `False` for the dying UIDs. Failing to do this means dead agents retain their disease flags, corrupting compartment counts and potentially causing downstream logic errors.

**Include exposure duration in timing calculations.** When adding an exposed state in `set_prognoses`, the total time from acquisition to recovery or death must account for the full pathway. Schedule `ti_infected = ti + dur_exp` (when the agent becomes symptomatic/infectious), and compute recovery/death times based on the total disease duration. A common bug is to set `ti_recovered = ti_infected + dur_inf` without accounting for the exposure period, resulting in agents spending too long in the exposed state or recovering before they become infected.

**Inherit from `ss.Infection`, not `ss.Disease`.** Almost all communicable diseases need the transmission logic provided by `ss.Infection`. Only use `ss.Disease` directly for non-communicable conditions without person-to-person spread. In practice, most custom diseases should inherit from `ss.SIR` or `ss.SIS` rather than `ss.Infection` directly, to get built-in states, transitions, and result tracking for free.

**Always call `super().__init__()` before `define_pars` and `define_states`.** The parent class initializer sets up internal data structures that `define_pars` and `define_states` write into. Calling these methods before `super().__init__()` will raise errors or produce undefined behavior.

**Do not forget `return` at the end of `__init__`.** While Python does not require an explicit return in `__init__`, Starsim's convention includes it for clarity, and some internal tooling may rely on it.

## Quick reference

```text
Class hierarchy:
  ss.Disease                         # Base (no transmission)
    ss.Infection                     # Adds infect() and network transmission
      ss.SIR                         # S-I-R with beta, dur_inf, p_death, init_prev
      ss.SIS                         # S-I-S (no recovered state, allows reinfection)

State types:
  ss.BoolState('name', label=...)    # Boolean per-agent state (auto-tracked in results)
  ss.FloatArr('name', label=...)     # Float per-agent array (timing, viral load, etc.)

Parameter management:
  self.define_pars(key=value, ...)   # Declare parameters with defaults in __init__
  self.update_pars(pars, **kwargs)   # Apply user overrides in __init__

Key properties to override:
  infectious                         # Property: BoolArr of who can transmit

Key methods to override:
  __init__(pars, **kwargs)           # Add pars via define_pars, states via define_states
  set_prognoses(uids, sources)       # Schedule state transitions for new infections
  step_state()                       # Process scheduled transitions each timestep
  step_die(uids)                     # Reset custom boolean states on agent death
  plot()                             # Custom visualization with additional compartments

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
