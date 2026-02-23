---
name: sir-elaborations
description: This skill should be used when the user asks about "SEIR model", "MSIR model", "SIRS model", "adding compartments", "age structure in models", "WAIFW matrix", "contact heterogeneity", "20/80 rule", "contact matrices", "calculating R0", "host-vector model", "multi-strain dynamics", "cross-immunity", or needs to extend a basic SIR model with additional complexity.
---

# Week 3: Elaborations of SIR Models

This module covers how to extend basic SIR models to capture real-world complexity: adding compartments for latency, immunity, and carrier states; incorporating age structure and contact heterogeneity; estimating contact rates from data; calculating R0 using four methods; and coupling host-vector and multi-strain dynamics.

## Decide When to Add Compartments

**Context:** The basic SIR framework assumes instant infectiousness upon infection, lifelong immunity after recovery, and a homogeneous infected class. Many diseases violate one or more of these assumptions, requiring additional compartments. Add complexity only when a subgroup differs meaningfully in transmission-relevant parameters (contact rate, susceptibility, infectiousness, or recovery rate).

**Steps:**

1. **Latent period (SIR to SEIR).** If infected individuals undergo a biologically meaningful delay before becoming infectious, insert an Exposed (E) compartment between S and I. Individuals move S to E at rate beta * S * I / N, then E to I at rate alpha = 1/(latent period). Only I, not E, contributes to the force of infection. A longer latent period delays and flattens the epidemic peak without changing R0 or cumulative attack rate. Distinguish the latent period (time to infectiousness) from the incubation period (time to symptoms) -- these differ substantially for some diseases (e.g., chickenpox: ~10-day latent, ~14-day incubation). When the latent period ends before symptoms appear, quarantine based on symptom monitoring will miss a pre-symptomatic transmission window.

2. **Maternal immunity (SIR to MSIR).** If newborns carry transient passive immunity from maternal antibodies, add an M compartment before S. Births enter M; individuals transition M to S at rate delta = 1/(duration of maternal immunity), typically 3-6 months. Use this for diseases where infant epidemiology differs from adult epidemiology (e.g., measles).

3. **Waning immunity (SIR to SIRS).** If post-infection immunity is temporary, add a return flow from R back to S at rate omega = 1/(duration of immunity). This enables recurrent epidemic cycles and a persistent endemic equilibrium. Apply to diseases with documented reinfection (e.g., RSV, rotavirus, pertussis).

4. **Carrier state (add C or A compartment).** If a fraction of infections are asymptomatic or produce chronic carriers with distinct infectiousness, split the infected class into symptomatic (I) and asymptomatic/carrier (A) compartments, each with its own transmission rate and recovery rate. Both may feed into a shared R compartment if post-infection immunity is equivalent.

5. **Vaccination with waning protection (add V compartment).** Route vaccinated susceptibles into a V compartment rather than directly into R. Add a return flow V to S at a rate reflecting waning vaccine efficacy to model booster timing and coverage requirements.

6. **Context-specific compartments.** Add compartments when the physical setting changes transmission parameters -- a Dead (D) compartment for Ebola to capture funeral transmission from infectious corpses, or a Hospitalized (H) compartment to represent reduced community contact. Diagram all compartments and flows explicitly, labeling parameters on each arrow, to make assumptions visible and communicable.

## Incorporate Age Structure

**Context:** Age structure is one of the most common and policy-relevant model elaborations. Contact rates, susceptibility, disease severity, and intervention uptake all vary by age. Age-structured models are essential when evaluating school closures, pediatric vaccination, or any intervention targeting a specific demographic.

**Steps:**

1. Replicate the S-I-R (or S-E-I-R) equations for each age group. For n age groups, this produces n sets of coupled differential equations.

2. Connect age groups through an aging term at rate 1/(time spent in age class). Births enter the youngest S compartment. Because the infectious disease process is typically much faster than aging, simplified models may apply aging transitions only to the susceptible compartment.

3. Construct a "Who Acquires Infection From Whom" (WAIFW) matrix of dimension n x n. Entry beta_ij represents the rate at which a susceptible in group i acquires infection from an infectious individual in group j. The force of infection on group i is lambda_i = sum_j(beta_ij * I_j / N_j).

4. Parameterize the WAIFW matrix from empirical contact data (e.g., the POLYMOD study by Mossong et al.). Strong diagonal values indicate assortative (like-with-like) mixing; off-diagonal values capture cross-age mixing (e.g., parents with young children produce a secondary diagonal band). Common structures:
   - **Assortative mixing:** Dominant diagonal. Most contacts occur within age groups. Appropriate for school-age transmission.
   - **Proportionate mixing:** Contact rates proportional to group activity levels. Assumes no preferential within-group mixing. Tends to overestimate epidemic growth relative to assortative assumptions.
   - **Empirical mixing:** Use measured contact matrices directly. Preferred when data are available.

5. Source demographic data (population size, birth rates, death rates by age group) from national census bureaus or UN World Population Prospects to parameterize aging flows and group sizes.

## Model Contact Heterogeneity

