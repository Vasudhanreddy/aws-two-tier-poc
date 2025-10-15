#!/bin/bash

# NOTE: Environment variables (DB_ENDPOINT, etc.) should be set in the EC2 instance's
# environment or retrieved via an initialization script/Secrets Manager.
# For simplicity here, we assume they are configured in the environment 
# where this script runs (e.g., in the CodeDeploy AppSpec file).

# Stop the existing Gunicorn process (if running)
if pgrep gunicorn > /dev/null
then
    echo "Stopping existing Gunicorn process..."
    pkill gunicorn
else
    echo "Gunicorn is not running."
fi

# Start Gunicorn to serve the Flask application on port 80
echo "Starting Gunicorn on port 80..."
# We use the current directory (where app.py is deployed)
/usr/local/bin/gunicorn3 --bind 0.0.0.0:80 app:app --daemon
echo "Application started."
