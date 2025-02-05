#!/bin/bash

# Get the first container ID from docker ps
CONTAINER_ID=$(docker ps -q | head -n 1)

# Check if the container ID is not empty
if [ -z "$CONTAINER_ID" ]; then
    echo "No running containers found."
    exit 1
fi

# Enter the container terminal
docker exec -it $CONTAINER_ID sh