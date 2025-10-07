"""
Setup Test Tables for Cross Database Validation
Creates source and target tables in respective schemas for testing
"""
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_test_tables():
    """Create test tables in both NP1 and DEV databases"""
    
    # Database configurations
    databases = {
        'NP1': {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': os.getenv('NP1_DUMMY_USERNAME', 'postgres'),
            'password': os.getenv('NP1_DUMMY_PASSWORD', 'admin')
        },
        'DEV': {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db_dev',
            'user': os.getenv('DEV_DUMMY_USERNAME', 'postgres'),
            'password': os.getenv('DEV_DUMMY_PASSWORD', 'admin')
        }
    }
    
    # Schema mapping
    schemas = {
        'NP1': 'public',
        'DEV': 'private'
    }
    
    # Table definitions
    table_definitions = {
        'employees': """
            CREATE TABLE {schema}.employees (
                emp_id SERIAL PRIMARY KEY,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE,
                hire_date DATE,
                salary DECIMAL(10,2),
                department_id INTEGER,
                manager_id INTEGER,
                phone VARCHAR(20),
                address TEXT,
                city VARCHAR(50),
                state VARCHAR(50),
                zip_code VARCHAR(10),
                country VARCHAR(50),
                birth_date DATE,
                gender CHAR(1),
                status VARCHAR(20) DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                emergency_contact VARCHAR(100),
                emergency_phone VARCHAR(20),
                job_title VARCHAR(100),
                experience_years INTEGER
            )
        """,
        'orders': """
            CREATE TABLE {schema}.orders (
                order_id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                ship_date DATE,
                delivery_date DATE,
                order_status VARCHAR(20) DEFAULT 'PENDING',
                total_amount DECIMAL(12,2),
                tax_amount DECIMAL(10,2),
                shipping_cost DECIMAL(8,2),
                discount_amount DECIMAL(8,2),
                payment_method VARCHAR(50),
                shipping_address TEXT,
                billing_address TEXT,
                notes TEXT,
                created_by INTEGER,
                updated_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'products': """
            CREATE TABLE {schema}.products (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(200) NOT NULL,
                product_code VARCHAR(50) UNIQUE,
                description TEXT,
                category_id INTEGER,
                brand_id INTEGER,
                unit_price DECIMAL(10,2),
                cost_price DECIMAL(10,2),
                stock_quantity INTEGER DEFAULT 0,
                reorder_level INTEGER DEFAULT 0,
                weight DECIMAL(8,3),
                dimensions VARCHAR(50),
                color VARCHAR(30),
                size VARCHAR(20),
                material VARCHAR(100),
                warranty_period INTEGER,
                supplier_id INTEGER,
                manufacture_date DATE,
                expiry_date DATE,
                barcode VARCHAR(100),
                status VARCHAR(20) DEFAULT 'ACTIVE',
                rating DECIMAL(3,2),
                reviews_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER
            )
        """
    }
    
    # Sample data
    sample_data = {
        'employees': [
            "('John', 'Doe', 'john.doe@company.com', '2020-01-15', 75000.00, 1, NULL, '555-0101', '123 Main St', 'New York', 'NY', '10001', 'USA', '1985-03-20', 'M', 'ACTIVE', '2020-01-15', '2024-01-01', 'Jane Doe', '555-0102', 'Software Engineer', 5)",
            "('Jane', 'Smith', 'jane.smith@company.com', '2019-06-01', 82000.00, 2, 1, '555-0201', '456 Oak Ave', 'Boston', 'MA', '02101', 'USA', '1988-07-15', 'F', 'ACTIVE', '2019-06-01', '2024-01-01', 'Bob Smith', '555-0202', 'Senior Developer', 7)",
            "('Mike', 'Johnson', 'mike.johnson@company.com', '2021-03-10', 68000.00, 1, 1, '555-0301', '789 Pine St', 'Chicago', 'IL', '60601', 'USA', '1990-11-05', 'M', 'ACTIVE', '2021-03-10', '2024-01-01', 'Sarah Johnson', '555-0302', 'Developer', 3)"
        ],
        'orders': [
            "(101, '2024-01-15', '2024-01-16', '2024-01-18', 'DELIVERED', 299.99, 24.00, 15.99, 0.00, 'CREDIT_CARD', '123 Customer St, City, State', '123 Customer St, City, State', 'First order', 1, 1)",
            "(102, '2024-01-20', '2024-01-21', '2024-01-23', 'DELIVERED', 149.50, 11.96, 9.99, 15.00, 'PAYPAL', '456 Client Ave, Town, State', '456 Client Ave, Town, State', 'Repeat customer', 1, 1)",
            "(103, '2024-02-01', NULL, NULL, 'PROCESSING', 89.99, 7.20, 12.50, 0.00, 'DEBIT_CARD', '789 Buyer Blvd, Village, State', '789 Buyer Blvd, Village, State', 'Rush order', 1, 1)"
        ],
        'products': [
            "('Wireless Headphones', 'WH-001', 'Premium wireless headphones with noise cancellation', 1, 1, 199.99, 120.00, 50, 10, 0.350, '8x7x3 inches', 'Black', 'Standard', 'Plastic/Metal', 24, 1, '2024-01-01', NULL, '1234567890123', 'ACTIVE', 4.5, 127)",
            "('Bluetooth Speaker', 'BS-002', 'Portable Bluetooth speaker with deep bass', 1, 2, 79.99, 45.00, 75, 15, 0.800, '6x4x4 inches', 'Blue', 'Medium', 'Plastic', 12, 2, '2024-01-15', NULL, '2345678901234', 'ACTIVE', 4.2, 89)",
            "('Smart Watch', 'SW-003', 'Fitness tracking smart watch with GPS', 2, 3, 299.99, 180.00, 25, 5, 0.045, '1.5x1.2x0.5 inches', 'Silver', 'Large', 'Aluminum', 24, 3, '2024-02-01', NULL, '3456789012345', 'ACTIVE', 4.7, 203)"
        ]
    }
    
    for db_name, config in databases.items():
        print(f"\n🔧 Setting up {db_name} database...")
        
        try:
            # Connect to database
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Create schema if it doesn't exist
            schema = schemas[db_name]
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
            print(f"✅ Schema '{schema}' created/verified")
            
            # Create tables
            for table_name, table_sql in table_definitions.items():
                # Drop table if exists
                cursor.execute(f"DROP TABLE IF EXISTS {schema}.{table_name} CASCADE")
                
                # Create table
                cursor.execute(table_sql.format(schema=schema))
                print(f"✅ Table '{schema}.{table_name}' created")
                
                # Insert sample data
                if table_name in sample_data:
                    # Get column names for insert
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_schema = '{schema}' AND table_name = '{table_name}' 
                        AND column_default IS NULL OR column_default NOT LIKE 'nextval%'
                        ORDER BY ordinal_position
                    """)
                    
                    columns = cursor.fetchall()
                    non_serial_columns = [col[0] for col in columns if not col[0].endswith('_id') or col[0] in ['customer_id', 'category_id', 'brand_id', 'supplier_id', 'department_id', 'manager_id', 'created_by', 'updated_by']]
                    
                    # Build insert statement
                    if table_name == 'employees':
                        insert_cols = "first_name, last_name, email, hire_date, salary, department_id, manager_id, phone, address, city, state, zip_code, country, birth_date, gender, status, created_at, updated_at, emergency_contact, emergency_phone, job_title, experience_years"
                    elif table_name == 'orders':
                        insert_cols = "customer_id, order_date, ship_date, delivery_date, order_status, total_amount, tax_amount, shipping_cost, discount_amount, payment_method, shipping_address, billing_address, notes, created_by, updated_by"
                    elif table_name == 'products':
                        insert_cols = "product_name, product_code, description, category_id, brand_id, unit_price, cost_price, stock_quantity, reorder_level, weight, dimensions, color, size, material, warranty_period, supplier_id, manufacture_date, expiry_date, barcode, status, rating, reviews_count"
                    
                    for data_row in sample_data[table_name]:
                        insert_sql = f"INSERT INTO {schema}.{table_name} ({insert_cols}) VALUES {data_row}"
                        cursor.execute(insert_sql)
                    
                    print(f"✅ Sample data inserted into '{schema}.{table_name}'")
            
            # Commit changes
            conn.commit()
            print(f"✅ {db_name} database setup completed successfully!")
            
        except Exception as e:
            print(f"❌ Error setting up {db_name} database: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()

if __name__ == "__main__":
    print("🚀 Setting up Cross Database Validation Test Tables")
    print("=" * 60)
    create_test_tables()
    print("\n🎉 Test table setup completed!")