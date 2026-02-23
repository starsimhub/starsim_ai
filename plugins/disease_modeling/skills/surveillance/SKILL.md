---
name: surveillance
description: This skill should be used when the user asks about "disease surveillance", "underreporting", "burden of illness pyramid", "reporting lags", "nowcasting", "epidemic forecasting", "forecast evaluation", "genomic epidemiology", "phylogenetic analysis", "molecular clock", "Google Flu Trends", "syndromic surveillance", "sentinel surveillance", or needs to work with surveillance data, forecast disease trajectories, or integrate genomic data with transmission models.
---

# Week 7: Surveillance, Forecasting, and Genomic Epidemiology

This module covers how disease data are collected through surveillance systems, how forecasting models project epidemic trajectories, and how pathogen genomic data inform transmission dynamics. It addresses practical challenges of underreporting, reporting lags, forecast evaluation, and integrating molecular sequence data with compartmental models.

## Estimate True Burden from Reported Data

**Context:** Passive surveillance captures only a fraction of true infections. The burden-of-illness pyramid describes how cases are lost at each step from infection to official report, and multiplier methods can recover estimates closer to true incidence.

**Steps:**

1. Map out the full reporting chain for the disease of interest: infection occurs, patient seeks medical care, clinician orders appropriate diagnostic test, laboratory confirms the pathogen, local health authority receives the report, report is forwarded to national surveillance. At each step a proportion of cases is lost. For foodborne illnesses in the United States, CDC estimates that for every confirmed case of Salmonella reported, approximately 29 actual cases occur in the community.

2. Identify which steps produce the largest losses. In resource-limited settings, care-seeking and laboratory confirmation are typically the bottleneck stages. In high-income settings, clinician testing behavior and reporting compliance dominate. Quantify the probability of completion at each step using data from active surveillance studies or healthcare utilization surveys.

3. Construct a multiplier to scale reported counts toward true incidence. Define the overall multiplier M as the inverse product of step-specific probabilities:
   M = 1 / (p_care x p_test x p_confirm x p_report),
   where each p represents the probability of completing that stage. Apply M to passive surveillance counts: estimated true cases = reported cases x M.

4. Calibrate multipliers using active surveillance data where available. Active surveillance programs (e.g., CDC FoodNet for enteric pathogens) capture cases systematically regardless of patient care-seeking or reporting behavior. Compare active and passive counts over the same population and time period to derive empirical multipliers. Update multipliers periodically as healthcare access and diagnostic practices change.

5. Propagate uncertainty through the multiplier. Each step-specific probability carries a confidence interval. Use Monte Carlo sampling or analytical error propagation to generate a distribution of estimated true cases rather than a single point estimate. Report burden estimates with credible intervals.

## Select the Appropriate Surveillance Type

**Context:** Different surveillance system designs serve different epidemiological purposes. Matching the surveillance type to the modeling question avoids misinterpreting data that were collected for a different objective.

**Steps:**

1. Use **passive (notifiable disease) surveillance** for monitoring long-run endemic trends. Providers report cases to public health authorities through routine channels. Strengths: broad geographic coverage, low cost, long time series. Limitations: substantial underreporting, variable case definitions across jurisdictions, reporting delays. Appropriate model uses: fitting endemic equilibrium parameters, tracking multi-year trends, calibrating transmission models at national scale.

2. Use **active surveillance** when more complete incidence estimates are required. Public health staff systematically contact healthcare facilities, laboratories, or community members to identify cases. Strengths: captures cases missed by passive systems, standardized case ascertainment. Limitations: resource-intensive, typically limited to specific populations or time periods. Appropriate model uses: estimating true incidence for model calibration, deriving underreporting multipliers for passive data.

3. Use **syndromic surveillance** for early outbreak detection, especially in low-resource settings with limited laboratory capacity. Monitor pre-diagnostic indicators (e.g., clusters of fever-with-rash, acute watery diarrhea, acute flaccid paralysis) rather than confirmed diagnoses. Strengths: rapid signal, no lab dependence. Limitations: low specificity (many pathogens share syndromes), high false-positive rate. Appropriate model uses: triggering outbreak investigation models, initializing early epidemic curve fits.

4. Use **sentinel surveillance** for tracking spatial and temporal trends where full population coverage is unavailable. Select a limited number of representative sites (hospitals, clinics, districts) that report consistently. Strengths: higher data quality per site, standardized protocols. Limitations: geographic gaps, results may not be nationally representative. Appropriate model uses: estimating seasonal patterns, parameterizing spatial heterogeneity, age-specific incidence estimation.

