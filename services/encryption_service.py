from cryptography.fernet import Fernet

# Load the encryption key
def load_key():
    with open("key.key", "rb") as key_file:
        return key_file.read()

# Initialize Fernet cipher
encryption_key = load_key()
cipher = Fernet(encryption_key)

def encrypt_data(data):
    """Encrypts a given string using Fernet encryption."""
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    """Decrypts a given encrypted string."""
    return cipher.decrypt(encrypted_data.encode()).decode()
