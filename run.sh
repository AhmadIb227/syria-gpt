#!/bin/bash
# Shell script to run the Syria-Gpt project

# Handle the "stop" argument
if [ "$1" == "stop" ]; then
    echo "Stopping the application..."
    docker-compose -f deployment/docker-compose.yml down
    exit 0
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start the Docker containers
echo "Building and starting the Docker containers..."
docker-compose -f deployment/docker-compose.yml up -d --build

# Check if the containers are running
if [ -z "$(docker ps -q -f name=syria-gpt-app -f status=running)" ]; then
    echo "The application container failed to start. Please check the logs."
    exit 1
fi

# Run database migrations
echo "Running database migrations..."
docker exec syria-gpt-app alembic upgrade head

echo ""
echo "The Syria-Gpt application is now running."
echo "You can access the API at http://localhost:9000"
echo "You can access pgAdmin at http://localhost:5050"
echo ""
echo "To stop the application, run this script with the \"stop\" argument:"
echo "  ./run.sh stop"
echo ""
