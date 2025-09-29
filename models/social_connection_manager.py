"""
Social Connection Manager
=========================
Comprehensive social connection and peer support system for mental health.
Includes peer matching, group therapy, community challenges, and relationship tools.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
import hashlib
from sqlalchemy import text

logger = logging.getLogger(__name__)

class ConnectionType(Enum):
    """Types of peer connections"""
    SUPPORT_BUDDY = "support_buddy"
    GROUP_THERAPY = "group_therapy"
    COMMUNITY_CHALLENGE = "community_challenge"
    MENTOR_MENTEE = "mentor_mentee"
    FAMILY_SUPPORT = "family_support"

class MatchingCriteria(Enum):
    """Criteria for peer matching"""
    SIMILAR_CONDITIONS = "similar_conditions"
    COMPLEMENTARY_STRENGTHS = "complementary_strengths"
    GEOGRAPHIC_PROXIMITY = "geographic_proximity"
    AGE_SIMILARITY = "age_similarity"
    SHARED_INTERESTS = "shared_interests"
    THERAPY_STAGE = "therapy_stage"

class GroupSessionType(Enum):
    """Types of group therapy sessions"""
    ANXIETY_SUPPORT = "anxiety_support"
    DEPRESSION_RECOVERY = "depression_recovery"
    PTSD_HEALING = "ptsd_healing"
    ADDICTION_RECOVERY = "addiction_recovery"
    GRIEF_SUPPORT = "grief_support"
    RELATIONSHIP_SKILLS = "relationship_skills"
    PARENTING_SUPPORT = "parenting_support"
    TEEN_SUPPORT = "teen_support"

@dataclass
class PeerMatch:
    """Peer matching result"""
    user1_id: int
    user2_id: int
    connection_type: ConnectionType
    compatibility_score: float
    shared_attributes: List[str]
    recommended_activities: List[str]
    match_reasoning: str
    safety_level: str

@dataclass
class GroupSession:
    """Group therapy session details"""
    session_id: str
    session_type: GroupSessionType
    title: str
    description: str
    moderator_id: int
    max_participants: int
    current_participants: List[int]
    scheduled_time: datetime
    duration_minutes: int
    meeting_link: str
    preparation_materials: List[str]
    session_guidelines: List[str]

@dataclass
class CommunityChallenge:
    """Community wellness challenge"""
    challenge_id: str
    title: str
    description: str
    challenge_type: str  # fitness, mindfulness, social, creative
    duration_days: int
    participants: List[int]
    daily_activities: List[str]
    rewards_system: Dict[str, Any]
    progress_tracking: Dict[str, Any]

class SocialConnectionManager:
    """Manages all social connection and peer support features"""

    def __init__(self):
        self.matching_algorithms = self._initialize_matching_algorithms()
        self.group_templates = self._initialize_group_templates()
        self.challenge_library = self._initialize_challenge_library()
        self.safety_protocols = self._initialize_safety_protocols()
        self.active_connections = {}
        self.moderation_queue = []

    def _initialize_matching_algorithms(self) -> Dict[str, Any]:
        """Initialize peer matching algorithms"""
        return {
            "support_buddy": {
                "weight_factors": {
                    "similar_conditions": 0.4,
                    "therapy_stage": 0.3,
                    "age_similarity": 0.1,
                    "geographic_proximity": 0.1,
                    "shared_interests": 0.1
                },
                "minimum_compatibility": 0.6,
                "safety_checks": ["verified_identity", "no_red_flags", "consent_given"]
            },
            "group_therapy": {
                "weight_factors": {
                    "similar_conditions": 0.5,
                    "therapy_stage": 0.2,
                    "communication_style": 0.2,
                    "availability": 0.1
                },
                "group_size_optimal": 6,
                "group_size_max": 10
            },
            "mentor_mentee": {
                "weight_factors": {
                    "experience_gap": 0.4,
                    "similar_conditions": 0.3,
                    "mentoring_skills": 0.2,
                    "availability": 0.1
                },
                "mentor_requirements": ["recovery_stability", "communication_skills", "training_completed"]
            }
        }

    def _initialize_group_templates(self) -> Dict[str, Any]:
        """Initialize group therapy session templates"""
        return {
            "anxiety_support": {
                "title": "Anxiety Support Circle",
                "description": "A safe space to share experiences and coping strategies for anxiety",
                "max_participants": 8,
                "duration_minutes": 60,
                "session_structure": [
                    "Welcome and check-in (10 min)",
                    "Topic discussion (30 min)",
                    "Coping strategies sharing (15 min)",
                    "Closing and resources (5 min)"
                ],
                "preparation_materials": [
                    "Anxiety tracking worksheet",
                    "Breathing exercise guide",
                    "Crisis contact information"
                ],
                "guidelines": [
                    "Respect confidentiality of all participants",
                    "Use 'I' statements when sharing",
                    "No giving medical advice",
                    "Support without judgment"
                ]
            },
            "depression_recovery": {
                "title": "Depression Recovery Journey",
                "description": "Supporting each other through depression recovery with hope and understanding",
                "max_participants": 6,
                "duration_minutes": 75,
                "session_structure": [
                    "Mood check-in (15 min)",
                    "Weekly wins sharing (20 min)",
                    "Challenge discussion (25 min)",
                    "Goal setting for next week (10 min)",
                    "Closing affirmations (5 min)"
                ],
                "preparation_materials": [
                    "Mood tracking journal",
                    "Activity scheduling worksheet",
                    "Self-compassion exercises"
                ],
                "guidelines": [
                    "Celebrate small victories",
                    "Hold space for difficult emotions",
                    "Share hope and encouragement",
                    "Respect different recovery paths"
                ]
            },
            "ptsd_healing": {
                "title": "PTSD Healing Circle",
                "description": "Trauma-informed support group for PTSD recovery",
                "max_participants": 6,
                "duration_minutes": 90,
                "session_structure": [
                    "Grounding exercise (10 min)",
                    "Safety check-in (10 min)",
                    "Guided sharing (40 min)",
                    "Coping skills practice (20 min)",
                    "Closing ritual (10 min)"
                ],
                "preparation_materials": [
                    "Grounding techniques card",
                    "Safety plan template",
                    "Trauma-informed resources"
                ],
                "guidelines": [
                    "Trauma-informed approach always",
                    "Right to pass on sharing",
                    "No graphic details required",
                    "Professional facilitator present"
                ]
            }
        }

    def _initialize_challenge_library(self) -> Dict[str, Any]:
        """Initialize community challenge library"""
        return {
            "mindful_march": {
                "title": "30-Day Mindfulness Challenge",
                "description": "Build a sustainable mindfulness practice together",
                "type": "mindfulness",
                "duration_days": 30,
                "daily_activities": [
                    "5-minute morning meditation",
                    "Mindful meal practice",
                    "Gratitude journaling",
                    "Evening reflection"
                ],
                "rewards": {
                    "daily_completion": 10,
                    "weekly_streak": 50,
                    "full_challenge": 200,
                    "peer_support": 25
                },
                "community_features": [
                    "Daily check-in posts",
                    "Meditation buddy matching",
                    "Weekly group meditation",
                    "Progress sharing celebration"
                ]
            },
            "movement_may": {
                "title": "Mental Health Movement Challenge",
                "description": "Exercise for mental wellness - any movement counts!",
                "type": "fitness",
                "duration_days": 31,
                "daily_activities": [
                    "20 minutes of any movement",
                    "Mood tracking before/after",
                    "Movement type logging",
                    "Energy level assessment"
                ],
                "rewards": {
                    "daily_movement": 15,
                    "mood_improvement": 20,
                    "variety_bonus": 30,
                    "encouragement_given": 10
                },
                "community_features": [
                    "Movement photo sharing",
                    "Workout buddy matching",
                    "Virtual group classes",
                    "Progress celebration posts"
                ]
            },
            "connection_challenge": {
                "title": "Social Connection Challenge",
                "description": "Building meaningful connections for better mental health",
                "type": "social",
                "duration_days": 21,
                "daily_activities": [
                    "Reach out to one person",
                    "Practice active listening",
                    "Share something personal",
                    "Express gratitude to someone"
                ],
                "rewards": {
                    "daily_connection": 20,
                    "deep_conversation": 35,
                    "new_relationship": 50,
                    "support_given": 25
                },
                "community_features": [
                    "Connection story sharing",
                    "Conversation starter prompts",
                    "Virtual coffee meetups",
                    "Friendship matching"
                ]
            }
        }

    def _initialize_safety_protocols(self) -> Dict[str, Any]:
        """Initialize safety and moderation protocols"""
        return {
            "peer_matching_safety": [
                "Identity verification required",
                "Background check for mentors",
                "Gradual disclosure encouraged",
                "Easy blocking and reporting",
                "Professional oversight available"
            ],
            "group_session_safety": [
                "Trained moderator present",
                "Clear community guidelines",
                "Zero tolerance for harassment",
                "Crisis intervention protocols",
                "Professional backup available"
            ],
            "content_moderation": [
                "AI-powered content screening",
                "Human moderator review",
                "Community reporting system",
                "Escalation procedures",
                "Support for affected users"
            ],
            "crisis_protocols": [
                "Immediate professional intervention",
                "Emergency contact notification",
                "Crisis resource provision",
                "Follow-up care coordination",
                "Safety plan activation"
            ]
        }

    def find_peer_matches(self, user_id: int, connection_type: ConnectionType,
                         user_preferences: Dict[str, Any] = None) -> List[PeerMatch]:
        """Find compatible peer matches for a user"""

        # Get user profile (in production, fetch from database)
        user_profile = self._get_user_profile(user_id)

        # Get potential matches (in production, query database)
        potential_matches = self._get_potential_matches(user_id, connection_type)

        matches = []
        algorithm = self.matching_algorithms.get(connection_type.value, self.matching_algorithms["support_buddy"])

        for candidate in potential_matches:
            compatibility_score = self._calculate_compatibility(
                user_profile,
                candidate,
                algorithm["weight_factors"]
            )

            if compatibility_score >= algorithm["minimum_compatibility"]:
                shared_attributes = self._find_shared_attributes(user_profile, candidate)
                recommended_activities = self._get_recommended_activities(
                    user_profile, candidate, connection_type
                )

                match = PeerMatch(
                    user1_id=user_id,
                    user2_id=candidate["user_id"],
                    connection_type=connection_type,
                    compatibility_score=compatibility_score,
                    shared_attributes=shared_attributes,
                    recommended_activities=recommended_activities,
                    match_reasoning=self._generate_match_reasoning(
                        user_profile, candidate, compatibility_score
                    ),
                    safety_level=self._assess_safety_level(user_profile, candidate)
                )
                matches.append(match)

        # Sort by compatibility score
        matches.sort(key=lambda x: x.compatibility_score, reverse=True)

        return matches[:10]  # Return top 10 matches

    def create_group_session(self, session_type: GroupSessionType,
                           moderator_id: int,
                           scheduled_time: datetime,
                           custom_config: Dict[str, Any] = None) -> GroupSession:
        """Create a new group therapy session"""

        session_id = str(uuid.uuid4())
        template = self.group_templates.get(session_type.value, self.group_templates["anxiety_support"])

        # Apply custom configuration if provided
        if custom_config:
            template.update(custom_config)

        # Generate meeting link (in production, integrate with video platform)
        meeting_link = f"https://mindmend.meet/{session_id}"

        session = GroupSession(
            session_id=session_id,
            session_type=session_type,
            title=template["title"],
            description=template["description"],
            moderator_id=moderator_id,
            max_participants=template["max_participants"],
            current_participants=[],
            scheduled_time=scheduled_time,
            duration_minutes=template["duration_minutes"],
            meeting_link=meeting_link,
            preparation_materials=template["preparation_materials"],
            session_guidelines=template["guidelines"]
        )

        # Store in database (in production)
        self._save_group_session(session)

        return session

    def join_group_session(self, session_id: str, user_id: int) -> Dict[str, Any]:
        """Allow user to join a group session"""

        session = self._get_group_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        # Check capacity
        if len(session.current_participants) >= session.max_participants:
            return {"success": False, "error": "Session is full"}

        # Check if user already joined
        if user_id in session.current_participants:
            return {"success": False, "error": "Already joined this session"}

        # Verify user eligibility
        if not self._verify_session_eligibility(user_id, session):
            return {"success": False, "error": "Not eligible for this session"}

        # Add user to session
        session.current_participants.append(user_id)
        self._update_group_session(session)

        # Send session details to user
        return {
            "success": True,
            "session_details": {
                "meeting_link": session.meeting_link,
                "scheduled_time": session.scheduled_time.isoformat(),
                "preparation_materials": session.preparation_materials,
                "guidelines": session.session_guidelines
            }
        }

    def create_community_challenge(self, challenge_type: str,
                                 start_date: datetime,
                                 custom_config: Dict[str, Any] = None) -> CommunityChallenge:
        """Create a new community wellness challenge"""

        challenge_id = str(uuid.uuid4())
        template = self.challenge_library.get(challenge_type, self.challenge_library["mindful_march"])

        # Apply custom configuration
        if custom_config:
            template.update(custom_config)

        challenge = CommunityChallenge(
            challenge_id=challenge_id,
            title=template["title"],
            description=template["description"],
            challenge_type=template["type"],
            duration_days=template["duration_days"],
            participants=[],
            daily_activities=template["daily_activities"],
            rewards_system=template["rewards"],
            progress_tracking={
                "start_date": start_date.isoformat(),
                "completion_rates": {},
                "leaderboard": [],
                "community_milestones": []
            }
        )

        # Store in database (in production)
        self._save_community_challenge(challenge)

        return challenge

    def assess_relationship_health(self, user1_id: int, user2_id: int,
                                 relationship_type: str = "romantic") -> Dict[str, Any]:
        """Assess relationship health and provide recommendations"""

        # Get relationship data (surveys, communication patterns, etc.)
        relationship_data = self._get_relationship_data(user1_id, user2_id)

        assessment = {
            "relationship_id": f"{user1_id}_{user2_id}",
            "relationship_type": relationship_type,
            "assessment_date": datetime.utcnow().isoformat(),
            "overall_health_score": 0,
            "dimension_scores": {},
            "strengths": [],
            "areas_for_improvement": [],
            "recommended_activities": [],
            "warning_signs": []
        }

        # Assess different dimensions
        dimensions = {
            "communication": self._assess_communication(relationship_data),
            "trust": self._assess_trust(relationship_data),
            "intimacy": self._assess_intimacy(relationship_data),
            "conflict_resolution": self._assess_conflict_resolution(relationship_data),
            "shared_values": self._assess_shared_values(relationship_data),
            "individual_growth": self._assess_individual_growth(relationship_data)
        }

        total_score = 0
        for dimension, score in dimensions.items():
            assessment["dimension_scores"][dimension] = score
            total_score += score

            if score >= 8:
                assessment["strengths"].append(f"Excellent {dimension.replace('_', ' ')}")
            elif score <= 5:
                assessment["areas_for_improvement"].append(f"Needs attention: {dimension.replace('_', ' ')}")
            elif score <= 3:
                assessment["warning_signs"].append(f"Concerning: {dimension.replace('_', ' ')}")

        assessment["overall_health_score"] = total_score / len(dimensions)

        # Generate recommendations
        assessment["recommended_activities"] = self._generate_relationship_activities(
            assessment["dimension_scores"], relationship_type
        )

        return assessment

    def moderate_content(self, content: str, user_id: int, context: str) -> Dict[str, Any]:
        """Moderate user-generated content for safety"""

        moderation_result = {
            "content_id": hashlib.md5(content.encode()).hexdigest(),
            "user_id": user_id,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
            "approved": True,
            "flags": [],
            "severity": "none",
            "action_required": "none"
        }

        # Check for harmful content patterns
        harmful_patterns = [
            r"\b(?:suicide|kill myself|end it all)\b",
            r"\b(?:self harm|cut myself|hurt myself)\b",
            r"\b(?:hate|worthless|deserve to die)\b",
            r"\b(?:abusive|violent|threatening)\b"
        ]

        import re
        for pattern in harmful_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                moderation_result["flags"].append("potential_self_harm")
                moderation_result["severity"] = "high"
                moderation_result["approved"] = False
                moderation_result["action_required"] = "immediate_intervention"
                break

        # Check for inappropriate sharing
        if any(word in content.lower() for word in ["personal info", "phone number", "address"]):
            moderation_result["flags"].append("personal_information")
            moderation_result["severity"] = "medium"

        # Check for spam or promotional content
        if content.count("http") > 2 or any(word in content.lower() for word in ["buy now", "click here", "discount"]):
            moderation_result["flags"].append("spam_promotional")
            moderation_result["severity"] = "low"

        # Add to moderation queue if flagged
        if moderation_result["flags"]:
            self.moderation_queue.append(moderation_result)

            # Trigger immediate intervention if high severity
            if moderation_result["severity"] == "high":
                self._trigger_crisis_intervention(user_id, content)

        return moderation_result

    def get_social_analytics(self, user_id: int, timeframe_days: int = 30) -> Dict[str, Any]:
        """Generate social connection analytics for a user"""

        analytics = {
            "user_id": user_id,
            "timeframe_days": timeframe_days,
            "analysis_date": datetime.utcnow().isoformat(),
            "connection_metrics": {},
            "engagement_patterns": {},
            "wellbeing_correlation": {},
            "recommendations": []
        }

        # Mock data - in production, fetch from database
        analytics["connection_metrics"] = {
            "active_connections": 5,
            "new_connections_made": 2,
            "group_sessions_attended": 8,
            "community_challenges_joined": 1,
            "support_given_count": 15,
            "support_received_count": 12
        }

        analytics["engagement_patterns"] = {
            "most_active_days": ["Tuesday", "Thursday", "Sunday"],
            "preferred_connection_type": "group_therapy",
            "average_session_duration_minutes": 45,
            "response_rate_to_messages": 0.85
        }

        analytics["wellbeing_correlation"] = {
            "mood_improvement_with_social_activity": 0.73,
            "anxiety_reduction_after_group_sessions": 0.68,
            "loneliness_score_trend": "improving",
            "social_confidence_growth": 0.45
        }

        # Generate personalized recommendations
        if analytics["connection_metrics"]["active_connections"] < 3:
            analytics["recommendations"].append("Consider joining more peer support connections")

        if analytics["engagement_patterns"]["response_rate_to_messages"] < 0.5:
            analytics["recommendations"].append("Try to engage more actively in conversations")

        if analytics["wellbeing_correlation"]["mood_improvement_with_social_activity"] > 0.6:
            analytics["recommendations"].append("Continue prioritizing social activities - they're helping your mood!")

        return analytics

    # Helper methods (simplified for demonstration)

    def _get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user profile for matching"""
        # Mock profile - in production, fetch from database
        return {
            "user_id": user_id,
            "age": 28,
            "conditions": ["anxiety", "depression"],
            "therapy_stage": "active_treatment",
            "interests": ["yoga", "reading", "hiking"],
            "location": {"city": "Sydney", "state": "NSW"},
            "availability": ["weekday_evenings", "weekend_mornings"],
            "communication_style": "supportive",
            "experience_level": "intermediate"
        }

    def _get_potential_matches(self, user_id: int, connection_type: ConnectionType) -> List[Dict[str, Any]]:
        """Get potential peer matches"""
        # Mock data - in production, query database with filters
        return [
            {
                "user_id": 2,
                "age": 26,
                "conditions": ["anxiety", "stress"],
                "therapy_stage": "active_treatment",
                "interests": ["yoga", "meditation", "art"],
                "location": {"city": "Sydney", "state": "NSW"},
                "availability": ["weekday_evenings", "weekend_afternoons"],
                "communication_style": "encouraging",
                "experience_level": "beginner"
            },
            {
                "user_id": 3,
                "age": 32,
                "conditions": ["depression", "anxiety"],
                "therapy_stage": "maintenance",
                "interests": ["hiking", "cooking", "reading"],
                "location": {"city": "Melbourne", "state": "VIC"},
                "availability": ["weekend_mornings", "weekday_lunch"],
                "communication_style": "practical",
                "experience_level": "advanced"
            }
        ]

    def _calculate_compatibility(self, user1: Dict[str, Any], user2: Dict[str, Any],
                               weights: Dict[str, float]) -> float:
        """Calculate compatibility score between two users"""
        total_score = 0

        # Similar conditions
        if "similar_conditions" in weights:
            common_conditions = set(user1["conditions"]) & set(user2["conditions"])
            condition_score = len(common_conditions) / max(len(user1["conditions"]), 1)
            total_score += condition_score * weights["similar_conditions"]

        # Age similarity
        if "age_similarity" in weights:
            age_diff = abs(user1["age"] - user2["age"])
            age_score = max(0, 1 - age_diff / 20)  # Normalize age difference
            total_score += age_score * weights["age_similarity"]

        # Shared interests
        if "shared_interests" in weights:
            common_interests = set(user1["interests"]) & set(user2["interests"])
            interest_score = len(common_interests) / max(len(user1["interests"]), 1)
            total_score += interest_score * weights["shared_interests"]

        # Therapy stage compatibility
        if "therapy_stage" in weights:
            stage_compatibility = {
                ("beginning", "beginning"): 0.9,
                ("beginning", "active_treatment"): 0.7,
                ("active_treatment", "active_treatment"): 0.95,
                ("active_treatment", "maintenance"): 0.8,
                ("maintenance", "maintenance"): 0.85
            }
            stage_key = (user1["therapy_stage"], user2["therapy_stage"])
            stage_score = stage_compatibility.get(stage_key, 0.5)
            total_score += stage_score * weights["therapy_stage"]

        return min(total_score, 1.0)  # Cap at 1.0

    def _find_shared_attributes(self, user1: Dict[str, Any], user2: Dict[str, Any]) -> List[str]:
        """Find shared attributes between users"""
        shared = []

        # Shared conditions
        common_conditions = set(user1["conditions"]) & set(user2["conditions"])
        for condition in common_conditions:
            shared.append(f"Both managing {condition}")

        # Shared interests
        common_interests = set(user1["interests"]) & set(user2["interests"])
        for interest in common_interests:
            shared.append(f"Both enjoy {interest}")

        # Similar age
        age_diff = abs(user1["age"] - user2["age"])
        if age_diff <= 5:
            shared.append("Similar age")

        return shared

    def _get_recommended_activities(self, user1: Dict[str, Any], user2: Dict[str, Any],
                                  connection_type: ConnectionType) -> List[str]:
        """Get recommended activities for matched users"""
        activities = []

        common_interests = set(user1["interests"]) & set(user2["interests"])

        if connection_type == ConnectionType.SUPPORT_BUDDY:
            activities = [
                "Weekly check-in calls",
                "Share coping strategies",
                "Virtual coffee sessions",
                "Goal accountability partnership"
            ]

            # Add interest-based activities
            if "yoga" in common_interests:
                activities.append("Virtual yoga sessions together")
            if "reading" in common_interests:
                activities.append("Mental health book club")

        elif connection_type == ConnectionType.GROUP_THERAPY:
            activities = [
                "Join anxiety support group",
                "Participate in group mindfulness sessions",
                "Share in discussion forums"
            ]

        return activities

    def _generate_match_reasoning(self, user1: Dict[str, Any], user2: Dict[str, Any],
                                score: float) -> str:
        """Generate explanation for why users were matched"""
        reasons = []

        common_conditions = set(user1["conditions"]) & set(user2["conditions"])
        if common_conditions:
            reasons.append(f"Both are managing {', '.join(common_conditions)}")

        common_interests = set(user1["interests"]) & set(user2["interests"])
        if common_interests:
            reasons.append(f"Share interests in {', '.join(list(common_interests)[:2])}")

        if user1["therapy_stage"] == user2["therapy_stage"]:
            reasons.append(f"Both in {user1['therapy_stage']} stage")

        if score > 0.8:
            return f"Excellent match! {' and '.join(reasons)}."
        elif score > 0.6:
            return f"Good compatibility: {' and '.join(reasons)}."
        else:
            return f"Potential connection: {' and '.join(reasons)}."

    def _assess_safety_level(self, user1: Dict[str, Any], user2: Dict[str, Any]) -> str:
        """Assess safety level for peer connection"""
        # Simplified safety assessment
        safety_factors = 0

        # Check verification status
        if user1.get("verified", False) and user2.get("verified", False):
            safety_factors += 1

        # Check experience level
        if user1.get("experience_level") in ["intermediate", "advanced"] or \
           user2.get("experience_level") in ["intermediate", "advanced"]:
            safety_factors += 1

        # Check for red flags (simplified)
        if not user1.get("red_flags", []) and not user2.get("red_flags", []):
            safety_factors += 1

        if safety_factors >= 2:
            return "high"
        elif safety_factors >= 1:
            return "medium"
        else:
            return "supervised_only"

    # Additional helper methods (simplified implementations)

    def _save_group_session(self, session: GroupSession):
        """Save group session to database"""
        pass  # Implementation would save to database

    def _get_group_session(self, session_id: str) -> Optional[GroupSession]:
        """Get group session from database"""
        pass  # Implementation would fetch from database

    def _update_group_session(self, session: GroupSession):
        """Update group session in database"""
        pass  # Implementation would update database

    def _verify_session_eligibility(self, user_id: int, session: GroupSession) -> bool:
        """Verify if user is eligible for the session"""
        return True  # Simplified - would check actual eligibility criteria

    def _save_community_challenge(self, challenge: CommunityChallenge):
        """Save community challenge to database"""
        pass  # Implementation would save to database

    def _get_relationship_data(self, user1_id: int, user2_id: int) -> Dict[str, Any]:
        """Get relationship assessment data"""
        # Mock data for demonstration
        return {
            "communication_frequency": 8.5,
            "conflict_frequency": 2.0,
            "shared_activities": 6.5,
            "trust_indicators": 8.0,
            "intimacy_rating": 7.5,
            "individual_satisfaction": [7.0, 8.0]
        }

    def _assess_communication(self, data: Dict[str, Any]) -> float:
        """Assess communication dimension"""
        return min(data.get("communication_frequency", 5) +
                  (10 - data.get("conflict_frequency", 5)), 10)

    def _assess_trust(self, data: Dict[str, Any]) -> float:
        """Assess trust dimension"""
        return data.get("trust_indicators", 5)

    def _assess_intimacy(self, data: Dict[str, Any]) -> float:
        """Assess intimacy dimension"""
        return data.get("intimacy_rating", 5)

    def _assess_conflict_resolution(self, data: Dict[str, Any]) -> float:
        """Assess conflict resolution skills"""
        return max(0, 10 - data.get("conflict_frequency", 5) * 2)

    def _assess_shared_values(self, data: Dict[str, Any]) -> float:
        """Assess shared values alignment"""
        return data.get("shared_activities", 5) * 1.2  # Simplified

    def _assess_individual_growth(self, data: Dict[str, Any]) -> float:
        """Assess individual growth within relationship"""
        satisfaction_scores = data.get("individual_satisfaction", [5, 5])
        return sum(satisfaction_scores) / len(satisfaction_scores)

    def _generate_relationship_activities(self, scores: Dict[str, float],
                                        relationship_type: str) -> List[str]:
        """Generate relationship improvement activities"""
        activities = []

        if scores.get("communication", 5) < 6:
            activities.append("Daily 15-minute check-in conversations")
            activities.append("Practice active listening exercises")

        if scores.get("trust", 5) < 6:
            activities.append("Trust-building transparency exercises")
            activities.append("Share daily appreciations")

        if scores.get("intimacy", 5) < 6:
            activities.append("Plan regular date nights")
            activities.append("Physical affection increase goals")

        if scores.get("conflict_resolution", 5) < 6:
            activities.append("Learn healthy conflict resolution techniques")
            activities.append("Practice 'time-out' during heated discussions")

        # Add general relationship strengthening activities
        activities.extend([
            "Weekly relationship check-in meetings",
            "Couples gratitude journal",
            "Shared mindfulness or meditation practice",
            "New experience challenges together"
        ])

        return activities[:5]  # Return top 5 recommendations

    def _trigger_crisis_intervention(self, user_id: int, content: str):
        """Trigger crisis intervention protocols"""
        logger.critical(f"Crisis intervention triggered for user {user_id}")

        # In production, this would:
        # 1. Alert crisis intervention team
        # 2. Send immediate resources to user
        # 3. Notify emergency contacts if consented
        # 4. Connect with crisis hotlines
        # 5. Schedule immediate professional follow-up

    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get platform-wide social connection statistics"""
        return {
            "total_peer_matches": 1250,
            "active_group_sessions": 45,
            "total_group_participants": 360,
            "active_challenges": 12,
            "challenge_participants": 890,
            "matches_this_week": 85,
            "pending_moderation": 3,
            "community_engagement_rate": 0.78,
            "average_match_satisfaction": 4.2,
            "crisis_interventions_prevented": 23
        }

# Create singleton instance
social_connection_manager = SocialConnectionManager()