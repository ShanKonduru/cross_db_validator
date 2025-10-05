#!/usr/bin/env python3
"""
Debug script to show exactly how database connections are determined
"""
import sys
import os
from dotenv import load_dotenv

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.database_config_manager import DatabaseConfigManager
from src.database_test_framework import DatabaseConnectionFactory
from src.excel_test_case_reader import ExcelTestCaseReader

def trace_database_connection():
    """Trace how the database connection is determined"""
    
    load_dotenv()
    
    print("🔍 TRACING DATABASE CONNECTION LOGIC")
    print("=" * 60)
    
    # Step 1: Get the Excel data to see what Environment/Application is being used
    print("\n📊 STEP 1: Reading Excel Test Configuration")
    reader = ExcelTestCaseReader("inputs/test_suite.xlsx")
    all_data = reader.get_test_case_details()
    
    if 'SMOKE' in all_data:
        df = all_data['SMOKE']
        first_row = df.iloc[0]
        
        environment = first_row.get('Environment_Name')
        application = first_row.get('Application_Name')
        
        print(f"   Environment from Excel: {environment}")
        print(f"   Application from Excel: {application}")
    
    # Step 2: Show the credential lookup
    print(f"\n🔐 STEP 2: Credential Lookup")
    username_var = f"{environment}_{application}_USERNAME"
    password_var = f"{environment}_{application}_PASSWORD"
    
    username = os.getenv(username_var)
    password = os.getenv(password_var)
    
    print(f"   Looking for env vars: {username_var}, {password_var}")
    print(f"   Username found: {username}")
    print(f"   Password found: {'***' if password else 'None'}")
    
    # Step 3: Show the configuration lookup
    print(f"\n⚙️  STEP 3: Database Configuration Lookup")
    config_manager = DatabaseConfigManager("configs/database_connections.json")
    config = config_manager.get_connection_details(environment.upper(), application.upper())
    
    if config:
        print(f"   Database Type: {config.get('db_type')}")
        print(f"   Host: {config.get('host')}")
        print(f"   Port: {config.get('port')}")
        print(f"   Database: {config.get('database')}")
        print(f"   Schema: {config.get('schema')}")
    else:
        print("   ❌ No configuration found!")
    
    # Step 4: Show the actual connection creation
    print(f"\n🔌 STEP 4: Creating Database Connection")
    factory = DatabaseConnectionFactory()
    connector, message = factory.create_connection(environment, application)
    
    if connector:
        print(f"   ✅ Connector created: {type(connector).__name__}")
        print(f"   Connection details:")
        print(f"     - Host: {connector.host}")
        print(f"     - Port: {connector.port}")
        print(f"     - Database: {getattr(connector, 'database', 'N/A')}")
        print(f"     - Username: {connector.username}")
        
        # Test the connection
        print(f"\n🧪 STEP 5: Testing Database Connection")
        success, connect_message = connector.connect()
        if success:
            print(f"   ✅ Connection successful!")
            
            # Show what schema we're actually in
            query = "SELECT current_database(), current_schema()"
            success, result = connector.execute_query(query)
            if success and result:
                database_name = result[0][0]
                schema_name = result[0][1]
                print(f"   📍 Currently connected to:")
                print(f"     - Database: {database_name}")
                print(f"     - Schema: {schema_name}")
            
            # Show what tables exist in current schema
            table_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = current_schema() 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
            """
            success, tables = connector.execute_query(table_query)
            if success and tables:
                print(f"   📋 Tables in current schema ({schema_name}):")
                for table in tables[:10]:  # Show first 10 tables
                    print(f"     - {table[0]}")
                if len(tables) > 10:
                    print(f"     ... and {len(tables) - 10} more tables")
            else:
                print(f"   📋 No tables found in schema '{schema_name}'")
            
            connector.disconnect()
        else:
            print(f"   ❌ Connection failed: {connect_message}")
    else:
        print(f"   ❌ Failed to create connector: {message}")
    
    print(f"\n" + "=" * 60)
    print("🎯 SUMMARY:")
    print(f"   The program connects to: {config.get('host')}:{config.get('port')}")
    print(f"   Database: {config.get('database')}")
    print(f"   Default Schema: {config.get('schema')}")
    print(f"   Using credentials: {username_var}/{password_var}")

if __name__ == "__main__":
    trace_database_connection()