---
name: starsim-dev-interventions
description: Use when adding interventions to a Starsim simulation — including vaccination, screening, treatment, and custom interventions.
---

# Starsim Interventions Reference

Starsim separates **products** (the vaccine, diagnostic, or treatment itself) from **interventions** (the delivery mechanism that administers products to people). Products define *what* is given; interventions define *who, when, and how often*. This guide covers all built-in intervention patterns plus how to write custom ones.

## Key classes

### Hierarchy

| Class | Purpose | Key features |
|-------|---------|--------------|
| `ss.Intervention` | Base class for all interventions | Eligibility checking, product integration, `step()` method |
| `ss.RoutineDelivery` | Continuous delivery over time | Interpolated probabilities, annual/timestep rates |
| `ss.CampaignDelivery` | One-off or discrete campaigns | Specific years, optional interpolation |
| `ss.BaseTest` | Base for screening/triage | Product administration, outcome tracking |
| `ss.BaseScreening` | Screening programs | Population-level eligibility checking |
| `ss.BaseTriage` | Triage/follow-up testing | Targeted eligibility (e.g., screen positives) |
| `ss.BaseTreatment` | Treatment interventions | Queue management, eligibility validation |
| `ss.BaseVaccination` | Vaccination programs | Dose tracking, vaccination state management |

### Ready-to-use interventions

| Class | Delivery | Use case |
|-------|----------|----------|
| `ss.routine_vx` | Continuous | Routine immunization programs |
| `ss.campaign_vx` | Discrete | Mass vaccination campaigns |
| `ss.routine_screening` | Continuous | Regular screening programs (e.g., annual STI screening) |
| `ss.campaign_screening` | Discrete | Mass screening events (e.g., outbreak response) |
| `ss.routine_triage` | Continuous | Follow-up testing for positives |
| `ss.campaign_triage` | Discrete | Campaign-based confirmatory testing |
| `ss.treat_num` | Per-timestep | Resource-constrained treatment (fixed capacity) |

## Patterns

### 1. Vaccine products

Use `ss.simple_vx()` for a generic vaccine with a given efficacy:

```python
import starsim as ss

# Create a vaccine product with 50% efficacy
my_vaccine = ss.simple_vx(efficacy=0.5)
```

The `efficacy` parameter sets the probability that vaccination successfully protects the recipient.

### 2. Routine vaccination

`ss.routine_vx` delivers a vaccine continuously starting from a given year, with a per-timestep probability of coverage:

```python
import starsim as ss

my_vaccine = ss.simple_vx(efficacy=0.5)

my_intervention = ss.routine_vx(
    start_year=2015,     # Begin vaccination in 2015
    prob=0.2,            # 20% coverage per timestep
    product=my_vaccine,  # The vaccine product
)

sim = ss.Sim(
    n_agents=5_000,
    networks='random',
    diseases='sir',
    interventions=my_intervention,
)
sim.run()
```

### 3. Campaign vaccination

`ss.campaign_vx` delivers a vaccine in specific years rather than continuously:

```python
import starsim as ss

vx = ss.simple_vx(efficacy=0.8)

campaign = ss.campaign_vx(
    product=vx,
    years=[2015, 2020],  # Vaccinate in these specific years
    prob=0.5,            # 50% coverage in each campaign
)

sim = ss.Sim(
    n_agents=5_000,
    networks='random',
    diseases='sir',
    interventions=campaign,
)
sim.run()
```

### 4. Diagnostic products

Diagnostics use `ss.Dx()` with a DataFrame that maps disease states to test result probabilities:

```python
import sciris as sc
import starsim as ss

dx_data = sc.dataframe(
    columns=['disease', 'state', 'result', 'probability'],
    data=[
        ['sis', 'susceptible', 'positive', 0.01],  # 1% false positive
        ['sis', 'susceptible', 'negative', 0.99],
        ['sis', 'infected',    'positive', 0.95],   # 95% sensitivity
        ['sis', 'infected',    'negative', 0.05],
    ]
)

screening = ss.routine_screening(
    product=ss.Dx(df=dx_data),
    prob=0.9,
    start_year=2010,
)
```

The DataFrame **must** have exactly four columns: `disease`, `state`, `result`, `probability`. Each disease state needs rows that sum to 1.0 across all result values for that state.

### 5. Routine screening

```python
import sciris as sc
import starsim as ss

dx_data = sc.dataframe(
    columns=['disease', 'state', 'result', 'probability'],
    data=[
        ['sis', 'susceptible', 'positive', 0.01],
        ['sis', 'susceptible', 'negative', 0.99],
        ['sis', 'infected',    'positive', 0.95],
        ['sis', 'infected',    'negative', 0.05],
    ]
)

screening = ss.routine_screening(
    product=ss.Dx(df=dx_data),
    prob=0.9,           # 90% of eligible people screened per timestep
    start_year=2010,
)
```

