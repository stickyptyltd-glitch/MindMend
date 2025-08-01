import re
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# TODO: Level 3+ Integration Points
# These comments show where advanced AI modules will be integrated:
# 
# 1. MICROEXPRESSION ANALYSIS INTEGRATION:
#    - Import from models.future_ai_modules import MicroexpressionAnalyzer
#    - Add microexpression_analyzer = MicroexpressionAnalyzer() to __init__
#    - Integrate facial analysis results with text-based crisis detection
#    - Cross-reference spoken words with facial micro-expressions for incongruence
#    - Use micro-expression stress indicators to enhance crisis prediction
#
# 2. BIOSENSOR DATA INTEGRATION:
#    - Import from models.future_ai_modules import BioSensorIntegration  
#    - Add biosensor_integration = BioSensorIntegration() to __init__
#    - Correlate heart rate variability with crisis indicators
#    - Use stress patterns from wearables to predict mental health episodes
#    - Integrate sleep quality and activity data for comprehensive health assessment
#
# 3. MULTI-MODAL CRISIS DETECTION:
#    - Combine text analysis + microexpressions + biosensor data
#    - Create weighted scoring system for crisis probability
#    - Implement real-time alert system for immediate intervention
#    - Generate personalized intervention strategies based on all data sources

class HealthChecker:
    def __init__(self):
        self.risk_keywords = {
            "crisis": {
                "keywords": [
                    "kill myself", "suicide", "end it all", "don't want to live",
                    "better off dead", "take my own life", "hurt myself badly",
                    "can't go on", "no point in living", "want to die",
                    "end my life", "kill me", "wish I was dead"
                ],
                "weight": 10,
                "action": "immediate_intervention"
            },
            "self_harm": {
                "keywords": [
                    "cut myself", "hurt myself", "self harm", "self-harm",
                    "burn myself", "scratch myself", "punish myself",
                    "deserve pain", "cutting", "razor", "blade",
                    "mutilate", "damage myself"
                ],
                "weight": 8,
                "action": "safety_planning"
            },
            "violence": {
                "keywords": [
                    "hurt someone", "kill someone", "attack", "murder",
                    "violence", "harm others", "revenge", "get back at",
                    "make them pay", "destroy them", "violent thoughts"
                ],
                "weight": 9,
                "action": "threat_assessment"
            },
            "severe_distress": {
                "keywords": [
                    "can't take it", "overwhelming", "falling apart",
                    "losing control", "breaking down", "desperate",
                    "hopeless", "worthless", "burden", "exhausted",
                    "unbearable", "can't cope", "giving up"
                ],
                "weight": 6,
                "action": "enhanced_support"
            },
            "substance_abuse": {
                "keywords": [
                    "drinking too much", "can't stop drinking", "need drugs",
                    "overdose", "getting high", "numbing the pain",
                    "addiction", "substance", "pills", "alcohol problem",
                    "drug problem", "abusing", "dependent"
                ],
                "weight": 7,
                "action": "addiction_resources"
            },
            "eating_disorder": {
                "keywords": [
                    "starving myself", "binge eating", "purging", "vomit",
                    "too fat", "hate my body", "restrict food",
                    "not eating", "weight obsession", "body dysmorphia",
                    "bulimia", "anorexia", "food control"
                ],
                "weight": 6,
                "action": "eating_disorder_support"
            },
            "psychosis": {
                "keywords": [
                    "hearing voices", "seeing things", "not real",
                    "hallucinations", "paranoid", "they're watching",
                    "conspiracy", "delusions", "losing my mind",
                    "voices telling me", "people following"
                ],
                "weight": 8,
                "action": "psychiatric_evaluation"
            },
            "trauma": {
                "keywords": [
                    "flashbacks", "nightmares", "reliving", "triggered",
                    "traumatic", "abuse", "assault", "violated",
                    "ptsd", "trauma response", "dissociating"
                ],
                "weight": 7,
                "action": "trauma_support"
            }
        }
        
        self.intensity_modifiers = {
            "extreme": ["very", "extremely", "really", "so", "completely", "totally", "absolutely"],
            "frequency": ["always", "constantly", "every day", "all the time", "never stops"],
            "immediacy": ["right now", "today", "tonight", "immediately", "this moment"]
        }
        
        self.protective_factors = [
            "support", "family", "friends", "therapy", "treatment",
            "help", "better", "hope", "future", "goals"
        ]
    
    def scan_text(self, text):
        """Scan text for mental health risk indicators"""
        if not text:
            return []
        
        text_lower = text.lower()
        alerts = []
        risk_score = 0
        
        # Check for protective factors
        protective_count = sum(1 for factor in self.protective_factors if factor in text_lower)
        
        for category, risk_data in self.risk_keywords.items():
            keywords = risk_data["keywords"]
            weight = risk_data["weight"]
            action = risk_data["action"]
            
            matched_keywords = []
            for keyword in keywords:
                if keyword in text_lower:
                    matched_keywords.append(keyword)
                    base_score = weight
                    
                    # Check for intensity modifiers
                    intensity_multiplier = self._check_intensity(text_lower, keyword)
                    adjusted_score = base_score + (base_score * intensity_multiplier)
                    
                    # Reduce score if protective factors present
                    if protective_count > 0:
                        adjusted_score *= (1 - (protective_count * 0.1))
                    
                    risk_score += adjusted_score
            
            if matched_keywords:
                alert = {
                    "category": category,
                    "severity": self._get_severity(weight),
                    "matched_keywords": matched_keywords,
                    "action": action,
                    "message": self._get_alert_message(category),
                    "resources": self._get_resources(category),
                    "immediate_steps": self._get_immediate_steps(category)
                }
                alerts.append(alert)
        
        # Sort alerts by severity (highest risk first)
        alerts.sort(key=lambda x: self.risk_keywords[x["category"]]["weight"], reverse=True)
        
        # Add overall risk assessment
        if alerts:
            overall_risk = self._calculate_overall_risk(risk_score)
            alerts.insert(0, {
                "category": "overall_assessment",
                "severity": overall_risk,
                "risk_score": round(risk_score, 1),
                "message": f"Overall risk level: {overall_risk}",
                "requires_intervention": risk_score >= 15,
                "protective_factors": protective_count,
                "recommendations": self._get_overall_recommendations(overall_risk, protective_count)
            })
        
        return alerts
    
    def _check_intensity(self, text, keyword):
        """Check for intensity modifiers around keywords"""
        # Find the position of the keyword
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return 0
        
        # Check words before and after the keyword
        words_before = text[:keyword_pos].split()[-3:]  # Last 3 words before
        words_after = text[keyword_pos + len(keyword):].split()[:3]  # First 3 words after
        
        context_words = words_before + words_after
        
        multiplier = 0
        for word in context_words:
            word = word.strip('.,!?";')
            if word in self.intensity_modifiers["extreme"]:
                multiplier += 0.3
            elif word in self.intensity_modifiers["frequency"]:
                multiplier += 0.4
            elif word in self.intensity_modifiers["immediacy"]:
                multiplier += 0.5
        
        return min(multiplier, 1.0)  # Cap at 1.0
    
    def _get_severity(self, weight):
        """Convert weight to severity level"""
        if weight >= 9:
            return "critical"
        elif weight >= 7:
            return "high"
        elif weight >= 5:
            return "medium"
        else:
            return "low"
    
    def _calculate_overall_risk(self, risk_score):
        """Calculate overall risk level"""
        if risk_score >= 25:
            return "critical"
        elif risk_score >= 15:
            return "high"
        elif risk_score >= 10:
            return "medium"
        else:
            return "low"
    
    def _get_alert_message(self, category):
        """Get appropriate alert message for category"""
        messages = {
            "crisis": "⚠️ CRISIS ALERT: Immediate suicide risk detected. Intervention required.",
            "self_harm": "⚠️ Self-harm indicators detected. Safety planning recommended.",
            "violence": "⚠️ Violence indicators detected. Threat assessment needed.",
            "severe_distress": "⚠️ Severe emotional distress detected. Enhanced support recommended.",
            "substance_abuse": "⚠️ Substance abuse concerns detected. Addiction resources recommended.",
            "eating_disorder": "⚠️ Eating disorder indicators detected. Specialized support recommended.",
            "psychosis": "⚠️ Psychotic symptoms detected. Psychiatric evaluation recommended.",
            "trauma": "⚠️ Trauma-related content detected. Trauma-informed care recommended."
        }
        return messages.get(category, f"⚠️ {category.replace('_', ' ').title()} risk detected.")
    
    def _get_resources(self, category):
        """Get relevant resources for each category"""
        resources = {
            "crisis": [
                {"name": "National Suicide Prevention Lifeline", "contact": "988"},
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                {"name": "Emergency Services", "contact": "911"},
                {"name": "National Suicide Prevention Website", "contact": "suicidepreventionlifeline.org"}
            ],
            "self_harm": [
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                {"name": "Self-Injury Outreach & Support", "contact": "sioutreach.org"},
                {"name": "To Write Love on Her Arms", "contact": "twloha.com"},
                {"name": "National Suicide Prevention Lifeline", "contact": "988"}
            ],
            "violence": [
                {"name": "National Domestic Violence Hotline", "contact": "1-800-799-7233"},
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                {"name": "Emergency Services", "contact": "911"},
                {"name": "National Sexual Assault Hotline", "contact": "1-800-656-4673"}
            ],
            "severe_distress": [
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                {"name": "SAMHSA Helpline", "contact": "1-800-662-4357"},
                {"name": "Mental Health America", "contact": "mhanational.org"},
                {"name": "National Alliance on Mental Illness", "contact": "nami.org"}
            ],
            "substance_abuse": [
                {"name": "SAMHSA Helpline", "contact": "1-800-662-4357"},
                {"name": "Alcoholics Anonymous", "contact": "aa.org"},
                {"name": "Narcotics Anonymous", "contact": "na.org"},
                {"name": "Smart Recovery", "contact": "smartrecovery.org"}
            ],
            "eating_disorder": [
                {"name": "National Eating Disorders Association", "contact": "1-800-931-2237"},
                {"name": "NEDA Text Line", "contact": "Text NEDA to 741741"},
                {"name": "Eating Recovery Center", "contact": "eatingrecoverycenter.com"},
                {"name": "National Association of Anorexia Nervosa", "contact": "anad.org"}
            ],
            "psychosis": [
                {"name": "SAMHSA Helpline", "contact": "1-800-662-4357"},
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                {"name": "Emergency Services", "contact": "911"},
                {"name": "National Alliance on Mental Illness", "contact": "nami.org"}
            ],
            "trauma": [
                {"name": "National Sexual Assault Hotline", "contact": "1-800-656-4673"},
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741"},
                {"name": "PTSD National Center", "contact": "ptsd.va.gov"},
                {"name": "National Domestic Violence Hotline", "contact": "1-800-799-7233"}
            ]
        }
        return resources.get(category, [])
    
    def _get_immediate_steps(self, category):
        """Get immediate steps for each risk category"""
        steps = {
            "crisis": [
                "Call 988 (Suicide Prevention Lifeline) immediately",
                "Go to the nearest emergency room",
                "Call 911 if in immediate danger",
                "Remove means of self-harm from environment",
                "Stay with a trusted person"
            ],
            "self_harm": [
                "Remove sharp objects and harmful items",
                "Use ice cubes or rubber bands as safer alternatives",
                "Call a crisis hotline for support",
                "Reach out to a trusted friend or family member",
                "Practice grounding techniques"
            ],
            "violence": [
                "Call 911 if there is immediate danger",
                "Contact local law enforcement",
                "Reach out to a crisis counselor",
                "Create a safety plan",
                "Consider removing yourself from the situation"
            ],
            "severe_distress": [
                "Practice deep breathing exercises",
                "Use grounding techniques (5-4-3-2-1 method)",
                "Call a crisis helpline",
                "Reach out to your support network",
                "Consider professional mental health support"
            ]
        }
        return steps.get(category, [
            "Reach out to a mental health professional",
            "Contact a crisis helpline for support",
            "Talk to a trusted friend or family member",
            "Practice self-care and stress management"
        ])
    
    def _get_overall_recommendations(self, risk_level, protective_factors):
        """Get overall recommendations based on risk level"""
        recommendations = []
        
        if risk_level == "critical":
            recommendations = [
                "Seek immediate professional help",
                "Contact emergency services if in danger",
                "Implement crisis safety plan",
                "Ensure continuous supervision if possible"
            ]
        elif risk_level == "high":
            recommendations = [
                "Schedule urgent mental health appointment",
                "Implement safety planning strategies",
                "Increase support system contact",
                "Consider intensive outpatient programs"
            ]
        elif risk_level == "medium":
            recommendations = [
                "Schedule mental health consultation",
                "Increase therapy frequency",
                "Practice stress management techniques",
                "Monitor symptoms closely"
            ]
        else:
            recommendations = [
                "Continue current mental health support",
                "Practice preventive self-care",
                "Maintain regular check-ins",
                "Build resilience strategies"
            ]
        
        # Add protective factor reinforcement
        if protective_factors > 0:
            recommendations.append("Continue leveraging your existing support systems")
        else:
            recommendations.append("Work on building a stronger support network")
        
        return recommendations
    
    def generate_safety_plan(self, alerts, patient_data=None):
        """Generate a personalized safety plan based on alerts"""
        if not alerts:
            return None
        
        # Filter out the overall assessment
        risk_alerts = [alert for alert in alerts if alert.get("category") != "overall_assessment"]
        
        if not risk_alerts:
            return None
        
        highest_risk = max(risk_alerts, key=lambda x: self.risk_keywords.get(x["category"], {}).get("weight", 0))
        
        safety_plan = {
            "immediate_actions": highest_risk.get("immediate_steps", []),
            "warning_signs": self._identify_warning_signs(risk_alerts),
            "coping_strategies": self._get_coping_strategies(highest_risk["category"]),
            "support_contacts": self._get_support_contacts(),
            "professional_resources": highest_risk.get("resources", []),
            "environmental_safety": self._get_environmental_safety(highest_risk["category"]),
            "follow_up_plan": self._get_follow_up_plan(highest_risk["severity"])
        }
        
        return safety_plan
    
    def _identify_warning_signs(self, alerts):
        """Identify warning signs from alerts"""
        warning_signs = []
        for alert in alerts:
            category = alert["category"]
            if category == "crisis":
                warning_signs.extend([
                    "Thoughts of suicide or self-harm",
                    "Feeling hopeless or trapped",
                    "Talking about death or dying"
                ])
            elif category == "severe_distress":
                warning_signs.extend([
                    "Feeling overwhelmed or out of control",
                    "Unable to cope with daily activities",
                    "Extreme mood changes"
                ])
        
        return list(set(warning_signs))  # Remove duplicates
    
    def _get_coping_strategies(self, category):
        """Get coping strategies for specific risk categories"""
        strategies = {
            "crisis": [
                "Call a crisis hotline immediately",
                "Use the STOP technique (Stop, Take a breath, Observe, Proceed mindfully)",
                "Practice grounding exercises",
                "Reach out to your support network"
            ],
            "self_harm": [
                "Hold ice cubes in your hands",
                "Draw on your skin with a red marker",
                "Do intense exercise",
                "Call a friend or family member"
            ],
            "severe_distress": [
                "Practice deep breathing (4-7-8 technique)",
                "Use progressive muscle relaxation",
                "Try the 5-4-3-2-1 grounding technique",
                "Take a warm bath or shower"
            ]
        }
        
        return strategies.get(category, [
            "Practice mindfulness and meditation",
            "Engage in physical activity",
            "Connect with supportive people",
            "Use healthy distraction techniques"
        ])
    
    def _get_support_contacts(self):
        """Get emergency support contacts"""
        return [
            {"role": "Crisis Hotline", "contact": "988", "available": "24/7"},
            {"role": "Emergency Services", "contact": "911", "available": "24/7"},
            {"role": "Crisis Text Line", "contact": "Text HOME to 741741", "available": "24/7"}
        ]
    
    def _get_environmental_safety(self, category):
        """Get environmental safety measures"""
        if category in ["crisis", "self_harm"]:
            return [
                "Remove or secure sharp objects",
                "Remove or secure medications",
                "Remove or secure firearms",
                "Ask someone to stay with you",
                "Go to a safe, public place if alone"
            ]
        else:
            return [
                "Create a calm, safe space",
                "Remove stressors from environment",
                "Ensure access to support resources",
                "Have comfort items readily available"
            ]
    
    def _get_follow_up_plan(self, severity):
        """Get follow-up plan based on severity"""
        if severity == "critical":
            return [
                "Emergency mental health evaluation within 24 hours",
                "Daily check-ins with mental health professional",
                "Consider inpatient treatment if necessary"
            ]
        elif severity == "high":
            return [
                "Mental health appointment within 48-72 hours",
                "Daily self-monitoring and reporting",
                "Increased therapy frequency"
            ]
        else:
            return [
                "Mental health appointment within 1 week",
                "Regular self-monitoring",
                "Continue current treatment plan with modifications"
            ]
    
    def log_risk_assessment(self, text, alerts, patient_id=None):
        """Log risk assessment for tracking and analysis"""
        assessment_log = {
            "timestamp": datetime.now().isoformat(),
            "patient_id": patient_id,
            "text_length": len(text),
            "alerts_triggered": len([a for a in alerts if a.get("category") != "overall_assessment"]),
            "highest_risk_category": alerts[1]["category"] if len(alerts) > 1 else None,
            "overall_risk_score": alerts[0].get("risk_score", 0) if alerts else 0,
            "protective_factors": alerts[0].get("protective_factors", 0) if alerts else 0,
            "intervention_required": any(alert.get("requires_intervention", False) for alert in alerts),
            "alerts": alerts
        }
        
        # In a real application, this would be stored in a database
        logging.info(f"Risk assessment logged: {json.dumps(assessment_log, indent=2)}")
        
        return assessment_log
