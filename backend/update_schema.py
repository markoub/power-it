import os
import sqlite3
import asyncio
from database import init_db

# Path to the database file
DB_PATH = "presentations.db"

async def recreate_database():
    print("Updating database schema...")
    
    # Check if database exists
    if os.path.exists(DB_PATH):
        print(f"Modifying existing database: {DB_PATH}")
        
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Existing tables: {tables}")
        
        # Backup existing data for debug purposes
        try:
            cursor.execute("SELECT * FROM presentations")
            presentations = cursor.fetchall()
            print(f"Found {len(presentations)} existing presentations")
            
            # Save them to a text file for reference
            with open("presentations_backup.txt", "w") as f:
                for p in presentations:
                    f.write(f"{p}\n")
                print("Saved backup to presentations_backup.txt")
        except Exception as e:
            print(f"Error backing up presentations: {e}")
        
        # Delete all presentation steps
        try:
            cursor.execute("DELETE FROM presentation_steps")
            conn.commit()
            print("Deleted all presentation steps")
        except Exception as e:
            print(f"Error deleting presentation steps: {e}")
        
        # Delete all presentations
        try:
            cursor.execute("DELETE FROM presentations")
            conn.commit()
            print("Deleted all presentations")
        except Exception as e:
            print(f"Error deleting presentations: {e}")
        
        # Check if author column exists
        try:
            cursor.execute("PRAGMA table_info(presentations)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            print(f"Presentation table columns: {column_names}")
            
            if "author" not in column_names:
                print("Adding author column to presentations table")
                cursor.execute("ALTER TABLE presentations ADD COLUMN author TEXT")
                conn.commit()
                print("Added author column successfully")
        except Exception as e:
            print(f"Error checking/adding author column: {e}")
        
        # Close connection
        conn.close()
    else:
        print(f"Database file {DB_PATH} not found, creating new database")
        # Initialize the database with the updated schema
        await init_db()
    
    print("Database schema updated successfully!")

if __name__ == "__main__":
    asyncio.run(recreate_database()) 