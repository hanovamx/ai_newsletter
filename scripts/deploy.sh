#!/bin/bash

# Exit on any error
set -e

# Update repository
git pull origin main

# Activate virtual environment (create if doesn't exist)
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Create logs directory
mkdir -p logs
chmod 755 logs

# Setup cron job if not exists
CRON_CMD="0 8 * * * cd $(pwd) && source venv/bin/activate && python src/main.py >> logs/newsletter.log 2>&1"
(crontab -l 2>/dev/null | grep -q "$CRON_CMD") || (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

# Verify environment
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one from .env.example"
    exit 1
fi

echo "Deployment completed successfully!" 