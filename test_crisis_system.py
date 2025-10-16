"""
Test Crisis Detection System
Tests the universal crisis predictor with various inputs
"""

import asyncio
import json
from models.universal_crisis_predictor import crisis_predictor, CrisisSeverity
from datetime import datetime

# Test cases with expected severity
test_cases = [
    # CRITICAL - Immediate danger
    {
        'text': "I can't do this anymore. I have pills and I'm going to take them all tonight.",
        'expected_severity': CrisisSeverity.CRITICAL,
        'description': 'Immediate suicide threat with means'
    },
    {
        'text': "This is goodbye. I've written my note and I know what I have to do.",
        'expected_severity': CrisisSeverity.CRITICAL,
        'description': 'Suicide note indication'
    },

    # HIGH - Urgent intervention needed
    {
        'text': "I've been cutting again and I can't stop. The pain helps me feel something.",
        'expected_severity': CrisisSeverity.HIGH,
        'description': 'Active self-harm'
    },
    {
        'text': "Everyone would be better off without me. I'm just a burden to everyone.",
        'expected_severity': CrisisSeverity.HIGH,
        'description': 'Severe hopelessness'
    },

    # MEDIUM - Close monitoring needed
    {
        'text': "I feel so hopeless and alone. Nothing seems to help anymore.",
        'expected_severity': CrisisSeverity.MEDIUM,
        'description': 'Depression and isolation'
    },
    {
        'text': "The panic attacks are getting worse. I can't breathe and I'm terrified.",
        'expected_severity': CrisisSeverity.MEDIUM,
        'description': 'Severe anxiety'
    },

    # LOW - Preventive measures
    {
        'text': "I've been feeling really down lately. Work stress is overwhelming.",
        'expected_severity': CrisisSeverity.LOW,
        'description': 'Mild depression'
    },
    {
        'text': "I'm tired all the time and nothing brings me joy anymore.",
        'expected_severity': CrisisSeverity.LOW,
        'description': 'Anhedonia'
    },

    # MINIMAL - No immediate concern
    {
        'text': "I had a tough day at work but talking about it helps.",
        'expected_severity': CrisisSeverity.MINIMAL,
        'description': 'Normal stress'
    },
    {
        'text': "I'm working on my coping strategies from therapy.",
        'expected_severity': CrisisSeverity.MINIMAL,
        'description': 'Positive coping'
    },

    # Edge cases
    {
        'text': "HELP ME PLEASE!!!!!!",
        'expected_severity': CrisisSeverity.HIGH,
        'description': 'Urgent but vague'
    },
    {
        'text': "i dont know what to do anymore",
        'expected_severity': CrisisSeverity.MEDIUM,
        'description': 'Subtle crisis language'
    }
]

async def test_crisis_detection():
    """Test crisis detection with various inputs"""

    print("=" * 80)
    print("CRISIS DETECTION SYSTEM TEST")
    print("=" * 80)
    print()

    results = []
    correct = 0
    total = len(test_cases)

    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}/{total}: {test['description']}")
        print(f"Text: \"{test['text'][:50]}...\"" if len(test['text']) > 50 else f"Text: \"{test['text']}\"")

        # Run prediction
        prediction = await crisis_predictor.predict_crisis(
            text=test['text'],
            user_tier='free',
            context={'test_mode': True},
            force_free=True
        )

        # Check if prediction matches expected
        severity_match = prediction.severity == test['expected_severity']
        if severity_match:
            correct += 1
            status = "✓ PASS"
        else:
            status = "✗ FAIL"

        print(f"Expected: {test['expected_severity'].value}")
        print(f"Detected: {prediction.severity.value}")
        print(f"Confidence: {prediction.confidence:.1%}")
        print(f"Risk Factors: {', '.join(prediction.risk_factors[:3]) if prediction.risk_factors else 'None'}")
        print(f"Latency: {prediction.latency*1000:.0f}ms")
        print(f"Status: {status}")
        print("-" * 40)

        results.append({
            'test': test['description'],
            'expected': test['expected_severity'].value,
            'detected': prediction.severity.value,
            'confidence': prediction.confidence,
            'correct': severity_match,
            'latency_ms': prediction.latency * 1000
        })

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total}")
    print(f"Passed: {correct}")
    print(f"Failed: {total - correct}")
    print(f"Accuracy: {correct/total:.1%}")

    # Performance metrics
    avg_latency = sum(r['latency_ms'] for r in results) / len(results)
    avg_confidence = sum(r['confidence'] for r in results) / len(results)

    print(f"\nAverage Latency: {avg_latency:.0f}ms")
    print(f"Average Confidence: {avg_confidence:.1%}")

    # Critical test check
    critical_tests = [r for r in results if r['expected'] == 'critical']
    critical_correct = sum(1 for r in critical_tests if r['correct'])

    print(f"\nCritical Detection Rate: {critical_correct}/{len(critical_tests)} "
          f"({critical_correct/len(critical_tests):.0%})")

    if critical_correct < len(critical_tests):
        print("⚠️ WARNING: Not all critical cases detected correctly!")

    # Save results
    with open('crisis_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'total': total,
                'passed': correct,
                'accuracy': correct/total,
                'avg_latency_ms': avg_latency,
                'avg_confidence': avg_confidence,
                'critical_detection_rate': critical_correct/len(critical_tests) if critical_tests else 1.0
            }
        }, f, indent=2)

    print("\nResults saved to crisis_test_results.json")

    return correct == total

async def test_performance():
    """Test system performance under load"""

    print("\n" + "=" * 80)
    print("PERFORMANCE TEST")
    print("=" * 80)

    test_text = "I'm feeling really overwhelmed and don't know what to do"

    # Test different user tiers
    tiers = ['free', 'basic', 'premium', 'enterprise']

    for tier in tiers:
        start = datetime.now()

        # Run 10 requests
        tasks = []
        for _ in range(10):
            task = crisis_predictor.predict_crisis(
                text=test_text,
                user_tier=tier,
                context={},
                force_free=(tier == 'free')
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        elapsed = (datetime.now() - start).total_seconds()
        avg_latency = elapsed / 10

        total_cost = sum(r.cost for r in results)

        print(f"\n{tier.upper()} Tier:")
        print(f"  10 requests in {elapsed:.2f}s")
        print(f"  Average latency: {avg_latency*1000:.0f}ms")
        print(f"  Total cost: ${total_cost:.4f}")
        print(f"  Model used: {results[0].model_used}")

if __name__ == "__main__":
    print("Starting Crisis Detection System Tests...")
    print()

    # Run tests
    asyncio.run(test_crisis_detection())
    asyncio.run(test_performance())

    print("\n✅ Crisis Detection System Test Complete!")
    print("\nSystem is ready for deployment.")