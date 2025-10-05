
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import logging
from datetime import datetime

ai_models_bp = Blueprint('ai_models', __name__)

@ai_models_bp.route("/ai-models")
@login_required
def ai_models_page():
    try:
        from models.ai_model_manager import ai_model_manager
        status = ai_model_manager.get_model_status()
        return render_template("ai_models.html", status=status)
    except Exception as e:
        logging.error(f"AI models page error: {e}")
        return render_template("ai_models.html", status={"model_details": [], "total_models": 0, "active_models": 0}, error="Failed to load models"), 500

@ai_models_bp.route("/api/ai-models/toggle", methods=["POST"])
@login_required
def api_toggle_ai_model():
    try:
        data = request.get_json(force=True)
        name = data.get('name')
        active = bool(data.get('active'))
        from models.ai_model_manager import ai_model_manager
        if name not in ai_model_manager.models:
            return jsonify({"error": "Unknown model"}), 400
        if active and name not in ai_model_manager.active_models:
            ai_model_manager.active_models.append(name)
        if not active and name in ai_model_manager.active_models:
            ai_model_manager.active_models.remove(name)
        return jsonify({"success": True, "active_models": ai_model_manager.active_models})
    except Exception as e:
        logging.error(f"Toggle AI model error: {e}")
        return jsonify({"error": "Failed to toggle model"}), 500

@ai_models_bp.route("/api/ai-models/status")
def api_ai_models_status():
    """Get status of available AI models"""
    try:
        from models.ai_model_manager import ai_model_manager
        status = ai_model_manager.get_model_status()
        
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"AI models status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_models_bp.route("/api/ai-models/diagnose", methods=["POST"])
def api_ai_diagnose():
    """Perform AI-powered diagnosis using ensemble models"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract patient data
        patient_data = {
            'age': data.get('age', 30),
            'gender': data.get('gender'),
            'chief_complaint': data.get('chief_complaint', ''),
            'symptoms': data.get('symptoms', {}),
            'behavioral_data': data.get('behavioral_data', {}),
            'assessment_scores': data.get('assessment_scores', {})
        }
        
        # Get diagnosis from ensemble
        from models.ai_model_manager import ai_model_manager
        diagnosis = ai_model_manager.diagnose_with_ensemble(patient_data)
        
        # Get treatment recommendations
        if diagnosis.get('primary_diagnosis'):
            from models.therapy_ai_integration import therapy_ai_integration
            treatment_plan = therapy_ai_integration.treatment_recommender.generate_personalized_treatment_plan(
                diagnosis=diagnosis,
                patient_profile=patient_data,
                preferences=data.get('preferences', {})
            )
            
            diagnosis['treatment_plan'] = {
                'primary_modality': treatment_plan.primary_modality.value,
                'secondary_modalities': [m.value for m in treatment_plan.secondary_modalities],
                'intensity': treatment_plan.intensity.value,
                'duration_weeks': treatment_plan.duration_weeks,
                'activities': treatment_plan.activities[:5],  # Top 5 activities
                'confidence': treatment_plan.confidence_score
            }
        
        return jsonify({
            'success': True,
            'diagnosis': diagnosis,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logging.error(f"AI diagnosis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
