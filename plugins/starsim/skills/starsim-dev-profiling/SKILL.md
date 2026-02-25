---
name: starsim-dev-profiling
description: Use when profiling or debugging Starsim simulation performance — including line profiling, execution loop inspection, and custom probes.
---

# Profiling and Debugging

Starsim includes built-in profiling tools to identify slow modules and bottleneck functions. It also exposes the internal execution loop (`sim.loop`) for debugging step order, inserting custom probes, and visualizing how modules with different timesteps interleave.

## Key Tools

| Tool / Method | Purpose | When to use |
|---------------|---------|-------------|
| `sim.profile()` | Line-profile the full simulation run | First step when a sim is slow |
| `sim.profile(follow=func)` | Profile a specific function in detail | Drill into a known bottleneck |
| `prof.disp(maxentries=N)` | Show top N entries from profiling results | Summarize profiling output |
| `sim.loop.df` / `sim.loop.to_df()` | View execution plan as a DataFrame | Understand what runs and when |
| `sim.loop.plot()` | Simple visual timeline of the loop | Quick overview of step order |
| `sim.loop.plot_step_order()` | 3D plot of execution order | Multi-dt simulations |
| `sim.loop.plot_cpu()` | CPU time per step (same as profile plot) | Identify slow steps visually |
| `sim.loop.insert(func, label)` | Insert a probe function into the loop | Fine-grained debugging at exact positions |

## Profiling Workflow

The typical profiling workflow is: (1) run `sim.profile()` to get the big picture, (2) inspect with `prof.disp()` to find the slowest functions, (3) drill into specific functions with `follow`, and (4) optimize the bottleneck code.

## Patterns

### Full simulation profiling

Profile an entire simulation to see where time is spent. The call runs the sim internally and returns a profiling object. By default it also displays a CPU-time bar chart (a shortcut to `sim.loop.plot_cpu()`), which shows how much wall-clock time each step in the integration loop consumes.

```python
import starsim as ss

pars = dict(
    start = '2000-01-01',
    stop = '2020-01-01',
    diseases = 'sis',
    networks = 'random'
)

sim = ss.Sim(pars)
prof = sim.profile()
```

The profiling object (`prof`) wraps Sciris's line profiler and provides methods for inspecting and displaying results. The bar chart gives an immediate visual answer to "which module is slowest?"

### Displaying profiling results

After profiling, use `prof.disp()` to see line-by-line detail of where each function spends time. Use `maxentries` to limit the output to the top N entries, which is useful when the sim has many functions.

```python
prof.disp(maxentries=5)
```

The output table shows each profiled function, how many times it was called, total time, and per-line timings. This is the primary tool for identifying exactly which lines of code are slow.

**Name mismatch note:** Function names in the table refer to the *actual* functions in the source code, which may differ from graph labels. For example, `ss.SIS` does not define its own `step()` method but inherits it from `Infection`. The graph shows `sis.step()`, but the table lists `Infection.step()` because that is where the actual code lives. This is expected behavior -- the profiler always refers to where lines of code physically exist in the codebase.

### Profiling a specific function

Once you identify a slow function, drill into it with the `follow` argument. For example, if `SIS.infect()` is the bottleneck:

```python
prof = sim.profile(follow=ss.SIS.infect, plot=False)
prof.disp()
```

This gives line-by-line profiling for just that function, showing exactly which lines inside `infect()` are consuming the most time. This is the key technique for narrowing down performance problems to specific lines of code.

**Important:** You can only follow functions that are called as part of `sim.run()`. To profile functions called during `sim.init()` or other setup code, use `sc.profile()` directly from Sciris:

```python
import sciris as sc

sim = ss.Sim(diseases='sis', networks='random')
with sc.profile() as prof:
    sim.init()
prof.disp()
```

### Inspecting the execution loop

The `sim.loop` object shows everything that happens during a simulation and in what order. After running or initializing a sim, inspect the full execution plan as a DataFrame:

```python
import starsim as ss

sim = ss.Sim(
    start = 2000,
    stop = 2002,
    diseases = 'sis',
    networks = 'random',
    verbose = 0,
)
sim.run()
sim.loop.df.disp()
```

Even a simple sim with three timesteps and two modules produces around 41 steps, so this view is valuable for understanding exactly what happens and in what order. The DataFrame columns include the function name, module, timestep index, and whether the step is active on a given tick. Use this to verify that your custom modules are being called at the right times and in the expected order relative to other modules.

### Visualizing the loop

Two plot methods help visualize execution order:

```python
# Simple timeline representation
sim.loop.plot()

# More detailed step-order plot (3D)
sim.loop.plot_step_order()
```

`plot_step_order()` is especially useful for multi-dt simulations (see below). The 3D plot is best viewed in an interactive window rather than inline in a notebook, so you can rotate it.

### Custom probes for debugging

Starsim lets you insert arbitrary "probe" functions directly into the execution loop at specific positions. This gives precise control over when your debugging code runs.

```python
def check_pop_size(sim):
    print(f'Population size is {len(sim.people)}')

sim = ss.Sim(diseases='sir', networks='random', demographics=True, dur=10)
sim.init()
sim.loop.insert(check_pop_size, label='people.finish_step')
sim.run()
```

The `label` argument specifies where in the loop to insert the function. The probe runs after the step matching that label. You can find valid labels by inspecting `sim.loop.df` -- the label column shows all available insertion points (e.g., `'people.finish_step'`, `'sis.step'`, `'randomnet.step'`). Probes receive the `sim` object as their only argument, giving full access to people, diseases, networks, and all other simulation state.

### Analyzers as a simpler alternative

For many debugging tasks, an analyzer is simpler than a probe. Analyzers always execute at the end of each timestep (after all modules have run).

```python
def check_pop_size(sim):
    print(f'Population size is {len(sim.people)}')

sim = ss.Sim(diseases='sir', networks='random', demographics=True, dur=10,
             analyzers=check_pop_size)
sim.run()
```

This produces the same output as the probe example above. The key tradeoff: probes give exact placement control within the loop (you can inspect state between any two steps), while analyzers are always executed last in the timestep (after all modules, results collection, etc.). Use analyzers for end-of-step monitoring and data collection; use probes when you need to inspect intermediate state, such as checking values between the disease state update and the transmission step.

### Different module timesteps

Starsim allows modules to run at different frequencies. For example, a disease might update every 0.1 time units while demographics update yearly. The `sim.loop` manages scheduling each module at its correct frequency.

```python
sis = ss.SIS(dt=0.1)
net = ss.RandomNet(dt=0.5)
births = ss.Births(dt=1)
sim = ss.Sim(dt=0.1, dur=5, diseases=sis, networks=net, demographics=births)
sim.init()
sim.loop.plot_step_order()
```

In this example:
- `SIS` runs every 0.1 time units (every step)
- `RandomNet` runs every 0.5 time units (every 5th step)
- `Births` runs every 1.0 time units (every 10th step)

The 3D step-order plot makes this interleaving visible. Each module appears as a separate row, with markers showing which global timesteps that module is active on. This is critical for verifying that fast-updating modules (like disease transmission) are correctly interleaved with slower modules (like demographic events).

When setting up multi-dt simulations, the sim's `dt` must be the smallest module `dt` (or a divisor of all module timesteps). Modules with larger `dt` values simply skip timesteps where they are not scheduled.

## Anti-patterns

**Do not profile in a notebook without `plot=False` when you only need the table.** The default `sim.profile()` generates a plot; pass `plot=False` if you only want the line-by-line output.

**Do not use probes when an analyzer suffices.** Probes are powerful but add complexity. If you just need end-of-timestep inspection, use an analyzer.

**Do not forget to call `sim.init()` before `sim.loop.insert()`.** The loop does not exist until the sim is initialized. Calling `insert` on an uninitialized sim will fail.

## Quick Reference

```python
import starsim as ss

# Full profiling
sim = ss.Sim(diseases='sis', networks='random')
prof = sim.profile()
prof.disp(maxentries=5)

# Profile a specific function
prof = sim.profile(follow=ss.SIS.infect, plot=False)
prof.disp()

# Inspect execution loop
sim.run()
sim.loop.df.disp()     # DataFrame of every step
sim.loop.plot()         # Visual timeline
sim.loop.plot_step_order()  # 3D plot

# Insert a probe
def my_probe(sim):
    print(f'N alive: {len(sim.people)}')

sim = ss.Sim(diseases='sir', networks='random', demographics=True, dur=10)
sim.init()
sim.loop.insert(my_probe, label='people.finish_step')
sim.run()

# Analyzer (simpler alternative)
sim = ss.Sim(diseases='sir', networks='random', dur=10, analyzers=my_probe)
sim.run()

# Multi-dt modules
sim = ss.Sim(dt=0.1, dur=5,
    diseases=ss.SIS(dt=0.1),
    networks=ss.RandomNet(dt=0.5),
    demographics=ss.Births(dt=1),
)
sim.init()
sim.loop.plot_step_order()
```
