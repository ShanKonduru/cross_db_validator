"""
Comprehensive Tolerance Test Data Generator
Creates realistic test data to showcase various tolerance scenarios:
- Date variations (hours, days)
- Float variations (percentages, absolute differences)
- String variations (case, whitespace)
- Decimal precision variations
- Record count differences
"""

import random
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.database_config_manager import DatabaseConfigManager
from src.postgresql_connector import PostgreSQLConnector

def create_tolerance_test_data():
    """
    Create comprehensive test data for tolerance validation scenarios.
    """
    print("🚀 Creating Comprehensive Tolerance Test Data...")
    
    config_manager = DatabaseConfigManager("configs/database_connections.json")
    
    # Connect to source database (NP1)
    src_config = config_manager.get_connection_details("NP1", "DUMMY")
    src_connector = PostgreSQLConnector(
        host=src_config['host'],
        port=src_config['port'],
        username=src_config['username'],
        password=src_config['password'],
        database=src_config['database']
    )
    
    if not src_connector.connect():
        print("❌ Failed to connect to source database")
        return False
    
    try:
        print("📝 Creating tolerance test data in source database...")
        
        # 1. Create enhanced orders table with timestamp and amount variations
        print("📊 Creating orders table with timestamp and amount variations...")
        
        # Drop and recreate orders table with enhanced schema
        src_connector.execute_query("DROP TABLE IF EXISTS public.orders CASCADE")
        src_connector.execute_query("""
            CREATE TABLE public.orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INTEGER,
                order_date DATE NOT NULL,
                created_timestamp TIMESTAMP NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                order_status VARCHAR(20) NOT NULL,
                notes TEXT,
                updated_by VARCHAR(50),
                shipping_cost DECIMAL(8,2) DEFAULT 0.00,
                tax_amount DECIMAL(8,2) DEFAULT 0.00,
                discount_amount DECIMAL(8,2) DEFAULT 0.00
            )
        """)
        
        # Insert orders with deliberate variations for tolerance testing
        base_date = datetime.now() - timedelta(days=30)
        base_timestamp = datetime.now() - timedelta(hours=24)
        
        for i in range(1, 1001):  # 1000 orders
            # Date variations: some exactly same, some 1 day off, some 2+ days off
            if i <= 300:  # 30% exact match
                order_date = base_date
                created_timestamp = base_timestamp
            elif i <= 600:  # 30% within 1 day tolerance
                order_date = base_date + timedelta(days=random.choice([-1, 1]))
                created_timestamp = base_timestamp + timedelta(hours=random.choice([-1, 1]))
            else:  # 40% outside 1 day tolerance
                order_date = base_date + timedelta(days=random.randint(-5, 5))
                created_timestamp = base_timestamp + timedelta(hours=random.randint(-25, 25))
            
            # Amount variations: base $100, with percentage and absolute differences
            base_amount = 100.00
            if i <= 200:  # 20% exact match
                total_amount = base_amount
            elif i <= 500:  # 30% within 5% tolerance
                variation = random.uniform(-4.99, 4.99)
                total_amount = base_amount * (1 + variation/100)
            elif i <= 800:  # 30% within 10 absolute tolerance
                variation = random.uniform(-9.99, 9.99)
                total_amount = base_amount + variation
            else:  # 20% outside tolerance
                variation = random.uniform(-50.0, 50.0)
                total_amount = base_amount + variation
            
            # Status variations for string tolerance testing
            statuses = ['ACTIVE', 'active', 'Active', ' ACTIVE ', 'PENDING', 'pending']
            status = random.choice(statuses)
            
            # Insert order
            src_connector.execute_query(f"""
                INSERT INTO public.orders 
                (order_id, customer_id, order_date, created_timestamp, total_amount, order_status, notes, updated_by, shipping_cost, tax_amount)
                VALUES ({i}, {(i-1) % 100 + 1}, '{order_date.strftime('%Y-%m-%d')}', 
                        '{created_timestamp.strftime('%Y-%m-%d %H:%M:%S')}', {total_amount:.2f}, 
                        '{status}', 'Order {i} notes', 'user{(i % 10)+1}', 
                        {random.uniform(5.0, 25.0):.2f}, {total_amount * 0.08:.2f})
            """)
        
        print("✅ Orders table created with 1000 records and tolerance variations")
        
        # 2. Create enhanced products table with decimal precision variations
        print("📊 Creating products table with decimal precision variations...")
        
        src_connector.execute_query("DROP TABLE IF EXISTS public.products CASCADE")
        src_connector.execute_query("""
            CREATE TABLE public.products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                unit_price DECIMAL(10,4) NOT NULL,
                weight_kg DECIMAL(8,3) NOT NULL,
                status VARCHAR(20) NOT NULL,
                category VARCHAR(50),
                description TEXT,
                manufacturer VARCHAR(100),
                created_date DATE DEFAULT CURRENT_DATE
            )
        """)
        
        # Insert products with decimal precision variations
        for i in range(1, 501):  # 500 products
            base_price = 50.00
            base_weight = 1.500
            
            # Price variations with different decimal precision
            if i <= 150:  # 30% exact match
                price = base_price
                unit_price = base_price
                weight_kg = base_weight
            elif i <= 300:  # 30% within 2 decimal place tolerance
                price = round(base_price + random.uniform(-5.0, 5.0), 2)
                unit_price = round(base_price + random.uniform(-0.05, 0.05), 4)
                weight_kg = round(base_weight + random.uniform(-0.1, 0.1), 3)
            else:  # 40% with high precision differences
                price = round(base_price + random.uniform(-10.0, 10.0), 2)
                unit_price = round(base_price + random.uniform(-1.0, 1.0), 4)
                weight_kg = round(base_weight + random.uniform(-0.5, 0.5), 3)
            
            # Status with case and whitespace variations
            statuses = ['ACTIVE', 'Active', ' ACTIVE', 'ACTIVE ', 'DISCONTINUED', 'discontinued', 'OUT_OF_STOCK']
            status = random.choice(statuses)
            
            src_connector.execute_query(f"""
                INSERT INTO public.products 
                (product_id, product_name, price, unit_price, weight_kg, status, category, description, manufacturer)
                VALUES ({i}, 'Product {i}', {price:.2f}, {unit_price:.4f}, {weight_kg:.3f}, 
                        '{status}', 'Category{(i % 10)+1}', 'Description for product {i}', 'Manufacturer{(i % 5)+1}')
            """)
        
        print("✅ Products table created with 500 records and decimal precision variations")
        
        # 3. Create enhanced employees table with string and date variations
        print("📊 Enhancing employees table with string and date variations...")
        
        # Add more columns for tolerance testing
        src_connector.execute_query("""
            ALTER TABLE public.employees 
            ADD COLUMN IF NOT EXISTS department VARCHAR(50) DEFAULT 'IT',
            ADD COLUMN IF NOT EXISTS salary DECIMAL(10,2) DEFAULT 50000.00,
            ADD COLUMN IF NOT EXISTS bonus_percentage DECIMAL(5,2) DEFAULT 10.00,
            ADD COLUMN IF NOT EXISTS last_review_date DATE DEFAULT CURRENT_DATE,
            ADD COLUMN IF NOT EXISTS performance_score DECIMAL(3,1) DEFAULT 8.5
        """)
        
        # Update employees with tolerance test data
        departments = ['IT', ' IT ', 'it', 'Engineering', 'ENGINEERING', 'Sales', ' Sales', 'HR', 'hr ']
        base_salary = 50000.00
        base_date = datetime.now() - timedelta(days=90)
        
        for emp_id in range(1, 1001):
            # Department with string variations
            department = random.choice(departments)
            
            # Salary with percentage and absolute variations
            if emp_id <= 200:  # 20% exact match
                salary = base_salary
            elif emp_id <= 500:  # 30% within 5% tolerance
                variation = random.uniform(-4.99, 4.99)
                salary = base_salary * (1 + variation/100)
            else:  # 50% with larger variations
                variation = random.uniform(-20.0, 20.0)
                salary = base_salary * (1 + variation/100)
            
            # Date with day variations
            if emp_id <= 300:  # 30% exact match
                review_date = base_date
            elif emp_id <= 600:  # 30% within 1 day tolerance
                review_date = base_date + timedelta(days=random.choice([-1, 1]))
            else:  # 40% outside 1 day tolerance
                review_date = base_date + timedelta(days=random.randint(-10, 10))
            
            # Performance score with decimal precision
            performance_score = round(random.uniform(5.0, 10.0), 1)
            bonus_percentage = round(random.uniform(5.0, 15.0), 2)
            
            src_connector.execute_query(f"""
                UPDATE public.employees 
                SET department = '{department}', 
                    salary = {salary:.2f}, 
                    bonus_percentage = {bonus_percentage:.2f},
                    last_review_date = '{review_date.strftime('%Y-%m-%d')}',
                    performance_score = {performance_score:.1f}
                WHERE emp_id = {emp_id}
            """)
        
        print("✅ Employees table enhanced with tolerance test variations")
        
        # 4. Create customers table for additional tolerance scenarios
        print("📊 Creating customers table for boundary testing...")
        
        src_connector.execute_query("DROP TABLE IF EXISTS public.customers CASCADE")
        src_connector.execute_query("""
            CREATE TABLE public.customers (
                customer_id SERIAL PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                registration_date DATE NOT NULL,
                credit_limit DECIMAL(10,2) DEFAULT 1000.00,
                total_spent DECIMAL(12,2) DEFAULT 0.00,
                loyalty_points INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'ACTIVE',
                last_purchase_date DATE
            )
        """)
        
        # Insert customers for boundary testing (exactly at tolerance limits)
        for i in range(1, 201):  # 200 customers
            registration_date = datetime.now() - timedelta(days=random.randint(1, 365))
            credit_limit = 1000.00 + (i * 10)  # Incremental increases for boundary testing
            total_spent = credit_limit * random.uniform(0.1, 0.9)
            loyalty_points = int(total_spent / 10)
            
            src_connector.execute_query(f"""
                INSERT INTO public.customers 
                (customer_id, customer_name, email, phone, registration_date, credit_limit, total_spent, loyalty_points, status)
                VALUES ({i}, 'Customer {i}', 'customer{i}@example.com', '555-{1000+i}', 
                        '{registration_date.strftime('%Y-%m-%d')}', {credit_limit:.2f}, {total_spent:.2f}, 
                        {loyalty_points}, 'ACTIVE')
            """)
        
        print("✅ Customers table created with 200 records for boundary testing")
        
        # 5. Create large_table for performance testing
        print("📊 Creating large table for performance testing...")
        
        src_connector.execute_query("DROP TABLE IF EXISTS public.large_table CASCADE")
        src_connector.execute_query("""
            CREATE TABLE public.large_table (
                id SERIAL PRIMARY KEY,
                data_value DECIMAL(10,2),
                timestamp_field TIMESTAMP DEFAULT NOW(),
                text_field VARCHAR(100),
                status_field VARCHAR(20) DEFAULT 'ACTIVE'
            )
        """)
        
        # Insert large dataset (5000 records for performance testing)
        batch_size = 100
        for batch_start in range(1, 5001, batch_size):
            values = []
            for i in range(batch_start, min(batch_start + batch_size, 5001)):
                data_value = random.uniform(100.0, 1000.0)
                text_field = f'Data record {i}'
                values.append(f"({i}, {data_value:.2f}, NOW(), '{text_field}', 'ACTIVE')")
            
            values_str = ",".join(values)
            src_connector.execute_query(f"""
                INSERT INTO public.large_table (id, data_value, timestamp_field, text_field, status_field)
                VALUES {values_str}
            """)
        
        print("✅ Large table created with 5000 records for performance testing")
        
        # 6. Create corresponding target data with deliberate variations
        print("📝 Creating target database variations...")
        
        tgt_config = config_manager.get_connection_details("DEV", "DUMMY")
        tgt_connector = PostgreSQLConnector(
            host=tgt_config['host'],
            port=tgt_config['port'],
            username=tgt_config['username'],
            password=tgt_config['password'],
            database=tgt_config['database']
        )
        
        if tgt_connector.connect():
            print("🔗 Connected to target database")
            
            # Create target schemas if not exist
            tgt_connector.execute_query("CREATE SCHEMA IF NOT EXISTS private")
            
            # Create target tables with variations for tolerance testing
            
            # Target orders (50% of source records with variations)
            tgt_connector.execute_query("DROP TABLE IF EXISTS private.orders CASCADE")
            tgt_connector.execute_query("""
                CREATE TABLE private.orders (
                    order_id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    order_date DATE NOT NULL,
                    created_timestamp TIMESTAMP NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    order_status VARCHAR(20) NOT NULL,
                    notes TEXT,
                    updated_by VARCHAR(50),
                    shipping_cost DECIMAL(8,2) DEFAULT 0.00,
                    tax_amount DECIMAL(8,2) DEFAULT 0.00,
                    discount_amount DECIMAL(8,2) DEFAULT 0.00
                )
            """)
            
            # Insert 500 orders (50% of source) with variations
            for i in range(1, 501):
                # Introduce deliberate variations for tolerance testing
                base_amount = 100.00
                
                # Date variations (some within tolerance, some outside)
                if i <= 150:  # 30% within 1 day tolerance
                    date_offset = random.choice([-1, 0, 1])
                    time_offset = random.choice([-1, 0, 1])
                else:  # 70% with larger variations
                    date_offset = random.randint(-3, 3)
                    time_offset = random.randint(-5, 5)
                
                order_date = (datetime.now() - timedelta(days=30) + timedelta(days=date_offset)).strftime('%Y-%m-%d')
                created_timestamp = (datetime.now() - timedelta(hours=24) + timedelta(hours=time_offset)).strftime('%Y-%m-%d %H:%M:%S')
                
                # Amount variations
                if i <= 100:  # 20% within 5% tolerance
                    amount_variation = random.uniform(-4.99, 4.99)
                    total_amount = base_amount * (1 + amount_variation/100)
                elif i <= 250:  # 30% within 10 absolute tolerance
                    amount_variation = random.uniform(-9.99, 9.99)
                    total_amount = base_amount + amount_variation
                else:  # 50% with larger variations
                    amount_variation = random.uniform(-30.0, 30.0)
                    total_amount = base_amount + amount_variation
                
                # Status variations (case and whitespace)
                statuses = ['ACTIVE', 'active', 'Active', ' ACTIVE ', 'PENDING']
                status = random.choice(statuses)
                
                tgt_connector.execute_query(f"""
                    INSERT INTO private.orders 
                    (order_id, customer_id, order_date, created_timestamp, total_amount, order_status, notes, updated_by, shipping_cost, tax_amount)
                    VALUES ({i}, {(i-1) % 50 + 1}, '{order_date}', '{created_timestamp}', {total_amount:.2f}, 
                            '{status}', 'Target order {i}', 'target_user{(i % 5)+1}', 
                            {random.uniform(3.0, 20.0):.2f}, {total_amount * 0.07:.2f})
                """)
            
            print("✅ Target orders table created with 500 records and tolerance variations")
            
            # Target products (30% of source records)
            tgt_connector.execute_query("DROP TABLE IF EXISTS private.products CASCADE")
            tgt_connector.execute_query("""
                CREATE TABLE private.products (
                    product_id INTEGER PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    unit_price DECIMAL(10,4) NOT NULL,
                    weight_kg DECIMAL(8,3) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    category VARCHAR(50),
                    description TEXT,
                    manufacturer VARCHAR(100),
                    created_date DATE DEFAULT CURRENT_DATE
                )
            """)
            
            # Insert 150 products with variations
            for i in range(1, 151):
                base_price = 50.00
                price_variation = random.uniform(-15.0, 15.0)
                price = base_price + price_variation
                unit_price = price + random.uniform(-0.50, 0.50)
                weight_kg = 1.500 + random.uniform(-0.3, 0.3)
                
                statuses = ['ACTIVE', ' ACTIVE', 'Active', 'DISCONTINUED']
                status = random.choice(statuses)
                
                tgt_connector.execute_query(f"""
                    INSERT INTO private.products 
                    (product_id, product_name, price, unit_price, weight_kg, status, category, description, manufacturer)
                    VALUES ({i}, 'Target Product {i}', {price:.2f}, {unit_price:.4f}, {weight_kg:.3f}, 
                            '{status}', 'TargetCat{(i % 5)+1}', 'Target description {i}', 'TargetMfg{(i % 3)+1}')
                """)
            
            print("✅ Target products table created with 150 records")
            
            # Target employees (10% of source records)  
            tgt_connector.execute_query("DROP TABLE IF EXISTS private.employees CASCADE")
            tgt_connector.execute_query("""
                CREATE TABLE private.employees (
                    emp_id INTEGER PRIMARY KEY,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    email VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'ACTIVE',
                    hire_date DATE DEFAULT '2020-01-01',
                    department VARCHAR(50) DEFAULT 'IT',
                    salary DECIMAL(10,2) DEFAULT 50000.00,
                    bonus_percentage DECIMAL(5,2) DEFAULT 10.00,
                    last_review_date DATE DEFAULT CURRENT_DATE,
                    performance_score DECIMAL(3,1) DEFAULT 8.5
                )
            """)
            
            # Insert 100 employees with tolerance variations
            departments = ['IT', ' IT', 'Engineering', ' Engineering ', 'Sales']
            base_salary = 50000.00
            base_date = datetime.now() - timedelta(days=90)
            
            for i in range(1, 101):
                department = random.choice(departments)
                salary_variation = random.uniform(-10.0, 10.0)
                salary = base_salary * (1 + salary_variation/100)
                
                date_offset = random.randint(-2, 2)
                review_date = (base_date + timedelta(days=date_offset)).strftime('%Y-%m-%d')
                
                performance_score = round(random.uniform(6.0, 9.5), 1)
                bonus_percentage = round(random.uniform(8.0, 12.0), 2)
                
                tgt_connector.execute_query(f"""
                    INSERT INTO private.employees 
                    (emp_id, first_name, last_name, email, status, hire_date, department, salary, bonus_percentage, last_review_date, performance_score)
                    VALUES ({i}, 'TargetFirst{i}', 'TargetLast{i}', 'target{i}@example.com', 'ACTIVE', 
                            '2020-01-01', '{department}', {salary:.2f}, {bonus_percentage:.2f}, '{review_date}', {performance_score:.1f})
                """)
            
            print("✅ Target employees table created with 100 records")
            
            # Target customers (95% of source for boundary testing)
            tgt_connector.execute_query("DROP TABLE IF EXISTS private.customers CASCADE")
            tgt_connector.execute_query("""
                CREATE TABLE private.customers (
                    customer_id INTEGER PRIMARY KEY,
                    customer_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    registration_date DATE NOT NULL,
                    credit_limit DECIMAL(10,2) DEFAULT 1000.00,
                    total_spent DECIMAL(12,2) DEFAULT 0.00,
                    loyalty_points INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'ACTIVE',
                    last_purchase_date DATE
                )
            """)
            
            # Insert 190 customers (95% of 200) for boundary testing
            for i in range(1, 191):
                registration_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d')
                credit_limit = 1000.00 + (i * 10) + random.uniform(-50, 50)  # Small variations
                total_spent = credit_limit * random.uniform(0.2, 0.8)
                loyalty_points = int(total_spent / 10)
                
                tgt_connector.execute_query(f"""
                    INSERT INTO private.customers 
                    (customer_id, customer_name, email, phone, registration_date, credit_limit, total_spent, loyalty_points, status)
                    VALUES ({i}, 'Target Customer {i}', 'tcustomer{i}@example.com', '555-{2000+i}', 
                            '{registration_date}', {credit_limit:.2f}, {total_spent:.2f}, {loyalty_points}, 'ACTIVE')
                """)
            
            print("✅ Target customers table created with 190 records (95% for boundary testing)")
            
            # Target large_table (98% of source for performance testing)
            tgt_connector.execute_query("DROP TABLE IF EXISTS private.large_table CASCADE")
            tgt_connector.execute_query("""
                CREATE TABLE private.large_table (
                    id INTEGER PRIMARY KEY,
                    data_value DECIMAL(10,2),
                    timestamp_field TIMESTAMP DEFAULT NOW(),
                    text_field VARCHAR(100),
                    status_field VARCHAR(20) DEFAULT 'ACTIVE'
                )
            """)
            
            # Insert 4900 records (98% of 5000)
            batch_size = 100
            for batch_start in range(1, 4901, batch_size):
                values = []
                for i in range(batch_start, min(batch_start + batch_size, 4901)):
                    data_value = random.uniform(95.0, 1050.0)  # Slight variations
                    text_field = f'Target data record {i}'
                    values.append(f"({i}, {data_value:.2f}, NOW(), '{text_field}', 'ACTIVE')")
                
                values_str = ",".join(values)
                tgt_connector.execute_query(f"""
                    INSERT INTO private.large_table (id, data_value, timestamp_field, text_field, status_field)
                    VALUES {values_str}
                """)
            
            print("✅ Target large table created with 4900 records (98% for performance testing)")
            
            tgt_connector.close()
        else:
            print("⚠️ Could not connect to target database - tolerance tests will use source data only")
        
        print(f"\n🎉 Comprehensive tolerance test data creation completed!")
        print(f"📊 Data summary:")
        print(f"   • Orders: 1000 source, 500 target (50% difference) - Date, float, string tolerance scenarios")
        print(f"   • Products: 500 source, 150 target (70% difference) - Decimal precision tolerance scenarios")
        print(f"   • Employees: 1000 source, 100 target (90% difference) - String, date, salary tolerance scenarios")
        print(f"   • Customers: 200 source, 190 target (5% difference) - Boundary testing scenarios")
        print(f"   • Large_table: 5000 source, 4900 target (2% difference) - Performance testing scenarios")
        print(f"\n🔍 Tolerance scenarios covered:")
        print(f"   • Date tolerance: Exact match, 1-day tolerance, beyond tolerance")
        print(f"   • Float tolerance: 5% percentage, $10 absolute, beyond tolerance")
        print(f"   • String tolerance: Case variations, whitespace variations")
        print(f"   • Decimal precision: 2-digit tolerance, exact match requirements")
        print(f"   • Count tolerance: 2%, 5%, 50%, 70%, 90% differences")
        print(f"   • Boundary conditions: Exactly at tolerance limits")
        print(f"\n✅ Ready for comprehensive tolerance testing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tolerance test data: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        src_connector.close()

if __name__ == "__main__":
    success = create_tolerance_test_data()
    if success:
        print(f"\n🚀 Tolerance test data created successfully!")
        print(f"   You can now run tolerance validation tests with realistic scenarios")
        print(f"   Next: Implement tolerance validation logic in the framework")
    else:
        print(f"\n❌ Failed to create tolerance test data")