"""
Therapy AI Guardrails System
===========================
Safety and ethical guardrails for MindMend therapy AI responses
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
from datetime import datetime

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InterventionType(Enum):
    NONE = "none"
    WARNING = "warning"
    REDIRECT = "redirect"
    ESCALATE = "escalate"
    BLOCK = "block"

@dataclass
class GuardrailResult:
    risk_level: RiskLevel
    intervention: InterventionType
    reason: str
    modified_response: Optional[str] = None
    escalation_data: Optional[Dict] = None

class TherapyGuardrails:
    def __init__(self):
        self.crisis_keywords = [
            # Suicide indicators
            "suicide", "kill myself", "end it all", "want to die", "better off dead",
            "no point living", "take my own life", "hurt myself", "self harm",
            "cut myself", "overdose", "jump off", "not worth living",
            
            # Violence indicators  
            "hurt someone", "kill someone", "violence", "weapon", "gun",
            "knife", "bomb", "attack", "murder",
            
            # Severe mental health crises
            "losing my mind", "can't take it anymore", "everything is hopeless",
            "no way out", "trapped", "worthless", "burden to everyone"
        ]
        
        self.inappropriate_content_patterns = [
            r"\b(sexual|erotic|intimate)\b.*\b(relationship|encounter|contact)\b",
            r"\b(drug|drugs|substance)\b.*\b(use|abuse|addiction)\b.*\b(how to|where to|obtain)\b",
            r"\b(illegal|unlawful|criminal)\b.*\b(activity|behavior|action)\b",
            r"\bpersonal.*\b(information|details|data)\b.*\b(therapist|counselor)\b"
        ]
        
        self.therapy_boundary_violations = [
            "personal relationship", "outside of therapy", "meet in person",
            "my personal life", "date me", "romantic", "physical contact",
            "home address", "phone number", "social media", "friend request"
        ]
        
        self.professional_responses = {
            "crisis": [
                "I'm very concerned about what you're sharing. Your safety is the most important thing right now.",
                "These feelings are serious and you deserve immediate support. Please contact emergency services or a crisis helpline.",
                "I want you to know that you're not alone, and there are people who can help you through this crisis."
            ],
            "boundary": [
                "I understand you may want to connect, but as an AI therapy assistant, I need to maintain professional boundaries.",
                "My role is to provide therapeutic support within this platform. I'm not able to form personal relationships outside of our sessions.",
                "Let's focus on how I can best support your mental health goals within our therapeutic relationship."
            ],
            "inappropriate": [
                "I notice this conversation is moving away from therapeutic topics. Let's refocus on your mental health and wellbeing.",
                "I'm designed to provide mental health support. I'd like to redirect our conversation to how I can help with your therapeutic goals.",
                "This seems outside my scope as a therapy AI. How can I help you with your mental health and wellness today?"
            ]
        }
        
        self.emergency_resources = {
            "AU": {
                "lifeline": {"name": "Lifeline Australia", "number": "13 11 14", "available": "24/7"},
                "crisis": {"name": "Crisis Support Chat", "url": "https://www.lifeline.org.au/crisis-chat/", "available": "24/7"},
                "emergency": {"name": "Emergency Services", "number": "000", "available": "24/7"},
                "mental_health": {"name": "Mental Health Emergency Response Line", "number": "1300 555 788", "available": "24/7"}
            }
        }
    
    def analyze_user_input(self, user_input: str, session_context: Dict = None) -> GuardrailResult:
        """Analyze user input for safety concerns"""
        user_input_lower = user_input.lower().strip()
        
        # Check for crisis indicators
        crisis_result = self._check_crisis_indicators(user_input_lower)
        if crisis_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return crisis_result
        
        # Check for inappropriate content
        inappropriate_result = self._check_inappropriate_content(user_input_lower)
        if inappropriate_result.risk_level == RiskLevel.HIGH:
            return inappropriate_result
        
        # Check for boundary violations
        boundary_result = self._check_boundary_violations(user_input_lower)
        if boundary_result.risk_level == RiskLevel.MEDIUM:
            return boundary_result
        
        # No significant risks detected
        return GuardrailResult(
            risk_level=RiskLevel.LOW,
            intervention=InterventionType.NONE,
            reason="No safety concerns detected"
        )
    
    def analyze_ai_response(self, ai_response: str, user_context: Dict = None) -> GuardrailResult:
        """Analyze AI response for safety and appropriateness"""
        response_lower = ai_response.lower().strip()
        
        # Check for harmful advice
        harmful_advice = self._check_harmful_advice(response_lower)
        if harmful_advice.risk_level == RiskLevel.HIGH:
            return harmful_advice
        
        # Check for unprofessional content
        unprofessional = self._check_professional_boundaries(response_lower)
        if unprofessional.risk_level == RiskLevel.MEDIUM:
            return unprofessional
        
        # Check response length and coherence
        coherence_check = self._check_response_coherence(ai_response)
        if coherence_check.risk_level == RiskLevel.MEDIUM:
            return coherence_check
        
        # Response appears safe
        return GuardrailResult(
            risk_level=RiskLevel.LOW,
            intervention=InterventionType.NONE,
            reason="Response passed all safety checks"
        )
    
    def _check_crisis_indicators(self, text: str) -> GuardrailResult:
        """Check for crisis/suicide indicators"""
        crisis_score = 0
        detected_keywords = []
        
        for keyword in self.crisis_keywords:
            if keyword in text:
                crisis_score += 1
                detected_keywords.append(keyword)
        
        # High-risk patterns
        high_risk_patterns = [
            r"(want to|going to|plan to).*(die|kill|hurt|end)",
            r"(no point|no reason|nothing).*(living|life|exist)",
            r"(everyone|world).*(better without|better off without)",
            r"(have a plan|planning to|ready to).*(die|suicide|kill)"
        ]
        
        for pattern in high_risk_patterns:
            if re.search(pattern, text):
                crisis_score += 3
                detected_keywords.append(f"pattern: {pattern}")
        
        if crisis_score >= 3 or any(re.search(p, text) for p in high_risk_patterns):
            return GuardrailResult(
                risk_level=RiskLevel.CRITICAL,
                intervention=InterventionType.ESCALATE,
                reason=f"Critical suicide/crisis indicators detected: {', '.join(detected_keywords[:3])}",
                escalation_data={
                    "crisis_type": "suicide_risk",
                    "keywords": detected_keywords,
                    "timestamp": datetime.utcnow().isoformat(),
                    "emergency_resources": self.emergency_resources["AU"]
                }
            )
        elif crisis_score >= 1:
            return GuardrailResult(
                risk_level=RiskLevel.HIGH,
                intervention=InterventionType.REDIRECT,
                reason=f"Potential crisis indicators: {', '.join(detected_keywords)}",
                modified_response=self._generate_crisis_response()
            )
        
        return GuardrailResult(
            risk_level=RiskLevel.LOW,
            intervention=InterventionType.NONE,
            reason="No crisis indicators detected"
        )
    
    def _check_inappropriate_content(self, text: str) -> GuardrailResult:
        """Check for inappropriate content requests"""
        for pattern in self.inappropriate_content_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return GuardrailResult(
                    risk_level=RiskLevel.HIGH,
                    intervention=InterventionType.REDIRECT,
                    reason=f"Inappropriate content pattern detected: {pattern}",
                    modified_response=self._get_professional_response("inappropriate")
                )
        
        return GuardrailResult(
            risk_level=RiskLevel.LOW,
            intervention=InterventionType.NONE,
            reason="No inappropriate content detected"
        )
    
    def _check_boundary_violations(self, text: str) -> GuardrailResult:
        """Check for therapy boundary violations"""
        for boundary_violation in self.therapy_boundary_violations:
            if boundary_violation in text:
                return GuardrailResult(
                    risk_level=RiskLevel.MEDIUM,
                    intervention=InterventionType.REDIRECT,
                    reason=f"Boundary violation detected: {boundary_violation}",
                    modified_response=self._get_professional_response("boundary")
                )
        
        return GuardrailResult(
            risk_level=RiskLevel.LOW,
            intervention=InterventionType.NONE,
            reason="No boundary violations detected"
        )
    
    def _check_harmful_advice(self, response: str) -> GuardrailResult:
        """Check AI response for potentially harmful advice"""
        harmful_patterns = [
            r"you should.*\b(drug|substance|alcohol)\b.*\bto\b.*\b(cope|feel better|relax)\b",
            r"(ignore|avoid).*\b(doctor|medication|treatment|therapy)\b",
            r"(self.*medicate|self.*treat).*\b(depression|anxiety|trauma)\b",
            r"(it's normal to|everyone).*(harm|hurt).*\b(themselves|others)\b"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return GuardrailResult(
                    risk_level=RiskLevel.HIGH,
                    intervention=InterventionType.BLOCK,
                    reason=f"Potentially harmful advice detected: {pattern}",
                    modified_response="I want to make sure I'm providing safe and appropriate support. Let me rephrase that in a way that prioritizes your wellbeing and safety."
                )
        
        return GuardrailResult(
            risk_level=RiskLevel.LOW,
            intervention=InterventionType.NONE,
            reason="No harmful advice detected"
        )
    
    def _check_professional_boundaries(self, response: str) -> GuardrailResult:
        """Check for professional boundary issues in AI response"""
        boundary_issues = [
            "i personally", "my own experience", "when i was", "my life",
            "we should meet", "personal relationship", "outside of therapy"
        ]
        
        for issue in boundary_issues:
            if issue in response:
                return GuardrailResult(
                    risk_level=RiskLevel.MEDIUM,
                    intervention=InterventionType.REDIRECT,
                    reason=f"Professional boundary issue: {issue}",
                    modified_response="As an AI therapy assistant, I'm here to focus on your experiences and support your mental health goals. Let me provide guidance based on therapeutic best practices."
                )
        
        return GuardrailResult(
            risk_level=RiskLevel.LOW,
            intervention=InterventionType.NONE,
            reason="Professional boundaries maintained"
        )
    
    def _check_response_coherence(self, response: str) -> GuardrailResult:
        """Check response length and coherence"""
        if len(response) > 3000:
            return GuardrailResult(
                risk_level=RiskLevel.MEDIUM,
                intervention=InterventionType.REDIRECT,
                reason="Response too long",
                modified_response="Let me provide a more focused response to better support you."
            )
        
        if len(response.strip()) < 10:
            return GuardrailResult(
                risk_level=RiskLevel.MEDIUM,
                intervention=InterventionType.REDIRECT,
                reason="Response too short",
                modified_response="I want to make sure I'm providing helpful support. Could you tell me more about what you're experiencing so I can better assist you?"
            )
        
        return GuardrailResult(
            risk_level=RiskLevel.LOW,
            intervention=InterventionType.NONE,
            reason="Response length and coherence acceptable"
        )
    
    def _generate_crisis_response(self) -> str:
        """Generate appropriate crisis intervention response"""
        crisis_response = (
            "I'm very concerned about what you're sharing, and I want you to know that your safety is the most important thing right now. "
            "You deserve immediate support from qualified professionals who can help you through this.\n\n"
            "Please reach out to:\n"
            "• Lifeline Australia: 13 11 14 (24/7)\n"
            "• Emergency Services: 000\n"
            "• Crisis Support Chat: https://www.lifeline.org.au/crisis-chat/\n\n"
            "You're not alone in this, and there are people who want to help you through this difficult time. "
            "Would you like to talk about getting connected with professional support?"
        )
        return crisis_response
    
    def _get_professional_response(self, response_type: str) -> str:
        """Get professional response for different situations"""
        responses = self.professional_responses.get(response_type, [])
        return responses[0] if responses else "I'm here to provide therapeutic support. How can I help you with your mental health and wellbeing today?"
    
    def log_guardrail_action(self, result: GuardrailResult, user_input: str = None, ai_response: str = None):
        """Log guardrail actions for monitoring and improvement"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "risk_level": result.risk_level.value,
            "intervention": result.intervention.value,
            "reason": result.reason,
            "user_input_length": len(user_input) if user_input else 0,
            "ai_response_length": len(ai_response) if ai_response else 0,
            "escalation_triggered": result.escalation_data is not None
        }
        
        if result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            logger.warning(f"High-risk guardrail trigger: {log_data}")
        else:
            logger.info(f"Guardrail check: {log_data}")

# Global guardrails instance
therapy_guardrails = TherapyGuardrails()