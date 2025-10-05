"""
Custom AI Model Builder for MindMend Platform
Allows admins to create, train, and deploy custom AI models for therapy
"""
import os
import json
import pickle
import logging
from datetime import datetime
from typing import Dict, List, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score
import openai

from models.database import db

class CustomAIModel(db.Model):
    """Database model for custom AI models"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    model_type = db.Column(db.String(50), nullable=False)  # classification, regression, generation
    algorithm = db.Column(db.String(50), nullable=False)   # naive_bayes, svm, neural_network, etc.
    training_data_size = db.Column(db.Integer)
    accuracy_score = db.Column(db.Float)
    validation_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='training')  # training, ready, deployed, error
    model_file_path = db.Column(db.String(200))
    vectorizer_file_path = db.Column(db.String(200))
    training_parameters = db.Column(db.Text)  # JSON string
    training_history = db.Column(db.Text)     # JSON string
    created_by = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_trained = db.Column(db.DateTime)
    deployment_count = db.Column(db.Integer, default=0)
    prediction_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<CustomAIModel {self.name}>'

class TrainingDataset(db.Model):
    """Database model for training datasets"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    data_type = db.Column(db.String(50))  # text, tabular, image, audio
    file_path = db.Column(db.String(200))
    size = db.Column(db.Integer)  # number of records
    columns = db.Column(db.Text)  # JSON string of column names
    target_column = db.Column(db.String(100))
    preprocessing_steps = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100))

    def __repr__(self):
        return f'<TrainingDataset {self.name}>'

