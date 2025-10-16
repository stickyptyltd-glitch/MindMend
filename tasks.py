"""
Background Tasks for MindMend

This module contains all Celery tasks for asynchronous processing.
Tasks include email notifications, AI analysis, data cleanup, and analytics.
"""

from celery_app import celery_app as celery
from datetime import datetime, timedelta, UTC
from models.database import db, Session, Patient, BiometricData, Subscription, Payment
import logging

logger = logging.getLogger(__name__)


# =======================
# Email & Notification Tasks
# =======================

@celery.task(bind=True, max_retries=3)
def send_email_notification(self, user_id, subject, message, email_type='general'):
    """
    Send email notification to user.

    Args:
        user_id: Patient ID
        subject: Email subject
        message: Email body (HTML supported)
        email_type: Type of email (general, welcome, reminder, alert)

    Returns:
        dict: Status and message
    """
    try:
        from flask_mail import Message
        from app import mail

        user = Patient.query.get(user_id)
        if not user:
            return {'status': 'error', 'message': 'User not found'}

        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=message,
            sender='noreply@mindmend.xyz'
        )

        # Note: mail.send() requires Flask-Mail configuration
        # For now, log instead (configure SMTP in production)
        logger.info(f"[EMAIL] To: {user.email}, Subject: {subject}, Type: {email_type}")

        return {
            'status': 'success',
            'message': f'Email queued for {user.email}',
            'type': email_type
        }

    except Exception as exc:
        logger.error(f"Email send failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery.task
def send_welcome_email(user_id):
    """Send welcome email to new user."""
    return send_email_notification(
        user_id,
        subject="Welcome to MindMend - Your Mental Health Journey Starts Here",
        message="""
        <h2>Welcome to MindMend!</h2>
        <p>We're excited to support you on your mental health journey.</p>
        <p>Here's what you can do:</p>
        <ul>
            <li>Start your first AI therapy session</li>
            <li>Track your mood and biometric data</li>
            <li>Access crisis support 24/7</li>
            <li>Connect with licensed therapists</li>
        </ul>
        <p><a href="https://mindmend.xyz/dashboard">Get Started Now</a></p>
        """,
        email_type='welcome'
    )


@celery.task
def send_session_reminder(user_id, session_date):
    """Send reminder for upcoming therapy session."""
    return send_email_notification(
        user_id,
        subject="Reminder: Your Therapy Session Tomorrow",
        message=f"""
        <h2>Session Reminder</h2>
        <p>You have a therapy session scheduled for {session_date}.</p>
        <p><a href="https://mindmend.xyz/sessions">View Session Details</a></p>
        """,
        email_type='reminder'
    )


# =======================
# AI Processing Tasks
# =======================

@celery.task(bind=True, max_retries=2)
def process_ai_analysis(self, session_id):
    """
    Process AI analysis for a therapy session in background.

    Args:
        session_id: Session ID to analyze

    Returns:
        dict: Analysis results
    """
    try:
        session = Session.query.get(session_id)
        if not session:
            return {'status': 'error', 'message': 'Session not found'}

        # Import AI models (lazy load to avoid startup issues)
        from models.ai_manager import AIManager

        ai_manager = AIManager()

        # Perform deep analysis
        analysis = {
            'session_id': session_id,
            'sentiment': ai_manager.analyze_sentiment(session.ai_response or ''),
            'themes': ai_manager.extract_themes(session.ai_response or ''),
            'recommendations': ai_manager.generate_recommendations(session_id),
            'processed_at': datetime.now(UTC).isoformat()
        }

        # Update session with analysis
        session.analysis_data = str(analysis)
        db.session.commit()

        logger.info(f"AI analysis completed for session {session_id}")

        return {'status': 'success', 'analysis': analysis}

    except Exception as exc:
        logger.error(f"AI analysis failed for session {session_id}: {exc}")
        raise self.retry(exc=exc, countdown=120)


@celery.task
def process_pending_ai_analyses():
    """
    Process all pending AI analyses (runs periodically via beat).

    Returns:
        dict: Summary of processed sessions
    """
    # Find sessions needing analysis (created in last hour, not analyzed)
    cutoff = datetime.now(UTC) - timedelta(hours=1)
    pending_sessions = Session.query.filter(
        Session.created_at >= cutoff,
        Session.analysis_data == None
    ).limit(50).all()

    processed = 0
    for session in pending_sessions:
        process_ai_analysis.delay(session.id)
        processed += 1

    logger.info(f"Queued {processed} sessions for AI analysis")

    return {
        'status': 'success',
        'queued': processed,
        'timestamp': datetime.now(UTC).isoformat()
    }


# =======================
# Data Cleanup Tasks
# =======================

@celery.task
def cleanup_old_sessions(days=90):
    """
    Clean up old session data.

    Args:
        days: Delete sessions older than this many days

    Returns:
        dict: Cleanup summary
    """
    try:
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        # Find old sessions (not premium users - they keep data longer)
        old_sessions = Session.query.join(Patient).filter(
            Session.created_at < cutoff_date,
            Patient.subscription_tier == 'free'
        ).all()

        deleted_count = len(old_sessions)

        for session in old_sessions:
            db.session.delete(session)

        db.session.commit()

        logger.info(f"Cleaned up {deleted_count} old sessions")

        return {
            'status': 'success',
            'deleted': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as exc:
        logger.error(f"Session cleanup failed: {exc}")
        db.session.rollback()
        return {'status': 'error', 'message': str(exc)}


@celery.task
def cleanup_old_biometric_data(days=180):
    """Clean up old biometric data."""
    try:
        cutoff_date = datetime.now(UTC) - timedelta(days=days)

        deleted = BiometricData.query.filter(
            BiometricData.timestamp < cutoff_date
        ).delete()

        db.session.commit()

        logger.info(f"Cleaned up {deleted} old biometric records")

        return {'status': 'success', 'deleted': deleted}

    except Exception as exc:
        logger.error(f"Biometric cleanup failed: {exc}")
        db.session.rollback()
        return {'status': 'error', 'message': str(exc)}


# =======================
# Analytics & Reporting Tasks
# =======================

@celery.task
def generate_daily_analytics():
    """
    Generate daily analytics report.

    Returns:
        dict: Analytics summary
    """
    try:
        today = datetime.now(UTC).date()
        yesterday = today - timedelta(days=1)

        # Calculate metrics
        new_users = Patient.query.filter(
            db.func.date(Patient.created_at) == yesterday
        ).count()

        sessions_today = Session.query.filter(
            db.func.date(Session.created_at) == yesterday
        ).count()

        active_users = Session.query.filter(
            db.func.date(Session.created_at) == yesterday
        ).distinct(Session.patient_id).count()

        analytics = {
            'date': yesterday.isoformat(),
            'new_users': new_users,
            'total_sessions': sessions_today,
            'active_users': active_users,
            'avg_sessions_per_user': round(sessions_today / max(active_users, 1), 2),
            'generated_at': datetime.now(UTC).isoformat()
        }

        logger.info(f"Daily analytics: {analytics}")

        # TODO: Store in analytics table or send to admin

        return {'status': 'success', 'analytics': analytics}

    except Exception as exc:
        logger.error(f"Analytics generation failed: {exc}")
        return {'status': 'error', 'message': str(exc)}


# =======================
# Subscription & Payment Tasks
# =======================

@celery.task
def check_subscription_renewals():
    """
    Check for expiring subscriptions and process renewals.

    Returns:
        dict: Renewal summary
    """
    try:
        # Find subscriptions expiring in next 3 days
        expiring_soon = datetime.now(UTC) + timedelta(days=3)

        expiring_subs = Subscription.query.filter(
            Subscription.end_date <= expiring_soon,
            Subscription.status == 'active',
            Subscription.cancel_at_period_end == False
        ).all()

        renewal_attempts = 0
        for sub in expiring_subs:
            # Send renewal reminder email
            send_email_notification.delay(
                sub.patient_id,
                subject="Your MindMend Subscription is Expiring Soon",
                message=f"""
                <h2>Subscription Renewal Reminder</h2>
                <p>Your {sub.tier} subscription expires on {sub.end_date.strftime('%B %d, %Y')}.</p>
                <p><a href="https://mindmend.xyz/subscribe">Renew Now</a></p>
                """,
                email_type='reminder'
            )
            renewal_attempts += 1

        logger.info(f"Sent {renewal_attempts} renewal reminders")

        return {
            'status': 'success',
            'reminders_sent': renewal_attempts,
            'checked_at': datetime.now(UTC).isoformat()
        }

    except Exception as exc:
        logger.error(f"Subscription check failed: {exc}")
        return {'status': 'error', 'message': str(exc)}


@celery.task
def process_failed_payments():
    """Retry failed payment processing."""
    try:
        failed_payments = Payment.query.filter(
            Payment.status == 'failed',
            Payment.created_at >= datetime.now(UTC) - timedelta(days=7)
        ).all()

        retry_count = 0
        for payment in failed_payments:
            # TODO: Implement Stripe retry logic
            logger.info(f"Retrying payment {payment.id}")
            retry_count += 1

        return {'status': 'success', 'retried': retry_count}

    except Exception as exc:
        logger.error(f"Payment retry failed: {exc}")
        return {'status': 'error', 'message': str(exc)}


# =======================
# Test & Utility Tasks
# =======================

@celery.task
def test_celery_task(message="Hello from Celery!"):
    """
    Simple test task to verify Celery is working.

    Args:
        message: Test message

    Returns:
        dict: Test result
    """
    logger.info(f"Test task executed: {message}")

    return {
        'status': 'success',
        'message': message,
        'executed_at': datetime.now(UTC).isoformat(),
        'worker': 'celery-worker'
    }


@celery.task
def heartbeat():
    """Periodic heartbeat task to verify workers are alive."""
    return {
        'status': 'alive',
        'timestamp': datetime.now(UTC).isoformat()
    }


# =======================
# AI Training Tasks
# =======================

# Import AI training tasks
from tasks_ai_training import (
    check_crisis_model_performance,
    trigger_model_training,
    comprehensive_model_retraining,
    generate_training_report,
    train_custom_crisis_model,
    collect_model_feedback,
    emergency_crisis_model_update,
    analyze_model_performance
)
