---
name: basic_epi_modeling
description: This skill should be used when the user asks about "disease burden", "DALYs", "population at risk", "transmission routes", "epidemic vs endemic", "compartmental model basics", "SI SIS SIR model selection", "incidence vs prevalence", "WAIFW matrix", or needs foundational guidance on setting up a new infectious disease model from scratch.
---

# Week 1: Introduction to Disease Modeling

This module covers the foundational steps of infectious disease modeling: quantifying disease burden, characterizing the population at risk through demography and transmission route, selecting between epidemic and endemic frameworks, and building basic compartmental (SI/SIS/SIR) models with balanced equations.

## Quantify Disease Burden Using DALYs

**Context:** Raw mortality counts fail to capture the full impact of a disease because they ignore non-fatal disability and age at death. Disability-Adjusted Life Years (DALYs) integrate both dimensions into a single comparable metric.

**Steps:**

1. Compute Years of Life Lost (YLL) for the disease of interest:
   YLL = number of deaths x standard life expectancy at age of death.
   Use a reference life table (e.g., GBD standard) for the expectancy values. Note that deaths in children under five produce far more YLL per death than deaths in older adults, making age-of-death distribution critical.

2. Compute Years Lived with Disability (YLD). Choose the appropriate formula based on disease dynamics:
   - *Incidence-based* YLD = number of incident cases x disability weight x average case duration. Use this for acute infections where cases resolve (e.g., influenza, cholera) and for forward-looking burden projections.
   - *Prevalence-based* YLD = number of prevalent cases x disability weight. Use this for chronic infections that accumulate in the population (e.g., HIV, hepatitis B) when cross-sectional burden snapshots are needed.

3. Sum the two components: DALY = YLL + YLD. Higher DALY counts indicate greater total burden. Use DALYs to compare diseases with very different mortality-to-morbidity ratios on a common scale (e.g., comparing malaria, which kills quickly, with lymphatic filariasis, which disables chronically).

4. Distinguish incidence from prevalence before selecting burden inputs. Prevalence counts all current cases at a point in time; incidence counts only new cases over a defined period. For chronic infections like HIV, prevalence grows monotonically even after incidence plateaus -- relying on only one metric can be misleading. Report both when characterizing burden.

5. Express burden as a per-capita rate (e.g., DALYs per 1,000 population) to reveal disparities that raw counts obscure, especially when comparing populations of different sizes or age structures.

## Characterize the Population at Risk Through Demography

**Context:** The size and age structure of a population determine the denominator against which disease metrics are measured and shape which diseases dominate the burden profile. Demographic dynamics -- births, deaths, and aging -- must be understood before layering on disease transmission.

**Steps:**

1. Model population change using the discrete-time equation:
   P(t+1) = P(t) + (b - d) x P(t),
   where b is the per-capita birth rate and d is the per-capita death rate. In continuous time this becomes dP/dt = k x P(t), where k = b - d. If k > 0, the population grows exponentially; if k < 0, it declines. This ODE is the structural foundation for all compartmental disease models.

2. Read population pyramids to assess the demographic context. A wide base (many children, few elderly) signals high birth and death rates typical of early epidemiologic transition -- associated with high infectious disease burden. A rectangular or inverted shape signals low birth/death rates and an older population where chronic non-communicable diseases dominate.

3. Identify the stage of epidemiologic transition for the setting. During transition, death rates fall before birth rates, producing rapid population growth and a shift from young-dominated to age-distributed populations. This changes which diseases are epidemiologically important: younger populations face more infectious disease; older populations face more chronic disease.

4. Build age-structured compartmental models when age modifies disease outcomes. Divide the population into age classes (e.g., 0-4, 5-14, 15-49, 50+). Individuals flow between classes at aging rates and exit via age-specific death rates. Encode different contact rates, susceptibility, and case fatality by age group. This is critical for diseases like malaria, measles, and COVID-19 where age strongly modifies transmission and severity.

