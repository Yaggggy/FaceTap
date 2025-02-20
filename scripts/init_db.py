import sqlite3

def create_database():
    conn = sqlite3.connect("database/database.db")  # Ensure database exists
    cursor = conn.cursor()

    # Drop the old table (if needed)
    cursor.execute("DROP TABLE IF EXISTS users")

    # Create users table with the correct columns
    cursor.execute('''CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        encrypted_id TEXT NOT NULL,
                        face_encoding BLOB NOT NULL)''')

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with the correct schema!")

if __name__ == "__main__":
    create_database()
