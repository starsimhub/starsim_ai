You are an expert software engineer in Python and R, and your aim is to optimize scientific research code in terms of quality, usability, and safety.

# Step 1: Write scoring schema

Read `$ROOT/plugins/project-improver/admin/engineering_quality_guidelines.md` for background on making the plugin, where `$ROOT` is the Starsim-AI root folder.

First, read the metrics and explanations and write a simple scoring schema (in markdown, json, or yaml format) with specific scoring instructions for each tier. You don't have to follow this schema exactly, but something like this:
```
- Tier 1:
    - Quality:
        - Correct: 0 = obvious bugs, 3 = no bugs but no tests, 7 = no bugs and good tests, 10 = no bugs and good tests with GitHub Actions
        - Clear: 0 = files, folders, variables do not make sense, 3 = code readable but no modularization 7 = code is somewhat modular and easy to read, 10 = no obvious improvements to code clarity or modularity
        - Concise: 0 = many simplifications possible and violates style guide, 3 = some simplifications possible, 7 = occasional style guide violations and simplifications possible, 10 = perfectly follows style guide and no simplifications possible
    - Usability:
        - Documented: 0 = no readme or no docstrings, 3 = readme only and minimal docstrings, 7 = readmes, good docstrings, and at least one tutorial, 10 = readmes in each folder, docstrings for each function, tutorials, and user guide

- Tier 2:
    - Quality:
        - Correct: 0 = obvious bugs, 5 = no bugs but no tests, 10 = no bugs and good tests
        - Clear: 0 = files, folders, variables do not make sense, 5 = code readable but no modularization 10 = code is modular and easy to read
        - Concise: 0 = many simplifications possible, 5 = some simplifications possible, 10 = no simplifications possible
    - Usability:
        - Documented: 0 = no readme, 5 = readme only, 10 = readme and at least one tutorial

- Tier 3:
    - Quality:
        - Correct: 0 = obvious bugs, 10 = no obvious bugs
        - Clear: 0 = files, folders, variables do not make sense, 10 = code function can be understood
        - Concise: 0 = large blocks of duplicated code, 10 = no duplicated code
    - Usability:
        - Documented: 0 = no readme, 10 = decent readme
```

Some example scores are listed at the end of the document (but note that these are from an earlier version of the metrics).

# Step 2: Write Project Scorer

For the plugin, I want two agents and/or skills (whichever you think makes more sense): a Project Scorer and a Project Fixer.

For the Project Scorer:
1. The user supplies a project (by default, the current repo, but can be a folder or a GitHub URL) and specifies what tier they want to check compliance against (by default, 2).
2. For each of the three top-level metrics (quality, usability, safety), write a skill and/or subagent (whichever you think makes more sense) that scores the project against each metric (score using an integer from 0-10). Use the descriptions provided in the "Explanations" section. Return results as a JSON with the following exact schema: `{"project": <project_path>, "tier":<user_provided_tier>, "overall_score": 72, "failed":false, "quality": {"correct": {"score": 9, "weight": 7, "reason": "No major bugs found and extensive tests with 83% test coverage"}, "clear": {"score": 5, "weight": 2, "reason": "Some docstrings missing, some readmes missing, no tutorial provided"}, ...}`.
3. For metrics 1.1 (quality:correct) and 3.1 (safety:compliant), if any serious violations are found (e.g. major bugs that affect scientific validity of results or dangerous use of data), set `"failed":true` in the JSON, set the score to 0.
4. Assemble the results from each subagent. Write a file called `engineering_score.md`. This file should have 3 sections: "# Summary": a brief plain-language summary of the results. "# Recommendations": clear, concrete (detailed but brief), and actionable recommendations to improve the score. "# Full results": include the full JSON result (with appropriate indenting) as a raw element.

# Step 3: Write Project Fixer

For the Project Fixer:
1. Read the recommendations from `engineering_score.md` and make a prioritized plan for implementing them. (If this file doesn't exist, ask the user to run the Project Scorer first.)
2. Be clear and realistic about what recommendations you can implement (e.g., adding an LICENSE file), and which you cannot (e.g., writing an entire user guide).
3. Implement recommendations in the order of priority, asking the user for clarification if needed.
4. If implementing one recommendation would significantly negatively impact another metric (e.g., a performance optimization would decrease readability), ask the user how they want to proceed.