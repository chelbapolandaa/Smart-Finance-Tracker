from flask import Blueprint, request, jsonify
import logging
import sys
from pathlib import Path
import pandas as pd

# Import ML models
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.models.category_predictor import CategoryPredictor
from src.models.spending_predictor import SpendingPredictor
from src.models.anomaly_detector import AnomalyDetector
from config.config import DATABASE_CONFIG

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)

# Global model instances
category_model = CategoryPredictor()
spending_predictor = SpendingPredictor()
anomaly_detector = AnomalyDetector()

def init_ai_models():
    """Initialize semua AI models"""
    try:
        models_dir = Path(__file__).parent.parent.parent / "models"
        
        # Load existing models
        category_model.load_model(models_dir / "category_model")
        spending_predictor.load_model(models_dir / "spending_predictor") 
        anomaly_detector.load_model(models_dir / "anomaly_detector")
        
        logger.info("AI models initialization completed")
    except Exception as e:
        logger.info("Some AI models need training")

@ai_bp.route('/categorize', methods=['POST'])
def categorize_transaction():
    """AI-powered transaction categorization dengan real ML model"""
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({
                "status": "error",
                "message": "No description provided"
            }), 400
        
        description = data['description']
        amount = data.get('amount', 0)
        
        # Predict menggunakan ML model
        if category_model.is_trained:
            predicted_category, confidence = category_model.predict_single(description, amount)
            model_type = "ml_model"
        else:
            # Fallback ke rule-based
            predicted_category = categorize_by_rules(description, amount)
            confidence = 0.6
            model_type = "rule_based"
        
        # Get alternative categories dengan confidence
        alternative_categories = get_alternative_categories(description, amount)
        
        return jsonify({
            "status": "success",
            "data": {
                "description": description,
                "predicted_category": predicted_category,
                "confidence": confidence,
                "model_version": model_type,
                "alternative_categories": alternative_categories
            }
        })
        
    except Exception as e:
        logger.error(f"Error in AI categorization: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"AI categorization failed: {str(e)}"
        }), 500

@ai_bp.route('/train-category-model', methods=['POST'])
def train_category_model():
    """Train atau retrain category prediction model"""
    try:
        # Get transaction data dari database
        import sqlite3
        conn = sqlite3.connect(DATABASE_CONFIG['path'])
        
        query = """
            SELECT description, category, amount 
            FROM transactions 
            WHERE description IS NOT NULL AND category IS NOT NULL
            AND LENGTH(description) > 3
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if len(df) < 10:
            return jsonify({
                "status": "error",
                "message": "Not enough training data. Need at least 10 transactions."
            }), 400
        
        # Train model
        accuracy = category_model.train(df)
        
        # Save model
        models_dir = Path(__file__).parent.parent.parent / "models" / "category_model"
        category_model.save_model(models_dir)
        
        # Convert categories to list properly
        categories_list = []
        if category_model.categories is not None:
            if hasattr(category_model.categories, 'tolist'):
                categories_list = category_model.categories.tolist()
            else:
                categories_list = list(category_model.categories)
        
        return jsonify({
            "status": "success",
            "data": {
                "training_samples": len(df),
                "accuracy": accuracy,
                "categories": categories_list,
                "model_saved": True
            }
        })
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Model training failed: {str(e)}"
        }), 500

@ai_bp.route('/model-status', methods=['GET'])
def get_model_status():
    """Get AI model status"""
    
    # Convert categories to list properly
    categories_list = []
    if category_model.categories is not None:
        if hasattr(category_model.categories, 'tolist'):
            categories_list = category_model.categories.tolist()
        else:
            categories_list = list(category_model.categories)
    
    return jsonify({
        "status": "success",
        "data": {
            "is_trained": category_model.is_trained,
            "model_type": "category_predictor",
            "categories": categories_list,
            "training_ready": check_training_data_availability()
        }
    })

@ai_bp.route('/predict-spending', methods=['GET'])
def predict_spending():
    """Predict next month's spending"""
    try:
        # Get transaction data
        import sqlite3
        conn = sqlite3.connect(DATABASE_CONFIG['path'])
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()
        
        # Train model jika belum trained
        if not spending_predictor.is_trained and len(df) >= 3:
            accuracy = spending_predictor.train(df)
            if accuracy > 0:
                spending_predictor.save_model(Path(__file__).parent.parent.parent / "models" / "spending_predictor")
        
        # Get prediction
        prediction = spending_predictor.predict_next_month(df)
        
        return jsonify({
            "status": "success",
            "data": prediction
        })
        
    except Exception as e:
        logger.error(f"Error in spending prediction: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Spending prediction failed: {str(e)}"
        }), 500

@ai_bp.route('/detect-anomalies', methods=['GET'])
def detect_anomalies():
    """Detect anomalous transactions"""
    try:
        # Get transaction data
        import sqlite3
        conn = sqlite3.connect(DATABASE_CONFIG['path'])
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()
        
        # Train model jika belum trained
        if not anomaly_detector.is_trained and len(df) >= 10:
            accuracy = anomaly_detector.train(df)
            if accuracy > 0:
                anomaly_detector.save_model(Path(__file__).parent.parent.parent / "models" / "anomaly_detector")
        
        # Detect anomalies
        anomalies = anomaly_detector.detect_anomalies(df)
        
        return jsonify({
            "status": "success",
            "data": anomalies
        })
        
    except Exception as e:
        logger.error(f"Error in anomaly detection: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"Anomaly detection failed: {str(e)}"
        }), 500

