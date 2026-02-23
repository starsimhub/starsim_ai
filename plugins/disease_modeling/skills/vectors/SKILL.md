---
name: vectors
description: This skill should be used when the user asks about "vector-borne disease model", "Ross-MacDonald model", "malaria model", "mosquito transmission", "biting rate", "extrinsic incubation period", "waterborne disease model", "SIWR model", "cholera model", "environmental reservoir", "multi-strain model", "cross-immunity", "dengue serotypes", "antigenic diversity", "structural uncertainty", or needs to model pathogens with vectors, environmental reservoirs, or multiple strains.
---

# Week 6: Vectors, Environmental Transmission, and Multi-Strain Pathogens

This module covers modeling pathogens whose transmission depends on intermediate vectors, environmental reservoirs, or antigenic diversity. It builds the Ross-MacDonald framework for vector-borne diseases, extends compartmental models to include waterborne environmental pathways, introduces multi-strain dynamics with cross-immunity, and addresses how parameter and structural uncertainty propagate through these more complex model architectures.

## Build a Ross-MacDonald Vector-Borne Model

**Context:** Vector-borne pathogens cycle between host and vector populations, requiring separate compartmental structures for each. The Ross-MacDonald model, originally developed for malaria, captures this two-population transmission loop and remains the foundation for vector-borne disease modeling.

**Steps:**

1. Create separate compartmental structures for hosts and vectors. Use SI or SIR compartments for the human population and SI or SEI compartments for the mosquito population. Mosquitoes do not recover from infection (once infectious, they remain so for life), so no R compartment is needed on the vector side.

2. Link the two populations through a shared biting rate parameter *a*, defined as the number of bites per mosquito per unit time. This single parameter governs contact in both transmission directions -- every bite is simultaneously an opportunity for mosquito-to-human and human-to-mosquito transmission.

3. Define asymmetric transmission probabilities for each direction:
   - *b* = probability that a bite from an infectious mosquito infects a susceptible human.
   - *c* = probability that a bite on an infectious human infects a susceptible mosquito.
   Separate these parameters rather than using a single transmission coefficient, because the biological mechanisms differ: *b* involves sporozoite injection and liver-stage establishment, while *c* involves gametocyte uptake and mosquito midgut invasion.

4. Introduce the mosquito-to-human ratio *m* = M/N, where M is the total mosquito population and N is the total human population. This ratio scales transmission intensity by vector abundance. In high-endemicity malaria settings, *m* can exceed 100; in marginal transmission zones, *m* may be close to 1.

5. Write the force of infection on humans as lambda_h = m * a * b * (proportion of mosquitoes infectious). Write the force of infection on mosquitoes as lambda_m = a * c * (proportion of humans infectious). Note that the biting rate *a* appears in both expressions -- this is the source of its squared contribution to R0.

6. Construct the coupled ODE system. For humans (SIS or SIR): dS_h/dt = -lambda_h * S_h + r * I_h (for SIS) or dS_h/dt = -lambda_h * S_h (for SIR), where r is the human recovery rate. For mosquitoes (SI): dS_m/dt = mu * M - a * c * (I_h/N) * S_m - mu * S_m and dI_m/dt = a * c * (I_h/N) * S_m - mu * I_m, where mu is the mosquito death rate and mu * M represents new (uninfected) mosquito recruitment.

## Incorporate Vector Survival into the Force of Infection

**Context:** Mosquitoes must survive long enough after acquiring infection for the parasite to complete its extrinsic incubation period (EIP) before they can transmit. Because mosquito lifespans are short relative to the EIP, vector survival is a critical bottleneck in transmission.

**Steps:**

1. Define the extrinsic incubation period tau as the time required for the parasite to develop within the mosquito to the point of transmissibility. For *Plasmodium falciparum*, tau is typically 10-14 days depending on temperature.

2. Assume constant mosquito mortality at rate mu per day. Under this assumption, the probability that a mosquito survives from the moment of infection to the end of the EIP is e^(-mu * tau). This exponential survival term represents the fraction of newly infected mosquitoes that live long enough to become infectious.

3. Incorporate this survival probability into the force of infection. The effective rate at which mosquitoes transition from exposed to infectious is not instantaneous but filtered by survival: only the fraction e^(-mu * tau) of infected mosquitoes ever transmit.

