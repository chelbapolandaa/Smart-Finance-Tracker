# 📱 Smart Finance Tracker

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.2.2-orange.svg)](https://scikit-learn.org/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![Accuracy](https://img.shields.io/badge/accuracy-97.38%25-brightgreen.svg)](#results)

AI-powered personal finance management dengan kemampuan prediksi pengeluaran, deteksi anomali, dan kategorisasi transaksi otomatis. Dibangun dengan Machine Learning untuk memberikan insights keuangan yang cerdas.

## 🚀 Fitur Utama

- ✅ Smart Categorization - Klasifikasi otomatis transaksi menggunakan ML (85% accuracy)
- ✅ Spending Prediction - Prediksi pengeluaran bulan depan dengan confidence 70%+
- ✅ Anomaly Detection - Deteksi transaksi mencurigakan secara real-time
- ✅ Financial Health Score - Skor kesehatan keuangan personal
- ✅ REST API - Mudah diintegrasikan dengan frontend/mobile apps
- ✅ Real-time Analytics - Dashboard insights keuangan live

## 📊 Model Performance

| Model | Purpose | Algorithm | Accuracy |
|-------|----------|-----------|--------|
| Category Predictor | Transaction categorization | Random Forest | 85%+ |
| Spending Predictor | Monthly spending forecast | Linear Regression | 70%+ |
| Anomaly Detector | Fraud detection | 	Isolation Forest | 90%+ |


## ⚡ Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

1. **Clone Repository**
```
git clone https://github.com/chelbapolandaa/Smart-Finance-Tracker.git
cd Smart-Finance-Tracker
```

2. **Install Dependencies**
```
pip install -r requirements.txt
```

3. **Run Application**
```
cd api
python app.py
```

## 🚀 Menjalankan Aplikasi

### Option 1: Backend API Only
```
# Terminal 1 - Start API
python api/app.py

# API akan berjalan di http://localhost:5000
```

### Option 2: Web Interface + API
```
# Terminal 1 - Start API
python api/app.py

# Terminal 2 - Start Web Interface
streamlit run web_app/app.py

# Web interface akan berjalan di http://localhost:8501
```

## 📡 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints
**🔍 Health Check**
```
GET /health
```

**Response:**
```
{
  "status": "healthy",
  "model_loaded": true
}
```

**🤖 AI Model Status**
```
GET /ai/model-status
```

**Response:**
```
{
  "status": "success",
  "data": {
    "is_trained": true,
    "model_type": "category_predictor",
    "categories": ["Makanan", "Transportasi", "Belanja", "Hiburan"],
    "training_ready": true
  }
}
```

**🎯 Smart Categorization**
```
POST /ai/categorize
Content-Type: application/json

{
  "description": "beli makan siang di restoran",
  "amount": 75000
}
```

**Response**
```
{
  "status": "success",
  "data": {
    "description": "beli makan siang di restoran",
    "predicted_category": "Makanan",
    "confidence": 0.87,
    "model_version": "ml_model",
    "alternative_categories": [
      {"category": "Makanan", "confidence": 0.87},
      {"category": "Hiburan", "confidence": 0.08}
    ]
  }
}
```

**📈 Spending Prediction**
```
GET /ai/predict-spending
```

**Response:**
```
{
  "status": "success",
  "data": {
    "predicted_amount": 3214460,
    "confidence": 0.7,
    "currency": "IDR",
    "next_month": "2025-12"
  }
}
```

**🚨 Anomaly Detection**
```
GET /ai/detect-anomalies
```

**Response:**
```
{
  "status": "success",
  "data": {
    "anomalies": [
      {
        "date": "2024-11-15",
        "amount": 2500000,
        "category": "Belanja",
        "description": "Beli laptop baru",
        "anomaly_score": -0.8,
        "reason": "Amount 2x higher than category average"
      }
    ],
    "total_analyzed": 150,
    "anomaly_count": 3
  }
}
```

**💡 Financial Insights**
```
GET /ai/financial-insights
```

**Response:**
```
{
  "status": "success",
  "data": {
    "financial_health": {
      "savings_rate": 0.25,
      "health_score": 85,
      "recommendation": "Excellent savings rate! Consider investment options."
    },
    "spending_insights": {
      "top_spending_category": "Makanan",
      "total_income": 10000000,
      "total_expense": 7500000,
      "net_savings": 2500000
    }
  }
}
```

## 🖥️ Web Interface

Web dashboard menyediakan:

- 📊 Financial Overview - Ringkasan keuangan real-time
- 🤖 AI Insights - Prediksi dan analisis cerdas
- 🚨 Anomaly Alerts - Notifikasi transaksi mencurigakan
- 📈 Spending Trends - Visualisasi pola pengeluaran

## 🛠️ Development

### Training Model
```
from src.models.category_predictor import CategoryPredictor

# Train category model
predictor = CategoryPredictor()
accuracy = predictor.train(transactions_df)
print(f"Model accuracy: {accuracy:.2f}")

# Save model
predictor.save_model("models/category_model")
```

### Using AI Categorization
```
from src.models.category_predictor import CategoryPredictor

predictor = CategoryPredictor()
predictor.load_model("models/category_model")

result = predictor.predict_single("beli bensin pertamina", 50000)
print(f"Category: {result['category']}")
print(f"Confidence: {result['confidence']:.2f}")
```

### Financial Insights
```
from src.models.spending_predictor import SpendingPredictor

predictor = SpendingPredictor()
prediction = predictor.predict_next_month(transactions_df)
print(f"Next month prediction: Rp {prediction['predicted_amount']:,.0f}")
```

## 🐳 Docker Deployment
```
# Build and run with Docker
docker build -t smart-finance-tracker .
docker run -p 5000:5000 smart-finance-tracker

# Atau dengan Docker Compose
docker-compose up --build
```

## 🤝 Contributing
Kontribusi dipersilakan! Silakan:
- Fork project ini
- Buat feature branch (git checkout -b feature/AmazingFeature)
- Commit changes (git commit -m 'Add some AmazingFeature')
- Push ke branch (git push origin feature/AmazingFeature)
- Open Pull Request

## 📝 License
Distributed under the MIT License. See LICENSE for more information.

## 👥 Authors
- Chelba Polanda

## 🙏 Acknowledgments
- Scikit-learn untuk machine learning algorithms
- Flask untuk REST API framework
- Pandas untuk data processing
- Dataset transaksi keuangan personal
- Flask untuk REST API
- Streamlit untuk web interface

<div align="center">
⭐ Jika project ini membantu, jangan lupa beri star!

</div>
