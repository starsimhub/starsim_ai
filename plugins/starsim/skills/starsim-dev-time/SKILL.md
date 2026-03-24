---
name: starsim-dev-time
description: Use when working with dates, durations, rates, and time conversions in Starsim — including ss.date, ss.dur, ss.peryear, ss.prob, and Timeline.
---

# Starsim Time, Dates, Durations, and Rates

Starsim provides a comprehensive time system with unit-aware dates, durations, and rates. Time is deceptively complex in disease modeling: a month is defined as exactly 1/12th of a year, a year equals 365 days, and converting between rates and probabilities requires careful ordering of operations. This skill covers all the time-related classes and the critical rules for working with them correctly.

## Key classes

| Class | Category | Purpose | Example |
|-------|----------|---------|---------|
| `ss.date` | Date | Calendar date (wraps `pd.Timestamp`) | `ss.date(2020)` |
| `ss.days` | Duration | Duration in days | `ss.days(7)` |
| `ss.weeks` | Duration | Duration in weeks | `ss.weeks(2)` |
| `ss.months` | Duration | Duration in months (1 month = 1/12 year) | `ss.months(6)` |
| `ss.years` | Duration | Duration in years (1 year = 365 days) | `ss.years(10)` |
| `ss.datedur` | Duration | Calendar-precise duration | `ss.datedur(months=6)` |
| `ss.Timeline` | Timeline | Manages sim/module time vectors | `ss.Timeline(start=2020, stop=2030, dt=ss.month)` |
| `ss.freqperyear` | Rate (freq) | Number of events per time | `ss.freqperyear(80)` |
| `ss.peryear` | Rate (per) | Probability rate per time | `ss.peryear(0.1)` |
| `ss.probperyear` | Rate (prob) | Probability over a time period | `ss.probperyear(0.01)` |
| `ss.prob` | Rate (prob) | Unitless probability | `ss.prob(0.5)` |

## Patterns

### Dates

Create dates from integers, strings, or components -- all are equivalent:

```python
import starsim as ss

d1 = ss.date(2020)
d2 = ss.date(2020, 1, 1)
d3 = ss.date('2020-01-01')

assert d1 == d2 == d3
```

Also accepts `pd.Timestamp` and `datetime.datetime` objects:

```python
import pandas as pd
import datetime as dt

d4 = ss.date(pd.Timestamp('2020-01-01'))
d5 = ss.date(dt.datetime(2020, 1, 1))
assert d1 == d4 == d5
```

Get the floating-point year and full property display:

```python
d = ss.date('2025.08.02')
print(d.years)   # Float year, e.g. 2025.5863...
print(float(d))  # Alias to d.years
d.disp()          # Print all properties
```

### Date arithmetic

Add durations to dates:

```python
d = ss.date('2015.8.10')
print(d + ss.years(10))                      # 10 years later
print(d + ss.datedur(months=3, days=-5))     # 3 months forward, 5 days back
```

### Date arrays and ranges

Create arrays of dates from NumPy arrays or using `arange`:

```python
import numpy as np

datearr = ss.date.from_array(np.arange(1990, 2020))
print(datearr)

weekarr = ss.date.arange(start='2025-07-01', stop='2025-09-18', step=ss.week)
print(weekarr)
```

### Durations

The base class is `ss.dur()`, but you almost always want `ss.days()`, `ss.weeks()`, `ss.months()`, or `ss.years()`. If you type `ss.dur(3, 'years')`, it returns `ss.years(3)`. The left-hand operator takes precedence in mixed-unit arithmetic:

```python
d1 = ss.years(2)
d2 = ss.days(3)
print(d1 + d2)  # Result in years
print(d2 + d1)  # Result in days
```

Convert between units (with or without trailing 's'):

```python
d1 = ss.years(10)
print(d1.days)          # View as days, internal unit stays years
d2 = d1.to('days')      # Convert internal representation to days
d3 = d1.to('day')       # Also works without the 's'
print(d2)
```

Shortcut constants for unit values:

```python
print(ss.week)   # Same as ss.weeks(1)
print(ss.day)    # Same as ss.days(1)
print(ss.month)  # Same as ss.months(1)
print(ss.year)   # Same as ss.years(1)
assert ss.weeks(1) == ss.week
```

### Date durations vs. float durations

