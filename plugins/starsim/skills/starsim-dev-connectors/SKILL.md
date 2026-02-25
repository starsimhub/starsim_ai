---
name: starsim-dev-connectors
description: Use when modeling interactions between multiple diseases in Starsim — including modifying susceptibility, transmissibility, or disease progression based on co-infection.
---

# Connectors: Modeling Disease-Disease Interactions

Connectors enable interactions between disease modules in a multi-disease Starsim simulation. They modify transmission parameters, susceptibility, or agent states based on co-infection status. Use connectors when one disease should affect the transmission or progression of another -- for example, HIV increasing susceptibility to syphilis, or syphilis increasing HIV transmissibility.

## Key Classes

| Class | Purpose |
|-------|---------|
| `ss.Connector` | Base class for all connectors. Subclass it and implement `step()` to define interaction logic |
| `ss.Sim(..., connectors=)` | Pass one or more connectors via the `connectors` keyword argument. Accepts a single connector or a list |

## Execution Timing

Connectors run **after** Demographics and `Disease.step_state()`, but **before** Networks, Interventions, and disease transmission updates. This placement is critical: because disease states (infection status, CD4 counts, etc.) have already been updated for the current timestep, connectors can read the latest disease states and then modify `rel_sus` and `rel_trans` before transmission is calculated. The full per-timestep execution order is:

```
Demographics -> Disease.step_state() -> ** Connectors ** -> Networks -> Interventions -> Transmission
```

Because connectors execute before transmission, any changes they make to `rel_sus` or `rel_trans` will take effect in the same timestep. This is why the reset-then-modify pattern (described below) works correctly -- you reset to baseline, apply current co-infection modifiers, and transmission uses those values immediately.

## Patterns

### Subclass ss.Connector and Implement step()

The minimal connector subclasses `ss.Connector` and implements a `step()` method. The `step()` method is called once per simulation timestep and receives no arguments -- all state is accessed through `self.sim`. Inside `step()`, access diseases via `self.sim.diseases.<name>` and modify their `rel_sus` or `rel_trans` arrays to alter transmission dynamics.

```python
import starsim as ss

class SIS_HIV(ss.Connector):
    """People with SIS infection are protected from HIV."""

    def step(self):
        hiv = self.sim.diseases.hiv
        sis = self.sim.diseases.sis
        sis_pos = (sis.infected).uids
        sis_neg = (sis.susceptible).uids

        # Reset to baseline then apply modifications
        hiv.rel_sus[sis_neg] = 1.0
        hiv.rel_sus[sis_pos] = 0  # SIS-infected cannot acquire HIV
```

Pass the connector to the sim via the `connectors` keyword:

```python
sim = ss.Sim(
    diseases=[hiv, sis],
    networks=[mf, 'random'],
    connectors=SIS_HIV(),
    verbose=0,
)
```

### define_pars() and update_pars() for Configurable Connectors

For connectors with tunable interaction strengths, use `define_pars()` in `__init__()` to declare named parameters with default values, and `update_pars()` to accept keyword overrides from the caller. Parameters are then accessed via `self.pars.<name>` inside `step()`. This pattern makes connectors reusable and calibratable -- you can sweep over parameter values or override them per-scenario without modifying the class itself.

```python
class HIV_Syphilis(ss.Connector):
    def __init__(self, **kwargs):
        super().__init__()
        self.define_pars(
            label='HIV-Syphilis',
            rel_sus_syph_hiv=2,      # HIV+ are 2x more susceptible to syphilis
            rel_sus_syph_aids=5,     # AIDS patients are 5x more susceptible
            rel_trans_syph_hiv=1.5,  # HIV+ are 1.5x more likely to transmit syphilis
            rel_trans_syph_aids=3,   # AIDS patients are 3x more likely to transmit
            rel_sus_hiv_syph=2.7,    # Syphilis+ are 2.7x more susceptible to HIV
            rel_trans_hiv_syph=2.7,  # Syphilis+ are 2.7x more likely to transmit HIV
        )
        self.update_pars(**kwargs)
```

