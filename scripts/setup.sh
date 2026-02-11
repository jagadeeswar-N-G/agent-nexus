#!/bin/bash

# AgentNexus - One-Click Setup Script
# This script sets up your entire development environment

set -e

echo "🤖 AgentNexus Setup"
echo "=================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

command -v node >/dev/null 2>&1 || { echo -e "${RED}❌ Node.js is required but not installed.${NC}" >&2; exit 1; }
command -v pnpm >/dev/null 2>&1 || { echo -e "${RED}❌ pnpm is required. Install with: npm install -g pnpm${NC}" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python 3.11+ is required but not installed.${NC}" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required but not installed.${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose is required but not installed.${NC}" >&2; exit 1; }

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
pnpm install
cd ..
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
echo ""

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate || . venv/Scripts/activate  # Windows compatibility
pip install --upgrade pip
pip install -r requirements.txt
cd ..
echo -e "${GREEN}✅ Python environment ready${NC}"
echo ""

# Create environment files
echo "⚙️  Creating environment files..."

# Frontend .env.local
if [ ! -f frontend/.env.local ]; then
    cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_NAME=AgentNexus
NEXT_PUBLIC_ENVIRONMENT=development
EOF
    echo -e "${GREEN}✅ Created frontend/.env.local${NC}"
else
    echo -e "${YELLOW}⚠️  frontend/.env.local already exists, skipping${NC}"
fi

# Backend .env
if [ ! -f backend/.env ]; then
    cat > backend/.env << EOF
# Application
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
SECRET_KEY=$(openssl rand -hex 32)

# Database
DATABASE_URL=postgresql://agentnexus:dev_password_change_in_prod@localhost:5432/agent_nexus

# Redis
REDIS_URL=redis://localhost:6379/0

# Qdrant
QDRANT_URL=http://localhost:6333

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=False

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Optional: Add your API keys
# ANTHROPIC_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here
EOF
    echo -e "${GREEN}✅ Created backend/.env${NC}"
else
    echo -e "${YELLOW}⚠️  backend/.env already exists, skipping${NC}"
fi
echo ""

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis qdrant minio
echo -e "${GREEN}✅ Docker services started${NC}"
echo ""

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
cd backend
source venv/bin/activate || . venv/Scripts/activate
export PYTHONPATH=$(pwd)
alembic upgrade head || echo -e "${YELLOW}⚠️  Migrations not set up yet, will create tables on first run${NC}"
cd ..
echo ""

# Setup complete
echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Start the development servers:"
echo "   ${YELLOW}pnpm dev${NC}"
echo ""
echo "2. Open your browser:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo "   MinIO Console: http://localhost:9001 (admin/admin)"
echo ""
echo "3. Read the documentation:"
echo "   ${YELLOW}cat README.md${NC}"
echo ""
echo "Happy coding! 🤖"
