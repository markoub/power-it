#!/usr/bin/env python3
"""
Migration script to add thumbnail_url column to presentations table
"""
import sqlite3
import os

def migrate_database():
    """Add thumbnail_url column to presentations table if it doesn't exist"""
    db_path = "presentations.db"
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. Migration not needed.")
        return
    
    print(f"Migrating database: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if thumbnail_url column already exists
        cursor.execute("PRAGMA table_info(presentations)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'thumbnail_url' in column_names:
            print("Column 'thumbnail_url' already exists. Migration not needed.")
            return
        
        # Add the thumbnail_url column
        cursor.execute("ALTER TABLE presentations ADD COLUMN thumbnail_url TEXT")
        conn.commit()
        
        print("Successfully added 'thumbnail_url' column to presentations table.")
        
        # Show current table structure
        cursor.execute("PRAGMA table_info(presentations)")
        columns = cursor.fetchall()
        print("\nCurrent table structure:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 