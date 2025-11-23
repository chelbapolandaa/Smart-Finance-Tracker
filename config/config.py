import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = DATA_DIR / "database"

# Create directories if they don't exist
DATABASE_DIR.mkdir(parents=True, exist_ok=True)

# Database Configuration
DATABASE_CONFIG = {
    'path': DATABASE_DIR / "finance.db",
    'echo': False
}

# API Configuration
API_CONFIG = {
    'HOST': '0.0.0.0',
    'PORT': 5000,
    'DEBUG': True,
    'SECRET_KEY': 'your-secret-key-here-change-in-production',
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB
}

# App Configuration
APP_CONFIG = {
    'name': 'Smart Finance Tracker',
    'version': '1.0.0',
    'debug': True
}

# Categories Configuration
CATEGORIES = {
    'income': ['Gaji', 'Investasi', 'Bonus', 'Lainnya'],
    'expense': ['Makanan', 'Transportasi', 'Hiburan', 'Belanja', 'Kesehatan', 'Pendidikan', 'Lainnya']
}