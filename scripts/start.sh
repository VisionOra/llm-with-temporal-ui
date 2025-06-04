#!/bin/bash

# Temporal LLM Web App Startup Script
# This script provides easy commands for running the application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

# Check if .env file exists
check_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found!"
        if [ -f "env.example" ]; then
            print_status "Copying env.example to .env"
            cp env.example .env
            print_warning "Please edit .env file with your OpenAI API key before proceeding"
            echo
            echo "Required: OPENAI_API_KEY=your_openai_api_key_here"
            echo
            exit 1
        else
            print_error "No env.example file found!"
            exit 1
        fi
    fi
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose not found. Please install Docker Compose."
        exit 1
    fi
}

# Start all services with Docker Compose
start_all() {
    print_header "Starting Temporal LLM Web App"
    
    check_env_file
    check_docker
    check_docker_compose
    
    print_status "Starting all services..."
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Checking service health..."
    
    # Wait for Temporal to be ready
    timeout=60
    counter=0
    while [ $counter -lt $timeout ]; do
        if curl -s http://localhost:7233 > /dev/null; then
            print_status "Temporal server is ready!"
            break
        fi
        sleep 2
        counter=$((counter + 2))
        echo -n "."
    done
    echo
    
    if [ $counter -ge $timeout ]; then
        print_warning "Temporal server may not be ready yet, but continuing..."
    fi
    
    print_status "Services started successfully!"
    echo
    print_status "Access points:"
    echo "  🌐 Web Application: http://localhost:8000"
    echo "  📊 Temporal Web UI: http://localhost:8080"
    echo "  📚 API Documentation: http://localhost:8000/docs"
    echo "  💾 Health Check: http://localhost:8000/api/health"
    echo
    print_status "View logs with: $0 logs"
    print_status "Stop services with: $0 stop"
}

# Stop all services
stop_all() {
    print_header "Stopping Services"
    docker-compose down
    print_status "All services stopped."
}

# Show logs
show_logs() {
    service=${2:-""}
    if [ -z "$service" ]; then
        print_header "Showing All Logs"
        docker-compose logs -f
    else
        print_header "Showing Logs for $service"
        docker-compose logs -f "$service"
    fi
}

# Restart services
restart_all() {
    print_header "Restarting Services"
    stop_all
    sleep 2
    start_all
}

# Build images
build_images() {
    print_header "Building Docker Images"
    docker-compose build
    print_status "Images built successfully!"
}

# Run tests
run_tests() {
    print_header "Running Tests"
    
    if [ ! -d ".venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    
    print_status "Installing dependencies..."
    pip install -r backend/requirements.txt
    
    print_status "Running tests..."
    cd backend
    pytest -v --tb=short
    cd ..
    
    print_status "Tests completed!"
}

# Setup development environment
setup_dev() {
    print_header "Setting Up Development Environment"
    
    check_env_file
    
    print_status "Creating Python virtual environment..."
    python3 -m venv .venv
    
    print_status "Activating virtual environment..."
    source .venv/bin/activate
    
    print_status "Installing Python dependencies..."
    pip install -r backend/requirements.txt
    
    print_status "Starting Temporal server..."
    docker-compose up -d temporal postgresql elasticsearch temporal-web
    
    print_status "Development environment ready!"
    echo
    print_status "To run the application manually:"
    echo "  1. Activate virtual environment: source .venv/bin/activate"
    echo "  2. Start worker: cd backend && python worker.py"
    echo "  3. Start web app: cd backend && python main.py"
}

# Clean up Docker resources
cleanup() {
    print_header "Cleaning Up Docker Resources"
    
    print_status "Stopping and removing containers..."
    docker-compose down -v
    
    print_status "Removing images..."
    docker-compose down --rmi all
    
    print_status "Removing volumes..."
    docker volume prune -f
    
    print_status "Cleanup completed!"
}

# Health check
health_check() {
    print_header "Health Check"
    
    print_status "Checking web application..."
    if curl -s http://localhost:8000/api/health | jq . > /dev/null 2>&1; then
        print_status "✅ Web application is healthy"
        curl -s http://localhost:8000/api/health | jq .
    else
        print_error "❌ Web application is not responding"
    fi
    
    echo
    print_status "Checking Temporal server..."
    if curl -s http://localhost:7233 > /dev/null 2>&1; then
        print_status "✅ Temporal server is healthy"
    else
        print_error "❌ Temporal server is not responding"
    fi
    
    echo
    print_status "Checking Temporal Web UI..."
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        print_status "✅ Temporal Web UI is healthy"
    else
        print_error "❌ Temporal Web UI is not responding"
    fi
}

# Show usage information
show_usage() {
    echo "Temporal LLM Web App - Startup Script"
    echo
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  start       Start all services (default)"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  logs [svc]  Show logs (optionally for specific service)"
    echo "  build       Build Docker images"
    echo "  test        Run tests"
    echo "  setup       Setup development environment"
    echo "  health      Check service health"
    echo "  cleanup     Clean up Docker resources"
    echo "  help        Show this help message"
    echo
    echo "Services available for logs:"
    echo "  web-app, worker, temporal, temporal-web, postgresql, elasticsearch"
    echo
    echo "Examples:"
    echo "  $0 start          # Start all services"
    echo "  $0 logs web-app   # Show web app logs"
    echo "  $0 test           # Run tests"
}

# Main script logic
case "${1:-start}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    logs)
        show_logs "$@"
        ;;
    build)
        build_images
        ;;
    test)
        run_tests
        ;;
    setup)
        setup_dev
        ;;
    health)
        health_check
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo
        show_usage
        exit 1
        ;;
esac 