5. Before using any surveillance dataset in a model, document the surveillance type, case definition (suspected vs. probable vs. confirmed), geographic scope, temporal resolution, and known biases. Mismatches between surveillance design and model assumptions are a common source of calibration error.

## Account for Reporting Lags and Biases

**Context:** Surveillance data pass through multiple administrative layers -- facility, district, regional, national -- each introducing delays. Real-time models that ignore these lags will systematically underestimate current incidence.

**Steps:**

1. Characterize the reporting delay distribution for the surveillance system. Collect timestamps at each administrative layer to compute the empirical distribution of time from symptom onset (or specimen collection) to appearance in the national database. Typical delays range from days (electronic laboratory reporting) to weeks (paper-based systems in remote areas).

2. Build lag corrections into real-time models. Treat recent data points as incomplete and apply nowcasting methods: estimate the true count for recent time periods by inflating observed counts based on the historical delay distribution. A common approach uses the reporting triangle, where rows represent event dates and columns represent reporting delays, to estimate the fraction of eventual reports already received for each event date.

3. Adjust for case classification differences. Surveillance systems often report suspected, probable, and confirmed cases using different criteria. When fitting models, decide which classification to use and apply it consistently. During fast-moving outbreaks, suspected case counts may be the only timely data available; adjust the model's observation likelihood to account for the lower specificity of suspected case definitions.

4. Correct for day-of-week and holiday effects. Many surveillance systems show artificial periodicity (e.g., lower Monday reporting due to weekend backlogs). Apply seasonal decomposition or day-of-week indicator variables to detrend these artifacts before fitting epidemic models.

5. When comparing data across jurisdictions or time periods, standardize for changes in surveillance effort. Increased testing capacity or a change in reporting policy can create apparent surges or declines unrelated to true transmission. Normalize by tests performed where testing data are available, or flag periods of known surveillance changes as structural breaks.

## Choose a Forecasting Approach

**Context:** Forecasting infectious disease trajectories supports resource allocation, intervention planning, and risk communication. The choice of method depends on data availability, pathogen novelty, forecast horizon, and whether scenario analysis is needed.

**Steps:**

1. Use **expert judgment / back-of-envelope estimation** when data are sparse and rapid guidance is needed. Estimate order-of-magnitude outcomes using basic parameters: R0, population size, and attack rate. For example, expected epidemic size in a fully susceptible population is approximately 1 - 1/R0 (the final size relation for an SIR epidemic). Best suited for the first hours to days of a novel outbreak.

2. Use **statistical / time-series models** when historical surveillance data are available and the goal is short-term prediction. ARIMA, exponential smoothing, and regression models fit patterns in past case counts to project forward. These models do not require mechanistic understanding of transmission but degrade rapidly beyond 2-4 weeks because they cannot anticipate behavioral changes or interventions. For vector-borne diseases, include environmental covariates (rainfall, temperature) as external regressors.

3. Use **mechanistic / compartmental models** when the goal is to capture transmission dynamics, test intervention scenarios, or forecast over longer horizons. SIR/SEIR-type models encode disease natural history and population structure. They require parameterization with natural history data (incubation period, infectious duration, R0) and surveillance counts for calibration. Strengths: scenario analysis (e.g., what if vaccination coverage reaches 80%?), interpretable parameters. Limitations: structural assumptions may be wrong, parameter uncertainty propagates into forecasts.

4. Use **hybrid models** that combine statistical and mechanistic components when flexibility and biological realism are both needed. For example, fit a mechanistic core model but allow a statistical residual process to capture unexplained variation in the data. Ensemble approaches that average predictions across multiple model types often outperform any single model.

5. Match the forecasting approach to the decision context. If the question is "how many hospital beds are needed next week," a statistical model trained on recent admission data may suffice. If the question is "what happens if we close schools for four weeks," only a mechanistic model that encodes school-based contact can answer it.

## Evaluate Forecast Quality

**Context:** Forecasts must be evaluated rigorously to build trust and improve models over time. A forecast that appears to fail may actually reflect a successful intervention that changed the trajectory.

**Steps:**

1. Perform out-of-sample testing. Train the model on data up to time t, generate a forecast for times t+1 through t+h (where h is the forecast horizon), then compare predictions to subsequently observed data. Repeat across multiple time origins to assess average performance rather than a single lucky or unlucky window.

2. Compute point forecast accuracy metrics. Mean Absolute Error (MAE) = (1/n) x sum of |observed_i - predicted_i| measures average magnitude of errors. Use MAE rather than Mean Squared Error when outlier sensitivity is undesirable. For comparing across diseases or scales, use Mean Absolute Percentage Error (MAPE) = (100/n) x sum of |observed_i - predicted_i| / observed_i.

