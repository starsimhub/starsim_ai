---
name: starsim-dev-networks
description: Use when setting up contact networks or mixing pools in Starsim — including random networks, sexual networks, maternal networks, mixing pools, and custom networks.
---

# Starsim Networks Reference

Starsim provides two mechanisms for disease transmission: **contact networks** (individual edge-based connections between agents) and **mixing pools** (group-level well-mixed transmission). Both inherit from `ss.Route` and can be used together in a single simulation. Networks are undirected edge lists that allow directional beta; mixing pools compute average contagion from source groups and expose destination groups.

## Key Classes

| Class | Parent | Purpose |
|-------|--------|---------|
| `ss.Route` | -- | Base class for all transmission pathways |
| `ss.Network` | `Route` | Base contact network with edge management |
| `ss.DynamicNetwork` | `Network` | Time-varying connections (adds/removes edges) |
| `ss.SexualNetwork` | `DynamicNetwork` | Sexual partnerships with debut age and acts |
| `ss.RandomNet` | `DynamicNetwork` | Random pairings for general infectious diseases |
| `ss.StaticNet` | `Network` | Import a NetworkX graph as a fixed network |
| `ss.MFNet` | `SexualNetwork` | Male-female (heterosexual) partnerships |
| `ss.MSMNet` | `SexualNetwork` | Men who have sex with men partnerships |
| `ss.MaternalNet` | `Network` | Mother-child transmission (base) |
| `ss.PrenatalNet` | `MaternalNet` | In-utero transmission |
| `ss.PostnatalNet` | `MaternalNet` | Birth canal / breastfeeding transmission |
| `ss.MixingPool` | `Route` | Single group-to-group well-mixed transmission |
| `ss.MixingPools` | `Route` | Multi-group mixing with contact matrix |
| `ss.AgeGroup` | -- | Helper to define age-filtered groups for pools |

### Hierarchy

```
ss.Route
├── ss.Network
│   ├── ss.StaticNet
│   └── ss.DynamicNetwork
│       ├── ss.RandomNet
│       └── ss.SexualNetwork
│           ├── ss.MFNet
│           └── ss.MSMNet
│   ├── ss.MaternalNet
│       ├── ss.PrenatalNet
│       └── ss.PostnatalNet
└── ss.MixingPool
    └── ss.MixingPools
```

## Patterns

### RandomNet -- general-purpose contact network

```python
import starsim as ss

net = ss.RandomNet(n_contacts=ss.poisson(4))
sir = ss.SIR(beta=0.1, dur_inf=10)
sim = ss.Sim(n_agents=10_000, diseases=sir, networks=net)
sim.run()
sim.plot()
```

The `n_contacts` parameter accepts a scalar or a distribution. Using `ss.poisson(4)` gives each agent a Poisson-distributed number of contacts with mean 4.

### MFNet -- heterosexual partnerships for STI modeling

```python
import starsim as ss
import starsim_examples as sse

syph = sse.Syphilis(
    beta={'mf': [0.25, 0.15]},  # male->female=0.25, female->male=0.15
)

mf = ss.MFNet(
    duration=1/24,  # Average partnership duration in years
    acts=80,        # Coital acts per year
)

pars = dict(start=2000, dur=20, dt=1/12)
sim = ss.Sim(pars=pars, diseases=syph, networks=mf)
sim.run()
sim.plot()
```

### Directional beta

For diseases on sexual networks, `beta` can be a dict keyed by network name. Each value is a two-element list `[p1_to_p2, p2_to_p1]`. In MFNet, p1=male and p2=female:

```python
beta = {'mf': [0.25, 0.15]}          # male->female=0.25, female->male=0.15
beta = {'mf': [0.25, 0.15], 'msm': [0.4, 0.4]}  # Add MSM network too
```

### MSMNet -- men who have sex with men

```python
msm = ss.MSMNet(
    duration=1/24,       # Partnership duration in years
    acts=80,             # Acts per year
    participation=0.1,   # Fraction of males who participate
)
```

Combine with MFNet for multi-network STI models:

```python
sim = ss.Sim(
    diseases=sse.Syphilis(beta={'mf': [0.25, 0.15], 'msm': [0.4, 0.4]}),
    networks=[mf, msm],
)
```

### Maternal networks -- mother-to-child transmission

Maternal networks require `ss.Pregnancy()` in demographics. As new agents are born, edges are automatically added between mother and child.

