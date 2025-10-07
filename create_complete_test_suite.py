"""
Complete Test Suite Creator
Creates a comprehensive test suite with all required sheets including CONTROLLER
"""
import pandas as pd
import os
from datetime import datetime

def create_complete_test_suite():
    """Create complete test suite with CONTROLLER and enhanced CROSS_DB_VALIDATIONS sheets"""
    
    print("🚀 Creating Complete Enhanced Test Suite")
    print("=" * 70)
    
    # Create CONTROLLER sheet
    controller_data = [
        {
            'SHEET_NAME': 'CROSS_DB_VALIDATIONS',
            'ENABLE': True,
            'Description': 'Enhanced cross-database validation test cases',
            'Test_Type': 'CROSS_DATABASE_VALIDATION',
            'Priority': 'HIGH',
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Last_Modified': datetime.now().strftime('%Y-%m-%d')
        }
    ]
    
    controller_df = pd.DataFrame(controller_data)
    
    # Enhanced Cross DB Validation test cases
    cross_db_test_cases = [
        # SCHEMA VALIDATION Tests
        {
            'Test_Case_ID': 'CROSS_DB_SCHEMA_001',
            'Test_Case_Name': 'Public Employees vs Private Employees Schema',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1', 
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate schema structure between public.employees and private.employees tables across different databases',
            'Prerequisites': '',
            'Parameters': 'source_table=public.employees;target_table=private.employees',
            'Test_Data': 'Employee table structures',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'schema,employees,cross-db',
            'Expected_Duration_mins': 2,
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Created_By': 'System',
            'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
            'Modified_By': 'System',
            'Version': '1.0',
            'Notes': 'Enhanced cross-database validation test case'
        },
        {
            'Test_Case_ID': 'CROSS_DB_SCHEMA_002',
            'Test_Case_Name': 'Public Orders vs Private Orders Schema',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY', 
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate schema structure between public.orders and private.orders tables across different databases',
            'Prerequisites': '',
            'Parameters': 'source_table=public.orders;target_table=private.orders',
            'Test_Data': 'Order table structures',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'schema,orders,cross-db',
            'Expected_Duration_mins': 2,
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Created_By': 'System',
            'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
            'Modified_By': 'System',
            'Version': '1.0',
            'Notes': 'Enhanced cross-database validation test case'
        },
        {
            'Test_Case_ID': 'CROSS_DB_SCHEMA_003',
            'Test_Case_Name': 'Public Products vs Private Products Schema',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV', 
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate schema structure between public.products and private.products tables across different databases',
            'Prerequisites': '',
            'Parameters': 'source_table=public.products;target_table=private.products',
            'Test_Data': 'Product table structures',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'schema,products,cross-db',
            'Expected_Duration_mins': 2,
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Created_By': 'System',
            'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
            'Modified_By': 'System',
            'Version': '1.0',
            'Notes': 'Enhanced cross-database validation test case'
        },
        
        # ROW COUNT VALIDATION Tests
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_001',
            'Test_Case_Name': 'Public Employees vs Private Employees Row Count',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare row counts between public.employees and private.employees tables with 50% tolerance',
            'Prerequisites': '',
            'Parameters': 'source_table=public.employees;target_table=private.employees;tolerance=50',
            'Test_Data': 'Employee data records',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'count,employees,cross-db',
            'Expected_Duration_mins': 2,
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Created_By': 'System',
            'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
            'Modified_By': 'System',
            'Version': '1.0',
            'Notes': 'Enhanced cross-database validation test case'
        },
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_002',
            'Test_Case_Name': 'Public Orders vs Private Orders Row Count',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare row counts between public.orders and private.orders tables with 50% tolerance',
            'Prerequisites': '',
            'Parameters': 'source_table=public.orders;target_table=private.orders;tolerance=50',
            'Test_Data': 'Order data records',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'count,orders,cross-db',
            'Expected_Duration_mins': 2,
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Created_By': 'System',
            'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
            'Modified_By': 'System',
            'Version': '1.0',
            'Notes': 'Enhanced cross-database validation test case'
        },
        
        # COL_COL_VALIDATION Tests
        {
            'Test_Case_ID': 'CROSS_DB_COLUMN_001',
            'Test_Case_Name': 'Employee Email Column Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare email column values between public.employees and private.employees tables',
            'Prerequisites': '',
            'Parameters': 'source_table=public.employees;target_table=private.employees;compare_columns=email;key_column=emp_id',
            'Test_Data': 'Employee email data',
            'Enable': True,
            'Priority': 'Medium',
            'Tags': 'column,email,employees,cross-db',
            'Expected_Duration_mins': 3,
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Created_By': 'System',
            'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
            'Modified_By': 'System',
            'Version': '1.0',
            'Notes': 'Enhanced cross-database validation test case'
        },
        {
            'Test_Case_ID': 'CROSS_DB_COLUMN_002',
            'Test_Case_Name': 'Order Status Column Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare order_status column values between public.orders and private.orders tables',
            'Prerequisites': '',
            'Parameters': 'source_table=public.orders;target_table=private.orders;compare_columns=order_status;key_column=order_id',
            'Test_Data': 'Order status data',
            'Enable': True,
            'Priority': 'Medium',
            'Tags': 'column,status,orders,cross-db',
            'Expected_Duration_mins': 3,
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Created_By': 'System',
            'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
            'Modified_By': 'System',
            'Version': '1.0',
            'Notes': 'Enhanced cross-database validation test case'
        },
        
        # Negative Test Cases
        {
            'Test_Case_ID': 'CROSS_DB_NEGATIVE_001',
            'Test_Case_Name': 'Non-Existent Table Schema Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Negative test: Validate schema for non-existent table to test error handling',
            'Prerequisites': '',
            'Parameters': 'source_table=public.non_existent_table;target_table=private.non_existent_table',
            'Test_Data': 'N/A - Testing error handling',
            'Enable': True,
            'Priority': 'Low',
            'Tags': 'negative-test,error-handling,schema',
            'Expected_Duration_mins': 1,
            'Created_Date': datetime.now().strftime('%Y-%m-%d'),
            'Created_By': 'System',
            'Last_Modified': datetime.now().strftime('%Y-%m-%d'),
            'Modified_By': 'System',
            'Version': '1.0',
            'Notes': 'Negative test case for error handling validation'
        }
    ]
    
    cross_db_df = pd.DataFrame(cross_db_test_cases)
    
    # Save to Excel file with multiple sheets
    output_file = 'inputs/test_suite.xlsx'
    
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            controller_df.to_excel(writer, sheet_name='CONTROLLER', index=False)
            cross_db_df.to_excel(writer, sheet_name='CROSS_DB_VALIDATIONS', index=False)
        
        print(f"✅ Complete test suite created: {output_file}")
        print(f"\n📊 Test Suite Summary:")
        print(f"   📋 CONTROLLER sheet: {len(controller_data)} enabled sheet(s)")
        print(f"   📋 CROSS_DB_VALIDATIONS sheet: {len(cross_db_test_cases)} test cases")
        print(f"   ✅ Enabled: {len([t for t in cross_db_test_cases if t['Enable']])}")
        print(f"   ❌ Disabled: {len([t for t in cross_db_test_cases if not t['Enable']])}")
        
        print(f"\n📋 Test Categories:")
        categories = cross_db_df['Test_Category'].value_counts()
        for category, count in categories.items():
            print(f"   • {category}: {count} tests")
        
        print(f"\n🏷️ Priority Distribution:")
        priorities = cross_db_df['Priority'].value_counts()
        for priority, count in priorities.items():
            print(f"   • {priority}: {count} tests")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating complete test suite: {e}")
        return False

if __name__ == "__main__":
    success = create_complete_test_suite()
    if success:
        print(f"\n💡 Ready to run enhanced cross-database validation:")
        print(f"   🚀 Execute: python main.py")
        print(f"   📊 Check reports in output/ folder")
        print(f"   🎯 Test comprehensive cross-database validation scenarios")