class CustomAIBuilder:
    """Main class for building custom AI models"""

    def __init__(self):
        self.model_storage_path = './data/custom_models'
        self.dataset_storage_path = './data/datasets'
        os.makedirs(self.model_storage_path, exist_ok=True)
        os.makedirs(self.dataset_storage_path, exist_ok=True)

        # Available algorithms
        self.algorithms = {
            'naive_bayes': {
                'class': MultinomialNB,
                'name': 'Naive Bayes',
                'description': 'Fast and effective for text classification',
                'params': {'alpha': [0.1, 0.5, 1.0]}
            },
            'svm': {
                'class': SVC,
                'name': 'Support Vector Machine',
                'description': 'Powerful for high-dimensional data',
                'params': {'C': [0.1, 1.0, 10.0], 'kernel': ['linear', 'rbf']}
            },
            'random_forest': {
                'class': RandomForestClassifier,
                'name': 'Random Forest',
                'description': 'Robust ensemble method',
                'params': {'n_estimators': [50, 100, 200], 'max_depth': [10, 20, None]}
            },
            'logistic_regression': {
                'class': LogisticRegression,
                'name': 'Logistic Regression',
                'description': 'Simple and interpretable',
                'params': {'C': [0.1, 1.0, 10.0], 'max_iter': [1000]}
            },
            'neural_network': {
                'class': MLPClassifier,
                'name': 'Neural Network',
                'description': 'Deep learning for complex patterns',
                'params': {'hidden_layer_sizes': [(50,), (100,), (50, 50)], 'activation': ['relu', 'tanh']}
            }
        }

    def create_model(self, model_config: Dict) -> CustomAIModel:
        """Create a new custom AI model"""
        try:
            model = CustomAIModel(
                name=model_config['name'],
                description=model_config.get('description', ''),
                model_type=model_config['model_type'],
                algorithm=model_config['algorithm'],
                training_parameters=json.dumps(model_config.get('parameters', {})),
                created_by=model_config.get('created_by', 'admin'),
                status='created'
            )

            db.session.add(model)
            db.session.commit()

            return model

        except Exception as e:
            logging.error(f"Error creating model: {e}")
            raise e

    def upload_dataset(self, dataset_config: Dict, file_content: str) -> TrainingDataset:
        """Upload and process training dataset"""
        try:
            # Save dataset file
            filename = f"dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = os.path.join(self.dataset_storage_path, filename)

            with open(file_path, 'w') as f:
                f.write(file_content)

            # Parse dataset to get metadata
            data = json.loads(file_content)

            dataset = TrainingDataset(
                name=dataset_config['name'],
                description=dataset_config.get('description', ''),
                data_type=dataset_config.get('data_type', 'text'),
                file_path=file_path,
                size=len(data) if isinstance(data, list) else len(data.get('records', [])),
                columns=json.dumps(list(data[0].keys()) if isinstance(data, list) and data else []),
                target_column=dataset_config.get('target_column'),
                created_by=dataset_config.get('created_by', 'admin')
            )

            db.session.add(dataset)
            db.session.commit()

            return dataset

        except Exception as e:
            logging.error(f"Error uploading dataset: {e}")
            raise e

    def train_model(self, model_id: int, dataset_id: int, training_config: Dict = None) -> Dict:
        """Train a custom AI model"""
        try:
            model = CustomAIModel.query.get(model_id)
            dataset = TrainingDataset.query.get(dataset_id)

            if not model or not dataset:
                raise ValueError("Model or dataset not found")

            # Update model status
            model.status = 'training'
            db.session.commit()

            # Load dataset
            with open(dataset.file_path, 'r') as f:
                data = json.load(f)

            # Prepare training data based on model type
            if model.model_type == 'classification':
                X, y = self._prepare_classification_data(data, dataset.target_column)
            elif model.model_type == 'regression':
                X, y = self._prepare_regression_data(data, dataset.target_column)
            else:
                raise ValueError(f"Unsupported model type: {model.model_type}")

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y if model.model_type == 'classification' else None
            )

            # Vectorize text data if needed
            vectorizer = None
            if isinstance(X_train[0], str):
                vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
                X_train = vectorizer.fit_transform(X_train)
                X_test = vectorizer.transform(X_test)

            # Get algorithm class and parameters
            algorithm_info = self.algorithms[model.algorithm]
            algorithm_class = algorithm_info['class']

            # Use provided parameters or defaults
            if training_config and 'parameters' in training_config:
                params = training_config['parameters']
            else:
                params = {}

            # Train model
            trained_model = algorithm_class(**params)
            trained_model.fit(X_train, y_train)

            # Evaluate model
            train_accuracy = trained_model.score(X_train, y_train)
            test_accuracy = trained_model.score(X_test, y_test)

            # Cross-validation
            cv_scores = cross_val_score(trained_model, X_train, y_train, cv=5)

            # Generate classification report
            y_pred = trained_model.predict(X_test)
            report = classification_report(y_test, y_pred, output_dict=True)

            # Save model and vectorizer
            model_filename = f"model_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            model_path = os.path.join(self.model_storage_path, model_filename)

            with open(model_path, 'wb') as f:
                pickle.dump(trained_model, f)

            if vectorizer:
                vectorizer_filename = f"vectorizer_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
                vectorizer_path = os.path.join(self.model_storage_path, vectorizer_filename)
                with open(vectorizer_path, 'wb') as f:
                    pickle.dump(vectorizer, f)
                model.vectorizer_file_path = vectorizer_path

            # Update model record
            model.model_file_path = model_path
            model.training_data_size = len(X_train)
            model.accuracy_score = test_accuracy
            model.validation_score = cv_scores.mean()
            model.status = 'ready'
            model.last_trained = datetime.utcnow()

            training_history = {
                'train_accuracy': train_accuracy,
                'test_accuracy': test_accuracy,
                'cv_scores': cv_scores.tolist(),
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'classification_report': report,
                'training_date': datetime.utcnow().isoformat(),
                'dataset_size': len(data),
                'parameters': params
            }

            model.training_history = json.dumps(training_history)
            db.session.commit()

            return {
                'success': True,
                'model_id': model_id,
                'accuracy': test_accuracy,
                'cv_score': cv_scores.mean(),
                'training_history': training_history
            }

        except Exception as e:
            # Update model status to error
            if 'model' in locals():
                model.status = 'error'
                db.session.commit()

            logging.error(f"Error training model: {e}")
            raise e

    def _prepare_classification_data(self, data: List[Dict], target_column: str):
        """Prepare data for classification"""
        if isinstance(data, list):
            X = [item.get('text', str(item)) for item in data]
            y = [item.get(target_column) for item in data]
        else:
            X = data.get('texts', [])
            y = data.get('labels', [])

        return X, y

    def _prepare_regression_data(self, data: List[Dict], target_column: str):
        """Prepare data for regression"""
        if isinstance(data, list):
            X = [item.get('text', str(item)) for item in data]
            y = [float(item.get(target_column, 0)) for item in data]
        else:
            X = data.get('texts', [])
            y = [float(val) for val in data.get('values', [])]

        return X, y

    def deploy_model(self, model_id: int) -> Dict:
        """Deploy a trained model for use"""
        try:
            model = CustomAIModel.query.get(model_id)
            if not model or model.status != 'ready':
                raise ValueError("Model not ready for deployment")

            model.status = 'deployed'
            model.deployment_count += 1
            db.session.commit()

            return {
                'success': True,
                'model_id': model_id,
                'deployment_count': model.deployment_count
            }

        except Exception as e:
            logging.error(f"Error deploying model: {e}")
            raise e

    def predict(self, model_id: int, input_data: str) -> Dict:
        """Make prediction using deployed model"""
        try:
            model = CustomAIModel.query.get(model_id)
            if not model or model.status != 'deployed':
                raise ValueError("Model not deployed or not found")

            # Load trained model
            with open(model.model_file_path, 'rb') as f:
                trained_model = pickle.load(f)

            # Load vectorizer if exists
            vectorizer = None
            if model.vectorizer_file_path and os.path.exists(model.vectorizer_file_path):
                with open(model.vectorizer_file_path, 'rb') as f:
                    vectorizer = pickle.load(f)

            # Prepare input
            if vectorizer:
                X = vectorizer.transform([input_data])
            else:
                X = [input_data]

            # Make prediction
            prediction = trained_model.predict(X)

            # Get prediction probability if available
            prob = None
            if hasattr(trained_model, 'predict_proba'):
                prob = trained_model.predict_proba(X).max()

            # Update prediction count
            model.prediction_count += 1
            db.session.commit()

            return {
                'success': True,
                'prediction': prediction[0] if isinstance(prediction, np.ndarray) else prediction,
                'confidence': prob,
                'model_name': model.name
            }

        except Exception as e:
            logging.error(f"Error making prediction: {e}")
            raise e

    def get_model_performance(self, model_id: int) -> Dict:
        """Get detailed performance metrics for a model"""
        try:
            model = CustomAIModel.query.get(model_id)
            if not model:
                raise ValueError("Model not found")

            training_history = json.loads(model.training_history) if model.training_history else {}

            return {
                'model_id': model_id,
                'name': model.name,
                'algorithm': model.algorithm,
                'accuracy': model.accuracy_score,
                'validation_score': model.validation_score,
                'training_data_size': model.training_data_size,
                'prediction_count': model.prediction_count,
                'deployment_count': model.deployment_count,
                'status': model.status,
                'created_at': model.created_at.isoformat(),
                'last_trained': model.last_trained.isoformat() if model.last_trained else None,
                'training_history': training_history
            }

        except Exception as e:
            logging.error(f"Error getting model performance: {e}")
            raise e

    def list_models(self) -> List[Dict]:
        """List all custom models"""
        models = CustomAIModel.query.all()
        return [
            {
                'id': model.id,
                'name': model.name,
                'description': model.description,
                'algorithm': model.algorithm,
                'status': model.status,
                'accuracy': model.accuracy_score,
                'created_at': model.created_at.isoformat(),
                'prediction_count': model.prediction_count
            }
            for model in models
        ]

    def list_datasets(self) -> List[Dict]:
        """List all training datasets"""
        datasets = TrainingDataset.query.all()
        return [
            {
                'id': dataset.id,
                'name': dataset.name,
                'description': dataset.description,
                'size': dataset.size,
                'data_type': dataset.data_type,
                'created_at': dataset.created_at.isoformat()
            }
            for dataset in datasets
        ]

    def delete_model(self, model_id: int) -> bool:
        """Delete a custom model"""
        try:
            model = CustomAIModel.query.get(model_id)
            if not model:
                return False

            # Delete model files
            if model.model_file_path and os.path.exists(model.model_file_path):
                os.remove(model.model_file_path)

            if model.vectorizer_file_path and os.path.exists(model.vectorizer_file_path):
                os.remove(model.vectorizer_file_path)

            # Delete database record
            db.session.delete(model)
            db.session.commit()

            return True

        except Exception as e:
            logging.error(f"Error deleting model: {e}")
            return False

    def generate_therapy_dataset_template(self) -> str:
        """Generate a template for therapy-specific training data"""
        template = [
            {
                "text": "I feel anxious about my upcoming job interview",
                "category": "anxiety",
                "severity": "moderate",
                "recommended_intervention": "breathing_exercise"
            },
            {
                "text": "I've been feeling depressed and unmotivated lately",
                "category": "depression",
                "severity": "high",
                "recommended_intervention": "cognitive_restructuring"
            },
            {
                "text": "I'm having trouble sleeping and feel stressed",
                "category": "stress",
                "severity": "moderate",
                "recommended_intervention": "relaxation_technique"
            },
            {
                "text": "I feel happy and accomplished today",
                "category": "positive",
                "severity": "low",
                "recommended_intervention": "positive_reinforcement"
            }
        ]

        return json.dumps(template, indent=2)

# Initialize global custom AI builder
custom_ai_builder = CustomAIBuilder()