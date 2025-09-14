"""
Crisis Intervention & Emergency Response System
24/7 crisis support, emergency protocols, and safety planning
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
from enum import Enum
import random

class CrisisLevel(Enum):
    GREEN = "green"  # No immediate risk
    YELLOW = "yellow"  # Elevated risk, monitoring needed
    ORANGE = "orange"  # High risk, intervention required
    RED = "red"  # Critical risk, immediate action needed
    PURPLE = "purple"  # Active emergency, 911/emergency services

class InterventionType(Enum):
    AUTOMATED_CHECK_IN = "automated_check_in"
    PEER_SUPPORT = "peer_support"
    CRISIS_COUNSELOR = "crisis_counselor"
    THERAPIST_ALERT = "therapist_alert"
    EMERGENCY_CONTACT = "emergency_contact"
    EMERGENCY_SERVICES = "emergency_services"
    SAFETY_PLAN_ACTIVATION = "safety_plan_activation"
    HOSPITALIZATION = "hospitalization"

class ResponseChannel(Enum):
    IN_APP_CHAT = "in_app_chat"
    SMS = "sms"
    PHONE_CALL = "phone_call"
    VIDEO_CALL = "video_call"
    EMAIL = "email"
    PUSH_NOTIFICATION = "push_notification"
    EMERGENCY_DISPATCH = "emergency_dispatch"

class SafetyPlanElement(Enum):
    WARNING_SIGNS = "warning_signs"
    COPING_STRATEGIES = "coping_strategies"
    SUPPORT_CONTACTS = "support_contacts"
    PROFESSIONAL_CONTACTS = "professional_contacts"
    ENVIRONMENT_SAFETY = "environment_safety"
    EMERGENCY_SERVICES = "emergency_services"

@dataclass
class CrisisAlert:
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    crisis_level: CrisisLevel = CrisisLevel.YELLOW
    trigger_source: str = "behavioral_analysis"  # behavioral_analysis, user_report, third_party
    trigger_data: Dict[str, Any] = field(default_factory=dict)
    risk_factors: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)
    immediate_concerns: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    escalated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    response_time_seconds: Optional[float] = None
    interventions_triggered: List[InterventionType] = field(default_factory=list)

@dataclass
class SafetyPlan:
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    created_with_therapist: bool = True
    warning_signs: List[str] = field(default_factory=list)
    internal_coping_strategies: List[str] = field(default_factory=list)
    social_support_contacts: List[Dict[str, str]] = field(default_factory=list)
    professional_contacts: List[Dict[str, str]] = field(default_factory=list)
    environmental_safety_steps: List[str] = field(default_factory=list)
    emergency_services_info: Dict[str, str] = field(default_factory=dict)
    personalized_reminders: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    last_reviewed: Optional[datetime] = None
    activation_count: int = 0

@dataclass
class CrisisIntervention:
    intervention_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    alert_id: str = ""
    user_id: str = ""
    intervention_type: InterventionType = InterventionType.AUTOMATED_CHECK_IN
    response_channel: ResponseChannel = ResponseChannel.IN_APP_CHAT
    initiated_at: datetime = field(default_factory=datetime.now)
    responder_id: Optional[str] = None  # Crisis counselor or therapist ID
    response_content: str = ""
    user_response: Optional[str] = None
    response_received_at: Optional[datetime] = None
    intervention_outcome: Optional[str] = None
    effectiveness_score: Optional[float] = None
    follow_up_required: bool = False
    follow_up_scheduled: Optional[datetime] = None

@dataclass
class EmergencyContact:
    contact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    name: str = ""
    relationship: str = ""
    phone_number: str = ""
    email: str = ""
    priority_level: int = 1  # 1 = highest priority
    can_be_contacted_24_7: bool = True
    preferred_contact_method: ResponseChannel = ResponseChannel.PHONE_CALL
    location: str = ""
    special_instructions: str = ""
    last_contacted: Optional[datetime] = None
    consent_to_contact: bool = True

@dataclass
class CrisisCounselor:
    counselor_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    credentials: List[str] = field(default_factory=list)
    specializations: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)
    availability_schedule: Dict[str, List[str]] = field(default_factory=dict)
    current_case_load: int = 0
    max_case_load: int = 10
    status: str = "available"  # available, busy, offline
    response_time_avg: float = 180.0  # seconds
    effectiveness_rating: float = 4.5
    total_interventions: int = 0

@dataclass
class ResourceDirectory:
    resource_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    resource_type: str = "hotline"  # hotline, website, app, location
    description: str = ""
    phone_number: Optional[str] = None
    website_url: Optional[str] = None
    available_24_7: bool = False
    languages_supported: List[str] = field(default_factory=list)
    geographic_coverage: List[str] = field(default_factory=list)
    target_demographics: List[str] = field(default_factory=list)
    specialties: List[str] = field(default_factory=list)
    cost: str = "free"
    accessibility_features: List[str] = field(default_factory=list)

class CrisisInterventionSystem:
    def __init__(self):
        self.active_alerts: Dict[str, CrisisAlert] = {}
        self.safety_plans: Dict[str, SafetyPlan] = {}
        self.interventions: Dict[str, List[CrisisIntervention]] = {}
        self.emergency_contacts: Dict[str, List[EmergencyContact]] = {}
        self.crisis_counselors: Dict[str, CrisisCounselor] = {}
        self.resource_directory = self._initialize_resource_directory()
        self.escalation_protocols = self._initialize_escalation_protocols()

    def _initialize_resource_directory(self) -> List[ResourceDirectory]:
        """Initialize crisis resource directory"""
        resources = []

        # National crisis hotlines
        resources.append(ResourceDirectory(
            name="988 Suicide & Crisis Lifeline",
            resource_type="hotline",
            description="24/7 crisis support for suicidal thoughts or emotional distress",
            phone_number="988",
            website_url="https://988lifeline.org",
            available_24_7=True,
            languages_supported=["English", "Spanish"],
            geographic_coverage=["United States"],
            specialties=["suicide_prevention", "crisis_counseling"],
            accessibility_features=["hearing_impaired", "chat_support"]
        ))

        resources.append(ResourceDirectory(
            name="Crisis Text Line",
            resource_type="hotline",
            description="24/7 crisis support via text messaging",
            phone_number="741741",
            website_url="https://crisistextline.org",
            available_24_7=True,
            languages_supported=["English", "Spanish"],
            geographic_coverage=["United States", "Canada", "United Kingdom"],
            specialties=["crisis_counseling", "youth_support"],
            accessibility_features=["text_based", "anonymous"]
        ))

        # Specialized support lines
        resources.append(ResourceDirectory(
            name="National Domestic Violence Hotline",
            resource_type="hotline",
            description="24/7 support for domestic violence situations",
            phone_number="1-800-799-7233",
            website_url="https://thehotline.org",
            available_24_7=True,
            languages_supported=["English", "Spanish", "200+ languages via interpretation"],
            specialties=["domestic_violence", "safety_planning"],
            accessibility_features=["TTY", "online_chat"]
        ))

        resources.append(ResourceDirectory(
            name="SAMHSA National Helpline",
            resource_type="hotline",
            description="24/7 treatment referral and information service",
            phone_number="1-800-662-4357",
            website_url="https://samhsa.gov",
            available_24_7=True,
            languages_supported=["English", "Spanish"],
            specialties=["substance_abuse", "mental_health_treatment", "referrals"],
            accessibility_features=["TTY"]
        ))

        # International resources
        resources.append(ResourceDirectory(
            name="Samaritans (UK)",
            resource_type="hotline",
            description="24/7 emotional support for anyone in distress",
            phone_number="116 123",
            website_url="https://samaritans.org",
            available_24_7=True,
            languages_supported=["English"],
            geographic_coverage=["United Kingdom", "Ireland"],
            specialties=["emotional_support", "suicide_prevention"]
        ))

        # Online resources
        resources.append(ResourceDirectory(
            name="7 Cups",
            resource_type="website",
            description="Free emotional support and online therapy",
            website_url="https://7cups.com",
            available_24_7=True,
            languages_supported=["English", "Spanish", "French", "German"],
            cost="free_and_paid",
            specialties=["peer_support", "online_therapy", "chat_support"]
        ))

        return resources

    def _initialize_escalation_protocols(self) -> Dict[CrisisLevel, Dict[str, Any]]:
        """Initialize crisis escalation protocols"""
        return {
            CrisisLevel.GREEN: {
                "response_time_max": 3600,  # 1 hour
                "interventions": [InterventionType.AUTOMATED_CHECK_IN],
                "escalation_criteria": ["no_response_24h", "risk_factors_increase"],
                "monitoring_frequency": "daily"
            },
            CrisisLevel.YELLOW: {
                "response_time_max": 1800,  # 30 minutes
                "interventions": [InterventionType.AUTOMATED_CHECK_IN, InterventionType.PEER_SUPPORT],
                "escalation_criteria": ["suicidal_ideation", "self_harm_intent", "no_response_2h"],
                "monitoring_frequency": "every_4_hours"
            },
            CrisisLevel.ORANGE: {
                "response_time_max": 600,  # 10 minutes
                "interventions": [InterventionType.CRISIS_COUNSELOR, InterventionType.THERAPIST_ALERT],
                "escalation_criteria": ["immediate_danger", "suicide_plan", "self_harm_attempt"],
                "monitoring_frequency": "every_hour"
            },
            CrisisLevel.RED: {
                "response_time_max": 180,  # 3 minutes
                "interventions": [InterventionType.CRISIS_COUNSELOR, InterventionType.EMERGENCY_CONTACT, InterventionType.SAFETY_PLAN_ACTIVATION],
                "escalation_criteria": ["active_suicide_attempt", "imminent_danger", "psychosis"],
                "monitoring_frequency": "continuous"
            },
            CrisisLevel.PURPLE: {
                "response_time_max": 60,  # 1 minute
                "interventions": [InterventionType.EMERGENCY_SERVICES, InterventionType.EMERGENCY_CONTACT],
                "escalation_criteria": [],  # Highest level
                "monitoring_frequency": "continuous"
            }
        }

    def assess_crisis_level(self, user_id: str, trigger_data: Dict[str, Any], trigger_source: str) -> CrisisAlert:
        """Assess crisis level based on multiple risk factors"""

        # Initialize risk scoring
        risk_score = 0
        risk_factors = []
        protective_factors = []
        immediate_concerns = []

        # Analyze trigger data based on source
        if trigger_source == "behavioral_analysis":
            risk_score += self._assess_behavioral_risk(trigger_data, risk_factors)
        elif trigger_source == "user_report":
            risk_score += self._assess_user_reported_risk(trigger_data, risk_factors, immediate_concerns)
        elif trigger_source == "third_party":
            risk_score += self._assess_third_party_risk(trigger_data, risk_factors)

        # Factor in protective elements
        protective_score = self._assess_protective_factors(user_id, protective_factors)
        adjusted_risk = max(0, risk_score - protective_score)

        # Determine crisis level
        crisis_level = self._determine_crisis_level(adjusted_risk, immediate_concerns)

        # Create crisis alert
        alert = CrisisAlert(
            user_id=user_id,
            crisis_level=crisis_level,
            trigger_source=trigger_source,
            trigger_data=trigger_data,
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            immediate_concerns=immediate_concerns
        )

        self.active_alerts[alert.alert_id] = alert

        # Trigger immediate response
        self._initiate_crisis_response(alert)

        return alert

    def _assess_behavioral_risk(self, data: Dict[str, Any], risk_factors: List[str]) -> float:
        """Assess risk from behavioral analysis data"""
        risk_score = 0

        # Sleep disruption
        if data.get("sleep_disruption_severity", 0) > 0.7:
            risk_score += 15
            risk_factors.append("severe_sleep_disruption")

        # Social withdrawal
        if data.get("social_withdrawal_score", 0) > 0.8:
            risk_score += 20
            risk_factors.append("extreme_social_isolation")

        # Mood indicators
        if data.get("negative_sentiment_score", 0) > 0.9:
            risk_score += 25
            risk_factors.append("severe_negative_mood")

        # Communication patterns
        if data.get("communication_decline", 0) > 0.9:
            risk_score += 15
            risk_factors.append("communication_shutdown")

        # Stress levels
        if data.get("stress_level", 0) > 0.9:
            risk_score += 20
            risk_factors.append("extreme_stress")

        return risk_score

    def _assess_user_reported_risk(self, data: Dict[str, Any], risk_factors: List[str], immediate_concerns: List[str]) -> float:
        """Assess risk from user self-reporting"""
        risk_score = 0

        # Direct suicidal ideation
        if data.get("suicidal_thoughts", False):
            if data.get("suicide_plan", False):
                risk_score += 80
                immediate_concerns.append("suicide_plan_identified")
                risk_factors.append("active_suicide_planning")
            else:
                risk_score += 50
                risk_factors.append("suicidal_ideation")

        # Self-harm indicators
        if data.get("self_harm_intent", False):
            risk_score += 40
            immediate_concerns.append("self_harm_intent")
            risk_factors.append("self_harm_risk")

        # Hopelessness
        if data.get("hopelessness_score", 0) > 8:  # 1-10 scale
            risk_score += 30
            risk_factors.append("severe_hopelessness")

        # Substance use
        if data.get("substance_use_increase", False):
            risk_score += 20
            risk_factors.append("substance_abuse_escalation")

        # Crisis request
        if data.get("crisis_help_requested", False):
            risk_score += 60
            immediate_concerns.append("user_requesting_crisis_help")

        return risk_score

    def _assess_third_party_risk(self, data: Dict[str, Any], risk_factors: List[str]) -> float:
        """Assess risk from third-party reports (family, friends, providers)"""
        risk_score = 0

        reporter_relationship = data.get("reporter_relationship", "")

        # High-credibility reporters
        if reporter_relationship in ["therapist", "psychiatrist", "family_member"]:
            credibility_multiplier = 1.5
        else:
            credibility_multiplier = 1.0

        # Reported concerns
        concerns = data.get("reported_concerns", [])

        concern_weights = {
            "expressed_suicidal_thoughts": 70,
            "suicide_attempt": 90,
            "self_harm_behavior": 50,
            "extreme_mood_changes": 30,
            "substance_abuse": 25,
            "psychotic_symptoms": 60,
            "aggressive_behavior": 40,
            "complete_withdrawal": 35
        }

        for concern in concerns:
            if concern in concern_weights:
                weighted_score = concern_weights[concern] * credibility_multiplier
                risk_score += weighted_score
                risk_factors.append(f"third_party_reported_{concern}")

        return risk_score

    def _assess_protective_factors(self, user_id: str, protective_factors: List[str]) -> float:
        """Assess protective factors that reduce risk"""
        protective_score = 0

        # Active safety plan
        if self.safety_plans.get(user_id):
            protective_score += 15
            protective_factors.append("active_safety_plan")

        # Recent therapy engagement
        # (Would check therapy system for recent sessions)
        if random.choice([True, False]):  # Simulated
            protective_score += 10
            protective_factors.append("recent_therapy_engagement")

        # Strong support network
        emergency_contacts = self.emergency_contacts.get(user_id, [])
        if len(emergency_contacts) >= 3:
            protective_score += 10
            protective_factors.append("strong_support_network")

        # Medication compliance
        # (Would check medication tracking system)
        if random.choice([True, False]):  # Simulated
            protective_score += 8
            protective_factors.append("medication_compliance")

        # Recent positive activities
        # (Would check activity tracking)
        if random.choice([True, False]):  # Simulated
            protective_score += 5
            protective_factors.append("recent_positive_activities")

        return protective_score

    def _determine_crisis_level(self, risk_score: float, immediate_concerns: List[str]) -> CrisisLevel:
        """Determine crisis level based on risk score and immediate concerns"""

        # Immediate escalation for certain concerns
        critical_concerns = ["suicide_plan_identified", "active_suicide_attempt", "imminent_danger"]
        if any(concern in immediate_concerns for concern in critical_concerns):
            return CrisisLevel.RED

        emergency_concerns = ["ongoing_suicide_attempt", "active_psychosis", "violent_behavior"]
        if any(concern in immediate_concerns for concern in emergency_concerns):
            return CrisisLevel.PURPLE

        # Score-based assessment
        if risk_score >= 70:
            return CrisisLevel.RED
        elif risk_score >= 50:
            return CrisisLevel.ORANGE
        elif risk_score >= 25:
            return CrisisLevel.YELLOW
        else:
            return CrisisLevel.GREEN

    def _initiate_crisis_response(self, alert: CrisisAlert):
        """Initiate appropriate crisis response based on alert level"""
        protocol = self.escalation_protocols[alert.crisis_level]

        # Record response initiation time
        response_start = datetime.now()

        # Trigger appropriate interventions
        for intervention_type in protocol["interventions"]:
            self._execute_intervention(alert, intervention_type)

        # Calculate response time
        alert.response_time_seconds = (datetime.now() - response_start).total_seconds()

    def _execute_intervention(self, alert: CrisisAlert, intervention_type: InterventionType):
        """Execute specific crisis intervention"""

        intervention = CrisisIntervention(
            alert_id=alert.alert_id,
            user_id=alert.user_id,
            intervention_type=intervention_type
        )

        if intervention_type == InterventionType.AUTOMATED_CHECK_IN:
            intervention.response_channel = ResponseChannel.IN_APP_CHAT
            intervention.response_content = self._generate_check_in_message(alert)

        elif intervention_type == InterventionType.CRISIS_COUNSELOR:
            counselor = self._assign_crisis_counselor(alert)
            if counselor:
                intervention.responder_id = counselor.counselor_id
                intervention.response_channel = ResponseChannel.VIDEO_CALL
                intervention.response_content = "Crisis counselor assigned and initiating contact"

        elif intervention_type == InterventionType.EMERGENCY_CONTACT:
            self._contact_emergency_contacts(alert, intervention)

        elif intervention_type == InterventionType.SAFETY_PLAN_ACTIVATION:
            self._activate_safety_plan(alert, intervention)

        elif intervention_type == InterventionType.EMERGENCY_SERVICES:
            self._contact_emergency_services(alert, intervention)

        # Store intervention
        if alert.user_id not in self.interventions:
            self.interventions[alert.user_id] = []
        self.interventions[alert.user_id].append(intervention)

        alert.interventions_triggered.append(intervention_type)

    def _generate_check_in_message(self, alert: CrisisAlert) -> str:
        """Generate personalized check-in message"""

        if alert.crisis_level == CrisisLevel.YELLOW:
            return ("Hi there. I've noticed you might be going through a tough time. "
                   "How are you feeling right now? Remember that support is available 24/7. "
                   "Would you like to talk to someone or review your safety plan?")

        elif alert.crisis_level == CrisisLevel.ORANGE:
            return ("I'm concerned about you and want to make sure you're safe. "
                   "You're not alone in this. A crisis counselor is standing by to talk. "
                   "If you're having thoughts of hurting yourself, please reach out immediately. "
                   "Text 'CRISIS' for immediate help or call 988.")

        elif alert.crisis_level == CrisisLevel.RED:
            return ("This is an urgent safety check. If you're in immediate danger, please call 911. "
                   "A crisis counselor is being connected to you right now. "
                   "You matter and help is available. Please stay safe.")

        else:
            return ("Just checking in to see how you're doing today. "
                   "Remember that support is always available if you need it.")

    def _assign_crisis_counselor(self, alert: CrisisAlert) -> Optional[CrisisCounselor]:
        """Assign available crisis counselor"""

        # Find available counselors
        available_counselors = [
            counselor for counselor in self.crisis_counselors.values()
            if counselor.status == "available" and counselor.current_case_load < counselor.max_case_load
        ]

        if not available_counselors:
            # Escalate to backup system
            return None

        # Select best match based on specialization and response time
        best_counselor = min(available_counselors,
                           key=lambda c: c.response_time_avg)

        # Update counselor status
        best_counselor.current_case_load += 1
        best_counselor.status = "busy"

        return best_counselor

    def _contact_emergency_contacts(self, alert: CrisisAlert, intervention: CrisisIntervention):
        """Contact user's emergency contacts"""
        contacts = self.emergency_contacts.get(alert.user_id, [])

        if not contacts:
            intervention.response_content = "No emergency contacts available"
            return

        # Sort by priority and contact
        contacts.sort(key=lambda c: c.priority_level)

        contacted_successfully = []
        for contact in contacts[:3]:  # Contact top 3 priority contacts
            if contact.can_be_contacted_24_7 or self._is_appropriate_time():
                # Simulate contact attempt
                if random.random() > 0.2:  # 80% success rate
                    contacted_successfully.append(contact.name)
                    contact.last_contacted = datetime.now()

        intervention.response_content = f"Emergency contacts notified: {', '.join(contacted_successfully)}"
        intervention.response_channel = ResponseChannel.PHONE_CALL

    def _activate_safety_plan(self, alert: CrisisAlert, intervention: CrisisIntervention):
        """Activate user's safety plan"""
        safety_plan = self.safety_plans.get(alert.user_id)

        if not safety_plan:
            intervention.response_content = "No safety plan available - creating emergency plan"
            self._create_emergency_safety_plan(alert.user_id)
            return

        # Update plan activation
        safety_plan.activation_count += 1
        safety_plan.last_reviewed = datetime.now()

        # Generate safety plan reminder
        plan_elements = []
        if safety_plan.warning_signs:
            plan_elements.append(f"Warning signs to watch: {', '.join(safety_plan.warning_signs[:3])}")
        if safety_plan.internal_coping_strategies:
            plan_elements.append(f"Try these coping strategies: {', '.join(safety_plan.internal_coping_strategies[:3])}")
        if safety_plan.social_support_contacts:
            plan_elements.append(f"Reach out to: {safety_plan.social_support_contacts[0]['name']}")

        intervention.response_content = "Safety plan activated. " + " | ".join(plan_elements)
        intervention.response_channel = ResponseChannel.IN_APP_CHAT

    def _contact_emergency_services(self, alert: CrisisAlert, intervention: CrisisIntervention):
        """Contact emergency services (911/police/ambulance)"""

        # In real implementation, this would integrate with emergency dispatch systems
        # For now, we log the action and would typically require human verification

        intervention.response_content = "Emergency services contact initiated - requires human verification"
        intervention.response_channel = ResponseChannel.EMERGENCY_DISPATCH
        intervention.follow_up_required = True

    def _is_appropriate_time(self) -> bool:
        """Check if current time is appropriate for contacting emergency contacts"""
        current_hour = datetime.now().hour
        return 8 <= current_hour <= 22  # 8 AM to 10 PM

    def create_safety_plan(self, user_id: str, plan_data: Dict[str, Any], created_with_therapist: bool = True) -> SafetyPlan:
        """Create comprehensive safety plan for user"""

        safety_plan = SafetyPlan(
            user_id=user_id,
            created_with_therapist=created_with_therapist,
            warning_signs=plan_data.get("warning_signs", []),
            internal_coping_strategies=plan_data.get("coping_strategies", []),
            social_support_contacts=plan_data.get("support_contacts", []),
            professional_contacts=plan_data.get("professional_contacts", []),
            environmental_safety_steps=plan_data.get("safety_steps", []),
            emergency_services_info=plan_data.get("emergency_info", {}),
            personalized_reminders=plan_data.get("reminders", [])
        )

        # Add default elements if missing
        if not safety_plan.warning_signs:
            safety_plan.warning_signs = [
                "Feeling hopeless or worthless",
                "Withdrawing from friends and family",
                "Increased substance use",
                "Extreme mood changes"
            ]

        if not safety_plan.internal_coping_strategies:
            safety_plan.internal_coping_strategies = [
                "Practice deep breathing exercises",
                "Listen to calming music",
                "Take a warm shower or bath",
                "Write in a journal",
                "Exercise or go for a walk"
            ]

        if not safety_plan.emergency_services_info:
            safety_plan.emergency_services_info = {
                "suicide_prevention": "988",
                "crisis_text": "741741",
                "emergency": "911",
                "local_crisis_center": "Contact admin for local resources"
            }

        self.safety_plans[user_id] = safety_plan
        return safety_plan

    def _create_emergency_safety_plan(self, user_id: str) -> SafetyPlan:
        """Create emergency safety plan with default elements"""

        emergency_plan_data = {
            "warning_signs": [
                "Thoughts of suicide or self-harm",
                "Feeling trapped or hopeless",
                "Extreme agitation or anxiety"
            ],
            "coping_strategies": [
                "Call a trusted friend or family member",
                "Practice grounding techniques (5-4-3-2-1 method)",
                "Remove means of self-harm from environment",
                "Go to a safe, public place"
            ],
            "emergency_info": {
                "suicide_prevention": "988",
                "crisis_text": "741741",
                "emergency": "911"
            }
        }

        return self.create_safety_plan(user_id, emergency_plan_data, created_with_therapist=False)

    def add_emergency_contact(self, user_id: str, contact_data: Dict[str, Any]) -> EmergencyContact:
        """Add emergency contact for user"""

        contact = EmergencyContact(
            user_id=user_id,
            name=contact_data["name"],
            relationship=contact_data["relationship"],
            phone_number=contact_data["phone_number"],
            email=contact_data.get("email", ""),
            priority_level=contact_data.get("priority_level", 1),
            can_be_contacted_24_7=contact_data.get("available_24_7", True),
            preferred_contact_method=ResponseChannel(contact_data.get("preferred_method", "phone_call")),
            location=contact_data.get("location", ""),
            special_instructions=contact_data.get("instructions", "")
        )

        if user_id not in self.emergency_contacts:
            self.emergency_contacts[user_id] = []

        self.emergency_contacts[user_id].append(contact)

        # Sort by priority
        self.emergency_contacts[user_id].sort(key=lambda c: c.priority_level)

        return contact

    def register_crisis_counselor(self, counselor_data: Dict[str, Any]) -> CrisisCounselor:
        """Register new crisis counselor"""

        counselor = CrisisCounselor(
            name=counselor_data["name"],
            credentials=counselor_data.get("credentials", []),
            specializations=counselor_data.get("specializations", []),
            languages=counselor_data.get("languages", ["English"]),
            availability_schedule=counselor_data.get("schedule", {}),
            max_case_load=counselor_data.get("max_cases", 10)
        )

        self.crisis_counselors[counselor.counselor_id] = counselor
        return counselor

    def handle_user_response(self, intervention_id: str, user_response: str, response_channel: ResponseChannel) -> Dict[str, Any]:
        """Handle user response to crisis intervention"""

        # Find intervention
        intervention = None
        for user_interventions in self.interventions.values():
            for interv in user_interventions:
                if interv.intervention_id == intervention_id:
                    intervention = interv
                    break

        if not intervention:
            return {"error": "Intervention not found"}

        # Update intervention with response
        intervention.user_response = user_response
        intervention.response_received_at = datetime.now()

        # Analyze response for risk indicators
        response_analysis = self._analyze_user_response(user_response)

        # Determine if escalation is needed
        if response_analysis["escalation_needed"]:
            alert = self.active_alerts.get(intervention.alert_id)
            if alert:
                self._escalate_crisis(alert, response_analysis["escalation_reason"])

        # Generate follow-up recommendations
        follow_up = self._generate_follow_up_plan(intervention, response_analysis)

        return {
            "intervention_id": intervention_id,
            "response_acknowledged": True,
            "risk_assessment": response_analysis,
            "follow_up_plan": follow_up,
            "next_check_in": follow_up.get("next_check_in")
        }

    def _analyze_user_response(self, response: str) -> Dict[str, Any]:
        """Analyze user response for risk indicators"""

        response_lower = response.lower()

        # High-risk indicators
        high_risk_phrases = [
            "want to die", "kill myself", "end it all", "can't go on",
            "suicide", "not worth living", "better off dead"
        ]

        medium_risk_phrases = [
            "don't want to be here", "can't take it", "too much pain",
            "no point", "give up", "hurt myself"
        ]

        positive_indicators = [
            "feeling better", "will be okay", "getting help", "safe",
            "not going to hurt", "talking to someone"
        ]

        escalation_needed = any(phrase in response_lower for phrase in high_risk_phrases)
        escalation_reason = ""

        if escalation_needed:
            escalation_reason = "High-risk language detected in user response"

        # Calculate risk score from response
        risk_score = 0
        for phrase in high_risk_phrases:
            if phrase in response_lower:
                risk_score += 3

        for phrase in medium_risk_phrases:
            if phrase in response_lower:
                risk_score += 2

        for phrase in positive_indicators:
            if phrase in response_lower:
                risk_score -= 1

        risk_level = "high" if risk_score >= 3 else "medium" if risk_score >= 1 else "low"

        return {
            "escalation_needed": escalation_needed,
            "escalation_reason": escalation_reason,
            "risk_level": risk_level,
            "risk_score": max(0, risk_score),
            "positive_indicators_present": any(phrase in response_lower for phrase in positive_indicators)
        }

    def _escalate_crisis(self, alert: CrisisAlert, reason: str):
        """Escalate crisis to higher level"""

        current_level = alert.crisis_level

        # Escalate to next level
        escalation_map = {
            CrisisLevel.GREEN: CrisisLevel.YELLOW,
            CrisisLevel.YELLOW: CrisisLevel.ORANGE,
            CrisisLevel.ORANGE: CrisisLevel.RED,
            CrisisLevel.RED: CrisisLevel.PURPLE
        }

        if current_level in escalation_map:
            alert.crisis_level = escalation_map[current_level]
            alert.escalated_at = datetime.now()

            # Trigger additional interventions for new level
            self._initiate_crisis_response(alert)

    def _generate_follow_up_plan(self, intervention: CrisisIntervention, response_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate follow-up plan based on intervention outcome"""

        plan = {
            "next_check_in": None,
            "recommended_actions": [],
            "monitoring_frequency": "daily",
            "resources_provided": []
        }

        risk_level = response_analysis["risk_level"]

        if risk_level == "high":
            plan["next_check_in"] = (datetime.now() + timedelta(hours=2)).isoformat()
            plan["monitoring_frequency"] = "every_2_hours"
            plan["recommended_actions"] = [
                "Immediate safety planning",
                "Crisis counselor follow-up",
                "Emergency contact notification"
            ]
        elif risk_level == "medium":
            plan["next_check_in"] = (datetime.now() + timedelta(hours=6)).isoformat()
            plan["monitoring_frequency"] = "every_6_hours"
            plan["recommended_actions"] = [
                "Safety plan review",
                "Coping strategy practice",
                "Therapist outreach"
            ]
        else:
            plan["next_check_in"] = (datetime.now() + timedelta(hours=24)).isoformat()
            plan["monitoring_frequency"] = "daily"
            plan["recommended_actions"] = [
                "Continue regular monitoring",
                "Wellness activity engagement"
            ]

        # Add relevant resources
        plan["resources_provided"] = [
            {"name": "988 Suicide & Crisis Lifeline", "contact": "988"},
            {"name": "Crisis Text Line", "contact": "Text HOME to 741741"}
        ]

        return plan

    def get_crisis_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get crisis management dashboard for user"""

        # Get recent alerts
        user_alerts = [alert for alert in self.active_alerts.values() if alert.user_id == user_id]
        recent_alerts = sorted(user_alerts, key=lambda a: a.created_at, reverse=True)[:5]

        # Get safety plan status
        safety_plan = self.safety_plans.get(user_id)

        # Get emergency contacts
        contacts = self.emergency_contacts.get(user_id, [])

        # Get recent interventions
        recent_interventions = self.interventions.get(user_id, [])[-10:]

        dashboard = {
            "user_id": user_id,
            "current_risk_level": recent_alerts[0].crisis_level.value if recent_alerts else "green",
            "safety_plan_status": {
                "exists": safety_plan is not None,
                "last_updated": safety_plan.last_updated.isoformat() if safety_plan else None,
                "last_reviewed": safety_plan.last_reviewed.isoformat() if safety_plan and safety_plan.last_reviewed else None,
                "activation_count": safety_plan.activation_count if safety_plan else 0
            },
            "emergency_contacts": len(contacts),
            "recent_alerts": [
                {
                    "alert_id": alert.alert_id,
                    "crisis_level": alert.crisis_level.value,
                    "created_at": alert.created_at.isoformat(),
                    "trigger_source": alert.trigger_source,
                    "resolved": alert.resolved_at is not None
                }
                for alert in recent_alerts
            ],
            "recent_interventions": [
                {
                    "intervention_type": interv.intervention_type.value,
                    "initiated_at": interv.initiated_at.isoformat(),
                    "response_received": interv.user_response is not None,
                    "outcome": interv.intervention_outcome
                }
                for interv in recent_interventions
            ],
            "available_resources": len(self.resource_directory),
            "crisis_support_available": len([c for c in self.crisis_counselors.values() if c.status == "available"]) > 0
        }

        return dashboard

    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform-wide crisis intervention statistics"""

        total_alerts = len(self.active_alerts)
        active_high_risk = len([a for a in self.active_alerts.values() if a.crisis_level in [CrisisLevel.ORANGE, CrisisLevel.RED, CrisisLevel.PURPLE]])

        # Calculate average response times
        response_times = [a.response_time_seconds for a in self.active_alerts.values() if a.response_time_seconds]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Safety plan coverage
        total_users_with_plans = len(self.safety_plans)

        # Counselor availability
        available_counselors = len([c for c in self.crisis_counselors.values() if c.status == "available"])
        total_counselors = len(self.crisis_counselors)

        return {
            "total_crisis_alerts": total_alerts,
            "active_high_risk_alerts": active_high_risk,
            "safety_plans_created": total_users_with_plans,
            "available_crisis_counselors": available_counselors,
            "total_crisis_counselors": total_counselors,
            "average_response_time_seconds": round(avg_response_time, 1),
            "total_interventions": sum(len(interventions) for interventions in self.interventions.values()),
            "emergency_contacts_registered": sum(len(contacts) for contacts in self.emergency_contacts.values()),
            "crisis_resources_available": len(self.resource_directory),
            "escalation_rate": round(len([a for a in self.active_alerts.values() if a.escalated_at]) / max(1, total_alerts), 2),
            "resolution_rate": round(len([a for a in self.active_alerts.values() if a.resolved_at]) / max(1, total_alerts), 2)
        }

# Global instance
crisis_intervention_system = CrisisInterventionSystem()