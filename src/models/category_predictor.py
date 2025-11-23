import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import re
import joblib
from pathlib import Path
import logging

from src.models.base_model import BaseModel

logger = logging.getLogger(__name__)

class CategoryPredictor(BaseModel):
    """ML model untuk predict transaction category berdasarkan description"""
    
    def __init__(self):
        super().__init__("category_predictor")
        self.categories = None
        self.feature_names = None
        
    def preprocess_text(self, text):
        """Enhanced text preprocessing"""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and numbers, keep Indonesian characters
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Indonesian stopwords (basic)
        indonesian_stopwords = {'di', 'ke', 'dan', 'atau', 'yang', 'untuk', 'pada', 'dengan', 'ini', 'itu'}
        
        # Remove stopwords
        words = text.split()
        words = [word for word in words if word not in indonesian_stopwords and len(word) > 2]
        
        # Remove extra whitespace
        text = ' '.join(words)
        
        return text
    
    def prepare_features(self, descriptions):
        """Prepare features dari transaction descriptions"""
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words=None,  # Bahasa Indonesia stopwords nanti kita tambah
                ngram_range=(1, 2)
            )
            features = self.vectorizer.fit_transform(descriptions)
            self.feature_names = self.vectorizer.get_feature_names_out()
        else:
            features = self.vectorizer.transform(descriptions)
        
        return features
    
    def train(self, transactions_df):
        """Train model dengan transaction data"""
        try:
            # Prepare data
            descriptions = transactions_df['description'].apply(self.preprocess_text)
            categories = transactions_df['category']
            
            # Get unique categories
            self.categories = sorted(categories.unique())
            logger.info(f"Training for categories: {self.categories}")
            
            # Prepare features
            X = self.prepare_features(descriptions)
            y = categories
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Evaluate
            train_accuracy = accuracy_score(y_train, self.model.predict(X_train))
            test_accuracy = accuracy_score(y_test, self.model.predict(X_test))
            
            logger.info(f"Training completed - Train Accuracy: {train_accuracy:.4f}, Test Accuracy: {test_accuracy:.4f}")
            
            return test_accuracy
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def predict(self, descriptions, return_confidence=False):
        """Predict category untuk transaction descriptions"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        if isinstance(descriptions, str):
            descriptions = [descriptions]
        
        # Preprocess
        processed_descriptions = [self.preprocess_text(desc) for desc in descriptions]
        
        # Prepare features
        features = self.prepare_features(processed_descriptions)
        
        # Predict
        predictions = self.model.predict(features)
        probabilities = self.model.predict_proba(features)
        
        if return_confidence:
            confidences = np.max(probabilities, axis=1)
            return predictions, confidences
        else:
            return predictions
    
    def predict_single(self, description, amount=0):
        """Predict single transaction dengan confidence"""
        if not self.is_trained:
            return "Lainnya", 0.0
        
        try:
            prediction, confidence = self.predict([description], return_confidence=True)
            
            # Rule-based fallback untuk amount-based categories
            predicted_category = prediction[0]
            final_confidence = confidence[0]
            
            # Amount-based rules (optional enhancement)
            if amount > 1000000 and predicted_category == "Lainnya":
                predicted_category = "Belanja"
                final_confidence = max(final_confidence, 0.7)
            
            return predicted_category, float(final_confidence)
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return "Lainnya", 0.0