```python
import starsim as ss
import starsim_examples as sse

syph = sse.Syphilis(
    beta={'mf': [0.25, 0.15], 'maternal': [0.99, 0]},
)

pregnancy = ss.Pregnancy(fertility_rate=20)
death = ss.Deaths(death_rate=15)
maternal = ss.MaternalNet()
mf = ss.MFNet(duration=1/24, acts=80)

pars = dict(start=2000, dur=10, dt=1/12)
sim = ss.Sim(
    pars=pars,
    diseases=syph,
    networks=[mf, maternal],
    demographics=[pregnancy, death],
)
sim.run()
sim.plot()
```

Use `ss.PrenatalNet()` for in-utero transmission or `ss.PostnatalNet()` for birth/breastfeeding transmission instead of the generic `ss.MaternalNet()`.

### StaticNet -- import a NetworkX graph

```python
import networkx as nx
import starsim as ss

G = nx.watts_strogatz_graph(n=1000, k=4, p=0.3)
net = ss.StaticNet(graph=G)
sim = ss.Sim(diseases=ss.SIR(), networks=net)
sim.run()
```

### MixingPool -- single group-to-group transmission

A mixing pool computes average contagion from source agents and exposes destination agents. It does not track individual edges.

```python
import starsim as ss

mp = ss.MixingPool(
    beta=1.0,
    n_contacts=ss.poisson(lam=3),
)
sir = ss.SIR()
sim = ss.Sim(diseases=sir, networks=mp, verbose=0)
sim.run()
sim.plot()
```

Filter by source/destination group and restrict to specific diseases:

```python
mp = ss.MixingPool(
    diseases='sir',                            # Only transmit SIR, not other diseases
    src=lambda sim: sim.people.age < 15,       # Sources: children under 15
    dst=ss.AgeGroup(low=15, high=None),        # Destinations: adults 15+
    n_contacts=ss.poisson(lam=5),
)
sim = ss.Sim(diseases=['sir', 'sis'], networks=mp)
sim.run()
```

The `src` and `dst` parameters accept a uid array, a callable `lambda sim: ...` returning uids/BoolArr, or an `ss.AgeGroup` object.

### MixingPools -- multi-group with contact matrix

`MixingPools` (plural) manages multiple pools via a contact matrix. The `src` and `dst` parameters are dicts mapping group names to uid-returning callables.

#### Age-structured mixing

```python
import numpy as np
import sciris as sc
import starsim as ss

bin_size = 5
lows = np.arange(0, 80, bin_size)
highs = sc.cat(lows[1:], 100)
groups = ss.ndict([ss.AgeGroup(low=low, high=high) for low, high in zip(lows, highs)])
n_groups = len(groups)

# Contact matrix: rows=source, columns=destination
# Replace with Prem et al. data for real applications
cm = np.random.random((n_groups, n_groups)) + 3 * np.diag(np.random.rand(n_groups))

mps = ss.MixingPools(
    n_contacts=cm,
    src=groups,
    dst=groups,
)

sir = ss.SIR()
sim = ss.Sim(diseases=sir, networks=mps, dur=5, dt=1/4, n_agents=1000, verbose=0)
sim.run()
sim.plot()
```

#### SES-based mixing with custom states

Mixing pools work with any agent property, not just age. Define custom states and filter groups accordingly:

```python
import numpy as np
import sciris as sc
import starsim as ss

ses = sc.objdict(low=0, mid=1, high=2)

# Add custom SES state: 50% low, 30% mid, 20% high
ses_arr = ss.FloatArr('ses', default=ss.choice(a=ses.values(), p=[0.5, 0.3, 0.2]))
ppl = ss.People(n_agents=5_000, extra_states=ses_arr)

mps = ss.MixingPools(
    src={k: lambda sim, s=v: ss.uids(sim.people.ses == s) for k, v in ses.items()},
    dst={k: lambda sim, s=v: ss.uids(sim.people.ses == s) for k, v in ses.items()[:-1]},
    # Rows=source, columns=destination
    n_contacts=np.array([
        [2.50, 0.00],  # low->low,  low->mid
        [0.05, 1.75],  # mid->low,  mid->mid
        [0.00, 0.15],  # high->low, high->mid
    ]),
)

sir = ss.SIR(beta=ss.peryear(0.2))
sim = ss.Sim(people=ppl, diseases=sir, networks=mps, dt=1/12, dur=35, verbose=0)
sim.run()
sim.plot()
```

Note the `lambda sim, s=v:` pattern -- the default argument `s=v` captures the loop variable by value. Without it, all lambdas would reference the last value of `v`.

### Network inspection

After initialization, networks expose methods for querying and visualizing contacts:

