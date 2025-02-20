import cv2
import face_recognition
import sqlite3
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.encryption_service import decrypt_data

def authenticate_user():
    conn = sqlite3.connect("database/database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, encrypted_id, face_encoding FROM users")
    users = cursor.fetchall()
    
    if not users:
        print("❌ No users found in the database.")
        return

    # Capture image for authentication
    video_capture = cv2.VideoCapture(0)
    print("📷 Looking for a match... Please look at the camera.")
    ret, frame = video_capture.read()
    video_capture.release()
    cv2.destroyAllWindows()

    if not ret:
        print("❌ Failed to capture image.")
        return

    # Detect and encode face
    face_locations = face_recognition.face_locations(frame)
    if len(face_locations) == 0:
        print("❌ No face detected. Try again.")
        return

    face_encoding = face_recognition.face_encodings(frame, face_locations)[0]

    # Compare with stored faces
    for name, encrypted_id, stored_encoding in users:
        stored_encoding_np = np.frombuffer(stored_encoding, dtype=np.float64)
        match = face_recognition.compare_faces([stored_encoding_np], face_encoding, tolerance=0.5)

        if match[0]:
            decrypted_id = decrypt_data(encrypted_id)
            print(f"✅ User authenticated: {name} (ID: {decrypted_id})")
            return

    print("❌ Authentication failed. No match found.")

if __name__ == "__main__":
    authenticate_user()
