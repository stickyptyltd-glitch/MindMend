"""
Clinical Outcomes API Blueprint
Minimal API for grant demonstration and clinical assessment integration

Routes:
- POST /api/v1/assessments/phq9 - Submit PHQ-9 assessment
- POST /api/v1/assessments/gad7 - Submit GAD-7 assessment
- POST /api/v1/assessments/pss10 - Submit PSS-10 assessment
- GET /api/v1/outcomes/patient/<patient_id> - Get patient outcomes
- GET /api/v1/outcomes/treatment-effectiveness - Get treatment effectiveness data
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, UTC
from models.database import db, ClinicalAssessment, OutcomeMeasure, Patient
from models.clinical_assessment_tools import assessment_manager
from models.clinical_outcomes_analyzer import outcomes_analyzer
import logging

logger = logging.getLogger(__name__)

clinical_api_bp = Blueprint('clinical_api', __name__, url_prefix='/api/v1')

@clinical_api_bp.route('/assessments/phq9', methods=['POST'])
@login_required
def submit_phq9():
    """
    Submit PHQ-9 Depression Assessment
    """
    try:
        data = request.get_json()

        if not data or 'responses' not in data:
            return jsonify({"error": "Missing 'responses' in request"}), 400

        responses = data['responses']
        patient_id = data.get('patient_id', current_user.id)

        if len(responses) != 9:
            return jsonify({"error": "PHQ-9 requires exactly 9 responses"}), 400

        if not all(isinstance(r, int) and 0 <= r <= 3 for r in responses):
            return jsonify({"error": "All responses must be integers between 0-3"}), 400

        result = assessment_manager.calculate_score('PHQ-9', responses)

        assessment = ClinicalAssessment(
            patient_id=patient_id,
            assessment_type='phq9',
            total_score=result.total_score,
            max_score=result.max_score,
            severity_level=result.severity_level.value,
            item_responses=str(responses),
            clinical_interpretation=result.clinical_interpretation,
            recommended_actions=str(result.recommended_actions),
            risk_flags=str(result.risk_flags),
            administered_by=f"user_{current_user.id}",
            completed_at=datetime.now(UTC)
        )

        db.session.add(assessment)

        outcome = OutcomeMeasure(
            patient_id=patient_id,
            outcome_type='symptom_reduction',
            outcome_name='PHQ-9',
            baseline_value=result.total_score, # Assuming this is the first assessment
            current_value=result.total_score,
            measurement_date=datetime.now(UTC),
            baseline_date=datetime.now(UTC)
        )

        db.session.add(outcome)
        db.session.commit()

        logger.info(f"PHQ-9 assessment submitted: patient_id={patient_id}, score={result.total_score}")

        return jsonify({
            "assessment_id": assessment.id,
            "outcome_id": outcome.id,
            "score": result.total_score,
            "severity": result.severity_level.value,
            "interpretation": result.clinical_interpretation,
            "recommendations": result.recommended_actions,
            "timestamp": assessment.completed_at.isoformat(),
            "follow_up_recommended": result.total_score >= 10
        }), 201

    except Exception as e:
        logger.error(f"Error submitting PHQ-9: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to submit assessment", "details": str(e)}), 500


@clinical_api_bp.route('/assessments/gad7', methods=['POST'])
@login_required
def submit_gad7():
    """
    Submit GAD-7 Anxiety Assessment
    """
    try:
        data = request.get_json()

        if not data or 'responses' not in data:
            return jsonify({"error": "Missing 'responses' in request"}), 400

        responses = data['responses']
        patient_id = data.get('patient_id', current_user.id)

        if len(responses) != 7:
            return jsonify({"error": "GAD-7 requires exactly 7 responses"}), 400

        if not all(isinstance(r, int) and 0 <= r <= 3 for r in responses):
            return jsonify({"error": "All responses must be integers between 0-3"}), 400

        result = assessment_manager.calculate_score('GAD-7', responses)

        assessment = ClinicalAssessment(
            patient_id=patient_id,
            assessment_type='gad7',
            total_score=result.total_score,
            max_score=result.max_score,
            severity_level=result.severity_level.value,
            item_responses=str(responses),
            clinical_interpretation=result.clinical_interpretation,
            recommended_actions=str(result.recommended_actions),
            risk_flags=str(result.risk_flags),
            administered_by=f"user_{current_user.id}",
            completed_at=datetime.now(UTC)
        )

        db.session.add(assessment)

        outcome = OutcomeMeasure(
            patient_id=patient_id,
            outcome_type='symptom_reduction',
            outcome_name='GAD-7',
            baseline_value=result.total_score,
            current_value=result.total_score,
            measurement_date=datetime.now(UTC),
            baseline_date=datetime.now(UTC)
        )

        db.session.add(outcome)
        db.session.commit()

        logger.info(f"GAD-7 assessment submitted: patient_id={patient_id}, score={result.total_score}")

        return jsonify({
            "assessment_id": assessment.id,
            "outcome_id": outcome.id,
            "score": result.total_score,
            "severity": result.severity_level.value,
            "interpretation": result.clinical_interpretation,
            "recommendations": result.recommended_actions,
            "timestamp": assessment.completed_at.isoformat(),
            "follow_up_recommended": result.total_score >= 10
        }), 201

    except Exception as e:
        logger.error(f"Error submitting GAD-7: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to submit assessment", "details": str(e)}), 500


@clinical_api_bp.route('/assessments/pss10', methods=['POST'])
@login_required
def submit_pss10():
    """
    Submit PSS-10 Stress Assessment
    """
    try:
        data = request.get_json()

        if not data or 'responses' not in data:
            return jsonify({"error": "Missing 'responses' in request"}), 400

        responses = data['responses']
        patient_id = data.get('patient_id', current_user.id)

        if len(responses) != 10:
            return jsonify({"error": "PSS-10 requires exactly 10 responses"}), 400

        if not all(isinstance(r, int) and 0 <= r <= 4 for r in responses):
            return jsonify({"error": "All responses must be integers between 0-4"}), 400

        result = assessment_manager.calculate_score('PSS-10', responses)

        assessment = ClinicalAssessment(
            patient_id=patient_id,
            assessment_type='pss10',
            total_score=result.total_score,
            max_score=result.max_score,
            severity_level=result.severity_level.value,
            item_responses=str(responses),
            clinical_interpretation=result.clinical_interpretation,
            recommended_actions=str(result.recommended_actions),
            risk_flags=str(result.risk_flags),
            administered_by=f"user_{current_user.id}",
            completed_at=datetime.now(UTC)
        )

        db.session.add(assessment)

        outcome = OutcomeMeasure(
            patient_id=patient_id,
            outcome_type='symptom_reduction',
            outcome_name='PSS-10',
            baseline_value=result.total_score,
            current_value=result.total_score,
            measurement_date=datetime.now(UTC),
            baseline_date=datetime.now(UTC)
        )

        db.session.add(outcome)
        db.session.commit()

        logger.info(f"PSS-10 assessment submitted: patient_id={patient_id}, score={result.total_score}")

        return jsonify({
            "assessment_id": assessment.id,
            "outcome_id": outcome.id,
            "score": result.total_score,
            "severity": result.severity_level.value,
            "interpretation": result.clinical_interpretation,
            "timestamp": assessment.completed_at.isoformat(),
            "follow_up_recommended": result.total_score >= 20
        }), 201

    except Exception as e:
        logger.error(f"Error submitting PSS-10: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Failed to submit assessment", "details": str(e)}), 500


@clinical_api_bp.route('/outcomes/patient/<int:patient_id>', methods=['GET'])
@login_required
def get_patient_outcomes(patient_id):
    """
    Get all outcomes for a specific patient
    """
    try:
        if patient_id != current_user.id and not hasattr(current_user, 'is_admin'):
            return jsonify({"error": "Unauthorized access"}), 403

        measure_type = request.args.get('measure_type')
        days = int(request.args.get('days', 90))
        include_trend = request.args.get('include_trend', 'true').lower() == 'true'

        start_date = datetime.now(UTC) - timedelta(days=days)

        query = OutcomeMeasure.query.filter(
            OutcomeMeasure.patient_id == patient_id,
            OutcomeMeasure.measurement_date >= start_date
        )

        if measure_type:
            query = query.filter(OutcomeMeasure.outcome_name == measure_type)

        outcomes = query.order_by(OutcomeMeasure.measurement_date.desc()).all()

        outcomes_data = [{
            "id": o.id,
            "outcome_type": o.outcome_type,
            "outcome_name": o.outcome_name,
            "current_value": o.current_value,
            "measurement_date": o.measurement_date.isoformat(),
        } for o in outcomes]

        response = {
            "patient_id": patient_id,
            "date_range": {
                "start": start_date.isoformat(),
                "end": datetime.now(UTC).isoformat(),
                "days": days
            },
            "outcomes": outcomes_data,
            "count": len(outcomes_data)
        }

        if include_trend and len(outcomes) >= 2:
            try:
                pass
            except Exception as e:
                logger.warning(f"Failed to calculate trend: {str(e)}")
                response['trend'] = None

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error fetching patient outcomes: {str(e)}")
        return jsonify({"error": "Failed to fetch outcomes", "details": str(e)}), 500


@clinical_api_bp.route('/outcomes/treatment-effectiveness', methods=['GET'])
@login_required
def get_treatment_effectiveness():
    """
    Get treatment effectiveness data across all patients
    """
    try:
        if not hasattr(current_user, 'is_admin') and not hasattr(current_user, 'is_professional'):
            return jsonify({"error": "Unauthorized: Admin or professional access required"}), 403

        days = int(request.args.get('days', 30))
        measure_type = request.args.get('measure_type')
        min_assessments = int(request.args.get('min_assessments', 2))

        start_date = datetime.now(UTC) - timedelta(days=days)

        query = ClinicalAssessment.query.filter(
            ClinicalAssessment.completed_at >= start_date
        )

        if measure_type:
            query = query.filter(ClinicalAssessment.assessment_type.contains(measure_type))

        assessments = query.all()

        patient_assessments = {}
        for assessment in assessments:
            if assessment.patient_id not in patient_assessments:
                patient_assessments[assessment.patient_id] = []
            patient_assessments[assessment.patient_id].append(assessment)

        total_patients = 0
        improved = 0
        stable = 0
        declined = 0

        for patient_id, patient_data in patient_assessments.items():
            if len(patient_data) < min_assessments:
                continue

            total_patients += 1

            sorted_data = sorted(patient_data, key=lambda x: x.completed_at)
            first_score = sorted_data[0].total_score
            last_score = sorted_data[-1].total_score

            if last_score < first_score - 3:
                improved += 1
            elif last_score > first_score + 3:
                declined += 1
            else:
                stable += 1

        if total_patients > 0:
            improvement_rate = (improved / total_patients) * 100
            stability_rate = (stable / total_patients) * 100
            decline_rate = (declined / total_patients) * 100
        else:
            improvement_rate = stability_rate = decline_rate = 0

        response = {
            "analysis_period": {
                "start": start_date.isoformat(),
                "end": datetime.now(UTC).isoformat(),
                "days": days
            },
            "summary": {
                "total_patients_analyzed": total_patients,
                "total_assessments": len(assessments),
                "min_assessments_filter": min_assessments
            },
            "effectiveness": {
                "improved": {
                    "count": improved,
                    "percentage": round(improvement_rate, 2)
                },
                "stable": {
                    "count": stable,
                    "percentage": round(stability_rate, 2)
                },
                "declined": {
                    "count": declined,
                    "percentage": round(decline_rate, 2)
                }
            },
            "interpretation": "Treatment effectiveness based on score changes over time"
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error calculating treatment effectiveness: {str(e)}")
        return jsonify({"error": "Failed to calculate effectiveness", "details": str(e)}), 500


@clinical_api_bp.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint for Clinical Outcomes API"""
    return jsonify({
        "status": "operational",
        "api": "Clinical Outcomes API",
        "version": "1.0",
        "endpoints": {
            "assessments": ["/phq9", "/gad7", "/pss10"],
            "outcomes": ["/patient/<id>", "/treatment-effectiveness"]
        },
        "timestamp": datetime.now(UTC).isoformat()
    }), 200
