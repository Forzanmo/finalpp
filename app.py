from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # This handles the CORS issue we discussed earlier

@app.route('/')
def hello():
    return {"message": "Backend is running!"}

# Do NOT use app.run() for Vercel; it handles the serving
