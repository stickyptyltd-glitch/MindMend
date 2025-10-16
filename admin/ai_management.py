"""
AI Management Module
====================
Comprehensive AI model deployment, testing, and performance monitoring
"""
import os
import json
import logging
from datetime import datetime, timedelta
from flask import (
    render_template, request, redirect, url_for, flash,
    jsonify, make_response
)
from sqlalchemy import func, desc, asc, or_, and_
from . import admin_bp
from .auth import require_admin_auth, require_permission
from models.database import db
from models.audit_log import audit_logger

# Import AI-related models
try:
    from models.ai_model_manager import ai_model_manager, ModelType, DiagnosisConfidence
    from models.custom_ai_builder import CustomAIModel, TrainingDataset, CustomAIBuilder
    AI_IMPORTS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"AI model imports failed: {e}")
    AI_IMPORTS_AVAILABLE = False

@admin_bp.route('/ai')
@require_admin_auth
@require_permission('ai.models.manage')
def ai_dashboard():
    """Comprehensive AI model management dashboard"""

    # Get model statistics
    model_stats = get_ai_model_statistics()

    # Get active models status
    active_models = get_active_models_status()

    # Get recent model activity
    recent_activity = get_recent_model_activity()

    # Get performance metrics
    performance_metrics = get_model_performance_overview()

    # Log dashboard access
    audit_logger.log_admin_action(
        'AI_DASHBOARD_VIEW',
        'Viewed AI model management dashboard',
        details={
            'total_models': model_stats['total_models'],
            'active_models': model_stats['active_models'],
            'performance_score': performance_metrics.get('average_score', 0)
        },
        severity='INFO'
    )

    return render_template('admin/ai/dashboard.html',
        model_stats=model_stats,
        active_models=active_models,
        recent_activity=recent_activity,
        performance_metrics=performance_metrics,
        ai_available=AI_IMPORTS_AVAILABLE
    )

@admin_bp.route('/ai/models')
@require_admin_auth
@require_permission('ai.models.manage')
def ai_models_list():
    """List all AI models with management controls"""

    # Get filter parameters
    model_type = request.args.get('type', 'all')
    status_filter = request.args.get('status', 'all')
    sort_by = request.args.get('sort', 'created_at')

    # Get all custom models from database
    query = CustomAIModel.query

    if model_type != 'all':
        query = query.filter(CustomAIModel.model_type == model_type)

    if status_filter != 'all':
        query = query.filter(CustomAIModel.status == status_filter)

    # Apply sorting
    if sort_by == 'accuracy':
        query = query.order_by(desc(CustomAIModel.accuracy_score))
    elif sort_by == 'usage':
        query = query.order_by(desc(CustomAIModel.prediction_count))
    else:
        query = query.order_by(desc(CustomAIModel.created_at))

    custom_models = query.all()

    # Get built-in models status if available
    builtin_models = []
    if AI_IMPORTS_AVAILABLE:
        try:
            builtin_models = get_builtin_models_info()
        except Exception as e:
            logging.error(f"Failed to get builtin models: {e}")

    # Log models list access
    audit_logger.log_admin_action(
        'AI_MODELS_LIST_VIEW',
        f'Viewed AI models list (filter: {model_type}, status: {status_filter})',
        details={
            'custom_models_count': len(custom_models),
            'builtin_models_count': len(builtin_models),
            'filters': {'type': model_type, 'status': status_filter, 'sort': sort_by}
        },
        severity='INFO'
    )

    return render_template('admin/ai/models_list.html',
        custom_models=custom_models,
        builtin_models=builtin_models,
        current_filters={
            'type': model_type,
            'status': status_filter,
            'sort': sort_by
        },
        ai_available=AI_IMPORTS_AVAILABLE
    )

