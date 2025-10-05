#!/usr/bin/env python3
"""
Show the simple Application_Name -> Environment_Name -> Database mapping
"""
import sys
import os

project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.excel_test_case_reader import ExcelTestCaseReader
from src.database_config_manager import DatabaseConfigManager

def show_simple_mapping():
    print("🎯 SIMPLE APPLICATION -> ENVIRONMENT -> DATABASE MAPPING")
    print("=" * 70)
    
    # Step 1: Read Excel to see what apps/envs are specified
    reader = ExcelTestCaseReader()
    all_data = reader.get_test_case_details()
    
    if 'SMOKE' in all_data:
        df = all_data['SMOKE']
        
        print("\n📊 From test_suite.xlsx:")
        combinations = df[['Application_Name', 'Environment_Name']].drop_duplicates()
        
        for index, row in combinations.iterrows():
            app = row['Application_Name']
            env = row['Environment_Name']
            print(f"   Test specifies: Application='{app}' Environment='{env}'")
        
        # Step 2: Show what database config this maps to
        print(f"\n⚙️  From database_connections.json:")
        config_manager = DatabaseConfigManager("configs/database_connections.json")
        
        for index, row in combinations.iterrows():
            app = row['Application_Name']
            env = row['Environment_Name']
            
            config = config_manager.get_connection_details(env.upper(), app.upper())
            if config:
                print(f"   {env}/{app} -> {config['db_type']} at {config['host']}:{config['port']}/{config['database']}")
                print(f"                Schema: {config.get('schema', 'default')}")
            else:
                print(f"   {env}/{app} -> ❌ No configuration found!")
        
        print(f"\n🔧 How it works:")
        print(f"   1. Excel test_suite.xlsx specifies Application_Name + Environment_Name")
        print(f"   2. System looks up configs/database_connections.json[Environment][Application]")
        print(f"   3. Gets database connection details (host, port, database, schema)")
        print(f"   4. Uses environment variables for credentials: {env.upper()}_{app.upper()}_USERNAME/PASSWORD")
        print(f"   5. Connects and runs the test")

if __name__ == "__main__":
    show_simple_mapping()