`ss.datedur` does calendar-precise arithmetic, while `ss.years` does float-based arithmetic. These can give different results:

```python
d = ss.date('2025.1.1')
print(d + ss.years(0.5))        # 2025-07-02 (float: 2025.5 maps to Jul 2)
print(d + ss.datedur(months=6)) # 2025-07-01 (calendar: exactly 6 months)
```

This happens because there are fewer days from Jan 1 to Jul 1 (181) than from Jul 1 to Dec 31 (183), so the fractional midpoint of the year (0.5) lands on Jul 2, not Jul 1:

```python
print(ss.date('2025.7.1') - ss.date('2025.1.1'))   # 181 days
print(ss.date('2025.12.31') - ss.date('2025.7.1'))  # 183 days
```

Use `ss.datedur` when calendar precision matters (e.g., "exactly 6 months from today"). Use `ss.years` when working with fractional year arithmetic in disease models.

### Timeline

`ss.Timeline` coordinates time across the sim and its modules. Stored as `sim.t` and each module's `.t`. It provides multiple representations of the same time:

```python
t = ss.Timeline(start=2020, stop=2022, dt=ss.month)
print(t.to_dict())
# Keys: datevec, yearvec, relvec, tivec, tvec, timevec
```

The key vectors:

| Vector | Content |
|--------|---------|
| `datevec` | Calendar dates |
| `yearvec` | Floating-point years |
| `relvec` | Relative times since sim start |
| `tivec` | Timestep indices |
| `timevec` | Most human-friendly representation (used for plotting and results) |

Duration-based timelines (no calendar dates) also work:

```python
t = ss.Timeline(start=ss.days(0), stop=ss.days(10), dt=ss.day)
```

### Plotting with dates

When results use `ss.date` objects in `timevec`, the x-axis is `np.datetime64[ns]`. Two safe approaches:

```python
# Approach 1: Plot with date x-axis, use ss.date() for annotations
plt.figure()
plt.plot(r1.timevec, r1.sis.prevalence, label='Baseline')
plt.axvline(ss.date(2015), color='k', label='Intervention')  # Wrap in ss.date()
plt.legend()

# Approach 2: Plot with float years to avoid date issues entirely
plt.figure()
years = r1.timevec.years  # Convert timevec to float years
plt.scatter(years, r1.sis.prevalence, label='Baseline')
plt.axvline(2015, color='k', label='Intervention')  # Plain int works with float axis
plt.legend()
```

### Rates: three types

Starsim distinguishes three types of rates. Choosing the right one is important.

**Frequency (`ss.freq`)** -- number of events per time. Arithmetic works like regular floats:

```python
f = ss.freqperyear(80)   # 80 events per year
print(f * 10)             # 800 events per year

# Construct from inverse of duration
d = ss.days(2)
f2 = 1 / d               # 0.5 per day
```

**Probability rate (`ss.per`)** -- rate at which a single event happens (e.g., death rate). Must be non-negative but can exceed 1. When multiplied by a scalar, the rate scales linearly. When multiplied by a duration, it converts to a probability:

```python
r = ss.peryear(0.8)
print(r * 2)              # 1.6 (scaled rate)
# r * ss.years(1) => 1 - exp(-0.8) ~ 0.55 (probability)
```

**Probability (`ss.prob`)** -- a probability optionally attached to a time period. When multiplied by a duration, uses the underlying rate to compute the new probability:

```python
p = ss.prob(0.8, ss.years(1))   # 80% chance per year
# p * ss.years(1)  => 0.8       (same period, unchanged)
# p * ss.years(2)  => 0.96      (two years, not 1.6)
```

The key difference between `ss.per` and `ss.prob` is subtle but important. `ss.per` works directly with the instantaneous rate. `ss.prob` starts with a probability and a duration, back-calculates the underlying rate (`rate = -log(1 - prob)`), then converts forward to the new probability. In practice:

- Use `ss.per` when you have a *rate* (e.g., from epidemiological literature: "death rate of 0.01 per year").
- Use `ss.prob` when you have an *observed probability* (e.g., "10 out of 1000 people died in a year").

For small values, `ss.per` and `ss.prob` are nearly identical. They diverge for larger values:

```python
# ss.peryear(0.8) * ss.years(1) => 1 - exp(-0.8) ~ 0.55
# ss.probperyear(0.8) * ss.years(1) => 0.8 (the probability itself)
```

