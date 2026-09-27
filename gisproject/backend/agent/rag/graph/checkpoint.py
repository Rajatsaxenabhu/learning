from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


async def create_checkpointer(
    database_path: str = "rag_checkpoints.db",
):
    return AsyncSqliteSaver.from_conn_string(
        database_path
    )