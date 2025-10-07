"""
Create Mock Test Tables for Cross Database Validation
Creates tables in memory or using existing database connections for testing
"""
import time

class MockTable:
    """Mock table for testing schema comparison"""
    
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns  # List of (column_name, data_type) tuples

class MockDatabaseConnector:
    """Mock database connector for testing"""
    
    def __init__(self, db_name, tables=None):
        self.db_name = db_name
        self.tables = tables or {}
        self.is_connected = True
    
    def get_table_schema(self, table_name):
        """Return mock table schema"""
        if table_name in self.tables:
            return self.tables[table_name].columns
        return []
    
    def get_row_count(self, table_name):
        """Return mock row count"""
        if table_name in self.tables:
            return 100  # Mock data
        return 0
    
    def close(self):
        """Mock close method"""
        pass

def create_mock_databases():
    """Create mock databases with test tables"""
    
    # Define table schemas
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
    source_db_tables = {
        'public.employees': MockTable('public.employees', employees_schema),
        'public.orders': MockTable('public.orders', orders_schema),
        'public.products': MockTable('public.products', products_schema)
    }
    
    target_db_tables = {
        'private.employees': MockTable('private.employees', employees_schema),
        'private.orders': MockTable('private.orders', orders_schema),
        'private.products': MockTable('private.products', products_schema)
    }
    
    # Create connectors
    source_connector = MockDatabaseConnector('DUMMY.NP1', source_db_tables)
    target_connector = MockDatabaseConnector('DUMMY.DEV', target_db_tables)
    
    return source_connector, target_connector

def test_cross_database_validation():
    """Test cross-database validation with mock data"""
    print("🧪 Testing Cross Database Validation with Mock Data")
    print("=" * 60)
    
    # Create mock databases
    source_connector, target_connector = create_mock_databases()
    
    # Test tables
    test_cases = [
        ('public.employees', 'private.employees'),
        ('public.orders', 'private.orders'),
        ('public.products', 'private.products')
    ]
    
    for source_table, target_table in test_cases:
        print(f"\n🔍 Testing: {source_table} vs {target_table}")
        
        # Get schemas
        source_schema = source_connector.get_table_schema(source_table)
        target_schema = target_connector.get_table_schema(target_table)
        
        print(f"✅ Source table '{source_table}' found with {len(source_schema)} columns")
        print(f"✅ Target table '{target_table}' found with {len(target_schema)} columns")
        
        # Simple comparison
        if len(source_schema) == len(target_schema):
            print(f"✅ Schema validation PASSED - Both tables have {len(source_schema)} columns")
        else:
            print(f"❌ Schema validation FAILED - Column count mismatch: {len(source_schema)} vs {len(target_schema)}")
    
    print(f"\n🎉 Mock testing completed!")

if __name__ == "__main__":
    test_cross_database_validation()