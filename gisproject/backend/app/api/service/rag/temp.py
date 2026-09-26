import asyncio

from app.api.service.rag.main import WebRAG


async def main():

    rag = WebRAG()

    await rag.initialize()

    thread_id = "rag-test-001"

    result = await rag.query(
        query="what is nisar",
        thread_id=thread_id,
    )

    print("\n==============================")
    print("RAG RESULT")
    print("==============================")

    print("Status:", result["status"])
    print("Tasks:", result["tasks"])
    print("Sources:", result["sources"])

    if result["tasks"]:

        print("\n==============================")
        print("HITL REQUIRED")
        print("==============================")

        result = await rag.resume(
            thread_id=thread_id,
            value="approve",
        )

    print("\n==============================")
    print("FINAL ANSWER")
    print("==============================")

    print(result["answer"])

    print("\n==============================")
    print("STATUS")
    print("==============================")

    print(result["status"])

    print("\n==============================")
    print("METRICS")
    print("==============================")

    for key, value in result["metrics"].items():
        if key != "request_start":
            print(f"{key}: {value}")

    if result["errors"]:

        print("\n==============================")
        print("ERRORS")
        print("==============================")

        for error in result["errors"]:
            print(error)

    await rag.close()


if __name__ == "__main__":
    asyncio.run(main())