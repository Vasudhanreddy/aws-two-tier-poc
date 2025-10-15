# NOTE: This file is now embedded directly into the poc-infra.yaml UserData script
# for automatic deployment. This is the logic that runs on the EC2 instance.

import os
import json
import psycopg2
from flask import Flask, request, jsonify
from passlib.hash import pbkdf2_sha256

# --- Configuration from Environment Variables ---
# These are injected by the CloudFormation UserData script
DB_ENDPOINT = os.environ.get("DB_ENDPOINT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USERNAME")
DB_PASS = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")

app = Flask(__name__)

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_ENDPOINT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        # In a real app, this would log to CloudWatch
        print(f"Database connection error: {e}")
        return None

def initialize_db():
    """Creates the 'users' table if it does not exist."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Simple users table to store email and hashed password
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                );
            """)
            conn.commit()
            cursor.close()
        except Exception as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    # Hash the password securely
    password_hash = pbkdf2_sha256.hash(password)
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database unavailable"}), 503

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
            (email, password_hash)
        )
        conn.commit()
        cursor.close()
        return jsonify({"message": "User created successfully"}), 201
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return jsonify({"error": "User already exists"}), 409
    except Exception as e:
        conn.rollback()
        print(f"Signup error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database unavailable"}), 503
    
    user_data = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
    except Exception as e:
        print(f"Login database error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        conn.close()

    if user_data:
        stored_hash = user_data[0]
        # Verify the password against the stored hash
        if pbkdf2_sha256.verify(password, stored_hash):
            return jsonify({"message": f"Login successful for {email}"}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/')
def serve_frontend():
    """Serves the frontend file."""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "Frontend file not found. Ensure index.html is in the application directory.", 500

# Initialization call happens outside the Flask main block
initialize_db()

if __name__ == '__main__':
    # This block is used for local testing, not for the Gunicorn deployment on EC2
    app.run(host='0.0.0.0', port=5000)
