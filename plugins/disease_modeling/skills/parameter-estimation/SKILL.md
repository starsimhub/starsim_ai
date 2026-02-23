---
name: parameter-estimation
description: This skill should be used when the user asks about "fitting a disease model", "parameter estimation", "least squares fitting", "maximum likelihood estimation", "MLE", "Bayesian inference for epidemiology", "estimating R0 from data", "chain binomial model", "TSIR model", "time series SIR", "model calibration", "stochastic epidemic model", "measurement error", "demographic stochasticity", or needs to connect a compartmental model to observed data.
---

# Week 5: Parameter Estimation

This module covers the statistical methods used to connect infectious disease models to observed data: fitting models via least squares and maximum likelihood, estimating the basic reproduction number (R0) from multiple data types, accounting for variability, and building stochastic and time-series models for outbreak and endemic disease data.

## Follow the Model Fitting Workflow

**Context:** Parameter estimation is not a single calculation but a structured process. Each step constrains the next, and skipping steps leads to unreliable estimates that cannot support public health decisions.

**Steps:**

1. Formulate a precise epidemiological question before touching data. The question determines which parameters need estimation (e.g., "What is R0 for this outbreak?" vs. "How does transmission vary seasonally?").

2. Choose a model that can answer the question. Match model structure to the disease biology and available data -- an SIR model for an immunizing infection, a chain binomial for discrete-generation outbreak data, a TSIR model for long endemic time series.

3. Identify sources of variability in the system (measurement error, demographic stochasticity, environmental stochasticity -- detailed in a later section) and select a statistical framework that accounts for the relevant sources.

4. Fit the model to data using an appropriate method (least squares for simple cases, maximum likelihood for probabilistic models, Bayesian methods when prior information is available).

5. Evaluate the fit both visually (overlay model predictions on observed data) and numerically (goodness-of-fit statistics, residual patterns). Systematic deviations indicate model misspecification.

6. Quantify uncertainty around parameter estimates by constructing confidence intervals (frequentist) or credible intervals (Bayesian). Point estimates without uncertainty ranges are insufficient for decision-making.

## Fit Models Using Least Squares

**Context:** Least squares is the most intuitive fitting method. It requires no distributional assumptions about the data and works well when residuals are approximately symmetric and homoscedastic.

**Steps:**

1. Compute the residual at each data point: residual_i = observed_i - predicted_i. The predicted value comes from the model evaluated at the current parameter guess.

2. Square each residual and sum across all data points to obtain the sum of squared residuals (SSR): SSR = sum of (observed_i - predicted_i)^2. Squaring ensures positive and negative deviations do not cancel.

3. Search over the parameter space to find values that minimize SSR. For an SIR model, vary R0 and outbreak start time systematically (grid search) or use a numerical optimizer (e.g., Nelder-Mead, gradient descent).

4. Assess fit visually by plotting the best-fit model curve against the observed epidemic curve. Check that the model captures peak timing, peak height, and overall shape. Numerical SSR alone can mask poor fit if errors concentrate in critical regions.

5. Examine residuals for structure. Randomly scattered residuals suggest a good fit; systematic patterns (e.g., consistent underprediction early, overprediction late) indicate missing model features.

6. Note the limitations: least squares treats all data points equally, does not naturally produce probability-based confidence intervals, and can perform poorly with count data that have variance proportional to the mean.

## Fit Models Using Maximum Likelihood Estimation

**Context:** Maximum likelihood estimation (MLE) explicitly models the data-generating process by specifying a probability distribution for the observations. This produces both point estimates and a natural framework for uncertainty quantification.

**Steps:**

1. Select a probability distribution that matches the data type. Common choices for epidemiological data:
   - *Poisson:* for count data (e.g., weekly case counts) where events are rare relative to the population. Variance equals the mean.
   - *Binomial:* for infection outcomes in a fixed susceptible pool (e.g., k infections out of n susceptibles). Appropriate when the denominator is known.
   - *Negative binomial:* for overdispersed count data where variance exceeds the mean, common in real surveillance data with clustering or heterogeneity.
   - *Normal (Gaussian):* for continuous measurements or when sample sizes are large enough for central limit theorem approximations.

