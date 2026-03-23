---
name: starsim-dev-indexing
description: Use when working with Starsim arrays, UIDs, boolean states, or agent indexing — understanding the difference between UIDs, auids, raw, and values.
---

# Starsim Array Indexing Reference

Starsim uses an indexing system built on NumPy arrays to manage agents throughout their lifecycle, including when they die or are removed. Every agent has a permanent UID (universal identifier), and all state arrays (age, sex, disease states) support two views: `.raw` for all agents ever created, and `.values` for currently active agents only. Getting this wrong silently returns incorrect data, so understanding the distinction is critical.

## Key Concepts

| Concept | Description | Access |
|---------|-------------|--------|
| **UID** | Unique integer assigned sequentially from 0. Never changes, never reused after death. | `sim.people.uid` |
| **auids** | UIDs of currently alive/active agents. Dynamic subset of all UIDs. | `sim.people.auids` |
| **`.raw`** | Underlying NumPy array indexed by UID. Contains data for all agents ever created, including dead ones. | `sim.people.age.raw` |
| **`.values`** | NumPy array of data for active agents only. Indexed by position in auids. | `sim.people.age.values` |

## Patterns

### Setup for examples

```python
import starsim as ss

pars = dict(
    n_agents=10,
    diseases=dict(type='sir', init_prev=0.5, p_death=0.2),
    networks='random',
)
sim = ss.Sim(pars)
sim.run()
```

### Inspecting UIDs and auids

After a simulation with deaths, UIDs and auids diverge. This is the fundamental concept to grasp -- the total number of UIDs ever assigned stays constant, but `auids` shrinks as agents die:

```python
print(f"Total agents ever created: {len(sim.people.uid.raw)}")
print(f"Active agents: {len(sim.people.auids)}")
print(f"UIDs: {sim.people.uid}")            # All UIDs ever assigned
print(f"Active UIDs: {sim.people.auids}")    # Only alive agents
print(f"All UIDs (raw): {sim.people.uid.raw}")
print(f"Alive status: {sim.people.alive.raw}")
```

If agents 3 and 7 died, `auids` will be something like `[0, 1, 2, 4, 5, 6, 8, 9]` -- the dead agents are excluded. The `.raw` arrays still have 10 entries (indexed 0-9), but `.values` arrays only have 8 entries (indexed 0-7 by position).

### Raw vs values

Every Starsim state array maintains two parallel views of the same data. The `.raw` array is the full storage buffer indexed by UID. The `.values` array is a filtered view containing only active agents, indexed by position. When you access an array without a suffix (e.g., `sim.people.age`), it behaves like `.values`.

```python
# .values: data for active agents only
print(f"Ages (values): {sim.people.age}")          # Same as .values
print(f"Ages (raw): {sim.people.age.raw}")          # Includes dead agents
```

The lengths differ once any agents have died: `len(sim.people.age.raw)` equals total agents ever created, while `len(sim.people.age.values)` equals only the currently active count.

### Statistical operations work on active agents only

```python
# These two are identical -- both operate on active agents
print(f"Mean age (direct): {sim.people.age.mean():.2f}")
print(f"Mean age (values): {sim.people.age.values.mean():.2f}")
```

Built-in methods like `.mean()`, `.sum()`, and `.std()` automatically use `.values`, so they exclude dead agents.

### Integer indexing: by position, not UID

Integer indices select by position within active agents:

```python
# Gets the age of the FIRST ACTIVE agent, not agent with UID 0
age_of_first_active = sim.people.age[0]
print(f"Age of first active agent: {age_of_first_active}")
```

If agent UID 0 is dead, `age[0]` returns the age of whatever agent is first in `auids`.

### Indexing by UID with ss.uids()

To index by specific UIDs, wrap them with `ss.uids()`. This is the type-safe way to tell Starsim "I mean these specific agents by their permanent identity":

```python
specific_uids = ss.uids([0, 1, 2])
ages_by_uid = sim.people.age[specific_uids]
print(f"Ages of UIDs {specific_uids}: {ages_by_uid}")
```

This retrieves data from `.raw` by UID, regardless of whether agents are alive or dead. The `ss.uids()` wrapper signals to the array that you are providing UID-based indices, not positional indices. Without it, Starsim cannot distinguish a plain list `[0, 1, 2]` from positional indices and will raise an error.

### BoolState: getting UIDs where condition is True

Boolean states (like `alive`, `female`, `infected`) have a `.uids` property that returns the UIDs of all active agents where the state is `True`. The returned object is already an `ss.uids` array, so it can be used directly for indexing other arrays:

```python
female_uids = sim.people.female.uids
female_ages = sim.people.age[female_uids]
print(f"Ages of female agents: {female_ages}")
```

This is the idiomatic way to filter agents by a condition -- get UIDs from a BoolState, then use those UIDs to index other arrays.

### BoolState: .true() and .false()

Use `.true()` and `.false()` for explicit boolean filtering:

```python
alive_uids = sim.people.alive.true()
dead_uids = sim.people.alive.false()
print(f"Alive UIDs: {alive_uids}")
print(f"Dead UIDs: {dead_uids}")
```

`.uids` is equivalent to `.true()`.

### Combining UID filters

Use set operations on UID arrays for compound filters. UID arrays support `.intersect()` and `.union()` for combining multiple conditions:

```python
# Infected females
infected_uids = sim.diseases.sir.infected.uids
female_uids = sim.people.female.uids
infected_females = infected_uids.intersect(female_uids)

# Any agent who is either infected or female
either = infected_uids.union(female_uids)
```