5. Use the Global Burden of Disease (GBD) Visualization Tool to situate the pathogen of interest. Filter by country, age, sex, year, and metric (mortality, DALYs, YLDs). Identify whether infectious diseases (GBD category I) or non-communicable diseases (category II) dominate. Note data limitations: GBD estimates may be temporally and spatially coarse in low-resource settings -- assess whether more granular surveillance data are needed for model parameterization.

## Identify the Transmission Route and Define the Population at Risk

**Context:** A pathogen's transmission route determines who is exposed, at what rate, and under what conditions. The route dictates whether the population at risk is defined by geography, behavior, age-based contact patterns, or vector ecology.

**Steps:**

1. Classify the transmission route into one of the major categories:
   - *Respiratory/airborne:* droplet or aerosol transmission (e.g., influenza, measles, TB, COVID-19). Population at risk defined by proximity and indoor contact.
   - *Sexual/direct contact:* (e.g., HIV, syphilis, gonorrhea). Population at risk defined by sexual network structure.
   - *Vector-borne:* transmitted via arthropod vectors (e.g., malaria via Anopheles mosquitoes, dengue via Aedes mosquitoes). Population at risk bounded by vector geographic range and seasonal abundance.
   - *Waterborne/fecal-oral:* (e.g., cholera, typhoid, schistosomiasis). Population at risk defined by water source and sanitation infrastructure.
   - *Fomite/environmental:* indirect transmission via contaminated surfaces or soil (e.g., norovirus on surfaces, hookworm in soil).

2. Construct or obtain a Who Acquires Infection From Whom (WAIFW) matrix for directly transmitted infections. Rows and columns represent age groups; cell values represent contact intensity. Empirical contact surveys (e.g., POLYMOD) show a strong diagonal (assortative age mixing) with off-diagonal clusters at parent-child and grandparent-grandchild contacts. Incorporate the WAIFW matrix into transmission models to capture realistic mixing.

3. Select density-dependent or frequency-dependent transmission based on route:
   - *Density-dependent:* contact rate scales with population density. Appropriate for airborne infections where crowding increases face-to-face encounters. The force of infection is proportional to the number of infectious individuals (beta x S x I / area, or simplified as beta x S x I when area is constant).
   - *Frequency-dependent:* contact rate is roughly constant regardless of population size. Appropriate for sexually transmitted infections where partnership behavior does not scale with density. The force of infection is proportional to the fraction infectious (beta x S x I/N).

4. For vector-borne and environmentally transmitted infections, constrain the at-risk population geographically and seasonally. Use vector distribution maps, proximity to environmental reservoirs (e.g., freshwater bodies for schistosomiasis), and seasonal vector abundance data. Update at-risk boundaries as vector ranges shift over time (e.g., dengue range expansion observed since the 1950s).

5. Account for multi-host life cycles when defining transmission parameters. For pathogens cycling through human and non-human hosts (e.g., schistosomiasis: human to snail to human), model each transmission step separately. Identify which ecological factors regulate each stage -- these determine where and when transmission occurs.

6. For sexually transmitted infections, use sexual network structure to identify high-risk subpopulations. Survey-derived contact networks reveal that most individuals form isolated pairs while a connected core drives widespread transmission. Identifying this core component allows more precise definition of the at-risk population and more targeted intervention modeling.

## Choose Between Epidemic and Endemic Modeling Frameworks

**Context:** Not all infectious disease dynamics look the same. A pathogen introduced into a fully susceptible population produces a fundamentally different pattern than one circulating indefinitely. The choice of modeling framework must match the epidemiological situation.

**Steps:**

1. Assess whether the situation is an epidemic (acute outbreak) or endemic (sustained transmission) by examining surveillance data:
   - *Epidemic indicators:* a sharply rising then falling epidemic curve, a largely naive (fully susceptible) population, a novel or re-emerging pathogen, no established seasonal pattern.
   - *Endemic indicators:* sustained or seasonally recurring case counts over years, the pathogen persists in the population indefinitely, partial population immunity, demographic turnover supplying new susceptibles.