**Context:** The transmission coefficient beta can be decomposed as beta = k * b, where k is the contact rate (number of potentially infectious contacts per unit time) and b is the per-contact transmission probability. Heterogeneity in k drives disproportionate transmission from high-contact individuals and has major implications for intervention targeting.

**Steps:**

1. Decompose beta from empirical data. Estimate b from household or exposure studies (see next section). Estimate k from contact diaries, contact tracing, or infection tracing.

2. Split the population into a high-contact "core" group and a low-contact "noncore" group. Define a mixing matrix on a spectrum from fully assortative (core mixes only with core) to proportionate (mixing proportional to group size).

3. Apply the 20/80 rule: in many infectious disease systems, approximately 20% of the population is responsible for approximately 80% of transmission. This arises from right-skewed (often power-law) contact distributions where a few individuals have very high connectivity.

4. Use network degree distributions to characterize contact heterogeneity. Represent individuals as nodes and contacts as edges in an adjacency matrix. A node's degree equals its number of contacts (k). A normal degree distribution (random network) produces gradual epidemic spread; a power-law degree distribution (scale-free network) produces rapid epidemics even at low average degree.

5. Target interventions to high-contact individuals. Vaccinating or treating the highest-contact 20% reduces the effective reproduction number far more efficiently than random allocation of the same number of doses. Calculate the reduction in Rc under targeted versus random strategies to quantify the efficiency gain for resource-constrained settings.

## Estimate Contact Rates from Data

**Context:** Accurate contact rate estimation is essential for parameterizing transmission models. Three primary empirical methods exist, each with different data requirements and trade-offs. A fourth method -- pathogen genomics -- is emerging but not yet standard.

**Steps:**

1. **Estimate per-contact transmission probability (b) from household exposure studies.** Collect data on the number of infectious exposures each individual experienced and whether infection resulted. Apply the geometric probability model: P(infection after n exposures) = 1 - (1 - b)^n. Fit this relationship to observed infection outcomes across exposure counts to back-calculate b.

2. **Estimate contact rate (k) via infection tracing.** Reconstruct who infected whom from linked clinical cases. This identifies super-spreaders and characterizes the realized transmission network, but misses contacts that did not result in infection, underestimating total k.

3. **Estimate k via contact tracing.** Identify all contacts of each index case, including those who did not become infected. This captures the full contact neighborhood and is commonly available during outbreaks. However, it is labor-intensive and subject to recall bias.

4. **Estimate k via diary studies.** Ask a representative sample of individuals to log all close interactions over a defined period (typically 1-2 days). This produces detailed, age-structured contact matrices independent of disease status. Results may vary across populations, seasons, and settings. The POLYMOD study across eight European countries is the standard reference dataset.

5. **Read and apply a contact matrix.** Contact matrices display contact frequency between age groups as a heat map. Strong diagonal values indicate age-assortative mixing. Use the matrix entries directly as the WAIFW parameters in an age-structured model, scaling by the per-contact transmission probability b.

## Calculate R0 Using Four Methods

**Context:** R0 -- the average number of secondary infections produced by one infectious individual in a fully susceptible population -- is the central summary statistic for transmissibility. Four methods apply in different data contexts: two during early epidemic growth, two at endemic equilibrium.

**Steps:**

1. **From early exponential growth with the serial interval.** During the exponential growth phase, plot case counts on a log scale to linearize the growth curve. Estimate the doubling time. Using the serial interval (average time between successive cases in a transmission chain), calculate the number of new cases per generation. For SIR dynamics: R0 = 1 + r * D, where r is the exponential growth rate and D is the infectious period. For SEIR dynamics with a latent period, use the more general relationship that accounts for the generation time distribution. Typical serial intervals for reference: measles ~11-12 days, influenza ~2-4 days, Ebola ~15 days, COVID-19 ~5-6 days.

2. **By fitting SIR/SEIR to case data.** Fit a compartmental model to observed case counts (and deaths, if available) to estimate beta and gamma, then compute R0 = beta / gamma. For SEIR models, R0 remains beta / gamma because the latent period delays but does not alter the total secondary infections. When disease-induced mortality is significant, use R0 = beta / (gamma + m), where m is the disease-specific death rate. This approach is rapid, assumption-transparent, and suitable for early outbreak assessment.

3. **From equilibrium susceptible fraction.** At endemic equilibrium, the effective reproduction number Re = 1 by definition. Since Re = R0 * (S* / N), rearranging gives R0 = N / S* = 1 / s*, where s* is the proportion susceptible at equilibrium. Estimate s* from seroprevalence surveys. This method requires stable endemic transmission -- not applicable during epidemic phases.

4. **From mean age of first infection.** At equilibrium, higher R0 implies more intense transmission and earlier infection in life. For a rectangular age distribution (low child mortality, typical of developed countries): R0 = L / A, where L is life expectancy and A is the average age of first infection. For a pyramidal age distribution (high mortality throughout life, typical of high-mortality settings): R0 = 1 + L / A. Example: measles with L = 70 years and A = 5 years gives R0 = 14 (rectangular) or R0 = 15 (pyramidal).

