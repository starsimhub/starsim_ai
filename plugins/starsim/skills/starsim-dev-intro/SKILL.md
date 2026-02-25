---
name: starsim-dev-intro
description: Use when the user is new to Starsim, needs to set up a first model, or wants to understand the basic architecture (Sim, People, modules).
---

# Starsim Introduction Reference

Starsim is a highly flexible agent-based modeling framework primarily designed for infectious disease modeling, though it also supports NCDs, family planning, and other domains. Models are assembled from modular components (People, Networks, Diseases, Demographics, Interventions, Analyzers, Connectors) that plug into a central `Sim` object. Common tasks -- defining parameters, running a simulation, plotting results -- are designed to be simple.

## Key Classes

| Class | Purpose | Key Parameters |
|-------|---------|----------------|
| `ss.Sim` | Assembles, initializes, and runs the model; stores top-level parameters and results | `n_agents`, `networks`, `diseases`, `demographics`, `interventions`, `analyzers`, `connectors`, `start`, `stop`, `dt`, `total_pop`, `rand_seed` |
| `ss.People` | Stores per-agent states (age, sex, alive) as arrays; extended by modules with disease-specific states | `n_agents` |
| `ss.SIR` | SIR (susceptible-infected-recovered) disease module | `beta`, `init_prev`, `dur_inf`, `p_death` |
| `ss.SIS` | SIS (susceptible-infected-susceptible) disease module | `beta`, `init_prev`, `dur_inf` |
| `ss.RandomNet` | Random contact network where each agent has a configurable number of contacts per timestep | `n_contacts` |
| `ss.Results` | Nested dictionary-like structure of time-series outputs from all modules | accessed via `sim.results` |

## Installation and Import

```python
pip install starsim
```

```python
import starsim as ss
```

For nicer plotting in Jupyter notebooks, add:

```python
ss.options(jupyter=True)
```

## Initialization Patterns

Starsim supports three ways to configure a simulation. All produce equivalent models.

### Pattern 1: Dict-based (quick prototyping)

All parameters are passed as a single dictionary. Network and disease types are specified by `type` key strings. This is the simplest approach and good for one-off explorations.

```python
import starsim as ss
ss.options(jupyter=True)

pars = dict(
    n_agents = 10_000,
    networks = dict(
        type = 'random',
        n_contacts = 10,
    ),
    diseases = dict(
        type = 'sir',
        init_prev = 0.01,
        beta = 0.05,
    ),
)

sim = ss.Sim(pars)
sim.run()
sim.plot()
sim.diseases.sir.plot()
```

The `pars` dictionary feeds directly into `ss.Sim()`. Under the hood, `type = 'random'` maps to `ss.RandomNet` and `type = 'sir'` maps to `ss.SIR`. Other recognized string types include `'sis'` for `ss.SIS`.

### Pattern 2: Component-based (more control, recommended)

Components are instantiated individually and passed to `Sim` as keyword arguments. This is the preferred style for anything beyond a quick prototype because it gives direct access to module objects before and after the run.

```python
import starsim as ss

people = ss.People(n_agents=5_000)
network = ss.RandomNet(n_contacts=4)
sir = ss.SIR(init_prev=0.1, beta=0.1)

sim = ss.Sim(diseases=sir, people=people, networks=network)
sim.run()
sim.plot()
```

With the component-based approach, you can inspect and configure each module independently before combining them into a simulation. You can also reference the module objects after the run (e.g., `sir.results`) without navigating through the sim.

### Pattern 3: Shorthand string notation

For the most common built-in modules, you can pass a string name instead of a dict or object. This is the most concise approach for quick tests.

```python
sim = ss.Sim(diseases='sis', networks='random')
sim.run()
sim.plot()
```

Recognized string names include `'sir'`, `'sis'` for diseases and `'random'` for networks. All other parameters use defaults when passed as strings.

## Sim Constructor Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `n_agents` | 10,000 | Number of agents in the simulation. Larger values give smoother results but run slower. |
| `total_pop` | None | Total population the agents represent. When set, results are scaled up from the simulated agents. |
| `networks` | None | Network(s) defining how agents contact each other. Accepts a string, dict, object, or list of these. |
| `diseases` | None | Disease module(s) to simulate. Accepts a string, dict, object, or list of these. |
| `demographics` | None | Demographics module(s) for births, deaths, migration. |
| `interventions` | None | Intervention(s) such as vaccines, treatments, screening. |
| `analyzers` | None | Analyzer(s) for custom result collection. |
| `connectors` | None | Connector(s) for multi-disease interactions. |
| `start` | 1995 | Simulation start. Can be an integer year (e.g., `2020`) or a date string (e.g., `'2020-01-01'`). |
| `stop` | 2030 | Simulation stop. Same format as `start`. |
| `dt` | 1.0 | Timestep in years. Use `ss.months(n)` or `ss.days(n)` helpers for sub-annual steps. |
| `rand_seed` | 0 | Random seed for reproducibility. |

