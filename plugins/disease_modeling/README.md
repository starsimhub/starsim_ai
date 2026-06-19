# Disease Modeling Plugin

> **Status**: Work in progress (v0.1.0)

A Claude Code plugin providing disease modeling skills trained on Harvard's [Introduction to Infectious Disease Modeling](https://hsph.harvard.edu/research/communicable-disease-ccdd/resources/id-modeling/) course.

## Installation

Install via the Starsim-AI marketplace in Claude Code:

```
/plugin marketplace add https://github.com/starsimhub/starsim_ai
```

Then install the **disease-modeling** plugin from the Discover tab (`/plugin`).

## Skills

| Skill | Purpose |
|-------|---------|
| `basic_epi_modeling` | Disease burden, demography, transmission routes, compartmental model basics |
| `sir-models` | SIR equations, R0, effective reproduction number, interventions |
| `sir-elaborations` | SEIR/MSIR/SIRS extensions, age structure, contact heterogeneity, R0 estimation |
| `vaccination` | Herd immunity thresholds, vaccination strategies, vaccine failure modes, eradicability |
| `parameter-estimation` | Least squares, MLE, Bayesian inference, chain binomial, TSIR models |
| `vectors` | Ross-MacDonald model, SIWR environmental reservoirs, multi-strain dynamics |
| `surveillance` | Surveillance types, forecasting, forecast evaluation, genomic epidemiology |
