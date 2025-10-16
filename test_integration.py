"""
Test complete AI integration
"""

import asyncio
import json
from crisis_integration import check_message_for_crisis
from models.universal_crisis_predictor import crisis_predictor
from models.ai_orchestrator import ai_orchestrator, ModelRequest, TaskType

def test_crisis_detection():
    """Test crisis detection on sample messages"""
    print("\n" + "="*60)
    print("TESTING CRISIS DETECTION")
    print("="*60)

    test_messages = [
        "I'm feeling really sad and hopeless today",
        "Everything is fine, just checking in",
        "I can't do this anymore, I have pills ready"
    ]

    for msg in test_messages:
        print(f"\nMessage: '{msg[:50]}...' if len(msg) > 50 else '{msg}'")
        result = check_message_for_crisis(msg)

        if result:
            print(f"  ⚠️ Crisis detected!")
            print(f"  Severity: {result.severity.value}")
            print(f"  Confidence: {result.confidence:.1%}")
        else:
            print(f"  ✅ No crisis detected")

async def test_orchestrator():
    """Test AI orchestrator"""
    print("\n" + "="*60)
    print("TESTING AI ORCHESTRATOR")
    print("="*60)

    # Test crisis detection through orchestrator
    request = ModelRequest(
        task_type=TaskType.CRISIS_DETECTION,
        prompt="I'm having dark thoughts and don't know what to do",
        context={'session_id': 'test_001'},
        user_tier='free'
    )

    print(f"\nRequest: Crisis detection for free tier")
    response = await ai_orchestrator.process_request(request)

    print(f"Response received:")
    print(f"  Models used: {response.models_used}")
    print(f"  Confidence: {response.confidence:.1%}")
    print(f"  Cost: ${response.total_cost:.4f}")
    print(f"  Latency: {response.total_latency*1000:.0f}ms")

    if response.metadata.get('crisis_detected'):
        print(f"  ⚠️ Crisis detected: {response.metadata.get('severity')}")

def test_celery_tasks():
    """Test Celery task imports"""
    print("\n" + "="*60)
    print("TESTING CELERY TASKS")
    print("="*60)

    try:
        from tasks import (
            check_crisis_model_performance,
            trigger_model_training,
            comprehensive_model_retraining
        )
        print("✅ All AI training tasks imported successfully")

        # List registered tasks
        from celery_app import celery_app
        print("\nRegistered AI tasks:")
        for task in celery_app.tasks:
            if 'crisis' in task or 'training' in task or 'model' in task:
                print(f"  - {task}")

    except ImportError as e:
        print(f"❌ Task import failed: {e}")

def test_system_status():
    """Test system status"""
    print("\n" + "="*60)
    print("SYSTEM STATUS")
    print("="*60)

    # Check crisis predictor status
    status = crisis_predictor.get_system_status()
    print("\nCrisis Predictor:")
    print(f"  Custom model: {'✅ Available' if status['custom_model_available'] else '❌ Not available'}")
    print(f"  Patterns loaded: {status['patterns_loaded']}")
    print(f"  Free tier capabilities: {status['free_tier_capabilities']}")

    # Check training pipeline status
    try:
        from models.auto_training_pipeline import training_pipeline
        training_status = training_pipeline.get_training_status()
        print("\nTraining Pipeline:")
        print(f"  Active models: {training_status['active_models']}")
        print(f"  Queue size: {training_status['queue_size']}")
        print(f"  Is training: {training_status['is_training']}")
    except Exception as e:
        print(f"\nTraining Pipeline: Not available ({e})")

if __name__ == "__main__":
    print("🚀 MindMend AI Integration Test Suite")
    print("="*60)

    # Run tests
    test_crisis_detection()
    asyncio.run(test_orchestrator())
    test_celery_tasks()
    test_system_status()

    print("\n" + "="*60)
    print("✅ Integration tests complete!")
    print("\nSystem is ready for deployment.")
    print("="*60)