2. For epidemic modeling, assume the entire (or a defined subset of the) population is initially susceptible. The model tracks a single outbreak wave: exponential growth, peak, and burnout as susceptibles are depleted. Demographic processes (births, non-disease deaths) can often be ignored because the outbreak timescale is short relative to demographic timescales. Examples: SARS (2003), early-phase pandemic influenza, Ebola outbreaks.

3. For endemic modeling, include demographic inflows and outflows because the pathogen persists across demographic timescales. Incorporate birth of new susceptibles, background mortality, seasonal forcing where relevant, and potentially waning immunity. The model must reach a non-trivial equilibrium where new infections balance recoveries and demographic turnover. Examples: malaria, TB, childhood diseases in pre-vaccine settings.

4. Evaluate whether the disease can be cleared by the host. Infections that are never cleared (e.g., HIV) drive prevalence upward even when incidence declines. Build models where individuals remain in the infected compartment indefinitely (no recovery transition) or transition to a chronic carrier state. Contrast with infections that resolve (e.g., influenza), where individuals exit the infected class via recovery.

## Select the Appropriate Compartmental Model Structure

**Context:** The compartmental model structure must reflect the biological progression of the specific disease. Different diseases require different arrangements of compartments and flow paths.

**Steps:**

1. Map the individual-level disease progression for the pathogen of interest: determine which states an infected person passes through and whether recovery confers immunity.

2. Match the biology to one of the standard model structures:
   - **SI (Susceptible-Infected):** No recovery. Once infected, individuals remain infected permanently. Use for chronic infections with no clearance and no significant mortality from the infection itself on the modeling timescale (e.g., herpes simplex, early HIV modeling).
   - **SIS (Susceptible-Infected-Susceptible):** Recovery occurs but confers no lasting immunity; individuals return to the susceptible class. Use for infections with repeated reinfection (e.g., gonorrhea, chlamydia, many bacterial infections).
   - **SIR (Susceptible-Infected-Recovered):** Recovery confers lasting immunity. Individuals move from S to I to R and do not re-enter S. Use for infections where a single episode produces durable immunity (e.g., measles, mumps, rubella, chickenpox).

3. Verify the chosen structure against known disease biology. Confirm: Does the pathogen clear from the host? Does infection confer lasting immunity? Is there a latent (exposed but not yet infectious) period that warrants an additional E compartment (making it SEIR)? Are there asymptomatic carriers? Each additional biological feature may require extending the basic structure.

4. Start with the simplest structure that captures the essential dynamics. Add complexity (additional compartments, age structure, spatial heterogeneity) only when simpler models fail to reproduce observed patterns or when the research question demands the additional resolution.

## Write and Balance Basic Compartmental Equations

**Context:** Once the compartmental structure is selected, translate it into mathematical equations that track flows between compartments. Every individual leaving one compartment must enter another -- balance is essential for model validity.

**Steps:**

1. Define the state variables. For a standard SIR model: S(t) = number susceptible, I(t) = number infected, R(t) = number recovered, N = S + I + R = total population (constant in a closed population without demography).

2. Decompose the transmission coefficient. Express beta = k x b, where:
   - k = per-capita contact rate (contacts per person per unit time), shaped by population density, mixing patterns, and transmission route.
   - b = probability of transmission per infectious contact, a property of pathogen biology and host susceptibility.
   This decomposition clarifies which factor drives differences when comparing pathogens or settings.

3. Write the continuous-time ODEs for each compartment:
   - dS/dt = -beta x S x I (outflow from S via new infections)
   - dI/dt = +beta x S x I - gamma x I (inflow from S, outflow via recovery)
   - dR/dt = +gamma x I (inflow from I via recovery)
   Where gamma is the recovery rate = 1 / (average infectious duration).