4. Recognize the biological interpretation: if the average mosquito lifespan is 1/mu = 10 days and the EIP is tau = 12 days, then e^(-mu * tau) = e^(-1.2) = 0.30 -- only 30% of infected mosquitoes survive to transmit. Increasing mu by even a small amount (e.g., from 0.10 to 0.12 per day) drops this survival fraction substantially due to the exponential relationship. This is why interventions that increase mosquito mortality are disproportionately effective.

## Interpret R0 Non-Linearities for Intervention Prioritization

**Context:** The Ross-MacDonald R0 formula contains non-linear parameter dependencies that create asymmetric leverage points for interventions. Understanding these non-linearities is essential for allocating control resources efficiently.

**Steps:**

1. Write out the Ross-MacDonald R0 formula:
   R0 = (m * a^2 * b * c * e^(-mu * tau)) / (r * mu)
   where m = mosquito-to-human ratio, a = biting rate, b = mosquito-to-human transmission probability, c = human-to-mosquito transmission probability, mu = mosquito death rate, tau = extrinsic incubation period, and r = human recovery rate.

2. Identify the squared biting rate term. The parameter *a* appears squared because it governs contact in both transmission directions (human-to-mosquito and mosquito-to-human). A 50% reduction in biting rate reduces R0 by 75% (0.5^2 = 0.25). This makes insecticide-treated bed nets (ITNs), which reduce biting rate *a*, highly cost-effective: they simultaneously lower the probability of a bite occurring in both transmission directions.

3. Identify the exponential mortality term. The mosquito death rate mu appears both in the denominator (linearly) and in the exponent (e^(-mu * tau)). Small increases in mu produce compounding reductions in R0 through both pathways. Indoor residual spraying (IRS) targets this parameter by increasing mosquito mortality after blood-feeding. For malaria, this double sensitivity to mu means IRS can achieve substantial R0 reductions even with imperfect coverage.

4. Map interventions to their target parameters:
   - ITNs: reduce biting rate *a* (squared effect on R0).
   - IRS: increase mosquito death rate mu (exponential effect on R0).
   - Larviciding and environmental management: reduce mosquito density, lowering the ratio *m* (linear effect on R0).
   - Drugs (treatment): increase recovery rate r, reducing the infectious period (linear effect on R0).
   Rank interventions by the non-linearity of their target parameter, not by their biological plausibility alone.

5. Recognize that malaria R0 is highly context-dependent. Unlike directly transmitted infections where R0 is relatively constrained (e.g., measles R0 = 12-18), malaria R0 can range from less than 1 in marginal transmission settings to over 1000 in hyperendemic areas, because long infectious durations, high biting exposure, and large mosquito-to-human ratios can each multiplicatively inflate R0.

## Model Environmental Reservoirs for Waterborne Pathogens

**Context:** Waterborne pathogens like cholera transmit through contaminated environmental reservoirs rather than (or in addition to) direct person-to-person contact. Standard SIR models omit this pathway; the SIWR extension explicitly represents pathogen persistence in the environment.

**Steps:**

1. Add a water/environment compartment W (or B, for bacterial concentration) to the standard SIR framework. W tracks pathogen concentration in the environmental reservoir (e.g., cells per mL in water sources). The resulting SIWR model has four state variables: S, I, W, R.

2. Write the additional ODE for the environmental compartment:
   dW/dt = xi * I - delta * W
   where xi is the shedding rate (pathogen units shed per infectious individual per unit time) and delta is the environmental decay rate of the pathogen. For cholera, a single diarrheal episode can increase environmental bacterial load by a factor of one million, making xi a dominant driver.

3. Define the environment-to-human force of infection using a dose-response function. A common formulation is:
   lambda_env = beta_W * W / (W + kappa)
   where beta_W is the maximum contact rate with contaminated water and kappa is the pathogen concentration that infects 50% of exposed individuals (the ID50). This saturating (Hill-type) function captures the dose-response biology: low concentrations produce few infections; above kappa, additional concentration yields diminishing marginal increases in infection probability.

4. Combine direct and indirect transmission in the total force of infection:
   lambda_total = beta_D * I/N + beta_W * W / (W + kappa)
   where beta_D governs direct person-to-person transmission and the second term governs environmental transmission. This allows the model to represent both pathways and assess their relative contributions.

