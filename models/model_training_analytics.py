"""
Advanced Model Training Analytics System
Learns from multi-model responses to train custom models
Tracks accuracy, effectiveness, and generates training data
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
import joblib
import sqlite3
from collections import defaultdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class ModelResponse:
    """Captures response from each AI model"""
    model_name: str
    provider: str
    response: str
    confidence: float
    latency: float
    cost: float
    timestamp: datetime
    session_id: str
    user_feedback: Optional[float] = None
    clinical_validation: Optional[bool] = None
    crisis_detected: bool = False
    risk_level: Optional[str] = None

@dataclass
class TrainingDataPoint:
    """Structured data point for model training"""
    input_text: str
    context: Dict[str, Any]
    model_responses: List[ModelResponse]
    ground_truth: Optional[str] = None
    outcome_metrics: Optional[Dict[str, float]] = None
    session_metadata: Dict[str, Any] = None

class ModelTrainingAnalytics:
    """
    Collects multi-model responses and trains custom models
    Focuses on creating effective, low-cost crisis detection
    """

    def __init__(self, db_path: str = "data/model_analytics.db"):
        self.db_path = db_path
        self.training_data = []
        self.model_performance = defaultdict(lambda: {
            'accuracy': [],
            'precision': [],
            'recall': [],
            'f1': [],
            'cost': [],
            'latency': [],
            'crisis_detection_rate': [],
            'false_positive_rate': [],
            'user_satisfaction': []
        })
        self.custom_models = {}
        self.crisis_patterns = []
        self._initialize_database()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _initialize_database(self):
        """Create tables for storing analytics data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Model responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                model_name TEXT,
                provider TEXT,
                input_hash TEXT,
                response TEXT,
                confidence REAL,
                latency REAL,
                cost REAL,
                crisis_detected BOOLEAN,
                risk_level TEXT,
                user_feedback REAL,
                clinical_validation BOOLEAN,
                timestamp DATETIME
            )
        ''')

        # Training data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT,
                context TEXT,
                features TEXT,
                labels TEXT,
                model_consensus TEXT,
                ground_truth TEXT,
                outcome_metrics TEXT,
                created_at DATETIME
            )
        ''')

        # Crisis patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crisis_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_text TEXT,
                pattern_features TEXT,
                severity_level INTEGER,
                detection_count INTEGER,
                true_positive_rate REAL,
                first_detected DATETIME,
                last_detected DATETIME
            )
        ''')

        # Custom model registry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT UNIQUE,
                model_type TEXT,
                training_samples INTEGER,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                cost_per_inference REAL,
                model_path TEXT,
                created_at DATETIME,
                last_updated DATETIME
            )
        ''')

        conn.commit()
        conn.close()

    async def capture_model_response(self,
                                    session_id: str,
                                    input_text: str,
                                    model_name: str,
                                    provider: str,
                                    response: str,
                                    confidence: float,
                                    latency: float,
                                    cost: float,
                                    crisis_detected: bool = False,
                                    risk_level: Optional[str] = None) -> ModelResponse:
        """Capture and store model response for analysis"""

        model_response = ModelResponse(
            model_name=model_name,
            provider=provider,
            response=response,
            confidence=confidence,
            latency=latency,
            cost=cost,
            timestamp=datetime.now(),
            session_id=session_id,
            crisis_detected=crisis_detected,
            risk_level=risk_level
        )

        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        input_hash = hashlib.md5(input_text.encode()).hexdigest()

        cursor.execute('''
            INSERT INTO model_responses
            (session_id, model_name, provider, input_hash, response,
             confidence, latency, cost, crisis_detected, risk_level, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, model_name, provider, input_hash, response,
            confidence, latency, cost, crisis_detected, risk_level,
            model_response.timestamp
        ))

        conn.commit()
        conn.close()

        # Update performance metrics
        self.model_performance[model_name]['latency'].append(latency)
        self.model_performance[model_name]['cost'].append(cost)

        # Check for crisis patterns
        if crisis_detected:
            await self._analyze_crisis_pattern(input_text, model_response)

        return model_response

    async def _analyze_crisis_pattern(self, input_text: str, response: ModelResponse):
        """Analyze and store crisis patterns for model training"""

        # Extract features from crisis text
        features = self._extract_crisis_features(input_text)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if pattern exists
        pattern_hash = hashlib.md5(json.dumps(features, sort_keys=True).encode()).hexdigest()

        cursor.execute('''
            SELECT id, detection_count FROM crisis_patterns
            WHERE pattern_features = ?
        ''', (pattern_hash,))

        existing = cursor.fetchone()

        if existing:
            # Update existing pattern
            cursor.execute('''
                UPDATE crisis_patterns
                SET detection_count = detection_count + 1,
                    last_detected = ?
                WHERE id = ?
            ''', (datetime.now(), existing[0]))
        else:
            # Add new pattern
            cursor.execute('''
                INSERT INTO crisis_patterns
                (pattern_text, pattern_features, severity_level,
                 detection_count, true_positive_rate, first_detected, last_detected)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                input_text[:500],  # Store first 500 chars
                pattern_hash,
                self._calculate_severity(response.risk_level),
                1,
                0.0,  # Will be updated with feedback
                datetime.now(),
                datetime.now()
            ))

        conn.commit()
        conn.close()

    def _extract_crisis_features(self, text: str) -> Dict[str, Any]:
        """Extract features indicative of crisis from text"""

        crisis_keywords = {
            'immediate': ['suicide', 'kill myself', 'end it all', 'can\'t go on',
                         'want to die', 'no point', 'worthless', 'hopeless'],
            'high': ['self harm', 'hurt myself', 'cutting', 'overdose',
                    'pills', 'jump', 'gun', 'rope'],
            'medium': ['depressed', 'anxious', 'panic', 'scared', 'alone',
                      'nobody cares', 'burden', 'failure'],
            'warning': ['tired', 'exhausted', 'giving up', 'done trying',
                       'goodbye', 'sorry', 'forgive me']
        }

        features = {
            'text_length': len(text),
            'word_count': len(text.split()),
            'exclamation_marks': text.count('!'),
            'question_marks': text.count('?'),
            'all_caps_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
            'crisis_keywords': {},
            'sentiment_indicators': {}
        }

        # Check for crisis keywords
        text_lower = text.lower()
        for severity, keywords in crisis_keywords.items():
            features['crisis_keywords'][severity] = sum(
                1 for keyword in keywords if keyword in text_lower
            )

        # Add sentiment indicators
        negative_words = ['not', 'no', 'never', 'nothing', 'nobody', 'nowhere']
        features['sentiment_indicators']['negation_count'] = sum(
            1 for word in negative_words if word in text_lower.split()
        )

        # Calculate urgency score
        features['urgency_score'] = (
            features['crisis_keywords'].get('immediate', 0) * 10 +
            features['crisis_keywords'].get('high', 0) * 5 +
            features['crisis_keywords'].get('medium', 0) * 2 +
            features['crisis_keywords'].get('warning', 0)
        )

        return features

    def _calculate_severity(self, risk_level: Optional[str]) -> int:
        """Convert risk level to severity score"""
        severity_map = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 2,
            'minimal': 1
        }
        return severity_map.get(risk_level, 3)

    async def create_training_batch(self,
                                   model_responses: List[ModelResponse],
                                   ground_truth: Optional[str] = None) -> TrainingDataPoint:
        """Create training data from multiple model responses"""

        # Aggregate responses
        consensus = self._calculate_consensus(model_responses)

        # Extract features
        features = {
            'model_agreement': self._calculate_agreement_score(model_responses),
            'avg_confidence': np.mean([r.confidence for r in model_responses]),
            'crisis_consensus': sum(1 for r in model_responses if r.crisis_detected) / len(model_responses),
            'response_variance': self._calculate_response_variance(model_responses),
            'cost_efficiency': self._calculate_cost_efficiency(model_responses)
        }

        training_point = TrainingDataPoint(
            input_text=model_responses[0].session_id,  # Use session_id as reference
            context=features,
            model_responses=model_responses,
            ground_truth=ground_truth
        )

        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO training_data
            (input_text, context, features, model_consensus, ground_truth, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            training_point.input_text,
            json.dumps(training_point.context),
            json.dumps(features),
            consensus,
            ground_truth,
            datetime.now()
        ))

        conn.commit()
        conn.close()

        return training_point

    def _calculate_consensus(self, responses: List[ModelResponse]) -> str:
        """Calculate consensus response from multiple models"""

        if not responses:
            return "No consensus available"

        # For crisis detection, use majority vote
        crisis_votes = sum(1 for r in responses if r.crisis_detected)
        crisis_consensus = crisis_votes > len(responses) / 2

        # For risk level, use weighted average based on confidence
        risk_levels = {'minimal': 1, 'low': 2, 'medium': 3, 'high': 4, 'critical': 5}
        weighted_risk = 0
        total_weight = 0

        for r in responses:
            if r.risk_level:
                weight = r.confidence
                weighted_risk += risk_levels.get(r.risk_level, 3) * weight
                total_weight += weight

        avg_risk = weighted_risk / max(total_weight, 1)

        # Map back to risk level
        for level, value in risk_levels.items():
            if avg_risk <= value:
                consensus_risk = level
                break
        else:
            consensus_risk = 'medium'

        return json.dumps({
            'crisis_detected': crisis_consensus,
            'risk_level': consensus_risk,
            'confidence': np.mean([r.confidence for r in responses])
        })

    def _calculate_agreement_score(self, responses: List[ModelResponse]) -> float:
        """Calculate how much models agree with each other"""

        if len(responses) < 2:
            return 1.0

        # Check crisis detection agreement
        crisis_detections = [r.crisis_detected for r in responses]
        crisis_agreement = (crisis_detections.count(True) / len(crisis_detections)
                           if sum(crisis_detections) > len(crisis_detections) / 2
                           else crisis_detections.count(False) / len(crisis_detections))

        # Check risk level agreement
        risk_levels = [r.risk_level for r in responses if r.risk_level]
        if risk_levels:
            most_common = max(set(risk_levels), key=risk_levels.count)
            risk_agreement = risk_levels.count(most_common) / len(risk_levels)
        else:
            risk_agreement = 1.0

        return (crisis_agreement + risk_agreement) / 2

    def _calculate_response_variance(self, responses: List[ModelResponse]) -> float:
        """Calculate variance in model responses"""

        if len(responses) < 2:
            return 0.0

        # Variance in confidence scores
        confidences = [r.confidence for r in responses]
        confidence_var = np.var(confidences)

        # Variance in response lengths
        lengths = [len(r.response) for r in responses]
        length_var = np.var(lengths) / max(np.mean(lengths), 1)

        return (confidence_var + length_var) / 2

    def _calculate_cost_efficiency(self, responses: List[ModelResponse]) -> float:
        """Calculate cost efficiency of model combination"""

        total_cost = sum(r.cost for r in responses)
        avg_confidence = np.mean([r.confidence for r in responses])

        # Efficiency = confidence per dollar
        return avg_confidence / max(total_cost, 0.001)

    async def train_custom_crisis_model(self, min_samples: int = 100) -> Optional[str]:
        """
        Train a custom crisis detection model from collected data
        Optimized for free-tier usage
        """

        logger.info("Starting custom crisis model training...")

        # Load training data
        conn = sqlite3.connect(self.db_path)
        df_responses = pd.read_sql_query('''
            SELECT * FROM model_responses
            WHERE crisis_detected IS NOT NULL
            ORDER BY timestamp DESC
            LIMIT 10000
        ''', conn)

        df_patterns = pd.read_sql_query('''
            SELECT * FROM crisis_patterns
        ''', conn)

        conn.close()

        if len(df_responses) < min_samples:
            logger.warning(f"Insufficient samples: {len(df_responses)} < {min_samples}")
            return None

        # Prepare features and labels
        X, y = self._prepare_crisis_training_data(df_responses, df_patterns)

        if len(X) < min_samples:
            return None

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Train multiple models
        models = {
            'rf_crisis': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                class_weight='balanced',
                random_state=42
            ),
            'gb_crisis': GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            ),
            'nn_crisis': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                activation='relu',
                solver='adam',
                max_iter=500,
                random_state=42
            )
        }

        best_model = None
        best_score = 0
        best_name = None

        for name, model in models.items():
            try:
                # Train model
                model.fit(X_train, y_train)

                # Evaluate
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                precision, recall, f1, _ = precision_recall_fscore_support(
                    y_test, y_pred, average='weighted'
                )

                # For crisis detection, recall is most important
                weighted_score = recall * 0.6 + precision * 0.3 + f1 * 0.1

                logger.info(f"Model {name}: Accuracy={accuracy:.3f}, "
                          f"Precision={precision:.3f}, Recall={recall:.3f}, "
                          f"F1={f1:.3f}, Weighted={weighted_score:.3f}")

                if weighted_score > best_score:
                    best_score = weighted_score
                    best_model = model
                    best_name = name

            except Exception as e:
                logger.error(f"Error training {name}: {e}")
                continue

        if best_model:
            # Save the best model
            model_path = f"models/custom_crisis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
            joblib.dump(best_model, model_path)

            # Register in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO custom_models
                (model_name, model_type, training_samples, accuracy,
                 precision, recall, f1_score, cost_per_inference,
                 model_path, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"custom_crisis_{best_name}",
                best_name,
                len(X_train),
                accuracy,
                precision,
                recall,
                f1,
                0.0001,  # Minimal cost for local inference
                model_path,
                datetime.now(),
                datetime.now()
            ))

            conn.commit()
            conn.close()

            logger.info(f"Custom crisis model trained and saved: {model_path}")
            return model_path

        return None

    def _prepare_crisis_training_data(self,
                                     df_responses: pd.DataFrame,
                                     df_patterns: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and labels for crisis model training"""

        features_list = []
        labels_list = []

        # Group by input_hash to aggregate model responses
        for input_hash, group in df_responses.groupby('input_hash'):
            # Extract features
            features = {
                'num_models': len(group),
                'crisis_consensus': group['crisis_detected'].mean(),
                'avg_confidence': group['confidence'].mean(),
                'max_confidence': group['confidence'].max(),
                'min_confidence': group['confidence'].min(),
                'confidence_std': group['confidence'].std(),
                'high_risk_count': (group['risk_level'] == 'high').sum() +
                                  (group['risk_level'] == 'critical').sum(),
                'response_time': group['latency'].mean()
            }

            # Add pattern-based features
            # (In production, would extract from actual text)
            features['urgency_score'] = np.random.random() * 10  # Placeholder
            features['keyword_count'] = np.random.randint(0, 5)  # Placeholder

            # Convert to array
            feature_array = np.array(list(features.values()))
            features_list.append(feature_array)

            # Label: crisis if majority detected it
            label = int(group['crisis_detected'].mean() > 0.5)
            labels_list.append(label)

        return np.array(features_list), np.array(labels_list)

    def get_model_recommendations(self, task_type: str) -> Dict[str, Any]:
        """Get recommendations for which models to use based on performance data"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get performance metrics for each model
        cursor.execute('''
            SELECT
                model_name,
                provider,
                AVG(confidence) as avg_confidence,
                AVG(latency) as avg_latency,
                AVG(cost) as avg_cost,
                SUM(CASE WHEN crisis_detected THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as crisis_detection_rate,
                COUNT(*) as usage_count
            FROM model_responses
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY model_name, provider
        ''')

        results = cursor.fetchall()
        conn.close()

        recommendations = {
            'primary': [],
            'fallback': [],
            'cost_effective': [],
            'high_accuracy': [],
            'low_latency': []
        }

        for row in results:
            model_info = {
                'model_name': row[0],
                'provider': row[1],
                'avg_confidence': row[2],
                'avg_latency': row[3],
                'avg_cost': row[4],
                'crisis_detection_rate': row[5],
                'usage_count': row[6]
            }

            # Categorize models
            if model_info['avg_cost'] < 0.001:
                recommendations['cost_effective'].append(model_info)
            if model_info['avg_confidence'] > 0.85:
                recommendations['high_accuracy'].append(model_info)
            if model_info['avg_latency'] < 1.0:
                recommendations['low_latency'].append(model_info)

        # Sort each category by relevance
        for category in recommendations:
            recommendations[category].sort(
                key=lambda x: x['avg_confidence'],
                reverse=True
            )

        # Select primary and fallback
        if recommendations['high_accuracy']:
            recommendations['primary'] = recommendations['high_accuracy'][:2]
        if recommendations['cost_effective']:
            recommendations['fallback'] = recommendations['cost_effective'][:2]

        return recommendations

    async def generate_model_report(self) -> Dict[str, Any]:
        """Generate comprehensive report on model performance and training progress"""

        conn = sqlite3.connect(self.db_path)

        # Get overall statistics
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(*) as total_responses,
                AVG(cost) as avg_cost,
                SUM(cost) as total_cost,
                AVG(latency) as avg_latency
            FROM model_responses
            WHERE timestamp > datetime('now', '-30 days')
        ''')

        overall_stats = cursor.fetchone()

        # Get model-specific performance
        df_performance = pd.read_sql_query('''
            SELECT
                model_name,
                provider,
                COUNT(*) as usage_count,
                AVG(confidence) as avg_confidence,
                AVG(cost) as avg_cost,
                AVG(latency) as avg_latency,
                SUM(CASE WHEN crisis_detected THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as crisis_detection_pct
            FROM model_responses
            WHERE timestamp > datetime('now', '-30 days')
            GROUP BY model_name, provider
            ORDER BY usage_count DESC
        ''', conn)

        # Get custom model performance
        df_custom = pd.read_sql_query('''
            SELECT * FROM custom_models
            ORDER BY created_at DESC
            LIMIT 10
        ''', conn)

        # Get crisis pattern insights
        df_patterns = pd.read_sql_query('''
            SELECT
                severity_level,
                COUNT(*) as pattern_count,
                SUM(detection_count) as total_detections,
                AVG(true_positive_rate) as avg_tpr
            FROM crisis_patterns
            GROUP BY severity_level
        ''', conn)

        conn.close()

        report = {
            'summary': {
                'total_sessions': overall_stats[0],
                'total_model_calls': overall_stats[1],
                'average_cost_per_call': overall_stats[2],
                'total_cost_30_days': overall_stats[3],
                'average_latency': overall_stats[4],
                'report_generated': datetime.now().isoformat()
            },
            'model_performance': df_performance.to_dict('records'),
            'custom_models': df_custom.to_dict('records'),
            'crisis_patterns': df_patterns.to_dict('records'),
            'recommendations': self.get_model_recommendations('general'),
            'training_progress': {
                'total_training_samples': len(self.training_data),
                'models_trained': len(self.custom_models),
                'next_training_threshold': 1000,
                'samples_until_training': max(0, 1000 - len(self.training_data))
            }
        }

        return report

# Singleton instance
model_analytics = ModelTrainingAnalytics()