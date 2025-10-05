#!/usr/bin/env python3
"""
Enhanced Database Connection Example
Demonstrates how to use DatabaseConfigManager.get_credentials() with database connectors.
This example shows a complete workflow from getting credentials to establishing database connections.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database_config_manager import DatabaseConfigManager
from src.postgresql_connector import PostgreSQLConnector
from src.oracle_connector import OracleConnector
from src.sqlserver_connector import SQLServerConnector


class DatabaseConnectionFactory:
    """
    Factory class that combines DatabaseConfigManager for credentials
    with database connectors for establishing connections.
    """
    
    def __init__(self, config_file_path: str = "configs/database_connections.json"):
        """
        Initialize the factory with configuration file path.
        
        Args:
            config_file_path: Path to the database configuration JSON file
        """
        self.config_manager = DatabaseConfigManager(config_file_path)
    
    def create_connection(self, environment: str, application: str):
        """
        Create and return a database connection using environment variables for credentials
        and configuration file for connection details.
        
        Args:
            environment: Environment name (e.g., "DEV", "QA", "ACC")
            application: Application name (e.g., "RED", "TPS", "MDW")
            
        Returns:
            Database connector instance or None if failed
        """
        # Step 1: Get credentials from environment variables
        username, password = DatabaseConfigManager.get_credentials(environment, application)
        
        if not username or not password:
            print(f"❌ Cannot create connection: Missing credentials for {environment}/{application}")
            return None
        
        # Step 2: Get connection configuration from JSON file
        config = self.config_manager.get_connection_details(environment.upper(), application.upper())
        
        if not config:
            print(f"❌ Cannot create connection: Missing configuration for {environment}/{application}")
            return None
        
        # Step 3: Create the appropriate connector based on database type
        db_type = config.get('db_type', '').lower()
        
        try:
            if db_type == 'postgresql':
                connector = PostgreSQLConnector(
                    host=config['host'],
                    port=config['port'],
                    username=username,
                    password=password,
                    database=config['database']
                )
                
            elif db_type == 'oracle':
                connector = OracleConnector(
                    host=config['host'],
                    port=config['port'],
                    username=username,
                    password=password,
                    service_name=config['service_name']
                )
                
            elif db_type == 'sqlserver':
                connector = SQLServerConnector(
                    host=config['host'],
                    port=config['port'],
                    username=username,
                    password=password,
                    database=config['database'],
                    driver=config.get('driver', 'ODBC Driver 17 for SQL Server')
                )
                
            else:
                print(f"❌ Unsupported database type: {db_type}")
                return None
            
            print(f"✅ Created {db_type.upper()} connector for {environment}/{application}")
            return connector
            
        except KeyError as e:
            print(f"❌ Missing required configuration key: {e}")
            return None
        except Exception as e:
            print(f"❌ Error creating connector: {str(e)}")
            return None


def demo_database_connections():
    """Demonstrate creating and testing database connections."""
    
    print("=" * 80)
    print("Database Connection Factory Demo")
    print("=" * 80)
    
    # Initialize the factory
    factory = DatabaseConnectionFactory()
    
    # Test different database connections
    test_connections = [
        ("DEV", "DUMMY", "PostgreSQL Development Database"),
        ("DEV", "RED", "Oracle Development Database"),
        ("QA", "MDW", "SQL Server QA Database"),
        ("ACC", "TPS", "PostgreSQL Acceptance Database"),
    ]
    
    for environment, application, description in test_connections:
        print(f"\n--- Testing: {description} ---")
        print(f"Environment: {environment}, Application: {application}")
        
        # Create connection
        connector = factory.create_connection(environment, application)
        
        if connector:
            print(f"✅ Connector created successfully")
            print(f"   Database Type: {type(connector).__name__}")
            print(f"   Host: {connector.host}")
            print(f"   Port: {connector.port}")
            print(f"   Username: {connector.username}")
            
            # Uncomment the following lines to test actual connection
            # WARNING: This will try to connect to real databases
            # success, message = connector.connect()
            # if success:
            #     print(f"✅ Connection successful: {message}")
            #     connector.disconnect()
            # else:
            #     print(f"❌ Connection failed: {message}")
        else:
            print(f"❌ Failed to create connector")


def demo_credential_validation():
    """Demonstrate credential validation before test execution."""
    
    print("\n" + "=" * 80)
    print("Credential Validation Demo")
    print("=" * 80)
    
    # Simulate a test suite that needs to validate credentials for multiple databases
    required_connections = [
        ("DEV", "DUMMY"),
        ("DEV", "RED"), 
        ("QA", "TPS"),
        ("ACC", "MDW"),
    ]
    
    print("Validating credentials for test suite execution...")
    
    missing_credentials = []
    available_credentials = []
    
    for environment, application in required_connections:
        username, password = DatabaseConfigManager.get_credentials(environment, application)
        
        if username and password:
            available_credentials.append(f"{environment}/{application}")
            print(f"✅ {environment}/{application}: Credentials available")
        else:
            missing_credentials.append(f"{environment}/{application}")
            print(f"❌ {environment}/{application}: Credentials missing")
    
    print(f"\n--- Validation Summary ---")
    print(f"Available: {len(available_credentials)} connections")
    print(f"Missing: {len(missing_credentials)} connections")
    
    if missing_credentials:
        print(f"\n⚠️  WARNING: The following connections are missing credentials:")
        for conn in missing_credentials:
            env, app = conn.split('/')
            print(f"   - {conn} (Expected: {env}_{app}_USERNAME, {env}_{app}_PASSWORD)")
        print(f"\nPlease update your .env file before running tests.")
    else:
        print(f"\n🎉 All required credentials are available. Ready to run tests!")


def demo_environment_specific_operations():
    """Demonstrate environment-specific database operations."""
    
    print("\n" + "=" * 80)
    print("Environment-Specific Operations Demo")
    print("=" * 80)
    
    # Example: Run smoke tests on DEV environment databases
    dev_applications = ["RED", "MREE", "SADB", "TPS", "MDW", "DUMMY"]
    
    print("Checking DEV environment database credentials for smoke tests...")
    
    for app in dev_applications:
        username, password = DatabaseConfigManager.get_credentials("DEV", app)
        
        if username and password:
            print(f"✅ DEV/{app}: Ready for smoke tests")
            # Here you would run actual smoke tests
            # run_smoke_tests(environment="DEV", application=app, username=username, password=password)
        else:
            print(f"❌ DEV/{app}: Cannot run smoke tests - missing credentials")
    
    print("\n--- Cross-Environment Validation ---")
    
    # Example: Validate that the same application has credentials across environments
    target_app = "DUMMY"
    environments = ["DEV", "QA", "ACC", "NP1", "PRE_PROD"]
    
    print(f"Checking {target_app} credentials across all environments...")
    
    for env in environments:
        username, password = DatabaseConfigManager.get_credentials(env, target_app)
        status = "✅ Available" if (username and password) else "❌ Missing"
        print(f"   {env}/{target_app}: {status}")


if __name__ == "__main__":
    print("Enhanced Database Connection Example")
    print("This example demonstrates how to use DatabaseConfigManager.get_credentials()")
    print("with database connectors for complete database connection management.\n")
    
    # Run all demonstrations
    demo_database_connections()
    demo_credential_validation()
    demo_environment_specific_operations()
    
    print(f"\n" + "=" * 80)
    print("Demo completed!")
    print("=" * 80)
    
    print(f"\nQuick Usage Reference:")
    print(f"# Get credentials")
    print(f"username, password = DatabaseConfigManager.get_credentials('DEV', 'DUMMY')")
    print(f"")
    print(f"# Create database connection")
    print(f"factory = DatabaseConnectionFactory()")
    print(f"connector = factory.create_connection('DEV', 'DUMMY')")
    print(f"")
    print(f"# Test connection")
    print(f"success, message = connector.connect()")
    print(f"if success:")
    print(f"    print('Connected successfully')")
    print(f"    connector.disconnect()")
    
    print(f"\nNote: Install dependencies with '003_setup.bat' if you see import errors.")