---
name: stisim-modeling
description: Use when the user is building, configuring, or debugging an STIsim simulation — including STI diseases (HIV, syphilis, chlamydia, gonorrhea, trichomoniasis, BV), structured sexual networks, risk groups, STI interventions, connectors, or calibration.
---

# STIsim Modeling

You are helping the user build agent-based STI transmission models with [STIsim](https://github.com/starsimhub/stisim), a framework for simulating sexually transmitted infections built on top of [Starsim](https://github.com/starsimhub/starsim). These instructions were written for STIsim version 1.5.0 on 2026-02-19.

## When to activate

- User asks to create or modify an `sti.Sim`, `sti.HIV`, `sti.Syphilis`, `sti.StructuredSexual`, or related class
- User asks about STI-specific parameters, risk groups, sexual networks, or disease interactions
- User is modeling HIV, syphilis, chlamydia, gonorrhea, trichomoniasis, or bacterial vaginosis
- User is working with STI interventions (testing, ART, VMMC, PrEP, partner notification)
- User is debugging an STIsim model run or comparing intervention scenarios

## Key concepts

### Sim

`sti.Sim` subclasses `ss.Sim` and accepts `diseases`, `networks`, `demographics`, `interventions`, `analyzers`, and `connectors`. It also accepts `disease_pars` and `network_pars` dicts for parameter overrides. `sti.MultiSim` runs multiple simulations for uncertainty quantification.

### Diseases

STIsim provides 7 disease modules in two families:

**SEIS-based** (Susceptible-Exposed-Infected-Susceptible, recoverable):

| Disease | Class | Key features |
|---------|-------|-------------|
| Chlamydia | `sti.Chlamydia` | Also `sti.ChlamydiaBL` for bacterial load dynamics |
| Gonorrhea | `sti.Gonorrhea` | Drug resistance tracking |
| Trichomoniasis | `sti.Trichomoniasis` | Long asymptomatic persistence in women |

SEIS diseases share: symptom probability (`p_symp`), care-seeking delay (`dur_symp2care`), PID (pelvic inflammatory disease) modeling.

**BaseSTI-based** (complex natural history):

| Disease | Class | Key features |
|---------|-------|-------------|
| HIV | `sti.HIV` | CD4 dynamics, acute/latent/falling stages, ART |
| Syphilis | `sti.Syphilis` | Primary/secondary/latent/tertiary stages |
| Bacterial Vaginosis | `sti.BV` | Microbiome model; also `sti.SimpleBV` |
| GUD (placeholder) | `sti.GUDPlaceholder` | Used in connectors for cofactor effects |

Each disease has a `Pars` class for its parameters. Common parameters include `beta_m2f` (male-to-female transmission), `init_prev` (initial prevalence), and `eff_condom` (condom effectiveness).

### Networks

**`sti.StructuredSexual`** is the primary network, modeling heterosexual partnerships with:
- **Risk groups**: 0 (low), 1 (medium), 2 (high) — controlled by `prop_f0`, `prop_m0`, `prop_f2`, `prop_m2`
- **Concurrency**: concurrent partners per risk group (`f0_conc`, `m1_conc`, etc.)
- **Sex work**: `fsw_shares`, `client_shares`, `sw_seeking_rate`
- **Relationship dynamics**: `p_pair_form`, `p_matched_stable`, duration distributions
- **Condom use**: time-varying by partnership type (`condom_data`)
- **Coital acts**: `acts` (per year, lognormal distribution)

Other networks: `sti.AgeMatchedMSM()` (men who have sex with men), `ss.MaternalNet()` (mother-to-child).

### Interventions

**HIV-specific:**
- `sti.HIVTest(years, test_prob_data)` — HIV testing with time-varying coverage
- `sti.ART(coverage_data)` — antiretroviral therapy
- `sti.VMMC(coverage_data)` — voluntary medical male circumcision
- `sti.Prep(coverage_data)` — pre-exposure prophylaxis

**Generic STI:**
- `sti.STITest()` — general STI testing
- `sti.STITreatment()` — treatment products
- `sti.SymptomaticTesting()` — symptom-driven testing
- `sti.PartnerNotification()` — contact tracing

### Connectors

Link diseases together for coinfection effects:
- `sti.hiv_sti(hiv_module, sti_module)` — HIV-STI cofactor interactions
- `sti.gud_syph(gud_module, syphilis_module)` — GUD-syphilis interactions

### Demographics

Use location strings (e.g. `'zimbabwe'`) to load real demographic data, or pass Starsim modules directly (`ss.Pregnancy`, `ss.Deaths`). Control with `total_pop` for population scaling.

### Analyzers

- `sti.coinfection_stats(disease1, disease2)` — coinfection prevalence
- `sti.sw_stats()` — sex work statistics
- `sti.partner_age_diff()` — partnership age gaps
- `sti.RelationshipDurations()` — relationship length tracking

## Approach

1. Use the starsim/sciris MCP tools (if available) to look up current API signatures and examples.
2. If MCP tools are unavailable, use Context7 (`/starsimhub/stisim`) for up-to-date docs.
3. Start simple — get a minimal working simulation, then layer in complexity.
4. Use `stisim_examples` factory functions for pre-configured location-based sims.
5. Prefer STIsim's built-in modules over custom implementations where possible.

## Examples

### Minimal HIV simulation

```python
import stisim as sti

sim = sti.Sim(
    diseases='hiv',
    n_agents=1000,
    dur=20,
)
sim.run()
sim.plot()
```

### Pre-configured location sim (recommended starting point)

```python
import stisim_examples as stx

sim = stx.HIVSim(location='zimbabwe')
sim.run()
sim.plot()

# Or multi-disease:
sim = stx.Sim(demographics='zimbabwe', diseases=['hiv', 'syphilis'])
sim.run()
```

### HIV with interventions and custom network

```python
import stisim as sti
import numpy as np

hiv = sti.HIV(beta_m2f=0.05, init_prev=0.1)

network = sti.StructuredSexual(
    prop_f0=0.85,
    prop_m0=0.80,
    prop_f2=0.01,
    prop_m2=0.02,
    m1_conc=0.2,
    f1_conc=0.01,
)

sim = sti.Sim(
    diseases=hiv,
    networks=network,
    demographics='zimbabwe',
    interventions=[
        sti.HIVTest(years=np.arange(2000, 2041), test_prob_data=0.3),
        sti.ART(),
        sti.VMMC(),
    ],
    n_agents=5000,
    start=1990,
    stop=2030,
)
sim.run()
sim.plot()
```

### Multi-disease with connectors

```python
import stisim as sti

hiv = sti.HIV(init_prev=0.1)
syphilis = sti.Syphilis(init_prev=0.05)

sim = sti.Sim(
    diseases=[hiv, syphilis],
    connectors=sti.hiv_sti(hiv, syphilis),
    demographics='zimbabwe',
    n_agents=5000,
    dur=30,
)
sim.run()
```

### MultiSim for uncertainty quantification

```python
import stisim as sti

base = sti.Sim(diseases='hiv', demographics='zimbabwe', n_agents=5000, dur=30)
msim = sti.MultiSim(sim=base, n_runs=10)
msim.run()
msim.plot()  # Plots median with IQR
```

### Parameter overrides via dicts

```python
import stisim as sti

sim = sti.Sim(
    diseases=['hiv', 'syphilis'],
    disease_pars={
        'hiv': {'beta_m2f': 0.05, 'init_prev': 0.1},
        'syphilis': {'init_prev': 0.05},
    },
    network_pars={
        'structuredsexual': {'prop_f0': 0.85, 'acts': 80},
    },
    demographics='zimbabwe',
    n_agents=5000,
    dur=30,
)
sim.run()
```
