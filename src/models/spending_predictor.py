import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib
from pathlib import Path
import logging
from datetime import datetime, timedelta

from src.models.base_model import BaseModel

logger = logging.getLogger(__name__)

class SpendingPredictor(BaseModel):
    """ML model untuk predict future spending patterns"""
    
    def __init__(self):
        super().__init__("spending_predictor")
        self.feature_columns = []
        
    def prepare_features(self, transactions_df):
        """Prepare features untuk training dan prediction"""
        # Convert to datetime
        transactions_df = transactions_df.copy()
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        
        # Aggregate monthly spending
        monthly_data = transactions_df[transactions_df['transaction_type'] == 'expense'].copy()
        monthly_data['year_month'] = monthly_data['date'].dt.to_period('M')
        
        monthly_spending = monthly_data.groupby('year_month').agg({
            'amount': 'sum',
            'id': 'count'  # transaction count
        }).reset_index()
        
        monthly_spending.columns = ['year_month', 'total_spending', 'transaction_count']
        monthly_spending['year_month'] = monthly_spending['year_month'].astype(str)
        
        # Create features
        if len(monthly_spending) > 1:
            monthly_spending['spending_ma_3'] = monthly_spending['total_spending'].rolling(3, min_periods=1).mean()
            monthly_spending['spending_trend'] = monthly_spending['total_spending'].pct_change()
            monthly_spending['month'] = pd.to_datetime(monthly_spending['year_month']).dt.month
            monthly_spending = monthly_spending.fillna(0)
        
        return monthly_spending
    
    def train(self, transactions_df, y=None):
        """Train spending prediction model - match BaseModel signature"""
        try:
            monthly_data = self.prepare_features(transactions_df)
            
            if len(monthly_data) < 3:
                logger.warning("Not enough data for spending prediction training")
                return 0.0
            
            # Prepare features and target
            feature_cols = ['total_spending', 'transaction_count', 'spending_ma_3', 'spending_trend', 'month']
            available_features = [col for col in feature_cols if col in monthly_data.columns]
            
            X = monthly_data[available_features].iloc[:-1]  # Features
            y = monthly_data['total_spending'].iloc[1:]     # Target
            
            if len(X) < 2:
                logger.warning("Not enough temporal data for prediction")
                return 0.0
            
            # Train model
            self.model = RandomForestRegressor(
                n_estimators=50,
                max_depth=5,
                random_state=42
            )
            
            self.model.fit(X, y)
            self.is_trained = True
            self.feature_columns = available_features
            
            # Calculate accuracy
            y_pred = self.model.predict(X)
            mae = mean_absolute_error(y, y_pred)
            accuracy = max(0, 1 - (mae / y.mean())) if y.mean() > 0 else 0
            
            logger.info(f"Spending prediction model trained - MAE: Rp {mae:,.0f}, Accuracy: {accuracy:.2f}")
            return accuracy
            
        except Exception as e:
            logger.error(f"Error training spending predictor: {e}")
            return 0.0
    
    def predict(self, transactions_df):
        """Predict spending - match BaseModel signature"""
        if not self.is_trained:
            return np.array([0])
        
        try:
            monthly_data = self.prepare_features(transactions_df)
            
            if len(monthly_data) < 1:
                return np.array([0])
            
            # Use latest data for prediction
            latest_data = monthly_data.iloc[-1][self.feature_columns].values.reshape(1, -1)
            predicted_spending = self.model.predict(latest_data)[0]
            
            return np.array([predicted_spending])
            
        except Exception as e:
            logger.error(f"Error in predict: {e}")
            return np.array([0])
    
    def predict_next_month(self, transactions_df):
        """Predict spending for next month - additional method"""
        if not self.is_trained:
            return {"error": "Model not trained"}
        
        try:
            prediction = self.predict(transactions_df)
            
            return {
                "predicted_amount": float(prediction[0]),
                "confidence": 0.7,
                "currency": "IDR",
                "next_month": (datetime.now() + timedelta(days=30)).strftime("%Y-%m")
            }
            
        except Exception as e:
            logger.error(f"Error predicting next month: {e}")
            return {"error": str(e)}