"""
Database Setup Script
Run this script to create and initialize your PostgreSQL database.
Works with: local PostgreSQL, Azure Database for PostgreSQL Flexible Server, Supabase.
For Azure: ensure POSTGRES_SSL=require is set in your .env file.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read env variables
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB", "ai_assistant")
POSTGRES_ADMIN_DB = os.getenv("POSTGRES_ADMIN_DB", "postgres")
POSTGRES_SSL = os.getenv("POSTGRES_SSL", "prefer")   # use "require" for Azure / cloud DBs

# Build shared SSL kwarg so every connect() call picks it up automatically
_SSL_KWARGS = {"sslmode": POSTGRES_SSL}


def _validate_env():
    missing = []
    for key, value in {
        "POSTGRES_USER": POSTGRES_USER,
        "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
    }.items():
        if not value:
            missing.append(key)

    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )


def create_database():
    """Create the ai_assistant database if it doesn't exist"""
    print("Creating database...")

    _validate_env()

    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_ADMIN_DB,
            **_SSL_KWARGS,
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s;",
            (POSTGRES_DB,)
        )
        exists = cursor.fetchone()

        if exists:
            print(f"Database '{POSTGRES_DB}' already exists")
        else:
            cursor.execute(f"CREATE DATABASE {POSTGRES_DB}")
            print(f"Database '{POSTGRES_DB}' created successfully")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Error creating database: {e}")
        return False


def initialize_schema():
    """Run the schema.sql file to create tables"""
    print("\n Initializing database schema...")

    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB,
            **_SSL_KWARGS,
        )
        cursor = conn.cursor()

        with open("schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()

        cursor.execute(schema_sql)
        conn.commit()

        print("Schema initialized successfully")

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print("\n📊 Tables created:")
        for table in tables:
            print(f"   - {table[0]}")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Error initializing schema: {e}")
        return False


def test_connection():
    """Test the database connection"""
    print("\n Testing database connection...")

    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB,
            **_SSL_KWARGS,
        )
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"Connected to: {version[:60]}...")

        cursor.execute("SELECT COUNT(*) FROM message_store;")
        count = cursor.fetchone()[0]
        print(f"message_store table accessible (current messages: {count})")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


def main():
    print("=" * 60)
    print("AI Assistant - Database Setup")
    print("=" * 60)

    if not create_database():
        return 1

    if not initialize_schema():
        return 1

    if not test_connection():
        return 1

    print("\n" + "=" * 60)
    print("Database setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python test_config.py")
    print("2. Run: streamlit run app.py\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
