#!/usr/bin/env python3
"""
Debug script to check what tables exist in the database
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.database_config_manager import DatabaseConfigManager
from src.postgresql_connector import PostgreSQLConnector

def check_database_tables():
    """Check what tables exist in the database"""
    try:
        # Get credentials from environment variables
        username, password = DatabaseConfigManager.get_credentials("DEV", "RED")
        
        if not username or password:
            print("❌ Missing credentials for DEV/RED")
            return
        
        # Get connection configuration
        config_manager = DatabaseConfigManager("configs/database_connections.json")
        config = config_manager.get_connection_details("DEV", "RED")
        
        if not config:
            print("❌ Missing configuration for DEV/RED")
            return
        
        # Create PostgreSQL connector
        connector = PostgreSQLConnector(
            host=config['host'],
            port=config['port'],
            username=username,
            password=password,
            database=config['database']
        )
        
        # Connect to database
        success, message = connector.connect()
        if not success:
            print(f"❌ Connection failed: {message}")
            return
        
        print(f"✅ Connected to {config['database']} database")
        
        # Query to check what tables exist in the public schema
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """
        
        success, result = connector.execute_query(query)
        
        if success and result:
            print("\n📋 Tables found in public schema:")
            for row in result:
                print(f"  - {row[0]}")
            print(f"\nTotal tables found: {len(result)}")
        else:
            print("❌ No tables found or query failed")
            print(f"Query result: {result}")
        
        # Also check all schemas
        schema_query = """
        SELECT schemaname 
        FROM pg_catalog.pg_tables 
        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
        GROUP BY schemaname
        ORDER BY schemaname;
        """
        
        success, schemas = connector.execute_query(schema_query)
        if success and schemas:
            print(f"\n🗂️  Available schemas:")
            for schema in schemas:
                print(f"  - {schema[0]}")
        
        connector.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    check_database_tables()