Summary of when to use each:

| Type | Use case | Example |
|------|----------|---------|
| `ss.freq` / `ss.freqperyear` | Number of events | Sexual acts per year: `ss.freqperyear(80)` |
| `ss.per` / `ss.peryear` | Probability of a single event from a rate | Death rate: `ss.peryear(0.01)` |
| `ss.prob` / `ss.probperyear` | Convert observed probability across time periods | Observed death probability: `ss.probperyear(0.01)` |

### Rate conversion: `to_prob()` and `to_events()` -- CRITICAL

Every rate has `.to_prob()` and `.to_events()` methods. The only difference between `ss.freq` and `ss.per` is that multiplying `ss.freq` by a duration calls `.to_events()`, while multiplying `ss.per` by a duration calls `.to_prob()`.

When the sim initializes, it finds all timepars and adds a `default_dur` property equal to the module's `dt`. This means `death_rate.to_prob()` is a shortcut for `death_rate * self.dt`.

**The `.to_prob()` call MUST be the last step**, after all multiplications by relative factors:

```python
# Define the death rate
death_rate = ss.peryear(0.1)
rel_death_age = 3.4  # Older age, higher risk
rel_death_ses = 5.7  # Lower SES, higher risk

# RIGHT -- multiply first, then convert to probability
p_death = (death_rate * rel_death_age * rel_death_ses).to_prob()

# WRONG -- converting to probability before multiplying by relative factors
p_death = death_rate.to_prob() * rel_death_age * rel_death_ses
```

Why? Because `to_prob()` applies the nonlinear transformation `p = 1 - exp(-rate * dt)`. Multiplying a probability by scalars afterward does not correctly compose the rates. The rate must be fully scaled before the nonlinear conversion.

The mathematical difference between rate types on multiplication by a duration:

- `ss.freq * duration` --> number of events (linear: `rate * duration`)
- `ss.per * duration` --> probability (nonlinear: `1 - exp(-rate * duration)`)
- `ss.prob * duration` --> probability (probability --> underlying rate --> new probability)

### Probability multiplication is not arithmetic

Probabilities are always constrained to [0, 1], so multiplication does not behave like normal arithmetic:

```python
print(ss.prob(0.5) * 2)  # ss.prob(0.75), NOT 1.0
print(ss.prob(0.1) * 2)  # ~ss.prob(0.19), NOT 0.2
```

The underlying math: multiply the rate by the scalar, then convert back to probability. For `ss.prob(0.5) * 2`: rate = `-log(1 - 0.5) = 0.693`, doubled = `1.386`, new prob = `1 - exp(-1.386) = 0.75`.

### Converting agent ages or durations between units

Duration objects work with arrays, so always use the starsim time API instead of manual conversion factors like `* 365.25`:

```python
# WRONG — manual conversion, fragile
age_days = sim.people.age[uids] * 365.25

# RIGHT — starsim time API, works with scalars and arrays
age_days = ss.years(sim.people.age[uids]).days

# Other conversions
ga_weeks = ss.years(duration_in_years).weeks
months = ss.days(n_days).months
```

## Anti-patterns

### CRITICAL: `plt.axvline(2015)` with date axes

When `timevec` contains `ss.date` objects, Matplotlib's x-axis uses `np.datetime64[ns]`. Passing a bare integer like `2015` is interpreted as 2,015 **nanoseconds** after January 1, 1970 -- placing the vertical line at the far left edge, completely wrong. This is one of the most common bugs.

```python
# WRONG -- 2015 interpreted as nanoseconds after epoch
plt.axvline(2015, color='k')

# RIGHT -- convert to a date
plt.axvline(ss.date(2015), color='k')

# ALSO RIGHT -- use floating-point years for the x-axis instead
years = r1.timevec.years
plt.scatter(years, r1.sis.prevalence)
plt.axvline(2015, color='k')  # Plain int works fine with float x-axis
```

This applies to all Matplotlib annotations: `axvline`, `axvspan`, `text`, `annotate`, and any other function that takes x-coordinates.

### CRITICAL: Converting rate to probability too early

This is the single most important rule for rate handling. The nonlinear rate-to-probability conversion must happen after all linear scaling:

```python
death_rate = ss.peryear(0.1)
rel_age = 3.4
rel_ses = 5.7

# WRONG -- probability is computed before scaling, produces invalid results
p = death_rate.to_prob() * rel_age * rel_ses

# RIGHT -- scale the rate first, then convert once at the end
p = (death_rate * rel_age * rel_ses).to_prob()
```

The same rule applies when combining rates from multiple sources in a disease model's `step_state()` or custom logic: accumulate all multiplicative factors on the rate, then call `.to_prob()` exactly once.

### `ss.years(0.5)` vs `ss.datedur(months=6)`

These are not always equivalent. Float-based `ss.years(0.5)` maps to the fractional midpoint of a year (often Jul 2), while `ss.datedur(months=6)` adds exactly 6 calendar months (Jul 1). Use `ss.datedur` when you need exact calendar dates; use `ss.years` when working with fractional math in models.

### Probability times scalar is not linear

Do not assume `ss.prob(x) * n == ss.prob(x * n)`:

```python
assert ss.prob(0.5) * 2 == ss.prob(0.75)  # NOT ss.prob(1.0)
assert ss.prob(0.1) * 2 != ss.prob(0.2)   # ~ss.prob(0.19)
```

This is correct behavior: multiplying a probability by a scalar doubles the *underlying rate*, not the probability itself. The conversion is: rate = `-log(1 - p)`, then new_p = `1 - exp(-rate * scalar)`.

### Year 0 does not exist in `ss.date`

There is no way to represent year 0 with `ss.date` (which wraps `pd.Timestamp`). For simulations that use relative time from zero (e.g., `start=0, stop=20`), use `ss.datedur` or duration-based timelines:

```python
# Duration-based timeline for relative sims (no calendar dates)
t = ss.Timeline(start=ss.days(0), stop=ss.years(20), dt=ss.month)
```

## Conventions

| Convention | Value |
|------------|-------|
| 1 month | Exactly 1/12 year |
| 1 year | 365 days |
| 1 week | 7 days |
| Units are loose vs unitless | `ss.days(5) == 5` |
| Units are strict vs other units | `ss.years(1) == ss.days(365)` |
| Year 0 | Not representable with `ss.date`; use `ss.datedur` for relative sims |

## Quick reference

```text
Dates:
  ss.date(2020)                          # From integer year
  ss.date('2020-01-01')                  # From string
  ss.date(2020, 1, 1)                    # From components
  d.years / float(d)                     # Float year
  d.disp()                               # Full property display
  ss.date.from_array(arr)                # Array of dates
  ss.date.arange(start, stop, step)      # Date range

Durations:
  ss.days(n), ss.weeks(n), ss.months(n), ss.years(n)
  ss.day, ss.week, ss.month, ss.year     # Unit shortcuts (value=1)
  ss.datedur(months=6, days=3)           # Calendar-precise duration
  ss.dur(n, 'unit')                      # Generic (returns specific subclass)
  d.to('days')                           # Convert units
  d.days, d.weeks, d.months, d.years     # View in other units

Timeline:
  ss.Timeline(start, stop, dt)
  t.datevec                              # Calendar dates
  t.yearvec                              # Floating-point years
  t.timevec                              # Human-friendly (used in results/plotting)
  t.relvec                               # Relative times since start
  t.tivec                                # Timestep indices
  sim.t                                  # Sim's timeline

Rates:
  ss.freqperyear(80)                     # Frequency: events per time
  ss.peryear(0.1)                        # Probability rate per time
  ss.probperyear(0.01)                   # Probability per time period
  ss.prob(0.5)                           # Unitless probability

Rate to probability:
  rate.to_prob()                         # Convert using module dt
  rate.to_events()                       # Convert to expected event count
  (rate * rel_factor1 * rel_factor2).to_prob()  # ALWAYS multiply first

Plotting:
  plt.axvline(ss.date(2015))             # Use ss.date() with date axes
  years = results.timevec.years          # Or use float years instead

Full class hierarchy:
  TimePar
  +-- dur                                # All durations (units of time)
  |   +-- days, weeks, months, years     # Specific unit durations
  |   +-- datedur                        # Calendar-precise durations
  +-- Rate                               # All rates (units of per-time)
      +-- freq                           # Events: freqperday..freqperyear
      +-- per                            # Probability rate: perday..peryear
      +-- prob                           # Probability: probperday..probperyear
```
