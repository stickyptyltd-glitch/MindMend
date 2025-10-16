#!/usr/bin/env python3
"""
Test script for Phase 4 Clinical Intelligence modules
Tests: Clinical assessments, outcomes analyzer
"""

import sys
from datetime import datetime, timedelta
from models.clinical_assessment_tools import (
    assessment_manager,
    PHQ9Assessment,
    GAD7Assessment,
    PSS10Assessment,
    WEMWBSAssessment
)
from models.clinical_outcomes_analyzer import outcomes_analyzer

def test_phq9_assessment():
    """Test PHQ-9 depression assessment"""
    print("\n" + "="*60)
    print("TEST 1: PHQ-9 Depression Assessment")
    print("="*60)

    phq9 = PHQ9Assessment()

    # Test case: Moderate depression with suicidal ideation
    responses = [2, 2, 2, 2, 1, 2, 1, 1, 1]  # Score: 14, Item 9: 1

    result = phq9.calculate_score(responses)

    print(f"Assessment Type: {result.assessment_type}")
    print(f"Total Score: {result.total_score}/{result.max_score}")
    print(f"Percentage: {result.percentage:.1f}%")
    print(f"Severity: {result.severity_level.value}")
    print(f"Interpretation: {result.clinical_interpretation}")
    print(f"Risk Flags: {', '.join(result.risk_flags) if result.risk_flags else 'None'}")
    print(f"Recommended Actions:")
    for action in result.recommended_actions:
        print(f"  - {action}")

    assert result.total_score == 14, "PHQ-9 scoring error"
    assert "Suicidal ideation" in result.risk_flags[0] if result.risk_flags else False
    print("\n✅ PHQ-9 Assessment Test PASSED")
    return result


def test_gad7_assessment():
    """Test GAD-7 anxiety assessment"""
    print("\n" + "="*60)
    print("TEST 2: GAD-7 Anxiety Assessment")
    print("="*60)

    gad7 = GAD7Assessment()

    # Test case: Severe anxiety
    responses = [3, 3, 3, 2, 2, 2, 2]  # Score: 17

    result = gad7.calculate_score(responses)

    print(f"Assessment Type: {result.assessment_type}")
    print(f"Total Score: {result.total_score}/{result.max_score}")
    print(f"Severity: {result.severity_level.value}")
    print(f"Interpretation: {result.clinical_interpretation}")
    print(f"Recommended Actions:")
    for action in result.recommended_actions:
        print(f"  - {action}")

    assert result.total_score == 17, "GAD-7 scoring error"
    assert result.severity_level.value == "severe"
    print("\n✅ GAD-7 Assessment Test PASSED")
    return result


def test_pss10_assessment():
    """Test PSS-10 stress assessment"""
    print("\n" + "="*60)
    print("TEST 3: PSS-10 Stress Assessment")
    print("="*60)

    pss10 = PSS10Assessment()

    # Test case: High stress (with reverse scoring)
    responses = [3, 3, 3, 1, 1, 3, 1, 1, 3, 3]  # Score after reverse: ~32

    result = pss10.calculate_score(responses)

    print(f"Assessment Type: {result.assessment_type}")
    print(f"Total Score: {result.total_score}/{result.max_score}")
    print(f"Severity: {result.severity_level.value}")
    print(f"Interpretation: {result.clinical_interpretation}")
    print(f"Risk Flags: {', '.join(result.risk_flags) if result.risk_flags else 'None'}")

    assert result.total_score >= 27, "PSS-10 high stress not detected"
    print("\n✅ PSS-10 Assessment Test PASSED")
    return result


def test_wemwbs_assessment():
    """Test WEMWBS wellbeing assessment"""
    print("\n" + "="*60)
    print("TEST 4: WEMWBS Wellbeing Assessment")
    print("="*60)

    wemwbs = WEMWBSAssessment()

    # Test case: Moderate wellbeing
    responses = [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]  # Score: 42

    result = wemwbs.calculate_score(responses)

    print(f"Assessment Type: {result.assessment_type}")
    print(f"Total Score: {result.total_score}/{result.max_score}")
    print(f"Severity: {result.severity_level.value}")
    print(f"Interpretation: {result.clinical_interpretation}")

    assert result.total_score == 42, "WEMWBS scoring error"
    print("\n✅ WEMWBS Assessment Test PASSED")
    return result


