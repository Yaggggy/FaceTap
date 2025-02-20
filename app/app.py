# app.py (Flask API)
from flask import Flask, request, jsonify
from authenticate_user import authenticate_user
from register_user import register_user

app = Flask(__name__)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    register_user(data["name"], data["user_id"])
    return jsonify({"message": "User registered successfully!"})

@app.route("/authenticate", methods=["POST"])
def authenticate():
    result = authenticate_user()
    return jsonify({"message": result})

if __name__ == "__main__":
    app.run(debug=True)
