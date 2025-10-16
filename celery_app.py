"""
Celery Application Configuration for MindMend

This module initializes Celery with Flask application context.
Used by celery workers and beat scheduler.
"""

from celery import Celery
from celery.schedules import crontab
import os

def make_celery(app):
    """
    Create and configure Celery application with Flask context.

    Args:
        app: Flask application instance

    Returns:
        Celery: Configured Celery instance
    """
    celery = Celery(
        'mindmend_tasks',
        broker=app.config.get('CELERY_BROKER_URL', os.getenv('CELERY_BROKER_URL', 'redis://:@redis:6379/0')),
        backend=app.config.get('CELERY_RESULT_BACKEND', os.getenv('CELERY_RESULT_BACKEND', 'redis://:@redis:6379/0')),
        include=['tasks']  # Import tasks module
    )

    # Update celery config from Flask config
    celery.conf.update(app.config)

    # Additional Celery configuration
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes max
        task_soft_time_limit=25 * 60,  # 25 minutes soft limit
        worker_prefetch_multiplier=4,
        worker_max_tasks_per_child=1000,
    )

    # Task context wrapper to run within Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery


# Create Flask app and Celery instance
from app import app as flask_app, db

celery_app = make_celery(flask_app)

# Configure periodic tasks (Celery Beat schedule)
celery_app.conf.beat_schedule = {
    'cleanup-old-sessions': {
        'task': 'tasks.cleanup_old_sessions',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'generate-daily-analytics': {
        'task': 'tasks.generate_daily_analytics',
        'schedule': crontab(hour=1, minute=0),  # Run at 1 AM daily
    },
    'check-subscription-renewals': {
        'task': 'tasks.check_subscription_renewals',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight daily
    },
    'process-pending-ai-analyses': {
        'task': 'tasks.process_pending_ai_analyses',
        'schedule': crontab(minute='*/15'),  # Run every 15 minutes
    },
    # AI Model Training Tasks
    'check-crisis-model-performance': {
        'task': 'tasks.check_crisis_model_performance',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'trigger-model-training': {
        'task': 'tasks.trigger_model_training',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'comprehensive-model-retraining': {
        'task': 'tasks.comprehensive_model_retraining',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    'generate-training-report': {
        'task': 'tasks.generate_training_report',
        'schedule': crontab(day_of_week=1, hour=6, minute=0),  # Weekly on Monday at 6 AM
    },
}

# Export for worker: celery -A celery_app worker
# The celery CLI looks for an 'app' attribute, so we alias it
app = celery_app
__all__ = ['celery_app', 'app', 'make_celery']
