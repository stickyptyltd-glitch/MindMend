"""
Clinical Assessment Tools - Validated Psychological Scales
==========================================================
Implements standardized clinical assessment tools:
- PHQ-9 (Patient Health Questionnaire - Depression)
- GAD-7 (Generalized Anxiety Disorder Scale)
- PSS-10 (Perceived Stress Scale)
- WEMWBS (Warwick-Edinburgh Mental Wellbeing Scale)
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, UTC


class AssessmentType(Enum):
    """Types of clinical assessments"""
    PHQ9 = "PHQ-9"
    GAD7 = "GAD-7"
    PSS10 = "PSS-10"
    WEMWBS = "WEMWBS"
    PHQ2 = "PHQ-2"  # Brief depression screener
    PC_PTSD5 = "PC-PTSD-5"  # PTSD screening


class SeverityLevel(Enum):
    """Severity classifications"""
    MINIMAL = "minimal"
    MILD = "mild"
    MODERATE = "moderate"
    MODERATELY_SEVERE = "moderately_severe"
    SEVERE = "severe"


@dataclass
class AssessmentQuestion:
    """Individual assessment question"""
    number: int
    text: str
    options: List[Dict[str, Any]]
    scoring_type: str = "likert"  # likert, binary, reverse_scored


@dataclass
class AssessmentResult:
    """Assessment result with clinical interpretation"""
    assessment_type: str
    total_score: int
    max_score: int
    percentage: float
    severity_level: SeverityLevel
    clinical_interpretation: str
    risk_flags: List[str]
    recommended_actions: List[str]
    item_responses: List[int]
    completed_at: datetime


class PHQ9Assessment:
    """
    Patient Health Questionnaire (PHQ-9) - Depression Assessment

    Validated 9-item depression screening tool
    Score range: 0-27
    - 0-4: Minimal depression
    - 5-9: Mild depression
    - 10-14: Moderate depression
    - 15-19: Moderately severe depression
    - 20-27: Severe depression
    """

    def __init__(self):
        self.questions = [
            AssessmentQuestion(
                number=1,
                text="Little interest or pleasure in doing things",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=2,
                text="Feeling down, depressed, or hopeless",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=3,
                text="Trouble falling or staying asleep, or sleeping too much",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=4,
                text="Feeling tired or having little energy",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=5,
                text="Poor appetite or overeating",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=6,
                text="Feeling bad about yourself - or that you are a failure or have let yourself or your family down",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=7,
                text="Trouble concentrating on things, such as reading the newspaper or watching television",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=8,
                text="Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=9,
                text="Thoughts that you would be better off dead, or of hurting yourself in some way",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            )
        ]

    def calculate_score(self, responses: List[int]) -> AssessmentResult:
        """Calculate PHQ-9 score and provide clinical interpretation"""
        if len(responses) != 9:
            raise ValueError("PHQ-9 requires exactly 9 responses")

        total_score = sum(responses)

        # Determine severity level
        if total_score <= 4:
            severity = SeverityLevel.MINIMAL
            interpretation = "Minimal or no depression. Symptoms are within normal range."
        elif total_score <= 9:
            severity = SeverityLevel.MILD
            interpretation = "Mild depression. Watchful waiting and repeat assessment recommended."
        elif total_score <= 14:
            severity = SeverityLevel.MODERATE
            interpretation = "Moderate depression. Consider treatment with counseling, follow-up and/or pharmacotherapy."
        elif total_score <= 19:
            severity = SeverityLevel.MODERATELY_SEVERE
            interpretation = "Moderately severe depression. Active treatment with pharmacotherapy and/or psychotherapy is recommended."
        else:
            severity = SeverityLevel.SEVERE
            interpretation = "Severe depression. Immediate initiation of pharmacotherapy and/or psychotherapy. Consider referral to mental health specialist."

        # Check for risk flags
        risk_flags = []
        recommended_actions = []

        # Question 9 is suicidal ideation screener
        if responses[8] > 0:
            risk_flags.append("Suicidal ideation reported (PHQ-9 Item 9)")
            recommended_actions.append("Immediate safety assessment required")
            recommended_actions.append("Consider crisis intervention or emergency referral")

        # High overall severity
        if total_score >= 15:
            risk_flags.append("High depression severity")
            recommended_actions.append("Psychiatric evaluation recommended")
            recommended_actions.append("Consider medication assessment")

        # Multiple moderate symptoms
        if total_score >= 10:
            recommended_actions.append("Evidence-based psychotherapy recommended (CBT, IPT, or behavioral activation)")
            recommended_actions.append("Regular follow-up assessments (every 2-4 weeks)")

        # Functional impairment check (based on severity)
        if total_score >= 5:
            recommended_actions.append("Assess impact on work, home, and relationships")

        return AssessmentResult(
            assessment_type="PHQ-9",
            total_score=total_score,
            max_score=27,
            percentage=(total_score / 27) * 100,
            severity_level=severity,
            clinical_interpretation=interpretation,
            risk_flags=risk_flags,
            recommended_actions=recommended_actions,
            item_responses=responses,
            completed_at=datetime.now(UTC)
        )


class GAD7Assessment:
    """
    Generalized Anxiety Disorder Scale (GAD-7)

    Validated 7-item anxiety screening tool
    Score range: 0-21
    - 0-4: Minimal anxiety
    - 5-9: Mild anxiety
    - 10-14: Moderate anxiety
    - 15-21: Severe anxiety
    """

    def __init__(self):
        self.questions = [
            AssessmentQuestion(
                number=1,
                text="Feeling nervous, anxious, or on edge",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=2,
                text="Not being able to stop or control worrying",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=3,
                text="Worrying too much about different things",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=4,
                text="Trouble relaxing",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=5,
                text="Being so restless that it's hard to sit still",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=6,
                text="Becoming easily annoyed or irritable",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            ),
            AssessmentQuestion(
                number=7,
                text="Feeling afraid as if something awful might happen",
                options=[
                    {"value": 0, "label": "Not at all"},
                    {"value": 1, "label": "Several days"},
                    {"value": 2, "label": "More than half the days"},
                    {"value": 3, "label": "Nearly every day"}
                ]
            )
        ]

    def calculate_score(self, responses: List[int]) -> AssessmentResult:
        """Calculate GAD-7 score and provide clinical interpretation"""
        if len(responses) != 7:
            raise ValueError("GAD-7 requires exactly 7 responses")

        total_score = sum(responses)

        # Determine severity level
        if total_score <= 4:
            severity = SeverityLevel.MINIMAL
            interpretation = "Minimal anxiety. No treatment indicated."
        elif total_score <= 9:
            severity = SeverityLevel.MILD
            interpretation = "Mild anxiety. Watchful waiting recommended. Consider psychoeducation and self-help resources."
        elif total_score <= 14:
            severity = SeverityLevel.MODERATE
            interpretation = "Moderate anxiety. Psychotherapy recommended (CBT or mindfulness-based interventions). Consider pharmacotherapy if appropriate."
        else:
            severity = SeverityLevel.SEVERE
            interpretation = "Severe anxiety. Active treatment indicated. Combination of psychotherapy and pharmacotherapy often most effective."

        risk_flags = []
        recommended_actions = []

        # Check for panic symptoms (restlessness, fear)
        if responses[4] >= 2 or responses[6] >= 2:
            risk_flags.append("Possible panic symptoms")
            recommended_actions.append("Screen for panic disorder")

        # Uncontrollable worry (GAD hallmark)
        if responses[1] >= 2:
            risk_flags.append("Difficulty controlling worry")
            recommended_actions.append("Consider GAD-specific interventions")

        if total_score >= 10:
            recommended_actions.append("Cognitive Behavioral Therapy (CBT) for anxiety recommended")
            recommended_actions.append("Consider relaxation training and mindfulness practices")
            recommended_actions.append("Assess for comorbid depression (administer PHQ-9)")

        if total_score >= 15:
            recommended_actions.append("Psychiatric evaluation for medication assessment")
            recommended_actions.append("Rule out other anxiety disorders (social anxiety, panic, PTSD)")

        return AssessmentResult(
            assessment_type="GAD-7",
            total_score=total_score,
            max_score=21,
            percentage=(total_score / 21) * 100,
            severity_level=severity,
            clinical_interpretation=interpretation,
            risk_flags=risk_flags,
            recommended_actions=recommended_actions,
            item_responses=responses,
            completed_at=datetime.now(UTC)
        )


class PSS10Assessment:
    """
    Perceived Stress Scale (PSS-10)

    Validated 10-item stress assessment
    Score range: 0-40
    - 0-13: Low stress
    - 14-26: Moderate stress
    - 27-40: High perceived stress
    """

    def __init__(self):
        self.questions = [
            AssessmentQuestion(
                number=1,
                text="In the last month, how often have you been upset because of something that happened unexpectedly?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ]
            ),
            AssessmentQuestion(
                number=2,
                text="In the last month, how often have you felt that you were unable to control the important things in your life?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ]
            ),
            AssessmentQuestion(
                number=3,
                text="In the last month, how often have you felt nervous and stressed?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ]
            ),
            AssessmentQuestion(
                number=4,
                text="In the last month, how often have you felt confident about your ability to handle your personal problems?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ],
                scoring_type="reverse_scored"
            ),
            AssessmentQuestion(
                number=5,
                text="In the last month, how often have you felt that things were going your way?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ],
                scoring_type="reverse_scored"
            ),
            AssessmentQuestion(
                number=6,
                text="In the last month, how often have you found that you could not cope with all the things that you had to do?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ]
            ),
            AssessmentQuestion(
                number=7,
                text="In the last month, how often have you been able to control irritations in your life?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ],
                scoring_type="reverse_scored"
            ),
            AssessmentQuestion(
                number=8,
                text="In the last month, how often have you felt that you were on top of things?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ],
                scoring_type="reverse_scored"
            ),
            AssessmentQuestion(
                number=9,
                text="In the last month, how often have you been angered because of things that were outside of your control?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ]
            ),
            AssessmentQuestion(
                number=10,
                text="In the last month, how often have you felt difficulties were piling up so high that you could not overcome them?",
                options=[
                    {"value": 0, "label": "Never"},
                    {"value": 1, "label": "Almost never"},
                    {"value": 2, "label": "Sometimes"},
                    {"value": 3, "label": "Fairly often"},
                    {"value": 4, "label": "Very often"}
                ]
            )
        ]

    def calculate_score(self, responses: List[int]) -> AssessmentResult:
        """Calculate PSS-10 score with reverse scoring for items 4, 5, 7, 8"""
        if len(responses) != 10:
            raise ValueError("PSS-10 requires exactly 10 responses")

        # Reverse score items 4, 5, 7, 8 (indices 3, 4, 6, 7)
        reverse_scored_indices = [3, 4, 6, 7]
        scored_responses = []

        for i, response in enumerate(responses):
            if i in reverse_scored_indices:
                scored_responses.append(4 - response)
            else:
                scored_responses.append(response)

        total_score = sum(scored_responses)

        # Determine stress level
        if total_score <= 13:
            severity = SeverityLevel.MINIMAL
            interpretation = "Low perceived stress. Coping resources appear adequate for current demands."
        elif total_score <= 26:
            severity = SeverityLevel.MODERATE
            interpretation = "Moderate perceived stress. May benefit from stress management techniques and lifestyle modifications."
        else:
            severity = SeverityLevel.SEVERE
            interpretation = "High perceived stress. Significant risk for stress-related health problems. Active stress management intervention recommended."

        risk_flags = []
        recommended_actions = []

        # Check for poor coping (items 4, 5, 7, 8)
        coping_items = [responses[i] for i in reverse_scored_indices]
        if sum(coping_items) <= 4:  # Low confidence in coping
            risk_flags.append("Low perceived coping ability")
            recommended_actions.append("Build coping skills and resilience")

        # Check for feeling overwhelmed (items 2, 6, 10)
        overwhelm_score = responses[1] + responses[5] + responses[9]
        if overwhelm_score >= 9:
            risk_flags.append("Feeling overwhelmed")
            recommended_actions.append("Address life stressors and time management")

        if total_score >= 14:
            recommended_actions.append("Stress reduction techniques: progressive muscle relaxation, deep breathing")
            recommended_actions.append("Consider mindfulness-based stress reduction (MBSR)")
            recommended_actions.append("Evaluate work-life balance and self-care practices")

        if total_score >= 27:
            recommended_actions.append("Comprehensive stress assessment recommended")
            recommended_actions.append("Screen for anxiety and depression (GAD-7, PHQ-9)")
            recommended_actions.append("Consider therapy for stress management")

        return AssessmentResult(
            assessment_type="PSS-10",
            total_score=total_score,
            max_score=40,
            percentage=(total_score / 40) * 100,
            severity_level=severity,
            clinical_interpretation=interpretation,
            risk_flags=risk_flags,
            recommended_actions=recommended_actions,
            item_responses=responses,
            completed_at=datetime.now(UTC)
        )


class WEMWBSAssessment:
    """
    Warwick-Edinburgh Mental Wellbeing Scale (WEMWBS)

    Validated 14-item positive mental wellbeing scale
    Score range: 14-70
    Higher scores indicate greater wellbeing
    - 14-40: Low wellbeing
    - 41-59: Moderate wellbeing
    - 60-70: High wellbeing
    """

    def __init__(self):
        self.questions = [
            AssessmentQuestion(
                number=1,
                text="I've been feeling optimistic about the future",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=2,
                text="I've been feeling useful",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=3,
                text="I've been feeling relaxed",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=4,
                text="I've been feeling interested in other people",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=5,
                text="I've had energy to spare",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=6,
                text="I've been dealing with problems well",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=7,
                text="I've been thinking clearly",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=8,
                text="I've been feeling good about myself",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=9,
                text="I've been feeling close to other people",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=10,
                text="I've been feeling confident",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=11,
                text="I've been able to make up my own mind about things",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=12,
                text="I've been feeling loved",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=13,
                text="I've been interested in new things",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            ),
            AssessmentQuestion(
                number=14,
                text="I've been feeling cheerful",
                options=[
                    {"value": 1, "label": "None of the time"},
                    {"value": 2, "label": "Rarely"},
                    {"value": 3, "label": "Some of the time"},
                    {"value": 4, "label": "Often"},
                    {"value": 5, "label": "All of the time"}
                ]
            )
        ]

    def calculate_score(self, responses: List[int]) -> AssessmentResult:
        """Calculate WEMWBS score - higher scores indicate better wellbeing"""
        if len(responses) != 14:
            raise ValueError("WEMWBS requires exactly 14 responses")

        total_score = sum(responses)

        # Determine wellbeing level
        if total_score <= 40:
            severity = SeverityLevel.SEVERE  # Low wellbeing
            interpretation = "Low mental wellbeing. May be experiencing mental health difficulties. Professional support recommended."
        elif total_score <= 59:
            severity = SeverityLevel.MODERATE
            interpretation = "Moderate mental wellbeing. Some room for improvement in positive mental health."
        else:
            severity = SeverityLevel.MINIMAL  # High wellbeing
            interpretation = "High mental wellbeing. Positive mental health indicators present."

        risk_flags = []
        recommended_actions = []

        # Low scores on key items
        if responses[0] <= 2:  # Optimism
            risk_flags.append("Low optimism")
        if responses[7] <= 2:  # Self-esteem
            risk_flags.append("Low self-esteem")
        if responses[9] <= 2:  # Confidence
            risk_flags.append("Low confidence")

        if total_score <= 40:
            recommended_actions.append("Comprehensive mental health assessment recommended")
            recommended_actions.append("Screen for depression and anxiety")
            recommended_actions.append("Consider positive psychology interventions")

        if total_score <= 59:
            recommended_actions.append("Wellbeing enhancement activities: gratitude practice, social connection, physical activity")
            recommended_actions.append("Consider strengths-based interventions")

        if total_score >= 60:
            recommended_actions.append("Maintain current wellbeing practices")
            recommended_actions.append("Continue protective factors (social support, self-care, purpose)")

        return AssessmentResult(
            assessment_type="WEMWBS",
            total_score=total_score,
            max_score=70,
            percentage=(total_score / 70) * 100,
            severity_level=severity,
            clinical_interpretation=interpretation,
            risk_flags=risk_flags,
            recommended_actions=recommended_actions,
            item_responses=responses,
            completed_at=datetime.now(UTC)
        )


class ClinicalAssessmentManager:
    """Manager class for all clinical assessments"""

    def __init__(self):
        self.phq9 = PHQ9Assessment()
        self.gad7 = GAD7Assessment()
        self.pss10 = PSS10Assessment()
        self.wemwbs = WEMWBSAssessment()

    def get_assessment(self, assessment_type: str):
        """Get assessment tool by type"""
        assessments = {
            "PHQ-9": self.phq9,
            "GAD-7": self.gad7,
            "PSS-10": self.pss10,
            "WEMWBS": self.wemwbs
        }
        return assessments.get(assessment_type)

    def calculate_score(self, assessment_type: str, responses: List[int]) -> AssessmentResult:
        """Calculate score for any assessment type"""
        assessment = self.get_assessment(assessment_type)
        if not assessment:
            raise ValueError(f"Unknown assessment type: {assessment_type}")
        return assessment.calculate_score(responses)

    def get_questions(self, assessment_type: str) -> List[AssessmentQuestion]:
        """Get questions for an assessment"""
        assessment = self.get_assessment(assessment_type)
        if not assessment:
            raise ValueError(f"Unknown assessment type: {assessment_type}")
        return assessment.questions

    def export_result_to_json(self, result: AssessmentResult) -> str:
        """Export assessment result to JSON"""
        return json.dumps({
            "assessment_type": result.assessment_type,
            "total_score": result.total_score,
            "max_score": result.max_score,
            "percentage": result.percentage,
            "severity_level": result.severity_level.value,
            "clinical_interpretation": result.clinical_interpretation,
            "risk_flags": result.risk_flags,
            "recommended_actions": result.recommended_actions,
            "item_responses": result.item_responses,
            "completed_at": result.completed_at.isoformat()
        }, indent=2)


# Global instance
assessment_manager = ClinicalAssessmentManager()
