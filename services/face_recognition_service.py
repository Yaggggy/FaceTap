import cv2
import numpy as np
import face_recognition
import sqlite3
import dlib
from scipy.spatial import distance as dist
from cryptography.fernet import Fernet

# Load encryption key (Must be the same as in register_user.py)
encryption_key = b'YOUR_SECRET_KEY_HERE'
cipher = Fernet(encryption_key)

# Load face detection model
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('models/shape_predictor_68_face_landmarks.dat')

# Decrypt face encoding
def decrypt_face_encoding(encrypted_encoding):
    return np.frombuffer(cipher.decrypt(encrypted_encoding), dtype=np.float64)

# Compute eye aspect ratio (EAR) for blink detection
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# Detect if user is blinking
def detect_blink(landmarks, frame):
    (lStart, lEnd) = (42, 48)  # Left eye
    (rStart, rEnd) = (36, 42)  # Right eye

    left_eye = landmarks[lStart:lEnd]
    right_eye = landmarks[rStart:rEnd]

    leftEAR = eye_aspect_ratio(left_eye)
    rightEAR = eye_aspect_ratio(right_eye)
    ear = (leftEAR + rightEAR) / 2.0

    return ear < 0.15  # Adjust threshold as needed

# Recognize face from camera feed
def recognize_face():
    cap = cv2.VideoCapture(0)

    conn = sqlite3.connect('database/database.db')
    c = conn.cursor()
    c.execute("SELECT name, face_encoding FROM users")
    users = c.fetchall()

    known_encodings = {name: decrypt_face_encoding(enc) for name, enc in users}

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        detected_name = "Unknown"
        is_liveness_verified = False

        for encoding, face_location in zip(face_encodings, face_locations):
            for name, known_encoding in known_encodings.items():
                matches = face_recognition.compare_faces([known_encoding], encoding)
                if matches[0]:
                    detected_name = name

                    # Liveness detection
                    for rect in rects:
                        shape = predictor(gray, rect)
                        landmarks = np.array([[shape.part(i).x, shape.part(i).y] for i in range(68)])

                        if detect_blink(landmarks, frame):
                            is_liveness_verified = True

                    break  # Stop checking other users once matched

            # Draw result
            top, right, bottom, left = face_location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            if is_liveness_verified:
                text = f"{detected_name} - Verified ✅"
            else:
                text = f"{detected_name} - Liveness Failed ❌"

            cv2.putText(frame, text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    recognize_face()
