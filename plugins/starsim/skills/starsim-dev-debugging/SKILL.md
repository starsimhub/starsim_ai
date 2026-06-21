---
name: starsim-dev-debugging
description: Use when a Starsim simulation errors, crashes, or produces wrong/implausible results — diagnosing exceptions, silent failures (no epidemic, wrong scale), reproducibility issues, and reading Starsim's execution loop. For performance/slowness, use starsim-dev-profiling instead.
---

# Debugging Starsim Simulations

This skill is for **correctness** debugging: a sim that errors, crashes, or returns implausible results. For *performance* debugging (slow sims, bottleneck functions), use `starsim-dev-profiling`. Most Starsim bugs fall into a small number of categories, and the symptom usually points straight at the cause.

## First moves

1. **Read the traceback bottom-up.** Starsim raises descriptive `errormsg` strings; the message usually names the fix (e.g. locked attributes, missing required method calls).
2. **Make it reproducible.** Set `rand_seed` and keep `n_agents` small while debugging:
   ```python
   sim = ss.Sim(diseases='sir', networks='random', n_agents=200, rand_seed=1, verbose=0.1)
   ```
3. **Turn warnings into errors** to surface silently-swallowed problems and get a traceback at the source:
   ```python
   ss.options(warnings='error')          # globally
   with ss.options.context(warnings='error'):   # or scoped
       sim.run()
   ```
4. **Make missing lifecycle calls fatal.** If results are missing/malformed, a `super()` call was likely skipped:
   ```python
   ss.options(check_method_calls='die')  # default is 'warn'
   ```
5. **Inspect, don't guess.** Run partway and look at real state (see below) rather than reasoning about it in the abstract.

## Inspecting a running sim

```python
sim = ss.Sim(diseases='sir', networks='random', start=2000, stop=2020, verbose=0)
sim.run(until=2010)            # stop mid-run

sim.people.to_df()             # all agent state as a DataFrame
sim.people.person(0)           # one agent's full attribute set
sim.diseases.sir.infected.uids # who is infected right now
sim.diseases.sir.infected.sum()# how many
sim.results.sir.new_infections # time series so far

sim.loop.df.disp()             # exactly what runs, and in what order (see starsim-dev-profiling)
```

To watch a value evolve, drop in a function analyzer (runs at the end of every step) or a loop probe (runs at an exact point in the step) — both covered in `starsim-dev-profiling` and `starsim-dev-analyzers`.

```python
def watch(sim):
    print(sim.ti, 'infected:', sim.diseases.sir.infected.sum())

sim = ss.Sim(diseases='sir', networks='random', analyzers=watch)
sim.run()
```

When a crash happens inside a `MultiSim` or `ss.Calibration`, the real traceback is hidden by the worker pool. Re-run with `debug=True` (serial, single process) to get a readable traceback:

```python
ss.MultiSim(sim).run(debug=True)
ss.Calibration(..., debug=True).calibrate()
```

## Symptom → cause table

| Symptom | Most likely cause | Where to look |
|---|---|---|
| Epidemic never takes off (prevalence just decays) | No `networks=`/mixing pool, or `init_prev=0` | `starsim-dev-networks` |
| Transmission far too high/low; results change wildly with `dt` | `beta` wrapped in a rate (`ss.peryear`/`ss.perday`) — it must be a **bare float** | `starsim-dev-time` |
| Death/event rates wrong; change with timestep | Called `.to_prob()` before multiplying by relative factors, or wrong rate type | `starsim-dev-time` |
| `IndexError`/nonsense agents selected; breaks after deaths | Boolean state used as UIDs, `np.where(mask)[0]`, or positional vs UID indexing | `starsim-dev-indexing` |
| Off-by-one in "new cases this step" | Hand-rolled previous-step tracker instead of `ti_infected == ti-1` | `starsim-dev-indexing` |
| Custom state not tracked / lost on birth/death / missing from results | Stored as a plain attribute instead of `define_states([...])` | `starsim-dev-interventions`, `starsim-dev-diseases` |
| `AttributeError` for `self.sim` in `__init__`; init logic never runs | Put init logic in `__init__` or a fake `initialize(self, sim)`; use `init_post(self)` | `starsim-dev-interventions` |
| Custom intervention fires every timestep | `step()` is not auto-gated on `start`/`stop`; gate explicitly | `starsim-dev-interventions` |
| Results differ run-to-run with same seed; scenarios diverge spuriously | `np.random` used instead of `ss.<dist>`, or one dist reused for two decisions | `starsim-dev-random`, `starsim-dev-distributions` |
| `Cannot modify attribute "x"; locked attributes are ...` | Assigning to a state array by name; use `self.x[:] = value` (or `self.x[uids] = value`) | see below |
| Dead agents corrupt means/counts | Used `.raw` for a statistic; use the `Arr` method (`.mean()`) or `.values` | `starsim-dev-indexing` |
| `MultiSim`/list of sims runs slowly / serially | Looped `sim.run()` instead of `ss.parallel()`/`MultiSim.run()` | `starsim-dev-run` |
| Calibration won't converge | No data-driven `guess`, missing `reseed`/`n_reps`, or mutating standardized pars in `build_fn` | `starsim-dev-calibration` |

