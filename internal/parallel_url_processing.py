"""
Parallel URL processing using the Claude Agent SDK.

Each URL gets its own Claude agent that downloads and processes it concurrently.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def process_url(url: str, instruction: str) -> dict:
    """Spawn a Claude agent to download and process a single URL."""
    result_text = None
    session_id = None

    async for message in query(
        prompt=f"{instruction}\n\nURL: {url}",
        options=ClaudeAgentOptions(
            allowed_tools=["WebFetch", "WebSearch"],
            max_turns=5,
        ),
    ):
        if message.type == "system" and message.subtype == "init":
            session_id = message.session_id
        elif message.type == "result":
            result_text = message.result

    return {"url": url, "result": result_text, "session_id": session_id}


async def process_urls_parallel(
    urls: list[str],
    instruction: str,
    max_concurrent: int = 5,
) -> list[dict]:
    """Process multiple URLs in parallel with a concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_process(url: str) -> dict:
        async with semaphore:
            print(f"Starting: {url}")
            result = await process_url(url, instruction)
            print(f"Finished: {url}")
            return result

    tasks = [limited_process(url) for url in urls]
    return await asyncio.gather(*tasks)


async def main():
    urls = [
        "https://docs.python.org/3/library/asyncio.html",
        "https://docs.python.org/3/library/concurrent.futures.html",
        "https://docs.python.org/3/library/multiprocessing.html",
    ]

    instruction = "Summarize this documentation page in 2-3 sentences. Focus on the main purpose and key features."

    print(f"Processing {len(urls)} URLs in parallel...\n")
    results = await process_urls_parallel(urls, instruction, max_concurrent=3)

    for r in results:
        print(f"\n{'='*60}")
        print(f"URL: {r['url']}")
        print(f"Result: {r['result']}")


if __name__ == "__main__":
    asyncio.run(main())
