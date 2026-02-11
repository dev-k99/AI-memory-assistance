"""
Configuration Test Script
Tests database and Groq API connections before running the main app
"""

import os
from dotenv import load_dotenv
import sys

def test_imports():
    """Test if all required packages are installed"""
    print("Testing package imports...")
    try:
        import streamlit
        import langchain_groq
        import langchain_postgres
        import psycopg2
        print("All packages imported successfully")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_env_variables():
    """Test if environment variables are set"""
    print("\n Testing environment variables...")
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    db_url = os.getenv("DATABASE_URL")
    
    if not groq_key:
        print("GROQ_API_KEY not found in .env")
        return False
    if not db_url:
        print("DATABASE_URL not found in .env")
        return False
    
    print(f"GROQ_API_KEY: {groq_key[:20]}...")
    print(f"DATABASE_URL: {db_url[:30]}...")
    return True

def test_database_connection():
    """Test PostgreSQL connection"""
    print("\n Testing database connection...")
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse connection string
        result = urlparse(db_url)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"Database connected: {version[:50]}...")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'message_store';
        """)
        
        if cursor.fetchone():
            print("Table 'message_store' exists")
        else:
            print("Table 'message_store' not found. Run schema.sql to create tables.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure PostgreSQL is running")
        print("2. Verify DATABASE_URL in .env is correct")
        print("3. Run schema.sql to create tables: psql your_db < schema.sql")
        return False

def test_groq_api():
    """Test Groq API connection"""
    print("\n Testing Groq API connection...")
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    
    try:
        from langchain_groq import ChatGroq
        
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=groq_key,
            max_tokens=50
        )
        
        response = llm.invoke("Say 'Hello, connection successful!' in 5 words or less.")
        print(f"Groq API connected")
        print(f"   Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"Groq API connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Verify GROQ_API_KEY in .env is correct")
        print("2. Check your Groq account at console.groq.com")
        print("3. Ensure you have sufficient API credits")
        return False

def main():
    print("=" * 60)
    print("AI Assistant Configuration Test")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Package Imports", test_imports()))
    results.append(("Environment Variables", test_env_variables()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Groq API", test_groq_api()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("All tests passed! You're ready to run the app:")
        print("   streamlit run app.py")
    else:
        print("Some tests failed. Please fix the issues above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())