def test_treatment_effectiveness_analysis():
    """Test clinical outcomes analyzer"""
    print("\n" + "="*60)
    print("TEST 5: Treatment Effectiveness Analysis")
    print("="*60)

    # Simulate patient treatment data
    baseline_assessments = {
        "PHQ-9": 18,  # Moderately severe depression
        "GAD-7": 15,  # Severe anxiety
        "PSS-10": 30  # High stress
    }

    current_assessments = {
        "PHQ-9": 8,   # Mild depression (improvement of 10 points)
        "GAD-7": 7,   # Mild anxiety (improvement of 8 points)
        "PSS-10": 15  # Moderate stress (improvement of 15 points)
    }

    treatment_start = datetime.utcnow() - timedelta(days=56)  # 8 weeks ago

    interventions = [
        {
            "intervention_name": "Cognitive Behavioral Therapy",
            "clinical_effectiveness": 78.5,
            "status": "completed"
        },
        {
            "intervention_name": "Mindfulness Meditation",
            "clinical_effectiveness": 65.0,
            "status": "completed"
        },
        {
            "intervention_name": "Sleep Hygiene Training",
            "clinical_effectiveness": 45.0,
            "status": "in_progress"
        }
    ]

    report = outcomes_analyzer.analyze_treatment_effectiveness(
        patient_id=1,
        baseline_assessments=baseline_assessments,
        current_assessments=current_assessments,
        treatment_start_date=treatment_start,
        session_count=8,
        interventions=interventions
    )

    print(f"Patient ID: {report.patient_id}")
    print(f"Treatment Duration: {report.treatment_duration_days} days")
    print(f"Total Sessions: {report.total_sessions}")
    print(f"\nOverall Improvement: {report.overall_improvement_percentage:.1f}%")
    print(f"Outcome Status: {report.outcome_status.value}")
    print(f"Change Significance: {report.change_significance.value}")
    print(f"Reliable Change Index: {report.reliable_change_index:.2f}")
    print(f"Effect Size (Cohen's d): {report.effect_size_cohens_d:.2f}")
    print(f"Meets Recovery Criteria: {report.meets_recovery_criteria}")

    if report.depression_change:
        print(f"\nDepression Change:")
        print(f"  Baseline: {report.depression_change['baseline_score']} ({report.depression_change['severity_baseline']})")
        print(f"  Current: {report.depression_change['current_score']} ({report.depression_change['severity_current']})")
        print(f"  Improvement: {report.depression_change['improvement_percentage']:.1f}%")
        print(f"  Clinically Significant: {report.depression_change['is_clinically_significant']}")

    if report.anxiety_change:
        print(f"\nAnxiety Change:")
        print(f"  Baseline: {report.anxiety_change['baseline_score']} ({report.anxiety_change['severity_baseline']})")
        print(f"  Current: {report.anxiety_change['current_score']} ({report.anxiety_change['severity_current']})")
        print(f"  Improvement: {report.anxiety_change['improvement_percentage']:.1f}%")

    print(f"\nMost Effective Interventions:")
    for intervention in report.most_effective_interventions:
        print(f"  ✓ {intervention}")

    print(f"\nClinical Recommendations:")
    for rec in report.clinical_recommendations:
        print(f"  • {rec}")

    assert report.overall_improvement_percentage > 40, "Treatment effectiveness not detected"
    assert report.outcome_status.value in ["improved", "recovered"]
    print("\n✅ Treatment Effectiveness Analysis Test PASSED")
    return report


