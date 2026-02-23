---
name: vaccination
description: This skill should be used when the user asks about "vaccination model", "herd immunity threshold", "critical vaccination coverage", "vaccine efficacy in models", "leaky vaccine", "all-or-nothing vaccine", "waning immunity", "pulse vaccination", "ring vaccination", "honeymoon effect", "age-shift effect", "disease eradication", "elimination vs eradication", or needs to incorporate vaccination into a compartmental disease model.
---

# Week 4: Vaccination

This module covers the mathematical foundations of vaccination in disease modeling: deriving herd immunity thresholds, implementing pediatric, mass, and pulse vaccination strategies in compartmental models, handling imperfect vaccines (leaky, all-or-nothing, waning), predicting unintended consequences such as age-shift and honeymoon effects, assessing disease eradicability, and designing targeted strategies like ring vaccination.

## Derive the Critical Vaccination Threshold

**Context:** Elimination does not require vaccinating the entire population. The critical vaccination threshold is the minimum immune fraction needed to reduce the effective reproductive number below one, halting sustained transmission.

**Steps:**

1. Start from the condition for elimination: R_effective < 1. Express R_effective = R0 x S/N, where S/N is the fraction of the population that remains susceptible. At the critical threshold, R_effective = 1.

2. Solve for the minimum immune proportion. Set R0 x (1 - p_c) = 1, where p_c is the fraction immune. Rearranging gives the critical vaccination threshold:

   p_c = 1 - 1/R0

   This tells us that for a disease with R0 = 5, at least 80% of the population must be immune to achieve herd immunity.

3. Adjust for imperfect vaccine efficacy. If the vaccine confers immunity in only a fraction VE of recipients, the required coverage (proportion of the population that must be vaccinated) rises to:

   p_c = (1 - 1/R0) / VE

   For example, with R0 = 10 and VE = 0.85, the required coverage is (1 - 0.1) / 0.85 = 0.9 / 0.85 = 1.06, indicating elimination is unachievable with this vaccine alone -- a critical feasibility check before designing an intervention program.

4. Interpret the relationship between R0 and vaccination burden. Higher R0 demands higher coverage, making highly transmissible diseases far more difficult to control. Note that even sub-threshold coverage still reduces disease burden linearly by shrinking the susceptible pool, even if it does not achieve elimination.

## Model Vaccination Strategies

**Context:** Different vaccination strategies modify the SIR equations in distinct ways. The three principal strategies -- pediatric (routine), mass, and pulse -- each suit different programmatic capacities and epidemiological contexts.

**Steps:**

1. Implement pediatric (routine) vaccination by redirecting a fraction p of newborns from the susceptible class directly into the recovered (immune) class. Modify the SIR equations with demography:

   - dS/dt = mu x N x (1 - p) - beta x S x I - mu x S
   - dI/dt = beta x S x I - gamma x I - mu x I
   - dR/dt = gamma x I + mu x N x p - mu x R

   Here mu is the per-capita birth/death rate. The fraction p of births bypasses the susceptible compartment entirely. Solve for the disease-free equilibrium (I* = 0) to confirm that p_c = 1 - 1/R0 is recovered analytically.

2. Implement mass vaccination by adding a continuous removal term from S to R. Add a vaccination rate rho that transfers susceptible individuals directly to the immune class:

   - dS/dt = mu x N - beta x S x I - mu x S - rho x S
   - dR/dt = gamma x I + rho x S - mu x R

   Solve for the critical mass vaccination rate rho_c by setting I* = 0 at equilibrium. The critical rate depends on both R0 and the demographic turnover rate mu.

3. Implement pulse vaccination as a periodic, discrete intervention. At each pulse (time interval T), vaccinate a fraction f of all current susceptibles, instantly moving them to R. Between pulses, the system follows standard SIR dynamics with demography. Calculate the maximum allowable pulse interval: after each pulse, S is reduced to S x (1 - f). Births then replenish S at rate mu x N. Compute the time for S/N to rise back to the elimination threshold 1/R0. Exceeding this interval risks resurgence between pulses.

4. Add a distinct V (vaccinated) compartment when vaccine-derived immunity differs from natural immunity (in duration, degree, or type). Track V separately from R to allow different waning rates, different susceptibility upon re-exposure, and independent parameterization of natural versus vaccine-induced protection.

## Handle Vaccine Failure Modes

**Context:** Real vaccines are imperfect. The standard threshold formula assumes perfect efficacy. Three failure modes -- leaky, all-or-nothing, and waning -- each require distinct model structures and raise the effective coverage needed for elimination.

**Steps:**

1. Model a leaky vaccine by reducing the per-exposure probability of infection for vaccinated individuals. All vaccinees receive partial protection. Move vaccinated individuals to a V compartment with a reduced force of infection:

   - Force of infection on V: (1 - VE) x beta x I

   Every vaccinated individual faces some residual risk on each exposure. Over time, cumulative exposure means a higher fraction of vaccinated individuals eventually become infected compared to the all-or-nothing model. Recalculate the critical threshold accounting for the reduced but nonzero transmission to V.

