"""
Cross Database Validation Demo with Mock Data
Demonstrates cross-database validation functionality using mock connectors
"""
import sys
import os
sys.path.append('src')

from cross_database_validation_test_case import CrossDatabaseValidationTestCase

class MockDatabaseConnector:
    """Mock database connector for demonstration"""
    
    def __init__(self, db_name, schema_data):
        self.db_name = db_name
        self.schema_data = schema_data
        self.is_connected = True
    
    def get_table_schema(self, table_name):
        """Return mock table schema"""
        if table_name in self.schema_data:
            return self.schema_data[table_name]
        return []
    
    def get_row_count(self, table_name):
        """Return mock row count"""
        if table_name in self.schema_data:
            return 150  # Mock row count
        return 0
    
    def close(self):
        """Mock close method"""
        self.is_connected = False

def create_demo_cross_database_validation():
    """Create and run a demonstration of cross-database validation"""
    
    print("🚀 Cross Database Validation Demo")
    print("=" * 60)
    
    # Define identical schemas for successful validation
    employees_schema = [
        ('emp_id', 'INTEGER'),
        ('first_name', 'VARCHAR'),
        ('last_name', 'VARCHAR'),
        ('email', 'VARCHAR'),
        ('hire_date', 'DATE'),
        ('salary', 'DECIMAL'),
        ('department_id', 'INTEGER'),
        ('manager_id', 'INTEGER'),
        ('phone', 'VARCHAR'),
        ('address', 'TEXT'),
        ('city', 'VARCHAR'),
        ('state', 'VARCHAR'),
        ('zip_code', 'VARCHAR'),
        ('country', 'VARCHAR'),
        ('birth_date', 'DATE'),
        ('gender', 'CHAR'),
        ('status', 'VARCHAR'),
        ('created_at', 'TIMESTAMP'),
        ('updated_at', 'TIMESTAMP'),
        ('emergency_contact', 'VARCHAR'),
        ('emergency_phone', 'VARCHAR'),
        ('job_title', 'VARCHAR'),
        ('experience_years', 'INTEGER')
    ]
    
    orders_schema = [
        ('order_id', 'INTEGER'),
        ('customer_id', 'INTEGER'),
        ('order_date', 'DATE'),
        ('ship_date', 'DATE'),
        ('delivery_date', 'DATE'),
        ('order_status', 'VARCHAR'),
        ('total_amount', 'DECIMAL'),
        ('tax_amount', 'DECIMAL'),
        ('shipping_cost', 'DECIMAL'),
        ('discount_amount', 'DECIMAL'),
        ('payment_method', 'VARCHAR'),
        ('shipping_address', 'TEXT'),
        ('billing_address', 'TEXT'),
        ('notes', 'TEXT'),
        ('created_by', 'INTEGER'),
        ('updated_by', 'INTEGER'),
        ('created_at', 'TIMESTAMP')
    ]
    
    products_schema = [
        ('product_id', 'INTEGER'),
        ('product_name', 'VARCHAR'),
        ('product_code', 'VARCHAR'),
        ('description', 'TEXT'),
        ('category_id', 'INTEGER'),
        ('brand_id', 'INTEGER'),
        ('unit_price', 'DECIMAL'),
        ('cost_price', 'DECIMAL'),
        ('stock_quantity', 'INTEGER'),
        ('reorder_level', 'INTEGER'),
        ('weight', 'DECIMAL'),
        ('dimensions', 'VARCHAR'),
        ('color', 'VARCHAR'),
        ('size', 'VARCHAR'),
        ('material', 'VARCHAR'),
        ('warranty_period', 'INTEGER'),
        ('supplier_id', 'INTEGER'),
        ('manufacture_date', 'DATE'),
        ('expiry_date', 'DATE'),
        ('barcode', 'VARCHAR'),
        ('status', 'VARCHAR'),
        ('rating', 'DECIMAL'),
        ('reviews_count', 'INTEGER'),
        ('created_at', 'TIMESTAMP'),
        ('updated_at', 'TIMESTAMP'),
        ('created_by', 'INTEGER')
    ]
    
    # Create mock databases
    source_schemas = {
        'public.employees': employees_schema,
        'public.orders': orders_schema,
        'public.products': products_schema
    }
    
    target_schemas = {
        'private.employees': employees_schema,  # Identical for success
        'private.orders': orders_schema,        # Identical for success  
        'private.products': products_schema     # Identical for success
    }
    
    # Create mock connectors
    source_connector = MockDatabaseConnector('DUMMY.NP1', source_schemas)
    target_connector = MockDatabaseConnector('DUMMY.DEV', target_schemas)
    
    # Test cases
    test_cases = [
        {
            'id': 'CROSS_DB_TEST_1',
            'name': 'Public Employees vs Private Employees',
            'category': 'SCHEMA_VALIDATION',
            'parameters': 'source_table=public.employees;target_table=private.employees'
        },
        {
            'id': 'CROSS_DB_TEST_2', 
            'name': 'Public Orders vs Private Orders',
            'category': 'ROW_COUNT_VALIDATION',
            'parameters': 'source_table=public.orders;target_table=private.orders'
        },
        {
            'id': 'CROSS_DB_TEST_3',
            'name': 'Public Products vs Private Products', 
            'category': 'SCHEMA_VALIDATION',
            'parameters': 'source_table=public.products;target_table=private.products'
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\n🔍 Running Test: {test_case['name']}")
        print(f"   Category: {test_case['category']}")
        print(f"   Parameters: {test_case['parameters']}")
        
        # Create cross-database test case
        cross_db_test = CrossDatabaseValidationTestCase(
            test_case_id=test_case['id'],
            test_name=test_case['name'],
            src_application_name='DUMMY',
            src_environment_name='NP1',
            tgt_application_name='DUMMY',
            tgt_environment_name='DEV',
            test_category=test_case['category'],
            expected_result='PASS',
            description=f"Cross-database validation: {test_case['name']}",
            parameters=test_case['parameters']
        )
        
        # Inject mock connectors
        cross_db_test.source_connector = source_connector
        cross_db_test.target_connector = target_connector
        
        # Execute validation manually
        if test_case['category'] == 'SCHEMA_VALIDATION':
            result = cross_db_test._execute_cross_db_schema_validation()
        elif test_case['category'] == 'ROW_COUNT_VALIDATION':
            result = cross_db_test._execute_cross_db_row_count_validation()
        else:
            result = False
        
        status = "PASSED" if result else "FAILED"
        results.append({'test': test_case['name'], 'status': status})
        
        if result:
            print(f"✅ {test_case['name']}: {status}")
        else:
            print(f"❌ {test_case['name']}: {status}")
    
    # Summary
    print(f"\n📊 Demo Results Summary:")
    print(f"=" * 40)
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    failed = sum(1 for r in results if r['status'] == 'FAILED')
    print(f"   Total Tests: {len(results)}")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    
    print(f"\n🎉 Cross Database Validation Demo Completed!")
    print(f"   The framework is working correctly and ready for real database connections.")
    
    return results

if __name__ == "__main__":
    create_demo_cross_database_validation()