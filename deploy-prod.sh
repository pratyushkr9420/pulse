#!/bin/bash
# ==============================================================================
# Pulse Production Deployment Script
# ==============================================================================
#
# This script automates the production deployment of Pulse using Docker Compose.
# It handles environment validation, docker image building, and service startup.
#
# Usage:
#   ./deploy-prod.sh [options]
#
# Options:
#   --build       Force rebuild of Docker images
#   --down        Stop and remove all containers
#   --logs        Show logs after deployment
#   --help        Show this help message
#
# Prerequisites:
#   1. Docker and Docker Compose installed
#   2. docker/.env.prod file with required secrets (copy from .env.prod.example)
#   3. packages/backend/data/stock_news.json file exists
#
# Required in docker/.env.prod:
#   OPENAI_API_KEY=sk-...
#   JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
#
# Important (with defaults):
#   NEXT_PUBLIC_API_URL=<URL accessible from user's browser>
#   ENABLE_METRICS=true (for Prometheus metrics)
#   CORS_ORIGINS=<comma-separated frontend URLs>
#
# Optional in docker/.env.prod:
#   SENTRY_DSN=https://...@sentry.io/...
#   LANGSMITH_API_KEY=lsv2_pt_...
#   LANGSMITH_PROJECT=pulse-prod
#
# ==============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_COMPOSE_FILE="$SCRIPT_DIR/docker/docker-compose.prod.yml"
ENV_FILE="$SCRIPT_DIR/docker/.env.prod"
ENV_EXAMPLE_FILE="$SCRIPT_DIR/docker/.env.prod.example"
DATA_FILE="$SCRIPT_DIR/packages/backend/data/stock_news.json"

# Parse command line arguments
BUILD_FLAG=""
SHOW_LOGS=false
ACTION="up"

while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            BUILD_FLAG="--build"
            shift
            ;;
        --down)
            ACTION="down"
            shift
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "#!/bin/bash" | sed 's/^# //' | sed 's/^#//'
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Check if running with down action
if [ "$ACTION" = "down" ]; then
    print_header "Stopping Pulse Production Environment"
    print_info "Stopping and removing containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    print_success "All containers stopped and removed"
    exit 0
fi

# Start deployment process
print_header "Pulse Production Deployment"

# Step 1: Check prerequisites
print_info "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
print_success "Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    echo "Install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi
print_success "Docker Compose found: $(docker-compose --version)"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    echo "Please start Docker Desktop or the Docker daemon"
    exit 1
fi
print_success "Docker daemon is running"

# Step 2: Check environment file
print_info "Checking environment configuration..."

if [ ! -f "$ENV_FILE" ]; then
    print_error ".env.prod file not found at: $ENV_FILE"
    echo ""
    echo "Create docker/.env.prod by copying the example:"
    echo "  cp docker/.env.prod.example docker/.env.prod"
    echo ""
    echo "Then edit docker/.env.prod with your production values:"
    echo ""
    echo "  OPENAI_API_KEY=sk-..."
    echo "  JWT_SECRET_KEY=\$(openssl rand -hex 32)"
    echo ""
    echo "Important variables (with defaults):"
    echo "  NEXT_PUBLIC_API_URL=http://localhost:8000  # or your production URL"
    echo "  ENABLE_METRICS=true"
    echo "  CORS_ORIGINS=http://localhost:3000"
    echo ""
    echo "Optional variables:"
    echo "  SENTRY_DSN=https://...@sentry.io/..."
    echo "  LANGSMITH_API_KEY=lsv2_pt_..."
    echo "  LANGSMITH_PROJECT=pulse-prod"
    exit 1
fi
print_success "Found docker/.env.prod file"

# Validate required environment variables
source "$ENV_FILE"

if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your-production-key-here" ]; then
    print_error "OPENAI_API_KEY is not set or still using example value in docker/.env.prod"
    echo "Get your API key from: https://platform.openai.com/api-keys"
    exit 1
