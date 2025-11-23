import requests
import pandas as pd

def test_model_accuracy():
    """Test model accuracy dengan test cases yang known"""
    
    BASE_URL = "http://127.0.0.1:5000/api/v1"
    
    # Test cases dengan expected categories
    test_cases = [
        {"description": "Makan siang di warteg", "expected": "Makanan"},
        {"description": "Isi bensin pertamax", "expected": "Transportasi"},
        {"description": "Belanja di supermarket", "expected": "Belanja"},
        {"description": "Nonton film di bioskop", "expected": "Hiburan"},
        {"description": "Beli obat di apotik", "expected": "Kesehatan"},
        {"description": "Transfer bank", "expected": "Lainnya"},
        {"description": "Bayar listrik", "expected": "Lainnya"},
        {"description": "Gojek ke mall", "expected": "Transportasi"},
        {"description": "Beli baju", "expected": "Belanja"},
        {"description": "Main game online", "expected": "Hiburan"},
    ]
    
    print("🧪 Testing Model Accuracy...\n")
    
    correct = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        response = requests.post(
            f"{BASE_URL}/ai/categorize",
            json={"description": test_case["description"], "amount": 0},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()['data']
            predicted = result['predicted_category']
            confidence = result['confidence']
            expected = test_case["expected"]
            
            is_correct = predicted == expected
            status = "✅" if is_correct else "❌"
            
            if is_correct:
                correct += 1
            
            print(f"{status} '{test_case['description']}'")
            print(f"   Expected: {expected}")
            print(f"   Predicted: {predicted} ({confidence:.1%})")
            print(f"   Model: {result['model_version']}\n")
        else:
            print(f"❌ Failed: {test_case['description']}")
            print(f"   Error: {response.text}\n")
    
    accuracy = correct / total
    print(f"🎯 Accuracy: {correct}/{total} ({accuracy:.1%})")
    
    if accuracy > 0.7:
        print("🚀 Excellent accuracy!")
    elif accuracy > 0.5:
        print("👍 Good accuracy!")
    else:
        print("💪 Keep training with more data!")

if __name__ == "__main__":
    test_model_accuracy()