#!/usr/bin/env python3
"""
Create Demo ML Models for MindMend AI System
===========================================
This script creates demonstration ML models with synthetic data
for the AI model testing system.
"""

import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

def create_demo_models():
    """Create demo ML models for mental health assessment"""

    # Ensure directory exists
    os.makedirs('models/ml', exist_ok=True)

    # Set random seed for reproducibility
    np.random.seed(42)

    # Create synthetic training data
    n_samples = 2000
    n_features = 12

    # Generate base features (normalized scores from assessments)
    X = np.random.rand(n_samples, n_features)

    models_to_create = [
        {
            'name': 'anxiety_rf',
            'model': RandomForestClassifier(n_estimators=100, random_state=42),
            'target_generator': lambda x: np.where(x[:, 2] + x[:, 9] > 1.2,
                                                  np.minimum(((x[:, 2] + x[:, 9]) * 2).astype(int), 3),
                                                  0),
            'scaler_needed': False
        },
        {
            'name': 'depression_gb',
            'model': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'target_generator': lambda x: np.minimum(
                ((x[:, 3] + x[:, 4] + x[:, 7]) * 1.5).astype(int), 4
            ),
            'scaler_needed': False
        },
        {
            'name': 'ptsd_nn',
            'model': MLPClassifier(hidden_layer_sizes=(50, 25), random_state=42, max_iter=1000),
            'target_generator': lambda x: np.where(
                x[:, 5] + x[:, 8] + x[:, 10] > 1.8,
                np.minimum(((x[:, 5] + x[:, 8]) * 1.2).astype(int), 2),
                0
            ),
            'scaler_needed': True
        },
        {
            'name': 'bipolar_svm',
            'model': SVC(kernel='rbf', probability=True, random_state=42),
            'target_generator': lambda x: np.where(
                (x[:, 1] > 0.7) & (x[:, 6] < 0.3), 1, 0
            ),
            'scaler_needed': True
        },
        {
            'name': 'suicide_risk_nn',
            'model': MLPClassifier(hidden_layer_sizes=(100, 50, 25), random_state=42, max_iter=1000),
            'target_generator': lambda x: np.where(
                (x[:, 3] > 0.8) & (x[:, 5] > 0.7) & (x[:, 11] > 0.6),
                2,  # High risk
                np.where((x[:, 3] > 0.6) | (x[:, 5] > 0.5), 1, 0)  # Medium/Low risk
            ),
            'scaler_needed': True
        }
    ]

    print("Creating demonstration ML models...")

    for model_info in models_to_create:
        print(f"Creating {model_info['name']}...")

        # Generate target based on features
        y = model_info['target_generator'](X)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale if needed
        if model_info['scaler_needed']:
            scaler = StandardScaler()
            X_train_processed = scaler.fit_transform(X_train)
            X_test_processed = scaler.transform(X_test)

            # Save scaler
            scaler_path = f"models/ml/{model_info['name']}_scaler.pkl"
            joblib.dump(scaler, scaler_path)
        else:
            X_train_processed = X_train
            X_test_processed = X_test

        # Train model
        model = model_info['model']
        model.fit(X_train_processed, y_train)

        # Evaluate
        train_accuracy = model.score(X_train_processed, y_train)
        test_accuracy = model.score(X_test_processed, y_test)

        print(f"  Train accuracy: {train_accuracy:.3f}")
        print(f"  Test accuracy: {test_accuracy:.3f}")

        # Save model
        model_path = f"models/ml/{model_info['name']}.pkl"
        joblib.dump(model, model_path)

        print(f"  Saved to {model_path}")

    print("\n✅ All demo ML models created successfully!")
    print("\nModels created:")
    for model_info in models_to_create:
        print(f"  - {model_info['name']}.pkl")

    print("\nThese models are now available in the AI Model Manager for testing!")

if __name__ == '__main__':
    create_demo_models()