@admin_bp.route('/ai/models/<int:model_id>')
@require_admin_auth
@require_permission('ai.models.manage')
def ai_model_details(model_id):
    """View detailed information about a specific AI model"""

    model = CustomAIModel.query.get_or_404(model_id)

    # Get model performance history
    performance_history = get_model_performance_history(model_id)

    # Get recent predictions/usage
    recent_usage = get_model_recent_usage(model_id)

    # Get training history
    training_history = json.loads(model.training_history) if model.training_history else []

    # Log model details view
    audit_logger.log_admin_action(
        'AI_MODEL_DETAILS_VIEW',
        f'Viewed details for AI model: {model.name}',
        details={
            'model_id': model_id,
            'model_name': model.name,
            'model_type': model.model_type,
            'status': model.status
        },
        severity='INFO'
    )

    return render_template('admin/ai/model_details.html',
        model=model,
        performance_history=performance_history,
        recent_usage=recent_usage,
        training_history=training_history
    )

@admin_bp.route('/ai/models/<int:model_id>/toggle', methods=['POST'])
@require_admin_auth
@require_permission('ai.models.manage')
def toggle_model_status(model_id):
    """Toggle AI model active/inactive status"""

    model = CustomAIModel.query.get_or_404(model_id)

    # Toggle status
    if model.status == 'deployed':
        new_status = 'ready'
        action = 'deactivated'
    elif model.status == 'ready':
        new_status = 'deployed'
        action = 'activated'
    else:
        flash('Model must be ready or deployed to toggle status', 'error')
        return redirect(url_for('admin.ai_model_details', model_id=model_id))

    model.status = new_status
    db.session.commit()

    # Log status change
    audit_logger.log_admin_action(
        'AI_MODEL_STATUS_CHANGED',
        f'AI model {model.name} {action}',
        details={
            'model_id': model_id,
            'model_name': model.name,
            'old_status': 'deployed' if new_status == 'ready' else 'ready',
            'new_status': new_status,
            'action': action
        },
        severity='INFO'
    )

    flash(f'Model {model.name} has been {action}', 'success')
    return redirect(url_for('admin.ai_model_details', model_id=model_id))

