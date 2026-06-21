# Starsim anti-patterns

Canonical list of the non-obvious mistakes that even capable models repeatedly make in
Starsim code. This file is the single source of truth for two surfaces:

- The **routing table** in `SKILL.md` references these by name to dispatch to the right skill.
- The **PostToolUse hook** (`hooks/check_antipatterns.py`) pattern-matches these in edited
  Python and nudges Claude at the moment the mistake is introduced.

If you add, remove, or reword a rule here, update the corresponding regex in
`hooks/check_antipatterns.py` (each rule there is tagged with the same `id`).

| id | Anti-pattern | Why it's wrong | Correct form | Skill |
|----|--------------|----------------|--------------|-------|
| `np-random` | Using `np.random` / `numpy.random` for sampling | Bypasses Starsim's Common Random Number (CRN) stream, breaking reproducibility and counterfactual analysis | Use an `ss.<dist>` (e.g. `ss.normal`, `ss.bernoulli`) so sampling flows through the CRN system | [starsim-dev-random](../starsim-dev-random/SKILL.md), [starsim-dev-distributions](../starsim-dev-distributions/SKILL.md) |
| `beta-rate` | Wrapping transmission `beta` in `ss.peryear(...)` / `ss.perday(...)` | `beta` is a bare float — a per-act/per-contact probability. Wrapping it in a rate corrupts the scale | Pass `beta` as a plain float (e.g. `beta=0.1`) | [starsim-dev-time](../starsim-dev-time/SKILL.md) |
| `old-initialize` | Defining `def initialize(self, sim)` on a module | Old/incorrect lifecycle hook signature | Override `init_post(self)` for post-initialization setup | [starsim-dev-interventions](../starsim-dev-interventions/SKILL.md), [starsim-dev-diseases](../starsim-dev-diseases/SKILL.md) |
| `sim-t-ti` | Reading the current timestep via `self.sim.t.ti` | Indirect and fragile inside a module | Use `self.ti` | [starsim-dev-sim](../starsim-dev-sim/SKILL.md) |
| `where-uids` | Getting agents via `np.where(state)[0]` (or `state[:]`, `int(state)`) | Returns positions/booleans, not UIDs — silently wrong indexing | Use `state.uids` to get the UIDs of agents in a boolean state | [starsim-dev-indexing](../starsim-dev-indexing/SKILL.md) |
| `hasattr-getattr` | Using `hasattr(...)` / `getattr(obj, 'x')` for introspection | Starsim prefers explicit type checks and dict-style access | Prefer `isinstance(...)`, and `people['x']` / `module['x']` over `getattr` | [starsim-style-python](../starsim-style-python/SKILL.md), [starsim-dev-indexing](../starsim-dev-indexing/SKILL.md) |

## Other recurring mistakes (not auto-detectable)

These are real footguns but too context-dependent to flag mechanically — watch for them
during review:

- **Per-agent state declared as plain attributes** instead of `define_states([...])`. Plain
  attributes don't grow/shrink with the population or reset on death. (`starsim-dev-diseases`,
  `starsim-dev-interventions`)
- **A transmissible disease with no network or mixing pool** — `ss.Infection` needs a contact
  structure or no epidemic occurs. (`starsim-dev-networks`)