Multiple modules of the same type can be passed as a list, e.g. `diseases=[ss.SIR(), ss.SIS()]` for multi-disease models.

## Time Configuration

The default simulation runs from 1995 to 2030 with an annual timestep (dt=1.0). Override with `start`, `stop`, and `dt`. Date strings allow precise sub-annual start/stop dates.

```python
# Monthly timestep, one year of simulation
sim = ss.Sim(
    start = '2020-01-01',
    stop = '2021-01-01',
    dt = ss.months(1),
    diseases = 'sis',
    networks = network,
)
sim.run()
sim.plot()
```

### Time helper functions

| Helper | Meaning | Example |
|--------|---------|---------|
| `ss.days(n)` | n days as a fraction of a year | `ss.days(1)` = ~0.00274 years |
| `ss.months(n)` | n months as a fraction of a year | `ss.months(1)` = ~0.0833 years |

These helpers return floats representing fractions of a year. Use them for the `dt` parameter and anywhere a duration in years is expected.

### Common time configurations

```python
# Daily timestep over 3 months
ss.Sim(start='2020-01-01', stop='2020-04-01', dt=ss.days(1), ...)

# Weekly timestep over 1 year
ss.Sim(start='2020-01-01', stop='2021-01-01', dt=ss.days(7), ...)

# Monthly timestep over 5 years
ss.Sim(start=2020, stop=2025, dt=ss.months(1), ...)

# Annual timestep (default) over 35 years
ss.Sim(start=1995, stop=2030, ...)
```

## Distribution-Based Parameters

Many parameters accept distribution objects to introduce heterogeneity across agents. Instead of every agent having the same value, each agent draws an independent sample. Two equivalent syntaxes are available.

```python
# Object syntax (preferred, more readable)
network = ss.RandomNet(n_contacts=ss.poisson(4))

# Dict syntax (equivalent, used in dict-based pars)
network = ss.RandomNet(n_contacts=dict(type='poisson', lam=4))
```

With either syntax, agents will have varying numbers of contacts drawn from a Poisson distribution with mean 4. The object syntax is generally preferred for clarity; the dict syntax is necessary when specifying distributions inside a parameters dictionary.

Distributions can be used for disease parameters as well, such as duration of infection, to capture real-world variability between agents. Common distribution types include `ss.poisson()`, `ss.normal()`, `ss.lognormal()`, and `ss.uniform()`.

## Module Update Order

On each timestep, modules are updated in this fixed order:

1. **Demographics** -- births, deaths, migration (new agents enter the population)
2. **Diseases (state updates)** -- progress through disease states (e.g., infected to recovered)
3. **Connectors** -- cross-disease interactions (e.g., HIV increases TB susceptibility)
4. **Networks** -- update contact layers (re-draw contacts for the new timestep)
5. **Interventions** -- apply vaccines, treatments, screening
6. **Diseases (transmission)** -- transmit infections over the updated networks
7. **Analyzers** -- collect custom results at the end of the timestep

This order matters and is not configurable. Key implications:
- Demographics runs first so newborns exist before disease updates process them.
- Networks update before transmission so contacts are fresh for each transmission step.
- Disease state updates happen before transmission, so agents that recover this timestep will not transmit.
- Interventions run between network updates and transmission, so a vaccine applied this timestep can reduce transmission probability immediately.
- Analyzers run last, capturing the final state after all other updates.

## What Happens at Initialization

When `sim.init()` is called (it is automatically called by `sim.run()` if not already done), the following integration occurs:

- Each module's parameters are added to the sim's centralized parameter dictionary, making them accessible via `sim.pars.<module_name>.<param>`.
- Each module's states (e.g., whether agents are infected) are added to `People`, accessible via `sim.people.<module_name>.<state>` or `sim.diseases.<module_name>.<state>`.
- Each module's results are registered in the sim's centralized Results, accessible via `sim.results.<module_name>.<result>` or `sim.diseases.<module_name>.results.<result>`.

```python
import starsim as ss

sir = ss.SIR(dur_inf=10, beta=0.2, init_prev=0.4, p_death=0.2)
sim = ss.Sim(diseases=sir, networks='random')
sim.init()

# Parameters -- two equivalent access paths:
sim.pars.sir.init_prev            # via centralized pars
sim.diseases.sir.pars.init_prev   # via the module directly

# States -- two equivalent access paths:
sim.people.sir.infected           # via People
sim.diseases.sir.infected         # via the module directly

# Results (populated after run, not init):
# sim.results.sir.n_infected
# sim.diseases.sir.results.n_infected
```