2. Write the likelihood function. For independent observations, the likelihood L(theta) equals the product of the probability of each observation given parameter vector theta: L(theta) = product of P(data_i | theta). In practice, work with the log-likelihood to convert products to sums and avoid numerical underflow: log L(theta) = sum of log P(data_i | theta).

3. For simple cases, solve analytically. Example: for binomial data (k successes in n trials), the MLE of the probability parameter is p_hat = k/n. This closed-form solution is the exception rather than the rule.

4. For complex models, use numerical optimization to find the parameter values that maximize the log-likelihood. Supply the optimizer with the log-likelihood function, initial parameter guesses, and parameter bounds. Common optimizers include Nelder-Mead (derivative-free), L-BFGS-B (bounded gradient-based), and differential evolution (global search).

5. Improve convergence by: (a) choosing reasonable starting values from prior knowledge or a coarse grid search, (b) reparameterizing to remove constraints (e.g., log-transform positive parameters), (c) scaling parameters to similar magnitudes, and (d) running from multiple starting points to check for local optima.

6. Construct confidence intervals from the likelihood surface. The profile likelihood method holds one parameter fixed at a range of values while optimizing over all others; the 95% confidence interval includes all parameter values where the log-likelihood is within 1.92 units (chi-squared critical value / 2) of the maximum.

## Choose Between Frequentist and Bayesian Inference

**Context:** Frequentist and Bayesian approaches answer different questions about parameters. The choice affects how results are interpreted and communicated.

**Steps:**

1. Apply frequentist inference when no prior information about parameters is available or when objectivity is paramount. The procedure treats parameters as fixed unknown constants and uses the likelihood alone. The output is a point estimate (MLE) plus a 95% confidence interval, interpreted as: if the estimation procedure were repeated on many independent datasets, 95% of the resulting intervals would contain the true parameter value.

2. Apply Bayesian inference when prior knowledge about parameters exists and should be formally incorporated. Combine a prior distribution P(theta) with the likelihood P(data | theta) via Bayes' theorem: P(theta | data) is proportional to P(data | theta) x P(theta). The output is a posterior distribution over parameters.

3. Specify priors carefully. Use informative priors when prior studies provide reliable parameter ranges (e.g., serial interval estimates from contact tracing). Use weakly informative or diffuse priors when prior knowledge is limited -- these regularize the estimate without dominating the data.

4. Summarize the posterior distribution by reporting the posterior median or mean as a point estimate, and the 95% credible interval (the interval containing 95% of the posterior probability). Unlike frequentist confidence intervals, a Bayesian credible interval has a direct probabilistic interpretation: there is a 95% probability the parameter lies in this interval, given the data and prior.

5. Prefer Bayesian approaches when: sample sizes are small (priors stabilize estimates), multiple data sources must be combined sequentially (posterior from one analysis becomes the prior for the next), or the goal is to produce posterior predictive distributions for forecasting.

## Estimate R0 from Data Using Four Methods

**Context:** The basic reproduction number R0 can be estimated from different data types without fitting a full dynamic model. Each method has distinct data requirements and assumptions.

**Steps:**

1. **From endemic equilibrium.** At equilibrium the effective reproduction number equals 1, so R0 = 1/S*, where S* is the proportion of the population that is susceptible. Obtain S* from serological surveys measuring the fraction without immunity. This method requires the disease to be at a true steady state.

2. **From the mean age of infection.** Apply R0 ~ L/A, where L is host life expectancy and A is the mean age of first infection. Estimate A from age-stratified seroprevalence data (the age at which ~50% have been infected). This approximation works best for endemic, fully immunizing childhood infections with rectangular age distributions. For populations with a pyramidal age structure (high child mortality), apply the corrected formula: R0 ~ 1 + L/A.

3. **From the final epidemic size.** For a single closed outbreak that runs to completion (no births, no re-introduction), use the final size equation. If a fraction p of the population remains uninfected, then R0 = -ln(p) / (1 - p). This requires complete data on total attack rate and a genuinely closed population.

4. **From exponential growth rate via log-linear regression.** During the early exponential phase of an epidemic: (a) take the log of incidence or cumulative case counts over time, (b) fit a linear regression to the log-transformed data -- the slope equals the exponential growth rate r, (c) convert to R0 using R0 = 1 + r x V, where V is the serial interval. Restrict the regression to the pre-peak period where growth is approximately exponential. Use cumulative incidence as a proxy for prevalence when prevalence data are unavailable.

