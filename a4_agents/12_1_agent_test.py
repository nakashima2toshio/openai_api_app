# python 12_1_agent_test.py
import asyncio

from agents import Agent, Runner

agent = Agent(
    name="Math Tutor",
    instructions="You help with math problems.",
)

async def main():
    result = await Runner.run(agent, "What is 2 + 2?")
    print(result.final_output)

# asyncio.run(main()) ←これで実行
if __name__ == '__main__':
    asyncio.run(main())

