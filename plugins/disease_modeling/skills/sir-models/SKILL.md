---
name: sir-models
description: This skill should be used when the user asks about "SIR model", "SIR equations", "transmission coefficient beta", "basic reproduction number", "R0", "effective reproduction number", "herd immunity threshold", "epidemic curve", "ODE solver for epidemics", "numerical simulation of disease", or needs to build, parameterize, or analyze an SIR compartmental model.
---

# Week 2: SIR Models and R0

This module covers the mechanics of building, parameterizing, and analyzing SIR compartmental models: writing differential equations, decomposing and estimating transmission parameters, deriving the basic and effective reproduction numbers, designing interventions within the model framework, and solving the system numerically to produce epidemic curves.

## Formulate the SIR Differential Equations

**Context:** The SIR model partitions a closed population into three compartments -- Susceptible (S), Infectious (I), and Recovered (R) -- connected by flows that represent infection and recovery. These ordinary differential equations (ODEs) are the mathematical backbone of epidemic modeling for diseases that confer lasting immunity.

**Steps:**

1. Define the state variables: S(t) = number susceptible at time t, I(t) = number infectious, R(t) = number recovered. Define the total population N = S + I + R, held constant in a closed population (no births, deaths, or migration).

2. Write the three ODEs governing flow between compartments:
   - dS/dt = -beta x S x I
   - dI/dt = +beta x S x I - gamma x I
   - dR/dt = +gamma x I

   Here beta is the transmission coefficient (rate at which susceptible-infectious contacts produce new infections) and gamma is the recovery rate.

3. Verify equation balance by summing all three equations: dS/dt + dI/dt + dR/dt = -beta x S x I + beta x S x I - gamma x I + gamma x I = 0. This confirms total population is conserved. If the sum is non-zero, there is a bookkeeping error in the equations.

4. Recognize the nonlinear transmission term. The beta x S x I product makes the system nonlinear -- the rate of new infections depends on both the current number of susceptibles and infectious individuals simultaneously. This feedback is what generates the characteristic epidemic curve: early exponential growth when S is large, a peak as S depletes, and burnout when too few susceptibles remain.

5. For discrete-time implementations, write difference equations:
   - S(t+1) = S(t) - beta x S(t) x I(t)
   - I(t+1) = I(t) + beta x S(t) x I(t) - gamma x I(t)
   - R(t+1) = R(t) + gamma x I(t)

   Apply the same balance check: every term subtracted from one equation must appear as an addition in another.

## Decompose and Parameterize the Transmission Coefficient

**Context:** The transmission coefficient beta is not a single biological quantity but a composite of contact behavior and pathogen infectiousness. Decomposing it into measurable components enables parameterization from empirical data and clarifies which factors drive transmission.

**Steps:**

1. Express beta as the product of two components: beta = k x b, where k is the per-capita contact rate (contacts per person per unit time) and b is the probability of transmission given an infectious contact. This decomposition separates behavioral from biological drivers.

2. Choose between density-dependent and frequency-dependent transmission formulations based on the pathogen's ecology:
   - *Density-dependent:* force of infection lambda = beta x I. Contact rate scales with population density. Appropriate for airborne infections (influenza, measles) where crowding increases face-to-face encounters. The force of infection is proportional to the absolute number of infectious individuals.
   - *Frequency-dependent:* force of infection lambda = beta x I/N. Contact rate is constant regardless of population size. Appropriate for sexually transmitted infections where partnership rates do not scale with density. The force of infection is proportional to the fraction infectious.

   The presence or absence of N in the denominator of the force of infection signals which assumption is embedded in the model.

3. Convert clinical durations to rate parameters. The recovery rate gamma = 1/D, where D is the average duration of infectiousness. Clinical data typically report durations (e.g., "infectious for 5 days"), not rates. For gamma, a 5-day infectious period yields gamma = 0.2 per day.

4. Ensure consistent time units across all parameters. If beta is expressed per day, gamma must also be per day. Mixing daily and weekly rates is a common source of errors that produces unrealistic dynamics.

