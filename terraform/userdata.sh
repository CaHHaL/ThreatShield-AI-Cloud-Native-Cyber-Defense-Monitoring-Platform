#!/bin/bash
set -e

# Redirect all output to a log file for debugging
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1

echo "Starting ThreatShield User Data Script..."

# Update and install dependencies
apt-get update -y
apt-get install -y git curl unzip apt-transport-https ca-certificates software-properties-common

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose Plugin (should be installed by get.docker.com, ensuring it is)
apt-get install -y docker-compose-plugin

# Create directory for the project
echo "Setting up project directory..."
mkdir -p /home/ubuntu/app
cd /home/ubuntu/app

# Clone the repository
echo "Cloning repository from ${github_repo}..."
git clone ${github_repo} .

# Change ownership to ubuntu user so we can work with it later
chown -R ubuntu:ubuntu /home/ubuntu/app

# Set up environment variables
cp .env.example .env

# We'll update the API URLs to the EC2's public IP dynamically inside the frontend build, 
# but for the backend, standard .env is fine.

# Start backend services using docker compose
# We ONLY start backend services, excluding the frontend container since it will be on Vercel
echo "Starting Docker containers..."
docker compose up -d postgres backend cowrie web-login-honeypot prometheus grafana

# Wait for database and backend to initialize
echo "Waiting for services to start..."
sleep 20

# Seed the database
echo "Seeding database..."
docker exec threatshield-backend python seed_data.py || echo "Seeding failed, might already be seeded."

echo "Deployment finished successfully!"
