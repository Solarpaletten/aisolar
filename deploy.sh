#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== AI Solar 2.0 Enhanced Deployment ===${NC}"

# 1. Pre-deployment checks
echo -e "${YELLOW}=== 1. Environment Checks ===${NC}"
docker --version || { echo -e "${RED}❌ Docker not installed${NC}"; exit 1; }
docker-compose --version || { echo -e "${RED}❌ Docker Compose not installed${NC}"; exit 1; }

# Check .env file
if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# 2. Cleanup and build
echo -e "${YELLOW}=== 2. Cleanup Previous Deployment ===${NC}"
docker-compose down --remove-orphans

echo -e "${YELLOW}=== 3. Building Images ===${NC}"
docker-compose build --no-cache

# 3. Start services
echo -e "${YELLOW}=== 4. Starting Services ===${NC}"
docker-compose up -d

# 4. Wait for services
echo -e "${YELLOW}=== 5. Waiting for Services ===${NC}"
sleep 15

# 5. Health checks
echo -e "${YELLOW}=== 6. Service Health Checks ===${NC}"

# Check PostgreSQL
echo -n "PostgreSQL: "
if docker-compose exec -T postgres pg_isready -U aisolar -q; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${RED}❌ Failed${NC}"
    exit 1
fi

# Check API
echo -n "FastAPI: "
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${RED}❌ Failed${NC}"
    docker-compose logs api --tail=10
    exit 1
fi

# Check Bot
echo -n "Telegram Bot: "
if docker-compose logs bot 2>/dev/null | grep -q "started\|polling\|running"; then
    echo -e "${GREEN}✅ Ready${NC}"
else
    echo -e "${YELLOW}⚠️ Check logs${NC}"
    docker-compose logs bot --tail=5
fi

# 6. Database migrations
echo -e "${YELLOW}=== 7. Database Setup ===${NC}"
echo "Running database migrations..."
docker-compose exec -T api python -c "
from backend.database import engine
from backend.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
" || echo -e "${YELLOW}⚠️ Tables might already exist${NC}"

# 7. API Tests
echo -e "${YELLOW}=== 8. API Testing ===${NC}"
echo -n "Testing endpoints: "

# Test /health
if curl -s http://localhost:8000/health | grep -q "status"; then
    echo -n "/health ✅ "
else
    echo -n "/health ❌ "
fi

# Test /tasks
if curl -s http://localhost:8000/tasks | grep -q "tasks"; then
    echo -n "/tasks ✅ "
else
    echo -n "/tasks ❌ "
fi

# Test /stats
if curl -s http://localhost:8000/stats | grep -q "total_tasks"; then
    echo -n "/stats ✅"
else
    echo -n "/stats ❌"
fi

echo ""

# 8. Container status
echo -e "${YELLOW}=== 9. Final Status ===${NC}"
docker-compose ps

echo -e "${GREEN}=== 🚀 Deployment Complete! ===${NC}"
echo -e "${BLUE}📊 Access points:${NC}"
echo "  • API: http://localhost:8000"
echo "  • API Docs: http://localhost:8000/docs"
echo "  • Telegram Bot: @aisolarbot"
echo "  • Database: localhost:5432"
echo ""
echo -e "${BLUE}📋 Quick tests:${NC}"
echo "  • curl http://localhost:8000/health"
echo "  • curl http://localhost:8000/tasks"
echo "  • Send /start to @aisolarbot"
echo ""
echo -e "${GREEN}✅ AI Solar 2.0 is ready for production!${NC}"