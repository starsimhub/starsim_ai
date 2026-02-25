---
name: starsim-dev-calibration
description: Use when calibrating a Starsim model to data — including Optuna-based optimization, likelihood components, custom evaluation functions, and Bayesian approaches.
---

# Calibration

Starsim provides built-in integration with Optuna for optimization-based model calibration through the `ss.Calibration` class. The workflow has three parts: define calibration parameters with search ranges, write a `build_fn` that maps those parameters onto an uninitialized sim, and specify either likelihood `components` or a custom `eval_fn` that scores each trial. Starsim also supports Bayesian sampling-importance-resampling workflows using the same simulation machinery.

## Key Classes

| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `ss.Calibration` | Orchestrate Optuna-based calibration | `sim`, `calib_pars`, `build_fn`, `build_kw`, `components`, `eval_fn`, `eval_kw`, `total_trials`, `n_workers`, `reseed`, `debug` |
| `ss.Normal` | Gaussian likelihood component | `name`, `expected`, `extract_fn`, `conform`, `sigma2`, `weight` |
| `ss.BetaBinomial` | Beta-binomial likelihood component | `name`, `expected`, `extract_fn`, `conform`, `weight` |
| `ss.Binomial` | Binomial likelihood component | `name`, `expected`, `extract_fn`, `conform`, `weight` |
| `ss.GammaPoisson` | Gamma-Poisson likelihood component | `name`, `expected`, `extract_fn`, `conform`, `weight` |
| `ss.DirichletMultinomial` | Dirichlet-multinomial likelihood component | `name`, `expected`, `extract_fn`, `conform`, `weight` |

## Patterns

### Calibration parameters

Define a dict of parameters for Optuna to search. Each entry must have `low`, `high`, and `guess`. Optionally specify `suggest_type` (default `suggest_float`) and `log` for log-scale search.

```python
calib_pars = dict(
    beta = dict(low=0.01, high=0.30, guess=0.15, suggest_type='suggest_float', log=True),
    init_prev = dict(low=0.01, high=0.05, guess=0.15),
    n_contacts = dict(low=2, high=10, guess=3, suggest_type='suggest_int'),
)
```

The `guess` value is not used by Optuna itself -- it is only used by `check_fit()` to compare the optimized parameters against initial guesses.

### Base sim factory

Create a function that returns an uninitialized `Sim` with default parameters:

```python
import starsim as ss

def make_sim():
    sir = ss.SIR(
        beta=ss.perday(0.075),
        init_prev=ss.bernoulli(0.02),
    )
    random = ss.RandomNet(n_contacts=ss.poisson(4))

    sim = ss.Sim(
        n_agents=2_000,
        start=ss.date('2020-01-01'),
        stop=ss.date('2020-02-12'),
        dt=ss.days(1),
        diseases=sir,
        networks=random,
        verbose=0,
    )
    return sim
```

### Build function

The `build_fn` receives an uninitialized sim plus the `calib_pars` dict (now augmented with a `value` key per parameter chosen by Optuna). Modify `sim.pars` attributes and return either a `Sim` or a `MultiSim`.

```python
import numpy as np

def build_sim(sim, calib_pars, n_reps=1, **kwargs):
    sir = sim.pars.diseases
    net = sim.pars.networks

    for k, pars in calib_pars.items():
        if k == 'rand_seed':
            sim.pars.rand_seed = pars['value']
            continue

        v = pars['value']
        if k == 'beta':
            sir.pars.beta = ss.perday(v)
        elif k == 'init_prev':
            sir.pars.init_prev = ss.bernoulli(v)
        elif k == 'n_contacts':
            net.pars.n_contacts = ss.poisson(v)
        else:
            raise NotImplementedError(f'Parameter {k} not recognized')

    if n_reps == 1:
        return sim

    # MultiSim for stochastic averaging -- must use parallel=False and debug=True inside calibration
    ms = ss.MultiSim(
        sim,
        iterpars=dict(rand_seed=np.random.randint(0, 1e6, n_reps)),
        initialize=True,
        debug=True,
        parallel=False,
    )
    return ms
```

### CalibComponent with Normal likelihood

Each component compares simulation output to observed data. The `expected` DataFrame must have a `pd.Index` named `t`. The `extract_fn` pulls the corresponding quantity from a completed sim and also returns a DataFrame indexed by `t`.

