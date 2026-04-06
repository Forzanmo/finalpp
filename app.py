from flask import Flask, jsonify
from flask_cors import CORS
import enroll  # Make sure this is lowercase to match your filename

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return {"message": "Backend is running!"}

# YOU NEED THIS:
@app.route('/get-data')
def get_data():
    # This calls a function inside your enroll.py file
    data = enroll.some_function_name() 
    return jsonify(data)
