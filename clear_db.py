#!/usr/bin/env python3
"""Simple script to clear the trading database and reset to default state."""

import sqlite3
import os

def clear_database():
    db_path = 'data/trading.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found.")
        return
    
    print(f"🗑️  Clearing database: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear all tables
        tables = ['portfolio', 'cash', 'trade_log', 'portfolio_history']
        
        for table in tables:
            try:
                cursor.execute(f'DELETE FROM {table}')
                rows_deleted = cursor.rowcount
                print(f"✅ Cleared {table}: {rows_deleted} rows deleted")
            except sqlite3.Error as e:
                print(f"⚠️  Error clearing {table}: {e}")
        
        # Insert default cash balance of $10,000
        try:
            cursor.execute('INSERT INTO cash (balance) VALUES (?)', (10000.0,))
            print("💰 Set initial cash balance to $10,000")
        except sqlite3.Error as e:
            print(f"⚠️  Error setting cash balance: {e}")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("✅ Database cleared successfully!")
        print("🚀 Ready to start fresh - you can now run the app!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    clear_database()
