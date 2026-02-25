---
name: starsim-dev-analyzers
description: Use when adding custom result collection or analysis to a Starsim simulation — including function-based analyzers, class-based analyzers, and built-in analyzers.
---

# Starsim Analyzers

Analyzers collect custom results from a Starsim simulation without modifying its state. They run at the end of each timestep, after all module updates, and report on the current state of agents, diseases, networks, or demographics. There are three ways to create an analyzer: a simple function, a class subclassing `ss.Analyzer`, or a built-in analyzer referenced by string name.

## When to use analyzers

Each Starsim module (e.g. `ss.HIV`, `ss.Pregnancy`) already records its own results automatically -- for example, `sim.results.hiv.new_infections` or `sim.results.pregnancy.pregnant`. If you need a result that no existing module provides, or you need a cross-cutting metric that combines state from multiple modules (e.g. HIV infections among pregnant women), create an analyzer. Analyzers are preferred over modifying module source code because they are composable, optional, and easy to add or remove from a sim.

## Key classes

| Class / Function | Purpose |
|---|---|
| `ss.Analyzer` | Base class for custom analyzers; subclass and override `step()` |
| `ss.Result('name')` | Declares a named result array that the sim tracks over time |
| `ss.infection_log()` | Built-in: line list of every infection event (source, target, time) |
| `ss.dynamics_by_age()` | Built-in: tracks a disease state stratified by configurable age bins |

## Patterns

### 1. Function analyzer

The simplest approach. Define a plain function that accepts `sim` as its only argument. Starsim calls it once per timestep. Pass it directly via the `analyzers` parameter.

```python
import numpy as np
import starsim as ss
import matplotlib.pyplot as plt

# Store the number of edges
n_edges = []

def count_edges(sim):
    """ Print out the number of edges in the network on each timestep """
    network = sim.networks[0]  # Get the first network
    n = len(network)
    n_edges.append(n)
    print(f'Number of edges for network {network.name} on step {sim.ti}: {n}')
    return

sim = ss.Sim(
    diseases='sis',
    networks='mf',
    analyzers=count_edges,
    demographics=True,
)
sim.run()

# Plot the number of edges
plt.figure()
plt.plot(sim.timevec, n_edges)
plt.title('Number of edges over time')
plt.ylim(bottom=0)
plt.show()
```

Function analyzers are best for quick one-off exploration or debugging. The limitation is that results are stored in an external variable (here `n_edges`) rather than being integrated into the sim's results framework. This means they will not appear in `sim.to_df()` and you cannot call `sim.plot()` to visualize them. For anything that needs structured results, automatic export, or a `plot()` method, use a class-based analyzer instead.

### 2. Class-based analyzer

Subclass `ss.Analyzer` and override the relevant lifecycle methods. This gives you full integration with the sim's result tracking, export, and plotting.

#### Lifecycle methods

| Method | When called | Purpose |
|---|---|---|
| `__init__()` | Construction | Store configuration parameters; must call `super().__init__()` |
| `init_results()` | During sim initialization | Declare result arrays with `self.define_results()`; must call `super().init_results()` first |
| `step()` | End of each timestep | Read sim state and write values to `self.results['name'][ti]` |
| `finalize_results()` | After sim completes | Post-process or convert collected data; must call `super().finalize_results()` first |
| `plot()` | On demand by user | Visualize the collected results |

The `step()` method is where the core logic lives. Inside it, `self.sim` gives you full read access to the simulation: `self.sim.people` for agent states, `self.sim.diseases` for disease modules, `self.sim.networks` for networks, `self.sim.demographics` for demographic modules, and `self.sim.ti` for the current timestep index.

#### Declaring results with `define_results()`

Use `self.define_results()` inside `init_results()` to register named result arrays. Each `ss.Result('name')` creates a numeric array automatically sized to the number of simulation timesteps. Results declared this way are accessible after the run at `sim.results.<analyzer_name>.<result_name>` and are automatically included in `sim.to_df()` exports.

You can declare multiple results in a single call:

```python
self.define_results(
    ss.Result('metric_a'),
    ss.Result('metric_b'),
)
```

#### Example: HIV infections during pregnancy

This analyzer tracks new HIV infections among currently pregnant women at each timestep, combining state from both the HIV disease module and the Pregnancy demographics module:

