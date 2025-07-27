"""
Database Migration Script: Add assigned_by_teacher column to HomeworkSchedule table

This script safely adds the new assigned_by_teacher column to the existing database
without losing any existing data.

Run this script after updating the models.py file.
"""

import sqlite3
import os

def migrate_database():
    # Database path
    db_path = os.path.join('instance', 'app.db')
    
    if not os.path.exists(db_path):
        print("Database not found. Creating new database with updated schema.")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(homework_schedule)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'assigned_by_teacher' not in columns:
            print("Adding assigned_by_teacher column to homework_schedule table...")
            
            # Add the new column
            cursor.execute("""
                ALTER TABLE homework_schedule 
                ADD COLUMN assigned_by_teacher INTEGER 
                REFERENCES user(id)
            """)
            
            print("✅ Column added successfully!")
        else:
            print("✅ Column already exists, no migration needed.")
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate_database()
