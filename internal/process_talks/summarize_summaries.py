"""
Parallel summary summarization using the Claude Agent SDK.

Like summarize_transcripts.py, but summarize the summaries into Claude skills.
"""

import asyncio
import sciris as sc
import claude_agent_sdk as claude

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


async def summarize_transcript(title, content):
    """Spawn a Claude agent to summarize a single transcript."""
    result_text = None

    async for message in claude.query(
        prompt=PROMPT_TEMPLATE.format(title=title, content=content),
        options=claude.ClaudeAgentOptions(
            allowed_tools=[],
            max_turns=1,
        ),
    ):
        if isinstance(message, claude.ResultMessage):
            result_text = message.result

    return result_text


async def summarize_all(transcript_dir, output_dir, max_concurrent=10):
    """Discover summaries, write skills in parallel """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Discover and read all transcripts
    transcript_files = sorted(transcript_dir.glob("*.txt"))
    print(f"Found {len(transcript_files)} transcripts\n")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_one(path):
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
    base = sc.thispath() / "harvard"
    summaries_dir = base / "summaries"
    output_dir = base / "harvard" / "skills"

    results = await summarize_all(summaries_dir, output_dir)

    succeeded = [r for r in results if r["output"]]
    failed = [r for r in results if not r["output"]]

    print(f"\n{'='*60}")
    print(f"Built {len(succeeded)}/{len(results)} skills")
    for r in succeeded:
        print(f"  {r['file']} -> {r['output']}")
    for r in failed:
        print(f"  {r['file']} -> FAILED")

    T.toc()


if __name__ == "__main__":
    with sc.timer():
        asyncio.run(main())