3. Evaluate probabilistic forecast calibration using the Weighted Interval Score (WIS), which generalizes MAE to interval forecasts. WIS penalizes both the width of prediction intervals (rewarding sharpness) and failure to cover the observed value (penalizing miscalibration). Lower WIS indicates better probabilistic forecasts.

4. Assess coverage probability: compute the fraction of observed values that fall within the stated credible intervals. A well-calibrated 95% interval should contain the observed value approximately 95% of the time. Chronic undercoverage indicates overconfident forecasts; chronic overcoverage indicates intervals that are uninformatively wide.

5. Distinguish genuine forecast failure from intervention-altered outcomes. When a forecast predicts a large outbreak but aggressive control measures are deployed and cases remain low, the discrepancy may reflect intervention success rather than model error. Document what interventions occurred during the forecast window. Use counterfactual analysis -- compare the predicted trajectory without intervention to the observed trajectory with intervention -- to estimate intervention impact.

6. Track forecast skill as a function of horizon. Plot error metrics against lead time (1 week ahead, 2 weeks ahead, etc.). Identify the horizon beyond which forecasts perform no better than a naive baseline (e.g., persistence forecast: next week equals this week). Report this effective forecast horizon to decision-makers.

## Integrate Genomic Data with Transmission Models

**Context:** Pathogen genome sequences, now routinely generated through dramatically reduced sequencing costs, contain information about transmission chains, drug resistance, and population connectivity that complements traditional case count data.

**Steps:**

1. Use phylogenetic tree topology to infer transmission dynamics. A ladder-like tree (sequential branching along a main trunk, as seen in influenza) indicates strong immune-driven selection with sequential strain replacement. A bushy, star-shaped tree (as in measles) indicates rapid expansion from a common ancestor with little immune pressure on the genome. Tree shape constrains which transmission models are biologically plausible.

2. Detect drug resistance emergence via selective sweep signatures. When a resistance mutation (e.g., PfCRT K76T for chloroquine-resistant P. falciparum) arises and spreads, it carries flanking genomic regions with it, reducing genetic diversity around the resistance locus. Sequence resistance genes alongside flanking microsatellite markers. A sharp reduction in flanking diversity indicates a recent selective sweep, providing evidence of strong selection for resistance and an estimate of sweep timing.

3. Map genetic variant distributions spatially to infer population connectivity. Plot the geographic distribution of pathogen genotypes or subtypes (e.g., HIV-1 subtypes across sub-Saharan Africa). Clusters of closely related sequences correspond to well-connected human populations. Boundaries between genetic clusters indicate barriers to transmission (geographic, behavioral, or infrastructural) and can define spatial units for compartmental models.

4. Apply molecular clock methods to estimate event timing. Use software such as BEAST (Bayesian Evolutionary Analysis by Sampling Trees) to estimate the time to most recent common ancestor (tMRCA) from dated sequence data. The molecular clock assumes a roughly constant substitution rate over time, calibrated using sequences with known sampling dates. Resulting divergence time estimates can parameterize or validate compartmental model timelines (e.g., when did the outbreak lineage diverge from its ancestor?).

5. Integrate sequence-derived parameters into compartmental models. Use tMRCA estimates to set outbreak start times, phylogenetic cluster assignments to define subpopulations, and substitution rate estimates to cross-validate generation time assumptions. Conversely, use epidemiological case count data to root and calibrate phylogenetic trees when sampling dates alone provide insufficient temporal resolution.

6. Assess whether whole-genome or targeted sequencing is appropriate. For small viral genomes (influenza at ~13 kb, SARS-CoV-2 at ~30 kb), whole-genome sequencing is standard and cost-effective. For large genomes (P. falciparum at ~23 Mb), target specific informative loci, amplicons, or known resistance genes. For pathogens that diversify primarily through recombination (e.g., malaria with its obligate sexual cycle), exclude recombinant segments or use recombination-aware phylogenetic methods, as standard tree-building algorithms assume clonal inheritance and produce misleading results with recombinant data.

## Assess Hybrid Surveillance Data Sources

**Context:** Non-traditional data streams such as internet search queries, social media posts, and electronic health records can supplement official surveillance but carry unique biases that require careful validation before use in models.

**Steps:**