5. Derive R0 for the SIWR model by collecting transmission-enhancing parameters in the numerator and transmission-reducing parameters in the denominator. The environmental pathway introduces additional parameters (shedding rate, contact rate with water, pathogen survival) that can substantially increase R0 relative to a direct-transmission-only model. Fitting both an SIR and an SIWR model to the same cholera epidemic curve has produced R0 estimates of 4.5 versus 9.3 -- a difference that translates to vaccination coverage targets of 78% versus 89%.

6. Account for parameter uncertainty in environmental transmission. Key cholera parameters span orders of magnitude: vibrio survival in water ranges from 3 to 41 days, contact rates with the reservoir range from 10^(-5) to 1, shedding rates from 0.01 to 10, and ID50 from 10^2 to 10^6 organisms. Propagate these ranges through the R0 formula to characterize the resulting uncertainty in R0 and any derived policy thresholds.

7. Apply R0-derived vaccination thresholds (1 - 1/R0) spatially rather than uniformly. Cholera transmission is highly heterogeneous due to unequal access to sanitation and clean water. Estimate local R0 values for distinct areas and direct vaccines toward high-transmission zones rather than distributing uniformly across the population, which wastes doses in low-risk areas.

## Handle Multi-Strain Dynamics

**Context:** Many pathogens circulate as multiple co-existing strains (e.g., dengue with 4 serotypes, influenza with continuous antigenic drift, *S. pneumoniae* with 90+ serotypes). Infection with one strain may confer partial or no protection against others, requiring models that track strain-specific immunity.

**Steps:**

1. Extend the SIR framework to multiple strains by tracking infection-order pathways. For two strains (A and B), create compartments for every combination of strain-specific immunity: susceptible to both, infected with A, recovered from A (immune to A, susceptible to B), infected with B after recovery from A, recovered from both, and the symmetric pathway through B first then A. Both pathways to dual immunity must be modeled separately because susceptibility to each strain depends on the sequence of prior exposures.

2. Reduce compartmental complexity by indexing on remaining susceptibility. Instead of tracing all possible routes through the model, define compartments by which strains a host is still susceptible to. For *n* strains, enumerate all 2^n subsets of strains a host can remain susceptible to. This approach cuts compartment count substantially compared to tracking full exposure histories, though it still grows exponentially with strain number.

3. Incorporate cross-immunity using a sigma parameter. In the Gog-Grenfell formulation, modify the force of infection for strain *i* by multiplying by sigma(i,j), which gives the probability that prior infection with strain *j* still leaves the host susceptible to strain *i*. When sigma = 0, prior infection confers complete cross-protection; when sigma = 1, there is no cross-immunity. Place strains in an antigenic space where proximity determines cross-protection strength.

4. Model strain competition through host availability. Even without immunological cross-reactivity (sigma = 1), strains compete because a host currently infected with one strain is temporarily unavailable to others. This demographic interference is sufficient to drive competitive exclusion or coexistence depending on strain-specific R0 values and recovery rates. Add cross-immunity (sigma < 1) to introduce immunological competition that can produce sequential strain replacement dynamics, as observed in seasonal influenza.

5. For multi-locus antigenic diversity (e.g., malaria, meningococcus), use strain-suppression logic. When pathogens have multiple independent antigenic loci (e.g., two loci each with two variants, yielding four possible strain combinations), strains with entirely non-overlapping antigen combinations tend to dominate at equilibrium while intermediate strains sharing one locus with each dominant type are suppressed.

6. Apply multi-strain thinking to dengue as a concrete example. Dengue has 4 serotypes; primary infection with one serotype confers lifelong immunity to that serotype but only transient cross-protection against the other three. Secondary infection with a different serotype carries elevated risk of severe disease through antibody-dependent enhancement (ADE). Model this by setting sigma close to 1 (minimal cross-protection) and adding a severity multiplier for secondary infections, then evaluate how vaccination interacts with natural exposure history.

7. Reinterpret aggregate epidemiological metrics under multi-strain dynamics. A low mean age of first infection, which in a single-strain model implies a high R0, may instead reflect many co-circulating strains each with a moderate individual R0. Decompose the overall force of infection into strain-specific components using age-seroprevalence curves stratified by strain to disentangle these contributions.

## Propagate Parameter and Structural Uncertainty

**Context:** Vector-borne, environmentally transmitted, and multi-strain models introduce more parameters than simple SIR models, many of which are poorly constrained empirically. Both parameter values and model structure itself become significant sources of uncertainty.

