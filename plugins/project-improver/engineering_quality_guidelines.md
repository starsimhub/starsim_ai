# **IDM software engineering quality guidelines**

Cliff Kerr1, Christopher Lorton1, Robyn Stuart1, Romesh Abeysuriya2, Vlad-Stefan Harbuz3,   
Jeremy Manson4, Jen Schripsema1, Mandy Izzo1, Jennifer Simeon1, Paul Saxman1

1 Institute for Disease Modeling, Gates Foundation;  2 Burnet Institute; 3 Open Source Pledge; 4 Google

Version 1.1 | 2026.03.23

# **Guidelines**

This section lists the guidelines for software quality, which correspond to "Tier 1" (library) code. Expectations are different for other tiers of code, as described below.

The percentage listed for each guideline is its relative weight, which can be used to calculate an overall quality score for a project. These scores should be interpreted carefully, since differences of opinion are frequently valid.

If a conflict between two guidelines cannot be resolved, then all else being equal, the order of the sections and the order listed in each subsection takes precedence (e.g., correct code takes precedence over clear code and performant code; simple code takes precedence over powerful code and reproducible code). Before making these tradeoffs, however: (a) use your judgement (e.g. a simpler loop syntax does not justify a 5x performance penalty); (b) if you are weighing two options that each conflict with a guideline, look for a third option that satisfies both.

Note that while code may contain minor bugs ("Quality: Correct") or have minor potential security issues ("Safety: Compliant") that affect its overall quality score, major bugs or security/legal issues mean the code should not be used at all until the issues are addressed.

## **The list**

1. \[40%\] **Quality**  
   1. \[70%\] **Correct**: works as intended with good test coverage  
   2. \[20%\] **Clear**: sensible modular structure and appropriately commented  
   3. \[10%\] **Concise**: amount of code is minimized  
2. \[40%\] **Usability**  
   1. \[30%\] **Simple**: APIs are easy and intuitive  
   2. \[20%\] **Powerful**: APIs are flexible and adaptable  
   3. \[20%\] **Performant**: the code runs quickly  
   4. \[20%\] **Documented**: users can quickly get up to speed  
   5. \[10%\] **Accessible**: the code is open source with key files present  
3. \[20%\] **Safety**  
   1. \[60%\] **Compliant**: no legal or security vulnerabilities  
   2. \[40%\] **Reproducible**: different people at different times can get the same results

## **The details** 

1. **Quality**  
   1. **Correct:** If the code is not correct, then it has no (or negative) value.  
      1. The software spec is clear, matches the problem being solved, and is scientifically correct.  
      2. Code is implemented correctly according to the spec.  
      3. Assumptions are explicit and documented; there are no "magic numbers" (all scientific parameters are linked to a source).  
      4. Code has been validated through real-world or representative usage.  
      5. Test coverage is sufficient to be confident that there are no major bugs.  
      6. Tests primarily check for correct scientific results (e.g. parameter behavior), including edge cases.  
      7. Tests are incorporated in an automated CI/CD pipeline.  
   2. **Clear:** If the code is not clear, it is hard to maintain and increases the risk of bugs.  
      1. Code is structured appropriately in terms of files and folders.  
      2. Within each file, the code is appropriately divided into classes, methods, and functions.  
      3. Variables, functions, and classes have clear, descriptive names that follow consistent conventions.  
      4. Code is easy to read and understand; someone looking at it can quickly explain what it is doing and why.  
      5. Clever or dense constructs are avoided, since debugging is hard at the best of times.  
      6. Abstractions are introduced only when they reduce complexity.  
      7. There are sufficient docstrings and line comments to make it clear what the code is doing.  
   3. **Concise:** If the code is not concise, it is also hard to maintain.  
      1. Code is written in the most efficient way (without compromising clarity).  
      2. Code is consistent with the style guide (via an automatic linter where possible).  
      3. There is minimal duplication within the codebase.  
      4. External libraries are used appropriately to avoid reimplementing features.  