```python
net = ss.RandomNet()
sir = ss.SIR()
sim = ss.Sim(n_agents=50, diseases=sir, networks=net)
sim.init()

net = sim.networks.randomnet

# Find all contacts of a specific agent
contacts = net.find_contacts([0])

# Convert edge list to a pandas DataFrame
df = net.to_df()  # Columns: p1, p2, beta, dur
uid0_edges = df.loc[(df['p1'] == 0) | (df['p2'] == 0)]

# Plot the network graph using networkx
net.plot()
```

### Custom networks -- override add_pairs()

To create a custom network, inherit from an existing class and override `add_pairs()`:

```python
import starsim as ss

class AgeMFNet(ss.MFNet):
    def add_pairs(self, people, ti=None):
        # Custom logic to select pairs based on age
        # Must return or populate self.edges
        return
```

This retains all MFNet behavior (debut, acts, duration) but lets you control how new partnerships are formed.

## Anti-Patterns

**Networks must be initialized within a sim before edges are populated.** A standalone network object has no edges:

```python
# WRONG -- edges are empty
net = ss.RandomNet()
net.edges  # Nothing here

# CORRECT -- initialize within a sim
sim = ss.Sim(n_agents=50, diseases=ss.SIR(), networks=net)
sim.init()
sim.networks.randomnet.edges  # Populated
```

**Contact matrix orientation: rows = source, columns = destination.**

```python
# In MixingPools, n_contacts shape is (n_src_groups, n_dst_groups)
# Row index selects the source group
# Column index selects the destination group
n_contacts = np.array([
    [2.50, 0.00],  # src=low  -> dst=low, dst=mid
    [0.05, 1.75],  # src=mid  -> dst=low, dst=mid
    [0.00, 0.15],  # src=high -> dst=low, dst=mid
])
```

**Network class names are lowercased when accessed on sim.networks:**

```python
# Access pattern: sim.networks.<classname_lowercase>
sim.networks.randomnet    # not sim.networks.RandomNet
sim.networks.mfnet        # not sim.networks.MFNet
sim.networks.maternalnet  # not sim.networks.MaternalNet
```

**MixingPools do not represent individual connections.** They compute average contagion across the source group and expose each destination agent to that average. You cannot call `find_contacts()` or `to_df()` on a mixing pool.

**Maternal networks require ss.Pregnancy() in demographics.** Without it, no mother-child edges are created:

```python
# WRONG -- maternal network with no pregnancy module
sim = ss.Sim(diseases=sir, networks=ss.MaternalNet())

# CORRECT
sim = ss.Sim(
    diseases=sir,
    networks=ss.MaternalNet(),
    demographics=ss.Pregnancy(fertility_rate=20),
)
```

**Do not forget networks for transmissible diseases.** Without a network or mixing pool, there is no transmission:

```python
# WRONG -- no contacts, no transmission
sim = ss.Sim(diseases=ss.SIR())

# CORRECT
sim = ss.Sim(diseases=ss.SIR(), networks=ss.RandomNet())
```

## Quick Reference

| Task | Code |
|------|------|
| Random network | `ss.RandomNet(n_contacts=ss.poisson(4))` |
| Heterosexual network | `ss.MFNet(duration=1/24, acts=80)` |
| MSM network | `ss.MSMNet(duration=1/24, acts=80, participation=0.1)` |
| Maternal network | `ss.MaternalNet()` (requires `ss.Pregnancy()`) |
| Prenatal network | `ss.PrenatalNet()` (requires `ss.Pregnancy()`) |
| Postnatal network | `ss.PostnatalNet()` (requires `ss.Pregnancy()`) |
| Static from NetworkX | `ss.StaticNet(graph=nx_graph)` |
| Directional STI beta | `beta={'mf': [0.25, 0.15]}` |
| Multi-network beta | `beta={'mf': [0.25, 0.15], 'msm': [0.4, 0.4]}` |
| Simple mixing pool | `ss.MixingPool(beta=1.0, n_contacts=ss.poisson(3))` |
| Pool with src/dst filter | `ss.MixingPool(src=lambda sim: sim.people.age < 15, dst=ss.AgeGroup(15, None))` |
| Pool for specific disease | `ss.MixingPool(diseases='sir', ...)` |
| Age-structured pools | `ss.MixingPools(n_contacts=cm, src=groups, dst=groups)` |
| Define age group | `ss.AgeGroup(low=0, high=15)` |
| Find contacts | `sim.networks.randomnet.find_contacts([uid])` |
| Edge list to DataFrame | `sim.networks.randomnet.to_df()` |
| Plot network graph | `sim.networks.randomnet.plot()` |
| Custom network | Subclass and override `add_pairs()` |
| Access network post-init | `sim.networks.randomnet` (lowercase class name) |
| Combine networks | `ss.Sim(networks=[mf, msm, maternal], ...)` |
