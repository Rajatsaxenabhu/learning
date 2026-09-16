import anyio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.llm import LLMClient


async def main() -> None:

    llm = LLMClient()

    messages = [
        {
            "role": "user",
            "content": "Calculate the area of POLYGON ((82 25, 82.01 25, 82.01 25.01, 82 25))",
        }
    ]

    response = await llm.chat_once(messages)

    print("TYPE:")
    print(type(response))

    print("\nRESPONSE:")
    print(response)

    print("\nMESSAGE:")
    print(response.message)

    print("\nTOOL CALLS:")
    print(response.message.tool_calls)


if __name__ == "__main__":
    anyio.run(main)