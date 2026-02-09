"""
Database Setup Script
Run this script to create and initialize your PostgreSQL database
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_database():
    """Create the ai_assistant database if it doesn't exist"""
    print("🗄️  Creating database...")
    
    # Connect to PostgreSQL (default postgres database)
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="VtrCor87",
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='ai_assistant'")
        exists = cursor.fetchone()
        
        if exists:
            print("✅ Database 'ai_assistant' already exists")
        else:
            # Create database
            cursor.execute("CREATE DATABASE ai_assistant")
            print("✅ Database 'ai_assistant' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def initialize_schema():
    """Run the schema.sql file to create tables"""
    print("\n📋 Initializing database schema...")
    
    try:
        # Connect to ai_assistant database
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password=os.getenv("POSTGRES_PASSWORD"),
            database="ai_assistant"
        )
        cursor = conn.cursor()
        
        # Read and execute schema.sql
        with open('schema.sql', 'r') as f:
            schema_sql = f.read()
        
        cursor.execute(schema_sql)
        conn.commit()
        
        print("✅ Schema initialized successfully")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📊 Tables created:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error initializing schema: {e}")
        return False

def test_connection():
    """Test the database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="VtrCor87",
            database="ai_assistant"
        )
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to: {version[:60]}...")
        
        # Test message_store table
        cursor.execute("SELECT COUNT(*) FROM message_store;")
        count = cursor.fetchone()[0]
        print(f"✅ message_store table accessible (current messages: {count})")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🧠 AI Assistant - Database Setup")
    print("=" * 60)
    print()
    
    # Step 1: Create database
    if not create_database():
        print("\n⚠️  Failed to create database. Please check your PostgreSQL installation.")
        return 1
    
    # Step 2: Initialize schema
    if not initialize_schema():
        print("\n⚠️  Failed to initialize schema. Please check schema.sql file.")
        return 1
    
    # Step 3: Test connection
    if not test_connection():
        print("\n⚠️  Failed to connect to database. Please check your credentials.")
        return 1
    
    print("\n" + "=" * 60)
    print("🎉 Database setup complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run: python test_config.py  (to verify full configuration)")
    print("2. Run: streamlit run app.py   (to start the application)")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())