fi
print_success "OPENAI_API_KEY is set"

if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "your-generated-secret-key-here" ]; then
    print_error "JWT_SECRET_KEY is not set or still using example value in docker/.env.prod"
    echo "Generate one with: openssl rand -hex 32"
    exit 1
fi
print_success "JWT_SECRET_KEY is set"

# Warn if NEXT_PUBLIC_API_URL is default (not an error, but worth noting)
if [ -n "$NEXT_PUBLIC_API_URL" ] && [ "$NEXT_PUBLIC_API_URL" != "http://localhost:8000" ]; then
    print_success "NEXT_PUBLIC_API_URL is configured: $NEXT_PUBLIC_API_URL"
elif [ -z "$NEXT_PUBLIC_API_URL" ]; then
    print_warning "NEXT_PUBLIC_API_URL not set, using default: http://localhost:8000"
    print_info "If accessing from external network, update NEXT_PUBLIC_API_URL in .env.prod"
else
    print_warning "NEXT_PUBLIC_API_URL using default: http://localhost:8000"
    print_info "This works for same-host access. For external access, update in .env.prod"
fi

# Step 3: Check data file
print_info "Checking data file..."

if [ ! -f "$DATA_FILE" ]; then
    print_error "Data file not found at: $DATA_FILE"
    echo "The stock_news.json file is required for data ingestion"
    exit 1
fi

FILE_SIZE=$(du -h "$DATA_FILE" | cut -f1)
print_success "Found stock_news.json ($FILE_SIZE)"

# Step 4: Build and start services
print_header "Starting Deployment"

if [ -n "$BUILD_FLAG" ]; then
    print_info "Building Docker images..."
else
    print_info "Starting services (use --build to rebuild images)..."
fi

# Start docker-compose with production configuration
docker-compose -f "$DOCKER_COMPOSE_FILE" --env-file "$ENV_FILE" up -d $BUILD_FLAG

if [ $? -eq 0 ]; then
    print_success "All services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Step 5: Wait for services to be healthy
print_info "Waiting for services to be healthy..."
sleep 5

# Check service health
BACKEND_HEALTHY=false
RETRIES=0
MAX_RETRIES=30

while [ $RETRIES -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        BACKEND_HEALTHY=true
        break
    fi
    sleep 2
    RETRIES=$((RETRIES + 1))
    echo -n "."
done
echo ""

if [ "$BACKEND_HEALTHY" = true ]; then
    print_success "Backend is healthy and responding"
else
    print_warning "Backend health check timed out (this may be normal during first startup)"
    print_info "Check logs with: docker-compose -f docker/docker-compose.prod.yml logs backend"
fi

# Step 6: Display deployment summary
print_header "Deployment Summary"

echo "Services running:"
echo "  • Frontend:  http://localhost:3000"
echo "  • Backend:   http://localhost:8000"
echo "  • API Docs:  http://localhost:8000/docs"
if [ "${ENABLE_METRICS:-true}" = "true" ]; then
    echo "  • Metrics:   http://localhost:8000/metrics"
fi
echo ""
echo "Infrastructure:"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis:      localhost:6379"
echo "  • Qdrant:     localhost:6333"
echo ""
echo "Data ingestion:"
echo "  • Automated on first startup (if collection is empty)"
echo "  • Check backend logs for ingestion status"
echo ""
echo "Useful commands:"
echo "  • View logs:    docker-compose -f docker/docker-compose.prod.yml logs -f"
echo "  • Stop all:     ./deploy-prod.sh --down"
echo "  • Restart:      ./deploy-prod.sh"
echo "  • Rebuild:      ./deploy-prod.sh --build"
echo ""

# Show logs if requested
if [ "$SHOW_LOGS" = true ]; then
    print_info "Showing logs (Ctrl+C to exit)..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
fi

print_success "Production deployment complete!"