2. **Usability**  
   1. **Simple:** If the code's classes/functions ("APIs") are not simple to use, users will make mistakes or not use it.  
      1. It is clear what APIs the user is supposed to interact with.  
      2. APIs have sensible defaults where possible, so things "just work".  
      3. APIs have as few arguments as possible (but no fewer).  
      4. Arguments can be standard Python/NumPy types if possible.  
      5. Arguments are documented (via docstrings and/or type hints) and explicitly validated.  
      6. Exceptions are anticipated, and error messages help the user fix the problem.  
      7. Common workflows require minimal configuration, and/or are encapsulated in one-line scripts or commands.  
   2. **Powerful:** If the code is not powerful, users will get frustrated and write their own.  
      1. APIs have as many arguments as needed (but no more).  
      2. The vast majority of use cases can be met with input arguments, without the user needing to modify the code.  
      3. All assumptions are transparent and modifiable by the user.  
      4. Classes can be easily subclassed (e.g., methods are small and modular).  
   3. **Performant:** If the code is not performant, it wastes the user's time and resources.  
      1. End-to-end code runs in negligible time (\<10 seconds) if possible; otherwise, it ideally runs within 2-5x of what it would in Rust/C++.  
      2. Performance bottlenecks are identified via profiling and optimized where they matter, and performance regressions are identified and fixed.  
      3. There are no obvious, major inefficiencies (e.g. for loops when vectors can be used).  
      4. Slow (\>30 s), embarrassingly parallel tasks can be run in parallel.  
      5. All algorithms are appropriate for the task they are being used for.  
   4. **Documented:** If the code is not documented, users will struggle to use it correctly (or at all).  
      1. Docstrings clearly explain what the APIs do, including examples where relevant.  
      2. If there are multiple ways to perform a task, the documentation makes it clear what the tradeoffs of each approach are.  
      3. For small projects, a readme explains installation, basic usage, and project structure.  
      4. For large projects, docs include a readme in each folder, interactive tutorials, and a user guide that describes the knowledge/processes needed for a typical workflow.  
      5. Docs are meaningful to users of different levels of expertise, including a non-technical introduction (for external-facing projects), information for users, and information for contributors.  
      6. Docs follow the relevant style guide.  
   5. **Accessible:** If the code is not accessible, it will not be used.  
      1. Code is released in a public GitHub repo, in an appropriate GitHub org.  
      2. Key files are present (MIT license and changelog; optionally contributing guidelines, code of conduct, and future roadmap).  
      3. Installation does not require special environments and is doable via 1-3 commands.  
      4. Code has been optimized for use with AI assistants (e.g. skills, MCP servers, etc).  
      5. Users know how to get support and feel comfortable doing so.  
3. **Safety**  
   1. **Compliant:** If the code is noncompliant, it should not be used.  
      1. Any data from external sources is used with permission, and this permission is documented in the repo (if applicable).  
      2. No API keys or secrets are exposed in the repository.  
      3. Code does not have any dependencies that have proprietary/restrictive licenses that our use violates.  
   2. **Reproducible:** If the results cannot be reproduced later, it wastes time and harms reputation.  
      1. Semantic versioning is used, including git tags for each release.  
      2. Releases are published on PyPI/CRAN.  
      3. Dependencies are specified (e.g. in pyproject.toml); if reproducibility is important (such as for research projects / non-library code), pinned versions, an environment file, or a lock file is included.  
      4. If random numbers are used, the same seeds give numerically identical results (where possible).

# **Code tiers**

This section outlines the minimum software engineering expectations for different types of project.

We divide code at IDM into three tiers, with different quality expectations for each:

