import logging
import os
import sqlite3
import cv2
import numpy as np
import face_recognition
import dlib
import time
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from scipy.spatial import distance as dist

# Initialize FastAPI
app = FastAPI()

# Paths
DATABASE_PATH = "database/database.db"
LOG_FILE = "logs/api.log"
MODEL_PATH = "models/shape_predictor_68_face_landmarks.dat"

# Encryption Key (Must be 16, 24, or 32 bytes long)
ENCRYPTION_KEY = b"mysecretkey123456"  # Replace with a secure key

# Ensure necessary directories exist
os.makedirs("database", exist_ok=True)
os.makedirs("logs", exist_ok=True)
os.makedirs("models", exist_ok=True)

# Logging Setup
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("🚀 API Server Started")

# Ensure SQLite database setup
with sqlite3.connect(DATABASE_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            face_encoding BLOB NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

logging.info("✅ Database setup completed")

# Load Dlib Model
if not os.path.exists(MODEL_PATH):
    logging.error("❌ Missing shape_predictor_68_face_landmarks.dat model!")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(MODEL_PATH)

# Eye landmarks for blink detection
LEFT_EYE = list(range(42, 48))
RIGHT_EYE = list(range(36, 42))


def encrypt_data(data: bytes) -> bytes:
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(cipher.iv + encrypted)


def decrypt_data(encrypted_data: bytes) -> bytes:
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:AES.block_size]
    encrypted_content = encrypted_data[AES.block_size:]
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_content), AES.block_size)


def detect_liveness(frame, face):
    shape = predictor(frame, face)
    left_eye = np.array([(shape.part(n).x, shape.part(n).y) for n in LEFT_EYE])
    right_eye = np.array([(shape.part(n).x, shape.part(n).y) for n in RIGHT_EYE])

    left_ratio = dist.euclidean(left_eye[1], left_eye[5]) / dist.euclidean(left_eye[0], left_eye[3])
    right_ratio = dist.euclidean(right_eye[1], right_eye[5]) / dist.euclidean(right_eye[0], right_eye[3])

    eye_aspect_ratio = (left_ratio + right_ratio) / 2.0
    return eye_aspect_ratio > 0.2  # Adjust threshold as needed


@app.get("/", response_class=FileResponse)
async def serve_frontend():
    logging.info("🖥️ Served frontend")
    return FileResponse("templates/index.html")


@app.post("/register/")
async def register_user(name: str = Form(...)):
    try:
        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        ret, frame = video_capture.read()
        video_capture.release()
        cv2.destroyAllWindows()

        if not ret:
            return JSONResponse(status_code=400, content={"detail": "Failed to capture image"})

        face_locations = face_recognition.face_locations(frame)
        if not face_locations:
            return JSONResponse(status_code=400, content={"detail": "No face detected"})

        face_encodings = face_recognition.face_encodings(frame, face_locations)
        if not face_encodings:
            return JSONResponse(status_code=400, content={"detail": "Face encoding failed"})

        face_encoding = face_encodings[0]
        encrypted_face_encoding = encrypt_data(np.array(face_encoding).tobytes())

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, face_encoding) VALUES (?, ?)", (name, encrypted_face_encoding))
            conn.commit()

        return JSONResponse(content={"message": f"User {name} registered successfully!"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/authenticate/")
async def authenticate_user():
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, face_encoding FROM users")
            users = cursor.fetchall()

        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        ret, frame = video_capture.read()
        video_capture.release()
        cv2.destroyAllWindows()

        if not ret:
            return JSONResponse(status_code=400, content={"detail": "Failed to capture image"})

        face_locations = face_recognition.face_locations(frame)
        if not face_locations:
            return JSONResponse(status_code=400, content={"detail": "No face detected"})

        face_encodings = face_recognition.face_encodings(frame, face_locations)
        if not face_encodings:
            return JSONResponse(status_code=400, content={"detail": "Face encoding failed"})

        face_encoding = face_encodings[0]

        for name, encrypted_encoding in users:
            decrypted_encoding = decrypt_data(encrypted_encoding)
            stored_encoding_np = np.frombuffer(decrypted_encoding, dtype=np.float64)
            match = face_recognition.compare_faces([stored_encoding_np], face_encoding, tolerance=0.5)

            if match[0]:
                with sqlite3.connect(DATABASE_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO logs (user_name, status) VALUES (?, 'Authenticated')", (name,))
                    conn.commit()

                return JSONResponse(content={"message": f"User authenticated: {name}"})

        return JSONResponse(status_code=401, content={"detail": "Authentication failed"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/logs/")
async def get_authentication_logs():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_name, status, timestamp FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()

    if not logs:
        return JSONResponse(status_code=404, content={"detail": "No authentication logs available"})

    formatted_logs = [{"user_name": log[0], "status": log[1], "timestamp": log[2]} for log in logs]
    return JSONResponse(content={"logs": formatted_logs})


if __name__ == "__main__":
    import uvicorn
    logging.info("🚀 Running API Server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
