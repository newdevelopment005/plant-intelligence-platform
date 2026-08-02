from celery import Celery

from app.config import settings

celery_app = Celery(
    "pip_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.modules.auth.tasks",
        "app.modules.literature.tasks",
        "app.modules.image_analysis.tasks",
        "app.modules.knowledge_graph.tasks",
        "app.modules.genomics.tasks",
        "app.modules.reporting.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3000,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_routes={
        "app.modules.ai.*": {"queue": "ai"},
        "app.modules.high_priority.*": {"queue": "high_priority"},
    },
    beat_schedule={
        "embed-new-papers": {
            "task": "app.modules.literature.tasks.embed_new_papers",
            "schedule": 3600.0,
        },
        "cleanup-expired-tokens": {
            "task": "app.modules.auth.tasks.cleanup_expired_tokens",
            "schedule": 86400.0,
        },
    },
)
