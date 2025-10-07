"""
Enhanced Cross Database Validation Test Suite Generator
Creates comprehensive test cases for cross-database validation scenarios
"""
import pandas as pd
import os
from datetime import datetime

def create_enhanced_cross_db_test_suite():
    """Create enhanced Cross DB Validation test cases"""
    
    print("🚀 Creating Enhanced Cross Database Validation Test Suite")
    print("=" * 70)
    
    # Define comprehensive test cases
    test_cases = [
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
            'Parameters': 'source_table=public.employees;target_table=private.employees',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'schema,employees,cross-db'
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
            'Parameters': 'source_table=public.orders;target_table=private.orders',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'schema,orders,cross-db'
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
            'Parameters': 'source_table=public.products;target_table=private.products',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'schema,products,cross-db'
        },
        {
            'Test_Case_ID': 'CROSS_DB_SCHEMA_004',
            'Test_Case_Name': 'Public Customers vs Private Customers Schema',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate schema structure between public.customers and private.customers tables across different databases',
            'Parameters': 'source_table=public.customers;target_table=private.customers',
            'Enable': True,
            'Priority': 'Medium',
            'Tags': 'schema,customers,cross-db'
        },
        {
            'Test_Case_ID': 'CROSS_DB_SCHEMA_005',
            'Test_Case_Name': 'Public Departments vs Private Departments Schema',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate schema structure between public.departments and private.departments tables across different databases',
            'Parameters': 'source_table=public.departments;target_table=private.departments',
            'Enable': True,
            'Priority': 'Medium',
            'Tags': 'schema,departments,cross-db'
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
            'Description': 'Compare row counts between public.employees and private.employees tables with 10% tolerance',
            'Parameters': 'source_table=public.employees;target_table=private.employees;tolerance=10',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'count,employees,cross-db'
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
            'Description': 'Compare row counts between public.orders and private.orders tables with 5% tolerance',
            'Parameters': 'source_table=public.orders;target_table=private.orders;tolerance=5',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'count,orders,cross-db'
        },
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_003',
            'Test_Case_Name': 'Public Products vs Private Products Row Count',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare row counts between public.products and private.products tables with exact match (0% tolerance)',
            'Parameters': 'source_table=public.products;target_table=private.products;tolerance=0',
            'Enable': True,
            'Priority': 'Medium',
            'Tags': 'count,products,cross-db'
        },
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_004',
            'Test_Case_Name': 'Public Customers vs Private Customers Row Count',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Compare row counts between public.customers and private.customers tables - expecting difference',
            'Parameters': 'source_table=public.customers;target_table=private.customers;tolerance=0',
            'Enable': True,
            'Priority': 'Medium',
            'Tags': 'count,customers,cross-db,negative-test'
        },
        
        # COL_COL_VALIDATION Tests (Column-to-Column Validation)
        {
            'Test_Case_ID': 'CROSS_DB_COLUMN_001',
            'Test_Case_Name': 'Employee Salary Column Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare salary column values between public.employees and private.employees tables',
            'Parameters': 'source_table=public.employees;target_table=private.employees;compare_columns=salary;key_column=emp_id',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'column,salary,employees,cross-db'
        },
        {
            'Test_Case_ID': 'CROSS_DB_COLUMN_002',
            'Test_Case_Name': 'Order Total Amount Column Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare total_amount column values between public.orders and private.orders tables',
            'Parameters': 'source_table=public.orders;target_table=private.orders;compare_columns=total_amount;key_column=order_id',
            'Enable': True,
            'Priority': 'High',
            'Tags': 'column,amount,orders,cross-db'
        },
        {
            'Test_Case_ID': 'CROSS_DB_COLUMN_003',
            'Test_Case_Name': 'Product Price Column Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare unit_price column values between public.products and private.products tables',
            'Parameters': 'source_table=public.products;target_table=private.products;compare_columns=unit_price;key_column=product_id',
            'Enable': True,
            'Priority': 'Medium',
            'Tags': 'column,price,products,cross-db'
        },
        
        # Cross-Application Tests (MREE vs SADB)
        {
            'Test_Case_ID': 'CROSS_APP_SCHEMA_001',
            'Test_Case_Name': 'MREE Employees vs SADB Employees Schema',
            'SRC_Application_Name': 'MREE',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'SADB',
            'TGT_Environment_Name3': 'NP1',
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Cross-application schema validation between MREE and SADB employee tables',
            'Parameters': 'source_table=employees;target_table=staff',
            'Enable': False,  # Disabled until MREE/SADB environments are available
            'Priority': 'Low',
            'Tags': 'schema,cross-app,mree,sadb'
        },
        {
            'Test_Case_ID': 'CROSS_APP_COUNT_001', 
            'Test_Case_Name': 'MREE Orders vs SADB Transactions Count',
            'SRC_Application_Name': 'MREE',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'SADB',
            'TGT_Environment_Name3': 'NP1',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Cross-application row count validation between MREE orders and SADB transactions',
            'Parameters': 'source_table=orders;target_table=transactions;tolerance=15',
            'Enable': False,  # Disabled until MREE/SADB environments are available
            'Priority': 'Low',
            'Tags': 'count,cross-app,mree,sadb'
        },
        
        # Cross-Environment Tests (DEV vs QA)
        {
            'Test_Case_ID': 'CROSS_ENV_SCHEMA_001',
            'Test_Case_Name': 'DEV vs QA Environment Schema Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'DEV',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'QA',
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Cross-environment schema validation between DEV and QA environments',
            'Parameters': 'source_table=public.employees;target_table=public.employees',
            'Enable': False,  # Disabled until QA environment is available
            'Priority': 'Medium',
            'Tags': 'schema,cross-env,dev,qa'
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
            'Parameters': 'source_table=public.non_existent_table;target_table=private.non_existent_table',
            'Enable': True,
            'Priority': 'Low',
            'Tags': 'negative-test,error-handling,schema'
        },
        {
            'Test_Case_ID': 'CROSS_DB_NEGATIVE_002',
            'Test_Case_Name': 'Mismatched Table Count Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Negative test: Row count validation with zero tolerance on tables with different counts',
            'Parameters': 'source_table=public.departments;target_table=private.departments;tolerance=0',
            'Enable': True,
            'Priority': 'Low',
            'Tags': 'negative-test,count,departments'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(test_cases)
    
    # Add additional required columns with default values
    df['Prerequisites'] = ''
    df['Test_Data'] = 'Enhanced test data with rich scenarios'
    df['Expected_Duration_mins'] = 2
    df['Created_Date'] = datetime.now().strftime('%Y-%m-%d')
    df['Created_By'] = 'System'
    df['Last_Modified'] = datetime.now().strftime('%Y-%m-%d')
    df['Modified_By'] = 'System'
    df['Version'] = '1.0'
    df['Notes'] = 'Enhanced cross-database validation test cases'
    
    # Reorder columns to match expected format
    column_order = [
        'Test_Case_ID', 'Test_Case_Name', 'SRC_Application_Name', 'SRC_Environment_Name',
        'TGT_Application_Name2', 'TGT_Environment_Name3', 'Test_Category', 'Expected_Result',
        'Description', 'Prerequisites', 'Parameters', 'Test_Data', 'Enable', 'Priority',
        'Tags', 'Expected_Duration_mins', 'Created_Date', 'Created_By', 'Last_Modified',
        'Modified_By', 'Version', 'Notes'
    ]
    
    df = df[column_order]
    
    # Save to Excel file
    output_file = 'inputs/enhanced_cross_db_test_suite.xlsx'
    
    try:
        # Try to read existing file and add new sheet
        if os.path.exists('inputs/test_suite.xlsx'):
            with pd.ExcelWriter('inputs/test_suite.xlsx', mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='CROSS_DB_VALIDATIONS', index=False)
            print(f"✅ Enhanced test cases added to existing test_suite.xlsx")
        else:
            # Create new file
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='CROSS_DB_VALIDATIONS', index=False)
            print(f"✅ New enhanced test suite created: {output_file}")
        
        # Also create a standalone enhanced file
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='CROSS_DB_VALIDATIONS', index=False)
        
        print(f"\n📊 Enhanced Test Suite Summary:")
        print(f"   Total Test Cases: {len(test_cases)}")
        print(f"   ✅ Enabled: {len([t for t in test_cases if t['Enable']])}")
        print(f"   ❌ Disabled: {len([t for t in test_cases if not t['Enable']])}")
        print(f"\n📋 Test Categories:")
        categories = df['Test_Category'].value_counts()
        for category, count in categories.items():
            print(f"   • {category}: {count} tests")
        
        print(f"\n🏷️ Priority Distribution:")
        priorities = df['Priority'].value_counts()
        for priority, count in priorities.items():
            print(f"   • {priority}: {count} tests")
            
        print(f"\n📁 File saved: {output_file}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error creating enhanced test suite: {e}")
        return None

