#!/bin/bash

# Healthcare Backend Quick Start Script
# This script sets up the development environment

echo "🏥 Universal Healthcare Backend - Quick Start"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if PostgreSQL is running
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed."
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Generate secure keys
echo ""
echo "🔐 Generating secure keys..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update .env file with generated keys
if [ -f .env ]; then
    echo "✅ Updating .env with generated keys..."
    sed -i.bak "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" .env
    sed -i.bak "s|ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENCRYPTION_KEY|g" .env
    rm .env.bak
else
    echo "⚠️  .env file not found. Please copy .env.example to .env"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Create PostgreSQL database: createdb healthcare_db"
echo "2. Update DATABASE_URL in .env if needed"
echo "3. Run the application: uvicorn main:app --reload"
echo ""
echo "🚀 To start the server:"
echo "   source venv/bin/activate"
echo "   uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo "❤️  Health Check: http://localhost:8000/health"