## Common error messages

### `Cannot modify attribute "x"; locked attributes are ...`

State arrays are locked to prevent accidentally replacing the array object. Assign *into* the array, don't rebind the name:

```python
# WRONG -- tries to replace the locked array
self.infected = new_values

# RIGHT -- assign into it
self.infected[:] = new_values        # all active agents
self.infected[uids] = True           # specific agents
```

### `The module <x> does not define a "step" method`

Every `ss.Module` subclass needs a `step(self)` method. If a module legitimately does nothing each step, define `def step(self): pass` explicitly.

### `The following methods are required, but were not called`

A lifecycle override skipped its `super()` call. Ensure overridden `init_results`/`finalize_results`/`init_post` call `super().<method>()` first (see `starsim-dev-analyzers`).

### `No matching module found for <query>`

`sim.diseases.<name>` / `sim.get_module(...)` couldn't find the module — check the module's `name` (defaults to the lowercased class name) and that it was actually added to the sim.

## Sanity checks for "the numbers look wrong"

Before assuming a deep bug, verify the inputs are what you think:

```python
sim.init()
sim.diseases.sir.pars.disp()                 # are beta/init_prev/durations what you set?
sim.diseases.sir.pars.dur_inf.plot_hist()    # does the duration distribution look right?
print(sim.t.timevec[[0, -1]], sim.dt)        # right time range and timestep?
print(len(sim.networks), [n.name for n in sim.networks])  # is there actually a network?
sim.loop.df.disp()                           # are modules running in the order you expect?
```

A large fraction of "wrong results" are actually wrong *inputs*: a `beta` wrapped in a rate, a missing network, a probability where a distribution was needed, or a `dt` that doesn't match the parameter units. Confirm the inputs first, then dig into logic.

## Anti-patterns

**Do not debug with `print` scattered through module source.** Use an analyzer or a `sim.loop.insert()` probe — they have full sim access and don't require editing library code.

**Do not debug at full scale.** Drop `n_agents` to a few hundred and shorten the time range; bugs reproduce just as well and iterate far faster.

**Do not silence warnings while debugging.** Warnings frequently flag the exact problem (automatic time conversions, missing method calls). Run with `warnings='error'` until the sim is clean.

**Do not chase stochastic noise.** If two runs differ, fix `rand_seed` first and confirm the difference is real before investigating.

## Quick reference

```python
import starsim as ss

# Reproducible, small, verbose
sim = ss.Sim(diseases='sir', networks='random', n_agents=200, rand_seed=1, verbose=0.1)

# Strict mode: surface hidden problems
ss.options(warnings='error', check_method_calls='die')

# Inspect mid-run
sim.run(until=2010)
sim.people.to_df()
sim.people.person(0)
sim.diseases.sir.infected.uids
sim.loop.df.disp()

# Readable tracebacks from parallel contexts
ss.MultiSim(sim).run(debug=True)

# Verify inputs
sim.init()
sim.diseases.sir.pars.disp()
sim.diseases.sir.pars.dur_inf.plot_hist()
```
