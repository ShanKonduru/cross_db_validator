#!/usr/bin/env python3
"""
Test script for column mapping functionality
"""
import sys
sys.path.append('src')

from data_validation_test_case import DataValidationTestCase

def test_column_mapping():
    """Test column mapping functionality"""
    print("🧪 Testing Column Mapping Functionality")
    print("=" * 50)
    
    # Create a test case with column mappings
    test_case = DataValidationTestCase(
        Enable=True,
        Test_Case_ID='MAPPING_TEST_001',
        Test_Case_Name='Products Column Mapping Test',
        Environment_Name='DEV',
        Application_Name='DUMMY',
        Test_Category='COL_COL_VALIDATION',
        Parameters=(
            'source_table=public.products;'
            'target_table=public.new_products;'
            'tolerance_numeric=0.001;'
            'sample_size=10;'
            'column_mappings=product_name=product_description,stock_quantity=price,is_active=is_active'
        )
    )
    
    print("📋 Test Case Configuration:")
    print(f"   Source: {test_case.parameters.get('source_table')}")
    print(f"   Target: {test_case.parameters.get('target_table')}")
    print(f"   Mappings: {test_case.parameters.get('column_mappings')}")
    print()
    
    # Execute the test
    result = test_case.execute_test()
    
    print()
    print(f"🎯 Test Result: {result}")
    print()
    
    # Show execution details
    details = test_case.get_last_execution_details()
    if details:
        print("📊 Execution Details:")
        print(f"   Total columns: {details.get('total_columns', 'N/A')}")
        print(f"   Passed columns: {details.get('passed_columns', 'N/A')}")
        print(f"   Failed columns: {details.get('failed_columns', 'N/A')}")
        print(f"   Column mappings: {details.get('column_mappings_count', 'N/A')}")
        
        if details.get('comparison_results'):
            print("\n📈 Column Comparison Results:")
            for result in details['comparison_results'][:5]:  # Show first 5
                status_icon = "✅" if result['status'] == 'PASSED' else "❌"
                print(f"   {status_icon} {result['column']}: {result.get('reason', result['status'])}")
    
    return result

if __name__ == "__main__":
    try:
        result = test_column_mapping()
        print(f"\n🎉 Column mapping test completed: {result}")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()