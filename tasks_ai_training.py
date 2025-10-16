"""
AI Model Training Tasks for MindMend
Celery tasks for automated model training and monitoring
"""

from celery_app import celery_app as celery
from datetime import datetime, timedelta
import asyncio
import logging
from models.database import db

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3)
def check_crisis_model_performance(self):
    """
    Monitor crisis detection model performance and trigger retraining if needed.
    Runs every 30 minutes.
    """
    try:
        from models.auto_training_pipeline import training_pipeline

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(training_pipeline.check_crisis_model_performance())

        logger.info("Crisis model performance check completed")
        return {'status': 'success', 'timestamp': datetime.utcnow().isoformat()}

    except Exception as exc:
        logger.error(f"Crisis model performance check failed: {exc}")
        self.retry(exc=exc, countdown=300)  # Retry in 5 minutes


@celery.task(bind=True, max_retries=2)
def trigger_model_training(self):
    """
    Trigger training cycle for AI models if conditions are met.
    Runs every 6 hours.
    """
    try:
        from models.auto_training_pipeline import training_pipeline

        # Run async training trigger
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(training_pipeline.trigger_training_cycle())

        logger.info("Model training cycle triggered")
        return {'status': 'success', 'timestamp': datetime.utcnow().isoformat()}

    except Exception as exc:
        logger.error(f"Model training trigger failed: {exc}")
        self.retry(exc=exc, countdown=1800)  # Retry in 30 minutes


@celery.task(bind=True, max_retries=1)
def comprehensive_model_retraining(self):
    """
    Comprehensive retraining of all models.
    Runs daily at 3 AM.
    """
    try:
        from models.auto_training_pipeline import training_pipeline

        # Run comprehensive retraining
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(training_pipeline.comprehensive_retraining())

        logger.info("Comprehensive model retraining completed")
        return {'status': 'success', 'timestamp': datetime.utcnow().isoformat()}

    except Exception as exc:
        logger.error(f"Comprehensive retraining failed: {exc}")
        # Don't retry comprehensive training - wait for next scheduled run
        return {'status': 'error', 'message': str(exc)}


@celery.task
def generate_training_report():
    """
    Generate weekly training report.
    Runs weekly on Monday at 6 AM.
    """
    try:
        from models.auto_training_pipeline import training_pipeline

        # Generate report
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(training_pipeline.generate_training_report())

        logger.info("Training report generated")

        # Email report to admins (if configured)
        # send_admin_report.delay(report)

        return {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'report_summary': {
                'models_trained': len(report.get('recent_models', [])),
                'active_models': report.get('active_models', []),
                'next_training': report.get('next_training')
            }
        }

    except Exception as exc:
        logger.error(f"Training report generation failed: {exc}")
        return {'status': 'error', 'message': str(exc)}


@celery.task(bind=True)
def train_custom_crisis_model(self, min_samples=50):
    """
    Train custom crisis detection model.
    Can be triggered manually or by other tasks.
    """
    try:
        from models.model_training_analytics import model_analytics

        # Run training
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        model_path = loop.run_until_complete(
            model_analytics.train_custom_crisis_model(min_samples)
        )

        if model_path:
            logger.info(f"Custom crisis model trained: {model_path}")

            # Update crisis predictor with new model
            from models.universal_crisis_predictor import crisis_predictor
            crisis_predictor.load_custom_model()

            return {
                'status': 'success',
                'model_path': model_path,
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            return {
                'status': 'insufficient_data',
                'message': f'Need at least {min_samples} samples for training'
            }

    except Exception as exc:
        logger.error(f"Crisis model training failed: {exc}")
        return {'status': 'error', 'message': str(exc)}


@celery.task
def collect_model_feedback(session_id, user_rating, clinical_validation=None):
    """
    Collect feedback for model improvement.
    Called after therapy sessions.
    """
    try:
        from models.auto_training_pipeline import training_pipeline

        # Collect feedback
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            training_pipeline.collect_feedback(
                session_id, user_rating, clinical_validation
            )
        )

        logger.info(f"Feedback collected for session {session_id}")
        return {'status': 'success', 'session_id': session_id}

    except Exception as exc:
        logger.error(f"Feedback collection failed: {exc}")
        return {'status': 'error', 'message': str(exc)}


@celery.task
def emergency_crisis_model_update(training_data):
    """
    Emergency update for crisis model when performance degrades.
    """
    try:
        from models.universal_crisis_predictor import crisis_predictor

        # Train emergency model
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            crisis_predictor.train_emergency_model(training_data)
        )

        if success:
            logger.critical("Emergency crisis model deployed successfully")
            return {'status': 'success', 'emergency': True}
        else:
            logger.error("Emergency model training failed")
            return {'status': 'error', 'emergency': True}

    except Exception as exc:
        logger.error(f"Emergency model update failed: {exc}")
        return {'status': 'error', 'message': str(exc)}


@celery.task
def analyze_model_performance():
    """
    Analyze and report on model performance metrics.
    """
    try:
        from models.ai_orchestrator import ai_orchestrator

        # Get system report
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(ai_orchestrator.get_system_report())

        # Check for concerning metrics
        alerts = []

        # Check crisis detection performance
        crisis_status = report.get('crisis_system', {})
        if not crisis_status.get('custom_model_available'):
            alerts.append('No custom crisis model available - using patterns only')

        # Check provider health
        for provider, health in report.get('providers', {}).items():
            if health['success_rate'] < 0.8:
                alerts.append(f"{provider} provider degraded: {health['success_rate']:.0%} success")

        if alerts:
            logger.warning(f"Model performance alerts: {alerts}")

        return {
            'status': 'success',
            'timestamp': datetime.utcnow().isoformat(),
            'alerts': alerts,
            'summary': report.get('analytics', {}).get('summary', {})
        }

    except Exception as exc:
        logger.error(f"Performance analysis failed: {exc}")
        return {'status': 'error', 'message': str(exc)}


# Register tasks with Celery
__all__ = [
    'check_crisis_model_performance',
    'trigger_model_training',
    'comprehensive_model_retraining',
    'generate_training_report',
    'train_custom_crisis_model',
    'collect_model_feedback',
    'emergency_crisis_model_update',
    'analyze_model_performance'
]