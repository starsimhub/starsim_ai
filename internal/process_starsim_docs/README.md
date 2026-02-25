# Process Starsim docs

This was the prompt used to generate the starsim-dev skills:
```
make a plan to write a new set of skills for the starsim plugin based on the starsim tutorials and user guide. specifically, see the files in /home/cliffk/idm/starsim/docs. make the following claude SKILLs in the plugins/starsim folder. do this by reading, parsing, and summarizing the files listed after each skill name:
1. starsim-dev-intro: tutorials/t1_intro.ipynb, tutorials/t2_model.ipynb, user_guide/basics_model.ipynb
2. starsim-dev-sim: user_guide/basics_sim.ipynb, user_guide/basics_people.ipynb, user_guide/basics_parameters.ipynb
3. starsim-dev-demographics: tutorials/t3_demographics.ipynb, user_guide/modules_demographics.ipynb
4. starsim-dev-diseases: tutorials/t4_diseases.ipynb, user_guide/modules_diseases.ipynb
5. starsim-dev-networks: tutorials/t5_networks.ipynb, user_guide/modules_networks.ipynb
6. starsim-dev-interventions: tutorials/t6_interventions.ipynb, user_guide/modules_interventions.ipynb
7. starsim-dev-analyzers: user_guide/modules_analyzers.ipynb
8. starsim-dev-connectors: user_guide/modules_connectors.ipynb
9. starsim-dev-run: user_guide/workflows_run.ipynb
10. starsim-dev-calibration: user_guide/workflows_calibration.ipynb, user_guide/workflows_sir_calibration.ipynb
11. starsim-dev-distributions: user_guide/advanced_distributions.ipynb
12. starsim-dev-indexing: user_guide/advanced_indexing.ipynb
13. starsim-dev-nonstandard: user_guide/advanced_nonstandard.ipynb
14. starsim-dev-profiling: user_guide/advanced_profiling.ipynb
15. starsim-dev-random: user_guide/advanced_random.ipynb
16. starsim-dev-time: user_guide/advanced_time.ipynb

focus on practical skills, i.e. skills that will be useful for writing python code, e.g. which classes and methods to use when, patterns to use and those not to use, how to solve different types of problem, etc. keep each skill under (roughly) 3000 words.
```