```python
import starsim as ss
import starsim_examples as sse
import pandas as pd

class HIV_preg(ss.Analyzer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return

    def init_results(self):
        super().init_results()
        self.define_results(
            ss.Result('new_infections_pregnancy'),
        )
        return

    def step(self):
        sim = self.sim
        ti = sim.ti
        hiv = sim.diseases.hiv
        pregnant = sim.demographics.pregnancy.pregnant
        newly_infected = hiv.ti_infected == ti
        self.results['new_infections_pregnancy'][ti] = len((newly_infected & pregnant).uids)
        return

pregnancy = ss.Pregnancy(fertility_rate=pd.read_csv('test_data/nigeria_asfr.csv'))
hiv = sse.HIV(beta={'mfnet': [0.5, 0.25]})

sim = ss.Sim(
    diseases=hiv,
    networks='mfnet',
    demographics=pregnancy,
    analyzers=HIV_preg(),
)
sim.run()

# Results are accessible as standard sim results
print(f'Total: {sim.results.hiv_preg.new_infections_pregnancy.sum()}')
```

Plot the analyzer results using the standard results object:

```python
import matplotlib.pyplot as plt

res = sim.results.hiv_preg
plt.figure()
plt.bar(res.timevec.years, res.new_infections_pregnancy)
plt.title('HIV infections acquired during pregnancy')
plt.show()
```

Key details:
- The analyzer name defaults to the lowercased class name (`hiv_preg`), which becomes the attribute name under `sim.results`.
- `hiv.ti_infected == ti` creates a boolean `Arr` of agents infected on this timestep. Combining it with `pregnant` (also a boolean `Arr`) using `&` gives the intersection. Calling `.uids` returns the matching UIDs and `len()` counts them.
- Because results are registered through `define_results()`, they appear in `sim.to_df()` alongside all other module results.

### 3. Custom analyzer with age bins

A common pattern is tracking a disease state stratified by age group. This full example demonstrates all four lifecycle methods including `finalize_results()` for post-processing and `plot()` for visualization:

```python
import numpy as np
import starsim as ss
import matplotlib.pyplot as plt

class dynamics_by_age(ss.Analyzer):
    def __init__(self, state, age_bins=(0, 20, 40, 100)):
        super().__init__()
        self.state = state
        self.age_bins = age_bins
        self.mins = age_bins[:-1]
        self.maxes = age_bins[1:]
        self.hist = {k: [] for k in self.mins}
        return

    def step(self):
        people = self.sim.people
        for min, max in zip(self.mins, self.maxes):
            mask = (people.age >= min) & (people.age < max)
            self.hist[min].append(people.states[self.state][mask].sum())
        return

    def finalize_results(self):
        """ Convert lists to numpy arrays for easier analysis """
        super().finalize_results()
        for k, hist in self.hist.items():
            self.hist[k] = np.array(hist)
        return

    def plot(self, **kwargs):
        kw = ss.plot_args(kwargs)
        with ss.style(**kw.style):
            fig = plt.figure(**kw.fig)
            for minage, maxage in zip(self.mins, self.maxes):
                plt.plot(self.sim.t.timevec, self.hist[minage],
                         label=f'Age {minage}-{maxage}', **kw.plot)
            plt.legend(**kw.legend)
            plt.xlabel('Model time')
            plt.ylabel('Count')
            plt.ylim(bottom=0)
        return ss.return_fig(fig, **kw.return_fig)

# Use it
by_age = dynamics_by_age('sis.infected', age_bins=(0, 10, 30, 100))
sim = ss.Sim(diseases='sis', networks='random', analyzers=by_age, copy_inputs=False)
sim.run()
by_age.plot()
```

Key details:
- The `state` parameter is a dotted string like `'sis.infected'`. Access it via `people.states[self.state]`, which returns a boolean `Arr` across all agents. Applying `[mask].sum()` counts agents in that state within the age range.
- `finalize_results()` runs once after the simulation ends. Use it to convert accumulated lists into numpy arrays, compute summary statistics, or reshape data.
- The `plot()` method uses `ss.plot_args(kwargs)` and `ss.style()` for consistent Starsim-style figures. Return `ss.return_fig(fig, **kw.return_fig)` for compatibility with Starsim's figure handling utilities.
- When passing an analyzer instance and wanting to access it directly after the run (as `by_age.plot()` rather than `sim.analyzers[0].plot()`), set `copy_inputs=False` on the sim so it does not deepcopy the analyzer.

