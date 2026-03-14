---
name: starsim-dev-demographics
description: Use when adding births, deaths, pregnancy, or population dynamics to a Starsim simulation.
---

# Starsim Demographics

Demographics modules add births, deaths, pregnancy, and aging to a Starsim simulation. Without demographics the population is fixed; with demographics it grows, shrinks, and ages naturally over time. These modules are essential for modeling disease transmission over long time horizons, generational effects, and realistic population dynamics.

## Key classes

| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `ss.Births` | Crude birth rate (per person) | `birth_rate` -- scalar via `ss.peryear()` or DataFrame with `Year`/`CBR` columns |
| `ss.Deaths` | Background mortality (separate from disease deaths) | `death_rate` -- scalar via `ss.peryear()` or DataFrame; `rate_units` (default `1/1000`, set to `1` if data are raw rates) |
| `ss.Pregnancy` | Age-specific fertility with pregnancy modeling | `fertility_rate`, `rel_fertility`, `min_age`, `max_age`, `p_maternal_death`, `dur_breastfeed` |
| `ss.People` | Agent population | `n_agents`, `age_data` (DataFrame with `age`/`value` columns) |

## Patterns

### 1. Constant birth and death rates

The simplest approach: pass scalar rates via `ss.peryear()`. Rates are per 1000 people per year.

```python
import starsim as ss

demographics = [
    ss.Births(birth_rate=ss.peryear(20)),   # 20 births per 1000 people/year
    ss.Deaths(death_rate=ss.peryear(15)),   # 15 deaths per 1000 people/year
]
sim = ss.Sim(demographics=demographics, networks='random', diseases='sir')
sim.run()
sim.plot()
```

Equivalent shorthand -- pass rates directly in sim parameters:

```python
pars = dict(
    birth_rate = ss.peryear(20),
    death_rate = ss.peryear(15),
    networks   = 'random',
    diseases   = 'sir',
)
sim = ss.Sim(pars)
```

### 2. Default demographics with `demographics=True`

Use `demographics=True` to apply built-in default birth and death rates. This is the fastest way to get a growing/shrinking population.

```python
sim = ss.Sim(demographics=True, diseases='sis', networks='random')
sim.run()
sim.plot()
```

### 3. Time-varying birth rates from a DataFrame

Supply a DataFrame with `Year` and `CBR` (crude birth rate) columns. Starsim interpolates between years.

```python
import pandas as pd
import starsim as ss

birth_data = pd.DataFrame({
    'Year': [2000, 2005, 2010, 2015, 2020, 2025, 2030],
    'CBR':  [40,   35,   30,   31,   32,   30,   28],
})

births = ss.Births(birth_rate=birth_data)
deaths = ss.Deaths(death_rate=ss.peryear(8))

sim = ss.Sim(demographics=[births, deaths], diseases='sis', networks='random')
sim.run()
```

### 4. Age-specific fertility with `ss.Pregnancy`

For detailed modeling use `ss.Pregnancy` instead of `ss.Births`. It models age-specific fertility rates, pregnancy duration, maternal mortality, and mother-to-child transmission pathways. The `fertility_rate` parameter accepts a DataFrame with `Time`, `AgeGrp`, and `ASFR` columns.

```python
import pandas as pd
import starsim as ss

fertility_data = pd.DataFrame({
    'Time':   [2020]*7,
    'AgeGrp': [15, 20, 25, 30, 35, 40, 45],
    'ASFR':   [0.05, 0.15, 0.20, 0.15, 0.10, 0.05, 0.01],
})

pregnancy = ss.Pregnancy(
    fertility_rate            = fertility_data,
    rel_fertility             = 1000,                          # Data are per 1000 women
    p_maternal_death          = ss.bernoulli(0.001),           # 0.1% maternal mortality
    p_survive_maternal_death  = ss.bernoulli(0.98),            # 98% chance unborn survives if mother dies
    dur_breastfeed            = ss.lognorm_ex(mean=ss.years(0.5), std=ss.years(0.25)),
    min_age                   = 15,
    max_age                   = 50,
)

deaths = ss.Deaths(death_rate=ss.peryear(8))
sim = ss.Sim(demographics=[pregnancy, deaths], diseases='sis', networks='random')
sim.run()
```

