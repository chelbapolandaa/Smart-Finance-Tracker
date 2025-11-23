import requests
import streamlit as st
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5000/api/v1"):
        self.base_url = base_url
        self.timeout = 10
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Generic method to make API requests"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            print(f"🔍 API Request: {method} {url} -> Status: {response.status_code}")
            
            # ✅ FIX: Handle 201 (Created) sebagai success juga
            if response.status_code in [200, 201]:  # 200 OK dan 201 Created
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API server. Make sure Flask API is running on localhost:5000")
            return None
        except requests.exceptions.Timeout:
            st.error("⏰ API request timeout")
            return None
        except Exception as e:
            st.error(f"🚨 Unexpected error: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        result = self._make_request("GET", "/health")
        return result is not None and result.get("status") == "healthy"
    
    def get_transactions(self, filters: Dict = None) -> Optional[List[Dict]]:
        """Get transactions with optional filters"""
        params = filters or {}
        result = self._make_request("GET", "/transactions/", params=params)
        return result.get("data") if result else None
    
    def create_transaction(self, transaction_data: Dict) -> Optional[Dict]:
        """Create a new transaction"""
        result = self._make_request(
            "POST", 
            "/transactions/", 
            json=transaction_data
        )
        # ✅ FIX: Return data bahkan untuk status 201
        if result and result.get("status") in ["success", "created"]:
            return result.get("data")
        return None
    
    def get_financial_summary(self) -> Optional[Dict]:
        """Get financial summary"""
        result = self._make_request("GET", "/analytics/summary")
        return result.get("data") if result else None
    
    def get_category_breakdown(self) -> Optional[Dict]:
        """Get category breakdown"""
        result = self._make_request("GET", "/analytics/categories")
        return result.get("data") if result else None
    
    def get_monthly_trend(self, months: int = 6) -> Optional[Dict]:
        """Get monthly trend data"""
        result = self._make_request(
            "GET", 
            "/analytics/monthly-trend", 
            params={"months": months}
        )
        return result.get("data") if result else None
    
    def ai_categorize(self, description: str, amount: float = 0) -> Optional[Dict]:
        """AI categorization for transaction"""
        result = self._make_request(
            "POST",
            "/ai/categorize",
            json={"description": description, "amount": amount}
        )
        return result.get("data") if result else None

# Global API client instance
api_client = APIClient()