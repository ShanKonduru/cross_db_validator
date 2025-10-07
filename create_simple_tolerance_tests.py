"""
Simple Tolerance Test Suite
Creates basic tolerance test cases to demonstrate parameter parsing.
"""

import pandas as pd
from datetime import datetime

def create_simple_tolerance_tests():
    """
    Create simple tolerance test cases to demonstrate the new parameter parsing.
    """
    print("🚀 Creating Simple Tolerance Test Cases...")
    
    # Controller sheet data
    controller_data = {
        'SHEET_NAME': ['SIMPLE_TOLERANCE_TESTS'],
        'ENABLE': [True]
    }
    controller_df = pd.DataFrame(controller_data)
    
    # Simple tolerance test cases
    test_cases = [
        # 1. Basic tolerance with soft validation
        {
            'Test_Case_ID': 'SIMPLE_TOL_001',
            'Test_Case_Name': 'Basic Row Count with Soft Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name': 'DUMMY',
            'TGT_Environment_Name': 'DEV',
            'Priority': 'High',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Test basic row count validation with 20% tolerance and soft validation',
            'Prerequisites': 'Tables exist with different row counts',
            'Tags': 'tolerance,soft-validation,row-count',
            'Parameters': 'source_table=public.employees,target_table=private.employees,tolerance=20.0,tolerance_type=percentage,validation_type=soft',
            'Enable': True
        },
        
        # 2. Hard validation with tolerance
        {
            'Test_Case_ID': 'SIMPLE_TOL_002',
            'Test_Case_Name': 'Row Count with Hard Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name': 'DUMMY',
            'TGT_Environment_Name': 'DEV',
            'Priority': 'High',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'FAIL',
            'Description': 'Test row count validation with 5% tolerance and hard validation (should fail)',
            'Prerequisites': 'Tables exist with row count difference > 5%',
            'Tags': 'tolerance,hard-validation,row-count',
            'Parameters': 'source_table=public.orders,target_table=private.orders,tolerance=5.0,tolerance_type=percentage,validation_type=hard',
            'Enable': True
        },
        
        # 3. Absolute tolerance test
        {
            'Test_Case_ID': 'SIMPLE_TOL_003',
            'Test_Case_Name': 'Absolute Count Tolerance Test',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name': 'DUMMY',
            'TGT_Environment_Name': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'ROW_COUNT_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Test row count validation with absolute tolerance (500 records)',
            'Prerequisites': 'Tables exist with absolute difference <= 500',
            'Tags': 'tolerance,absolute,soft-validation',
            'Parameters': 'source_table=public.products,target_table=private.products,tolerance=500,tolerance_type=absolute,validation_type=soft',
            'Enable': True
        },
        
        # 4. Column validation with string tolerance
        {
            'Test_Case_ID': 'SIMPLE_TOL_004',
            'Test_Case_Name': 'String Tolerance Column Validation',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name': 'DUMMY',
            'TGT_Environment_Name': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Test column validation with case insensitive string tolerance',
            'Prerequisites': 'Tables exist with string columns having case differences',
            'Tags': 'tolerance,string,case-insensitive',
            'Parameters': 'source_table=public.employees,target_table=private.employees,compare_columns=status,key_column=emp_id,string_tolerance=case_insensitive,validation_type=soft',
            'Enable': True
        },
        
        # 5. Combined tolerance parameters
        {
            'Test_Case_ID': 'SIMPLE_TOL_005',
            'Test_Case_Name': 'Combined Tolerance Parameters Test',
            'SRC_Application_Name': 'DUMMY',
            'SRC_Environment_Name': 'NP1',
            'TGT_Application_Name': 'DUMMY',
            'TGT_Environment_Name': 'DEV',
            'Priority': 'Medium',
            'Test_Category': 'COL_COL_VALIDATION',
            'Expected_Result': 'PASS',
            'Description': 'Test multiple tolerance parameters in one test case',
            'Prerequisites': 'Tables exist with various data types',
            'Tags': 'tolerance,combined,multiple-types',
            'Parameters': 'source_table=public.orders,target_table=private.orders,compare_columns=total_amount,key_column=order_id,float_tolerance=10.0,date_tolerance=1 day,validation_type=soft',
            'Enable': True
        }
    ]
    
    # Create DataFrame from test cases
    simple_tolerance_df = pd.DataFrame(test_cases)
    
    # Create Excel file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    excel_file = f'inputs/simple_tolerance_tests_{timestamp}.xlsx'
    
    print(f"📝 Writing simple tolerance test suite to {excel_file}...")
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Write CONTROLLER sheet
        controller_df.to_excel(writer, sheet_name='CONTROLLER', index=False)
        
        # Write SIMPLE_TOLERANCE_TESTS sheet
        simple_tolerance_df.to_excel(writer, sheet_name='SIMPLE_TOLERANCE_TESTS', index=False)
    
    print(f"✅ Simple tolerance test suite created with {len(test_cases)} test cases!")
    print(f"📊 Test scenarios:")
    print(f"   • Percentage tolerance with soft validation")
    print(f"   • Percentage tolerance with hard validation")
    print(f"   • Absolute tolerance testing")
    print(f"   • String tolerance (case insensitive)")
    print(f"   • Combined tolerance parameters")
    print(f"")
    print(f"💾 File saved: {excel_file}")
    
    # Copy to main test file
    import shutil
    main_file = 'inputs/test_suite.xlsx'
    print(f"")
    print(f"🔄 Copying simple tolerance tests to main file: {main_file}")
    shutil.copy2(excel_file, main_file)
    print(f"✅ Main test suite updated successfully!")
    
    return excel_file

if __name__ == "__main__":
    # Create the simple tolerance test suite
    excel_file = create_simple_tolerance_tests()
    
    print(f"")
    print(f"🚀 Ready to test tolerance parameter parsing!")
    print(f"   Run 'python main.py' to see tolerance parameters being parsed")
    print(f"   Next: Implement tolerance validation logic")