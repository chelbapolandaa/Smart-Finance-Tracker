import sqlite3
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_CONFIG

def reset_database():
    """Hapus semua data transaksi dan mulai fresh"""
    
    print("🧹 Resetting database...")
    
    conn = sqlite3.connect(DATABASE_CONFIG['path'])
    cursor = conn.cursor()
    
    # Hapus semua data transaksi
    cursor.execute("DELETE FROM transactions")
    
    # Reset auto-increment counter (optional)
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
    
    conn.commit()
    conn.close()
    
    print("✅ Database reset completed!")
    print("📊 All transactions have been cleared.")
    print("🆕 Ready for fresh data generation.")

def check_database_status():
    """Cek status database setelah reset"""
    
    conn = sqlite3.connect(DATABASE_CONFIG['path'])
    cursor = conn.cursor()
    
    # Count remaining transactions
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    
    # Check categories
    cursor.execute("SELECT DISTINCT category FROM transactions")
    categories = cursor.fetchall()
    
    conn.close()
    
    print(f"📊 Current database status:")
    print(f"   Transactions: {count}")
    print(f"   Categories: {[cat[0] for cat in categories] if categories else 'None'}")

if __name__ == "__main__":
    reset_database()
    check_database_status()
    