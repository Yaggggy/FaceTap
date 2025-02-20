import sqlite3

DATABASE_PATH = "database/database.db"

with sqlite3.connect(DATABASE_PATH) as conn:
    cursor = conn.cursor()
    
    # Check current table structure
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    if "encrypted_id" in column_names:
        print("✅ 'encrypted_id' column exists. Consider adding a default value if needed.")

    else:
        print("🔹 'encrypted_id' does not exist. No issue there.")