### 5. Data-driven age-specific fertility from CSV

Real-world ASFR data files typically have `Time`, `AgeGrp`, and `ASFR` columns with rows for every age and year. Load them directly into `ss.Pregnancy`.

```python
import pandas as pd
import starsim as ss

fertility_rates = pd.read_csv('nigeria_asfr.csv')
# Expected columns: Time, AgeGrp, ASFR
# Example rows:
#   Time  AgeGrp  ASFR
#   1990  15      71.229
#   1990  16      111.213

pregnancy = ss.Pregnancy(fertility_rate=fertility_rates)
```

### 6. Data-driven death rates from CSV

Death rate files typically have `Time`, `Sex`, `AgeGrpStart`, and `mx` columns. Set `rate_units=1` when the data are raw rates (not per 1000).

```python
import pandas as pd
import starsim as ss

death_rates = pd.read_csv('nigeria_deaths.csv')
# Expected columns: Time, Sex, AgeGrpStart, mx
# Example rows:
#   Time  Sex     AgeGrpStart  mx
#   1990  Male    0            0.14221132
#   1990  Male    1            0.02790468

deaths = ss.Deaths(death_rate=death_rates, rate_units=1)
```

### 7. Realistic age distribution with `age_data`

Initialize agents with a realistic age pyramid by passing `age_data` to `ss.People`. The DataFrame should have `age` and `value` columns (value is population count per single-year age group, in thousands).

```python
import pandas as pd
import starsim as ss

age_data = pd.read_csv('nigeria_age.csv')
# Expected columns: age, value
# Example rows:
#   age  value
#   0    4245.106
#   1    3876.368

ppl = ss.People(n_agents=5_000, age_data=age_data)
sim = ss.Sim(people=ppl, demographics=True, networks='random', diseases='sir')
sim.run()
```

### 8. Scaling results to whole populations

Use `total_pop` to scale results from a small agent population to a real-world population size. Each agent effectively represents `total_pop / n_agents` people.

```python
import pandas as pd
import starsim as ss

age_data     = pd.read_csv('nigeria_age.csv')
nga_pop_1995 = 106_819_805

ppl = ss.People(n_agents=5_000, age_data=age_data)

fertility_rates = pd.read_csv('nigeria_asfr.csv')
death_rates     = pd.read_csv('nigeria_deaths.csv')

demographics = [
    ss.Pregnancy(fertility_rate=fertility_rates),
    ss.Deaths(death_rate=death_rates, rate_units=1),
]

sim = ss.Sim(
    total_pop    = nga_pop_1995,
    start        = 1995,
    people       = ppl,
    demographics = demographics,
    networks     = 'random',
    diseases     = 'sir',
)
sim.run()
```

### 9. Aging behavior

By default, agents age if and only if at least one demographics module is present. You can override this:

```python
# Demographics without aging
ss.Sim(demographics=True, use_aging=False)

# Aging without demographics (fixed population, but agents get older)
ss.Sim(use_aging=True)
```

### 10. Comparing simulations with and without demographics

```python
import starsim as ss

pars = dict(diseases='sis', networks='random', verbose=0)

sim1 = ss.Sim(label='No demographics', **pars)
sim2 = ss.Sim(label='With demographics', demographics=True, **pars)

msim = ss.parallel(sim1, sim2)
msim.plot(['n_alive', 'cum_deaths', 'sis_n_susceptible', 'sis_n_infected'])
```

### 11. Full Nigeria example

Putting it all together -- realistic demographics for Nigeria with validation against actual population data.