### 6. Campaign screening

Same as routine screening but delivered in specific years:

```python
campaign_screen = ss.campaign_screening(
    product=ss.Dx(df=dx_data),
    years=[2012, 2016],
    prob=0.7,
)
```

### 7. Treatment

`ss.treat_num` treats a fixed number of people per timestep:

```python
treatment = ss.treat_num(num_treated=100)  # Treat up to 100 people per timestep
```

By default it treats as many people as need treatment, but you can set a maximum to model resource constraints.

### 8. Eligibility functions

Interventions accept an `eligibility` parameter -- a callable that receives the sim and returns UIDs of eligible agents:

```python
import starsim as ss

# Simple lambda: adults only
eligible_adults = lambda sim: (sim.people.age >= 18).uids

# Complex function: combining multiple conditions
def high_risk_eligibility(sim):
    adults = sim.people.age >= 18
    sexually_active = sim.networks.mfnet.participant
    return (adults & sexually_active).uids

# Using intervention outcomes for triage
screen_positives = lambda sim: sim.interventions.screening.outcomes['positive']

# Pass to any intervention
vx = ss.simple_vx(efficacy=0.9)
vaccination = ss.routine_vx(
    product=vx,
    prob=0.8,
    start_year=2010,
    eligibility=eligible_adults,
)
```

### 9. Multiple interventions with unique names

When adding multiple interventions of the same type, give each a unique `name`:

```python
import starsim as ss

vx = ss.simple_vx(efficacy=0.8)

intv_low  = ss.routine_vx(name='intv_low',  start_year=2010, prob=0.2, product=vx)
intv_high = ss.routine_vx(name='intv_high', start_year=2020, prob=0.6, product=vx)

pars = dict(n_agents=5000, networks='random', diseases='sis', verbose=0)
s0 = ss.Sim(pars, label='Baseline')
s1 = ss.Sim(pars, label='Low coverage', interventions=intv_low)
s2 = ss.Sim(pars, label='Low + high coverage', interventions=[intv_low, intv_high])

msim = ss.parallel(s0, s1, s2)
msim.plot('sis_new_infections')
```

### 10. Combining vaccination and screening

You can mix different intervention types in a single simulation:

```python
import sciris as sc
import starsim as ss

pars = dict(
    n_agents=5_000,
    start=2000,
    stop=2020,
    diseases='sis',
    networks='random',
)

# Vaccine
my_vaccine = ss.simple_vx(efficacy=0.9)
vaccination = ss.routine_vx(product=my_vaccine, prob=0.8, start_year=2005)

# Diagnostic + screening
dx_data = sc.dataframe(
    columns=['disease', 'state', 'result', 'probability'],
    data=[
        ['sis', 'susceptible', 'positive', 0.01],
        ['sis', 'susceptible', 'negative', 0.99],
        ['sis', 'infected',    'positive', 0.95],
        ['sis', 'infected',    'negative', 0.05],
    ]
)
screening = ss.routine_screening(product=ss.Dx(df=dx_data), prob=0.9, start_year=2010)

sim = ss.Sim(pars, interventions=[screening, vaccination])
sim.run()
sim.plot()
```

### 11. Custom intervention as a function

The simplest custom intervention is a plain function that takes `sim` as its first argument. Starsim calls it every timestep, so you must handle timing yourself:

```python
import starsim as ss

def simple_sis_vaccine(sim, start=2030, eff=0.9):
    if sim.now == start:
        sim.diseases.sis.rel_trans[:] *= 1 - eff
    return

pars = dict(
    start=2000,
    stop=2050,
    diseases='sis',
    networks='random',
    interventions=simple_sis_vaccine,
)

sim = ss.Sim(pars)
sim.run()
sim.plot()
```

Key points for function-based interventions:
- The function is called **every timestep**, so use `if sim.now == start:` or similar guards.
- Access disease attributes via `sim.diseases.<name>` (e.g., `sim.diseases.sis.rel_trans`).
- Access people via `sim.people`.
- The function can accept extra keyword arguments with default values.

### 12. Custom intervention as a class

For more complex behavior, subclass `ss.Intervention` and implement `step()`:

```python
import starsim as ss

class MyVaccine(ss.Intervention):
    def __init__(self, start_year=2020, efficacy=0.9, **kwargs):
        super().__init__(**kwargs)
        self.start_year = start_year
        self.efficacy = efficacy

    def step(self):
        if self.sim.now == self.start_year:
            eligible = (self.sim.people.age >= 5).uids
            self.sim.diseases.sir.rel_trans[eligible] *= 1 - self.efficacy

sim = ss.Sim(
    diseases='sir',
    networks='random',
    interventions=MyVaccine(start_year=2020, efficacy=0.9),
)
sim.run()
```