|  | Tier 1 | Tier 2 | Tier 3 |
| :---- | :---- | :---- | :---- |
| **What is it?** | "Library" or "digital public good" (DPG) code that we share globally as one of IDM's flagship outputs, expecting considerable use internally and externally. | Solves a specific problem in a reusable way, e.g. a model calibrated to a specific disease in a specific country or a set of utilities used by a handful of internal projects. | One-off code that may be used repeatedly, but only within the context of a single project, e.g. code to produce the results for a paper or presentation. |
| **Number of expected users** | Many (\>10), including internal and external | Several (2-10), potentially including some external | Often only one, but sometimes several |
| **TImeline** | Long (\>12 months) | Medium (\>3 months) | Short (typically \<3 months) |
| **Public repo?** | Yes | Usually, but not always | Sometimes (e.g. code for a paper), but often not. |
| **Downstream dependencies?** | Always some, typically many (\>5) | Usually some, but not always | No |
| **Examples** | Modeling frameworks ([EMOD](https://github.com/EMOD-Hub/EMOD), [LASER](https://github.com/laser-base/laser-core), [Starsim](https://github.com/starsimhub/starsim)), disease models (e.g. [EMOD-Malaria](https://github.com/EMOD-Hub/emodpy-malaria), [LASER-Measles](https://github.com/InstituteforDiseaseModeling/laser-measles), [HPVsim](https://github.com/starsimhub/hpvsim), [MOSAIC](https://github.com/InstituteforDiseaseModeling/MOSAIC-pkg)), core utilities (e.g. [Sciris](https://github.com/sciris/sciris), [Starsim-AI](https://github.com/starsimhub/starsim_ai)) | Calibrated models (e.g. [HIVsim-Kenya](https://github.com/starsimhub/hiv_kenya), [LASER-Polio-Nigeria](https://github.com/InstituteforDiseaseModeling/laser-polio-nigeria)); internally used utilities (e.g. [idmtools](https://github.com/InstituteforDiseaseModeling/idmtools), [RasterToolkit](https://github.com/InstituteforDiseaseModeling/RasterToolkit), [Calabaria](https://github.com/InstituteforDiseaseModeling/modelops-calabaria)) | Code for presentations (e.g. [Bridging the Gap](https://github.com/InstituteforDiseaseModeling/Bridging-the-Gap-Low-Resource-African-Languages), [VMB-Dashboard](https://github.com/starsimhub/vmb-dashboard)), code for papers (e.g. [Zimbabwe-Syphilis](https://github.com/starsimhub/syph_dx_zim)), experiments or validations (e.g. [Malaria-Validation](https://github.com/InstituteforDiseaseModeling/malaria-model_validation)) |

In addition to these tiers, there is also "Tier ∞" code, which consists of quick experiments/explorations. It is never seen by anyone other than the author and will likely never be used after the day (or hour) it was written. It is typically not pushed to GitHub, or if it is, it's in a private repo. Examples of Tier ∞ code include a short script for plotting simulation outputs to help diagnose a bug, or a statistical test on a dataset to check if further analyses are worth pursuing. This code can be arbitrarily lousy, and it will not be discussed further.

Tier 1 requirements are similar to industry-standard "engineering quality" guidelines. Why not just enforce these for all tiers? Because when you're just trying to plot some data, some "best practices" like a CI/CD pipeline are not only not helpful, they actively create technical debt and maintenance burden.

## **Tier 1: Large-scale project (e.g. modeling framework)**

1. All requirements listed above.

## **Tier 2: Small-scale project (e.g. calibrated country model)**

1. Quality  
   1. Correct: works as intended, with basic test coverage  
   2. Clear: modular structure if appropriate, some comments  
   3. Concise: no excessive duplication  
2. Usability  
   1. Simple: APIs for most common pathways are easy and intuitive  
   2. Powerful: some flexibility is allowed  
   3. Performant: no obvious/major inefficiencies  
   4. Documented: one or more readmes and a tutorial or set of example scripts   
   5. Accessible: as above (code is open source)  
3. Safety  
   1. Compliant: as above (no legal or security vulnerabilities)  
   2. Reproducible: as above (different people at different times can get the same results)

## **Tier 3: One-off/exploratory project (e.g. analysis script)**

1. Quality  
   1. Correct: works as intended; tested through usage with no tests expected  
   2. Clear: the author is confident it will still make sense to them in 1-3 months  
   3. Concise: no egregious code duplication (e.g., copied files with small modifications)  
2. Usability  
   1. Simple: common workflows are not too painful  
   2. Powerful: N/A (no flexibility is expected)  
   3. Performant: total time spent running the code over the project lifetime is less than the time it would take to refactor it  
   4. Documented: a folder readme  
   5. Accessible: code is in an appropriate GitHub org, but is often private  
3. Safety  
   1. Compliant: as above (no legal or security vulnerabilities)  
   2. Reproducible: all files needed to run the code are checked into GitHub