5. Recognize the distributional implication of constant rates. A constant per-capita recovery rate gamma implies exponentially distributed time spent in the infectious compartment: I(t) = I(0) x e^(-gamma x t). This means some individuals recover very quickly and others very slowly -- not everyone spends exactly 1/gamma time units infected. The mean is 1/gamma, but there is substantial variance.

## Set Initial Conditions and Validate

**Context:** Initial conditions determine whether a simulated epidemic can start at all and strongly influence its trajectory. Poorly chosen initial values produce misleading output or no epidemic dynamics whatsoever.

**Steps:**

1. Specify starting values for all compartments: S(0), I(0), and R(0). Ensure that S(0) + I(0) + R(0) = N exactly. Any violation of this constraint introduces spurious population growth or loss.

2. Seed the epidemic with a small number of initial infections. Set I(0) to at least 1 (or a small fraction of N). Starting with I(0) = 0 produces no epidemic regardless of parameter values, since the transmission term beta x S x I equals zero.

3. Choose S(0) to reflect the population's prior immunity. For a fully naive population, set S(0) = N - I(0) and R(0) = 0. For a partially immune population (e.g., after a prior epidemic wave or vaccination campaign), set R(0) to the number of immune individuals and S(0) = N - I(0) - R(0).

4. Sanity-check initial conditions against expected dynamics. A highly immune population (large R(0) relative to N) will suppress an epidemic even with high beta. Verify that the initial susceptible fraction is consistent with the scenario being modeled.

5. Verify compartment balance at every time step during simulation. Sum S(t) + I(t) + R(t) at several output time points and confirm the total equals N within numerical tolerance. Drift from N indicates either equation errors or numerical instability in the solver.

## Derive and Interpret the Basic Reproduction Number R0

**Context:** R0, the basic reproduction number, is the average number of secondary infections produced by a single infectious individual introduced into a fully susceptible population. It is the single most important threshold parameter in epidemic modeling.

**Steps:**

1. Derive R0 from the SIR equations. Starting from dI/dt = beta x S x I - gamma x I, factor out I: dI/dt = I x (beta x S - gamma). At the start of an epidemic, S is approximately N (fully susceptible). The infected compartment grows when beta x N - gamma > 0, i.e., when beta x N / gamma > 1. For frequency-dependent transmission (where beta already accounts for N), this simplifies to R0 = beta / gamma.

2. Decompose R0 into its biological components: R0 = (k x b) / gamma = k x b x D, where k is the contact rate, b is per-contact transmission probability, and D = 1/gamma is the average infectious duration. This reveals three independent levers for reducing R0.

3. Apply the threshold theorem: an epidemic occurs if and only if R0 > 1. When R0 < 1, each case generates fewer than one secondary case on average and the infection dies out. When R0 = 1, infection persists at a constant level (endemic equilibrium). When R0 > 1, exponential growth occurs in the early phase.

4. Estimate R0 from early outbreak data using the exponential growth rate. During the initial phase of an epidemic (before susceptible depletion), case counts grow approximately exponentially. Fit the early incidence curve to extract the growth rate r, then use R0 = 1 + r/gamma (for simple SIR dynamics) or fit the full model to the time series to back-calculate beta and compute R0 = beta/gamma. This approach was used during the 2014-2015 West Africa Ebola outbreak.

5. Estimate R0 from contact tracing data. Count the number of secondary cases generated by each known index case across early transmission generations. The average number of secondary cases approximates R0. The distribution of secondary cases also reveals transmission heterogeneity -- highly skewed distributions indicate superspreading events, as documented in SARS.

6. Back-calculate R0 from endemic equilibrium. If a disease is endemic, RE = 1 by definition and RE = R0 x (S*/N), where S* is the equilibrium susceptible fraction. Therefore R0 = N/S* = 1/x, where x is the susceptible proportion at equilibrium. For example, if 10% of the population remains susceptible at equilibrium, R0 = 10.

7. Interpret R0 comparatively. Higher R0 values produce faster-rising epidemic curves, higher peaks, and larger final epidemic sizes. Compare SIR simulations with different R0 values (e.g., R0 = 2 vs. R0 = 10) to build quantitative intuition for how R0 shapes outbreak dynamics.