## Couple Host-Vector Models

**Context:** Vector-borne diseases (malaria, dengue, Zika, chikungunya) require modeling transmission between two species. The Ross-MacDonald framework provides the foundational structure: separate compartments for hosts and vectors, linked through a shared biting rate.

**Steps:**

1. Define host compartments (typically S_h, I_h, R_h for humans) and vector compartments (S_v, E_v, I_v for mosquitoes -- vectors typically do not recover, remaining infectious for life).

2. Link species through the biting rate a (bites per vector per unit time). Transmission requires two bites: one infectious vector biting a susceptible host (probability b_vh per bite), and one susceptible vector biting an infectious host (probability b_hv per bite).

3. Write the force of infection for each species as dependent on the infectious prevalence in the other. For hosts: lambda_h = a * b_vh * (I_v / N_h). For vectors: lambda_v = a * b_hv * (I_h / N_h).

4. Compute R0 for the coupled system. In the Ross-MacDonald framework: R0 = (m * a^2 * b_vh * b_hv) / (gamma_h * mu_v), where m is the ratio of vectors to hosts and mu_v is the vector death rate. Note R0 is proportional to a^2 (biting rate squared) because transmission requires two biting events.

5. Incorporate the extrinsic incubation period (EIP) -- the time a pathogen develops within the vector before the vector becomes infectious -- as the latent period in the E_v compartment. Because mosquito lifespans are short relative to EIP, vector mortality during the latent period substantially reduces transmission.

## Model Multi-Strain Dynamics

**Context:** Many pathogens circulate as multiple strains or serotypes (dengue has four, influenza reassorts seasonally). Cross-immunity between strains, competitive exclusion, and co-infection create dynamics absent from single-strain models.

**Steps:**

1. Track infection history by strain. For dengue with four serotypes, route individuals through: fully susceptible, primary infection with strain i, recovered from strain i (immune to i, susceptible to others), secondary infection with strain j, and fully immune (after two or more infections).

2. Parameterize cross-immunity. After primary infection with one strain, define a temporary cross-protection period during which susceptibility to other strains is reduced. This temporary immunity wanes at rate phi, returning individuals to partial susceptibility.

3. Model enhanced disease severity for secondary infections if applicable (e.g., antibody-dependent enhancement in dengue). Add a severity-stratified compartment or a multiplier on the case fatality rate for secondary versus primary infections.

4. For influenza-like dynamics with annual strain replacement, model strain competition: the strain with the highest effective R0 in the current immune landscape tends to dominate. Prior immunity from related strains reduces the susceptible pool available to each new variant.

5. For co-infection scenarios, track individuals simultaneously infected with multiple strains. This requires expanding the state space substantially -- for two strains, the compartments include S, I1, I2, I1+I2, R1, R2, R1+R2, and transitions between them.

## Quick Reference

**Model Acronyms:**
- **SIR:** Susceptible-Infectious-Recovered (immediate infectiousness, lifelong immunity)
- **SEIR:** Adds Exposed (latent period before infectiousness)
- **MSIR:** Adds Maternally immune (passive immunity at birth)
- **SIRS:** Waning immunity; R returns to S
- **SIS:** No lasting immunity; I returns directly to S

**WAIFW Matrix Structure:**
An n x n matrix where entry beta_ij is the transmission rate from infectious group j to susceptible group i. Diagonal entries represent within-group transmission; off-diagonal entries represent between-group transmission. Parameterize from contact diary data scaled by per-contact transmission probability.

**R0 Estimation Methods Summary:**

| Method | Data Required | Applicable Phase |
|---|---|---|
| Exponential growth + serial interval | Case time series, serial interval estimate | Early epidemic |
| Model fitting (beta/gamma) | Case time series | Early epidemic |
| Equilibrium susceptible fraction (1/s*) | Seroprevalence survey | Endemic equilibrium |
| Mean age of infection (L/A or 1+L/A) | Age-stratified seroprevalence, life expectancy | Endemic equilibrium |

**Critical Equations:**
- Force of infection: lambda = beta * I / N
- Beta decomposition: beta = k * b
- R0 (SIR): beta / gamma
- R0 (with disease mortality): beta / (gamma + m)
- Geometric infection probability: P(infection) = 1 - (1 - b)^n
- R0 from equilibrium: 1 / s*
- R0 from mean age (rectangular): L / A
- R0 from mean age (pyramidal): 1 + L / A
- Ross-MacDonald R0: (m * a^2 * b_vh * b_hv) / (gamma_h * mu_v)

**Common Serial Intervals:**
Measles ~11-12 days, influenza ~2-4 days, Ebola ~15 days, COVID-19 ~5-6 days, SARS ~8-12 days, smallpox ~13-17 days.

**Rules of Thumb:**
- 20/80 rule: ~20% of hosts responsible for ~80% of transmission in heterogeneous populations
- Herd immunity threshold: 1 - 1/R0
- Proportionate mixing overestimates epidemic growth compared to assortative mixing
- R0 is unchanged by adding a latent period; only epidemic timing changes
- Vector-borne R0 scales with the square of the biting rate
