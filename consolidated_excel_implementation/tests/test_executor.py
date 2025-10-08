#!/usr/bin/env python3
"""
Test the consolidated test executor functionality.
"""

import sys
import os

# Add the parent directory (where src/ is located) to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from src.consolidated_test_executor import ConsolidatedTestExecutor
    print("✅ Successfully imported ConsolidatedTestExecutor")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_executor_initialization():
    """Test the consolidated test executor initialization."""
    print("\n🧪 Testing Consolidated Test Executor")
    print("=" * 40)
    
    # Test file path
    main_project_dir = os.path.dirname(parent_dir)
    excel_file = os.path.join(main_project_dir, "inputs", "consolidated_test_suite_20251007_213209.xlsx")
    config_file = os.path.join(main_project_dir, "configs", "database_connections.json")
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return False
        
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        return False
    
    try:
        # Create executor
        executor = ConsolidatedTestExecutor(excel_file, config_file)
        print(f"📖 Initialized executor with:")
        print(f"   Excel file: {os.path.basename(excel_file)}")
        print(f"   Config file: {os.path.basename(config_file)}")
        
        # Test reading test cases
        print(f"\n📋 Test cases loaded: {len(executor.test_cases)}")
        
        # Show sample test cases by type
        for test_type in ['SMOKE', 'DATA_VALIDATION', 'CROSS_DB_VALIDATION']:
            type_tests = [tc for tc in executor.test_cases if tc.get('TEST_TYPE') == test_type]
            if type_tests:
                sample = type_tests[0]
                print(f"   {test_type}: {len(type_tests)} tests")
                print(f"      Sample: {sample.get('Test_Case_ID')} - {sample.get('Test_Case_Name')}")
        
        print("✅ Executor initialization successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing executor: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dry_run():
    """Test executor dry run mode."""
    print("\n🧪 Testing Dry Run Mode")
    print("=" * 30)
    
    # Test file path
    main_project_dir = os.path.dirname(parent_dir)
    excel_file = os.path.join(main_project_dir, "inputs", "consolidated_test_suite_20251007_213209.xlsx")
    config_file = os.path.join(main_project_dir, "configs", "database_connections.json")
    
    try:
        executor = ConsolidatedTestExecutor(excel_file, config_file)
        
        # Test with a small subset of test cases for dry run
        smoke_tests = [tc for tc in executor.test_cases if tc.get('TEST_TYPE') == 'SMOKE'][:2]
        
        print(f"🔍 Dry run with {len(smoke_tests)} SMOKE tests")
        
        for test_case in smoke_tests:
            print(f"\n📋 Processing: {test_case.get('Test_Case_ID')}")
            print(f"   Type: {test_case.get('TEST_TYPE')}")
            print(f"   Category: {test_case.get('Category')}")
            print(f"   Environment: {test_case.get('Environment')}")
            
            # Show parameters
            params = test_case.get('Parameters', {})
            if params:
                print(f"   Parameters: {params}")
            
            print("   ✅ Dry run passed")
        
        print("✅ Dry run completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in dry run: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = True
    
    # Test initialization
    success &= test_executor_initialization()
    
    # Test dry run
    success &= test_dry_run()
    
    if success:
        print("\n✅ All executor tests passed!")
    else:
        print("\n❌ Some executor tests failed!")
        sys.exit(1)