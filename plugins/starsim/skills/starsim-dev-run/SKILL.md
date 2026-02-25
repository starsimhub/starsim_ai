---
name: starsim-dev-run
description: Use when running multiple simulations, comparing scenarios, or parallelizing Starsim runs — including MultiSim, parallel(), and result aggregation.
---

# Running Multiple Simulations

Starsim provides `ss.parallel()` and `ss.MultiSim` for running multiple simulations, comparing scenarios, and computing summary statistics across replicates. Most real-world workflows require running many sims -- either different scenarios side by side or the same scenario with different random seeds to quantify uncertainty. This skill covers the full range of multi-sim workflows, from simple two-scenario comparisons to large-scale parameter sweeps with hundreds of runs.

## Key Classes

| Class / Function | Purpose | Key Parameters |
|------------------|---------|----------------|
| `ss.parallel(*sims)` | Run multiple sims in parallel using all cores | `*sims`, `verbose`, `inplace` |
| `ss.MultiSim` | Container for multiple sims; supports stats and plotting | `sims` (list or single sim), `n_runs` |
| `msim.run()` | Execute all sims in the MultiSim | `verbose` |
| `msim.mean()` | Reduce results to mean +/- 2 std dev | -- |
| `msim.median()` | Reduce results to median with 10th/90th quantiles | -- |
| `msim.reduce()` | General-purpose reduction with custom quantiles | `quantiles` |
| `msim.plot()` | Plot individual or reduced results | -- |
| `sc.parallelize()` | Parallelize arbitrary functions (from Sciris) | `func`, `iterkwargs` |

## Patterns

### Running different scenarios with ss.parallel()

The simplest way to compare scenarios is to create sims with different configurations and pass them to `ss.parallel()`:

```python
import starsim as ss

sim1 = ss.Sim(label='random', diseases='sis', networks='random')
sim2 = ss.Sim(label='randomsafe', diseases='sis', networks='randomsafe')
msim = ss.parallel(sim1, sim2)
msim.plot()
```

`ss.parallel()` returns a `MultiSim` object. It is a convenience wrapper around `ss.MultiSim().run()`. The equivalent longhand form gives you access to the `MultiSim` before running, which can be useful for configuration:

```python
sim1 = ss.Sim(diseases='sis', networks='random')
sim2 = ss.Sim(diseases='sis', networks='randomsafe')
msim = ss.MultiSim(sims=[sim1, sim2]).run(verbose=0)
msim.plot()
```

You can also construct sims in a loop and unpack them:

```python
betas = [0.05, 0.1, 0.2, 0.5]
sims = [ss.Sim(label=f'beta={b}', diseases=ss.SIR(beta=b), networks='random') for b in betas]
msim = ss.parallel(*sims)
msim.plot()
```

### Running replicates with different random seeds

Pass a single sim to `ss.MultiSim()` to automatically create replicates with different random seeds:

```python
sim = ss.Sim(n_agents=2000, diseases='sir', networks='random', verbose=0)
msim = ss.MultiSim(sim).run()
msim.plot()
```

By default this creates 5 replicates (controlled by `n_runs`). Each replicate gets a different random seed but identical parameters.

### Computing summary statistics

After running replicates, reduce the results to summary statistics:

```python
sim = ss.Sim(n_agents=2000, diseases='sir', networks='random', verbose=0)
msim = ss.MultiSim(sim).run()

# Mean with +/- 2 standard deviations
msim.mean()
msim.plot()

# Median with 10th/90th quantiles (preferred for bounded quantities)
msim.median()
msim.plot()
```

`msim.mean()` replaces the individual sim results with the mean and shows error bounds at +/- 2 standard deviations. `msim.median()` uses the median and shows the 10th and 90th quantiles by default. Use `msim.reduce()` for custom quantile ranges.

Key behavioral note: calling `msim.mean()` or `msim.median()` **mutates** the `MultiSim` object. After reduction, the individual sim results are replaced with the aggregate. Call `msim.plot()` after the reduction method to see the summarized results with uncertainty bands.

