# utils.py
from cryptography.fernet import Fernet
import os

# Generate encryption key (Run once)
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Load encryption key
def load_key():
    return open("key.key", "rb").read()

# Encrypt data
def encrypt_data(data):
    key = load_key()
    cipher = Fernet(key)
    return cipher.encrypt(data.encode())

# Decrypt data
def decrypt_data(encrypted_data):
    key = load_key()
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_data).decode()

# Run to generate the key (only once)
if __name__ == "__main__":
    generate_key()
    print("Encryption key generated!")