This allows users to override defaults at instantiation:

```python
connector = HIV_Syphilis(rel_sus_syph_hiv=3, rel_sus_hiv_syph=4)
```

### Reset Parameters to Baseline, Then Apply Modifications

This is the single most important pattern for connectors. Always reset `rel_sus` and `rel_trans` to baseline (1.0) at the start of `step()`, then apply modifications. Because `step()` runs every timestep, failing to reset means that agents who recovered from a co-infection will retain stale modifier values from previous timesteps. The slice assignment `[:] = 1.0` efficiently resets the entire array for all agents.

```python
def step(self):
    diseases = self.sim.diseases
    syph = diseases.syphilis
    hiv = diseases.hiv

    # Reset to baseline FIRST
    syph.rel_sus[:] = 1.0
    syph.rel_trans[:] = 1.0
    hiv.rel_sus[:] = 1.0
    hiv.rel_trans[:] = 1.0

    # Then apply modifications...
```

### Modify rel_sus and rel_trans on Disease Objects

The two primary properties connectors modify are:

- `disease.rel_sus` -- relative susceptibility. A multiplier on the probability that an agent *acquires* the disease. A value of 2.0 means twice as likely to be infected; 0.0 means fully protected.
- `disease.rel_trans` -- relative transmissibility. A multiplier on the probability that an infected agent *transmits* the disease. A value of 1.5 means 50% more likely to transmit.

Both are NumPy arrays with one entry per agent, indexed by agent UID. You can set values using UID arrays, boolean state arrays, or NumPy boolean conditions. The default value for both is 1.0 (no modification).

```python
# People with syphilis are more susceptible to HIV
hiv.rel_sus[syph.active] = self.pars.rel_sus_hiv_syph

# People with syphilis transmit HIV more easily
hiv.rel_trans[syph.active] = self.pars.rel_trans_hiv_syph
```

### Access Disease States

Each disease module exposes boolean and numeric state arrays that connectors can read. Access them through `self.sim.diseases.<name>` for the disease object, or `self.sim.people.<name>` for agent-level state arrays tied to that disease. Boolean state arrays (like `infected`, `susceptible`, `active`) can be used directly as indices into other arrays. Numeric arrays (like `cd4`) support standard NumPy comparison operators for conditional logic.

```python
# Boolean state arrays (can be used for indexing)
sis.infected         # Currently infected with SIS
sis.susceptible      # Currently susceptible to SIS
syph.active          # Active syphilis infection

# Numeric state arrays
cd4 = self.sim.people.hiv.cd4  # CD4 count from HIV module

# Get UIDs from boolean arrays
sis_pos = (sis.infected).uids
```

### HIV-Syphilis Bidirectional Example with CD4-Dependent Effects

This complete pattern shows bidirectional effects that vary by disease progression stage (CD4 count). HIV increases susceptibility and transmissibility of syphilis, with stronger effects at lower CD4 counts (AIDS stage). Conversely, active syphilis increases both susceptibility to and transmissibility of HIV. Note the ordering: set `cd4 < 500` first, then `cd4 < 200` to override with the stronger AIDS-stage effect for the sickest agents.

```python
class HIV_Syphilis(ss.Connector):
    def __init__(self, **kwargs):
        super().__init__()
        self.define_pars(
            label='HIV-Syphilis',
            rel_sus_syph_hiv=2,
            rel_sus_syph_aids=5,
            rel_trans_syph_hiv=1.5,
            rel_trans_syph_aids=3,
            rel_sus_hiv_syph=2.7,
            rel_trans_hiv_syph=2.7,
        )
        self.update_pars(**kwargs)

    def step(self):
        diseases = self.sim.diseases
        syph = diseases.syphilis
        hiv = diseases.hiv
        cd4 = self.sim.people.hiv.cd4

        # Reset to baseline
        syph.rel_sus[:] = 1.0
        syph.rel_trans[:] = 1.0
        hiv.rel_sus[:] = 1.0
        hiv.rel_trans[:] = 1.0

        # HIV -> syphilis effects (CD4-dependent)
        syph.rel_sus[cd4 < 500] = self.pars.rel_sus_syph_hiv
        syph.rel_sus[cd4 < 200] = self.pars.rel_sus_syph_aids
        syph.rel_trans[cd4 < 500] = self.pars.rel_trans_syph_hiv
        syph.rel_trans[cd4 < 200] = self.pars.rel_trans_syph_aids

        # Syphilis -> HIV effects
        hiv.rel_sus[syph.active] = self.pars.rel_sus_hiv_syph
        hiv.rel_trans[syph.active] = self.pars.rel_trans_hiv_syph
```

