import logging
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
task_id_var: ContextVar[str] = ContextVar("task_id", default="-")
task_name_var: ContextVar[str] = ContextVar("task_name", default="-")


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.task_id = task_id_var.get()
        record.task_name = task_name_var.get()
        return True