1. Evaluate internet search trend data (e.g., Google Trends, Wikipedia page views) as supplementary signals. These data are available in near-real-time and can detect population-level health-seeking behavior before official case reports. However, search behavior is driven by media coverage and public attention as well as illness. Google Flu Trends famously overpredicted the 2012-2013 US influenza season by approximately 2x, largely because media coverage of a severe season drove search volumes beyond what illness alone would produce. Treat search data as a noisy, biased proxy that requires recalibration each season.

2. Assess social media signals (Twitter/X, Facebook, health forums) for syndromic indicators. Natural language processing can extract symptom mentions and geolocate them. Limitations: user demographics are not representative of the general population, signal-to-noise ratio is low, and platform algorithm changes can alter data availability. Use social media data only as a complement to -- never a replacement for -- traditional surveillance.

3. Leverage electronic health records (EHR) and insurance claims data for near-real-time syndromic surveillance. ICD-coded diagnoses, prescription fills (e.g., antiviral prescriptions as a flu proxy), and emergency department chief complaints provide structured, population-level health data. Advantages over search data: generated by clinical encounters rather than media-driven behavior. Limitations: restricted access, variable coding practices, lag from encounter to data availability.

4. Validate any non-traditional data source statistically before incorporating it into a model. Compute correlation with gold-standard surveillance data across multiple seasons or outbreak cycles. Test for temporal stability: a data source that correlates well in one season may fail in the next due to behavioral or algorithmic shifts. Use prospective (out-of-sample) rather than retrospective (in-sample) validation to avoid overfitting.

5. When incorporating non-traditional data, use it to improve nowcasting (estimating current incidence) rather than medium-term forecasting. These signals are most valuable in the 1-2 week window before official surveillance data become available. Beyond that window, their added predictive value over traditional data diminishes.

## Quick Reference

**Surveillance Type Comparison**

| Type | Coverage | Completeness | Cost | Timeliness | Best Model Use |
|---|---|---|---|---|---|
| Passive/notifiable | Broad | Low (pyramid losses) | Low | Slow (reporting lags) | Endemic trend monitoring |
| Active | Targeted | High | High | Moderate | True incidence estimation |
| Syndromic | Variable | Moderate (low specificity) | Low-moderate | Fast | Early outbreak detection |
| Sentinel | Limited sites | High per site | Moderate | Moderate | Spatial/temporal trends |

**Forecasting Method Decision Guide**

| Factor | Expert/Envelope | Statistical | Mechanistic | Hybrid |
|---|---|---|---|---|
| Data required | Minimal | Historical time series | Natural history + surveillance | Both |
| Scenario analysis | No | No | Yes | Partial |
| Forecast horizon | Hours-days | Days-weeks | Weeks-months | Weeks-months |
| Novel pathogen | Yes (if R0 known) | No (needs history) | Yes | Yes |
| Computational cost | Negligible | Low | Moderate-high | High |

**Key Forecast Evaluation Metrics**
- MAE = (1/n) x sum(|observed - predicted|): average absolute error for point forecasts.
- WIS (Weighted Interval Score): penalizes both interval width and failure to cover the truth; standard metric for probabilistic forecasts.
- Coverage probability: fraction of observations within stated credible intervals (target: nominal level, e.g., 95%).
- Effective forecast horizon: lead time beyond which skill drops to naive-baseline level.

**Key Genomic Epidemiology Terms**
- **Phylogenetic tree:** branching diagram showing evolutionary relationships among pathogen sequences.
- **Molecular clock:** assumption of roughly constant nucleotide substitution rate, enabling divergence time estimation.
- **tMRCA:** time to most recent common ancestor, estimated from dated sequences using Bayesian methods (e.g., BEAST).
- **Selective sweep:** rapid fixation of an advantageous mutation (e.g., drug resistance) that reduces flanking genetic diversity.
- **Coalescent theory:** mathematical framework relating genealogical tree shape to population-level processes (population size changes, migration, selection).
- **Recombination:** exchange of genetic material between co-infecting lineages; violates standard phylogenetic tree assumptions; prevalent in malaria, HIV, influenza (reassortment).

**Rules of Thumb**
- Passive surveillance typically captures 1/10 to 1/50 of true infections, depending on disease and setting.
- Forecast accuracy degrades with horizon; evaluate skill at each lead time separately.
- A forecast that overestimates an outbreak may reflect successful intervention, not model failure.
- Google Flu Trends failure (2012-2013): media-driven search behavior inflated estimates by ~2x -- validate non-traditional data sources prospectively.
- Ladder-like phylogenetic trees suggest immune-driven selection; star-shaped trees suggest rapid clonal expansion.
- For recombinant pathogens, restrict phylogenetic analysis to non-recombining genomic regions or use specialized methods.