```python
import pandas as pd

prevalence = ss.Normal(
    name='Disease prevalence',
    conform='prevalent',
    expected=pd.DataFrame({
        'x': [0.13, 0.16, 0.06],
    }, index=pd.Index(
        [ss.date(d) for d in ['2020-01-12', '2020-01-25', '2020-02-02']],
        name='t',
    )),
    extract_fn=lambda sim: pd.DataFrame({
        'x': sim.results.sir.prevalence,
    }, index=pd.Index(sim.results.timevec, name='t')),
    sigma2=0.05,  # Optional: single float or array matching expected shape
)
```

### CalibComponent with BetaBinomial likelihood

Use when you have count data with numerator (`x`) and denominator (`n`):

```python
prevalence_component = ss.BetaBinomial(
    name='SIR Disease Prevalence',
    conform='step_containing',
    expected=starsim_data[['x', 'n']],  # DataFrame with columns x, n and Index named 't'
    extract_fn=lambda sim: pd.DataFrame({
        'x': sim.results.sir.n_infected,
        'n': sim.results.n_alive,
    }, index=pd.Index(sim.results.timevec, name='t')),
)
```

### Conformers

Conformers align simulation output (every timestep) to sparse observed data:

| Conformer | Behavior | Use case |
|-----------|----------|----------|
| `'step_containing'` | Select the simulation timestep containing each observation time | Point-in-time surveys |
| `'prevalent'` | Interpolate simulation values at each observation time | Prevalence data |
| `'incident'` | Sum events between `t` and `t1` columns in expected data | Incidence/flow data over intervals |

### Full calibration setup

```python
import sciris as sc

sim = make_sim()

calib = ss.Calibration(
    calib_pars=calib_pars,
    sim=sim,
    build_fn=build_sim,
    build_kw=dict(n_reps=3),
    reseed=True,
    components=[prevalence],
    total_trials=100,
    n_workers=None,   # None = use all available CPUs
    die=True,
    debug=False,
    verbose=0,
)

calib.calibrate()
```

### Inspecting results

```python
# Best parameters found
calib.best_pars

# Compare guess vs. best with more replicates
calib.build_kw['n_reps'] = 15
calib.check_fit(do_plot=False)

# Plot likelihood distributions: guess (top) vs. best (bottom)
calib.plot()

# Bootstrap plot: resample n_reps with replacement, plot distribution of means
calib.plot(bootstrap=True)

# Plot final fitted simulations
calib.plot_final()

# Export top K trials as a DataFrame
df = calib.to_df(top_k=10)
```

### Optuna diagnostic plots

```python
calib.plot_optuna('plot_optimization_history')
calib.plot_optuna('plot_contour')
calib.plot_optuna('plot_param_importances')

# Multiple plots at once
figs = calib.plot_optuna(['plot_optimization_history', 'plot_contour'])
```

Available Optuna plots: `plot_contour`, `plot_edf`, `plot_optimization_history`, `plot_parallel_coordinate`, `plot_param_importances`, `plot_rank`, `plot_slice`, `plot_timeline`.

### Custom eval_fn (no components)

Instead of components, provide a function that receives a completed sim (or MultiSim) and returns a mismatch float (lower is better):

```python
my_data = (ss.date('2020-01-12'), 0.13)

def eval(sim, expected):
    date, p = expected
    if not isinstance(sim, ss.MultiSim):
        sim = ss.MultiSim(sims=[sim])

    ret = 0
    for s in sim.sims:
        ind = np.searchsorted(s.results.timevec, date, side='left')
        prev = s.results.sir.prevalence[ind]
        ret += (prev - p) ** 2
    return ret

calib = ss.Calibration(
    calib_pars=calib_pars,
    sim=make_sim(),
    build_fn=build_sim,
    build_kw=dict(n_reps=2),
    reseed=True,
    eval_fn=eval,
    eval_kw=dict(expected=my_data),
    total_trials=20,
    n_workers=None,
    die=True,
    debug=False,
    verbose=0,
)

calib.calibrate()
calib.check_fit()
```

### Custom Optuna sampler

You can pass an Optuna sampler to control the search strategy:

```python
import optuna

calib = ss.Calibration(
    sim=sim,
    calib_pars=calib_pars,
    build_fn=modify_sim,
    reseed=True,
    components=[prevalence_component],
    total_trials=100,
    sampler=optuna.samplers.TPESampler(n_startup_trials=50),
)
```

### Bayesian workflow (sampling-importance-resampling)

For full posterior inference, run many simulations from prior samples and weight by likelihood. This uses Starsim's simulation infrastructure but manages the calibration loop externally:

