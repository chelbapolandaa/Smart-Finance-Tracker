from flask import Blueprint, request, jsonify
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging
import numpy as np
import sys
from pathlib import Path

# Import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import DATABASE_CONFIG

# Blueprint Definition
analytics_bp = Blueprint('analytics', __name__)
logger = logging.getLogger(__name__)

def convert_to_serializable(obj):
    """Convert numpy/pandas types to native Python types for JSON serialization"""
    if pd.isna(obj) or obj is None:
        return 0
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    else:
        return obj

def get_db_connection():
    conn = sqlite3.connect(DATABASE_CONFIG['path'])
    return conn

@analytics_bp.route('/summary', methods=['GET'])
def get_financial_summary():
    """
    Get overall financial summary
    """
    try:
        conn = get_db_connection()
        
        # Basic summary
        summary_query = """
            SELECT 
                SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as total_expense,
                COUNT(*) as total_transactions,
                COUNT(DISTINCT category) as unique_categories,
                MIN(date) as first_transaction_date,
                MAX(date) as last_transaction_date
            FROM transactions
        """
        
        summary_df = pd.read_sql_query(summary_query, conn)
        
        # Current month summary
        current_month = datetime.now().strftime('%Y-%m')
        monthly_query = """
            SELECT 
                SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as monthly_income,
                SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as monthly_expense
            FROM transactions
            WHERE strftime('%Y-%m', date) = ?
        """
        
        monthly_df = pd.read_sql_query(monthly_query, conn, params=(current_month,))
        
        conn.close()
        
        # Convert to native Python types
        total_income = convert_to_serializable(summary_df.iloc[0]['total_income'])
        total_expense = convert_to_serializable(summary_df.iloc[0]['total_expense'])
        total_transactions = convert_to_serializable(summary_df.iloc[0]['total_transactions'])
        unique_categories = convert_to_serializable(summary_df.iloc[0]['unique_categories'])
        
        monthly_income = convert_to_serializable(monthly_df.iloc[0]['monthly_income'])
        monthly_expense = convert_to_serializable(monthly_df.iloc[0]['monthly_expense'])
        
        # Calculate additional metrics
        balance = total_income - total_expense
        monthly_balance = monthly_income - monthly_expense
        
        return jsonify({
            "status": "success",
            "data": {
                "overall": {
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "balance": balance,
                    "total_transactions": total_transactions,
                    "unique_categories": unique_categories,
                    "first_transaction_date": str(summary_df.iloc[0]['first_transaction_date']) if summary_df.iloc[0]['first_transaction_date'] else None,
                    "last_transaction_date": str(summary_df.iloc[0]['last_transaction_date']) if summary_df.iloc[0]['last_transaction_date'] else None
                },
                "current_month": {
                    "income": monthly_income,
                    "expense": monthly_expense,
                    "balance": monthly_balance,
                    "month": current_month
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting financial summary: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get financial summary: {str(e)}"
        }), 500

@analytics_bp.route('/categories', methods=['GET'])
def get_category_breakdown():
    """
    Get spending/income breakdown by category
    """
    try:
        conn = get_db_connection()
        
        category_query = """
            SELECT 
                category,
                transaction_type,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount,
                AVG(amount) as average_amount
            FROM transactions
            GROUP BY category, transaction_type
            ORDER BY total_amount DESC
        """
        
        df = pd.read_sql_query(category_query, conn)
        conn.close()
        
        # Convert all numeric columns to native Python types
        for col in ['transaction_count', 'total_amount', 'average_amount']:
            df[col] = df[col].apply(convert_to_serializable)
        
        return jsonify({
            "status": "success",
            "data": {
                "breakdown": df.to_dict('records')
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting category breakdown: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get category breakdown: {str(e)}"
        }), 500

@analytics_bp.route('/monthly-trend', methods=['GET'])
def get_monthly_trend():
    """
    Get monthly income/expense trend
    Query parameters: months (number of months to include)
    """
    try:
        months = request.args.get('months', 6, type=int)
        
        conn = get_db_connection()
        
        trend_query = """
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END) as income,
                SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END) as expense,
                COUNT(*) as transaction_count
            FROM transactions
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month DESC
            LIMIT ?
        """
        
        df = pd.read_sql_query(trend_query, conn, params=(months,))
        conn.close()
        
        # Convert numeric columns to native Python types
        for col in ['income', 'expense', 'transaction_count']:
            df[col] = df[col].apply(convert_to_serializable)
        
        # Calculate balance for each month
        df['balance'] = df['income'] - df['expense']
        
        return jsonify({
            "status": "success",
            "data": {
                "trend": df.to_dict('records'),
                "period_months": months
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting monthly trend: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get monthly trend: {str(e)}"
        }), 500