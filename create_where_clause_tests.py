"""
Enhanced Test Suite Generator with WHERE Clause Testing
Creates comprehensive cross-database validation tests with WHERE clause scenarios.
"""

import pandas as pd
import os
from datetime import datetime

def create_where_clause_test_suite():
    """
    Create an enhanced test suite with WHERE clause testing scenarios.
    """
    print("🚀 Creating Enhanced Test Suite with WHERE Clause Testing...")
    
    # Controller sheet data
    controller_data = {
        'SHEET_NAME': ['CROSS_DB_VALIDATIONS'],
        'ENABLE': [True]
    }
    controller_df = pd.DataFrame(controller_data)
    
    # Enhanced test cases with WHERE clause scenarios
    test_cases = [
        # 1. Schema validation tests (existing)
        {
            'Test_Case_ID': 'CROSS_DB_SCHEMA_001',
            'Test_Case_Name': 'Public Employees vs Private Employees Schema',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'SCHEMA_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate schema structure between public.employees and private.employees tables across different databases',
            'Prerequisites': 'Both databases accessible, tables exist',
            'Tags': 'schema,cross-db,validation',
            'Parameters': 'source_table=public.employees,target_table=private.employees',
            'Enable': True
        },
        
        # 2. Row count validation with WHERE clauses - Same WHERE clause for both
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_WHERE_001',
            'Test_Case_Name': 'Employee Count with Same WHERE Filter',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare employee counts with same WHERE clause filter (active employees only)',
            'Prerequisites': 'Both databases accessible, tables exist with status column',
            'Tags': 'row-count,cross-db,where-clause,same-filter',
            'Parameters': 'source_table=public.employees,target_table=private.employees,source_where=status = \'ACTIVE\',target_where=status = \'ACTIVE\',tolerance=10.0',
            'Enable': True
        },
        
        # 3. Row count validation with WHERE clauses - Different WHERE clauses
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_WHERE_002',
            'Test_Case_Name': 'Employee Count with Different WHERE Filters',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare employee counts with different WHERE clause filters (source: active, target: all)',
            'Prerequisites': 'Both databases accessible, tables exist with status column',
            'Tags': 'row-count,cross-db,where-clause,different-filter',
            'Parameters': 'source_table=public.employees,target_table=private.employees,source_where=status = \'ACTIVE\',target_where=,tolerance=50.0',
            'Enable': True
        },
        
        # 4. Row count validation with WHERE clauses - Date-based filtering
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_WHERE_003',
            'Test_Case_Name': 'Order Count with Date Range Filter',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare order counts with date range filtering (orders from last 30 days)',
            'Prerequisites': 'Both databases accessible, tables exist with order_date column',
            'Tags': 'row-count,cross-db,where-clause,date-filter',
            'Parameters': 'source_table=public.orders,target_table=private.orders,source_where=order_date >= CURRENT_DATE - INTERVAL \'30 days\',target_where=order_date >= CURRENT_DATE - INTERVAL \'30 days\',tolerance=5.0',
            'Enable': True
        },
        
        # 5. Column validation with WHERE clauses - Same filters
        {
            'Test_Case_ID': 'CROSS_DB_COLUMN_WHERE_001',
            'Test_Case_Name': 'Employee Email Validation with Status Filter',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare email column values for active employees only between databases',
            'Prerequisites': 'Both databases accessible, tables exist with email and status columns',
            'Tags': 'column,cross-db,where-clause,email-validation',
            'Parameters': 'source_table=public.employees,target_table=private.employees,compare_columns=email,key_column=emp_id,source_where=status = \'ACTIVE\',target_where=status = \'ACTIVE\'',
            'Enable': True
        },
        
        # 6. Column validation with WHERE clauses - Different filters
        {
            'Test_Case_ID': 'CROSS_DB_COLUMN_WHERE_002',
            'Test_Case_Name': 'Order Status Validation with Amount Filter',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare order status for different amount ranges between databases',
            'Prerequisites': 'Both databases accessible, tables exist with order_status and total_amount columns',
            'Tags': 'column,cross-db,where-clause,order-validation',
            'Parameters': 'source_table=public.orders,target_table=private.orders,compare_columns=order_status,key_column=order_id,source_where=total_amount > 1000,target_where=total_amount > 500',
            'Enable': True
        },
        
        # 7. Complex WHERE clause test - Multiple conditions
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_WHERE_004',
            'Test_Case_Name': 'Product Count with Complex WHERE Conditions',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare product counts with complex WHERE conditions (active products with price > 100)',
            'Prerequisites': 'Both databases accessible, tables exist with status and price columns',
            'Tags': 'row-count,cross-db,where-clause,complex-filter',
            'Parameters': 'source_table=public.products,target_table=private.products,source_where=status = \'ACTIVE\' AND price > 100,target_where=status = \'ACTIVE\' AND price > 100,tolerance=15.0',
            'Enable': True
        },
        
        # 8. Negative test - WHERE clause with non-existent column
        {
            'Test_Case_ID': 'CROSS_DB_WHERE_NEGATIVE_001',
            'Test_Case_Name': 'Negative Test: WHERE with Non-existent Column',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Low',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Negative test: Validate error handling for WHERE clause with non-existent column',
            'Prerequisites': 'Both databases accessible, tables exist',
            'Tags': 'negative-test,cross-db,where-clause,error-handling',
            'Parameters': 'source_table=public.employees,target_table=private.employees,source_where=non_existent_column = \'value\',target_where=non_existent_column = \'value\'',
            'Enable': True
        },
        
        # 9. Source-only WHERE clause test
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_WHERE_005',
            'Test_Case_Name': 'Employee Count with Source-only WHERE Filter',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare employee counts with WHERE clause only on source table',
            'Prerequisites': 'Both databases accessible, tables exist with hire_date column',
            'Tags': 'row-count,cross-db,where-clause,source-only',
            'Parameters': 'source_table=public.employees,target_table=private.employees,source_where=hire_date >= \'2020-01-01\',tolerance=70.0',
            'Enable': True
        },
        
        # 10. Target-only WHERE clause test
        {
            'Test_Case_ID': 'CROSS_DB_COUNT_WHERE_006',
            'Test_Case_Name': 'Employee Count with Target-only WHERE Filter',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Compare employee counts with WHERE clause only on target table',
            'Prerequisites': 'Both databases accessible, tables exist with department column',
            'Tags': 'row-count,cross-db,where-clause,target-only',
            'Parameters': 'source_table=public.employees,target_table=private.employees,target_where=department = \'IT\',tolerance=80.0',
            'Enable': True
        }
    ]
    
    # Create DataFrame from test cases
    cross_db_df = pd.DataFrame(test_cases)
    
    # Create Excel file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f'inputs/test_suite_with_where_clauses_{timestamp}.xlsx'
    
    print(f"📝 Writing enhanced test suite to {excel_file}...")
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Write CONTROLLER sheet
        controller_df.to_excel(writer, sheet_name='CONTROLLER', index=False)
        
        # Write CROSS_DB_VALIDATIONS sheet
        cross_db_df.to_excel(writer, sheet_name='CROSS_DB_VALIDATIONS', index=False)
    
    print(f"✅ Enhanced test suite created with {len(test_cases)} test cases!")
    print(f"📊 Test breakdown:")
    print(f"   • Schema validation: 1 test")
    print(f"   • Row count with WHERE clauses: 6 tests")
    print(f"   • Column validation with WHERE clauses: 2 tests")
    print(f"   • Negative test: 1 test")
    print(f"")
    print(f"🔍 WHERE clause scenarios included:")
    print(f"   • Same WHERE clause for source and target")
    print(f"   • Different WHERE clauses for source and target")
    print(f"   • Date-based filtering")
    print(f"   • Complex conditions with AND/OR")
    print(f"   • Source-only WHERE clause")
    print(f"   • Target-only WHERE clause")
    print(f"   • Error handling for invalid WHERE clauses")
    print(f"")
    print(f"💾 File saved: {excel_file}")
    
    return excel_file

if __name__ == "__main__":
    # Create the enhanced test suite
    excel_file = create_where_clause_test_suite()
    
    # Copy to the main test_suite.xlsx file
    import shutil
    main_file = 'inputs/test_suite.xlsx'
    print(f"")
    print(f"🔄 Copying enhanced test suite to main file: {main_file}")
    shutil.copy2(excel_file, main_file)
    print(f"✅ Main test suite updated successfully!")
    print(f"")
    print(f"🚀 Ready to test enhanced WHERE clause functionality!")
    print(f"   Run 'python main.py' to execute the enhanced test suite")