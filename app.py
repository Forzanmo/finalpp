from flask import Flask, jsonify
from flask_cors import CORS
import enroll # This imports your enroll.py file

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return {"message": "Backend is running!"}

# Add the route that actually DOES something
@app.route('/enroll', methods=['POST', 'GET'])
def do_enroll():
    # Call the function inside your enroll.py
    result = enroll.your_function_name() 
    return jsonify(result)
