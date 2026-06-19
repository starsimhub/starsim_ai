"""
Parallel transcript summarization using the Claude Agent SDK.

Each transcript gets its own Claude agent that reads and summarizes it concurrently.
"""

import asyncio
import sciris as sc
from process_common import run_pipeline

PROMPT_TEMPLATE = """\
Summarize this lecture transcript into a structured markdown document \
focused on disease modeling skills. Use this exact format:

# {title}

## Overview
1-2 sentence summary of the lecture's main topic.

## Key Concepts
- Very brief, bulleted list of the main ideas covered

## Modeling Skills
- Summarize the specific techniques, methods, or modeling approaches taught \
that a disease modeler could apply. Explain the actual skill rather than \
referencing it. For example, instead of "Reading and interpreting epidemic curves" \
say "Use epidemic curves to count cases and determine the type of epidemic  \
(outbreak: rapidly rising cases; endemic: steady)".

## Key Terms
Comma-separated list of important technical terms

Aim for roughly 200-800 words, but this is a guideline — let the \
content dictate the length. Shorter or longer is fine as long as \
the summary is substantive and complete.

---
TRANSCRIPT:
{content}"""


async def main():
    base = sc.thispath()
    await run_pipeline(
        input_dir=base / "harvard" / "transcripts",
        output_dir=base / "harvard" / "summaries",
        prompt_template=PROMPT_TEMPLATE,
        label="summaries",
    )


if __name__ == "__main__":
    with sc.timer():
        asyncio.run(main())
