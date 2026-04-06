from flask import Flask, jsonify
from flask_cors import CORS
import os
import enroll  # Links to your enroll.py
import main    # Links to your main.py

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Backend is running!"})

@app.route('/api/data')
def get_data():
    try:
        # CRITICAL: If your function in enroll.py is NOT named 'get_results', 
        # change the word below to match your function name!
        result = enroll.get_results() 
        return jsonify(result)
    except Exception as e:
        # This will tell you EXACTLY why it crashed in the browser
        return jsonify({"error": str(e), "type": "Logic Error"}), 500

# Do NOT add app.run()
