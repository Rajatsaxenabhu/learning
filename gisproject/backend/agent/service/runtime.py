from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_core.tools import tool


@tool(
    "get_current_datetime",
    description=(
        "Get the current date, time, and timezone. "
        "Use this whenever the user's question depends on "
        "the current date or time, including current, latest, "
        "recent, today, this week, or this month."
    ),
)
def get_current_datetime() -> dict:
    now = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return {
        "datetime": now.isoformat(),
        "date": now.date().isoformat(),
        "time": now.strftime("%H:%M:%S"),
        "timezone": "Asia/Kolkata",
    }


get_current_datetime.metadata = {
    "read_only": True,
    "source": "runtime",
}