Usage:

```python
import starsim_examples as sse

hiv = sse.HIV(beta={'mf': [0.0008, 0.0004]}, init_prev=0.2)
syph = sse.Syphilis(beta={'mf': [0.1, 0.05]}, init_prev=0.05)
mf = ss.MFNet()

sim = ss.Sim(
    diseases=[hiv, syph],
    networks=mf,
    connectors=HIV_Syphilis(),
    n_agents=2000,
)
sim.run()
```

### Connectors with Interventions: Treatment That Resets Co-Infection Effects

When an intervention cures a disease, it should also reset the co-infection effects that the connector applied. This is important because interventions run after connectors in the timestep order -- so if the connector has already set `rel_sus` and `rel_trans` based on co-infection status, and then the intervention cures the co-infection, the modifier values would be stale for the rest of that timestep. The intervention should explicitly reset `rel_sus` and `rel_trans` for treated agents. On subsequent timesteps, the connector's reset-then-modify pattern will handle things correctly since the agents are no longer co-infected.

```python
class Penicillin(ss.Intervention):
    """Syphilis treatment that also resets HIV co-infection effects."""

    def __init__(self, year=2020, prob=0.8):
        super().__init__()
        self.prob = prob
        self.year = ss.date(year)

    def step(self):
        sim = self.sim
        if sim.now >= self.year:
            syphilis = sim.diseases.syphilis
            eligible_ids = syphilis.infected.uids
            n_eligible = len(eligible_ids)

            if n_eligible > 0:
                is_treated = np.random.rand(n_eligible) < self.prob
                treat_ids = eligible_ids[is_treated]

                # Cure syphilis
                syphilis.infected[treat_ids] = False
                syphilis.susceptible[treat_ids] = True

                # Reset HIV parameters (remove co-infection effects)
                sim.diseases.hiv.rel_sus[treat_ids] = 1.0
                sim.diseases.hiv.rel_trans[treat_ids] = 1.0
```

Combine with the connector:

```python
sim = ss.Sim(
    diseases=[hiv, syph],
    networks=mf,
    connectors=HIV_Syphilis(),
    interventions=Penicillin(year=2020, prob=0.8),
    n_agents=2000,
)
```

### Comparing Simulations With and Without Connectors

A common workflow is to run one simulation without a connector and one with it, then compare results. Use `ss.parallel()` to run both at the same time. Labeling each sim makes the comparison plots easier to interpret.

```python
s1 = ss.Sim(label='Without connector', diseases=[hiv, syph], networks=mf)
s2 = ss.Sim(label='With connector', diseases=[hiv, syph], networks=mf,
            connectors=HIV_Syphilis())
msim = ss.parallel(s1, s2)
msim.plot()
```

## Anti-Patterns

**Must reset parameters to baseline each step().** If you only set `rel_sus` for currently infected agents without resetting first, values accumulate or persist for agents who have recovered. An agent who was co-infected on timestep 10 but recovered by timestep 11 would still carry the elevated `rel_sus` from timestep 10 indefinitely. Always reset all agents to 1.0 first, then apply modifications based on current infection state:

```python
# WRONG -- values accumulate for recovered agents
def step(self):
    hiv.rel_sus[syph.active] = 2.7  # Never resets for recovered agents!

# RIGHT -- reset first, then modify
def step(self):
    hiv.rel_sus[:] = 1.0             # Reset everyone
    hiv.rel_sus[syph.active] = 2.7   # Then apply based on current state
```

