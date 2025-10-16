"""
Universal Crisis Prediction System
Prioritizes free/low-cost models while maintaining high accuracy
Includes rapid custom model training for free-tier users
"""

import os
import json
import logging
import numpy as np
import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import joblib
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Import local models
from models.model_training_analytics import ModelTrainingAnalytics

logger = logging.getLogger(__name__)

class CrisisSeverity(Enum):
    """Crisis severity levels"""
    CRITICAL = "critical"  # Immediate intervention needed
    HIGH = "high"          # Urgent response required
    MEDIUM = "medium"      # Close monitoring needed
    LOW = "low"            # Preventive measures
    MINIMAL = "minimal"    # No immediate concern

class ModelTier(Enum):
    """Model tiers based on cost"""
    FREE = "free"          # Local models, no API cost
    CHEAP = "cheap"        # < $0.001 per call
    MODERATE = "moderate"  # < $0.01 per call
    EXPENSIVE = "expensive" # > $0.01 per call

@dataclass
class CrisisPrediction:
    """Crisis prediction result"""
    is_crisis: bool
    severity: CrisisSeverity
    confidence: float
    risk_factors: List[str]
    recommended_actions: List[str]
    model_used: str
    cost: float
    latency: float
    requires_human_review: bool

class UniversalCrisisPredictor:
    """
    Universal crisis detection system that works across all user tiers
    Prioritizes free/low-cost models and trains custom models rapidly
    """

    def __init__(self):
        self.analytics = ModelTrainingAnalytics()
        self.custom_model = None
        self.custom_model_path = None
        self.load_custom_model()
        self.executor = ThreadPoolExecutor(max_workers=3)

        # Crisis detection patterns (works offline)
        self.crisis_patterns = self._initialize_crisis_patterns()

        # Model routing configuration
        self.model_routes = {
            ModelTier.FREE: [
                'custom_crisis_model',
                'pattern_matching',
                'rule_based_detector'
            ],
            ModelTier.CHEAP: [
                'ollama_llama2',
                'ollama_mistral',
                'huggingface_mental_bert'
            ],
            ModelTier.MODERATE: [
                'gpt-3.5-turbo',
                'claude-instant'
            ],
            ModelTier.EXPENSIVE: [
                'gpt-4o',
                'claude-3-opus'
            ]
        }

        # Cache for recent predictions
        self.prediction_cache = {}
        self.cache_ttl = 300  # 5 minutes

    def _initialize_crisis_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize crisis detection patterns for offline detection"""
        return {
            'immediate_danger': {
                'patterns': [
                    r'\b(suicide|kill\s+myself|end\s+it\s+all|want\s+to\s+die)\b',
                    r'\b(can\'t\s+do\s+this|can\'t\s+go\s+on|no\s+point\s+living|better\s+off\s+dead)\b',
                    r'\b(goodbye\s+forever|final\s+goodbye|this\s+is\s+(goodbye|it))\b',
                    r'\b(pills|gun|rope|jump|bridge|knife|razor)\b.*\b(take|use|do\s+it|tonight|ready)\b',
                    r'\b(have|got)\b.*\b(pills|gun|rope)\b.*\b(going\s+to|will|tonight)\b'
                ],
                'severity': CrisisSeverity.CRITICAL,
                'confidence_boost': 0.3
            },
            'self_harm': {
                'patterns': [
                    r'\b(cut|cutting|self[\s-]?harm|hurt\s+myself)\b',
                    r'\b(burn|burning\s+myself|razor|blade)\b',
                    r'\b(punish\s+myself|deserve\s+pain|need\s+to\s+feel)\b',
                    r'\b(relapse|slipped|did\s+it\s+again)\b.*\b(cut|harm)\b'
                ],
                'severity': CrisisSeverity.HIGH,
                'confidence_boost': 0.2
            },
            'severe_distress': {
                'patterns': [
                    r'\b(hopeless|helpless|worthless|useless)\b',
                    r'\b(everyone\s+hates|nobody\s+cares|all\s+alone)\b',
                    r'\b(can\'t\s+take\s+it|breaking\s+down|falling\s+apart)\b',
                    r'\b(panic|terrified|overwhelming|drowning)\b'
                ],
                'severity': CrisisSeverity.MEDIUM,
                'confidence_boost': 0.1
            },
            'risk_indicators': {
                'patterns': [
                    r'\b(given\s+up|done\s+trying|what\'s\s+the\s+point)\b',
                    r'\b(burden|better\s+without\s+me|holding.*back)\b',
                    r'\b(trapped|no\s+escape|no\s+way\s+out)\b',
                    r'\b(final|last|end|goodbye)\b.*\b(note|letter|message)\b'
                ],
                'severity': CrisisSeverity.HIGH,
                'confidence_boost': 0.15
            },
            'substance_crisis': {
                'patterns': [
                    r'\b(overdose|OD|too\s+many\s+pills)\b',
                    r'\b(drunk|wasted|high)\b.*\b(suicide|die|end)\b',
                    r'\b(mixing|combined|together)\b.*\b(pills|drugs|alcohol)\b',
                    r'\b(relapsed|using\s+again|back\s+on)\b.*\b(drugs|drinking)\b'
                ],
                'severity': CrisisSeverity.HIGH,
                'confidence_boost': 0.2
            }
        }

    def load_custom_model(self):
        """Load the latest custom crisis model if available"""
        try:
            # Check for existing custom model
            import os
            model_files = [f for f in os.listdir('models')
                          if f.startswith('custom_crisis_') and f.endswith('.joblib')]

            if model_files:
                # Load the most recent model
                latest_model = sorted(model_files)[-1]
                self.custom_model_path = f'models/{latest_model}'
                self.custom_model = joblib.load(self.custom_model_path)
                logger.info(f"Loaded custom crisis model: {latest_model}")
        except Exception as e:
            logger.warning(f"No custom crisis model available: {e}")
            self.custom_model = None

    async def predict_crisis(self,
                            text: str,
                            user_tier: str = 'free',
                            context: Optional[Dict[str, Any]] = None,
                            force_free: bool = False) -> CrisisPrediction:
        """
        Predict crisis with tier-appropriate models
        Always runs free detection first for immediate response
        """

        # Check cache first
        cache_key = hashlib.md5(f"{text}{user_tier}".encode()).hexdigest()
        if cache_key in self.prediction_cache:
            cached = self.prediction_cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < self.cache_ttl:
                return cached['prediction']

        # Always run free detection first for immediate response
        free_prediction = await self._run_free_detection(text, context)

        # If critical crisis detected, return immediately
        if free_prediction.severity == CrisisSeverity.CRITICAL:
            logger.warning(f"CRITICAL crisis detected: {free_prediction.risk_factors}")
            return free_prediction

        # If user is free tier or force_free, return free prediction
        if user_tier == 'free' or force_free:
            return free_prediction

        # For paid tiers, enhance with additional models
        enhanced_prediction = await self._enhance_with_paid_models(
            text, context, user_tier, free_prediction
        )

        # Cache the result
        self.prediction_cache[cache_key] = {
            'prediction': enhanced_prediction,
            'timestamp': datetime.now()
        }

        # Log for training data
        await self._log_prediction(text, enhanced_prediction)

        return enhanced_prediction

    async def _run_free_detection(self,
                                 text: str,
                                 context: Optional[Dict[str, Any]] = None) -> CrisisPrediction:
        """Run completely free crisis detection"""

        start_time = datetime.now()

        # 1. Pattern-based detection (instant, no cost)
        pattern_result = self._detect_crisis_patterns(text)

        # 2. Rule-based detection (instant, no cost)
        rule_result = self._apply_crisis_rules(text, context)

        # 3. Custom model if available (near-instant, no cost)
        custom_result = None
        if self.custom_model:
            custom_result = self._run_custom_model(text, context)

        # Combine results
        predictions = [pattern_result, rule_result]
        if custom_result:
            predictions.append(custom_result)

        # Aggregate predictions
        final_prediction = self._aggregate_predictions(predictions)

        # Calculate latency
        latency = (datetime.now() - start_time).total_seconds()

        return CrisisPrediction(
            is_crisis=final_prediction['is_crisis'],
            severity=final_prediction['severity'],
            confidence=final_prediction['confidence'],
            risk_factors=final_prediction['risk_factors'],
            recommended_actions=self._get_recommended_actions(final_prediction['severity']),
            model_used='free_ensemble',
            cost=0.0,
            latency=latency,
            requires_human_review=final_prediction['confidence'] < 0.7
        )

    def _detect_crisis_patterns(self, text: str) -> Dict[str, Any]:
        """Detect crisis using regex patterns"""

        text_lower = text.lower()
        detected_patterns = []
        max_severity = CrisisSeverity.MINIMAL
        confidence = 0.0

        for category, config in self.crisis_patterns.items():
            for pattern in config['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected_patterns.append(category)
                    confidence += config['confidence_boost']

                    # Fix severity comparison - use proper enum comparison
                    severity_order = {
                        CrisisSeverity.MINIMAL: 0,
                        CrisisSeverity.LOW: 1,
                        CrisisSeverity.MEDIUM: 2,
                        CrisisSeverity.HIGH: 3,
                        CrisisSeverity.CRITICAL: 4
                    }
                    if severity_order[config['severity']] > severity_order[max_severity]:
                        max_severity = config['severity']

                    break  # Only count each category once

        # Adjust confidence
        confidence = min(confidence, 0.95)  # Cap at 95%

        # Check text characteristics
        if len(text) < 20:
            confidence *= 0.7  # Short texts are less reliable
        if text.isupper():
            confidence += 0.1  # All caps indicates distress
        if text.count('!') > 3:
            confidence += 0.05  # Multiple exclamations

        return {
            'is_crisis': len(detected_patterns) > 0,
            'severity': max_severity,
            'confidence': confidence,
            'risk_factors': detected_patterns,
            'method': 'pattern_matching'
        }

    def _apply_crisis_rules(self, text: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply rule-based crisis detection"""

        risk_score = 0
        risk_factors = []

        # Text-based rules
        text_lower = text.lower()

        # Negation analysis
        negations = ['not', 'no', 'never', 'nothing', 'nobody', 'nowhere', 'none']
        negation_count = sum(1 for word in negations if word in text_lower.split())
        if negation_count > 3:
            risk_score += 20
            risk_factors.append('high_negation')

        # Temporal urgency
        urgent_temporal = ['now', 'today', 'tonight', 'immediately', 'soon', 'finally']
        if any(word in text_lower for word in urgent_temporal):
            risk_score += 15
            risk_factors.append('temporal_urgency')

        # Finality indicators
        final_words = ['goodbye', 'farewell', 'sorry', 'forgive', 'last', 'final', 'end']
        if any(word in text_lower for word in final_words):
            risk_score += 25
            risk_factors.append('finality_language')

        # Context-based rules (if available)
        if context:
            # Recent crisis history
            if context.get('recent_crisis', False):
                risk_score += 30
                risk_factors.append('crisis_history')

            # Time of day (late night/early morning higher risk)
            hour = datetime.now().hour
            if hour < 6 or hour > 23:
                risk_score += 10
                risk_factors.append('high_risk_time')

            # Session frequency drop
            if context.get('session_frequency_drop', False):
                risk_score += 15
                risk_factors.append('engagement_drop')

        # Determine severity based on risk score
        if risk_score >= 70:
            severity = CrisisSeverity.CRITICAL
        elif risk_score >= 50:
            severity = CrisisSeverity.HIGH
        elif risk_score >= 30:
            severity = CrisisSeverity.MEDIUM
        elif risk_score >= 15:
            severity = CrisisSeverity.LOW
        else:
            severity = CrisisSeverity.MINIMAL

        return {
            'is_crisis': risk_score >= 30,
            'severity': severity,
            'confidence': min(risk_score / 100, 0.9),
            'risk_factors': risk_factors,
            'method': 'rule_based'
        }

    def _run_custom_model(self, text: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Run custom trained model for crisis detection"""

        if not self.custom_model:
            return None

        try:
            # Extract features (simplified version)
            features = self._extract_model_features(text, context)

            # Make prediction
            prediction = self.custom_model.predict_proba([features])[0]
            crisis_probability = prediction[1] if len(prediction) > 1 else prediction[0]

            # Determine severity based on probability
            if crisis_probability >= 0.9:
                severity = CrisisSeverity.CRITICAL
            elif crisis_probability >= 0.7:
                severity = CrisisSeverity.HIGH
            elif crisis_probability >= 0.5:
                severity = CrisisSeverity.MEDIUM
            elif crisis_probability >= 0.3:
                severity = CrisisSeverity.LOW
            else:
                severity = CrisisSeverity.MINIMAL

            return {
                'is_crisis': crisis_probability >= 0.5,
                'severity': severity,
                'confidence': crisis_probability,
                'risk_factors': ['ml_model_detection'],
                'method': 'custom_model'
            }

        except Exception as e:
            logger.error(f"Error running custom model: {e}")
            return None

    def _extract_model_features(self, text: str, context: Optional[Dict[str, Any]]) -> np.ndarray:
        """Extract features for ML model"""

        features = []

        # Text features
        features.append(len(text))
        features.append(len(text.split()))
        features.append(text.count('!'))
        features.append(text.count('?'))
        features.append(sum(1 for c in text if c.isupper()) / max(len(text), 1))

        # Pattern matches
        text_lower = text.lower()
        crisis_keywords = ['suicide', 'die', 'kill', 'hurt', 'pain', 'hopeless', 'worthless']
        features.append(sum(1 for kw in crisis_keywords if kw in text_lower))

        # Context features (if available)
        if context:
            features.append(float(context.get('session_count', 0)))
            features.append(float(context.get('days_since_last_crisis', 30)))
            features.append(float(context.get('user_age', 25)))
        else:
            features.extend([0, 30, 25])  # Default values

        return np.array(features)

    def _aggregate_predictions(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple predictions into final result"""

        if not predictions:
            return {
                'is_crisis': False,
                'severity': CrisisSeverity.MINIMAL,
                'confidence': 0.0,
                'risk_factors': []
            }

        # Remove None values
        predictions = [p for p in predictions if p is not None]

        # Weighted voting based on method reliability
        weights = {
            'pattern_matching': 0.35,
            'rule_based': 0.30,
            'custom_model': 0.35
        }

        total_weight = 0
        weighted_confidence = 0
        all_risk_factors = []
        severity_scores = []

        for pred in predictions:
            method = pred.get('method', 'unknown')
            weight = weights.get(method, 0.2)

            weighted_confidence += pred['confidence'] * weight
            total_weight += weight
            all_risk_factors.extend(pred['risk_factors'])

            # Convert severity to numeric score
            severity_map = {
                CrisisSeverity.CRITICAL: 5,
                CrisisSeverity.HIGH: 4,
                CrisisSeverity.MEDIUM: 3,
                CrisisSeverity.LOW: 2,
                CrisisSeverity.MINIMAL: 1
            }
            severity_scores.append(severity_map[pred['severity']] * weight)

        # Calculate final values
        final_confidence = weighted_confidence / max(total_weight, 0.001)
        avg_severity_score = sum(severity_scores) / max(total_weight, 0.001)

        # Map severity score back to enum
        if avg_severity_score >= 4.5:
            final_severity = CrisisSeverity.CRITICAL
        elif avg_severity_score >= 3.5:
            final_severity = CrisisSeverity.HIGH
        elif avg_severity_score >= 2.5:
            final_severity = CrisisSeverity.MEDIUM
        elif avg_severity_score >= 1.5:
            final_severity = CrisisSeverity.LOW
        else:
            final_severity = CrisisSeverity.MINIMAL

        # Crisis detection threshold
        is_crisis = final_confidence >= 0.4 or final_severity.value >= CrisisSeverity.HIGH.value

        return {
            'is_crisis': is_crisis,
            'severity': final_severity,
            'confidence': final_confidence,
            'risk_factors': list(set(all_risk_factors))  # Remove duplicates
        }

    async def _enhance_with_paid_models(self,
                                       text: str,
                                       context: Optional[Dict[str, Any]],
                                       user_tier: str,
                                       base_prediction: CrisisPrediction) -> CrisisPrediction:
        """Enhance prediction with paid models for premium users"""

        # This would integrate with actual AI providers
        # For now, return enhanced version of base prediction

        # Simulate API call delay
        await asyncio.sleep(0.1)

        # In production, would call actual models based on tier
        enhanced = CrisisPrediction(
            is_crisis=base_prediction.is_crisis,
            severity=base_prediction.severity,
            confidence=min(base_prediction.confidence + 0.1, 0.99),  # Boost confidence
            risk_factors=base_prediction.risk_factors + ['enhanced_analysis'],
            recommended_actions=base_prediction.recommended_actions,
            model_used=f'{base_prediction.model_used}+{user_tier}_models',
            cost=0.001 if user_tier == 'basic' else 0.01,  # Simulated cost
            latency=base_prediction.latency + 0.5,
            requires_human_review=base_prediction.confidence < 0.8
        )

        return enhanced

    def _get_recommended_actions(self, severity: CrisisSeverity) -> List[str]:
        """Get recommended actions based on severity"""

        actions = {
            CrisisSeverity.CRITICAL: [
                "Immediately connect with crisis counselor",
                "Call emergency services if in immediate danger",
                "Activate safety plan",
                "Remove access to harmful means",
                "Stay with someone trusted"
            ],
            CrisisSeverity.HIGH: [
                "Schedule urgent session with therapist",
                "Contact crisis hotline for support",
                "Reach out to support network",
                "Practice crisis coping skills",
                "Monitor closely for next 24 hours"
            ],
            CrisisSeverity.MEDIUM: [
                "Schedule therapy session within 48 hours",
                "Increase check-in frequency",
                "Practice self-care activities",
                "Review coping strategies",
                "Connect with support group"
            ],
            CrisisSeverity.LOW: [
                "Continue regular therapy schedule",
                "Practice mindfulness exercises",
                "Maintain healthy routines",
                "Journal about feelings",
                "Engage in pleasant activities"
            ],
            CrisisSeverity.MINIMAL: [
                "Continue self-care practices",
                "Maintain therapy if scheduled",
                "Focus on wellness activities",
                "Build resilience skills",
                "Celebrate progress"
            ]
        }

        return actions.get(severity, [])

    async def _log_prediction(self, text: str, prediction: CrisisPrediction):
        """Log prediction for training data"""

        # This would log to the analytics system
        if prediction.is_crisis:
            logger.info(f"Crisis detected: Severity={prediction.severity.value}, "
                       f"Confidence={prediction.confidence:.2f}, "
                       f"Model={prediction.model_used}")

    async def train_emergency_model(self, training_data: List[Tuple[str, bool]]) -> bool:
        """
        Rapidly train a crisis model with minimal data
        Used when custom model needs urgent update
        """

        logger.info(f"Emergency model training initiated with {len(training_data)} samples")

        if len(training_data) < 50:
            logger.warning("Insufficient data for emergency training")
            return False

        try:
            # Extract features and labels
            X = []
            y = []

            for text, is_crisis in training_data:
                features = self._extract_model_features(text, {})
                X.append(features)
                y.append(int(is_crisis))

            X = np.array(X)
            y = np.array(y)

            # Train a simple model quickly
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(
                n_estimators=50,  # Fewer trees for speed
                max_depth=5,
                min_samples_split=5,
                class_weight='balanced',  # Handle imbalanced data
                random_state=42
            )

            model.fit(X, y)

            # Save emergency model
            emergency_path = f"models/emergency_crisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
            joblib.dump(model, emergency_path)

            # Update to use new model
            self.custom_model = model
            self.custom_model_path = emergency_path

            logger.info(f"Emergency model trained and deployed: {emergency_path}")
            return True

        except Exception as e:
            logger.error(f"Emergency training failed: {e}")
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status and capabilities"""

        return {
            'custom_model_available': self.custom_model is not None,
            'custom_model_path': self.custom_model_path,
            'free_tier_capabilities': [
                'pattern_matching',
                'rule_based_detection',
                'custom_model' if self.custom_model else None
            ],
            'cache_size': len(self.prediction_cache),
            'patterns_loaded': len(self.crisis_patterns),
            'status': 'operational'
        }

# Create singleton instance
crisis_predictor = UniversalCrisisPredictor()