"""
Parallel transcript summarization using the Claude Agent SDK.

Each transcript gets its own Claude agent that reads and summarizes it concurrently.
"""

import asyncio
from pathlib import Path

import sciris as sc
from claude_agent_sdk import query, ClaudeAgentOptions

PROMPT_TEMPLATE = """\
Summarize this lecture transcript into a structured markdown document \
focused on disease modeling skills. Use this exact format:

# {title}

## Overview
1-2 sentence summary of the lecture's main topic.

## Key Concepts
- Bulleted list of the main ideas covered

## Modeling Skills
- Specific techniques, methods, or modeling approaches taught \
that a disease modeler could apply

## Key Terms
Comma-separated list of important technical terms

Aim for roughly 100-500 words, but this is a guideline — let the \
content dictate the length. Shorter or longer is fine as long as \
the summary is substantive and complete.

---
TRANSCRIPT:
{content}"""


async def summarize_transcript(title: str, content: str) -> str:
    """Spawn a Claude agent to summarize a single transcript."""
    result_text = None

    async for message in query(
        prompt=PROMPT_TEMPLATE.format(title=title, content=content),
        options=ClaudeAgentOptions(
            allowed_tools=[],
            max_turns=1,
        ),
    ):
        if message.type == "result":
            result_text = message.result

    return result_text


async def summarize_all(
    transcript_dir: Path,
    output_dir: Path,
    max_concurrent: int = 5,
) -> list[dict]:
    """Discover transcripts, summarize in parallel, write markdown files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover and read all transcripts
    transcript_files = sorted(transcript_dir.glob("*.txt"))
    print(f"Found {len(transcript_files)} transcripts\n")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_one(path: Path) -> dict:
        # Reverse sc.sanitizefilename: underscores->spaces, double-space->colon-space
        title = path.stem.replace("_", " ").replace("  ", ": ")

        async with semaphore:
            content = path.read_text()
            sc.printgreen(f"Starting: {path.name}")
            try:
                result = await summarize_transcript(title, content)
            except Exception as e:
                print(f"FAILED: {path.name}: {e}")
                return {"file": path.name, "output": None}

        if result is None:
            print(f"WARNING: No result for {path.name}")
            return {"file": path.name, "output": None}

        print(f"Finished: {path.name}")
        out_path = output_dir / f"{path.stem}.md"
        out_path.write_text(result)
        return {"file": path.name, "output": str(out_path)}

    tasks = [process_one(p) for p in transcript_files]
    return await asyncio.gather(*tasks)


async def main():
    T = sc.timer()
    base = sc.thispath()
    transcript_dir = base / "harvard" / "transcripts"
    output_dir = base / "harvard" / "summaries"

    results = await summarize_all(transcript_dir, output_dir)

    succeeded = [r for r in results if r["output"]]
    failed = [r for r in results if not r["output"]]

    print(f"\n{'='*60}")
    print(f"Summarized {len(succeeded)}/{len(results)} transcripts")
    for r in succeeded:
        print(f"  {r['file']} -> {r['output']}")
    for r in failed:
        print(f"  {r['file']} -> FAILED")

    T.toc()


if __name__ == "__main__":
    asyncio.run(main())
