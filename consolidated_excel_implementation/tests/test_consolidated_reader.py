#!/usr/bin/env python3
"""
Test the consolidated Excel reader functionality.
"""

import sys
import os

# Add the current working directory and parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Add the parent directory (where src/ is located) to the path
sys.path.insert(0, parent_dir)

try:
    from src.consolidated_excel_reader import ConsolidatedExcelTestCaseReader
    print("✅ Successfully imported ConsolidatedExcelTestCaseReader")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"Parent directory: {parent_dir}")
    sys.exit(1)


def test_consolidated_reader():
    """Test the consolidated Excel reader."""
    print("🧪 Testing Consolidated Excel Reader")
    print("=" * 40)
    
    # Test file path - go up to the main project directory
    main_project_dir = os.path.dirname(parent_dir)
    excel_file = os.path.join(main_project_dir, "inputs", "consolidated_test_suite_20251007_213209.xlsx")
    
    if not os.path.exists(excel_file):
        print(f"❌ Test file not found: {excel_file}")
        print(f"Looking in: {os.path.dirname(excel_file)}")
        return False
    
    try:
        # Create reader
        reader = ConsolidatedExcelTestCaseReader(excel_file)
        print(f"📖 Reading file: {excel_file}")
        
        # Read test cases
        test_data = reader.get_test_case_details()
        
        print(f"\n📊 Results:")
        print(f"   Test types found: {list(test_data.keys())}")
        
        for test_type, df in test_data.items():
            print(f"   {test_type}: {len(df)} test cases")
            
            # Show sample test case
            if len(df) > 0:
                sample = df.iloc[0]
                print(f"      Sample: {sample['Test_Case_ID']} - {sample['Test_Case_Name']}")
                
                # Show parsed parameters
                if 'parsed_parameters' in sample and sample['parsed_parameters']:
                    print(f"      Parameters: {sample['parsed_parameters']}")
        
        # Get statistics
        stats = reader.get_test_statistics()
        print(f"\n📈 Statistics:")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")
        
        # Test individual test type retrieval
        print(f"\n🔍 Testing individual test type retrieval:")
        smoke_tests = reader.get_tests_by_type('SMOKE')
        if smoke_tests is not None:
            print(f"   SMOKE tests: {len(smoke_tests)} found")
        
        data_val_tests = reader.get_tests_by_type('DATA_VALIDATION')
        if data_val_tests is not None:
            print(f"   DATA_VALIDATION tests: {len(data_val_tests)} found")
        
        cross_db_tests = reader.get_tests_by_type('CROSS_DB_VALIDATION')
        if cross_db_tests is not None:
            print(f"   CROSS_DB_VALIDATION tests: {len(cross_db_tests)} found")
        
        # Test export functionality
        print(f"\n💾 Testing export functionality:")
        output_dir = "consolidated_excel_implementation/output"
        os.makedirs(output_dir, exist_ok=True)
        reader.export_test_summary(f"{output_dir}/test_summary.xlsx")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_consolidated_reader()
    sys.exit(0 if success else 1)