from flask import Blueprint, request, jsonify
import sqlite3
import pandas as pd
from datetime import datetime
import logging
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path untuk import config
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import DATABASE_CONFIG
from api.models.transaction_model import TransactionCreate, TransactionResponse, BulkTransactionCreate

transactions_bp = Blueprint('transactions', __name__)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_CONFIG['path'])
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@transactions_bp.route('/', methods=['GET'])
def get_transactions():
    """
    Get all transactions with optional filtering
    Query parameters: type, category, start_date, end_date, limit
    """
    try:
        # Get query parameters
        transaction_type = request.args.get('type')
        category = request.args.get('category')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', 100, type=int)
        
        conn = get_db_connection()
        
        # Build query dynamically based on filters
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        
        if transaction_type:
            query += " AND transaction_type = ?"
            params.append(transaction_type)
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC, id DESC LIMIT ?"
        params.append(limit)
        
        # Execute query
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Convert to list of dictionaries
        transactions = df.to_dict('records')
        
        return jsonify({
            "status": "success",
            "data": transactions,
            "count": len(transactions),
            "filters": {
                "type": transaction_type,
                "category": category,
                "start_date": start_date,
                "end_date": end_date
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting transactions: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get transactions: {str(e)}"
        }), 500

@transactions_bp.route('/', methods=['POST'])
def create_transaction():
    """
    Create a new transaction
    """
    try:
        # Validate input data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Validate using Pydantic model
        transaction_data = TransactionCreate(**data)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert transaction
        cursor.execute('''
            INSERT INTO transactions (date, amount, transaction_type, category, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            transaction_data.date.isoformat(),
            transaction_data.amount,
            transaction_data.type.value,
            transaction_data.category,
            transaction_data.description
        ))
        
        transaction_id = cursor.lastrowid
        
        # Get the created transaction
        created_transaction = cursor.execute(
            'SELECT * FROM transactions WHERE id = ?', 
            (transaction_id,)
        ).fetchone()
        
        conn.commit()
        conn.close()
        
        # Convert to dictionary
        transaction_dict = dict(created_transaction)
        
        return jsonify({
            "status": "success",
            "message": "Transaction created successfully",
            "data": transaction_dict
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to create transaction: {str(e)}"
        }), 500

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    """
    Get a specific transaction by ID
    """
    try:
        conn = get_db_connection()
        
        transaction = conn.execute(
            'SELECT * FROM transactions WHERE id = ?', 
            (transaction_id,)
        ).fetchone()
        
        conn.close()
        
        if not transaction:
            return jsonify({
                "status": "error",
                "message": f"Transaction with ID {transaction_id} not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": dict(transaction)
        })
        
    except Exception as e:
        logger.error(f"Error getting transaction {transaction_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to get transaction: {str(e)}"
        }), 500

@transactions_bp.route('/bulk', methods=['POST'])
def create_bulk_transactions():
    """
    Create multiple transactions at once
    """
    try:
        data = request.get_json()
        
        if not data or 'transactions' not in data:
            return jsonify({
                "status": "error",
                "message": "No transactions data provided"
            }), 400
        
        bulk_data = BulkTransactionCreate(**data)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        created_ids = []
        
        for transaction in bulk_data.transactions:
            cursor.execute('''
                INSERT INTO transactions (date, amount, transaction_type, category, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                transaction.date.isoformat(),
                transaction.amount,
                transaction.type.value,
                transaction.category,
                transaction.description
            ))
            created_ids.append(cursor.lastrowid)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": f"Successfully created {len(created_ids)} transactions",
            "data": {
                "created_ids": created_ids
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating bulk transactions: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to create bulk transactions: {str(e)}"
        }), 500

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """
    Delete a transaction
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if transaction exists
        existing = cursor.execute(
            'SELECT id FROM transactions WHERE id = ?', 
            (transaction_id,)
        ).fetchone()
        
        if not existing:
            return jsonify({
                "status": "error",
                "message": f"Transaction with ID {transaction_id} not found"
            }), 404
        
        # Delete transaction
        cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": f"Transaction with ID {transaction_id} deleted successfully"
        })
        
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to delete transaction: {str(e)}"
        }), 500