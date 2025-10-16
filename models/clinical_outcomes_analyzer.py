"""
Clinical Outcomes Analyzer - Treatment Effectiveness Engine
===========================================================
Analyzes treatment effectiveness, measures symptom reduction,
calculates recovery trajectories, and identifies response predictors.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class OutcomeStatus(Enum):
    """Treatment outcome status"""
    IMPROVED = "improved"
    STABLE = "stable"
    DECLINED = "declined"
    RECOVERED = "recovered"
    RELAPSED = "relapsed"


class ChangeSignificance(Enum):
    """Clinical significance of change"""
    CLINICALLY_SIGNIFICANT = "clinically_significant"
    STATISTICALLY_SIGNIFICANT = "statistically_significant"
    RELIABLE_CHANGE = "reliable_change"
    MINIMAL_CHANGE = "minimal_change"
    NO_CHANGE = "no_change"


@dataclass
class TreatmentEffectivenessReport:
    """Comprehensive treatment effectiveness report"""
    patient_id: int
    report_date: datetime
    treatment_duration_days: int

    # Symptom changes
    depression_change: Optional[Dict[str, Any]] = None
    anxiety_change: Optional[Dict[str, Any]] = None
    stress_change: Optional[Dict[str, Any]] = None
    wellbeing_change: Optional[Dict[str, Any]] = None

    # Overall outcomes
    overall_improvement_percentage: float = 0.0
    outcome_status: OutcomeStatus = OutcomeStatus.STABLE
    change_significance: ChangeSignificance = ChangeSignificance.NO_CHANGE

    # Clinical measures
    reliable_change_index: float = 0.0
    effect_size_cohens_d: float = 0.0
    meets_recovery_criteria: bool = False

    # Session metrics
    total_sessions: int = 0
    session_attendance_rate: float = 100.0
    homework_completion_rate: float = 0.0

    # Intervention effectiveness
    most_effective_interventions: List[str] = field(default_factory=list)
    least_effective_interventions: List[str] = field(default_factory=list)

    # Risk factors
    risk_factors_addressed: List[str] = field(default_factory=list)
    remaining_risk_factors: List[str] = field(default_factory=list)

    # Recommendations
    clinical_recommendations: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)


@dataclass
class RecoveryTrajectory:
    """Patient recovery trajectory prediction"""
    patient_id: int
    current_severity: str
    baseline_severity: str

    # Trajectory prediction
    predicted_recovery_weeks: int
    confidence_interval: Tuple[int, int]
    trajectory_slope: float  # Rate of improvement

    # Progress markers
    milestones_achieved: List[Dict[str, Any]]
    next_milestone: Dict[str, Any]

    # Prediction factors
    favorable_factors: List[str]
    risk_factors: List[str]

    # Treatment adjustments
    recommended_adjustments: List[str]


@dataclass
class InterventionEffectivenessScore:
    """Score for specific intervention effectiveness"""
    intervention_name: str
    intervention_type: str

    # Effectiveness metrics
    effectiveness_score: float  # 0-100
    completion_rate: float
    adherence_rate: float

    # Clinical outcomes
    pre_score: Optional[float]
    post_score: Optional[float]
    symptom_reduction_percentage: float

    # Sample metrics
    patient_count: int
    average_sessions: float

    # Statistical metrics
    effect_size: float
    statistical_significance: bool


class ClinicalOutcomesAnalyzer:
    """
    Comprehensive clinical outcomes analysis system
    Measures treatment effectiveness, predicts recovery, and optimizes interventions
    """

    def __init__(self, db_session=None):
        self.db = db_session
        self.recovery_criteria = self._init_recovery_criteria()
        self.rci_parameters = self._init_rci_parameters()

    def _init_recovery_criteria(self) -> Dict[str, Dict[str, Any]]:
        """Initialize recovery criteria for different assessments"""
        return {
            "PHQ-9": {
                "recovery_threshold": 4,  # Score ≤4 indicates minimal depression
                "reliable_change": 6,  # Change of ≥6 points is reliable
                "test_retest_reliability": 0.84,
                "standard_deviation": 6.0
            },
            "GAD-7": {
                "recovery_threshold": 4,  # Score ≤4 indicates minimal anxiety
                "reliable_change": 5,  # Change of ≥5 points is reliable
                "test_retest_reliability": 0.83,
                "standard_deviation": 4.5
            },
            "PSS-10": {
                "recovery_threshold": 13,  # Score ≤13 indicates low stress
                "reliable_change": 8,  # Change of ≥8 points is reliable
                "test_retest_reliability": 0.78,
                "standard_deviation": 6.2
            },
            "WEMWBS": {
                "recovery_threshold": 60,  # Score ≥60 indicates high wellbeing
                "reliable_change": 9,  # Change of ≥9 points is reliable
                "test_retest_reliability": 0.83,
                "standard_deviation": 8.0
            }
        }

    def _init_rci_parameters(self) -> Dict[str, float]:
        """Initialize Reliable Change Index parameters"""
        return {
            "PHQ-9": 1.96 * 6.0 * np.sqrt(2 * (1 - 0.84)),  # ≈6.19
            "GAD-7": 1.96 * 4.5 * np.sqrt(2 * (1 - 0.83)),  # ≈4.81
            "PSS-10": 1.96 * 6.2 * np.sqrt(2 * (1 - 0.78)),  # ≈7.87
            "WEMWBS": 1.96 * 8.0 * np.sqrt(2 * (1 - 0.83))   # ≈8.55
        }

    def analyze_treatment_effectiveness(
        self,
        patient_id: int,
        baseline_assessments: Dict[str, int],
        current_assessments: Dict[str, int],
        treatment_start_date: datetime,
        session_count: int,
        interventions: List[Dict[str, Any]]
    ) -> TreatmentEffectivenessReport:
        """
        Comprehensive analysis of treatment effectiveness for a patient

        Args:
            patient_id: Patient identifier
            baseline_assessments: Dict of assessment_type: baseline_score
            current_assessments: Dict of assessment_type: current_score
            treatment_start_date: When treatment began
            session_count: Number of sessions completed
            interventions: List of interventions with tracking data

        Returns:
            TreatmentEffectivenessReport with comprehensive analysis
        """

        treatment_duration = (datetime.utcnow() - treatment_start_date).days

        # Analyze each assessment type
        depression_change = self._analyze_assessment_change(
            "PHQ-9",
            baseline_assessments.get("PHQ-9"),
            current_assessments.get("PHQ-9")
        ) if "PHQ-9" in baseline_assessments else None

        anxiety_change = self._analyze_assessment_change(
            "GAD-7",
            baseline_assessments.get("GAD-7"),
            current_assessments.get("GAD-7")
        ) if "GAD-7" in baseline_assessments else None

        stress_change = self._analyze_assessment_change(
            "PSS-10",
            baseline_assessments.get("PSS-10"),
            current_assessments.get("PSS-10")
        ) if "PSS-10" in baseline_assessments else None

        wellbeing_change = self._analyze_assessment_change(
            "WEMWBS",
            baseline_assessments.get("WEMWBS"),
            current_assessments.get("WEMWBS")
        ) if "WEMWBS" in baseline_assessments else None

        # Calculate overall improvement
        improvement_scores = []
        if depression_change:
            improvement_scores.append(depression_change['improvement_percentage'])
        if anxiety_change:
            improvement_scores.append(anxiety_change['improvement_percentage'])
        if stress_change:
            improvement_scores.append(stress_change['improvement_percentage'])
        if wellbeing_change:
            improvement_scores.append(wellbeing_change['improvement_percentage'])

        overall_improvement = np.mean(improvement_scores) if improvement_scores else 0.0

        # Determine outcome status
        outcome_status = self._determine_outcome_status(
            depression_change,
            anxiety_change,
            stress_change,
            wellbeing_change
        )

        # Calculate Reliable Change Index
        rci = self._calculate_overall_rci(
            baseline_assessments,
            current_assessments
        )

        # Determine change significance
        change_significance = self._determine_change_significance(
            overall_improvement,
            rci,
            outcome_status
        )

        # Calculate effect size (Cohen's d)
        effect_size = self._calculate_cohens_d(
            baseline_assessments,
            current_assessments
        )

        # Check recovery criteria
        meets_recovery = self._check_recovery_criteria(
            current_assessments,
            change_significance
        )

        # Analyze intervention effectiveness
        effective_interventions, ineffective_interventions = \
            self._analyze_intervention_effectiveness(interventions)

        # Generate clinical recommendations
        recommendations = self._generate_clinical_recommendations(
            outcome_status,
            change_significance,
            overall_improvement,
            treatment_duration,
            session_count
        )

        return TreatmentEffectivenessReport(
            patient_id=patient_id,
            report_date=datetime.utcnow(),
            treatment_duration_days=treatment_duration,
            depression_change=depression_change,
            anxiety_change=anxiety_change,
            stress_change=stress_change,
            wellbeing_change=wellbeing_change,
            overall_improvement_percentage=overall_improvement,
            outcome_status=outcome_status,
            change_significance=change_significance,
            reliable_change_index=rci,
            effect_size_cohens_d=effect_size,
            meets_recovery_criteria=meets_recovery,
            total_sessions=session_count,
            most_effective_interventions=effective_interventions,
            least_effective_interventions=ineffective_interventions,
            clinical_recommendations=recommendations
        )

    def _analyze_assessment_change(
        self,
        assessment_type: str,
        baseline_score: Optional[int],
        current_score: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """Analyze change in a specific assessment"""
        if baseline_score is None or current_score is None:
            return None

        criteria = self.recovery_criteria[assessment_type]

        # Calculate raw change
        raw_change = baseline_score - current_score

        # For wellbeing scales (higher is better), invert the calculation
        if assessment_type == "WEMWBS":
            raw_change = current_score - baseline_score

        # Calculate percentage improvement
        if baseline_score != 0:
            improvement_pct = (abs(raw_change) / abs(baseline_score)) * 100
        else:
            improvement_pct = 0.0

        # Calculate Reliable Change Index for this assessment
        rci_value = raw_change / self.rci_parameters[assessment_type]

        # Determine if change is reliable
        is_reliable_change = abs(rci_value) >= 1.96

        # Determine if patient has recovered
        if assessment_type == "WEMWBS":
            has_recovered = current_score >= criteria['recovery_threshold']
        else:
            has_recovered = current_score <= criteria['recovery_threshold']

        # Determine clinical significance
        is_clinically_significant = is_reliable_change and (
            (raw_change > 0 and has_recovered) if assessment_type != "WEMWBS"
            else (raw_change > 0 and has_recovered)
        )

        return {
            "assessment_type": assessment_type,
            "baseline_score": baseline_score,
            "current_score": current_score,
            "raw_change": raw_change,
            "improvement_percentage": improvement_pct if raw_change > 0 else -improvement_pct,
            "reliable_change_index": rci_value,
            "is_reliable_change": is_reliable_change,
            "has_recovered": has_recovered,
            "is_clinically_significant": is_clinically_significant,
            "severity_baseline": self._get_severity_label(assessment_type, baseline_score),
            "severity_current": self._get_severity_label(assessment_type, current_score)
        }

    def _get_severity_label(self, assessment_type: str, score: int) -> str:
        """Get severity label for a score"""
        if assessment_type == "PHQ-9":
            if score <= 4: return "minimal"
            elif score <= 9: return "mild"
            elif score <= 14: return "moderate"
            elif score <= 19: return "moderately_severe"
            else: return "severe"

        elif assessment_type == "GAD-7":
            if score <= 4: return "minimal"
            elif score <= 9: return "mild"
            elif score <= 14: return "moderate"
            else: return "severe"

        elif assessment_type == "PSS-10":
            if score <= 13: return "low"
            elif score <= 26: return "moderate"
            else: return "high"

        elif assessment_type == "WEMWBS":
            if score <= 40: return "low"
            elif score <= 59: return "moderate"
            else: return "high"

        return "unknown"

    def _determine_outcome_status(
        self,
        depression_change: Optional[Dict],
        anxiety_change: Optional[Dict],
        stress_change: Optional[Dict],
        wellbeing_change: Optional[Dict]
    ) -> OutcomeStatus:
        """Determine overall outcome status"""

        # Count recoveries and reliable improvements
        recovered_count = 0
        improved_count = 0
        declined_count = 0
        total_measures = 0

        for change in [depression_change, anxiety_change, stress_change, wellbeing_change]:
            if change:
                total_measures += 1
                if change['has_recovered']:
                    recovered_count += 1
                # Check for improvement (positive raw_change means better)
                elif change['improvement_percentage'] > 0:
                    if change['is_reliable_change']:
                        improved_count += 1
                    elif change['improvement_percentage'] > 30:  # Substantial improvement even if not reliable
                        improved_count += 0.5
                # Check for decline
                elif change['improvement_percentage'] < 0:
                    if change['is_reliable_change']:
                        declined_count += 1

        if total_measures == 0:
            return OutcomeStatus.STABLE

        # Determine status based on counts
        if recovered_count == total_measures:
            return OutcomeStatus.RECOVERED
        elif declined_count >= total_measures / 2:
            return OutcomeStatus.DECLINED
        elif improved_count + recovered_count >= total_measures / 2:
            return OutcomeStatus.IMPROVED
        else:
            return OutcomeStatus.STABLE

    def _calculate_overall_rci(
        self,
        baseline: Dict[str, int],
        current: Dict[str, int]
    ) -> float:
        """Calculate overall Reliable Change Index across all measures"""
        rci_values = []

        for assessment_type in baseline.keys():
            if assessment_type in current and assessment_type in self.rci_parameters:
                baseline_score = baseline[assessment_type]
                current_score = current[assessment_type]

                if assessment_type == "WEMWBS":
                    change = current_score - baseline_score
                else:
                    change = baseline_score - current_score

                rci = change / self.rci_parameters[assessment_type]
                rci_values.append(rci)

        return np.mean(rci_values) if rci_values else 0.0

    def _determine_change_significance(
        self,
        improvement_pct: float,
        rci: float,
        outcome_status: OutcomeStatus
    ) -> ChangeSignificance:
        """Determine clinical significance of change"""

        if outcome_status == OutcomeStatus.RECOVERED:
            return ChangeSignificance.CLINICALLY_SIGNIFICANT

        if abs(rci) >= 1.96:  # p < 0.05
            if improvement_pct >= 30:
                return ChangeSignificance.CLINICALLY_SIGNIFICANT
            else:
                return ChangeSignificance.RELIABLE_CHANGE

        if improvement_pct >= 20:
            return ChangeSignificance.STATISTICALLY_SIGNIFICANT

        if improvement_pct >= 10:
            return ChangeSignificance.MINIMAL_CHANGE

        return ChangeSignificance.NO_CHANGE

    def _calculate_cohens_d(
        self,
        baseline: Dict[str, int],
        current: Dict[str, int]
    ) -> float:
        """Calculate Cohen's d effect size"""
        effect_sizes = []

        for assessment_type in baseline.keys():
            if assessment_type in current and assessment_type in self.recovery_criteria:
                baseline_score = baseline[assessment_type]
                current_score = current[assessment_type]
                sd = self.recovery_criteria[assessment_type]['standard_deviation']

                if assessment_type == "WEMWBS":
                    d = (current_score - baseline_score) / sd
                else:
                    d = (baseline_score - current_score) / sd

                effect_sizes.append(d)

        return np.mean(effect_sizes) if effect_sizes else 0.0

    def _check_recovery_criteria(
        self,
        current_assessments: Dict[str, int],
        change_significance: ChangeSignificance
    ) -> bool:
        """Check if patient meets recovery criteria"""

        if change_significance != ChangeSignificance.CLINICALLY_SIGNIFICANT:
            return False

        recovery_count = 0
        total_assessments = 0

        for assessment_type, current_score in current_assessments.items():
            if assessment_type in self.recovery_criteria:
                total_assessments += 1
                threshold = self.recovery_criteria[assessment_type]['recovery_threshold']

                if assessment_type == "WEMWBS":
                    if current_score >= threshold:
                        recovery_count += 1
                else:
                    if current_score <= threshold:
                        recovery_count += 1

        # Patient must meet recovery criteria on all available assessments
        return recovery_count == total_assessments if total_assessments > 0 else False

    def _analyze_intervention_effectiveness(
        self,
        interventions: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """Analyze which interventions were most and least effective"""

        intervention_scores = defaultdict(list)

        for intervention in interventions:
            name = intervention.get('intervention_name', 'Unknown')
            effectiveness = intervention.get('clinical_effectiveness', 0)

            if effectiveness is not None:
                intervention_scores[name].append(effectiveness)

        # Calculate average effectiveness for each intervention
        avg_effectiveness = {
            name: np.mean(scores)
            for name, scores in intervention_scores.items()
        }

        # Sort by effectiveness
        sorted_interventions = sorted(
            avg_effectiveness.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Top 3 most effective
        most_effective = [name for name, score in sorted_interventions[:3] if score >= 50]

        # Bottom 3 least effective
        least_effective = [name for name, score in sorted_interventions[-3:] if score < 30]

        return most_effective, least_effective

    def _generate_clinical_recommendations(
        self,
        outcome_status: OutcomeStatus,
        change_significance: ChangeSignificance,
        improvement_pct: float,
        treatment_duration: int,
        session_count: int
    ) -> List[str]:
        """Generate personalized clinical recommendations"""

        recommendations = []

        # Based on outcome status
        if outcome_status == OutcomeStatus.RECOVERED:
            recommendations.append("Patient has achieved recovery criteria. Consider transitioning to maintenance phase.")
            recommendations.append("Schedule follow-up assessments at 1, 3, and 6 months to monitor for relapse.")
            recommendations.append("Develop relapse prevention plan with early warning signs.")

        elif outcome_status == OutcomeStatus.IMPROVED:
            recommendations.append("Patient showing significant improvement. Continue current treatment approach.")
            if improvement_pct < 50:
                recommendations.append("Consider treatment intensification to accelerate progress.")
            recommendations.append("Reinforce effective coping strategies and interventions.")

        elif outcome_status == OutcomeStatus.STABLE:
            recommendations.append("Limited treatment progress observed. Reassess treatment approach.")
            recommendations.append("Consider alternative therapeutic modalities or augmentation strategies.")
            recommendations.append("Evaluate barriers to treatment engagement and adherence.")

        elif outcome_status == OutcomeStatus.DECLINED:
            recommendations.append("Patient showing clinical deterioration. Immediate intervention required.")
            recommendations.append("Comprehensive reassessment recommended, including medication review.")
            recommendations.append("Consider referral to psychiatrist or higher level of care.")

        # Based on treatment duration
        if treatment_duration > 90 and change_significance == ChangeSignificance.NO_CHANGE:
            recommendations.append("Minimal progress after 12+ weeks. Consider treatment alternatives.")
            recommendations.append("Consult with multidisciplinary team for complex case review.")

        # Based on session attendance
        if session_count < (treatment_duration / 7):  # Less than weekly
            recommendations.append("Low session frequency may impact outcomes. Consider increasing session frequency.")

        return recommendations

    def calculate_recovery_trajectory(
        self,
        patient_id: int,
        assessment_history: List[Dict[str, Any]],
        current_severity: str,
        baseline_severity: str
    ) -> RecoveryTrajectory:
        """
        Predict patient recovery trajectory based on historical data

        Args:
            patient_id: Patient identifier
            assessment_history: List of assessments with dates and scores
            current_severity: Current severity level
            baseline_severity: Baseline severity level

        Returns:
            RecoveryTrajectory with predictions
        """

        # Calculate rate of change (slope)
        if len(assessment_history) < 2:
            trajectory_slope = 0.0
        else:
            # Linear regression on scores over time
            dates = [(a['date'] - assessment_history[0]['date']).days
                    for a in assessment_history]
            scores = [a['score'] for a in assessment_history]

            if len(dates) > 1 and len(scores) > 1:
                slope, _ = np.polyfit(dates, scores, 1)
                trajectory_slope = slope
            else:
                trajectory_slope = 0.0

        # Predict recovery time based on trajectory
        predicted_weeks = self._predict_recovery_time(
            current_severity,
            trajectory_slope,
            len(assessment_history)
        )

        # Calculate confidence interval
        confidence_lower = max(predicted_weeks - 4, 2)
        confidence_upper = predicted_weeks + 4

        # Identify milestones achieved
        milestones = self._identify_milestones(assessment_history)

        # Determine next milestone
        next_milestone = self._get_next_milestone(
            current_severity,
            assessment_history
        )

        # Identify favorable and risk factors
        favorable, risks = self._identify_trajectory_factors(
            trajectory_slope,
            assessment_history
        )

        # Generate treatment adjustments
        adjustments = self._recommend_trajectory_adjustments(
            trajectory_slope,
            predicted_weeks,
            current_severity
        )

        return RecoveryTrajectory(
            patient_id=patient_id,
            current_severity=current_severity,
            baseline_severity=baseline_severity,
            predicted_recovery_weeks=predicted_weeks,
            confidence_interval=(confidence_lower, confidence_upper),
            trajectory_slope=trajectory_slope,
            milestones_achieved=milestones,
            next_milestone=next_milestone,
            favorable_factors=favorable,
            risk_factors=risks,
            recommended_adjustments=adjustments
        )

    def _predict_recovery_time(
        self,
        current_severity: str,
        slope: float,
        data_points: int
    ) -> int:
        """Predict weeks to recovery based on current trajectory"""

        # Base estimates by severity (weeks)
        base_estimates = {
            "severe": 16,
            "moderately_severe": 12,
            "moderate": 10,
            "mild": 6,
            "minimal": 2
        }

        base_weeks = base_estimates.get(current_severity, 12)

        # Adjust based on rate of improvement (slope)
        if slope < -0.5:  # Rapid improvement
            adjustment = 0.7
        elif slope < -0.2:  # Moderate improvement
            adjustment = 0.9
        elif slope < 0:  # Slow improvement
            adjustment = 1.1
        else:  # No improvement or declining
            adjustment = 1.5

        predicted = int(base_weeks * adjustment)

        # Cap predictions
        return min(max(predicted, 2), 26)  # Between 2-26 weeks

    def _identify_milestones(
        self,
        assessment_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify treatment milestones achieved"""
        milestones = []

        if len(assessment_history) < 2:
            return milestones

        baseline_score = assessment_history[0]['score']

        for i, assessment in enumerate(assessment_history[1:], 1):
            improvement = ((baseline_score - assessment['score']) / baseline_score) * 100

            if improvement >= 25 and not any(m['type'] == '25_percent' for m in milestones):
                milestones.append({
                    "type": "25_percent",
                    "description": "25% symptom reduction achieved",
                    "date": assessment['date'],
                    "week": i
                })

            if improvement >= 50 and not any(m['type'] == '50_percent' for m in milestones):
                milestones.append({
                    "type": "50_percent",
                    "description": "50% symptom reduction achieved",
                    "date": assessment['date'],
                    "week": i
                })

        return milestones

    def _get_next_milestone(
        self,
        current_severity: str,
        assessment_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine next treatment milestone"""

        if current_severity in ["severe", "moderately_severe"]:
            return {
                "type": "severity_reduction",
                "description": "Reduce severity to moderate",
                "target_timeframe": "4-6 weeks"
            }
        elif current_severity == "moderate":
            return {
                "type": "severity_reduction",
                "description": "Reduce severity to mild",
                "target_timeframe": "4-8 weeks"
            }
        else:
            return {
                "type": "recovery",
                "description": "Achieve full recovery criteria",
                "target_timeframe": "2-4 weeks"
            }

    def _identify_trajectory_factors(
        self,
        slope: float,
        assessment_history: List[Dict[str, Any]]
    ) -> Tuple[List[str], List[str]]:
        """Identify factors affecting recovery trajectory"""

        favorable = []
        risks = []

        # Analyze trajectory
        if slope < -0.3:
            favorable.append("Rapid symptom improvement trend")
        elif slope > 0:
            risks.append("Lack of treatment response")

        # Consistency of improvement
        if len(assessment_history) >= 3:
            recent_scores = [a['score'] for a in assessment_history[-3:]]
            if all(recent_scores[i] <= recent_scores[i+1] for i in range(len(recent_scores)-1)):
                favorable.append("Consistent improvement pattern")
            else:
                risks.append("Inconsistent progress")

        return favorable, risks

    def _recommend_trajectory_adjustments(
        self,
        slope: float,
        predicted_weeks: int,
        current_severity: str
    ) -> List[str]:
        """Recommend treatment adjustments based on trajectory"""

        adjustments = []

        if slope >= 0:
            adjustments.append("Consider treatment intensification or modality change")
            adjustments.append("Evaluate medication optimization")

        if predicted_weeks > 20:
            adjustments.append("Extended treatment duration likely needed")
            adjustments.append("Consider augmentation strategies")

        if current_severity in ["severe", "moderately_severe"] and slope > -0.2:
            adjustments.append("Increase session frequency to twice weekly")

        return adjustments


# Global instance
outcomes_analyzer = ClinicalOutcomesAnalyzer()