2. Model an all-or-nothing vaccine by splitting the vaccinated population into two subgroups at the time of vaccination: a fraction VE who are fully protected (move to R, identical to naturally immune) and a fraction (1 - VE) who receive zero protection (remain functionally in S). This produces a bimodal outcome -- some individuals are completely immune, others completely susceptible -- rather than the uniform partial protection of a leaky vaccine.

3. Model waning immunity by adding a flow from V back to S at rate delta (where 1/delta is the average duration of vaccine-derived immunity):

   - dV/dt = (vaccination inflow) - delta x V - mu x V
   - dS/dt = ... + delta x V

   Recalculate the critical vaccination threshold, which now depends on delta in addition to R0 and mu. Even modest waning rates (e.g., 1/delta = 10 years) substantially increase the coverage required for elimination. For pathogens where natural infection confers longer-lasting immunity than vaccination, assign separate waning rates to R (natural immunity, rate w_R) and V (vaccine immunity, rate w_V).

4. Model waning with boosting for pathogens where re-exposure extends protection. Add a temporary full-protection state that wanes at rate w, but allow re-exposure to circulating pathogen (at rate proportional to the force of infection lambda) to boost individuals back into the protected state. This captures the interaction between natural circulation and vaccine-derived immunity -- reducing circulation via vaccination paradoxically accelerates immunity loss.

## Predict Age-Shift and Honeymoon Effects

**Context:** Partial vaccination coverage produces two counterintuitive consequences that can undermine program goals: the age-shift effect and the honeymoon period. Both emerge naturally from SIR models with vaccination but are easily overlooked without explicit modeling.

**Steps:**

1. Model the age-shift effect using an age-structured SIR framework. As vaccination coverage increases, the force of infection declines. Susceptible individuals who escape both vaccination and childhood infection encounter the pathogen later in life, raising the mean age at first infection. Compute the mean age of infection A as a function of coverage p:

   - Without vaccination: A = 1/lambda (where lambda is the force of infection)
   - As coverage increases, lambda decreases, so A increases

2. Assess whether the age shift is beneficial or harmful by incorporating age-dependent severity. For measles, shifting infections to older children is generally less concerning. For rubella, shifting infections to women of childbearing age increases risk of Congenital Rubella Syndrome (CRS). Compute the burden ratio: CRS cases under vaccination divided by CRS cases without vaccination. At intermediate coverage levels, this ratio can exceed 1.0 -- meaning the vaccination program causes net harm for this specific outcome. This analysis is essential before introducing rubella vaccination in any country.

3. Anticipate the honeymoon period and subsequent resurgence. After vaccination is introduced, expect a sharp initial decline in cases as the susceptible pool contracts. Recognize that susceptibles continue to accumulate silently during this low-incidence period through: births of unvaccinated children, primary vaccine failures, and waning immunity. Once the susceptible fraction exceeds 1/R0, a resurgent epidemic occurs before the system settles into a new, lower equilibrium.

4. Avoid misinterpreting early vaccination success as permanent elimination. Run models forward for multiple decades (at least 3-5 generation times of the susceptible accumulation cycle) to observe the full transient dynamics. Use the time from vaccination introduction to the first resurgent peak as a planning horizon for surveillance intensification.

5. Evaluate coverage thresholds alongside efficacy through sensitivity analysis. Run the model across a range of vaccine coverage levels and efficacy scenarios (best, base, worst case). Low-efficacy vaccines at moderate coverage can produce worse long-run morbidity outcomes than no vaccination because the age-shift effect offsets case reduction -- a result that only emerges from parameter sweeps.

## Assess Disease Eradicability

**Context:** Eradication (global elimination of a pathogen) is the ultimate goal of vaccination but is biologically feasible for only a narrow class of diseases. Assessing eradicability before committing to an eradication program avoids wasting resources on infeasible targets.

**Steps:**

1. Apply the eradicability checklist. Evaluate the pathogen against each criterion:
   - **No animal reservoir:** The pathogen circulates only in humans, so elimination in humans means global elimination. Diseases with zoonotic reservoirs (e.g., yellow fever in primates) cannot be eradicated through human vaccination alone.
   - **Lifelong immunity after infection or vaccination:** Recovery or vaccination produces durable protection, preventing re-susceptibility that would sustain transmission.
   - **No chronic asymptomatic carriage:** All infectious individuals are eventually detectable, enabling case identification and ring vaccination. Pathogens with long-term asymptomatic carriers (e.g., hepatitis B, typhoid) evade surveillance.
   - **Recognizable clinical symptoms:** Cases can be identified without laboratory confirmation in resource-limited settings, enabling rapid case detection and response.
   - **Effective vaccine exists:** A vaccine with sufficiently high efficacy to achieve coverage above p_c is available and deployable.

2. Score candidate diseases. Smallpox satisfied all criteria and was eradicated in 1980. Rinderpest (a cattle disease) was eradicated in 2011. Polio nearly satisfies all criteria but is complicated by vaccine-derived poliovirus and rare chronic excretors. Measles has very high R0 (~12-18), demanding >92% coverage -- logistically challenging but biologically feasible. Apply this checklist to any novel pathogen to rapidly assess eradication feasibility.