### 4. Built-in analyzers

Starsim ships with two built-in analyzers. You can pass them by string name or by instantiating the class directly.

#### Infection log

Produces a line list of every infection event, recording the source agent, target agent, and time of transmission. This is useful for transmission tree analysis, identifying superspreaders, or validating network-driven transmission patterns.

```python
sim = ss.Sim(
    n_agents=1000,
    dt=0.2,
    dur=15,
    diseases='sir',
    networks='random',
    analyzers='infection_log',
)
sim.run()

infection_log = sim.analyzers[0]
infection_log.plot()       # Raster plot of infections over time
# infection_log.animate()  # Animated version (interactive)
```

The infection log is integrated into `ss.Disease` internals to capture source/target pairs that are otherwise discarded each timestep for memory efficiency. This is why it must be added as an analyzer rather than computed after the fact.

#### Dynamics by age (built-in)

The built-in `ss.dynamics_by_age()` provides the same functionality as the custom class shown in pattern 3:

```python
sim = ss.Sim(
    diseases='sis',
    networks='random',
    analyzers=ss.dynamics_by_age('sis.infected', age_bins=(0, 20, 40, 100)),
)
sim.run()
sim.analyzers[0].plot()
```

## Anti-patterns

**Analyzers observe, they do not modify state.** An analyzer runs after all modules have updated for the timestep. Do not set disease states, modify networks, or change agent attributes inside an analyzer. Doing so will produce incorrect results because the changes bypass the normal module update order. If you need to change simulation state (e.g. vaccinate agents, treat infections), write an `ss.Intervention` instead.

**Always call `super()` in lifecycle methods.** If you override `init_results()`, the first line must be `super().init_results()`. If you override `finalize_results()`, the first line must be `super().finalize_results()`. Forgetting these calls will break result array initialization and post-run cleanup, leading to missing or malformed results.

**Do not rely on execution order between analyzers.** Multiple analyzers run in list order within a timestep, but one analyzer should not read another analyzer's results from the current timestep. Each analyzer should depend only on the sim's state, not on side effects of other analyzers.

**Use `self.define_results()` for tracked results.** Do not manually create numpy arrays and attach them to `self`. Using `define_results(ss.Result('name'))` ensures results are properly sized to the simulation duration, correctly named, and automatically exported by `sim.to_df()`.

**Do not store large per-agent data in results.** `ss.Result` arrays are one value per timestep (scalars over time). If you need per-agent data, store it in a custom attribute (like `self.hist` in the age bins example) and convert it in `finalize_results()`.

## Quick reference

```python
# --- Function analyzer ---
def my_func(sim):
    print(sim.ti, sim.diseases.sir.prevalence)

sim = ss.Sim(analyzers=my_func, diseases='sir', networks='random')

# --- Class analyzer skeleton ---
class MyAnalyzer(ss.Analyzer):
    def init_results(self):
        super().init_results()
        self.define_results(ss.Result('my_metric'))

    def step(self):
        self.results['my_metric'][self.sim.ti] = <value>

sim = ss.Sim(analyzers=MyAnalyzer(), diseases='sir', networks='random')

# --- Built-in by string ---
sim = ss.Sim(analyzers='infection_log', diseases='sir', networks='random')

# --- Multiple analyzers ---
sim = ss.Sim(
    analyzers=[count_edges, HIV_preg(), 'infection_log'],
    diseases='sir',
    networks='random',
)

# --- Access results after run ---
sim.run()
sim.results.<analyzer_name>.<result_name>   # Time series array
sim.analyzers[0].plot()                      # Call plot() if defined
sim.to_df()                                  # Includes analyzer results
```

### Common sim attributes available in `step()`

| Access path | Returns |
|---|---|
| `self.sim.ti` | Current timestep index (int) |
| `self.sim.t.timevec` | Full array of simulation time points |
| `self.sim.people` | People object with agent states and attributes |
| `self.sim.people.age` | Agent ages (Arr) |
| `self.sim.people.alive` | Boolean Arr of living agents |
| `self.sim.people.states['disease.state']` | Boolean Arr for a named disease state |
| `self.sim.diseases.<name>` | Disease module by name |
| `self.sim.networks[0]` | First network; `len(network)` gives edge count |
| `self.sim.demographics.<name>` | Demographic module (e.g. `pregnancy`) |
