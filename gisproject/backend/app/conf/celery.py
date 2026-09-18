import time

from app.conf.logging.celerylog import logger as log
from app.conf.logging.context import request_id_var, task_id_var, task_name_var
from app.conf.settings import Settings
from kombu import Queue, Exchange
from celery import Celery
from celery.signals import (
    before_task_publish,
    task_prerun,
    task_postrun,
    task_failure,
    task_retry,
)
log.info("Celery starting…")

app = Celery(
    "myapp",
    backend=Settings().CELERY_RESULT_BACKEND,
    broker=Settings().CELERY_BROKER_URL,
    include=["app.api.service.celery.celery_task"],
)

# core Celery config
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,

    # default routing
    task_default_queue="default",
    task_default_exchange="default",
    task_default_exchange_type="direct",
    task_default_routing_key="default",

    # declare queues with routing info
    task_queues=(
        Queue(
            "default",
            Exchange("default", type="direct"),
            routing_key="default",
        ),
        Queue(
            "heavy_task",
            Exchange("heavy_task", type="direct"),
            routing_key="heavy_task",
        ),
        Queue(
            "medium_task",
            Exchange("medium_task", type="direct"),
            routing_key="medium_task",
        ),
        Queue(
            "internal_task",
            Exchange("internal_task", type="direct"),
            routing_key="internal_task",
        ),
    ),



    broker_connection_retry_on_startup=True,
    broker_heartbeat=30,
    broker_pool_limit=10,
    broker_transport_options={"visibility_timeout": 3600},
    task_reject_on_worker_lost=True,

    result_extended=True,
    result_expires=3600,

    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,

    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,

    worker_hijack_root_logger=False,

    task_soft_time_limit=600,
    task_time_limit=650,
)

log.info("Celery app initialized successfully")


_task_start_times: dict[str, float] = {}


@before_task_publish.connect
def _propagate_request_id(headers=None, **_):
    if headers is not None:
        headers["request_id"] = request_id_var.get()


@task_prerun.connect
def _log_task_prerun(task_id=None, task=None, args=None, kwargs=None, **_):
    request = getattr(task, "request", None)
    request_id_var.set(request.get("request_id", "-") if request else "-")
    task_id_var.set(task_id or "-")
    task_name_var.set(task.name if task else "-")
    _task_start_times[task_id] = time.perf_counter()

    log.info("Task started", extra={"task_name": task.name, "task_id": task_id})


@task_postrun.connect
def _log_task_postrun(task_id=None, task=None, state=None, **_):
    start = _task_start_times.pop(task_id, None)
    duration_ms = round((time.perf_counter() - start) * 1000, 1) if start else None

    log.info(
        "Task finished",
        extra={
            "task_name": task.name,
            "task_id": task_id,
            "status": state,
            "duration_ms": duration_ms,
        },
    )

    request_id_var.set("-")
    task_id_var.set("-")
    task_name_var.set("-")


@task_failure.connect
def _log_task_failure(task_id=None, sender=None, exception=None, **_):
    start = _task_start_times.get(task_id)
    duration_ms = round((time.perf_counter() - start) * 1000, 1) if start else None

    log.error(
        "Task failed",
        extra={
            "task_name": sender.name,
            "task_id": task_id,
            "error": str(exception),
            "duration_ms": duration_ms,
        },
    )


@task_retry.connect
def _log_task_retry(sender=None, request=None, reason=None, **_):
    log.warning(
        "Task retrying",
        extra={
            "task_name": sender.name,
            "task_id": getattr(request, "id", None),
            "reason": str(reason),
        },
    )
