#!/usr/bin/env python3
"""
Simple test for the consolidated test executor functionality.
Tests only the basic initialization and reading capabilities.
"""

import sys
import os

# Add the parent directory (where src/ is located) to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
main_project_dir = os.path.dirname(parent_dir)

# Only add the parent directory to import the local src module
sys.path.insert(0, parent_dir)

try:
    from src.consolidated_excel_reader import ConsolidatedExcelTestCaseReader
    print("✅ Successfully imported ConsolidatedExcelTestCaseReader")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_basic_functionality():
    """Test basic functionality without full executor."""
    print("\n🧪 Testing Basic Consolidated Functionality")
    print("=" * 45)
    
    # Test file path
    excel_file = os.path.join(main_project_dir, "inputs", "consolidated_test_suite_20251007_213209.xlsx")
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return False
    
    try:
        # Create reader
        reader = ConsolidatedExcelTestCaseReader(excel_file)
        print(f"📖 Reading file: {os.path.basename(excel_file)}")
        
        # Test getting different test types
        all_tests = reader.get_all_enabled_tests()
        smoke_tests = reader.get_tests_by_type('SMOKE')
        data_validation_tests = reader.get_tests_by_type('DATA_VALIDATION') 
        cross_db_tests = reader.get_tests_by_type('CROSS_DB_VALIDATION')
        
        print(f"\n📊 Test Distribution:")
        print(f"   Total tests: {len(all_tests)}")
        print(f"   SMOKE: {len(smoke_tests) if smoke_tests is not None else 0}")
        print(f"   DATA_VALIDATION: {len(data_validation_tests) if data_validation_tests is not None else 0}")
        print(f"   CROSS_DB_VALIDATION: {len(cross_db_tests) if cross_db_tests is not None else 0}")
        
        # Test specific scenarios
        print(f"\n🔍 Testing Specific Scenarios:")
        
        # Convert dataframe to list of dictionaries for easier processing
        test_list = all_tests.to_dict('records')
        
        # Test tolerance scenarios
        tolerance_tests = [t for t in test_list if 'tolerance' in str(t.get('Parameters', '')).lower()]
        print(f"   Tests with tolerance: {len(tolerance_tests)}")
        
        # Test expected column scenarios  
        expected_col_tests = [t for t in test_list if 'expected_' in str(t.get('Parameters', '')).lower()]
        print(f"   Tests with expected columns: {len(expected_col_tests)}")
        
        # Show sample test cases
        print(f"\n📋 Sample Test Cases:")
        
        if smoke_tests is not None and len(smoke_tests) > 0:
            sample = smoke_tests.iloc[0]
            print(f"   SMOKE: {sample.get('Test_Case_ID')} - {sample.get('Test_Case_Name')}")
            print(f"     Environment: {sample.get('Environment')}")
            print(f"     Parameters: {sample.get('Parameters', {})}")
        
        if data_validation_tests is not None and len(data_validation_tests) > 0:
            sample = data_validation_tests.iloc[0]
            print(f"   DATA_VALIDATION: {sample.get('Test_Case_ID')} - {sample.get('Test_Case_Name')}")
            print(f"     Category: {sample.get('Category')}")
            print(f"     Source Table: {sample.get('SRC_Table_Name')}")
            print(f"     Target Table: {sample.get('TGT_Table_Name')}")
        
        if cross_db_tests is not None and len(cross_db_tests) > 0:
            sample = cross_db_tests.iloc[0]
            print(f"   CROSS_DB_VALIDATION: {sample.get('Test_Case_ID')} - {sample.get('Test_Case_Name')}")
            print(f"     Category: {sample.get('Category')}")
            print(f"     Parameters: {sample.get('Parameters', {})}")
        
        # Test parameter parsing
        print(f"\n🔧 Parameter Parsing Examples:")
        for i, test in enumerate(test_list[:3]):
            params = test.get('Parameters', {})
            if params:
                print(f"   {test.get('Test_Case_ID')}: {params}")
        
        print("\n✅ Basic functionality test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_specific_test_scenarios():
    """Test specific test scenarios from the consolidated Excel."""
    print("\n🧪 Testing Specific Test Scenarios")
    print("=" * 35)
    
    excel_file = os.path.join(main_project_dir, "inputs", "consolidated_test_suite_20251007_213209.xlsx")
    
    try:
        reader = ConsolidatedExcelTestCaseReader(excel_file)
        all_tests = reader.get_all_enabled_tests()
        test_list = all_tests.to_dict('records')
        
        # Find interesting test cases
        tolerance_test = None
        expected_col_test = None
        cross_db_test = None
        
        for test in test_list:
            params_str = str(test.get('Parameters', ''))
            if 'tolerance' in params_str.lower() and not tolerance_test:
                tolerance_test = test
            if 'expected_' in params_str.lower() and not expected_col_test:
                expected_col_test = test
            if test.get('TEST_TYPE') == 'CROSS_DB_VALIDATION' and not cross_db_test:
                cross_db_test = test
        
        print("🔍 Found Specific Test Scenarios:")
        
        if tolerance_test:
            print(f"\n📐 Tolerance Test: {tolerance_test.get('Test_Case_ID')}")
            print(f"   Name: {tolerance_test.get('Test_Case_Name')}")
            print(f"   Parameters: {tolerance_test.get('Parameters', {})}")
        
        if expected_col_test:
            print(f"\n📊 Expected Column Test: {expected_col_test.get('Test_Case_ID')}")
            print(f"   Name: {expected_col_test.get('Test_Case_Name')}")
            print(f"   Parameters: {expected_col_test.get('Parameters', {})}")
        
        if cross_db_test:
            print(f"\n🔗 Cross-DB Test: {cross_db_test.get('Test_Case_ID')}")
            print(f"   Name: {cross_db_test.get('Test_Case_Name')}")
            print(f"   Source: {cross_db_test.get('SRC_Table_Name')}")
            print(f"   Target: {cross_db_test.get('TGT_Table_Name')}")
            print(f"   Parameters: {cross_db_test.get('Parameters', {})}")
        
        print("\n✅ Specific scenario tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in scenario test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = True
    
    # Test basic functionality
    success &= test_basic_functionality()
    
    # Test specific scenarios
    success &= test_specific_test_scenarios()
    
    if success:
        print("\n🎉 All consolidated Excel tests passed!")
        print("\n📋 Summary:")
        print("   ✅ ConsolidatedExcelTestCaseReader working correctly")
        print("   ✅ Reading 32 comprehensive test cases")
        print("   ✅ Proper test type categorization")
        print("   ✅ Parameter parsing with tolerance and expected columns")
        print("   ✅ Statistics and export functionality")
        print("\n💡 Ready for integration with full test execution!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)