## Calculate the Effective Reproduction Number RE

**Context:** While R0 describes transmissibility in a fully susceptible population, the effective reproduction number RE reflects actual transmission potential as immunity accumulates. RE is the real-time metric for monitoring epidemic trajectory.

**Steps:**

1. Compute RE from R0 and current susceptibility: RE = R0 x (S/N), where S/N is the fraction of the population still susceptible at time t. As individuals recover and move to R, S/N declines and RE decreases.

2. Track RE over time alongside the incidence curve. When RE > 1, case counts are accelerating. When RE drops below 1, the epidemic is declining -- each case generates fewer than one secondary case. The point at which RE crosses 1 corresponds to the epidemic peak.

3. Use RE to identify epidemic turning points. Plotting RE against time (as done for Guinea during the 2014 Ebola outbreak and for MERS-CoV across different regions) reveals when interventions or susceptible depletion begin to control transmission. Sustained RE < 1 indicates the epidemic is on a trajectory toward extinction.

4. Distinguish the causes of RE decline. RE can fall below 1 due to susceptible depletion (natural epidemic burnout), behavioral changes that reduce contact rates, or interventions such as vaccination. The model structure determines which mechanism is represented -- ensure the modeled RE decline corresponds to the mechanism of interest.

## Design Interventions in the Model

**Context:** Interventions modify either model parameters (changing transmission or recovery rates) or state variables (moving individuals between compartments). Mapping real-world interventions onto the correct model element is essential for generating meaningful policy projections.

**Steps:**

1. Identify which model element each intervention targets before modifying equations:
   - *Reducing contacts* (social distancing, school closures, travel restrictions): decrease the contact rate k, which lowers beta = k x b and therefore R0.
   - *Reducing per-contact transmission* (masking, hand hygiene, PPE): decrease the transmission probability b, which lowers beta.
   - *Shortening the infectious period* (antiviral treatment, early isolation): increase gamma (equivalently, decrease D = 1/gamma), which lowers R0 = beta/gamma.
   - *Vaccination:* remove individuals from S, reducing S/N and therefore RE = R0 x S/N.

2. Model vaccination as a flow from S to R. Add a per-capita vaccination rate v to the equations: dS/dt = -beta x S x I - v x S and dR/dt = gamma x I + v x S. This assumes sterilizing, lifelong immunity equivalent to natural infection. Use this simpler formulation when vaccine-derived and infection-derived immunity are indistinguishable.

3. Model vaccination with waning immunity using a separate V compartment. Add dV/dt = v x S - w x V, where w is the per-capita waning rate. Individuals whose immunity wanes return to S: include +w x V in the dS/dt equation. This extension is necessary when vaccine protection decays over time and re-vaccination or booster strategies must be evaluated.

4. Model quarantine by adding compartments. Introduce S_Q (quarantined susceptibles) and I_Q (quarantined infectious). Critically, quarantined infectious individuals must be excluded from the force of infection -- they do not contribute to the beta x S x I term. Define rates for entering and leaving quarantine, and route quarantine recoveries into the shared R compartment.

5. Calculate the herd immunity threshold from R0. Because RE = R0 x S/N, herd immunity is achieved when the immune fraction p satisfies p >= 1 - 1/R0. This yields the critical vaccination coverage:
   - R0 = 2: p_c = 50%
   - R0 = 5: p_c = 80%
   - R0 = 12: p_c = 92%
   - R0 = 18: p_c = 94%

   This directly translates R0 estimates into vaccination coverage targets. Note that this formula assumes homogeneous mixing; heterogeneous contact patterns can alter the actual threshold.

6. Choose the most practical intervention lever by decomposing R0. For high-contact, short-duration infections (e.g., airborne influenza: high k, small D), reducing contacts is more tractable than further shortening the infectious period. For low-contact, long-duration infections (e.g., sexually transmitted infections: low k, large D), reducing the infectious period via treatment is highly effective. Decompose R0 = k x b x D to identify the dominant term.