@ai_bp.route('/financial-insights', methods=['GET'])
def get_financial_insights():
    """Get comprehensive financial insights"""
    try:
        import sqlite3
        conn = sqlite3.connect(DATABASE_CONFIG['path'])
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()
        
        # Basic analytics
        total_income = df[df['transaction_type'] == 'income']['amount'].sum()
        total_expense = df[df['transaction_type'] == 'expense']['amount'].sum()
        savings_rate = (total_income - total_expense) / total_income if total_income > 0 else 0
        
        # Category insights
        expense_by_category = df[df['transaction_type'] == 'expense'].groupby('category')['amount'].sum()
        top_category = expense_by_category.idxmax() if not expense_by_category.empty else "No data"
        
        # Monthly trends
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        monthly_expense = df[df['transaction_type'] == 'expense'].groupby('month')['amount'].sum()
        
        insights = {
            "financial_health": {
                "savings_rate": float(savings_rate),
                "health_score": min(100, max(0, savings_rate * 100)),
                "recommendation": get_financial_recommendation(savings_rate)
            },
            "spending_insights": {
                "top_spending_category": top_category,
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "net_savings": float(total_income - total_expense)
            },
            "monthly_trend": {
                "trend": "increasing" if len(monthly_expense) > 1 and monthly_expense.iloc[-1] > monthly_expense.iloc[-2] else "stable",
                "last_month_spending": float(monthly_expense.iloc[-1]) if not monthly_expense.empty else 0
            }
        }
        
        return jsonify({
            "status": "success",
            "data": insights
        })
        
    except Exception as e:
        logger.error(f"Error getting financial insights: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Financial insights failed: {str(e)}"
        }), 500

# ==================== HELPER FUNCTIONS ====================

def categorize_by_rules(description, amount=0):
    """Rule-based categorization fallback"""
    description_lower = description.lower()
    
    food_keywords = ['makan', 'restoran', 'warung', 'kafe', 'minum', 'kopi', 'makanan', 'warteg', 'nasi']
    transport_keywords = ['bensin', 'transport', 'gojek', 'grab', 'taxi', 'angkot', 'bus', 'ojek', 'perjalanan']
    entertainment_keywords = ['nonton', 'film', 'hiburan', 'game', 'hobi', 'travel', 'liburan', 'hotel']
    shopping_keywords = ['belanja', 'mall', 'supermarket', 'tokopedia', 'shopee', 'online', 'pakaian']
    health_keywords = ['kesehatan', 'dokter', 'rumah sakit', 'obat', 'apotik', 'medical']
    
    if any(keyword in description_lower for keyword in food_keywords):
        return "Makanan"
    elif any(keyword in description_lower for keyword in transport_keywords):
        return "Transportasi"
    elif any(keyword in description_lower for keyword in entertainment_keywords):
        return "Hiburan"
    elif any(keyword in description_lower for keyword in shopping_keywords):
        return "Belanja"
    elif any(keyword in description_lower for keyword in health_keywords):
        return "Kesehatan"
    elif amount > 5000000:  # Large amount likely investment
        return "Investasi"
    else:
        return "Lainnya"

def get_alternative_categories(description, amount=0):
    """Get alternative categories dengan confidence scores"""
    alternatives = []
    
    if category_model.is_trained:
        try:
            # Get probabilities for all categories
            processed_desc = category_model.preprocess_text(description)
            features = category_model.prepare_features([processed_desc])
            probabilities = category_model.model.predict_proba(features)[0]
            
            for category, prob in zip(category_model.categories, probabilities):
                if prob > 0.1:  # Only show categories with >10% probability
                    alternatives.append({
                        "category": category,
                        "confidence": float(prob)
                    })
            
            # Sort by confidence
            alternatives.sort(key=lambda x: x["confidence"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting alternatives: {e}")
    
    # Jika tidak ada alternatives, berikan default
    if not alternatives:
        alternatives = [
            {"category": "Makanan", "confidence": 0.3},
            {"category": "Transportasi", "confidence": 0.3},
            {"category": "Lainnya", "confidence": 0.4}
        ]
    
    return alternatives[:3]  # Return top 3 alternatives

def check_training_data_availability():
    """Check if enough data available for training"""
    try:
        import sqlite3
        conn = sqlite3.connect(DATABASE_CONFIG['path'])
        
        query = "SELECT COUNT(*) as count FROM transactions WHERE description IS NOT NULL AND category IS NOT NULL"
        result = conn.execute(query).fetchone()
        conn.close()
        
        return result[0] >= 10  # Minimum 10 samples
    except:
        return False

def get_financial_recommendation(savings_rate):
    """Get AI-powered financial recommendation"""
    if savings_rate >= 0.2:
        return "Excellent savings rate! Consider investment options."
    elif savings_rate >= 0.1:
        return "Good savings rate. Maintain this healthy habit."
    elif savings_rate >= 0:
        return "Positive savings. Look for opportunities to reduce expenses."
    else:
        return "Spending exceeds income. Review expenses and create a budget."

# Initialize models on import
init_ai_models()