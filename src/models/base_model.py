import pandas as pd
import numpy as np
import joblib
from abc import ABC, abstractmethod
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    """Base class for all ML models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.vectorizer = None
        self.is_trained = False
        
    @abstractmethod
    def train(self, X, y):
        pass
    
    @abstractmethod
    def predict(self, X):
        pass
    
    def save_model(self, model_dir: Path):
        """Save model and vectorizer"""
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if self.model:
            joblib.dump(self.model, model_dir / f"{self.model_name}_model.pkl")
        if self.vectorizer:
            joblib.dump(self.vectorizer, model_dir / f"{self.model_name}_vectorizer.pkl")
        
        logger.info(f"Model saved to {model_dir}")
    
    def load_model(self, model_dir: Path):
        """Load model and vectorizer"""
        try:
            model_path = model_dir / f"{self.model_name}_model.pkl"
            vectorizer_path = model_dir / f"{self.model_name}_vectorizer.pkl"
            
            if model_path.exists():
                self.model = joblib.load(model_path)
            if vectorizer_path.exists():
                self.vectorizer = joblib.load(vectorizer_path)
            
            self.is_trained = self.model is not None
            logger.info(f"Model loaded from {model_dir}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        from sklearn.metrics import accuracy_score, classification_report
        
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        y_pred = self.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model Accuracy: {accuracy:.4f}")
        logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        
        return accuracy, classification_report(y_test, y_pred)