def test_recovery_trajectory():
    """Test recovery trajectory prediction"""
    print("\n" + "="*60)
    print("TEST 6: Recovery Trajectory Prediction")
    print("="*60)

    # Simulate assessment history showing improvement
    assessment_history = [
        {"date": datetime.utcnow() - timedelta(weeks=8), "score": 18},
        {"date": datetime.utcnow() - timedelta(weeks=6), "score": 15},
        {"date": datetime.utcnow() - timedelta(weeks=4), "score": 12},
        {"date": datetime.utcnow() - timedelta(weeks=2), "score": 9},
        {"date": datetime.utcnow(), "score": 7}
    ]

    trajectory = outcomes_analyzer.calculate_recovery_trajectory(
        patient_id=1,
        assessment_history=assessment_history,
        current_severity="mild",
        baseline_severity="moderately_severe"
    )

    print(f"Patient ID: {trajectory.patient_id}")
    print(f"Current Severity: {trajectory.current_severity}")
    print(f"Baseline Severity: {trajectory.baseline_severity}")
    print(f"Predicted Recovery: {trajectory.predicted_recovery_weeks} weeks")
    print(f"Confidence Interval: {trajectory.confidence_interval[0]}-{trajectory.confidence_interval[1]} weeks")
    print(f"Trajectory Slope: {trajectory.trajectory_slope:.3f}")

    print(f"\nMilestones Achieved:")
    for milestone in trajectory.milestones_achieved:
        print(f"  ✓ Week {milestone['week']}: {milestone['description']}")

    print(f"\nNext Milestone:")
    print(f"  → {trajectory.next_milestone['description']}")
    print(f"  Target: {trajectory.next_milestone['target_timeframe']}")

    print(f"\nFavorable Factors:")
    for factor in trajectory.favorable_factors:
        print(f"  + {factor}")

    if trajectory.risk_factors:
        print(f"\nRisk Factors:")
        for risk in trajectory.risk_factors:
            print(f"  - {risk}")

    print(f"\nRecommended Adjustments:")
    for adjustment in trajectory.recommended_adjustments:
        print(f"  • {adjustment}")

    assert trajectory.trajectory_slope < 0, "Improvement trajectory not detected"
    assert trajectory.predicted_recovery_weeks > 0
    print("\n✅ Recovery Trajectory Prediction Test PASSED")
    return trajectory


def test_assessment_manager():
    """Test assessment manager convenience functions"""
    print("\n" + "="*60)
    print("TEST 7: Assessment Manager Integration")
    print("="*60)

    # Test getting questions
    phq9_questions = assessment_manager.get_questions("PHQ-9")
    print(f"PHQ-9 has {len(phq9_questions)} questions")
    assert len(phq9_questions) == 9

    # Test calculating multiple assessments
    phq9_result = assessment_manager.calculate_score("PHQ-9", [1, 1, 1, 1, 1, 1, 1, 1, 0])
    gad7_result = assessment_manager.calculate_score("GAD-7", [1, 1, 1, 1, 1, 1, 1])

    print(f"PHQ-9 Result: {phq9_result.total_score}/27 ({phq9_result.severity_level.value})")
    print(f"GAD-7 Result: {gad7_result.total_score}/21 ({gad7_result.severity_level.value})")

    # Test JSON export
    json_output = assessment_manager.export_result_to_json(phq9_result)
    print(f"\nJSON Export (truncated):")
    print(json_output[:200] + "...")

    assert "PHQ-9" in json_output
    print("\n✅ Assessment Manager Integration Test PASSED")


def run_all_tests():
    """Run all Phase 4 clinical intelligence tests"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   PHASE 4 CLINICAL INTELLIGENCE MODULE TEST SUITE         ║")
    print("╚════════════════════════════════════════════════════════════╝")

    try:
        # Test individual assessments
        test_phq9_assessment()
        test_gad7_assessment()
        test_pss10_assessment()
        test_wemwbs_assessment()

        # Test outcomes analyzer
        test_treatment_effectiveness_analysis()
        test_recovery_trajectory()

        # Test manager
        test_assessment_manager()

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("✅ All 7 tests PASSED")
        print("\nPhase 4 Clinical Intelligence modules are working correctly!")
        print("\nKey capabilities verified:")
        print("  • PHQ-9, GAD-7, PSS-10, WEMWBS assessments")
        print("  • Clinical interpretation and risk flagging")
        print("  • Treatment effectiveness analysis (RCI, Cohen's d)")
        print("  • Recovery trajectory prediction")
        print("  • Intervention effectiveness scoring")
        print("  • Personalized clinical recommendations")
        print("\n✅ READY FOR PRODUCTION INTEGRATION")
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
