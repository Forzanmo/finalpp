import os
import cv2
import pickle
import torch
import numpy as np
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from facenet_pytorch import MTCNN, InceptionResnetV1
from deepface import DeepFace

app = FastAPI(title="Face Recognition API")

# Allow your frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Load Models & Database in Memory Once ---
device = torch.device('cpu')
detector = MTCNN(keep_all=False, device=device)
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "face_database.pkl")
if os.path.exists(db_path):
    with open(db_path, "rb") as f:
        database = pickle.load(f)
else:
    database = {}
    print("Warning: face_database.pkl not found!")

@app.post("/analyze-face")
async def analyze_face(file: UploadFile = File(...)):
    # 1. Read the uploaded file into OpenCV
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return {"error": "Invalid image file."}
        
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 2. Detect Face
    face = detector(img_rgb)
    if face is None:
        return {"status": "error", "message": "No face detected"}

    # 3. Create Embedding
    with torch.no_grad():
        embedding = model(face.unsqueeze(0))
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
        test_embedding = embedding.numpy().flatten()

    # 4. Compare with Database
    min_dist = float("inf")
    identity = "Unknown"
    
    for name, db_embedding in database.items():
        dist = np.linalg.norm(db_embedding - test_embedding)
        if dist < min_dist:
            min_dist = dist
            identity = name

    # 5. Build the Response
    threshold = 0.9 
    
    if min_dist < threshold:
        return {
            "status": "success",
            "identity": identity,
            "confidence": float(min_dist),
            "known": True
        }
    else:
        # Unknown face - Run DeepFace for attributes (Age, Gender, Race)
        # Note: DeepFace doesn't have a native "beauty score" model built-in, but handles the rest perfectly.
        temp_path = "temp_uploaded.jpg"
        cv2.imwrite(temp_path, img) # DeepFace prefers reading from a file path
        
        try:
            analysis = DeepFace.analyze(img_path=temp_path, actions=['age', 'gender', 'race'], enforce_detection=False)
            if isinstance(analysis, list):
                analysis = analysis[0]
                
            os.remove(temp_path) # Clean up temp file
            
            return {
                "status": "success",
                "identity": "Unknown",
                "known": False,
                "attributes": {
                    "age": analysis.get('age'),
                    "gender": analysis.get('dominant_gender'),
                    "race": analysis.get('dominant_race')
                }
            }
        except Exception as e:
            if os.path.exists(temp_path): os.remove(temp_path)
            return {"status": "error", "message": f"Could not analyze attributes: {str(e)}"}