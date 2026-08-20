import sqlite3

def migrate():
    try:
        conn = sqlite3.connect('verisense.db')
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(scan_history)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'user' not in columns:
            cursor.execute("ALTER TABLE scan_history ADD COLUMN user TEXT DEFAULT 'System User'")
            print("Added user column")
            
        if 'advice' not in columns:
            cursor.execute("ALTER TABLE scan_history ADD COLUMN advice TEXT")
            print("Added advice column")
            
        conn.commit()
        conn.close()
        print("Migration successful")
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