```python
import sciris as sc

def run_starsim(pars, rand_seed=0):
    sim = make_sim()
    sim = modify_sim(sim, pars, rand_seed)
    sim.run()
    results = pd.DataFrame(dict(
        S=sim.results.sir.n_susceptible,
        I=sim.results.sir.n_infected,
        R=sim.results.sir.n_recovered,
    ), index=pd.Index(sim.results.timevec, name='Time'))
    return results

N = 1000
prior_samples = pd.DataFrame({
    'beta': np.random.uniform(0, 0.15, N),
    'gamma': np.random.uniform(0, 0.08, N),
})

sample_pars_list = [
    {'pars': {'beta': {'value': row['beta']}, 'gamma': {'value': row['gamma']}},
     'rand_seed': idx}
    for idx, row in prior_samples.iterrows()
]

results_list = sc.parallelize(run_starsim, iterkwargs=sample_pars_list)

# Compute likelihoods, then resample with probability proportional to likelihood
weights = likelihoods / likelihoods.sum()
ESS = 1 / np.sum(weights ** 2)
K = int(np.ceil(1.5 * ESS))
posterior_indices = np.random.choice(N, size=K, replace=True, p=weights)
```

## Anti-patterns

**Do not forget `log=True` for multiplicative parameters.** Parameters like `beta` have multiplicative effects: doubling from 0.01 to 0.02 has a much larger impact than 0.11 to 0.12. Always set `log=True` so Optuna searches on a log scale.

**Do not modify initialized objects in `build_fn`.** The sim passed to `build_fn` has NOT been initialized. Modify `sim.pars.diseases`, `sim.pars.networks`, etc. -- not runtime objects. For example, use `sim.pars.diseases.pars['beta'] = ss.perday(v)`, not `sim.diseases.sir.beta = v`.

**Do not return likelihood from `eval_fn`.** The `eval_fn` must return a mismatch score where lower is better. Optuna is configured to minimize. If you return a likelihood (higher is better), the optimizer will find the worst parameters.

**Do not use `parallel=True` for MultiSim inside calibration.** When `build_fn` returns a `MultiSim`, set `parallel=False` and `debug=True` on the MultiSim to avoid nested parallelism conflicts with Optuna's worker pool.

**Do not forget the `'t'` index name on DataFrames.** Both `expected` and the DataFrame returned by `extract_fn` must have their index named `'t'`. Missing this causes conformer alignment to fail silently.

**Do not use `reseed=False` with stochastic models.** Without reseeding, every trial uses the same random seed, preventing the optimizer from distinguishing parameter effects from stochastic noise. Set `reseed=True` (and use `n_reps > 1` via `build_kw`) for stochastic models.

## Quick Reference

```python
import starsim as ss
import pandas as pd
import numpy as np

# 1. Calibration parameters
calib_pars = dict(
    beta=dict(low=0.01, high=0.30, guess=0.15, log=True),
    init_prev=dict(low=0.01, high=0.05, guess=0.02),
)

# 2. Build function -- modifies uninitialized sim
def build_sim(sim, calib_pars, **kwargs):
    sim.pars.diseases.pars.beta = ss.perday(calib_pars['beta']['value'])
    sim.pars.diseases.pars.init_prev = ss.bernoulli(calib_pars['init_prev']['value'])
    return sim

# 3. Component with observed data
component = ss.Normal(
    name='Prevalence',
    conform='prevalent',
    expected=pd.DataFrame({'x': [0.13, 0.16]},
        index=pd.Index([ss.date('2020-01-12'), ss.date('2020-01-25')], name='t')),
    extract_fn=lambda sim: pd.DataFrame({'x': sim.results.sir.prevalence},
        index=pd.Index(sim.results.timevec, name='t')),
)

# 4. Run calibration
calib = ss.Calibration(
    sim=make_sim(), calib_pars=calib_pars, build_fn=build_sim,
    components=[component], total_trials=100, n_workers=None,
)
calib.calibrate()

# 5. Inspect
calib.best_pars                              # Best parameters
calib.check_fit()                            # Compare guess vs. best
calib.plot()                                 # Likelihood plot
calib.plot(bootstrap=True)                   # Bootstrap plot
calib.plot_final()                           # Final fitted sims
calib.to_df(top_k=10)                        # Top 10 trials as DataFrame
calib.plot_optuna('plot_optimization_history')  # Optuna diagnostics
```