```python
import starsim as ss
import pandas as pd
import matplotlib.pyplot as plt

# Load data files
fertility_rates = pd.read_csv('nigeria_asfr.csv')
death_rates     = pd.read_csv('nigeria_deaths.csv')
age_data        = pd.read_csv('nigeria_age.csv')
nigeria_popsize = pd.read_csv('nigeria_popsize.csv')

n_agents     = 5_000
nga_pop_1995 = 106_819_805

# Build components
ppl          = ss.People(n_agents, age_data=age_data)
pregnancy    = ss.Pregnancy(fertility_rate=fertility_rates)
death        = ss.Deaths(death_rate=death_rates, rate_units=1)
demographics = [pregnancy, death]

# Run simulation
sim = ss.Sim(
    total_pop    = nga_pop_1995,
    start        = 1995,
    people       = ppl,
    demographics = demographics,
    networks     = 'random',
    diseases     = 'sir',
)
sim.run()

# Validate against real population data
data = nigeria_popsize[(nigeria_popsize.year >= 1995) & (nigeria_popsize.year <= 2030)]

fig, ax = plt.subplots(1, 1)
ax.scatter(data.year, data.n_alive, alpha=0.5, label='Data')
ax.plot(sim.t.yearvec, sim.results.n_alive, color='k', label='Model')
ax.legend()
ax.set_title('Nigeria Population: Model vs Data')
plt.show()
```

## Anti-patterns

### fertility_rate vs birth_rate

`fertility_rate` (used with `ss.Pregnancy`) is defined **per woman**. `birth_rate` (used with `ss.Births`) is defined **per person**. Mixing these up will give wildly incorrect population dynamics.

```python
# WRONG: using fertility_rate with ss.Births
births = ss.Births(birth_rate=fertility_data)  # fertility_data is per woman, birth_rate expects per person

# CORRECT: use ss.Pregnancy for fertility data
pregnancy = ss.Pregnancy(fertility_rate=fertility_data)

# CORRECT: use ss.Births for crude birth rates
births = ss.Births(birth_rate=birth_data)  # birth_data has Year/CBR columns, rate is per person
```

### rate_units mismatch

When loading death rates from data files, the `rate_units` parameter must match the scale of your data. The default is `1/1000` (rates are per 1000 people). If your data contain raw rates (e.g., `mx = 0.142`), you must set `rate_units=1`.

```python
# WRONG: data are raw rates but rate_units defaults to 1/1000
deaths = ss.Deaths(death_rate=death_rates)  # Rates will be 1000x too small

# CORRECT: set rate_units=1 for raw rate data
deaths = ss.Deaths(death_rate=death_rates, rate_units=1)
```

### Forgetting total_pop for scaling

Without `total_pop`, results reflect only the simulated agent count. If you are modeling a real country, always set `total_pop` so results scale correctly.

```python
# WRONG: results will show ~5000 people, not millions
sim = ss.Sim(people=ss.People(5_000, age_data=age_data), demographics=demographics)

# CORRECT: results scale to the real population
sim = ss.Sim(
    total_pop = 106_819_805,
    people    = ss.People(5_000, age_data=age_data),
    demographics = demographics,
)
```

### Using demographics=True when you need custom rates

`demographics=True` uses built-in default rates. If you need country-specific or time-varying rates, construct the modules explicitly.

```python
# This uses default rates, NOT your custom data
sim = ss.Sim(demographics=True)

# Do this instead for custom rates
sim = ss.Sim(demographics=[
    ss.Births(birth_rate=birth_data),
    ss.Deaths(death_rate=death_rates, rate_units=1),
])
```

### 12. Pregnancy loss and neonatal death classification

`ss.Pregnancy` classifies adverse birth outcomes automatically:

- **Background pregnancy loss**: Set `p_loss` to a non-zero per-timestep probability. Early losses are naturally more common because pregnancies spend more timesteps at early gestational ages.
- **Miscarriage vs stillbirth**: Prenatal deaths are classified by gestational age: `<loss_threshold` (default 20 weeks) = miscarriage, `>=loss_threshold` = stillbirth. Both background losses and disease-specific losses (via `request_death`) are classified.
- **Preterm birth**: Births at `<preterm_threshold` (default 37 weeks) are flagged as preterm; `<very_preterm_threshold` (default 32 weeks) as very preterm.
- **Neonatal death**: Deaths of agents aged 0-28 days are passively detected and classified as neonatal deaths. Any mechanism that kills a newborn (disease, congenital outcomes, background mortality) is captured.