7. Verify equation balance after adding intervention terms. Every new outflow must have a matching inflow elsewhere. Sum all modified equations and confirm the total remains zero for a closed population.

## Solve SIR Models Numerically

**Context:** The SIR system has no closed-form analytical solution due to the nonlinear beta x S x I transmission term. Numerical simulation is the standard approach for exploring model behavior.

**Steps:**

1. Select an ODE solver. For basic SIR models, a standard solver such as scipy.integrate.solve_ivp (Python) or ode45 (MATLAB) with an adaptive step-size method (e.g., Runge-Kutta 4/5) is sufficient. Avoid fixed-step Euler methods for production work -- they require very small time steps to remain stable and accurate.

2. Define the system as a function that takes the current state vector [S, I, R] and parameters (beta, gamma) and returns the derivative vector [dS/dt, dI/dt, dR/dt]. Pass this function to the ODE solver along with initial conditions and the desired time span.

3. Choose an appropriate time resolution. For diseases with infectious periods of days, use sub-daily or daily time steps. For diseases with infectious periods of weeks or months, daily steps are typically sufficient. The adaptive solver will refine internally, but the output time points should be dense enough to capture the epidemic peak.

4. Interpret the simulated epidemic curve. Track all three compartments over time:
   - S(t) declines monotonically as the epidemic progresses.
   - I(t) rises, peaks, then falls -- the peak occurs when RE crosses 1 (i.e., when S/N = gamma/beta = 1/R0).
   - R(t) accumulates monotonically.

   The characteristic bell-shaped I(t) curve emerges from susceptible depletion, not from any external intervention.

5. Conduct sensitivity analysis by varying parameters. Run simulations across a range of beta and gamma values (or equivalently, R0 values) to observe how the epidemic peak height, peak timing, and final epidemic size change. Higher R0 produces earlier, taller peaks and larger cumulative attack rates.

6. Guard against numerical artifacts. Verify that S(t) + I(t) + R(t) = N at all output time points. Check that no compartment goes negative. If either condition is violated, reduce the solver tolerance or switch to a more robust integration method.

## Quick Reference

**Core SIR Equations**
- dS/dt = -beta x S x I
- dI/dt = +beta x S x I - gamma x I
- dR/dt = +gamma x I
- Constraint: S + I + R = N (constant)

**Key Formulas**
- Transmission coefficient: beta = k x b (contact rate times transmission probability)
- Recovery rate: gamma = 1/D (D = average infectious duration)
- Basic reproduction number: R0 = beta/gamma = k x b x D
- Effective reproduction number: RE = R0 x (S/N)
- Epidemic threshold: epidemic occurs iff R0 > 1
- Herd immunity threshold: p_c = 1 - 1/R0
- Endemic equilibrium susceptible fraction: S*/N = 1/R0
- Back-calculate R0 from equilibrium: R0 = 1/(S*/N)

**Common R0 Values by Disease**

| Disease | Typical R0 | Herd Immunity Threshold |
|---|---|---|
| Measles | 12-18 | 92-94% |
| Pertussis (whooping cough) | 12-17 | 92-94% |
| Mumps | 10-12 | 90-92% |
| Rubella | 6-7 | 83-86% |
| Diphtheria | 6-7 | 83-86% |
| Smallpox | 5-7 | 80-86% |
| Polio | 5-7 | 80-86% |
| COVID-19 (ancestral) | 2-3 | 50-67% |
| Influenza (seasonal) | 1.5-2 | 33-50% |
| Ebola | 1.5-2.5 | 33-60% |

**Rules of Thumb**
- No analytical solution exists for SIR -- always solve numerically.
- The epidemic peak occurs when S/N = 1/R0.
- Constant rate gamma implies exponentially distributed infectious duration (mean = 1/gamma, with high variance).
- All rate parameters must share the same time unit (per day, per week, etc.).
- Every outflow from one compartment must appear as an inflow to another -- verify balance by summing all equations to zero.
- Start with the simplest model structure; add compartments only when the research question demands it.
- Density-dependent transmission: lambda = beta x I (airborne). Frequency-dependent: lambda = beta x I/N (sexual).
