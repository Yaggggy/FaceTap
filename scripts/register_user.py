import cv2
import face_recognition
import sqlite3
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.encryption_service import encrypt_data
from services.log_service import log_info, log_error

def register_user(name, user_id):
    try:
        encrypted_id = encrypt_data(user_id)
        log_info(f"Starting registration for user: {name}")

        # Capture image using webcam
        video_capture = cv2.VideoCapture(0)
        print("📷 Capturing your face... Look at the camera.")
        ret, frame = video_capture.read()
        video_capture.release()
        cv2.destroyAllWindows()

        if not ret:
            log_error("Failed to capture image")
            print("❌ Failed to capture image.")
            return

        # Detect face and generate encoding
        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) == 0:
            log_error("No face detected during registration")
            print("❌ No face detected. Try again.")
            return

        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
        encoded_face_bytes = np.array(face_encoding).tobytes()

        # Save to database
        conn = sqlite3.connect("database/database.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (name, encrypted_id, face_encoding) VALUES (?, ?, ?)",
                       (name, encrypted_id, encoded_face_bytes))

        conn.commit()
        conn.close()

        log_info(f"User {name} registered successfully with encrypted ID: {encrypted_id}")
        print(f"✅ User {name} registered successfully with encrypted ID: {encrypted_id}")

    except Exception as e:
        log_error(f"Error registering user {name}: {str(e)}")
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    name = input("Name: ")
    user_id = input("Unique ID: ")

    try:
        register_user(name, user_id)
    except Exception as e:
        log_error(f"Unexpected error during registration: {str(e)}")
        print(f"❌ Unexpected error: {str(e)}")