You can call `sim.init()` without `sim.run()` when you want to inspect the initialized model structure, check that modules are wired correctly, or examine the initial state of the People population before any timesteps execute.

## Accessing Results

After `sim.run()`, all results are stored under `sim.results` as a nested structure keyed by module name. Top-level keys include core outputs like `n_alive`, `new_deaths`, `births`, `deaths`, plus one key per disease module.

```python
sim.run()

# Top-level results
sim.results.n_alive              # Population size over time
sim.results.new_deaths           # Deaths per timestep

# Disease-specific results
sim.results.sir.n_infected       # Number currently infected at each timestep
sim.results.sir.new_infections   # New infections per timestep
```

### Plotting

Starsim provides built-in plotting for both the sim and individual modules:

```python
sim.plot()                # Plot core sim-level results (population, deaths)
sim.diseases.sir.plot()   # Plot disease-specific results (S, I, R curves)
```

### Export results to DataFrame

The `sim.to_df()` method converts time-series results into a pandas DataFrame, suitable for further analysis or export:

```python
df = sim.to_df()
df.to_excel('results.xlsx')
```

### Export per-agent data to DataFrame

The `sim.people.to_df()` method exports per-agent state at the end of the simulation. This includes all base states (age, sex, alive) plus any states added by modules (e.g., disease infection status, time of infection):

```python
sim = ss.Sim(n_agents=20, diseases=dict(type='sis', init_prev=0.2), networks='random')
sim.run()
df = sim.people.to_df()
df.disp()
```

Even with a simple single-disease model, each agent can have many tracked states, generating a rich per-agent dataset.

## Saving and Loading

### Save a sim (shrunken by default)

By default, `save()` removes large objects like `People` to reduce file size. The saved sim retains results for analysis but cannot be resumed or re-run.

```python
sim.save('example.sim')
new_sim = ss.load('example.sim')
```

### Save full sim (for resuming)

Pass `shrink=False` to preserve all internal state, including People. This allows reloading the sim and continuing the run.

```python
sim.save('example-big.sim', shrink=False)
```

### Save arbitrary objects

The `ss.save()` and `ss.load()` functions can serialize any Python object (DataFrames, dicts, custom objects) using the same mechanism:

```python
df = sim.to_df()
ss.save('example.df', df)
new_df = ss.load('example.df')
```

For human-readable export, convert to a DataFrame first, then use pandas I/O:

```python
df = sim.to_df()
df.to_excel('results.xlsx')
```

## Complete Worked Examples

### Example 1: Minimal SIR with dict-based configuration

This is the simplest possible Starsim model. It creates 10,000 agents with a random contact network and an SIR disease, runs the simulation over the default 35-year period, and plots both sim-level and disease-level results.

```python
import starsim as ss
ss.options(jupyter=True)

pars = dict(
    n_agents = 10_000,
    networks = dict(
        type = 'random',
        n_contacts = 10,
    ),
    diseases = dict(
        type = 'sir',
        init_prev = 0.01,
        beta = 0.05,
    ),
)

sim = ss.Sim(pars)
sim.run()
sim.plot()
sim.diseases.sir.plot()
```

### Example 2: Component-based SIR with custom disease parameters

This example uses the component-based style, which is more explicit and provides direct handles to each module. It also demonstrates additional SIR parameters like `dur_inf` and `p_death`.

```python
import starsim as ss

people = ss.People(n_agents=5_000)
network = ss.RandomNet(n_contacts=4)
sir = ss.SIR(dur_inf=10, beta=0.2, init_prev=0.4, p_death=0.2)

sim = ss.Sim(diseases=sir, people=people, networks=network)
sim.run()
sim.plot()
```

### Example 3: Short-term SIS model with monthly timestep

This demonstrates time configuration for a sub-annual model. It simulates an SIS disease over one year with a monthly timestep using heterogeneous contact counts.

```python
import starsim as ss

network = ss.RandomNet(n_contacts=ss.poisson(4))
sim = ss.Sim(
    start = '2020-01-01',
    stop = '2021-01-01',
    dt = ss.months(1),
    diseases = 'sis',
    networks = network,
)
sim.run()
sim.plot()
```

### Example 4: Inspecting people states

This demonstrates how to initialize a sim and inspect the per-agent data without running.

```python
import starsim as ss

sim = ss.Sim(n_agents=10)
sim.init()
df = sim.people.to_df()
print(df)
```

### Example 5: Save, load, and export workflow

```python
import starsim as ss

sim = ss.Sim(diseases='sir', networks='random', n_agents=5_000)
sim.run()

# Save compact version (results only)
sim.save('results.sim')

# Save full version (can resume)
sim.save('full.sim', shrink=False)

# Export to DataFrame and Excel
df = sim.to_df()
df.to_excel('results.xlsx')

# Save/load arbitrary objects
ss.save('dataframe.df', df)
loaded_df = ss.load('dataframe.df')

# Reload sim
reloaded = ss.load('results.sim')
```

