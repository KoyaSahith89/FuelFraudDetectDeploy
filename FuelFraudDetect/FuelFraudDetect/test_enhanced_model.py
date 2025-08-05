#!/usr/bin/env python3
"""
Test script to validate the enhanced fraud detection model
"""

from enhanced_predictor import enhanced_predictor
import sys

def test_fraud_scenarios():
    """Test various fraud scenarios to validate model accuracy"""
    
    print("🔍 Testing Enhanced Fraud Detection Model")
    print("=" * 50)
    
    # Test cases: [fuel_qty, rate, amount, pump_id, emp_id, expected_result, description]
    test_cases = [
        # Normal transactions
        (25.5, 1.45, 36.98, 3, 101, False, "Normal transaction: 25.5L @ $1.45/L = $36.98"),
        (40.0, 1.60, 64.00, 5, 150, False, "Normal transaction: 40L @ $1.60/L = $64.00"),
        (15.2, 1.35, 20.52, 2, 120, False, "Normal transaction: 15.2L @ $1.35/L = $20.52"),
        
        # Undercharging fraud
        (50.0, 1.50, 25.00, 4, 130, True, "Undercharging: 50L @ $1.50/L charged only $25 (should be $75)"),
        (30.0, 1.70, 20.00, 7, 180, True, "Undercharging: 30L @ $1.70/L charged only $20 (should be $51)"),
        
        # Overcharging fraud
        (20.0, 1.40, 50.00, 1, 110, True, "Overcharging: 20L @ $1.40/L charged $50 (should be $28)"),
        (35.0, 1.55, 80.00, 6, 160, True, "Overcharging: 35L @ $1.55/L charged $80 (should be $54.25)"),
        
        # Rate manipulation
        (25.0, 0.80, 20.00, 3, 140, True, "Rate manipulation: Suspiciously low rate $0.80/L"),
        (30.0, 3.50, 105.00, 8, 190, True, "Rate manipulation: Suspiciously high rate $3.50/L"),
        
        # Quantity manipulation
        (2.0, 1.50, 3.00, 2, 125, True, "Quantity fraud: Suspiciously low quantity 2L"),
        (150.0, 1.60, 240.00, 9, 200, True, "Quantity fraud: Suspiciously high quantity 150L"),
    ]
    
    correct_predictions = 0
    total_tests = len(test_cases)
    
    for i, (fuel_qty, rate, amount, pump_id, emp_id, expected_fraud, description) in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {description}")
        
        is_fraud, confidence, explanation = enhanced_predictor.predict_fraud(
            fuel_qty, rate, amount, pump_id, emp_id
        )
        
        # Check if prediction matches expected result
        correct = (is_fraud == expected_fraud)
        if correct:
            correct_predictions += 1
            status = "✅ CORRECT"
        else:
            status = "❌ INCORRECT"
        
        print(f"   Expected: {'FRAUD' if expected_fraud else 'NORMAL'}")
        print(f"   Predicted: {'FRAUD' if is_fraud else 'NORMAL'} (confidence: {confidence:.3f})")
        print(f"   Status: {status}")
        print(f"   Explanation: {explanation[:100]}...")
    
    accuracy = (correct_predictions / total_tests) * 100
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS:")
    print(f"   Correct Predictions: {correct_predictions}/{total_tests}")
    print(f"   Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 80:
        print("🎉 Model performance is EXCELLENT!")
    elif accuracy >= 70:
        print("👍 Model performance is GOOD!")
    elif accuracy >= 60:
        print("⚠️  Model performance is ACCEPTABLE but could be improved")
    else:
        print("❌ Model performance needs improvement")
    
    return accuracy

def test_model_info():
    """Test model information retrieval"""
    print("\n🔧 Model Information:")
    print("-" * 30)
    
    model_info = enhanced_predictor.get_model_info()
    for key, value in model_info.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    try:
        # Test fraud detection accuracy
        accuracy = test_fraud_scenarios()
        
        # Show model information
        test_model_info()
        
        print(f"\n✨ Enhanced fraud detection model is ready!")
        print(f"   Model accuracy on test cases: {accuracy:.1f}%")
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")
        sys.exit(1)