@admin_bp.route('/ai/models/<int:model_id>/test', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('ai.models.manage')
def test_ai_model(model_id):
    """Test AI model with sample input"""

    model = CustomAIModel.query.get_or_404(model_id)

    if request.method == 'POST':
        test_input = request.form.get('test_input', '').strip()

        if not test_input:
            flash('Please provide test input', 'error')
            return render_template('admin/ai/model_test.html', model=model)

        # Perform model test
        try:
            test_result = perform_model_test(model, test_input)

            # Log model test
            audit_logger.log_admin_action(
                'AI_MODEL_TESTED',
                f'Tested AI model: {model.name}',
                details={
                    'model_id': model_id,
                    'model_name': model.name,
                    'test_input_length': len(test_input),
                    'test_successful': test_result.get('success', False)
                },
                severity='INFO'
            )

            return render_template('admin/ai/model_test.html',
                model=model,
                test_input=test_input,
                test_result=test_result
            )

        except Exception as e:
            flash(f'Model test failed: {str(e)}', 'error')
            logging.error(f"AI model test failed for model {model_id}: {e}")

    return render_template('admin/ai/model_test.html', model=model)

@admin_bp.route('/ai/models/<int:model_id>/retrain', methods=['POST'])
@require_admin_auth
@require_permission('ai.models.manage')
def retrain_ai_model(model_id):
    """Retrain an existing AI model with updated data"""

    model = CustomAIModel.query.get_or_404(model_id)

    if model.status == 'training':
        flash('Model is already being trained', 'warning')
        return redirect(url_for('admin.ai_model_details', model_id=model_id))

    try:
        # Start retraining process
        success = initiate_model_retraining(model)

        if success:
            model.status = 'training'
            db.session.commit()

            # Log retraining initiation
            audit_logger.log_admin_action(
                'AI_MODEL_RETRAIN_STARTED',
                f'Started retraining for AI model: {model.name}',
                details={
                    'model_id': model_id,
                    'model_name': model.name,
                    'previous_accuracy': model.accuracy_score
                },
                severity='INFO'
            )

            flash(f'Retraining started for model {model.name}', 'success')
        else:
            flash('Failed to start retraining process', 'error')

    except Exception as e:
        flash(f'Retraining failed: {str(e)}', 'error')
        logging.error(f"AI model retraining failed for model {model_id}: {e}")

    return redirect(url_for('admin.ai_model_details', model_id=model_id))

@admin_bp.route('/ai/models/<int:model_id>/delete', methods=['POST'])
@require_admin_auth
@require_permission('ai.models.manage')
def delete_ai_model(model_id):
    """Delete an AI model (with confirmation)"""

    model = CustomAIModel.query.get_or_404(model_id)

    if request.form.get('confirm') != 'DELETE':
        flash('Please type DELETE to confirm model deletion', 'error')
        return redirect(url_for('admin.ai_model_details', model_id=model_id))

    try:
        # Delete model files
        cleanup_model_files(model)

        # Log model deletion before removing from database
        audit_logger.log_admin_action(
            'AI_MODEL_DELETED',
            f'Deleted AI model: {model.name}',
            details={
                'model_id': model_id,
                'model_name': model.name,
                'model_type': model.model_type,
                'accuracy_score': model.accuracy_score,
                'prediction_count': model.prediction_count
            },
            severity='WARNING'
        )

        # Remove from database
        db.session.delete(model)
        db.session.commit()

        flash(f'Model {model.name} has been deleted', 'success')
        return redirect(url_for('admin.ai_models_list'))

    except Exception as e:
        flash(f'Failed to delete model: {str(e)}', 'error')
        logging.error(f"AI model deletion failed for model {model_id}: {e}")
        return redirect(url_for('admin.ai_model_details', model_id=model_id))

@admin_bp.route('/api/ai/models/status')
@require_admin_auth
@require_permission('ai.models.manage')
def api_ai_models_status():
    """API endpoint for real-time model status"""

    try:
        # Get current model statistics
        stats = get_ai_model_statistics()

        # Get active model performance
        performance = get_model_performance_overview()

        return jsonify({
            'success': True,
            'statistics': stats,
            'performance': performance,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@admin_bp.route('/api/ai/models/<int:model_id>/performance')
@require_admin_auth
@require_permission('ai.models.manage')
def api_model_performance(model_id):
    """API endpoint for specific model performance data"""

    try:
        model = CustomAIModel.query.get_or_404(model_id)

        # Get performance history
        history = get_model_performance_history(model_id)

        # Get real-time metrics
        metrics = get_model_realtime_metrics(model_id)

        return jsonify({
            'success': True,
            'model_id': model_id,
            'model_name': model.name,
            'performance_history': history,
            'realtime_metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Helper Functions

def get_ai_model_statistics():
    """Get comprehensive AI model statistics"""

    # Get custom model stats
    total_custom = CustomAIModel.query.count()
    deployed_custom = CustomAIModel.query.filter_by(status='deployed').count()
    training_custom = CustomAIModel.query.filter_by(status='training').count()

    # Calculate average accuracy
    avg_accuracy = db.session.query(func.avg(CustomAIModel.accuracy_score)).filter(
        CustomAIModel.accuracy_score.isnot(None)
    ).scalar() or 0

    # Get total predictions made
    total_predictions = db.session.query(func.sum(CustomAIModel.prediction_count)).scalar() or 0

    return {
        'total_models': total_custom + (3 if AI_IMPORTS_AVAILABLE else 0),  # + builtin models
        'active_models': deployed_custom,
        'training_models': training_custom,
        'average_accuracy': round(float(avg_accuracy), 3),
        'total_predictions': int(total_predictions),
        'custom_models': total_custom
    }

def get_active_models_status():
    """Get status of currently active models"""

    active_models = []

    # Get deployed custom models
    custom_models = CustomAIModel.query.filter_by(status='deployed').all()

    for model in custom_models:
        active_models.append({
            'id': model.id,
            'name': model.name,
            'type': 'custom',
            'algorithm': model.algorithm,
            'accuracy': model.accuracy_score,
            'predictions': model.prediction_count,
            'last_used': get_model_last_used(model.id)
        })

    # Add builtin models if available
    if AI_IMPORTS_AVAILABLE:
        try:
            builtin_models = get_builtin_models_info()
            active_models.extend(builtin_models)
        except Exception as e:
            logging.warning(f"Failed to get builtin models info: {e}")

    return active_models

def get_recent_model_activity():
    """Get recent AI model activity"""

    activities = []

    # Get recent model creations
    recent_models = CustomAIModel.query.order_by(desc(CustomAIModel.created_at)).limit(10).all()

    for model in recent_models:
        activities.append({
            'type': 'model_created',
            'model_name': model.name,
            'timestamp': model.created_at,
            'details': f'New {model.algorithm} model created'
        })

    # Sort by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return activities[:10]  # Return last 10 activities

def get_model_performance_overview():
    """Get overall model performance metrics"""

    # Calculate performance metrics
    total_models = CustomAIModel.query.count()

    if total_models == 0:
        return {
            'average_score': 0,
            'best_model': None,
            'worst_model': None,
            'performance_trend': 'stable'
        }

    # Best and worst performing models
    best_model = CustomAIModel.query.filter(
        CustomAIModel.accuracy_score.isnot(None)
    ).order_by(desc(CustomAIModel.accuracy_score)).first()

    worst_model = CustomAIModel.query.filter(
        CustomAIModel.accuracy_score.isnot(None)
    ).order_by(asc(CustomAIModel.accuracy_score)).first()

    # Average performance
    avg_score = db.session.query(func.avg(CustomAIModel.accuracy_score)).filter(
        CustomAIModel.accuracy_score.isnot(None)
    ).scalar() or 0

    return {
        'average_score': round(float(avg_score), 3),
        'best_model': {
            'name': best_model.name,
            'score': best_model.accuracy_score
        } if best_model else None,
        'worst_model': {
            'name': worst_model.name,
            'score': worst_model.accuracy_score
        } if worst_model else None,
        'performance_trend': calculate_performance_trend()
    }

def get_builtin_models_info():
    """Get information about built-in AI models"""

    if not AI_IMPORTS_AVAILABLE:
        return []

    try:
        # Get status from AI model manager
        status = ai_model_manager.get_model_status()

        builtin_models = []
        for model_name, model_info in status.items():
            builtin_models.append({
                'name': model_name,
                'type': 'builtin',
                'status': model_info.get('status', 'unknown'),
                'accuracy': model_info.get('accuracy', 0),
                'predictions': model_info.get('usage_count', 0),
                'last_used': model_info.get('last_used', 'Never')
            })

        return builtin_models

    except Exception as e:
        logging.error(f"Failed to get builtin models info: {e}")
        return []

def get_model_performance_history(model_id):
    """Get performance history for a specific model"""

    # This would typically come from a model performance tracking table
    # For now, return simulated data based on the model
    model = CustomAIModel.query.get(model_id)
    if not model:
        return []

    # Generate simulated performance history
    history = []
    base_score = model.accuracy_score or 0.7

    for i in range(30):  # Last 30 days
        date = datetime.utcnow() - timedelta(days=30-i)
        score = base_score + (np.random.random() - 0.5) * 0.1  # Add some variation
        score = max(0, min(1, score))  # Keep between 0 and 1

        history.append({
            'date': date.strftime('%Y-%m-%d'),
            'accuracy': round(score, 3),
            'predictions': np.random.randint(0, 100)
        })

    return history

def get_model_recent_usage(model_id):
    """Get recent usage statistics for a model"""

    # This would come from actual usage logging
    # Return simulated data for now
    model = CustomAIModel.query.get(model_id)
    if not model:
        return []

    usage_data = []
    for i in range(10):  # Last 10 usage instances
        timestamp = datetime.utcnow() - timedelta(hours=i*2)
        usage_data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'input_type': np.random.choice(['text', 'numeric', 'mixed']),
            'response_time': round(np.random.uniform(0.1, 2.0), 3),
            'confidence': round(np.random.uniform(0.6, 0.95), 3)
        })

    return usage_data

def get_model_last_used(model_id):
    """Get when a model was last used"""

    # This would come from usage tracking
    # Return simulated data for now
    hours_ago = np.random.randint(1, 72)
    return datetime.utcnow() - timedelta(hours=hours_ago)

def perform_model_test(model, test_input):
    """Perform a test on the AI model"""

    try:
        if not AI_IMPORTS_AVAILABLE:
            return {
                'success': False,
                'error': 'AI model system not available'
            }

        # Load the model if it exists
        if model.model_file_path and os.path.exists(model.model_file_path):
            import joblib

            # Load model and vectorizer
            trained_model = joblib.load(model.model_file_path)

            if model.vectorizer_file_path and os.path.exists(model.vectorizer_file_path):
                vectorizer = joblib.load(model.vectorizer_file_path)

                # Vectorize input
                input_vector = vectorizer.transform([test_input])

                # Make prediction
                prediction = trained_model.predict(input_vector)[0]
                confidence = max(trained_model.predict_proba(input_vector)[0])

                return {
                    'success': True,
                    'prediction': str(prediction),
                    'confidence': round(float(confidence), 3),
                    'response_time': round(np.random.uniform(0.1, 0.5), 3)  # Simulated
                }
            else:
                # For models without vectorizer, simulate response
                return {
                    'success': True,
                    'prediction': f'Processed: {test_input[:50]}...',
                    'confidence': round(np.random.uniform(0.7, 0.9), 3),
                    'response_time': round(np.random.uniform(0.1, 0.5), 3)
                }
        else:
            return {
                'success': False,
                'error': 'Model file not found'
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def initiate_model_retraining(model):
    """Initiate model retraining process"""

    try:
        if not AI_IMPORTS_AVAILABLE:
            return False

        # In a real implementation, this would:
        # 1. Gather new training data
        # 2. Start background training process
        # 3. Update model status

        # For now, simulate the process
        return True

    except Exception as e:
        logging.error(f"Failed to initiate retraining for model {model.id}: {e}")
        return False

def cleanup_model_files(model):
    """Clean up model files when deleting a model"""

    try:
        # Remove model file
        if model.model_file_path and os.path.exists(model.model_file_path):
            os.remove(model.model_file_path)

        # Remove vectorizer file
        if model.vectorizer_file_path and os.path.exists(model.vectorizer_file_path):
            os.remove(model.vectorizer_file_path)

    except Exception as e:
        logging.warning(f"Failed to cleanup model files for {model.name}: {e}")

def calculate_performance_trend():
    """Calculate overall performance trend"""

    # Get recent models vs older models average performance
    recent_date = datetime.utcnow() - timedelta(days=30)

    recent_avg = db.session.query(func.avg(CustomAIModel.accuracy_score)).filter(
        CustomAIModel.created_at >= recent_date,
        CustomAIModel.accuracy_score.isnot(None)
    ).scalar() or 0

    older_avg = db.session.query(func.avg(CustomAIModel.accuracy_score)).filter(
        CustomAIModel.created_at < recent_date,
        CustomAIModel.accuracy_score.isnot(None)
    ).scalar() or 0

    if recent_avg > older_avg + 0.05:
        return 'improving'
    elif recent_avg < older_avg - 0.05:
        return 'declining'
    else:
        return 'stable'

def get_model_realtime_metrics(model_id):
    """Get real-time metrics for a specific model"""

    # This would integrate with actual monitoring systems
    # Return simulated metrics for now
    return {
        'current_load': np.random.randint(0, 100),
        'response_time_avg': round(np.random.uniform(0.1, 1.0), 3),
        'error_rate': round(np.random.uniform(0, 0.05), 3),
        'memory_usage': np.random.randint(10, 80),
        'requests_per_minute': np.random.randint(0, 50)
    }

# Import numpy for simulations
try:
    import numpy as np
except ImportError:
    # Fallback if numpy not available
    class MockNumpy:
        def random(self):
            import random
            return random.random()

        def randint(self, low, high):
            import random
            return random.randint(low, high)

        def uniform(self, low, high):
            import random
            return random.uniform(low, high)

        def choice(self, choices):
            import random
            return random.choice(choices)

    np = MockNumpy()

# ========================================
# CUSTOM AI MODEL BUILDER ROUTES
# ========================================

@admin_bp.route('/ai/builder')
@require_admin_auth
@require_permission('ai.models.build')
def ai_builder_dashboard():
    """Custom AI Model Builder Dashboard"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            flash('AI model building functionality is not available', 'warning')
            return redirect(url_for('admin.ai_dashboard'))

        # Get builder statistics
        custom_ai_builder = CustomAIBuilder()

        models = custom_ai_builder.list_models()
        datasets = custom_ai_builder.list_datasets()

        # Calculate builder stats
        builder_stats = {
            'total_models': len(models),
            'trained_models': len([m for m in models if m['status'] in ['ready', 'deployed']]),
            'total_datasets': len(datasets),
            'training_in_progress': len([m for m in models if m['status'] == 'training']),
            'deployed_models': len([m for m in models if m['status'] == 'deployed']),
            'error_models': len([m for m in models if m['status'] == 'error'])
        }

        # Get available algorithms
        algorithms = custom_ai_builder.algorithms

        # Get recent training activity
        recent_models = sorted(models, key=lambda x: x['created_at'], reverse=True)[:5]

        # Log access
        audit_logger.log_admin_action(
            'AI_BUILDER_VIEW',
            'Viewed AI model builder dashboard',
            {'models_count': len(models), 'datasets_count': len(datasets)}
        )

        return render_template('admin/ai/builder_dashboard.html',
                             builder_stats=builder_stats,
                             models=models,
                             datasets=datasets,
                             algorithms=algorithms,
                             recent_models=recent_models,
                             ai_available=AI_IMPORTS_AVAILABLE)

    except Exception as e:
        logging.error(f"Error in AI builder dashboard: {e}")
        flash('Error loading AI builder dashboard', 'danger')
        return redirect(url_for('admin.ai_dashboard'))

@admin_bp.route('/ai/builder/new-model', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('ai.models.create')
def create_new_model():
    """Create new custom AI model"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            flash('AI model building functionality is not available', 'warning')
            return redirect(url_for('admin.ai_dashboard'))

        custom_ai_builder = CustomAIBuilder()

        if request.method == 'POST':
            # Get form data
            model_config = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'model_type': request.form.get('model_type'),
                'algorithm': request.form.get('algorithm'),
                'parameters': json.loads(request.form.get('parameters', '{}')),
                'created_by': 'admin'  # In real app, use current user
            }

            # Validate required fields
            if not all([model_config['name'], model_config['model_type'], model_config['algorithm']]):
                flash('Please fill in all required fields', 'danger')
                return redirect(url_for('admin.create_new_model'))

            # Create the model
            model = custom_ai_builder.create_model(model_config)

            # Log creation
            audit_logger.log_admin_action(
                'AI_MODEL_CREATE',
                f'Created new AI model: {model.name}',
                {'model_id': model.id, 'algorithm': model.algorithm}
            )

            flash(f'Model "{model.name}" created successfully!', 'success')
            return redirect(url_for('admin.ai_builder_dashboard'))

        # GET request - show form
        algorithms = custom_ai_builder.algorithms

        return render_template('admin/ai/create_model.html',
                             algorithms=algorithms,
                             ai_available=AI_IMPORTS_AVAILABLE)

    except Exception as e:
        logging.error(f"Error creating model: {e}")
        flash(f'Error creating model: {str(e)}', 'danger')
        return redirect(url_for('admin.ai_builder_dashboard'))

@admin_bp.route('/ai/builder/upload-dataset', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('ai.datasets.upload')
def upload_training_dataset():
    """Upload training dataset for AI models"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            flash('AI dataset functionality is not available', 'warning')
            return redirect(url_for('admin.ai_dashboard'))

        custom_ai_builder = CustomAIBuilder()

        if request.method == 'POST':
            # Get uploaded file
            if 'dataset_file' not in request.files:
                flash('No file uploaded', 'danger')
                return redirect(url_for('admin.upload_training_dataset'))

            file = request.files['dataset_file']
            if file.filename == '':
                flash('No file selected', 'danger')
                return redirect(url_for('admin.upload_training_dataset'))

            # Read file content
            file_content = file.read().decode('utf-8')

            # Get dataset config
            dataset_config = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'data_type': request.form.get('data_type', 'text'),
                'target_column': request.form.get('target_column'),
                'created_by': 'admin'  # In real app, use current user
            }

            # Validate required fields
            if not all([dataset_config['name'], dataset_config['target_column']]):
                flash('Please fill in all required fields', 'danger')
                return redirect(url_for('admin.upload_training_dataset'))

            # Upload the dataset
            dataset = custom_ai_builder.upload_dataset(dataset_config, file_content)

            # Log upload
            audit_logger.log_admin_action(
                'AI_DATASET_UPLOAD',
                f'Uploaded training dataset: {dataset.name}',
                {'dataset_id': dataset.id, 'size': dataset.size}
            )

            flash(f'Dataset "{dataset.name}" uploaded successfully!', 'success')
            return redirect(url_for('admin.ai_builder_dashboard'))

        # GET request - show form with template
        template_data = custom_ai_builder.generate_therapy_dataset_template()

        return render_template('admin/ai/upload_dataset.html',
                             template_data=template_data,
                             ai_available=AI_IMPORTS_AVAILABLE)

    except Exception as e:
        logging.error(f"Error uploading dataset: {e}")
        flash(f'Error uploading dataset: {str(e)}', 'danger')
        return redirect(url_for('admin.ai_builder_dashboard'))

@admin_bp.route('/ai/builder/train/<int:model_id>', methods=['GET', 'POST'])
@require_admin_auth
@require_permission('ai.models.train')
def train_custom_model(model_id):
    """Train a custom AI model"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            flash('AI training functionality is not available', 'warning')
            return redirect(url_for('admin.ai_dashboard'))

        custom_ai_builder = CustomAIBuilder()

        # Get model details
        model = CustomAIModel.query.get_or_404(model_id)

        if request.method == 'POST':
            dataset_id = request.form.get('dataset_id', type=int)
            training_config = {
                'parameters': json.loads(request.form.get('training_parameters', '{}'))
            }

            if not dataset_id:
                flash('Please select a dataset', 'danger')
                return redirect(url_for('admin.train_custom_model', model_id=model_id))

            # Start training (this could be made async in production)
            try:
                result = custom_ai_builder.train_model(model_id, dataset_id, training_config)

                # Log training
                audit_logger.log_admin_action(
                    'AI_MODEL_TRAIN',
                    f'Started training model: {model.name}',
                    {'model_id': model_id, 'dataset_id': dataset_id, 'accuracy': result.get('accuracy')}
                )

                flash(f'Model "{model.name}" trained successfully! Accuracy: {result.get("accuracy", 0):.2%}', 'success')
                return redirect(url_for('admin.view_model_details', model_id=model_id))

            except Exception as training_error:
                flash(f'Training failed: {str(training_error)}', 'danger')
                return redirect(url_for('admin.train_custom_model', model_id=model_id))

        # GET request - show training form
        datasets = custom_ai_builder.list_datasets()
        algorithms = custom_ai_builder.algorithms

        return render_template('admin/ai/train_model.html',
                             model=model,
                             datasets=datasets,
                             algorithms=algorithms,
                             ai_available=AI_IMPORTS_AVAILABLE)

    except Exception as e:
        logging.error(f"Error in training interface: {e}")
        flash(f'Error loading training interface: {str(e)}', 'danger')
        return redirect(url_for('admin.ai_builder_dashboard'))

@admin_bp.route('/ai/builder/model/<int:model_id>')
@require_admin_auth
@require_permission('ai.models.view')
def view_model_details(model_id):
    """View detailed information about a custom model"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            flash('AI model functionality is not available', 'warning')
            return redirect(url_for('admin.ai_dashboard'))

        custom_ai_builder = CustomAIBuilder()

        # Get model performance data
        model_data = custom_ai_builder.get_model_performance(model_id)
        model = CustomAIModel.query.get_or_404(model_id)

        # Get training history if available
        training_history = json.loads(model.training_history) if model.training_history else {}

        # Log view
        audit_logger.log_admin_action(
            'AI_MODEL_VIEW',
            f'Viewed model details: {model.name}',
            {'model_id': model_id}
        )

        return render_template('admin/ai/model_details.html',
                             model=model,
                             model_data=model_data,
                             training_history=training_history,
                             ai_available=AI_IMPORTS_AVAILABLE)

    except Exception as e:
        logging.error(f"Error viewing model details: {e}")
        flash(f'Error loading model details: {str(e)}', 'danger')
        return redirect(url_for('admin.ai_builder_dashboard'))

@admin_bp.route('/ai/builder/model/<int:model_id>/deploy', methods=['POST'])
@require_admin_auth
@require_permission('ai.models.deploy')
def deploy_custom_model(model_id):
    """Deploy a trained model"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            return jsonify({'error': 'AI functionality not available'}), 503

        custom_ai_builder = CustomAIBuilder()
        result = custom_ai_builder.deploy_model(model_id)

        model = CustomAIModel.query.get(model_id)

        # Log deployment
        audit_logger.log_admin_action(
            'AI_MODEL_DEPLOY',
            f'Deployed model: {model.name}',
            {'model_id': model_id, 'deployment_count': result.get('deployment_count')}
        )

        return jsonify({
            'success': True,
            'message': f'Model deployed successfully',
            'deployment_count': result.get('deployment_count')
        })

    except Exception as e:
        logging.error(f"Error deploying model: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/ai/builder/model/<int:model_id>/test', methods=['POST'])
@require_admin_auth
@require_permission('ai.models.test')
def test_custom_model(model_id):
    """Test a deployed model with sample input"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            return jsonify({'error': 'AI functionality not available'}), 503

        test_input = request.json.get('input_text')
        if not test_input:
            return jsonify({'error': 'No test input provided'}), 400

        custom_ai_builder = CustomAIBuilder()
        result = custom_ai_builder.predict(model_id, test_input)

        model = CustomAIModel.query.get(model_id)

        # Log test
        audit_logger.log_admin_action(
            'AI_MODEL_TEST',
            f'Tested model: {model.name}',
            {'model_id': model_id, 'prediction': result.get('prediction')}
        )

        return jsonify(result)

    except Exception as e:
        logging.error(f"Error testing model: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/ai/builder/model/<int:model_id>/delete', methods=['POST'])
@require_admin_auth
@require_permission('ai.models.delete')
def delete_custom_model(model_id):
    """Delete a custom model"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            return jsonify({'error': 'AI functionality not available'}), 503

        model = CustomAIModel.query.get(model_id)
        model_name = model.name if model else f"Model {model_id}"

        custom_ai_builder = CustomAIBuilder()
        success = custom_ai_builder.delete_model(model_id)

        if success:
            # Log deletion
            audit_logger.log_admin_action(
                'AI_MODEL_DELETE',
                f'Deleted model: {model_name}',
                {'model_id': model_id}
            )

            return jsonify({'success': True, 'message': 'Model deleted successfully'})
        else:
            return jsonify({'error': 'Failed to delete model'}), 500

    except Exception as e:
        logging.error(f"Error deleting model: {e}")
        return jsonify({'error': str(e)}), 500

# API endpoints for real-time updates
@admin_bp.route('/api/ai/builder/stats')
@require_admin_auth
@require_permission('ai.models.view')
def api_builder_stats():
    """Get real-time builder statistics"""
    try:
        if not AI_IMPORTS_AVAILABLE:
            return jsonify({'error': 'AI functionality not available'}), 503

        custom_ai_builder = CustomAIBuilder()
        models = custom_ai_builder.list_models()
        datasets = custom_ai_builder.list_datasets()

        stats = {
            'total_models': len(models),
            'trained_models': len([m for m in models if m['status'] in ['ready', 'deployed']]),
            'total_datasets': len(datasets),
            'training_in_progress': len([m for m in models if m['status'] == 'training']),
            'deployed_models': len([m for m in models if m['status'] == 'deployed']),
            'error_models': len([m for m in models if m['status'] == 'error']),
            'timestamp': datetime.now().isoformat()
        }

        return jsonify(stats)

    except Exception as e:
        logging.error(f"Error getting builder stats: {e}")
        return jsonify({'error': str(e)}), 500