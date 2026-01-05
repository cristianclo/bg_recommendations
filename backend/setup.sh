#!/bin/bash
# Quick setup script for CJEI Recommendations System

echo "🎲 CJEI Board Game Recommendation System - Quick Setup"
echo "========================================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python3 --version || { echo "❌ Python 3.11+ required"; exit 1; }

# Create virtual environment
echo "✓ Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "✓ Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your database credentials"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "========================================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your database configuration"
echo "2. Create PostgreSQL database: createdb cjei_recommendations"
echo "3. Run migrations: alembic upgrade head"
echo "4. Seed data: python -m scripts.seed_data"
echo "5. Start server: uvicorn app.main:app --reload"
echo ""
echo "Documentation: http://localhost:8000/docs"
echo "========================================================="