**Do not put connectors in the disease list.** Connectors are a separate module type with their own execution timing. Passing a connector in the `diseases` list will cause errors or incorrect behavior because connectors do not have the same interface as disease modules. Always use the dedicated `connectors` keyword argument:

```python
# WRONG -- connector in disease list
sim = ss.Sim(diseases=[hiv, syph, HIV_Syphilis()])

# RIGHT -- connector in connectors argument
sim = ss.Sim(diseases=[hiv, syph], connectors=HIV_Syphilis())
```

**Do not modify disease states directly in connectors.** Connectors should modify `rel_sus` and `rel_trans` (transmission parameters), not directly change `infected` or `susceptible` states. Changing infection states is the responsibility of disease modules and interventions. If you need to cure agents or change infection status in response to co-infection, do that in an intervention instead.

**Avoid order-dependent logic between multiple connectors.** If you have multiple connectors that modify the same disease's `rel_sus`, be aware that they run sequentially and the last one to write wins. If both connectors reset to baseline, the second connector's reset will overwrite the first connector's modifications. When using multiple connectors, coordinate which disease parameters each connector is responsible for, or have a single connector handle all interactions.

## Debugging and Verification

### Tracking Connector Effects with an Analyzer

Use an `ss.Analyzer` to verify that the connector is working as expected. The analyzer runs each timestep and can record the values the connector is modifying (such as mean `rel_sus`) alongside disease prevalence.

```python
class check_connector(ss.Analyzer):
    def __init__(self):
        super().__init__()
        self.time = sc.autolist()
        self.rel_sus = sc.autolist()
        self.sis_prev = sc.autolist()
        self.hiv_prev = sc.autolist()

    def step(self):
        sis = self.sim.diseases.sis
        hiv = self.sim.diseases.hiv
        self.time += self.ti
        self.rel_sus += hiv.rel_sus.mean()
        self.sis_prev += sis.results.prevalence[self.ti]
        self.hiv_prev += hiv.results.prevalence[self.ti]
```

Pass the analyzer alongside the connector:

```python
sim = ss.Sim(
    diseases=[hiv, sis],
    networks=[mf, 'random'],
    connectors=SIS_HIV(),
    analyzers=check_connector(),
)
```

## Quick Reference

```python
# Minimal connector
class MyConnector(ss.Connector):
    def step(self):
        d1 = self.sim.diseases.disease1
        d2 = self.sim.diseases.disease2
        d1.rel_sus[:] = 1.0                    # Reset baseline
        d1.rel_sus[d2.infected.uids] = 2.0     # Apply modifier

# Parameterized connector
class MyConnector(ss.Connector):
    def __init__(self, **kwargs):
        super().__init__()
        self.define_pars(label='MyConn', multiplier=2.0)
        self.update_pars(**kwargs)
    def step(self):
        d1 = self.sim.diseases.disease1
        d1.rel_sus[:] = 1.0
        d1.rel_sus[condition] = self.pars.multiplier

# Sim setup
sim = ss.Sim(
    diseases=[disease1, disease2],
    networks=network,
    connectors=MyConnector(),        # Single connector
    # connectors=[conn1, conn2],     # Multiple connectors
    interventions=treatment,         # Optional
)

# Key properties to modify in step()
disease.rel_sus[uids] = value     # Relative susceptibility (multiplier)
disease.rel_trans[uids] = value   # Relative transmissibility (multiplier)
disease.infected[uids] = False    # Cure agents (in interventions only)
disease.susceptible[uids] = True  # Mark as susceptible (in interventions only)

# Access disease states
self.sim.diseases.<name>.infected       # Boolean array: currently infected
self.sim.diseases.<name>.susceptible    # Boolean array: currently susceptible
self.sim.diseases.<name>.active         # Boolean array: active infection (some diseases)
self.sim.people.<name>.cd4             # Numeric state: CD4 count (HIV-specific)

# Execution order per timestep
# Demographics -> Disease.step_state() -> Connectors -> Networks -> Interventions -> Transmission
```
