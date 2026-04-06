from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import enroll  # This imports your enroll.py file
import main    # This imports your main.py file

app = Flask(__name__)

# Allows your frontend to talk to this backend
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Backend is running!", "status": "success"})

@app.route('/api/enroll', methods=['GET'])
def get_enroll_data():
    try:
        # Replace 'get_data()' with the actual function name inside enroll.py
        data = enroll.get_data() 
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_main():
    try:
        # If your frontend sends data, it arrives here
        user_data = request.json
        # Replace 'run_logic' with the actual function in main.py
        result = main.run_logic(user_data) 
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# IMPORTANT: Do not use app.run() for Vercel