4. Verify balance: sum all equations. dS/dt + dI/dt + dR/dt = -beta x S x I + beta x S x I - gamma x I + gamma x I = 0. Total population is conserved. If the sum is non-zero, there is a bookkeeping error.

5. For discrete-time (difference equation) formulations, express:
   - S(t+1) = S(t) - beta x S(t) x I(t)
   - I(t+1) = I(t) + beta x S(t) x I(t) - gamma x I(t)
   - R(t+1) = R(t) + gamma x I(t)
   Every term subtracted from one compartment appears as an addition to another.

6. To add demography, include birth and death terms:
   - dS/dt = mu x N - beta x S x I - mu x S
   - dI/dt = beta x S x I - gamma x I - mu x I
   - dR/dt = gamma x I - mu x R
   Where mu is the per-capita birth/death rate (assumed equal for a constant population). New births enter the susceptible class. This modification is necessary for endemic modeling where demographic turnover sustains transmission.

7. Interpret the nonlinear transmission term. The beta x S x I term makes the system nonlinear -- the rate of new infections depends on both the number of susceptibles and the number of infectious individuals. This feedback drives the characteristic epidemic curve: early exponential growth (when S is large and I is small but growing), peak (as S depletes), and burnout (when S is too sparse to sustain transmission).

## Quick Reference

**Key Terms**
- **Incidence:** number of new cases arising over a defined time period.
- **Prevalence:** total number of existing cases at a point in time.
- **DALY:** Disability-Adjusted Life Year = YLL + YLD. One DALY = one lost year of healthy life.
- **Epidemiologic transition:** shift from infectious to non-communicable diseases as dominant causes of death, driven by declining mortality and fertility.
- **WAIFW matrix:** Who Acquires Infection From Whom -- an age-structured contact matrix used to parameterize mixing in transmission models.
- **Density-dependent transmission:** contact rate scales with population density (airborne infections).
- **Frequency-dependent transmission:** contact rate independent of population size (sexually transmitted infections).
- **Compartmental model:** population divided into disease-state compartments (S, I, R, etc.) with defined flow rates between them.
- **Epidemic curve:** time series of case counts showing the trajectory of an outbreak.

**Critical Equations**
- DALY = YLL + YLD
- YLL = deaths x life expectancy at age of death
- YLD (incidence) = incident cases x disability weight x duration
- Population growth: dP/dt = (b - d) x P
- SIR system: dS/dt = -beta x S x I; dI/dt = beta x S x I - gamma x I; dR/dt = gamma x I
- Transmission coefficient decomposition: beta = k x b
- Recovery rate: gamma = 1 / average infectious duration

**Common Transmission Route Categories**
| Route | Example Diseases | Contact Type |
|---|---|---|
| Respiratory/airborne | Measles, influenza, TB, COVID-19 | Density-dependent |
| Sexual/direct contact | HIV, gonorrhea, syphilis | Frequency-dependent |
| Vector-borne | Malaria, dengue, Zika | Vector-range bounded |
| Waterborne/fecal-oral | Cholera, typhoid, schistosomiasis | Geographically bounded |
| Fomite/environmental | Norovirus, hookworm | Context-dependent |

**Model Structure Selection**
| Structure | Recovery? | Immunity? | Example Diseases |
|---|---|---|---|
| SI | No | N/A | Herpes, early HIV models |
| SIS | Yes | No | Gonorrhea, chlamydia |
| SIR | Yes | Yes (lasting) | Measles, mumps, rubella |

**Rules of Thumb**
- Epidemic timescale (weeks to months): demography can often be ignored.
- Endemic timescale (years to decades): demography must be included.
- Always verify equation balance: sum of all dX/dt terms must equal zero in a closed population.
- Start with the simplest model structure that captures essential dynamics; add complexity only as needed.
- Report both incidence and prevalence for chronic infections to avoid misleading burden estimates.