5. Recognize that all four methods produce point estimates without formal uncertainty quantification. For decision-relevant estimates, proceed to likelihood-based or Bayesian fitting methods that produce confidence or credible intervals.

## Account for Sources of Variability

**Context:** Observed disease data deviate from deterministic model predictions for multiple reasons. Identifying which sources of variability are relevant determines the appropriate statistical model.

**Steps:**

1. **Measurement error:** Recognize that reported case counts imperfectly observe the true disease state. Under-reporting, diagnostic sensitivity, and reporting delays all introduce measurement noise. Model this as normally distributed error around the true value for continuous outcomes, or as a reporting probability (binomial thinning) for count data.

2. **Demographic stochasticity:** Account for random variation in individual-level events (infection, recovery, death) that becomes significant in small populations. Even with identical conditions, repeated outbreaks in a small community will differ in size and timing due to chance. This matters most when population sizes or case counts are small (roughly below a few hundred).

3. **Environmental stochasticity:** Incorporate external forcing factors that systematically alter transmission over time. Seasonal variation in contact rates (driven by school terms, climate, or agricultural cycles) is the most common example. Model this as a time-varying transmission parameter beta(t).

4. Match the statistical framework to the dominant variability sources. If measurement error dominates, a deterministic model with observation noise may suffice. If demographic stochasticity is important, use a stochastic transmission model (e.g., chain binomial). If environmental stochasticity drives patterns, include seasonal forcing terms.

## Build and Fit Stochastic Chain Binomial Models

**Context:** The chain binomial model is a discrete-time stochastic framework for outbreak data where transmission occurs in distinct generations. It captures demographic stochasticity and uses the full incidence time series for estimation.

**Steps:**

1. Aggregate reported incidence into time bins matching the pathogen's serial interval or generation time. For example, if the generation time is two weeks, sum cases into two-week windows.

2. Define the per-generation infection probability for each susceptible individual: P(infection) = 1 - exp(-beta x I_t / N), where I_t is the number of infectious individuals at generation t and N is population size. This derives from modeling effective contacts as a Poisson process with rate beta x I_t / N.

3. Draw new infections at each generation from a binomial distribution: I_{t+1} ~ Binomial(S_t, 1 - exp(-beta x I_t / N)). This captures the inherent randomness in who becomes infected while constraining the outcome to the finite susceptible pool.

4. Update the susceptible count each generation: S_{t+1} = S_t - I_{t+1}. Equivalently, S_t = S_0 - cumulative incidence through generation t. This assumes complete immunity after infection and a closed population.

5. Write the total likelihood as the product of binomial probabilities across all observed generations: log L(beta, S_0) = sum over t of log Binomial(I_{t+1} | S_t, 1 - exp(-beta x I_t / N)).

6. Maximize the log-likelihood over the parameter space (beta, S_0) using numerical optimization. Note that R0 ~ beta under this model when the entire population is susceptible, so the beta estimate directly informs R0.

7. Validate the fitted model by simulating many realizations (e.g., 500 stochastic trajectories) from the estimated parameters. Overlay simulations on observed data. Check whether the ensemble captures peak timing, peak magnitude, total outbreak size, and overall epidemic shape. Systematic discrepancies -- such as consistently wrong peak timing -- suggest model misspecification, data artifacts (e.g., early under-reporting), or incorrect assumptions about S_0.

## Fit Time-Series SIR (TSIR) Models

**Context:** The TSIR model is designed for endemic, seasonally recurring diseases observed over long time periods (years to decades). It estimates a time-varying seasonal transmission rate from case and demographic data.

**Steps:**

1. Reformulate the continuous-time SIR equations into discrete-time difference equations with a time step equal to the serial interval (e.g., biweekly for measles). The key equation is: I_{t+1} = beta_t x I_t^alpha x S_t / N, where beta_t is the time-varying transmission rate and alpha is a mixing correction exponent (typically 0.95-1.0) that accounts for non-homogeneous mixing and time-discretization effects.

2. Reconstruct the unobserved susceptible time series. Because susceptible counts are not directly measured, decompose S_t into a mean level S_bar plus a time-varying deviation Z_t: S_t = S_bar + Z_t. Estimate Z_t by regressing cumulative births on cumulative reported cases. In a pre-vaccination setting, new susceptibles come from births and exit via infection; the residuals of this cumulative regression yield the deviation series Z_t.

