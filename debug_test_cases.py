#!/usr/bin/env python3
"""
Debug script to check what tables the test cases are expecting
"""
import sys
import os
import pandas as pd

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

from src.excel_test_case_reader import ExcelTestCaseReader

def check_test_expectations():
    """Check what tables the test cases are expecting"""
    try:
        # Read the Excel test cases
        reader = ExcelTestCaseReader("inputs/test_suite.xlsx")
        
        # Get test case details for all enabled sheets
        all_test_data = reader.get_test_case_details()
        
        print(f"📊 Enabled sheets: {list(all_test_data.keys())}")
        
        # Get test case details for SMOKE sheet
        if 'SMOKE' in all_test_data:
            df_smoke = all_test_data['SMOKE']
            
            print(f"\n🔍 Analyzing SMOKE test cases...")
            print(f"Total test cases: {len(df_smoke)}")
            
            # Look for table-related tests
            table_tests = []
            for index, row in df_smoke.iterrows():
                test_name = str(row.get('Test_Case_Name', '')).lower()
                if any(keyword in test_name for keyword in ['table', 'products', 'employees', 'orders']):
                    table_tests.append({
                        'name': row.get('Test_Case_Name'),
                        'category': row.get('Test_Category'),
                        'parameters': row.get('Parameters', ''),
                        'description': row.get('Description', '')
                    })
            
            print(f"\n📋 Table-related tests found ({len(table_tests)}):")
            for i, test in enumerate(table_tests, 1):
                print(f"{i:2d}. {test['name']}")
                print(f"    Category: {test['category']}")
                print(f"    Parameters: {test['parameters']}")
                print(f"    Description: {test['description']}")
                print()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_test_expectations()