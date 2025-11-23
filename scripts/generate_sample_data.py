import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import DATABASE_CONFIG

def generate_sample_data():
    """Generate sample transaction data untuk training model"""
    
    # Sample transactions dengan categories yang clear
    sample_transactions = [
        # Makanan
        {"description": "Makan siang di warung padang", "category": "Makanan", "amount": 25000},
        {"description": "Sarapan roti dan kopi", "category": "Makanan", "amount": 15000},
        {"description": "Makan malam di restoran", "category": "Makanan", "amount": 80000},
        {"description": "Beli nasi goreng", "category": "Makanan", "amount": 20000},
        {"description": "Minum jus buah", "category": "Makanan", "amount": 12000},
        
        # Transportasi
        {"description": "Isi bensin motor", "category": "Transportasi", "amount": 20000},
        {"description": "Bayar parkir", "category": "Transportasi", "amount": 5000},
        {"description": "Gojek ke kantor", "category": "Transportasi", "amount": 15000},
        {"description": "Tiket busway", "category": "Transportasi", "amount": 3500},
        {"description": "Service motor", "category": "Transportasi", "amount": 150000},
        
        # Belanja
        {"description": "Belanja di supermarket", "category": "Belanja", "amount": 300000},
        {"description": "Beli baju di mall", "category": "Belanja", "amount": 250000},
        {"description": "Order dari tokopedia", "category": "Belanja", "amount": 120000},
        {"description": "Beli elektronik", "category": "Belanja", "amount": 500000},
        {"description": "Belanja bulanan", "category": "Belanja", "amount": 450000},
        
        # Hiburan
        {"description": "Nonton film di bioskop", "category": "Hiburan", "amount": 50000},
        {"description": "Main game online", "category": "Hiburan", "amount": 100000},
        {"description": "Karaoke dengan teman", "category": "Hiburan", "amount": 75000},
        {"description": "Tiket konser musik", "category": "Hiburan", "amount": 300000},
        {"description": "Langganan Netflix", "category": "Hiburan", "amount": 54000},
        
        # Kesehatan
        {"description": "Konsultasi dokter", "category": "Kesehatan", "amount": 150000},
        {"description": "Beli obat di apotik", "category": "Kesehatan", "amount": 75000},
        {"description": "Medical checkup", "category": "Kesehatan", "amount": 500000},
        {"description": "Vitamin dan suplemen", "category": "Kesehatan", "amount": 120000},
        
        # Lainnya
        {"description": "Bayar listrik", "category": "Lainnya", "amount": 350000},
        {"description": "Donasi", "category": "Lainnya", "amount": 50000},
        {"description": "Biaya administrasi bank", "category": "Lainnya", "amount": 15000},

        # Makanan - Expanded
        {"description": "Makan siang di warung padang", "category": "Makanan", "amount": 25000},
        {"description": "Sarapan roti dan kopi", "category": "Makanan", "amount": 15000},
        {"description": "Makan malam di restoran", "category": "Makanan", "amount": 80000},
        {"description": "Beli nasi goreng", "category": "Makanan", "amount": 20000},
        {"description": "Minum jus buah", "category": "Makanan", "amount": 12000},
        {"description": "Makan bakso", "category": "Makanan", "amount": 18000},
        {"description": "Beli martabak", "category": "Makanan", "amount": 30000},
        {"description": "Kedai kopi Starbucks", "category": "Makanan", "amount": 45000},
        
        # Transportasi - Expanded  
        {"description": "Isi bensin motor", "category": "Transportasi", "amount": 20000},
        {"description": "Bayar parkir", "category": "Transportasi", "amount": 5000},
        {"description": "Gojek ke kantor", "category": "Transportasi", "amount": 15000},
        {"description": "Tiket busway", "category": "Transportasi", "amount": 3500},
        {"description": "Service motor", "category": "Transportasi", "amount": 150000},
        {"description": "Beli oli motor", "category": "Transportasi", "amount": 75000},
        {"description": "Tol jalan", "category": "Transportasi", "amount": 25000},
        {"description": "Taxi online", "category": "Transportasi", "amount": 35000},
        
        # Belanja - Expanded
        {"description": "Belanja di supermarket", "category": "Belanja", "amount": 300000},
        {"description": "Beli baju di mall", "category": "Belanja", "amount": 250000},
        {"description": "Order dari tokopedia", "category": "Belanja", "amount": 120000},
        {"description": "Beli elektronik", "category": "Belanja", "amount": 500000},
        {"description": "Belanja bulanan", "category": "Belanja", "amount": 450000},
        {"description": "Peralatan rumah tangga", "category": "Belanja", "amount": 200000},
        {"description": "Buku dan alat tulis", "category": "Belanja", "amount": 150000},
        
        # Hiburan - Expanded
        {"description": "Nonton film di bioskop", "category": "Hiburan", "amount": 50000},
        {"description": "Main game online", "category": "Hiburan", "amount": 100000},
        {"description": "Karaoke dengan teman", "category": "Hiburan", "amount": 75000},
        {"description": "Tiket konser musik", "category": "Hiburan", "amount": 300000},
        {"description": "Langganan Netflix", "category": "Hiburan", "amount": 54000},
        {"description": "Main bowling", "category": "Hiburan", "amount": 80000},
        {"description": "Tiket wahana bermain", "category": "Hiburan", "amount": 120000},
        {"description": "Nonton film cinema", "category": "Hiburan", "amount": 50000},
        {"description": "Tiket bioskop", "category": "Hiburan", "amount": 45000},
        {"description": "Nonton di XXI", "category": "Hiburan", "amount": 55000},
        {"description": "Movie theater", "category": "Hiburan", "amount": 60000},
        
        # Kesehatan - Expanded
        {"description": "Konsultasi dokter", "category": "Kesehatan", "amount": 150000},
        {"description": "Beli obat di apotik", "category": "Kesehatan", "amount": 75000},
        {"description": "Medical checkup", "category": "Kesehatan", "amount": 500000},
        {"description": "Vitamin dan suplemen", "category": "Kesehatan", "amount": 120000},
        {"description": "Beli masker kesehatan", "category": "Kesehatan", "amount": 50000},
        {"description": "Periksa gigi", "category": "Kesehatan", "amount": 200000},
        
        # Lainnya - Expanded
        {"description": "Bayar listrik", "category": "Lainnya", "amount": 350000},
        {"description": "Donasi", "category": "Lainnya", "amount": 50000},
        {"description": "Biaya administrasi bank", "category": "Lainnya", "amount": 15000},
        {"description": "Transfer uang", "category": "Lainnya", "amount": 1000000},
        {"description": "Bayar tagihan air", "category": "Lainnya", "amount": 80000},
        {"description": "Biaya kirim paket", "category": "Lainnya", "amount": 25000},

        # Tambah di generate_sample_data.py - samples yang clarify transport vs shopping
        {"description": "Gojek ke mall untuk belanja", "category": "Belanja", "amount": 15000},
        {"description": "Gojek ke mall meeting", "category": "Transportasi", "amount": 15000},
        {"description": "Naik gojek ke pusat perbelanjaan", "category": "Transportasi", "amount": 12000},
        {"description": "Ojek online ke supermarket", "category": "Transportasi", "amount": 10000},
    ]
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_CONFIG['path'])
    cursor = conn.cursor()
    
    # Clear existing sample data (optional)
    cursor.execute("DELETE FROM transactions WHERE description LIKE '%sample%' OR description IN (?, ?, ?, ?, ?, ?, ?, ?)", 
                  ('Makan siang di warung padang', 'Isi bensin motor', 'Belanja di supermarket', 
                   'Nonton film di bioskop', 'Konsultasi dokter', 'Bayar listrik', 'Sarapan roti dan kopi', 'Gojek ke kantor'))
    
    # Insert sample data
    for i, transaction in enumerate(sample_transactions):
        date = (datetime.now() - timedelta(days=len(sample_transactions)-i)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO transactions (date, amount, transaction_type, category, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            date,
            transaction['amount'],
            'expense',
            transaction['category'],
            transaction['description']
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Generated {len(sample_transactions)} sample transactions")
    print("📊 Categories distribution:")
    
    # Show category distribution
    df = pd.DataFrame(sample_transactions)
    print(df['category'].value_counts())

if __name__ == "__main__":
    generate_sample_data()