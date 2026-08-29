# Starsim anti-patterns

Canonical list of the non-obvious mistakes that even capable models repeatedly make in Starsim code. The **routing table** in `SKILL.md` references these by name to dispatch to the right skill. Check code you write against both tables below before declaring the work done.

| id | Anti-pattern | Why it's wrong | Correct form | Skill |
|----|--------------|----------------|--------------|-------|
| `np-random` | Using `np.random` / `numpy.random` for sampling | Bypasses Starsim's Common Random Number (CRN) stream, breaking reproducibility and counterfactual analysis. (Rare corner cases outside the CRN system may justify it — but prefer `ss.<dist>` where possible) | Use an `ss.<dist>` (e.g. `ss.normal`, `ss.bernoulli`) where possible, so sampling flows through the CRN system | [starsim-dev-random](../starsim-dev-random/SKILL.md), [starsim-dev-distributions](../starsim-dev-distributions/SKILL.md) |
| `beta-rate` | Wrapping transmission `beta` in `ss.peryear(...)` / `ss.perday(...)` | For the typical contact-network case, `beta` is a per-contact probability and the network handles the timestep, so wrapping it in a rate corrupts the scale. (A non-contact-based transmission route can be the exception — verify which you have) | Usually pass `beta` as a plain float (e.g. `beta=0.1`); use a rate only for a deliberately non-contact-based route | [starsim-dev-time](../starsim-dev-time/SKILL.md) |
| `old-initialize` | Defining `def initialize(self, sim)` on a module | Old/incorrect lifecycle hook signature | Override `init_post(self)` for post-initialization setup | [starsim-dev-interventions](../starsim-dev-interventions/SKILL.md), [starsim-dev-diseases](../starsim-dev-diseases/SKILL.md) |
| `sim-t-ti` | Reading the current timestep via `self.sim.t.ti` | Indirect and fragile inside a module | Use `self.ti` | [starsim-dev-sim](../starsim-dev-sim/SKILL.md) |
| `where-uids` | Getting agents via `np.where(state)[0]` (or `state[:]`, `int(state)`) | Returns positions/booleans, not UIDs — silently wrong indexing | Use `state.uids` to get the UIDs of agents in a boolean state | [starsim-dev-indexing](../starsim-dev-indexing/SKILL.md) |
| `hasattr-getattr` | Using `hasattr(...)` / `getattr(obj, 'x')` for introspection | Starsim prefers explicit type checks and dict-style access | Prefer `isinstance(...)`, and `people['x']` / `module['x']` over `getattr` | [starsim-style-python](../starsim-style-python/SKILL.md), [starsim-dev-indexing](../starsim-dev-indexing/SKILL.md) |

## Other recurring mistakes

These are just as common, but more context-dependent, so they need judgment rather than pattern-matching:

- **Per-agent state declared as plain attributes** instead of `define_states([...])`. Plain
  attributes don't grow/shrink with the population or reset on death. (`starsim-dev-diseases`,
  `starsim-dev-interventions`)
- **A transmissible disease with no network or mixing pool** — `ss.Infection` needs a contact
  structure or no epidemic occurs. (`starsim-dev-networks`)
- **`len(sim.people)` used as a per-timestep denominator.** It counts the agents in `auids`, which still includes agents who died this timestep, so any rate computed from it is understated by that timestep's deaths. Use `sim.people.n_alive` (or `results.n_alive`). (`starsim-dev-sim`, `starsim-dev-indexing`)
- **Scheduling later disease stages from the time of acquisition** in a model with a latent period, so the latent period eats into the infectious period rather than delaying it. Schedule from `ti_infectious`, and use `ss.SEIR` rather than hand-rolling one. (`starsim-dev-diseases`)