3. Distinguish elimination from eradication when setting program targets. Elimination refers to halting transmission within a defined geographic area (e.g., measles elimination in the Americas). Eradication means worldwide elimination with zero cases. Use this distinction to define the geographic scope, timeline, and success criteria for a vaccination program model.

## Model Ring Vaccination and Targeted Strategies

**Context:** When blanket population coverage is infeasible or inefficient, targeted vaccination strategies focus resources on the highest-risk individuals. Ring vaccination -- vaccinating contacts of confirmed cases -- was central to smallpox eradication and has been applied to Ebola outbreaks.

**Steps:**

1. Define the ring vaccination protocol in the model. Upon identification of an index case, vaccinate all known contacts (and potentially contacts of contacts) within a defined time window. The key parameters are: case detection probability, time from symptom onset to case detection, contact tracing completeness, and time from detection to vaccination of contacts.

2. Implement ring vaccination by coupling a surveillance module to the transmission model. At each time step, detected cases trigger vaccination of a fraction of their contacts. The effectiveness depends on: how quickly cases are identified relative to the serial interval, what fraction of contacts can be traced and vaccinated before they become infectious, and whether the vaccine provides post-exposure prophylaxis.

3. Assess when ring vaccination is sufficient versus when mass vaccination is necessary. Ring vaccination is most effective when: R0 is moderate (not extremely high), cases are clinically recognizable (enabling rapid detection), the serial interval is long enough to allow contact tracing, and contact tracing infrastructure exists. For highly transmissible diseases (e.g., measles with R0 > 12), ring vaccination alone is rarely sufficient.

4. Use socioeconomic and geographic heterogeneity to design targeted (non-ring) strategies. Vaccine coverage correlates with GDP at the country level. Parameterize lower-income regions with lower baseline coverage, producing spatial heterogeneity in herd immunity. Target supplementary immunization activities to regions where coverage falls below p_c, rather than applying uniform national campaigns.

## Quick Reference

**Key Terms**
- **Critical vaccination threshold (p_c):** minimum fraction of the population that must be immune to prevent sustained transmission. p_c = 1 - 1/R0.
- **Vaccine efficacy (VE):** probability that vaccination successfully induces protective immunity in a recipient.
- **Herd immunity:** indirect protection of unvaccinated individuals resulting from high population-level immunity reducing the force of infection.
- **Elimination:** cessation of disease transmission within a defined geographic area.
- **Eradication:** permanent global reduction of a disease to zero cases.
- **Honeymoon period:** the transient low-incidence interval after vaccination introduction, before susceptibles accumulate sufficiently to trigger resurgence.
- **Age-shift effect:** increase in mean age at first infection caused by reduced force of infection under partial vaccination coverage.
- **Leaky vaccine:** all recipients receive partial protection (reduced per-exposure infection probability).
- **All-or-nothing vaccine:** a fraction VE of recipients gain full protection; the remainder gain none.
- **Waning vaccine:** vaccine-induced immunity decays over time, returning individuals to susceptibility.
- **Ring vaccination:** targeted vaccination of contacts of confirmed cases, guided by surveillance and contact tracing.

**Critical Equations**
- Critical vaccination threshold: p_c = 1 - 1/R0
- Adjusted for imperfect efficacy: p_c = (1 - 1/R0) / VE
- Pediatric vaccination (modified birth term): dS/dt = mu x N x (1 - p) - beta x S x I - mu x S
- Leaky vaccine force of infection on V: lambda_V = (1 - VE) x beta x I
- Waning immunity flow: dV/dt = ... - delta x V; dS/dt = ... + delta x V

**Herd Immunity Thresholds by Disease**
| Disease | R0 (approx.) | Critical Coverage (p_c) |
|---|---|---|
| Measles | 12-18 | 92-95% |
| Pertussis | 12-17 | 92-94% |
| Diphtheria | 6-7 | 83-86% |
| Rubella | 6-7 | 83-85% |
| Smallpox | 5-7 | 80-85% |
| Polio | 5-7 | 80-86% |
| Mumps | 4-7 | 75-86% |

**Vaccine Failure Mode Comparison**
| Mode | Model Structure | Effect on Threshold |
|---|---|---|
| Leaky | All vaccinees in V with reduced susceptibility | Threshold rises; cumulative exposure erodes protection |
| All-or-nothing | Split vaccinees: fraction VE to R, rest to S | Threshold rises by factor 1/VE |
| Waning | V returns to S at rate delta | Threshold depends on delta, R0, and mu; even slow waning raises threshold substantially |

**Rules of Thumb**
- Even sub-threshold vaccination reduces disease burden linearly -- partial coverage is still valuable.
- Always run age-structured models when disease severity varies by age before introducing a vaccination program.
- Simulate at least 30-50 years post-vaccination to observe honeymoon effects and long-term equilibrium.
- For rubella, intermediate coverage can increase CRS burden -- model before implementing.
- Ring vaccination works best when R0 is moderate, cases are recognizable, and serial intervals allow time for contact tracing.
- Smallpox (eradicated 1980) and rinderpest (eradicated 2011) are the only two diseases successfully eradicated; both satisfied all eradicability criteria.
