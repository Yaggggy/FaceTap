# Smart Queue Reduction System 🚀

## 📌 Overview
The **Smart Queue Reduction System** is an AI-powered solution designed to **eliminate long queues** by automating identity verification using **facial recognition with liveness detection**. This system enhances security, reduces wait times, and ensures a seamless access control process in various real-world applications such as **event management, corporate offices, public transport, and voting systems**.

## 🎯 Project Aim
The primary objective of this project is to:
- **Reduce long waiting times** in queues through automated verification.
- **Enhance security** by preventing unauthorized access and spoofing.
- **Improve efficiency** with AI-driven authentication and real-time queue analytics.
- **Provide scalable & secure access control solutions** using cloud integration.

## 🔥 Key Features
✅ **AI-powered facial recognition** for fast authentication.  
✅ **Liveness detection** to prevent spoofing (e.g., photos/videos).  
✅ **Queue management dashboard** for real-time monitoring & control.  
✅ **Encrypted face data storage** using **Fernet encryption** for security.  
✅ **Real-time logs & analytics** for tracking authentication events.  
✅ **Multi-camera support** (upcoming) for large-scale access points.  
✅ **AWS Cloud integration** (upcoming) for centralized monitoring.  

## 🛠️ Technologies Used
- **Programming Language:** Python 🐍
- **AI & Computer Vision:** OpenCV, dlib, face_recognition
- **Liveness Detection:** dlib’s 68-point facial landmark model (blink detection)
- **Web Framework:** Flask (for web-based dashboard)
- **Database:** SQLite (encrypted face encodings storage)
- **Security:** Fernet encryption (cryptography module)
- **Logging & Monitoring:** Python `logging` module
- **Frontend (Upcoming):** HTML, CSS, JavaScript (for admin dashboard UI)
- **Cloud Services (Upcoming):** AWS CloudWatch for centralized logging

## 🚀 Installation & Setup
### 1️⃣ Prerequisites
Ensure you have **Python 3.8+** and install the required dependencies:
```bash
pip install opencv-python dlib face_recognition cryptography flask sqlite3
```

### 2️⃣ Clone the Repository
```bash
git clone https://github.com/Yaggggy/presence.git
cd presence
```

### 3️⃣ Initialize the Database
```bash
python scripts/init_db.py
```

### 4️⃣ Run the System
```bash
python scripts/main.py
```

## 🔍 How It Works
1️⃣ **User stands in front of the camera** – System captures a real-time image.  
2️⃣ **Liveness detection** – Ensures a live person is present, preventing spoofing.  
3️⃣ **Face encoding extraction** – Compares against encrypted data in SQLite.  
4️⃣ **Authentication decision** – Access is granted or denied.  
5️⃣ **Logging & analytics** – Stores access logs for monitoring.  

## 🚧 Future Enhancements
- **Real-time queue status & live monitoring dashboard.**
- **Multi-camera tracking for large-scale authentication.**
- **AWS-based centralized logging & monitoring.**
- **Mobile app integration for on-the-go authentication.**
- **Advanced anti-spoofing techniques (e.g., 3D face detection).**

## 📌 Applications
✔ **Concerts & Events:** Secure ticket verification.  
✔ **Corporate Offices:** Employee access control.  
✔ **Voting Systems:** Fraud-proof identity authentication.  
✔ **Public Transport:** AI-driven ticket validation.  



---
💡 **Developed with passion by Yagyansh Singh Deshwal** 🚀
