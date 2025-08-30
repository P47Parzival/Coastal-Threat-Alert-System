# backend/celery_config.py

from celery import Celery
from celery.schedules import crontab
import os

# Use Redis as the message broker
# The broker URL points to your running Redis instance.
BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create a Celery instance
celery_app = Celery(
    "tasks",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["tasks_gee", "tasks_flood_monitoring"]  # IMPORTANT: Tell Celery where to find tasks
)

# --- Define the Scheduled Task ---
# This is the "monitoring" part of your system.
celery_app.conf.beat_schedule = {
    'check-all-aois-daily': {
        'task': 'tasks_gee.schedule_all_aoi_checks', # Points to the task function
        'schedule': crontab("*"),  
        # Use crontab(minute='*/30') for every 30 mins for testing
    },
    'monitor-flood-risk-every-3-hours': {
        'task': 'tasks_flood_monitoring.monitor_all_users_for_flood',
        'schedule': crontab(minute=0, hour='*/3'),  # Every 3 hours
    },
    'cleanup-old-flood-alerts-daily': {
        'task': 'tasks_flood_monitoring.cleanup_old_flood_alerts',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

celery_app.conf.timezone = 'UTC'