# **IDM software engineering quality guidelines**

This document provides guidelines on software engineering quality at IDM. 

There are millions\[*citation needed*\] of [software](https://en.wikipedia.org/wiki/Software_quality) [engineering](https://getdx.com/blog/software-quality-metrics/) [quality](https://www.geeksforgeeks.org/software-engineering/software-engineering-software-quality/) [guidelines](https://ieeexplore.ieee.org/document/10372494) already available. Why does IDM need its own? Because most of these guidelines are written with the assumption that software is the organization's main product. At IDM, code is usually a means to an end: still important, but subservient to our ultimate goal of providing timely, accurate analyses and recommendations.

# **Metrics**

## **The list**

*(Percentages are relative weights; if principles conflict, the order listed here takes precedence)*

1. Quality  
   1. \[70%\] Correct: works as intended with good test coverage  
   2. \[20%\] Clear: sensible modular structure and appropriately commented  
   3. \[10%\] Concise: amount of code is minimized  
2. Usability  
   1. \[30%\] Simple: APIs are easy and intuitive  
   2. \[20%\] Powerful: APIs are flexible and adaptable  
   3. \[20%\] Performant: the code runs quickly  
   4. \[20%\] Documented: users can quickly get up to speed  
   5. \[10%\] Accessible: the code is open source  
3. Safety  
   1. \[60%\] Compliant: no legal or security vulnerabilities  
   2. \[40%\] Reproducible: different people at different times can get the same results

## **Explanations**

1. **Quality**  
   1. **Correct:** If the code is not correct, then it has no (or negative) value.  
      1. The software spec is clear, matches the problem being solved, and is scientifically correct.  
      2. Code is implemented correctly according to the spec.  
      3. Code has been validated through real-world or representative usage.  
      4. Test coverage is sufficient to be confident that there are no major bugs.  
      5. Tests primarily check for correct scientific results (e.g. parameter behavior), including edge cases.  
      6. Tests are incorporated in an automated CI/CD pipeline.  
   2. **Clear:** If the code is not clear, it is hard to maintain and increases the risk of bugs.  
      1. Code is structured appropriately in terms of files and folders.  
      2. Within each file, the code is appropriately divided into classes, methods, and functions.  
      3. Variables, functions, and classes have clear, descriptive names that follow consistent conventions.  
      4. Code is easy to read and understand.  
      5. Explicit, readable code is better than clever or dense constructs.  
      6. Introduce abstractions only when they reduce complexity.  
      7. There are sufficient docstrings and line comments to make it clear what the code is doing.  
   3. **Concise:** If the code is not concise, it is also hard to maintain.  
      1. There is minimal duplication within the codebase.  
      2. Code is written in the most efficient way, consistent with the style guide (via an automatic linter where possible).  
      3. External libraries are used as shortcuts where appropriate.  
2. **Usability**  
   1. **Simple:** If the code is not simple, users will make mistakes or not use it.  
      1. It is clear what classes/functions ("APIs") the user is supposed to interact with.  
      2. APIs have sensible defaults where possible, so things "just work".  
      3. APIs have as few arguments as possible (but no fewer).  
      4. Arguments are standard Python/NumPy types if possible.  
      5. Arguments are documented (via docstrings/type hints) and explicitly validated.  
      6. Exceptions are anticipated, and error messages help the user fix the problem.  
      7. Common workflows require minimal configuration, and/or are encapsulated in one-line scripts or commands.  
   2. **Powerful:** If the code is not powerful, users will get frustrated and write their own.  
      1. APIs have as many arguments as needed (but no more).  
      2. The vast majority of use cases are met without the user needing to modify the code.  
      3. All assumptions are transparent and modifiable by the user.  
      4. Classes can be easily subclassed (e.g., methods are modular).  
   3. **Performant:** If the code is not performant, it wastes the user's time and resources.  
      1. End-to-end code runs in negligible time (\<10 seconds) if possible; otherwise, it aims to runs within 2-5x of what it would in Rust/C++.  
      2. Performance bottlenecks are identified via profiling and optimized where they matter, and performance regressions are identified and fixed.  
      3. There are no obvious, major inefficiencies (e.g. for loops when vectors can be used).  
      4. All algorithms are appropriate for the task they are being used for.  
   4. **Documented:** If the code is not documented, users will struggle to use it correctly (or at all).  
      1. Docstrings clearly explain what the APIs do, including examples.  
      2. For small projects, a readme explains installation, basic usage, and project structure.  
      3. For large projects, docs include a readme in each folder, interactive tutorials, and a detailed user guide.  
      4. Docs are meaningful to users of different levels of expertise.  
   5. **Accessible:** If the code is not accessible, it will not be used.  
      1. Code is released in a public GitHub repo, in an appropriate GitHub org.  
      2. Key files are present (MIT license and changelog; optionally contributing guidelines, code of conduct, and future roadmap).  
      3. Installation does not require special environments and is doable via 1-3 commands.  
      4. Code has been optimized for use with AI assistants (e.g. skills, MCP servers, etc).  
      5. Users know how to get support and feel comfortable doing so.  
3. **Safety**  
   1. **Compliant:** If the code is noncompliant, it should not be used.  
      1. Any data from external sources is used with permission (if applicable).  
      2. No API keys or secrets are exposed in the repository.  
      3. Code does not have any dependencies that have proprietary/restrictive licenses.  
   2. **Reproducible:** If the results cannot be reproduced later, it wastes time and harms reputation.  
      1. Semantic versioning is used, including git tags for each release.  
      2. Releases are published on PyPI/CRAN.  
      3. Dependencies are specified, with upward-pinned (\>=) versions where needed.  
      4. If reproducibility is important (e.g. non-library code), there is an optional lock file.  
      5. If random numbers are used, the same seeds give identical results (where possible).

# **Minimum expectations**

This section outlines the minimum software engineering expectations for different types of project.

We divide code at IDM into four tiers, with different quality expectations for each:

* **Tier 0** code is quick experiments/explorations. It is never seen by anyone other than the author and will likely never be used after the day it was written. It is typically not pushed to GitHub, or of it is, it's in a private repo. There are no quality expectations for this code, and it will not be discussed further.  
  * *Examples*: A short script for plotting simulation outputs to help diagnose a bug; a statistical test on a dataset to check if further analyses are worth pursuing.  
* **Tier 1** code is one-off code that may be used repeatedly, but only within the context of a single project, often still by a single person. Tier 1 code does not have any downstream dependencies.   
  * *Examples*: Code that analyzes data and plots a figure used in a presentation; a proof of principle implementation of a model that may or not be used in future.  
* **Tier 2** code solves a specific problem, but is used by multiple projects and/or people, typically over a period of several months or more. Tier 2 code may have downstream dependencies.  
  * *Examples*: A model calibrated to a specific disease in a specific country; a set of utilities used by a handful of internal projects.  
* **Tier 3** code is "library" or "GPG" code, expected to be used by many people (including external collaborators) for many projects for many months/years.  
  * *Examples*: EMOD, EMOD-Malaria, LASER, LASER-Measles, Starsim, FPsim

Tier 3 requirements are similar to industry-standard "engineering quality" guidelines. Why not just enforce these for all tiers? Because when you're just trying to plot some data, some "best practices" like a CI/CD pipeline are not only not helpful, they actively create technical debt and maintenance burden.

## **Tier 1: One-off/exploratory project**

1. Quality  
   1. Correct: appears to work as intended; no tests expected  
   2. Clear: the author is confident it will still make sense to them in 1-3 months  
   3. Concise: no egregious code duplication (e.g., copied files with small modifications)  
2. Usability  
   1. Simple: common workflows are not too painful  
   2. Powerful: N/A (no flexibility is expected)  
   3. Performant: total time spent running the code over the project lifetime is less than the time it would take to refactor it  
   4. Documented: a folder readme  
   5. Accessible: N/A (often a private repo)  
3. Safety  
   1. Compliant: as above (no legal or security vulnerabilities)  
   2. Reproducible: key files checked into GitHub

## **Tier 2: Small-scale project**

1. Quality  
   1. Correct: works as intended, with basic test coverage  
   2. Clear: modular structure if appropriate, some comments  
   3. Concise: no excessive duplication  
2. Usability  
   1. Simple: APIs for most common pathways are easy and intuitive  
   2. Powerful: some flexibility is allowed  
   3. Performant: no obvious/major inefficiencies  
   4. Documented: one or more readmes and at least one tutorial  
   5. Accessible: as above (code is open source)  
3. Safety  
   1. Compliant: as above (no legal or security vulnerabilities)  
   2. Reproducible: as above (different people at different times can get the same results)

## **Tier 3: Software library**

1. All requirements listed above.
