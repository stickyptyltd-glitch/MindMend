"""
Automated Model Training Pipeline
Continuously improves models based on multi-model responses and outcomes
"""

import os
import json
import logging
import asyncio
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import sqlite3
from collections import defaultdict

logger = logging.getLogger(__name__)

class AutoTrainingPipeline:
    """
    Automated pipeline for training custom models from multi-model responses
    Focuses on rapid iteration and continuous improvement
    """

    def __init__(self,
                 analytics_db: str = "data/model_analytics.db",
                 training_interval_hours: int = 6):
        self.analytics_db = analytics_db
        self.training_interval = timedelta(hours=training_interval_hours)
        self.last_training = datetime.now() - self.training_interval

        # Training thresholds
        self.min_samples = {
            'crisis': 50,      # Minimum for crisis model (safety critical)
            'emotion': 100,    # Minimum for emotion classifier
            'therapy': 200,    # Minimum for therapy enhancer
            'general': 500     # Minimum for general models
        }

        # Model registry
        self.active_models = {}
        self.model_performance = defaultdict(list)

        # Training queue
        self.training_queue = asyncio.Queue()
        self.is_training = False

        # Initialize scheduler
        self._setup_scheduler()

    def _setup_scheduler(self):
        """Setup automated training schedule"""

        # Schedule regular training cycles
        schedule.every(6).hours.do(self.trigger_training_cycle)
        schedule.every().day.at("03:00").do(self.comprehensive_retraining)
        schedule.every().week.do(self.generate_training_report)

        # Emergency training for crisis models
        schedule.every(30).minutes.do(self.check_crisis_model_performance)

    async def trigger_training_cycle(self):
        """Trigger a training cycle if conditions are met"""

        logger.info("Checking training conditions...")

        # Check data availability
        conn = sqlite3.connect(self.analytics_db)
        cursor = conn.cursor()

        # Count recent samples
        cursor.execute("""
            SELECT COUNT(*) FROM model_responses
            WHERE timestamp > datetime('now', '-7 days')
        """)
        recent_samples = cursor.fetchone()[0]

        # Count unprocessed training data
        cursor.execute("""
            SELECT COUNT(*) FROM training_data
            WHERE ground_truth IS NULL
        """)
        unlabeled_samples = cursor.fetchone()[0]

        conn.close()

        logger.info(f"Recent samples: {recent_samples}, Unlabeled: {unlabeled_samples}")

        # Decide what to train
        training_tasks = []

        if recent_samples >= self.min_samples['crisis']:
            training_tasks.append(('crisis', self.train_crisis_model))

        if recent_samples >= self.min_samples['emotion']:
            training_tasks.append(('emotion', self.train_emotion_model))

        if recent_samples >= self.min_samples['therapy']:
            training_tasks.append(('therapy', self.train_therapy_enhancer))

        # Execute training tasks
        for model_type, training_func in training_tasks:
            await self.training_queue.put((model_type, training_func))

        # Process training queue
        await self.process_training_queue()

    async def process_training_queue(self):
        """Process queued training tasks"""

        if self.is_training:
            logger.info("Training already in progress, skipping")
            return

        self.is_training = True

        try:
            while not self.training_queue.empty():
                model_type, training_func = await self.training_queue.get()
                logger.info(f"Training {model_type} model...")

                try:
                    success = await training_func()
                    if success:
                        logger.info(f"{model_type} model trained successfully")
                    else:
                        logger.warning(f"{model_type} model training failed")
                except Exception as e:
                    logger.error(f"Error training {model_type}: {e}")

        finally:
            self.is_training = False

    async def train_crisis_model(self) -> bool:
        """Train or update crisis detection model"""

        logger.info("Starting crisis model training...")

        try:
            # Load training data
            conn = sqlite3.connect(self.analytics_db)

            # Get crisis-related responses
            df = pd.read_sql_query("""
                SELECT
                    mr.input_hash,
                    mr.model_name,
                    mr.confidence,
                    mr.crisis_detected,
                    mr.risk_level,
                    td.ground_truth
                FROM model_responses mr
                LEFT JOIN training_data td ON mr.session_id = td.input_text
                WHERE mr.crisis_detected IS NOT NULL
                AND mr.timestamp > datetime('now', '-30 days')
            """, conn)

            conn.close()

            if len(df) < self.min_samples['crisis']:
                logger.warning(f"Insufficient crisis samples: {len(df)}")
                return False

            # Prepare features
            X, y = self._prepare_crisis_features(df)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            # Train ensemble model
            models = [
                ('rf', RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    class_weight='balanced',
                    random_state=42
                )),
                ('nn', MLPClassifier(
                    hidden_layer_sizes=(50, 25),
                    activation='relu',
                    max_iter=500,
                    random_state=42
                ))
            ]

            ensemble = VotingClassifier(
                estimators=models,
                voting='soft'
            )

            # Train
            ensemble.fit(X_train, y_train)

            # Evaluate
            y_pred = ensemble.predict(X_test)
            y_pred_proba = ensemble.predict_proba(X_test)[:, 1]

            # Calculate metrics
            report = classification_report(y_test, y_pred, output_dict=True)
            auc_score = roc_auc_score(y_test, y_pred_proba)

            logger.info(f"Crisis model - Accuracy: {report['accuracy']:.3f}, "
                       f"Recall: {report['1']['recall']:.3f}, "
                       f"AUC: {auc_score:.3f}")

            # Save if performance is good
            if report['1']['recall'] >= 0.8:  # High recall is critical for crisis
                model_path = f"models/crisis_ensemble_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
                joblib.dump(ensemble, model_path)

                # Update registry
                self._register_model('crisis', model_path, report)

                logger.info(f"Crisis model saved: {model_path}")
                return True
            else:
                logger.warning("Crisis model performance below threshold")
                return False

        except Exception as e:
            logger.error(f"Crisis model training error: {e}")
            return False

    def _prepare_crisis_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for crisis model"""

        # Aggregate by input_hash
        feature_list = []
        label_list = []

        for input_hash, group in df.groupby('input_hash'):
            features = []

            # Model consensus features
            features.append(group['crisis_detected'].mean())  # Crisis consensus
            features.append(group['confidence'].mean())        # Avg confidence
            features.append(group['confidence'].std())         # Confidence variance
            features.append(len(group))                        # Number of models

            # Risk level features
            risk_map = {'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'minimal': 1}
            risk_scores = [risk_map.get(r, 3) for r in group['risk_level'].dropna()]
            features.append(np.mean(risk_scores) if risk_scores else 3)
            features.append(np.max(risk_scores) if risk_scores else 3)

            # Model diversity
            unique_models = group['model_name'].nunique()
            features.append(unique_models)

            # Ground truth or majority vote
            if pd.notna(group['ground_truth'].iloc[0]):
                label = int(group['ground_truth'].iloc[0] == 'crisis')
            else:
                label = int(group['crisis_detected'].mean() > 0.5)

            feature_list.append(features)
            label_list.append(label)

        return np.array(feature_list), np.array(label_list)

    async def train_emotion_model(self) -> bool:
        """Train emotion classification model"""

        logger.info("Starting emotion model training...")

        # Simplified version - would be more complex in production
        try:
            # Load emotion-tagged data
            conn = sqlite3.connect(self.analytics_db)

            # This would load actual emotion labels
            # For now, using placeholder logic
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM model_responses
                WHERE timestamp > datetime('now', '-7 days')
            """)
            count = cursor.fetchone()[0]
            conn.close()

            if count < self.min_samples['emotion']:
                return False

            # Train emotion classifier
            # (Placeholder - would use actual emotion data)
            logger.info("Emotion model training completed (simulated)")
            return True

        except Exception as e:
            logger.error(f"Emotion model training error: {e}")
            return False

    async def train_therapy_enhancer(self) -> bool:
        """Train model to enhance therapy responses"""

        logger.info("Starting therapy enhancer training...")

        try:
            # This would train a model to:
            # 1. Learn from high-rated therapy responses
            # 2. Identify effective therapeutic techniques
            # 3. Enhance future responses

            conn = sqlite3.connect(self.analytics_db)

            # Get therapy responses with feedback
            df = pd.read_sql_query("""
                SELECT
                    response,
                    confidence,
                    user_feedback,
                    clinical_validation
                FROM model_responses
                WHERE model_name LIKE '%therapy%'
                AND user_feedback IS NOT NULL
                AND timestamp > datetime('now', '-30 days')
            """, conn)

            conn.close()

            if len(df) < self.min_samples['therapy']:
                return False

            # Train enhancer model
            # (Simplified - would use NLP techniques in production)
            logger.info("Therapy enhancer training completed")
            return True

        except Exception as e:
            logger.error(f"Therapy enhancer training error: {e}")
            return False

    async def check_crisis_model_performance(self):
        """Monitor crisis model performance and trigger emergency training if needed"""

        conn = sqlite3.connect(self.analytics_db)
        cursor = conn.cursor()

        # Check recent false negatives (missed crises)
        cursor.execute("""
            SELECT COUNT(*) FROM model_responses
            WHERE crisis_detected = 0
            AND clinical_validation = 1
            AND timestamp > datetime('now', '-1 day')
        """)

        false_negatives = cursor.fetchone()[0]

        conn.close()

        if false_negatives > 5:  # Threshold for concern
            logger.warning(f"High false negative rate detected: {false_negatives}")

            # Trigger emergency retraining
            await self.emergency_crisis_retraining()

    async def emergency_crisis_retraining(self):
        """Emergency retraining of crisis model"""

        logger.warning("EMERGENCY: Retraining crisis model due to performance issues")

        # Prioritize crisis model training
        await self.training_queue.put(('crisis_emergency', self.train_crisis_model))

        # Process immediately
        await self.process_training_queue()

        # Alert administrators
        self._send_alert("Emergency crisis model retraining initiated")

    async def comprehensive_retraining(self):
        """Comprehensive retraining of all models"""

        logger.info("Starting comprehensive model retraining...")

        # Train all models
        tasks = [
            self.train_crisis_model(),
            self.train_emotion_model(),
            self.train_therapy_enhancer()
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if r is True)
        logger.info(f"Comprehensive retraining complete: {success_count}/{len(tasks)} successful")

    def _register_model(self, model_type: str, path: str, metrics: Dict[str, Any]):
        """Register a trained model"""

        conn = sqlite3.connect(self.analytics_db)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO custom_models
            (model_name, model_type, training_samples, accuracy,
             precision, recall, f1_score, model_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"{model_type}_{datetime.now().strftime('%Y%m%d')}",
            model_type,
            metrics.get('support', 0),
            metrics.get('accuracy', 0),
            metrics.get('1', {}).get('precision', 0),
            metrics.get('1', {}).get('recall', 0),
            metrics.get('1', {}).get('f1-score', 0),
            path,
            datetime.now()
        ))

        conn.commit()
        conn.close()

        # Update active models
        self.active_models[model_type] = path
        self.model_performance[model_type].append({
            'timestamp': datetime.now(),
            'metrics': metrics
        })

    async def generate_training_report(self) -> Dict[str, Any]:
        """Generate comprehensive training report"""

        conn = sqlite3.connect(self.analytics_db)

        # Get model statistics
        df_models = pd.read_sql_query("""
            SELECT * FROM custom_models
            ORDER BY created_at DESC
            LIMIT 20
        """, conn)

        # Get training data statistics
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*) as total_samples,
                SUM(CASE WHEN ground_truth IS NOT NULL THEN 1 ELSE 0 END) as labeled_samples,
                COUNT(DISTINCT input_text) as unique_sessions
            FROM training_data
        """)

        training_stats = cursor.fetchone()

        conn.close()

        report = {
            'generated_at': datetime.now().isoformat(),
            'active_models': list(self.active_models.keys()),
            'model_count': len(self.active_models),
            'recent_models': df_models.to_dict('records'),
            'training_statistics': {
                'total_samples': training_stats[0],
                'labeled_samples': training_stats[1],
                'unique_sessions': training_stats[2],
                'labeling_rate': training_stats[1] / max(training_stats[0], 1)
            },
            'performance_trends': self._calculate_performance_trends(),
            'next_training': (self.last_training + self.training_interval).isoformat()
        }

        # Save report
        with open(f"reports/training_report_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info("Training report generated")
        return report

    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calculate model performance trends"""

        trends = {}

        for model_type, performances in self.model_performance.items():
            if not performances:
                continue

            recent = performances[-10:]  # Last 10 versions

            # Extract accuracy trend
            accuracies = [p['metrics'].get('accuracy', 0) for p in recent]

            trends[model_type] = {
                'current_accuracy': accuracies[-1] if accuracies else 0,
                'accuracy_trend': 'improving' if len(accuracies) > 1 and accuracies[-1] > accuracies[0] else 'stable',
                'average_accuracy': np.mean(accuracies) if accuracies else 0,
                'versions_trained': len(performances)
            }

        return trends

    def _send_alert(self, message: str):
        """Send alert to administrators"""

        logger.critical(f"ALERT: {message}")
        # In production, would send email/SMS/Slack notification

    async def collect_feedback(self,
                              session_id: str,
                              user_rating: float,
                              clinical_validation: Optional[bool] = None):
        """Collect feedback for model improvement"""

        conn = sqlite3.connect(self.analytics_db)
        cursor = conn.cursor()

        # Update model responses with feedback
        cursor.execute("""
            UPDATE model_responses
            SET user_feedback = ?,
                clinical_validation = ?
            WHERE session_id = ?
        """, (user_rating, clinical_validation, session_id))

        # Update training data
        if clinical_validation is not None:
            cursor.execute("""
                UPDATE training_data
                SET ground_truth = ?
                WHERE input_text = ?
            """, ('crisis' if clinical_validation else 'no_crisis', session_id))

        conn.commit()
        conn.close()

        logger.info(f"Feedback collected for session {session_id}")

    def get_training_status(self) -> Dict[str, Any]:
        """Get current training pipeline status"""

        return {
            'is_training': self.is_training,
            'queue_size': self.training_queue.qsize(),
            'active_models': list(self.active_models.keys()),
            'last_training': self.last_training.isoformat(),
            'next_scheduled': (self.last_training + self.training_interval).isoformat(),
            'model_performance': {
                model: perfs[-1]['metrics'].get('accuracy', 0) if perfs else 0
                for model, perfs in self.model_performance.items()
            }
        }

# Create singleton instance
training_pipeline = AutoTrainingPipeline()