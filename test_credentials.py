#!/usr/bin/env python3
"""
Test script to demonstrate the usage of DatabaseConfigManager.get_credentials() static method.
This script shows how to retrieve username and password for different environments and applications.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database_config_manager import DatabaseConfigManager


def test_get_credentials():
    """Test the get_credentials static method with various environment and application combinations."""
    
    print("=" * 80)
    print("Testing DatabaseConfigManager.get_credentials() Static Method")
    print("=" * 80)
    
    # Test cases: (environment, application, description)
    test_cases = [
        ("DEV", "DUMMY", "Development DUMMY PostgreSQL"),
        ("DEV", "RED", "Development RED Oracle"),
        ("QA", "TPS", "QA TPS PostgreSQL"),
        ("ACC", "MDW", "Acceptance MDW SQL Server"),
        ("NP1", "MREE", "Non-Production 1 MREE Oracle"),
        ("PRE_PROD", "SADB", "Pre-Production SADB Oracle"),
        ("INVALID", "TEST", "Invalid environment/application (should fail)"),
    ]
    
    for environment, application, description in test_cases:
        print(f"\n--- Testing: {description} ---")
        print(f"Environment: {environment}, Application: {application}")
        
        try:
            username, password = DatabaseConfigManager.get_credentials(environment, application)
            
            if username and password:
                print(f"✅ SUCCESS: Found credentials")
                print(f"   Username: {username}")
                print(f"   Password: {'*' * len(password)}")  # Mask password for security
            else:
                print(f"❌ FAILED: No credentials found")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 80)
    print("Test completed")
    print("=" * 80)


def demo_real_usage():
    """Demonstrate real-world usage scenarios."""
    
    print("\n" + "=" * 80)
    print("Real-world Usage Examples")
    print("=" * 80)
    
    # Example 1: Get credentials for database connection
    print("\n--- Example 1: Getting DEV DUMMY credentials for database connection ---")
    username, password = DatabaseConfigManager.get_credentials("DEV", "DUMMY")
    
    if username and password:
        print(f"Connecting to database with username: {username}")
        # In real usage, you would use these credentials to connect to the database
        # connection = some_db_connector(username=username, password=password, ...)
        print("✅ Ready to establish database connection")
    else:
        print("❌ Cannot connect: Missing credentials")
    
    # Example 2: Loop through multiple environments for the same application
    print("\n--- Example 2: Getting TPS credentials across all environments ---")
    environments = ["DEV", "QA", "ACC", "NP1", "PRE_PROD"]
    
    for env in environments:
        username, password = DatabaseConfigManager.get_credentials(env, "TPS")
        status = "✅ Available" if username and password else "❌ Missing"
        print(f"   {env} TPS: {status}")
    
    # Example 3: Validation before processing
    print("\n--- Example 3: Validate credentials before test execution ---")
    test_environment = "DEV"
    test_application = "DUMMY"
    
    username, password = DatabaseConfigManager.get_credentials(test_environment, test_application)
    
    if username and password:
        print(f"✅ Credentials validated for {test_environment}/{test_application}")
        print("   Proceeding with test execution...")
        # Here you would execute your actual test logic
    else:
        print(f"❌ Cannot proceed: Missing credentials for {test_environment}/{test_application}")
        print("   Please check your .env file and ensure the required environment variables are set")


if __name__ == "__main__":
    # Run the tests
    test_get_credentials()
    
    # Show real-world usage examples
    demo_real_usage()
    
    print(f"\nNOTE: Make sure to run '003_setup.bat' to install 'python-dotenv' if you see import errors.")
    print(f"Expected .env file location: {os.path.abspath('.env')}")