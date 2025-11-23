import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import logging

from src.models.base_model import BaseModel

logger = logging.getLogger(__name__)

class AnomalyDetector(BaseModel):
    """ML model untuk detect anomalous transactions"""
    
    def __init__(self):
        super().__init__("anomaly_detector")
        self.feature_names = ['amount', 'description_length', 'category_encoding', 'amount_ratio']
        
    def _prepare_features(self, transactions_df):
        """Prepare features untuk anomaly detection"""
        expense_data = transactions_df[transactions_df['transaction_type'] == 'expense'].copy()
        
        if len(expense_data) == 0:
            return np.array([]), expense_data
        
        # Feature engineering
        features = []
        for _, transaction in expense_data.iterrows():
            feature_vector = [
                transaction['amount'],
                len(str(transaction['description'])),  # description length
                self._get_category_encoding(transaction['category']),
                transaction['amount'] / expense_data['amount'].mean() if expense_data['amount'].mean() > 0 else 0
            ]
            features.append(feature_vector)
        
        return np.array(features), expense_data
    
    def train(self, transactions_df, y=None):
        """Train anomaly detection model - match BaseModel signature"""
        try:
            X, expense_data = self._prepare_features(transactions_df)
            
            if len(X) < 10:
                logger.warning("Not enough expense data for anomaly detection")
                return 0.0
            
            # Train Isolation Forest
            self.model = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42
            )
            
            self.model.fit(X)
            self.is_trained = True
            
            # Calculate accuracy (pseudo-accuracy untuk unsupervised learning)
            scores = self.model.decision_function(X)
            accuracy = np.mean(scores > 0)  # Percentage of "normal" transactions
            
            logger.info(f"Anomaly detection model trained - Normal transactions: {accuracy:.2f}")
            return accuracy
            
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")
            return 0.0
    
    def predict(self, transactions_df):
        """Predict anomalies - match BaseModel signature"""
        if not self.is_trained:
            return np.array([0])
        
        try:
            X, expense_data = self._prepare_features(transactions_df)
            
            if len(X) == 0:
                return np.array([0])
            
            # Predict anomalies (-1 for anomalies, 1 for normal)
            predictions = self.model.predict(X)
            
            # Return anomaly scores (negative scores indicate anomalies)
            anomaly_scores = self.model.decision_function(X)
            return anomaly_scores
            
        except Exception as e:
            logger.error(f"Error in predict: {e}")
            return np.array([0])
    
    def detect_anomalies(self, transactions_df, top_n=5):
        """Detect top anomalous transactions - additional method"""
        if not self.is_trained:
            return {"error": "Model not trained"}
        
        try:
            X, expense_data = self._prepare_features(transactions_df)
            
            if len(expense_data) < 5:
                return {"anomalies": [], "message": "Insufficient expense data"}
            
            # Get predictions and scores
            anomaly_scores = self.predict(transactions_df)
            predictions = self.model.predict(X)
            
            # Get top anomalies
            expense_data['anomaly_score'] = anomaly_scores
            expense_data['is_anomaly'] = predictions == -1
            
            anomalies = expense_data[expense_data['is_anomaly']].nlargest(top_n, 'anomaly_score')
            
            result_anomalies = []
            for _, anomaly in anomalies.iterrows():
                result_anomalies.append({
                    'date': anomaly['date'],
                    'amount': float(anomaly['amount']),
                    'category': anomaly['category'],
                    'description': anomaly['description'],
                    'anomaly_score': float(anomaly['anomaly_score']),
                    'reason': self._get_anomaly_reason(anomaly, expense_data)
                })
            
            return {
                "anomalies": result_anomalies,
                "total_analyzed": len(expense_data),
                "anomaly_count": len(anomalies)
            }
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {"error": str(e)}
    
    def _get_category_encoding(self, category):
        """Encode category to numerical value"""
        category_map = {
            'Makanan': 1, 'Transportasi': 2, 'Belanja': 3, 
            'Hiburan': 4, 'Kesehatan': 5, 'Lainnya': 6
        }
        return category_map.get(category, 6)
    
    def _get_anomaly_reason(self, transaction, all_transactions):
        """Generate human-readable reason for anomaly"""
        try:
            category_avg = all_transactions[all_transactions['category'] == transaction['category']]['amount'].mean()
            
            if transaction['amount'] > category_avg * 2:
                return f"Amount 2x higher than category average (Rp {category_avg:,.0f})"
            elif transaction['amount'] > all_transactions['amount'].quantile(0.9):
                return "In top 10% of all transactions by amount"
            else:
                return "Unusual spending pattern detected"
        except:
            return "Anomalous transaction detected"