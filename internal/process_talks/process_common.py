"""
Shared logic for parallel transcript/summary processing with Claude agents.
"""

import asyncio
import sciris as sc
import claude_agent_sdk as claude


async def process_with_claude(title, content, prompt_template):
    """Spawn a Claude agent to process a single file using the given prompt template.

    Args:
        title (str):           Display title derived from the filename.
        content (str):         File content to process.
        prompt_template (str): Prompt with {title} and {content} placeholders.

    Returns:
        str: The agent's result text, or None if no result was returned.
    """
    result_text = None
    async for message in claude.query(
        prompt=prompt_template.format(title=title, content=content),
        options=claude.ClaudeAgentOptions(
            allowed_tools=[],
            max_turns=1,
        ),
    ):
        if isinstance(message, claude.ResultMessage):
            result_text = message.result
    return result_text


async def process_all(input_dir, output_dir, prompt_template, max_concurrent=10):
    """Discover .txt files, process each in parallel, write markdown outputs.

    Args:
        input_dir (Path):       Directory containing .txt input files.
        output_dir (Path):      Directory to write .md output files.
        prompt_template (str):  Prompt with {title} and {content} placeholders.
        max_concurrent (int):   Maximum number of concurrent Claude agents.

    Returns:
        list: List of dicts with 'file' and 'output' keys.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    input_files = sorted(input_dir.glob("*.txt"))
    print(f"Found {len(input_files)} files\n")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_one(path):
        title = path.stem.replace("_", " ").replace("  ", ": ")
        async with semaphore:
            content = path.read_text()
            sc.printgreen(f"Starting: {path.name}")
            try:
                result = await process_with_claude(title, content, prompt_template)
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

    tasks = [process_one(p) for p in input_files]
    return await asyncio.gather(*tasks)


async def run_pipeline(input_dir, output_dir, prompt_template, label="files"):
    """Run the full processing pipeline with timing and summary output.

    Args:
        input_dir (Path):       Directory containing .txt input files.
        output_dir (Path):      Directory to write .md output files.
        prompt_template (str):  Prompt with {title} and {content} placeholders.
        label (str):            Label for the summary message (e.g. "transcripts", "skills").
    """
    T = sc.timer()
    results = await process_all(input_dir, output_dir, prompt_template)

    succeeded = [r for r in results if r["output"]]
    failed = [r for r in results if not r["output"]]

    print(f"\n{'='*60}")
    print(f"Built {len(succeeded)}/{len(results)} {label}")
    for r in succeeded:
        print(f"  {r['file']} -> {r['output']}")
    for r in failed:
        print(f"  {r['file']} -> FAILED")

    T.toc()
