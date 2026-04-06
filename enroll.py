import os
import cv2
import pickle
import torch
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1

# --- Setup Models ---
device = torch.device('cpu')
detector = MTCNN(keep_all=False, device=device)
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)

def recognize_face(test_image_path):
    # 1. Locate and load the database
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "face_database.pkl")
    
    if not os.path.exists(db_path):
        print(" Error: face_database.pkl not found! Run enroll.py first.")
        return

    with open(db_path, "rb") as f:
        database = pickle.load(f)

    # 2. Load the test image
    if not os.path.exists(test_image_path):
        print(f" Error: Test image '{test_image_path}' not found.")
        return
        
    img = cv2.imread(test_image_path)
    if img is None:
        print(f" Error: Could not read '{test_image_path}'. Check if the file is corrupted.")
        return
        
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 3. Detect the face
    face = detector(img_rgb)
    if face is None:
        print(" Warning: No face detected in the test image.")
        return

    # 4. Create an embedding for the new face
    with torch.no_grad():
        embedding = model(face.unsqueeze(0))
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)
        test_embedding = embedding.numpy().flatten()

    # 5. Compare with the database
    min_dist = float("inf")
    identity = "Unknown"

    print("\n--- Comparing Faces ---")
    for name, db_embedding in database.items():
        # Calculate the Euclidean distance
        dist = np.linalg.norm(db_embedding - test_embedding)
        print(f" Distance to {name}: {dist:.4f}")
        
        if dist < min_dist:
            min_dist = dist
            identity = name

    # 6. Make a decision based on a threshold (lower distance = better match)
    threshold = 0.9 
    
    print("\n--- Final Result ---")
    if min_dist < threshold:
        print(f" MATCH FOUND: {identity} (Confidence Distance: {min_dist:.4f})")
    else:
        print(f" UNKNOWN. Closest match was {identity}, but distance ({min_dist:.4f}) is too high.")

# --- Execution ---
if __name__ == "__main__":
    # Updated to point directly to your rocky.jpg file
    test_photo = "rocky.jpg" 
    
    recognize_face(test_photo)