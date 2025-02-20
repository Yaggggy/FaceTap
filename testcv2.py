import logging
import os
import uuid
import time
import sqlite3
import numpy as np
import cv2
import face_recognition
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Initialize FastAPI
app = FastAPI()

# Database Path
DATABASE_PATH = "database/database.db"

# Logging Setup
LOG_FILE = "logs/api.log"
os.makedirs("logs", exist_ok=True)  # Ensure logs directory exists

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("🚀 API Server Started")

# Ensure database directory exists
if not os.path.exists("database"):
    os.makedirs("database", exist_ok=True)

# Ensure users table exists
with sqlite3.connect(DATABASE_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            encrypted_id TEXT UNIQUE NOT NULL,
            face_encoding BLOB NOT NULL
        )
    """)
    conn.commit()

logging.info("✅ Database and users table ensured")

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="templates/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend index.html"""
    logging.info("🖥️ Served frontend to client")
    return FileResponse("templates/index.html")


@app.get("/register-page", response_class=HTMLResponse)
async def register_page():
    """Serve the registration page"""
    return FileResponse("templates/register.html")


@app.get("/authenticate-page", response_class=HTMLResponse)
async def authenticate_page():
    """Serve the authentication page"""
    return FileResponse("templates/authenticate.html")


def capture_face_encoding(liveness_check=True, timeout=10):
    """Capture live face encoding with optional liveness check (blink detection)"""
    video_capture = cv2.VideoCapture(0)
    start_time = time.time()
    blink_detected = False

    while time.time() - start_time < timeout:
        ret, frame = video_capture.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_locations = face_recognition.face_locations(frame)

        if liveness_check:
            eyes_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
            eyes = eyes_cascade.detectMultiScale(gray, 1.1, 4)
            if len(eyes) >= 2:
                blink_detected = True

        if face_locations and (not liveness_check or blink_detected):
            face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
            video_capture.release()
            return face_encoding  

    video_capture.release()
    return None  


@app.post("/register/")
async def register_user(name: str = Form(...)):
    """Register a new user using webcam image"""
    try:
        encrypted_id = str(uuid.uuid4())  # Generate a unique encrypted_id

        face_encoding = capture_face_encoding(liveness_check=False)
        if face_encoding is None:
            logging.warning("⚠️ No face detected during registration")
            return JSONResponse(status_code=400, content={"detail": "No face detected. Try again."})

        encoded_face_bytes = np.array(face_encoding).tobytes()

        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (name, encrypted_id, face_encoding) VALUES (?, ?, ?)", 
                           (name, encrypted_id, encoded_face_bytes))
            conn.commit()

        logging.info(f"✅ User {name} registered successfully with ID {encrypted_id}")

        return JSONResponse(content={"message": f"User {name} registered successfully!", "encrypted_id": encrypted_id})

    except Exception as e:
        logging.error(f"❌ Error during registration: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.post("/authenticate/")
async def authenticate_user():
    """Authenticate a user using webcam image"""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, encrypted_id, face_encoding FROM users")
            users = cursor.fetchall()

        if not users:
            logging.warning("⚠️ Authentication failed - No users found in database")
            return JSONResponse(status_code=404, content={"detail": "No users found in database"})

        face_encoding = capture_face_encoding(liveness_check=True)
        if face_encoding is None:
            logging.warning("⚠️ No face detected during authentication")
            return JSONResponse(status_code=400, content={"detail": "No face detected. Try again."})

        for name, encrypted_id, stored_encoding in users:
            stored_encoding_np = np.frombuffer(stored_encoding, dtype=np.float64)
            match = face_recognition.compare_faces([stored_encoding_np], face_encoding, tolerance=0.5)

            if match[0]:  # Authentication success
                logging.info(f"✅ Authentication successful for user {name}")
                return JSONResponse(content={"message": f"User authenticated: {name}", "encrypted_id": encrypted_id})

        logging.warning("⚠️ Authentication failed - No matching face found")
        return JSONResponse(status_code=401, content={"detail": "Authentication failed"})

    except Exception as e:
        logging.error(f"❌ Error during authentication: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": str(e)})


if __name__ == "__main__":
    import uvicorn
    logging.info("🚀 Running API Server on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