For custom quantiles, use `msim.reduce()` directly:

```python
msim.reduce(quantiles=[0.25, 0.75])  # Interquartile range
msim.plot()
```

### Reusing modules across sims (copy semantics)

Sims copy their inputs by default (`copy_inputs=True`), so you can safely share module objects between sims:

```python
sis = ss.SIS(beta=0.1)

s1 = ss.Sim(label='Low contacts', diseases=sis, networks=ss.RandomNet(n_contacts=5))
s2 = ss.Sim(label='High contacts', diseases=sis, networks=ss.RandomNet(n_contacts=10))
ss.parallel(s1, s2).plot()
```

The same `sis` object is passed to both sims, but each sim gets its own internal copy. This is safe and is the intended workflow. Without `copy_inputs=True`, the second sim would fail because the first sim's `init()` modifies the module in place (registering states, connecting to People, etc.).

### Accessing module state post-run with copy_inputs=False

If you need to access a module object directly after the sim runs, set `copy_inputs=False`:

```python
sir = ss.SIR(beta=0.035)
sim = ss.Sim(diseases=sir, networks='random', copy_inputs=False)
sim.run()
sir.plot()  # Works because sir IS the module used in the sim
```

Without `copy_inputs=False`, the `sir` object above would be the original (un-run) copy, and calling `sir.plot()` would fail or show no results.

### Copy semantics summary

Understanding which objects get copied is critical for correct workflows:

| Object | Default behavior | Override |
|--------|-----------------|----------|
| `ss.Sim` inputs (modules) | Copied (`copy_inputs=True`) | `ss.Sim(..., copy_inputs=False)` |
| `ss.MultiSim` sims | NOT copied (`inplace=True`) | `ss.parallel(..., inplace=False)` |

**Rule of thumb**: Sim copies its modules so you can share them; MultiSim does NOT copy sims so you can access results directly.

### MultiSim does not copy sims by default (inplace behavior)

Unlike `Sim`, `MultiSim` does **not** copy its input sims. Sims are modified in place when run:

```python
s1 = ss.Sim(diseases='sis', networks='random')
s2 = ss.Sim(diseases='sir', networks='random')
ss.parallel(s1, s2, verbose=0)

s1.plot()  # Works -- s1 was run in place
```

To prevent modification of the originals, use `inplace=False`:

```python
s1 = ss.Sim(diseases='sis', networks='random')
s2 = ss.Sim(diseases='sir', networks='random')
ss.parallel(s1, s2, verbose=0, inplace=False)

s1.run().plot()  # Works -- s1 was NOT run, so we can run it fresh
```

### The make_sim() pattern for parameterized sim creation

For complex models, define a `make_sim()` function that returns a configured sim. This is the standard pattern for production workflows:

```python
def make_sim(seed=1, n_agents=None, start=1990, stop=2030, debug=False):

    total_pop = {1990: 9980999, 2000: 11.83e6}[start]
    if n_agents is None:
        n_agents = [int(10e3), int(5e2)][debug]

    # Demographic modules
    pregnancy = ss.Pregnancy(dt='month', fertility_rate=fertility_data)
    death = ss.Deaths(death_rate=death_data, rate_units=1)

    # People and networks
    ppl = ss.People(n_agents)
    network = ss.RandomNet(n_contacts=4)

    # Diseases
    sir = ss.SIR(beta=0.1)

    sim = ss.Sim(
        dt=1/12,
        rand_seed=seed,
        total_pop=total_pop,
        start=start,
        stop=stop,
        people=ppl,
        diseases=[sir],
        networks=[network],
        demographics=[pregnancy, death],
    )
    return sim
```

Then run with different parameters:

```python
sims = [make_sim(seed=s) for s in range(5)]
msim = ss.parallel(*sims)
msim.median()
msim.plot()
```

### Parallelizing sim creation with sc.parallelize()

When `make_sim()` is computationally expensive (e.g., loading large data files), parallelize the sim creation itself using `sc.parallelize()` from Sciris:

```python
import sciris as sc

# Build the argument list
iterkwargs = []
for seed in range(100):
    for n_agents in [1e3, 2e3, 5e3, 10e3]:
        iterkwargs.append(dict(seed=seed, n_agents=n_agents))

# Create sims in parallel
sims = sc.parallelize(make_sim, iterkwargs=iterkwargs)

# Run sims in parallel
msim = ss.parallel(*sims)
```

This is especially useful for large parameter sweeps where you may create hundreds of sims. Note that `sc.parallelize()` handles sim **creation** in parallel, while `ss.parallel()` handles sim **execution** in parallel. For the largest sweeps, you may want to parallelize both steps.

### Combining replicates with scenarios

A common advanced pattern combines scenario comparison with stochastic replicates. Create multiple sims per scenario, run them all, then group by scenario for analysis:

```python
import starsim as ss

def make_sim(seed, network_type):
    return ss.Sim(
        label=network_type,
        rand_seed=seed,
        diseases='sir',
        networks=network_type,
        n_agents=2000,
        verbose=0,
    )

sims = []
for net in ['random', 'randomsafe']:
    for seed in range(10):
        sims.append(make_sim(seed, net))

msim = ss.parallel(*sims)
```

### Workflow decision tree

Use this to decide which approach fits the task:

- **Comparing 2-5 different configurations**: Create sims individually with labels, run with `ss.parallel()`, call `msim.plot()`.
- **Quantifying stochastic uncertainty**: Pass a single sim to `ss.MultiSim(sim).run()`, then call `msim.median()` and `msim.plot()`.
- **Parameter sweep (10+ configurations)**: Write a `make_sim()` function, build sims in a loop or with `sc.parallelize()`, run with `ss.parallel(*sims)`.
- **Scenarios with uncertainty**: Combine both -- create N replicates per scenario using `make_sim(seed, scenario)`, run all, then group and reduce.

### Production workflow end-to-end

A complete production workflow typically follows this pattern:

```python
import starsim as ss
import sciris as sc

# 1. Define parameterized sim builder
def make_sim(seed=0, beta=0.1, n_contacts=4):
    return ss.Sim(
        label=f'beta={beta}, contacts={n_contacts}',
        rand_seed=seed,
        n_agents=5000,
        diseases=ss.SIR(beta=beta),
        networks=ss.RandomNet(n_contacts=n_contacts),
        verbose=0,
    )

# 2. Build parameter grid
iterkwargs = []
for seed in range(20):
    for beta in [0.05, 0.1, 0.2]:
        iterkwargs.append(dict(seed=seed, beta=beta))

# 3. Create and run sims
sims = sc.parallelize(make_sim, iterkwargs=iterkwargs)
msim = ss.parallel(*sims)

# 4. Analyze results
msim.median()
msim.plot()
```

## Anti-Patterns

**Do not** use `msim.mean()` for bounded quantities like deaths, prevalence counts, or any non-negative measure. Mean +/- 2 standard deviations can produce impossible values (e.g., negative deaths) because the error bounds are symmetric and do not respect natural constraints. Use `msim.median()` instead, which shows quantile-based bounds that remain within realistic ranges:

```python
# WRONG -- error bounds can go negative for counts
msim.mean()
msim.plot()  # Shows negative death counts in error bounds

# CORRECT -- quantile bounds respect natural constraints better
msim.median()
msim.plot()  # Shows 10th/90th quantiles, stays non-negative
```

**Do not** assume `ss.parallel()` leaves original sims unmodified. By default, sims are run in place (`inplace=True` in MultiSim). If you need the originals unchanged, pass `inplace=False`:

```python
# WRONG assumption -- s1 has been modified
s1 = ss.Sim(diseases='sir', networks='random')
ss.parallel(s1, verbose=0)
s1.run()  # Already ran, results overwritten

# CORRECT -- preserve originals
s1 = ss.Sim(diseases='sir', networks='random')
ss.parallel(s1, verbose=0, inplace=False)
s1.run()  # Safe, s1 was not modified
```