3. Estimate the reporting rate (rho) and mean susceptible level (S_bar) using profile likelihood. Hold rho fixed at a candidate value, reconstruct susceptibles, fit the transmission model, compute the likelihood, and repeat over a grid of rho values. Select the rho that maximizes the profile likelihood. Divide reported cases by rho to approximate true cases.

4. Estimate seasonally varying beta by log-linearizing the TSIR equation: log(I_{t+1}) = log(beta_t) + alpha x log(I_t) + log(S_t). Include dummy variables for each month (or biweek) of the year. Run a linear regression to obtain a separate beta estimate for each seasonal period. The resulting seasonal beta curve reveals when transmission peaks and troughs.

5. Interpret the seasonal beta curve by overlaying known behavioral or environmental covariates. A consistent dip in beta during school holidays (summer, winter breaks) across multiple diseases and locations provides evidence that school-based contact drives transmission. Overlay school calendar dates on the beta time series for visual comparison.

6. Assess uncertainty by examining confidence intervals on the seasonal beta estimates. Wide intervals indicate insufficient data for reliable estimation. Consider extending the time series or pooling data from multiple locations.

7. Apply TSIR fitting spatially by running the model independently for each geographic unit (e.g., state, province). Mean-center the resulting beta curves and overlay to identify consistent national-level seasonal patterns versus location-specific anomalies.

## Quick Reference

**Fitting Workflow Summary**
1. Formulate question
2. Choose model
3. Account for variability
4. Fit to data
5. Evaluate fit
6. Quantify uncertainty

**Least Squares vs. MLE Comparison**

| Feature | Least Squares | Maximum Likelihood |
|---|---|---|
| Distributional assumption | None (implicit normality) | Explicit (Poisson, binomial, etc.) |
| Objective function | Minimize sum of squared residuals | Maximize probability of observed data |
| Confidence intervals | Requires additional assumptions | Natural via likelihood surface |
| Best suited for | Continuous data, quick exploration | Count data, formal inference |

**R0 Estimation Methods at a Glance**

| Method | Data Required | Formula | Key Assumption |
|---|---|---|---|
| Endemic equilibrium | Seroprevalence | R0 = 1/S* | True steady state |
| Mean age of infection | Age-stratified serology | R0 ~ L/A | Endemic, immunizing, rectangular age distribution |
| Final epidemic size | Total attack rate | R0 = -ln(p)/(1-p) | Closed population, complete outbreak |
| Exponential growth | Early incidence time series | R0 = 1 + rV | Exponential phase only, known serial interval |

**Variability Types**

| Type | Source | Scale | Typical Model |
|---|---|---|---|
| Measurement error | Imperfect observation | Any | Normal noise, binomial thinning |
| Demographic stochasticity | Individual randomness | Small populations | Chain binomial, Markov chain |
| Environmental stochasticity | External forcing | Any | Seasonal beta(t) |

**Common Probability Distributions for Epidemiological Data**
- *Poisson:* rare event counts (weekly cases); mean = variance.
- *Binomial:* k infections from n susceptibles; requires known denominator.
- *Negative binomial:* overdispersed counts; variance > mean; adds dispersion parameter.
- *Normal:* continuous measurements; large-sample approximations.

**Key Equations**
- Residual: r_i = observed_i - predicted_i
- SSR = sum of r_i^2
- Log-likelihood: log L(theta) = sum of log P(data_i | theta)
- Bayes' theorem: P(theta | data) proportional to P(data | theta) x P(theta)
- Chain binomial infection probability: P(inf) = 1 - exp(-beta x I/N)
- TSIR: I_{t+1} = beta_t x I_t^alpha x S_t / N
- Profile likelihood CI threshold: log L_max - 1.92

**Rules of Thumb**
- Least squares is fastest for initial exploration; switch to MLE for formal inference.
- If variance increases with the mean (typical for count data), use Poisson or negative binomial likelihood rather than least squares.
- Run optimizers from multiple starting points to guard against local optima.
- Bayesian methods are most advantageous with small samples, strong priors, or sequential data integration.
- Restrict log-linear regression for growth rate estimation to the pre-peak exponential phase only.
- Always report uncertainty alongside point estimates; estimates without intervals are incomplete.
