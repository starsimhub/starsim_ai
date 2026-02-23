"""
Check what tools the agents have access to
"""

import asyncio
import sciris as sc
import claude_agent_sdk as claude

async def ask_about_tools():

    async for message in claude.query(
        prompt="List all available plugins, skills, and tools you have access to",
        options=claude.ClaudeAgentOptions(
            cwd="/home/cliffk/idm/starsim_ai",
            allowed_tools=["Read", "Glob", "Grep"]
        )
    ):
        print(message)
    if isinstance(message, claude.ResultMessage):
        sc.heading('Result')
        sc.pr(message)
        print(message.result)
    return message

if __name__ == "__main__":
    with sc.timer():
        asyncio.run(ask_about_tools())