## Anti-Patterns

### Do not mix component objects into the pars dict

The `pars` dict expects plain dicts for modules (with `type` keys), not instantiated objects. Pass objects as keyword arguments instead.

```python
# WRONG -- mixing instantiated objects into the pars dict
pars = dict(n_agents=5000, diseases=ss.SIR(beta=0.1))
sim = ss.Sim(pars)

# CORRECT -- pass objects as keyword arguments
sim = ss.Sim(n_agents=5000, diseases=ss.SIR(beta=0.1))
```

### Do not access results before running

Results are only populated after `sim.run()` (or at minimum `sim.init()` for structure inspection).

```python
# WRONG -- results don't exist yet
sim = ss.Sim(diseases='sir', networks='random')
sim.results.sir.n_infected  # Error

# CORRECT
sim.run()
sim.results.sir.n_infected
```

### Do not assume the timestep is days

The default `dt` is 1.0, meaning one year per timestep. For sub-annual models, always set `dt` explicitly.

```python
# WRONG -- dt defaults to 1 year, not 1 day
sim = ss.Sim(start='2020-01-01', stop='2020-03-01', diseases='sir', networks='random')

# CORRECT -- explicitly set daily timestep
sim = ss.Sim(start='2020-01-01', stop='2020-03-01', dt=ss.days(1), diseases='sir', networks='random')
```

### Do not forget networks for transmissible diseases

Without a network, agents have no contacts, and no transmission occurs. The disease will simply decay as initial infections recover.

```python
# WRONG -- no transmission will occur
sim = ss.Sim(diseases='sir')

# CORRECT -- provide a contact network
sim = ss.Sim(diseases='sir', networks='random')
```

### Do not use shrink=False unless necessary

The default shrunken save is much smaller. Only use `shrink=False` when you need to reload and continue running.

### Do not reduce n_agents too far for reliable results

Very small populations (e.g., 200 agents) produce noisy, unreliable results due to stochastic effects. Use at least a few thousand agents for meaningful epidemic dynamics, or use `total_pop` to scale results from a smaller sample.

## Key Disease Parameters

The epidemic trajectory depends heavily on three parameters:

| Parameter | Module | Effect |
|-----------|--------|--------|
| `beta` | Disease | Probability of transmission per contact per timestep. Higher beta = faster spread. |
| `n_contacts` | Network | Average number of contacts per agent per timestep. More contacts = more transmission opportunities. |
| `dur_inf` | Disease | Duration of infection (in timestep units). Longer duration = more time to transmit. |

The basic reproduction number (R0) depends on the combination of all three. Experiment with different values and compare `sim.results.sir.n_infected` trajectories.

## Quick Reference

| Task | Code |
|------|------|
| Create and run minimal SIR | `ss.Sim(diseases='sir', networks='random').run()` |
| Component-based SIR | `ss.Sim(diseases=ss.SIR(beta=0.1), networks=ss.RandomNet(n_contacts=4))` |
| SIR with death | `ss.SIR(dur_inf=10, beta=0.2, init_prev=0.4, p_death=0.2)` |
| Set time range | `ss.Sim(start='2020-01-01', stop='2021-01-01', dt=ss.months(1), ...)` |
| Monthly timestep | `dt=ss.months(1)` |
| Daily timestep | `dt=ss.days(1)` |
| Weekly timestep | `dt=ss.days(7)` |
| Poisson-distributed contacts | `ss.RandomNet(n_contacts=ss.poisson(4))` |
| Dict-style Poisson contacts | `ss.RandomNet(n_contacts=dict(type='poisson', lam=4))` |
| Run and plot | `sim.run(); sim.plot()` |
| Plot disease results | `sim.diseases.sir.plot()` |
| Get infected count | `sim.results.sir.n_infected` |
| Get new infections | `sim.results.sir.new_infections` |
| Get population size | `sim.results.n_alive` |
| Export results to DataFrame | `sim.to_df()` |
| Export results to Excel | `sim.to_df().to_excel('file.xlsx')` |
| Export people to DataFrame | `sim.people.to_df()` |
| Save sim (compact) | `sim.save('file.sim')` |
| Save sim (full, resumable) | `sim.save('file.sim', shrink=False)` |
| Load sim or object | `ss.load('file.sim')` |
| Save arbitrary object | `ss.save('file.obj', obj)` |
| Initialize without running | `sim.init()` |
| Access parameters post-init | `sim.pars.sir.init_prev` |
| Access people states post-init | `sim.people.sir.infected` |
| Nice Jupyter plots | `ss.options(jupyter=True)` |