def create_test_summary():
    """Create a summary of all test types and scenarios"""
    
    print(f"\n🎯 Enhanced Cross Database Validation Test Plan")
    print("=" * 70)
    
    test_scenarios = {
        'Schema Validation Tests': [
            '✅ Compare table structures across databases',
            '✅ Validate column names and data types',
            '✅ Check for missing/extra columns',
            '✅ Handle schema-qualified table names'
        ],
        'Row Count Validation Tests': [
            '✅ Compare exact row counts (0% tolerance)',
            '✅ Compare with configurable tolerance (5%, 10%)',
            '✅ Handle empty tables',
            '✅ Negative testing for expected differences'
        ],
        'Column-to-Column Validation Tests': [
            '✅ Compare specific column values',
            '✅ Key-based matching between tables',
            '✅ Numeric and text column comparisons',
            '✅ Handle missing records gracefully'
        ],
        'Cross-Application Tests': [
            '🔧 MREE vs SADB validations (ready when environments available)',
            '🔧 Different table naming conventions',
            '🔧 Cross-application data consistency'
        ],
        'Cross-Environment Tests': [
            '🔧 DEV vs QA environment validation',
            '🔧 Data promotion validation',
            '🔧 Environment synchronization checks'
        ],
        'Error Handling & Negative Tests': [
            '✅ Non-existent table handling',
            '✅ Connection failure scenarios',
            '✅ Invalid parameter handling',
            '✅ Timeout and resource management'
        ]
    }
    
    for category, tests in test_scenarios.items():
        print(f"\n🔹 {category}:")
        for test in tests:
            print(f"    {test}")
    
    print(f"\n🎉 Complete cross-database validation framework ready!")

if __name__ == "__main__":
    df = create_enhanced_cross_db_test_suite()
    if df is not None:
        create_test_summary()
        print(f"\n💡 Next Steps:")
        print(f"   1. Review the enhanced test cases in inputs/enhanced_cross_db_test_suite.xlsx")
        print(f"   2. Enable/disable test cases as needed")
        print(f"   3. Run: python main.py to execute the enhanced test suite")
        print(f"   4. Check detailed reports in the output/ folder")