**Steps:**

1. Identify parameters with wide empirical ranges. For vector-borne models: mosquito lifespan, biting rate, and EIP vary with temperature, humidity, and species. For waterborne models: pathogen environmental survival, shedding rates, and dose-response thresholds span orders of magnitude. Compile published ranges for each parameter from the literature.

2. Propagate parameter uncertainty through R0 and model outputs. Calculate R0 at the extremes of each parameter's range while holding others at baseline values, then at joint extremes. Report the resulting range of R0 and derived quantities (vaccination thresholds, intervention impact estimates) to communicate how parameter uncertainty translates into decision-relevant uncertainty.

3. Compare model structures using the same data. Fit both simpler (SIR) and more complex (SIWR, multi-strain) models to the same epidemic time series. When models produce substantially different R0 estimates or intervention projections from the same data, the divergence quantifies structural uncertainty -- the component of uncertainty that cannot be resolved by better parameter estimation alone.

4. Use ensemble or multi-model approaches when structural uncertainty is large. When different plausible model structures produce divergent predictions for the same intervention scenario (e.g., 21% vs. 95% prevalence reduction for the same mass drug administration strategy in malaria models), report the range of predictions across models rather than selecting a single "best" model. This is especially important for policy communications.

5. Prefer transparent, low-complexity models when ecological and environmental heterogeneities make specific predictions unreliable. A simple model that clearly reveals how parameters relate to outcomes (e.g., how mu affects R0 through the exponential survival term) may be more useful for intervention planning than a high-complexity model that generates specific but poorly reproducible numerical forecasts.

## Quick Reference

**Key Terms**
- **Ross-MacDonald model:** two-population (host-vector) compartmental framework for vector-borne disease transmission.
- **Biting rate (a):** number of bites per mosquito per unit time; squared in R0 because it governs both transmission directions.
- **Mosquito-to-human ratio (m):** M/N; scales transmission intensity by vector abundance.
- **Extrinsic incubation period (tau):** time for parasite development within the vector to the point of transmissibility.
- **SIWR model:** SIR extension with a water/environment compartment for indirect transmission.
- **Dose-response (kappa):** pathogen concentration that infects 50% of exposed individuals (ID50).
- **Cross-immunity (sigma):** probability that prior infection with one strain leaves a host susceptible to another; sigma = 0 is full cross-protection, sigma = 1 is none.
- **Structural uncertainty:** divergence in model predictions arising from differences in model structure rather than parameter values.

**Critical Equations**
- Ross-MacDonald R0: R0 = m * a^2 * b * c * e^(-mu * tau) / (r * mu)
- Mosquito survival to transmit: P(survive EIP) = e^(-mu * tau)
- SIWR environmental dynamics: dW/dt = xi * I - delta * W
- Environmental force of infection: lambda = beta_W * W / (W + kappa)
- Vaccination threshold: p_c = 1 - 1/R0

**Common Parameter Values and Rules of Thumb**
| Parameter | Typical Range | Notes |
|---|---|---|
| Malaria R0 | <1 to >1000 | Highly context-dependent; driven by local ecology |
| Cholera R0 | ~3 (wide uncertainty) | Sensitive to model structure (SIR vs. SIWR) |
| Dengue serotypes | 4 | ADE makes secondary infections more severe |
| Plasmodium EIP (tau) | 10-14 days | Temperature-dependent |
| Mosquito lifespan (1/mu) | 7-30 days | Species- and environment-dependent |
| Vibrio survival in water | 3-41 days | Drives environmental transmission persistence |
| Cholera ID50 (kappa) | 10^2 to 10^6 organisms | Spans four orders of magnitude |

**Intervention-Parameter Mapping**
| Intervention | Target Parameter | Effect on R0 |
|---|---|---|
| Insecticide-treated nets (ITNs) | Biting rate *a* | Quadratic reduction (a^2) |
| Indoor residual spraying (IRS) | Mosquito death rate mu | Exponential reduction (e^(-mu*tau)) + linear (1/mu) |
| Larviciding / environmental management | Mosquito ratio *m* | Linear reduction |
| Drug treatment | Recovery rate *r* | Linear reduction (1/r) |
| Water/sanitation infrastructure | Contact rate beta_W, decay delta | Reduces environmental transmission pathway |
| Vaccination | Susceptible fraction | Threshold: 1 - 1/R0 |
