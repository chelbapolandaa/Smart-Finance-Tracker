import sqlite3
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_CONFIG

def clean_training_data():
    """Clean and fix mislabeled training data"""
    
    print("🧹 Cleaning training data...")
    
    conn = sqlite3.connect(DATABASE_CONFIG['path'])
    cursor = conn.cursor()
    
    # Fix mislabeled transportation data
    fix_queries = [
        # Fix gojek/ojek - should always be Transportasi
        "UPDATE transactions SET category = 'Transportasi' WHERE description LIKE '%gojek%' AND category != 'Transportasi'",
        "UPDATE transactions SET category = 'Transportasi' WHERE description LIKE '%ojek%' AND category != 'Transportasi'",
        
        # Fix bensin/parkir/tol - should be Transportasi
        "UPDATE transactions SET category = 'Transportasi' WHERE description LIKE '%bensin%' AND category != 'Transportasi'",
        "UPDATE transactions SET category = 'Transportasi' WHERE description LIKE '%parkir%' AND category != 'Transportasi'",
        "UPDATE transactions SET category = 'Transportasi' WHERE description LIKE '%tol%' AND category != 'Transportasi'",
        
        # Fix nonton/bioskop - should be Hiburan
        "UPDATE transactions SET category = 'Hiburan' WHERE description LIKE '%nonton%' AND category != 'Hiburan'",
        "UPDATE transactions SET category = 'Hiburan' WHERE description LIKE '%bioskop%' AND category != 'Hiburan'",
        "UPDATE transactions SET category = 'Hiburan' WHERE description LIKE '%cinema%' AND category != 'Hiburan'",
        
        # Fix obat/apotik - should be Kesehatan
        "UPDATE transactions SET category = 'Kesehatan' WHERE description LIKE '%obat%' AND category != 'Kesehatan'",
        "UPDATE transactions SET category = 'Kesehatan' WHERE description LIKE '%apotik%' AND category != 'Kesehatan'",
    ]
    
    for query in fix_queries:
        try:
            cursor.execute(query)
            rows_affected = cursor.rowcount
            if rows_affected > 0:
                print(f"✅ Fixed {rows_affected} records: {query[:60]}...")
        except Exception as e:
            print(f"❌ Error in query: {e}")
    
    conn.commit()
    
    # Show cleaned data distribution
    cursor.execute("SELECT category, COUNT(*) FROM transactions GROUP BY category")
    results = cursor.fetchall()
    
    print("\n📊 Cleaned Data Distribution:")
    for category, count in results:
        print(f"   {category}: {count} samples")
    
    conn.close()
    print("\n🎉 Data cleaning completed!")

if __name__ == "__main__":
    clean_training_data()