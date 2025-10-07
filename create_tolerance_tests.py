"""
Comprehensive Tolerance Testing Suite Generator
Creates test cases showcasing soft/hard validations with various tolerance types:
- Date tolerance (days, hours, minutes)
- Float number tolerance (percentage, absolute)
- Record count tolerance (percentage, absolute)
- String tolerance (case sensitivity, whitespace)
- Decimal precision tolerance
"""

import pandas as pd
import os
from datetime import datetime

def create_tolerance_test_suite():
    """
    Create comprehensive test suite with tolerance and soft/hard validation scenarios.
    """
    print("🚀 Creating Comprehensive Tolerance Testing Suite...")
    
    # Controller sheet data
    controller_data = {
        'SHEET_NAME': ['TOLERANCE_VALIDATIONS'],
        'ENABLE': [True]
    }
    controller_df = pd.DataFrame(controller_data)
    
    # Comprehensive tolerance test cases
    test_cases = [
        # 1. Date Tolerance Tests - Various time intervals
        {
            'Test_Case_ID': 'TOLERANCE_DATE_001',
            'Test_Case_Name': 'Date Tolerance - 1 Day Soft Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate date columns with 1-day tolerance (soft validation - warnings only)',
            'Prerequisites': 'Tables exist with date columns, dates within 1-day tolerance',
            'Tags': 'date-tolerance,soft-validation,1-day',
            'Parameters': 'source_table=public.orders,target_table=private.orders,compare_columns=order_date,key_column=order_id,date_tolerance=1 day,validation_type=soft',
            'Enable': True
        },
        
        {
            'Test_Case_ID': 'TOLERANCE_DATE_002',
            'Test_Case_Name': 'Date Tolerance - 1 Hour Hard Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Validate timestamp columns with 1-hour tolerance (hard validation - fail if exceeded)',
            'Prerequisites': 'Tables exist with timestamp columns, some dates exceed 1-hour tolerance',
            'Tags': 'date-tolerance,hard-validation,1-hour',
            'Parameters': 'source_table=public.orders,target_table=private.orders,compare_columns=created_timestamp,key_column=order_id,date_tolerance=1 hour,validation_type=hard',
            'Enable': True
        },
        
        # 2. Float/Decimal Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_FLOAT_001',
            'Test_Case_Name': 'Float Tolerance - 5% Percentage Soft Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate price columns with 5% percentage tolerance (soft validation)',
            'Prerequisites': 'Tables exist with price columns, values within 5% tolerance',
            'Tags': 'float-tolerance,percentage,soft-validation,5-percent',
            'Parameters': 'source_table=public.products,target_table=private.products,compare_columns=price,key_column=product_id,float_tolerance=5%,validation_type=soft',
            'Enable': True
        },
        
        {
            'Test_Case_ID': 'TOLERANCE_FLOAT_002',
            'Test_Case_Name': 'Float Tolerance - $10 Absolute Hard Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Validate amount columns with $10 absolute tolerance (hard validation)',
            'Prerequisites': 'Tables exist with amount columns, some values exceed $10 tolerance',
            'Tags': 'float-tolerance,absolute,hard-validation,10-dollars',
            'Parameters': 'source_table=public.orders,target_table=private.orders,compare_columns=total_amount,key_column=order_id,float_tolerance=10.00,validation_type=hard',
            'Enable': True
        },
        
        # 3. Record Count Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_COUNT_001',
            'Test_Case_Name': 'Record Count - 10% Percentage Soft Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate record counts with 10% tolerance (soft validation - warnings for variance)',
            'Prerequisites': 'Tables exist, record count difference within 10%',
            'Tags': 'count-tolerance,percentage,soft-validation,10-percent',
            'Parameters': 'source_table=public.employees,target_table=private.employees,tolerance=10.0,validation_type=soft',
            'Enable': True
        },
        
        {
            'Test_Case_ID': 'TOLERANCE_COUNT_002',
            'Test_Case_Name': 'Record Count - 100 Records Absolute Hard Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Validate record counts with 100 records absolute tolerance (hard validation)',
            'Prerequisites': 'Tables exist, record count difference exceeds 100 records',
            'Tags': 'count-tolerance,absolute,hard-validation,100-records',
            'Parameters': 'source_table=public.orders,target_table=private.orders,tolerance_type=absolute,tolerance=100,validation_type=hard',
            'Enable': True
        },
        
        # 4. String Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_STRING_001',
            'Test_Case_Name': 'String Tolerance - Case Insensitive Soft Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate string columns ignoring case differences (soft validation)',
            'Prerequisites': 'Tables exist with string columns, case differences present',
            'Tags': 'string-tolerance,case-insensitive,soft-validation',
            'Parameters': 'source_table=public.employees,target_table=private.employees,compare_columns=status,key_column=emp_id,string_tolerance=case_insensitive,validation_type=soft',
            'Enable': True
        },
        
        {
            'Test_Case_ID': 'TOLERANCE_STRING_002',
            'Test_Case_Name': 'String Tolerance - Whitespace Trim Hard Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Validate string columns with whitespace trimming (hard validation)',
            'Prerequisites': 'Tables exist with string columns, whitespace differences present',
            'Tags': 'string-tolerance,whitespace-trim,hard-validation',
            'Parameters': 'source_table=public.employees,target_table=private.employees,compare_columns=department,key_column=emp_id,string_tolerance=trim_whitespace,validation_type=hard',
            'Enable': True
        },
        
        # 5. Decimal Precision Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_DECIMAL_001',
            'Test_Case_Name': 'Decimal Precision - 2 Digits Soft Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate decimal columns with 2-digit precision tolerance (soft validation)',
            'Prerequisites': 'Tables exist with decimal columns, precision differences within 2 digits',
            'Tags': 'decimal-tolerance,precision,soft-validation,2-digits',
            'Parameters': 'source_table=public.products,target_table=private.products,compare_columns=weight_kg,key_column=product_id,decimal_precision=2,validation_type=soft',
            'Enable': True
        },
        
        {
            'Test_Case_ID': 'TOLERANCE_DECIMAL_002',
            'Test_Case_Name': 'Decimal Precision - Exact Match Hard Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Validate decimal columns requiring exact precision match (hard validation)',
            'Prerequisites': 'Tables exist with decimal columns, precision differences present',
            'Tags': 'decimal-tolerance,exact-match,hard-validation',
            'Parameters': 'source_table=public.products,target_table=private.products,compare_columns=unit_price,key_column=product_id,decimal_precision=exact,validation_type=hard',
            'Enable': True
        },
        
        # 6. Combined Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_COMBINED_001',
            'Test_Case_Name': 'Combined Tolerances - Multiple Columns Soft Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Validate multiple columns with different tolerance types (soft validation)',
            'Prerequisites': 'Tables exist with multiple data types, tolerances within limits',
            'Tags': 'combined-tolerance,multi-column,soft-validation',
            'Parameters': 'source_table=public.orders,target_table=private.orders,compare_columns=order_date|total_amount|status,key_column=order_id,date_tolerance=1 day,float_tolerance=5%,string_tolerance=case_insensitive,validation_type=soft',
            'Enable': True
        },
        
        # 7. Boundary Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_BOUNDARY_001',
            'Test_Case_Name': 'Boundary Test - Exact Tolerance Limit Soft Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Test boundary condition - exactly at tolerance limit (soft validation)',
            'Prerequisites': 'Tables exist with record count exactly at tolerance boundary',
            'Tags': 'boundary-test,exact-limit,soft-validation',
            'Parameters': 'source_table=public.products,target_table=private.products,tolerance=15.0,validation_type=soft',
            'Enable': True
        },
        
        {
            'Test_Case_ID': 'TOLERANCE_BOUNDARY_002',
            'Test_Case_Name': 'Boundary Test - Just Over Tolerance Limit Hard Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Test boundary condition - just over tolerance limit (hard validation)',
            'Prerequisites': 'Tables exist with record count just exceeding tolerance',
            'Tags': 'boundary-test,over-limit,hard-validation',
            'Parameters': 'source_table=public.customers,target_table=private.customers,tolerance=5.0,validation_type=hard',
            'Enable': True
        },
        
        # 8. Zero Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_ZERO_001',
            'Test_Case_Name': 'Zero Tolerance - Exact Match Required Hard Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'High',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Zero tolerance test - exact match required (hard validation)',
            'Prerequisites': 'Tables exist with different record counts',
            'Tags': 'zero-tolerance,exact-match,hard-validation',
            'Parameters': 'source_table=public.employees,target_table=private.employees,tolerance=0.0,validation_type=hard',
            'Enable': True
        },
        
        # 9. Performance Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_PERFORMANCE_001',
            'Test_Case_Name': 'Performance Test - Large Dataset with Tolerance',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Low',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Performance test with large dataset and tolerance validation',
            'Prerequisites': 'Large tables exist, performance metrics within acceptable range',
            'Tags': 'performance-test,large-dataset,tolerance',
            'Parameters': 'source_table=public.large_table,target_table=private.large_table,tolerance=2.0,validation_type=soft,performance_threshold=5000ms',
            'Enable': True
        },
        
        # 10. Negative Tolerance Tests
        {
            'Test_Case_ID': 'TOLERANCE_NEGATIVE_001',
            'Test_Case_Name': 'Negative Test - Invalid Tolerance Configuration',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name2': 'DUMMY',
            'TGT_Environment_Name3': 'DEV',
            'Priority': 'Low',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Negative test - invalid tolerance configuration should fail gracefully',
            'Prerequisites': 'Tables exist, invalid tolerance parameters provided',
            'Tags': 'negative-test,invalid-config,error-handling',
            'Parameters': 'source_table=public.employees,target_table=private.employees,tolerance=-5.0,validation_type=invalid_type',
            'Enable': True
        }
    ]
    
    # Create DataFrame from test cases
    tolerance_df = pd.DataFrame(test_cases)
    
    # Create Excel file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f'inputs/tolerance_test_suite_{timestamp}.xlsx'
    
    print(f"📝 Writing tolerance test suite to {excel_file}...")
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Write CONTROLLER sheet
        controller_df.to_excel(writer, sheet_name='CONTROLLER', index=False)
        
        # Write TOLERANCE_VALIDATIONS sheet
        tolerance_df.to_excel(writer, sheet_name='TOLERANCE_VALIDATIONS', index=False)
    
    print(f"✅ Tolerance test suite created with {len(test_cases)} test cases!")
    print(f"📊 Test breakdown:")
    print(f"   • Date tolerance tests: 2 tests")
    print(f"   • Float/decimal tolerance tests: 4 tests")
    print(f"   • Record count tolerance tests: 4 tests")
    print(f"   • String tolerance tests: 2 tests")
    print(f"   • Combined tolerance tests: 1 test")
    print(f"   • Boundary tests: 2 tests")
    print(f"   • Zero tolerance tests: 1 test")
    print(f"   • Performance tests: 1 test")
    print(f"   • Negative tests: 1 test")
    print(f"")
    print(f"🔍 Tolerance scenarios included:")
    print(f"   • Date tolerance: 1 day, 1 hour")
    print(f"   • Float tolerance: 5% percentage, $10 absolute")
    print(f"   • Count tolerance: 10% percentage, 100 records absolute")
    print(f"   • String tolerance: case insensitive, whitespace trim")
    print(f"   • Decimal precision: 2 digits, exact match")
    print(f"   • Soft vs Hard validations")
    print(f"   • Boundary condition testing")
    print(f"   • Zero tolerance (exact match)")
    print(f"")
    print(f"💾 File saved: {excel_file}")
    
    return excel_file

if __name__ == "__main__":
    # Create the tolerance test suite
    excel_file = create_tolerance_test_suite()
    
    # Copy to a new test file (keep existing WHERE clause tests)
    print(f"")
    print(f"📋 Tolerance test suite created successfully!")
    print(f"   File: {excel_file}")
    print(f"")
    print(f"🚀 Ready to implement tolerance validation logic and test data!")
    print(f"   Next steps:")
    print(f"   1. Implement tolerance validation logic in framework")
    print(f"   2. Create test data with tolerance scenarios")
    print(f"   3. Run tolerance validation tests")