**Do not** try to access module state post-run when `copy_inputs=True` (the default). The module you passed in is not the same object used in the sim:

```python
# WRONG -- sir was copied, this is the original unused object
sir = ss.SIR(beta=0.1)
sim = ss.Sim(diseases=sir, networks='random')
sim.run()
sir.plot()  # Plots nothing useful -- sir was never run

# CORRECT -- either use copy_inputs=False or access via sim
sir = ss.SIR(beta=0.1)
sim = ss.Sim(diseases=sir, networks='random', copy_inputs=False)
sim.run()
sir.plot()  # Works

# ALSO CORRECT -- access the module through the sim
sim.diseases.sir.plot()
```

**Do not** forget to label sims when comparing scenarios. Labels appear in plot legends and are essential for distinguishing results:

```python
# WRONG -- no way to tell plots apart
sim1 = ss.Sim(diseases='sis', networks='random')
sim2 = ss.Sim(diseases='sis', networks='randomsafe')

# CORRECT
sim1 = ss.Sim(label='Random network', diseases='sis', networks='random')
sim2 = ss.Sim(label='Safe network', diseases='sis', networks='randomsafe')
```

**Do not** create sims inside `ss.parallel()` arguments. Build the sim list first, then pass it. This makes debugging easier and allows inspection before running:

```python
# WRONG -- hard to debug if something fails
msim = ss.parallel(
    ss.Sim(diseases='sir', networks='random'),
    ss.Sim(diseases='sis', networks='random'),
)

# CORRECT -- sims are inspectable before running
sim1 = ss.Sim(label='SIR', diseases='sir', networks='random')
sim2 = ss.Sim(label='SIS', diseases='sis', networks='random')
msim = ss.parallel(sim1, sim2)
```

## Quick Reference

| Task | Code |
|------|------|
| Run two sims in parallel | `ss.parallel(sim1, sim2)` |
| Run sims without modifying originals | `ss.parallel(sim1, sim2, inplace=False)` |
| Replicates with different seeds | `ss.MultiSim(sim).run()` |
| Explicit MultiSim construction | `ss.MultiSim(sims=[sim1, sim2]).run()` |
| Mean +/- 2 std dev | `msim.mean(); msim.plot()` |
| Median with 10th/90th quantiles | `msim.median(); msim.plot()` |
| Custom quantile reduction | `msim.reduce(quantiles=[0.25, 0.75])` |
| Reuse module across sims | Pass same object to multiple `Sim()` calls (copied by default) |
| Access module state post-run | `ss.Sim(diseases=sir, copy_inputs=False)` |
| Parameterized sim creation | Define `make_sim(seed=0, ...)` returning `ss.Sim(...)` |
| Parallelize sim creation | `sc.parallelize(make_sim, iterkwargs=kwargs_list)` |
| Suppress output during runs | `msim.run(verbose=0)` or `ss.parallel(s1, s2, verbose=0)` |
| Set number of replicates | `ss.MultiSim(sim, n_runs=20).run()` |
| Loop-based scenario comparison | `sims = [ss.Sim(label=f'b={b}', diseases=ss.SIR(beta=b), networks='random') for b in betas]` |
| Full parameter sweep | `sc.parallelize(make_sim, iterkwargs=kwarg_list)` then `ss.parallel(*sims)` |

## Notes on Performance

- `ss.parallel()` uses all available CPU cores by default. For machines with many cores and small sims, the overhead of multiprocessing may exceed the computation time. In such cases, consider running sequentially with a simple loop.
- `sc.parallelize()` also uses multiprocessing. When both sim creation and sim execution are parallelized, be mindful of total memory usage -- each process holds a full copy of the sim in memory.
- For very large sweeps (hundreds of sims), consider running in batches to avoid memory exhaustion: create and run 50 sims at a time, extract results, then proceed to the next batch.
- The `verbose=0` parameter suppresses per-sim progress output, which significantly cleans up console output when running many sims and avoids interleaved log messages from parallel processes.
