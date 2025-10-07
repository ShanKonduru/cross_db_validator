"""
Enhanced Test Data Setup for WHERE Clause Testing
Adds comprehensive test data with status, date, and filtering columns.
"""

import random
from datetime import datetime, timedelta
from src.database_config_manager import DatabaseConfigManager
from src.postgresql_connector import PostgreSQLConnector

def create_enhanced_test_data():
    """
    Create enhanced test data with columns needed for WHERE clause testing.
    """
    print("🚀 Creating Enhanced Test Data for WHERE Clause Testing...")
    
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
        # 1. Update employees table with status and hire_date columns
        print("📝 Enhancing employees table...")
        
        # Add status column if not exists
        src_connector.execute_query("""
            ALTER TABLE public.employees 
            ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'ACTIVE'
        """)
        
        # Add hire_date column if not exists
        src_connector.execute_query("""
            ALTER TABLE public.employees 
            ADD COLUMN IF NOT EXISTS hire_date DATE DEFAULT '2020-01-01'
        """)
        
        # Update existing employees with random status and hire dates
        statuses = ['ACTIVE', 'INACTIVE', 'PENDING']
        for emp_id in range(1, 1001):  # Assuming 1000 employees
            status = random.choice(statuses)
            # Random hire date between 2018 and 2024
            start_date = datetime(2018, 1, 1)
            end_date = datetime(2024, 12, 31)
            random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
            hire_date = random_date.strftime('%Y-%m-%d')
            
            src_connector.execute_query(f"""
                UPDATE public.employees 
                SET status = '{status}', hire_date = '{hire_date}' 
                WHERE emp_id = {emp_id}
            """)
        
        print("✅ Employees table enhanced with status and hire_date")
        
        # 2. Update orders table with order_date and total_amount columns
        print("📝 Enhancing orders table...")
        
        # Add order_date column if not exists
        src_connector.execute_query("""
            ALTER TABLE public.orders 
            ADD COLUMN IF NOT EXISTS order_date DATE DEFAULT CURRENT_DATE
        """)
        
        # Add total_amount column if not exists
        src_connector.execute_query("""
            ALTER TABLE public.orders 
            ADD COLUMN IF NOT EXISTS total_amount DECIMAL(10,2) DEFAULT 100.00
        """)
        
        # Update existing orders with random dates and amounts
        for order_id in range(1, 801):  # Assuming 800 orders
            # Random order date in last 60 days
            order_date = datetime.now() - timedelta(days=random.randint(1, 60))
            order_date_str = order_date.strftime('%Y-%m-%d')
            
            # Random amount between 50 and 2000
            total_amount = round(random.uniform(50.0, 2000.0), 2)
            
            src_connector.execute_query(f"""
                UPDATE public.orders 
                SET order_date = '{order_date_str}', total_amount = {total_amount}
                WHERE order_id = {order_id}
            """)
        
        print("✅ Orders table enhanced with order_date and total_amount")
        
        # 3. Update products table with status and price columns
        print("📝 Enhancing products table...")
        
        # Add status column if not exists
        src_connector.execute_query("""
            ALTER TABLE public.products 
            ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'ACTIVE'
        """)
        
        # Add price column if not exists
        src_connector.execute_query("""
            ALTER TABLE public.products 
            ADD COLUMN IF NOT EXISTS price DECIMAL(10,2) DEFAULT 50.00
        """)
        
        # Update existing products with random status and prices
        product_statuses = ['ACTIVE', 'DISCONTINUED', 'OUT_OF_STOCK']
        
        # Get actual product count first
        success, result = src_connector.execute_query("SELECT COUNT(*) FROM public.products")
        product_count = result[0][0] if success and result else 0
        
        for i in range(1, min(product_count + 1, 1000)):  # Update existing products
            status = random.choice(product_statuses)
            # Random price between 10 and 500
            price = round(random.uniform(10.0, 500.0), 2)
            
            src_connector.execute_query(f"""
                UPDATE public.products 
                SET status = '{status}', price = {price}
                WHERE product_id = {i}
                OR product_id IN (SELECT product_id FROM public.products LIMIT 1 OFFSET {i-1})
            """)
        
        print("✅ Products table enhanced with status and price")
        
        # 4. Create corresponding data in target database if accessible
        print("📝 Attempting to create corresponding target data...")
        
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
            
            # Copy some sample data to target for testing
            # Copy 10% of employees to target (active employees only)
            tgt_connector.execute_query("""
                CREATE TABLE IF NOT EXISTS private.employees AS 
                SELECT * FROM public.employees LIMIT 0
            """)
            
            # Add the new columns to target table structure
            tgt_connector.execute_query("""
                ALTER TABLE private.employees 
                ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'ACTIVE'
            """)
            tgt_connector.execute_query("""
                ALTER TABLE private.employees 
                ADD COLUMN IF NOT EXISTS hire_date DATE DEFAULT '2020-01-01'
            """)
            
            # Insert some sample active employees for testing
            for emp_id in range(1, 101):  # 100 sample employees
                hire_date = (datetime.now() - timedelta(days=random.randint(365, 1095))).strftime('%Y-%m-%d')
                
                # Insert with basic data plus new columns
                tgt_connector.execute_query(f"""
                    INSERT INTO private.employees (emp_id, first_name, last_name, email, status, hire_date)
                    VALUES ({emp_id}, 'TestFirst{emp_id}', 'TestLast{emp_id}', 'test{emp_id}@example.com', 'ACTIVE', '{hire_date}')
                    ON CONFLICT (emp_id) DO UPDATE SET
                    status = 'ACTIVE', hire_date = '{hire_date}'
                """)
            
            print("✅ Target database populated with sample data")
            tgt_connector.close()
        else:
            print("⚠️ Could not connect to target database - WHERE clause tests will use source data only")
        
        print(f"\n🎉 Enhanced test data creation completed!")
        print(f"📊 Data summary:")
        print(f"   • Employees: Enhanced with status (ACTIVE/INACTIVE/PENDING) and hire_date")
        print(f"   • Orders: Enhanced with order_date and total_amount")
        print(f"   • Products: Enhanced with status (ACTIVE/DISCONTINUED/OUT_OF_STOCK) and price")
        print(f"   • Target: Sample data for testing (100 active employees)")
        print(f"\n✅ Ready for WHERE clause testing!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating enhanced test data: {e}")
        return False
    finally:
        src_connector.close()

if __name__ == "__main__":
    success = create_enhanced_test_data()
    if success:
        print(f"\n🚀 Enhanced test data created successfully!")
        print(f"   You can now run WHERE clause tests with realistic filtering scenarios")
    else:
        print(f"\n❌ Failed to create enhanced test data")