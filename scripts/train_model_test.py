import requests
import json
import time

def test_model_training():
    """Test training the category prediction model"""
    
    BASE_URL = "http://127.0.0.1:5000/api/v1"
    
    print("🧪 Testing Model Training Pipeline...\n")
    
    # Step 1: Check model status
    print("1. Checking model status...")
    response = requests.get(f"{BASE_URL}/ai/model-status")
    if response.status_code == 200:
        status = response.json()
        print(f"   Model trained: {status['data']['is_trained']}")
        print(f"   Training ready: {status['data']['training_ready']}")
    else:
        print(f"   ❌ Error: {response.text}")
        return
    
    # Step 2: Train model
    print("\n2. Training model...")
    response = requests.post(f"{BASE_URL}/ai/train-category-model")
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'success':
            training_data = result['data']
            print(f"   ✅ Training successful!")
            print(f"   Samples: {training_data['training_samples']}")
            print(f"   Accuracy: {training_data['accuracy']:.4f}")
            print(f"   Categories: {', '.join(training_data['categories'])}")
        else:
            print(f"   ❌ Training failed: {result['message']}")
    else:
        print(f"   ❌ Error: {response.text}")
        return
    
    # Step 3: Test predictions
    print("\n3. Testing predictions...")
    
    test_cases = [
        {"description": "Makan siang di warteg", "amount": 20000},
        {"description": "Isi bensin pertamax", "amount": 50000},
        {"description": "Belanja di indomaret", "amount": 150000},
        {"description": "Nonton di cinema", "amount": 45000},
        {"description": "Beli obat batuk", "amount": 25000},
        {"description": "Transfer bank", "amount": 1000000},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        response = requests.post(
            f"{BASE_URL}/ai/categorize",
            json=test_case,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()['data']
            print(f"   {i}. '{test_case['description']}'")
            print(f"      → {result['predicted_category']} ({result['confidence']:.1%})")
            print(f"      Model: {result['model_version']}")
        else:
            print(f"   {i}. ❌ Prediction failed: {response.text}")

if __name__ == "__main__":
    test_model_training()