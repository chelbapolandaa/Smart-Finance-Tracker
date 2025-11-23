import pandas as pd
import sqlite3
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_CONFIG

def analyze_data_quality():
    """Analyze training data quality issues"""
    
    print("🔍 Analyzing Data Quality...\n")
    
    conn = sqlite3.connect(DATABASE_CONFIG['path'])
    
    # Get all training data
    query = """
        SELECT description, category, amount 
        FROM transactions 
        WHERE description IS NOT NULL AND category IS NOT NULL
        AND LENGTH(description) > 3
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(f"Total training samples: {len(df)}")
    print(f"Categories: {df['category'].unique().tolist()}\n")
    
    # 1. Check category distribution
    print("📊 Category Distribution:")
    category_counts = df['category'].value_counts()
    print(category_counts)
    print()
    
    # 2. Check for potential mislabeling
    print("🔎 Checking for potential mislabeled data...")
    
    # Look for descriptions that might be misclassified
    suspicious_patterns = {
        'bensin': 'Transportasi',
        'gojek': 'Transportasi', 
        'transport': 'Transportasi',
        'parkir': 'Transportasi',
        'ojek': 'Transportasi'
    }
    
    for pattern, expected_category in suspicious_patterns.items():
        matches = df[df['description'].str.contains(pattern, case=False, na=False)]
        if len(matches) > 0:
            mismatches = matches[matches['category'] != expected_category]
            if len(mismatches) > 0:
                print(f"❌ Potential mislabeling for '{pattern}':")
                for _, row in mismatches.head(3).iterrows():
                    print(f"   '{row['description']}' → {row['category']} (should be {expected_category})")
                print()
    
    # 3. Check for very similar descriptions with different categories
    print("🔄 Checking similar descriptions with different categories...")
    
    # Group by first few words
    df['first_words'] = df['description'].str.lower().str.split().str[:3].str.join(' ')
    similar_descriptions = df.groupby('first_words')['category'].nunique()
    conflicting = similar_descriptions[similar_descriptions > 1]
    
    if len(conflicting) > 0:
        print("Found conflicting descriptions:")
        for desc_start in conflicting.index[:5]:  # Show first 5
            categories = df[df['first_words'] == desc_start]['category'].unique()
            examples = df[df['first_words'] == desc_start][['description', 'category']].head(2)
            print(f"   '{desc_start}...' → Categories: {list(categories)}")
            for _, row in examples.iterrows():
                print(f"      - '{row['description']}' → {row['category']}")
            print()
    
    # 4. Check description length and quality
    print("📝 Description Quality Analysis:")
    df['desc_length'] = df['description'].str.len()
    print(f"Average description length: {df['desc_length'].mean():.1f} characters")
    print(f"Shortest: '{df.loc[df['desc_length'].idxmin(), 'description']}'")
    print(f"Longest: '{df.loc[df['desc_length'].idxmax(), 'description']}'")
    
    # 5. Show some problematic predictions
    print("\n🎯 Problematic Cases from Recent Test:")
    problematic_cases = [
        ("Isi bensin pertamax", "Transportasi", "Hiburan"),
        ("Gojek ke mall", "Transportasi", "Belanja")
    ]
    
    for desc, expected, predicted in problematic_cases:
        print(f"   '{desc}'")
        print(f"      Expected: {expected}, Predicted: {predicted}")
        
        # Find similar training examples
        similar = df[df['description'].str.contains('bensin|gojek', case=False, na=False)]
        if len(similar) > 0:
            print(f"      Similar training examples:")
            for _, row in similar.head(2).iterrows():
                print(f"        - '{row['description']}' → {row['category']}")

if __name__ == "__main__":
    analyze_data_quality()