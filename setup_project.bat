@echo off
echo 🚀 Setting up Smart Finance Tracker Project Structure...

mkdir api\models api\routes api\utils
mkdir web_app\components web_app\pages web_app\utils
mkdir src\data src\models src\analytics src\services
mkdir config
mkdir models\category_model models\spending_model
mkdir data\raw data\processed data\database
mkdir tests\unit tests\integration tests\fixtures
mkdir docs\api docs\deployment docs\development
mkdir scripts
mkdir .github\workflows .github\ISSUE_TEMPLATE

echo. > requirements.txt
echo. > requirements-dev.txt
echo. > Dockerfile
echo. > docker-compose.yml
echo. > .env.example
echo. > .gitignore
echo. > LICENSE
echo. > README.md
echo. > setup.py
echo. > pyproject.toml

echo ✅ Project structure created successfully!