### 13. Comparing baseline vs. intervention with ss.parallel()

The standard workflow for measuring intervention impact:

```python
import starsim as ss
import matplotlib.pyplot as plt

pars = dict(
    n_agents=5_000,
    birth_rate=ss.peryear(20),
    death_rate=15,
    networks=dict(type='randomnet', n_contacts=4),
    diseases=dict(type='sir', dur_inf=10, beta=0.1),
)

my_vaccine = ss.simple_vx(efficacy=0.5)
my_intervention = ss.routine_vx(start_year=2015, prob=0.2, product=my_vaccine)

sim_base = ss.Sim(pars=pars)
sim_intv = ss.Sim(pars=pars, interventions=my_intervention)

# Run both in parallel
msim = ss.parallel(sim_base, sim_intv)

# Plot results
res_base = msim.sims[0].results
res_intv = msim.sims[1].results

plt.figure()
plt.plot(res_base.timevec, res_base.sir.prevalence, label='Baseline')
plt.plot(res_intv.timevec, res_intv.sir.prevalence, label='Vaccination')
plt.axvline(x=ss.date(2015), color='k', ls='--')
plt.title('Prevalence')
plt.legend()
plt.show()
```

## Anti-patterns

### Coverage `prob` is per-timestep, not cumulative

The `prob` parameter in `ss.routine_vx` and `ss.routine_screening` is applied **every timestep**, not once over the simulation. A `prob=0.2` with weekly timesteps means 20% of eligible people are vaccinated *each week*, which compounds rapidly. To model a target annual coverage, account for the timestep frequency:

```python
# If timestep is 1 week (~52 per year) and you want ~80% annual coverage:
# prob_per_step = 1 - (1 - annual_target) ** (1 / steps_per_year)
import numpy as np
annual_target = 0.8
steps_per_year = 52
prob_per_step = 1 - (1 - annual_target) ** (1 / steps_per_year)
```

### Multiple same-type interventions need unique names

If you add two `ss.routine_vx` instances without distinct `name` values, they will collide and one will overwrite the other:

```python
# WRONG -- names will collide
vx1 = ss.routine_vx(start_year=2010, prob=0.2, product=vx)
vx2 = ss.routine_vx(start_year=2020, prob=0.6, product=vx)

# CORRECT -- give unique names
vx1 = ss.routine_vx(name='vx_early', start_year=2010, prob=0.2, product=vx)
vx2 = ss.routine_vx(name='vx_late',  start_year=2020, prob=0.6, product=vx)
```

### Custom interventions must handle timing

Function-based and class-based custom interventions are called every timestep. Forgetting to guard on `sim.now` means the intervention fires repeatedly:

```python
# WRONG -- reduces transmission EVERY timestep
def bad_vaccine(sim, eff=0.9):
    sim.diseases.sis.rel_trans[:] *= 1 - eff

# CORRECT -- only fires once at the target year
def good_vaccine(sim, start=2030, eff=0.9):
    if sim.now == start:
        sim.diseases.sis.rel_trans[:] *= 1 - eff
```

### Diagnostic DataFrame rows must sum to 1.0

For each combination of `disease` and `state`, the `probability` column must sum to 1.0 across all `result` values. Failing to do so produces silent errors in screening outcomes.

## Quick reference

```text
PRODUCTS
  ss.simple_vx(efficacy=float)                  Simple vaccine product
  ss.Dx(df=dataframe)                           Diagnostic product (requires DataFrame)

VACCINATION
  ss.routine_vx(product, prob, start_year)       Routine delivery
  ss.campaign_vx(product, years, prob)           Campaign delivery

SCREENING
  ss.routine_screening(product, prob, start_year)  Routine screening
  ss.campaign_screening(product, years, prob)      Campaign screening

TRIAGE
  ss.routine_triage(product, prob, start_year)   Routine follow-up testing
  ss.campaign_triage(product, years, prob)        Campaign follow-up testing

TREATMENT
  ss.treat_num(num_treated=int)                  Fixed-capacity treatment

COMMON PARAMETERS
  product       Product object (vaccine, diagnostic, etc.)
  prob          Per-timestep probability of delivery (float, 0-1)
  start_year    Year to begin routine delivery (int or float)
  years         List of years for campaign delivery (list)
  name          Unique identifier (required when using multiple same-type interventions)
  eligibility   Callable: fn(sim) -> UIDs of eligible agents

CUSTOM INTERVENTIONS
  Function:     def my_intv(sim, **kwargs): ...     (passed as interventions=my_intv)
  Class:        class MyIntv(ss.Intervention): ...  (implement step() method)

COMPARISON
  ss.parallel(sim_base, sim_intv)               Run sims in parallel for comparison
```