This is more explicit and efficient than manually combining boolean arrays.

## Anti-Patterns (CRITICAL)

These mistakes silently produce wrong results or raise confusing errors. Read this section carefully -- these are the most common sources of bugs when working with Starsim arrays.

### `age[0]` does NOT get agent with UID 0

```python
# WRONG mental model -- this is NOT "agent 0"
sim.people.age[0]  # Gets first ACTIVE agent by position in auids

# CORRECT -- to get age of agent with UID 0
sim.people.age[ss.uids([0])]
```

If agents have died, the first active agent may have UID 2 or any other value. Integer indexing operates on the `.values` array (active agents only), indexed by position.

### Raw list indexing raises an error

```python
# WRONG -- raw Python list of ints is ambiguous and raises an error
sim.people.age[[0, 1, 2]]  # Raises error!

# CORRECT -- wrap in ss.uids() to index by UID
sim.people.age[ss.uids([0, 1, 2])]
```

Always use `ss.uids()` to convert a list of integers into a proper UID index.

### `.raw.mean()` includes dead agents

```python
# WRONG -- includes dead agents in the average
mean_all = sim.people.age.raw.mean()

# CORRECT -- uses active agents only
mean_active = sim.people.age.mean()

# Also correct -- explicit .values access
mean_active = sim.people.age.values.mean()
```

Since `.raw` is the full underlying NumPy array, standard NumPy operations on it include all agents ever created. Dead agents may have stale or zeroed-out values that corrupt your statistics. Always use the built-in `.mean()`, `.sum()`, `.std()` methods on the Starsim array directly -- they automatically filter to active agents.

### Do not mix .values and .raw indexing

```python
# WRONG -- .values is indexed by position, .raw is indexed by UID
# These are different arrays with different lengths and meanings
idx = 5
val_result = sim.people.age.values[idx]  # 5th active agent
raw_result = sim.people.age.raw[idx]     # Agent with UID 5

# They may return the same value if no agents have died,
# but will silently diverge once deaths occur.
```

Pick one indexing approach and use it consistently. Prefer the Starsim array methods (`.mean()`, indexing with `ss.uids()`) over direct NumPy access to `.raw` or `.values`. Code that works correctly with no deaths will silently break once deaths occur if it conflates positional and UID-based indexing.

### Do not wrap starsim array indexing results in np.asarray

When you index a starsim `Arr` with UIDs or a boolean mask, the result already works with numpy operations, boolean logic, and matplotlib. Wrapping in `np.asarray(..., dtype=bool)` or similar is unnecessary noise.

```python
# WRONG — unnecessary wrapping
is_ptb = np.asarray(preg.preterm[newborn_uids], dtype=bool)
is_lbw = np.asarray(fh.lbw[newborn_uids], dtype=bool)

# RIGHT — just use the result directly
is_ptb = preg.preterm[newborn_uids]
is_lbw = fh.lbw[newborn_uids]

# These already support boolean ops, sum, plotting, etc.
n_both = (is_ptb & is_lbw).sum()
plt.hist(fh.birth_weight[mask], bins=30)
```

Also note: indexing an `Arr` with UIDs (e.g., `arr[uids]`) returns a plain numpy array, not an `Arr` — so calling `.values` on the result will fail. Just use the result directly.

### Do not forget to check if UID arrays are empty

```python
# WRONG -- may fail or return meaningless results on empty arrays
infected_uids = sim.diseases.sir.infected.uids
mean_age = sim.people.age[infected_uids].mean()  # NaN or error if nobody infected

# CORRECT -- guard against empty
infected_uids = sim.diseases.sir.infected.uids
if len(infected_uids) > 0:
    mean_age = sim.people.age[infected_uids].mean()
```

## Quick Reference

| Task | Code |
|------|------|
| Get all active UIDs | `sim.people.auids` |
| Get all UIDs (including dead) | `sim.people.uid.raw` |
| Get age of active agents | `sim.people.age` or `sim.people.age.values` |
| Get age of all agents (including dead) | `sim.people.age.raw` |
| Index by specific UIDs | `sim.people.age[ss.uids([0, 1, 2])]` |
| Index by position in active agents | `sim.people.age[0]` (first active agent) |
| Mean age of active agents | `sim.people.age.mean()` |
| Sum over active agents | `sim.people.age.sum()` |
| UIDs where BoolState is True | `sim.people.female.uids` or `sim.people.female.true()` |
| UIDs where BoolState is False | `sim.people.alive.false()` |
| Intersect two UID sets | `uids_a.intersect(uids_b)` |
| Union two UID sets | `uids_a.union(uids_b)` |
| Wrap list as UID index | `ss.uids([0, 1, 2])` |
| Check number of active agents | `len(sim.people.auids)` |
| Check number of agents ever created | `len(sim.people.uid.raw)` |
| Boolean filter then index | `sim.people.age[sim.people.female.uids]` |

## Decision Rules

When writing code that accesses Starsim agent data, follow these rules:

1. **Need a specific agent by identity?** Use `ss.uids([uid])` to index.
2. **Need agents matching a condition?** Use `bool_state.uids` to get UIDs, then index other arrays with those UIDs.
3. **Need a statistic (mean, sum, count)?** Call the method directly on the Starsim array (e.g., `age.mean()`). Never call it on `.raw`.
4. **Need to iterate over all active agents?** Use `sim.people.auids` as the loop iterator.
5. **Need to include dead agents?** This is rare. Access `.raw` explicitly and document why.
