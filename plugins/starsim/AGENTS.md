# AGENTS.md — Starsim

Portable guidance for AI coding agents (Codex, Cursor, OpenCode, and other harnesses
that read `AGENTS.md`) working on [Starsim](https://github.com/starsimhub/starsim)
agent-based disease models. Claude Code users get this and much more automatically via
the `starsim-ai` plugin's skills and hooks — this file is the standalone export for
everything else. Drop it into the root of a Starsim project to make it active.

> Canonical source for the anti-patterns below: `skills/starsim-dev/starsim-antipatterns.md`.
> Keep the two in sync if you edit either.

## Approach

1. Look up current API signatures before writing code (Starsim's API moves between versions).
   If a docs MCP/Context7 source is available, prefer it over memory.
2. Start simple — get a minimal working simulation, then layer in complexity.
3. Prefer built-in modules (`ss.SIR`, `ss.RandomNet`, ...) over custom implementations.
4. **Verify before declaring done.** Run the model and sanity-check results — Starsim fails
   *silently* (no epidemic, flat curves, implausible scale) as often as it errors. A clean
   run is not proof the model is correct.

## Anti-patterns to avoid

- **`np.random` for sampling** → use an `ss.<dist>` (e.g. `ss.normal`, `ss.bernoulli`) so
  sampling flows through the Common Random Number (CRN) stream. Reproducibility depends on it.
- **`beta=ss.peryear(...)` / `ss.perday(...)`** → transmission `beta` is a bare per-act
  probability float; pass it plain (`beta=0.1`). Wrapping it in a rate corrupts the scale.
- **`def initialize(self, sim)`** → wrong lifecycle hook; override `init_post(self)`.
- **`self.sim.t.ti`** → inside a module use `self.ti`.
- **`np.where(state)[0]` / `state[:]` / `int(state)` to get agents** → these give
  positions/booleans, not UIDs. Use `state.uids`.
- **`hasattr` / `getattr`** → prefer `isinstance(...)` and `people['x']` / `module['x']`.
- **Per-agent state as plain attributes** → declare with `define_states([...])` so it grows,
  shrinks, and resets with the population.
- **A transmissible disease with no network/mixing pool** → no contact structure means no
  epidemic.

## Minimal example

```python
import starsim as ss

sim = ss.Sim(
    diseases=ss.SIR(beta=0.1, dur_inf=10),
    networks=ss.RandomNet(n_contacts=4),
)
sim.run()
sim.plot()
```