```python
import starsim as ss

pregnancy = ss.Pregnancy(
    fertility_rate      = ss.freqperyear(30),
    p_loss              = ss.bernoulli(p=0.005),  # 0.5% per-timestep loss probability
    loss_threshold      = ss.weeks(20),           # Default: 20 weeks
    preterm_threshold   = ss.weeks(37),           # Default: 37 weeks
)

sim = ss.Sim(demographics=[pregnancy, ss.Deaths()], networks='random')
sim.run()

# Results
print(sim.results.pregnancy.miscarriages.sum())
print(sim.results.pregnancy.stillbirths.sum())
print(sim.results.pregnancy.nnds.sum())
print(sim.results.pregnancy.n_preterm.sum())
print(sim.results.pregnancy.preterm_rate)
```

States stored on newborns: `preterm`, `very_preterm`, `neonatal_death`. States stored on mothers: `n_miscarriages`, `n_stillbirths`.

### 13. FetalHealth module

`ss.FetalHealth` tracks gestational-age-dependent birth weight, growth restriction, and timing shifts. Pass as a custom module:

```python
sim = ss.Sim(
    demographics=ss.Pregnancy(),
    custom=ss.FetalHealth(),
    networks=ss.PrenatalNet(),
)
```

Connectors and interventions interact with fetal health via callback methods:
- `fh.apply_timing_shift(uids, weeks)` — bring delivery forward (preterm)
- `fh.apply_growth_restriction(uids, penalty)` — reduce birth weight
- `fh.reverse_timing_shift(uids, fraction)` — partially undo timing shift
- `fh.reverse_growth_restriction(uids, amount)` — partially undo growth restriction

See `starsim_examples/mnch/` for complete connector and intervention examples.

## Quick reference

| Task | Code |
|------|------|
| Constant birth rate | `ss.Births(birth_rate=ss.peryear(20))` |
| Constant death rate | `ss.Deaths(death_rate=ss.peryear(15))` |
| Default demographics | `ss.Sim(demographics=True)` |
| Time-varying births | `ss.Births(birth_rate=df)` where `df` has `Year`/`CBR` columns |
| Age-specific fertility | `ss.Pregnancy(fertility_rate=df)` where `df` has `Time`/`AgeGrp`/`ASFR` columns |
| Data-driven deaths | `ss.Deaths(death_rate=df, rate_units=1)` where `df` has `Time`/`Sex`/`AgeGrpStart`/`mx` columns |
| Realistic age pyramid | `ss.People(n_agents=5000, age_data=df)` where `df` has `age`/`value` columns |
| Population scaling | `ss.Sim(total_pop=200e6, n_agents=50e3)` |
| Enable aging only | `ss.Sim(use_aging=True)` |
| Demographics without aging | `ss.Sim(demographics=True, use_aging=False)` |
| Maternal mortality | `ss.Pregnancy(p_maternal_death=ss.bernoulli(0.001))` |
| Breastfeeding duration | `ss.Pregnancy(dur_breastfeed=ss.lognorm_ex(mean=ss.years(0.5), std=ss.years(0.25)))` |
| Fertility scaling factor | `ss.Pregnancy(rel_fertility=1000)` -- set to 1000 if data are per 1000 women |
| Background pregnancy loss | `ss.Pregnancy(p_loss=ss.bernoulli(p=0.005))` |
| Loss classification threshold | `ss.Pregnancy(loss_threshold=ss.weeks(20))` |
| Preterm threshold | `ss.Pregnancy(preterm_threshold=ss.weeks(37))` |
| Fetal health tracking | `ss.Sim(custom=ss.FetalHealth(), networks=ss.PrenatalNet())` |
