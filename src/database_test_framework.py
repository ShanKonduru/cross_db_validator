"""
Database Test Framework - Base Classes
Implements test execution framework based on test categories for smoke tests.
"""
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

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
            return None, f"Missing credentials for {environment}/{application}"
        
        # Step 2: Get connection configuration from JSON file
        config = self.config_manager.get_connection_details(environment.upper(), application.upper())
        
        if not config:
            return None, f"Missing configuration for {environment}/{application}"
        
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
                return None, f"Unsupported database type: {db_type}"
            
            return connector, f"Created {db_type.upper()} connector successfully"
            
        except KeyError as e:
            return None, f"Missing required configuration key: {e}"
        except Exception as e:
            return None, f"Error creating connector: {str(e)}"


class DatabaseTest(ABC):
    """
    Abstract base class for all database tests.
    Provides common functionality for database connection and test execution.
    """
    
    def __init__(self, environment: str, application: str, parameters: Dict[str, Any] = None):
        """
        Initialize the database test.
        
        Args:
            environment: Environment name (e.g., "DEV", "QA", "ACC")
            application: Application name (e.g., "RED", "TPS", "MDW") 
            parameters: Additional test parameters from Excel
        """
        self.environment = environment
        self.application = application
        self.parameters = parameters or {}
        self.factory = DatabaseConnectionFactory()
        self.connector = None
        self.connection_error = None
    
    def setup_connection(self) -> Tuple[bool, str]:
        """
        Establish database connection.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            self.connector, message = self.factory.create_connection(
                self.environment, 
                self.application
            )
            
            if not self.connector:
                self.connection_error = message
                return False, message
            
            # Attempt to connect
            success, connect_message = self.connector.connect()
            if not success:
                self.connection_error = connect_message
                return False, f"Connection failed: {connect_message}"
            
            return True, "Database connection established successfully"
            
        except Exception as e:
            self.connection_error = str(e)
            return False, f"Error during connection setup: {str(e)}"
    
    def teardown_connection(self):
        """Clean up database connection."""
        if self.connector:
            try:
                self.connector.disconnect()
            except Exception:
                pass  # Ignore cleanup errors
    
    @abstractmethod
    def execute_test_logic(self) -> Tuple[bool, str]:
        """
        Execute the specific test logic. Must be implemented by subclasses.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        pass
    
    def execute(self) -> str:
        """
        Main test execution method that handles setup, test execution, and cleanup.
        
        Returns:
            Test status: "PASSED", "FAILED", or "SKIPPED"
        """
        try:
            # Setup connection
            setup_success, setup_message = self.setup_connection()
            if not setup_success:
                return f"FAILED: {setup_message}"
            
            # Execute test logic
            test_success, test_message = self.execute_test_logic()
            
            # Cleanup
            self.teardown_connection()
            
            if test_success:
                return "PASSED"
            else:
                return f"FAILED: {test_message}"
                
        except Exception as e:
            self.teardown_connection()
            return f"FAILED: Unexpected error - {str(e)}"


class SetupValidationTest(DatabaseTest):
    """Test database setup and initial configuration."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Validate basic database setup."""
        try:
            # Test basic query execution
            success, result = self.connector.execute_query("SELECT 1")
            if not success:
                return False, f"Basic query failed: {result}"
            
            # Verify connection parameters
            if not self.connector.is_connected:
                return False, "Connection status inconsistent"
            
            return True, "Database setup validation passed"
            
        except Exception as e:
            return False, f"Setup validation error: {str(e)}"


class ConfigurationTest(DatabaseTest):
    """Test database configuration and settings."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Validate database configuration."""
        try:
            # Check database version and settings based on type
            connector_type = type(self.connector).__name__
            
            if "PostgreSQL" in connector_type:
                success, result = self.connector.execute_query("SELECT version()")
            elif "Oracle" in connector_type:
                success, result = self.connector.execute_query("SELECT * FROM v$version WHERE rownum = 1")
            elif "SQLServer" in connector_type:
                success, result = self.connector.execute_query("SELECT @@VERSION")
            else:
                return False, f"Unknown connector type: {connector_type}"
            
            if not success:
                return False, f"Configuration query failed: {result}"
            
            return True, f"Configuration test passed - Database accessible"
            
        except Exception as e:
            return False, f"Configuration test error: {str(e)}"


class SecurityTest(DatabaseTest):
    """Test database security and access controls."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Validate security settings and access."""
        try:
            # Test user access and permissions
            connector_type = type(self.connector).__name__
            
            if "PostgreSQL" in connector_type:
                success, result = self.connector.execute_query("SELECT current_user, session_user")
            elif "Oracle" in connector_type:
                success, result = self.connector.execute_query("SELECT USER FROM DUAL")
            elif "SQLServer" in connector_type:
                success, result = self.connector.execute_query("SELECT SYSTEM_USER, USER_NAME()")
            else:
                return False, f"Unknown connector type: {connector_type}"
            
            if not success:
                return False, f"Security query failed: {result}"
            
            # Verify we got a valid user result
            if not result or len(result) == 0:
                return False, "No user information returned"
            
            return True, "Security test passed - User access verified"
            
        except Exception as e:
            return False, f"Security test error: {str(e)}"


class ConnectionTest(DatabaseTest):
    """Test database connection stability and parameters."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Test connection stability."""
        try:
            # Test multiple queries to verify connection stability
            test_queries = [
                "SELECT 1",
                "SELECT 1 + 1", 
                "SELECT 'connection_test'"
            ]
            
            for i, query in enumerate(test_queries):
                success, result = self.connector.execute_query(query)
                if not success:
                    return False, f"Connection test query {i+1} failed: {result}"
            
            # Test connection properties
            if not hasattr(self.connector, 'host') or not self.connector.host:
                return False, "Connection missing host information"
            
            if not hasattr(self.connector, 'port') or not self.connector.port:
                return False, "Connection missing port information"
            
            return True, "Connection test passed - Stable connection verified"
            
        except Exception as e:
            return False, f"Connection test error: {str(e)}"


class QueriesTest(DatabaseTest):
    """Test database query execution capabilities."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Test various query types."""
        try:
            # Test different types of queries
            queries_to_test = []
            connector_type = type(self.connector).__name__
            
            if "PostgreSQL" in connector_type:
                queries_to_test = [
                    "SELECT 1 as test_column",
                    "SELECT NOW() as current_time",
                    "SELECT COUNT(*) FROM information_schema.tables"
                ]
            elif "Oracle" in connector_type:
                queries_to_test = [
                    "SELECT 1 as test_column FROM DUAL",
                    "SELECT SYSDATE as current_time FROM DUAL", 
                    "SELECT COUNT(*) FROM user_tables"
                ]
            elif "SQLServer" in connector_type:
                queries_to_test = [
                    "SELECT 1 as test_column",
                    "SELECT GETDATE() as current_time",
                    "SELECT COUNT(*) FROM information_schema.tables"
                ]
            
            for query in queries_to_test:
                success, result = self.connector.execute_query(query)
                if not success:
                    return False, f"Query test failed: {query} - {result}"
            
            return True, f"Queries test passed - {len(queries_to_test)} queries executed successfully"
            
        except Exception as e:
            return False, f"Queries test error: {str(e)}"


class PerformanceTest(DatabaseTest):
    """Test database performance and responsiveness."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Test basic performance metrics."""
        try:
            import time
            
            # Simple performance test - measure query execution time
            start_time = time.time()
            success, result = self.connector.execute_query("SELECT 1")
            end_time = time.time()
            
            if not success:
                return False, f"Performance test query failed: {result}"
            
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Check if execution time is reasonable (less than 5 seconds)
            max_execution_time = float(self.parameters.get('max_execution_time_ms', 5000))
            
            if execution_time > max_execution_time:
                return False, f"Performance test failed - Query took {execution_time:.2f}ms (max: {max_execution_time}ms)"
            
            return True, f"Performance test passed - Query executed in {execution_time:.2f}ms"
            
        except Exception as e:
            return False, f"Performance test error: {str(e)}"


class TableExistsTest(DatabaseTest):
    """Test if specific tables exist in the database."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Test table existence."""
        try:
            # Get table name from parameters or use default
            table_name = self.parameters.get('table_name', 'test_table')
            
            # Use the connector's table_exists method
            if hasattr(self.connector, 'table_exists'):
                exists = self.connector.table_exists(table_name)
                
                if exists:
                    return True, f"Table '{table_name}' exists"
                else:
                    return False, f"Table '{table_name}' does not exist"
            else:
                return False, "Connector does not support table_exists method"
            
        except Exception as e:
            return False, f"Table exists test error: {str(e)}"


class TableSelectTest(DatabaseTest):
    """Test data selection from tables."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Test table data selection."""
        try:
            # Get table name from parameters
            table_name = self.parameters.get('table_name', 'test_table')
            limit = self.parameters.get('row_limit', 1)
            
            # First check if table exists
            if hasattr(self.connector, 'table_exists'):
                if not self.connector.table_exists(table_name):
                    return False, f"Table '{table_name}' does not exist"
            
            # Try to select data
            query = f"SELECT * FROM {table_name}"
            
            # Add LIMIT clause based on database type
            connector_type = type(self.connector).__name__
            if "PostgreSQL" in connector_type or "SQLServer" in connector_type:
                query += f" LIMIT {limit}" if "PostgreSQL" in connector_type else f" TOP {limit}"
            elif "Oracle" in connector_type:
                query = f"SELECT * FROM {table_name} WHERE rownum <= {limit}"
            
            success, result = self.connector.execute_query(query)
            
            if not success:
                return False, f"Table select failed: {result}"
            
            return True, f"Table select successful - Retrieved {len(result) if result else 0} rows"
            
        except Exception as e:
            return False, f"Table select test error: {str(e)}"


class TableRowsTest(DatabaseTest):
    """Test table row count operations."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Test table row counting."""
        try:
            # Get table name from parameters
            table_name = self.parameters.get('table_name', 'test_table')
            
            # First check if table exists
            if hasattr(self.connector, 'table_exists'):
                if not self.connector.table_exists(table_name):
                    return False, f"Table '{table_name}' does not exist"
            
            # Use connector's get_row_count method if available
            if hasattr(self.connector, 'get_row_count'):
                row_count = self.connector.get_row_count(table_name)
                return True, f"Table '{table_name}' has {row_count} rows"
            else:
                # Fallback to manual count query
                success, result = self.connector.execute_query(f"SELECT COUNT(*) FROM {table_name}")
                
                if not success:
                    return False, f"Row count query failed: {result}"
                
                row_count = result[0][0] if result and len(result) > 0 else 0
                return True, f"Table '{table_name}' has {row_count} rows"
            
        except Exception as e:
            return False, f"Table rows test error: {str(e)}"


class TableStructureTest(DatabaseTest):
    """Test table structure and schema information."""
    
    def execute_test_logic(self) -> Tuple[bool, str]:
        """Test table structure retrieval."""
        try:
            # Get table name from parameters
            table_name = self.parameters.get('table_name', 'test_table')
            
            # First check if table exists
            if hasattr(self.connector, 'table_exists'):
                if not self.connector.table_exists(table_name):
                    return False, f"Table '{table_name}' does not exist"
            
            # Get table structure based on database type
            connector_type = type(self.connector).__name__
            
            if "PostgreSQL" in connector_type:
                # Handle schema-qualified table names (e.g., 'public.products')
                if '.' in table_name:
                    schema_name, table_only = table_name.split('.', 1)
                    # Remove quotes if present and sanitize
                    schema_name = schema_name.strip('\'"').replace("'", "''")
                    table_only = table_only.strip('\'"').replace("'", "''")
                    
                    query = f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_schema = '{schema_name}' AND table_name = '{table_only}'
                        ORDER BY ordinal_position
                    """
                else:
                    # No schema specified, use current schema
                    table_name_clean = table_name.replace("'", "''")
                    query = f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name_clean}' AND table_schema = current_schema()
                        ORDER BY ordinal_position
                    """
            elif "Oracle" in connector_type:
                # Handle schema-qualified table names for Oracle
                if '.' in table_name:
                    schema_name, table_only = table_name.split('.', 1)
                    schema_name = schema_name.strip('\'"').replace("'", "''").upper()
                    table_only = table_only.strip('\'"').replace("'", "''").upper()
                    
                    query = f"""
                        SELECT column_name, data_type, nullable 
                        FROM all_tab_columns 
                        WHERE owner = '{schema_name}' AND table_name = '{table_only}'
                        ORDER BY column_id
                    """
                else:
                    table_name_clean = table_name.replace("'", "''").upper()
                    query = f"""
                        SELECT column_name, data_type, nullable 
                        FROM user_tab_columns 
                        WHERE table_name = '{table_name_clean}'
                        ORDER BY column_id
                    """
            elif "SQLServer" in connector_type:
                # Handle schema-qualified table names for SQL Server
                if '.' in table_name:
                    schema_name, table_only = table_name.split('.', 1)
                    schema_name = schema_name.strip('\'"').replace("'", "''")
                    table_only = table_only.strip('\'"').replace("'", "''")
                    
                    query = f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_schema = '{schema_name}' AND table_name = '{table_only}'
                        ORDER BY ordinal_position
                    """
                else:
                    table_name_clean = table_name.replace("'", "''")
                    query = f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns 
                        WHERE table_name = '{table_name_clean}' AND table_schema = SCHEMA_NAME()
                        ORDER BY ordinal_position
                    """
            else:
                return False, f"Unknown connector type: {connector_type}"
            
            success, result = self.connector.execute_query(query)
            
            if not success:
                return False, f"Table structure query failed: {result}"
            
            if not result:
                return False, f"No structure information found for table '{table_name}'"
            
            column_count = len(result)
            return True, f"Table '{table_name}' structure retrieved - {column_count} columns found"
            
        except Exception as e:
            return False, f"Table structure test error: {str(e)}"


# Test factory to create appropriate test instances
class DatabaseTestFactory:
    """Factory to create database test instances based on test category."""
    
    _test_classes = {
        'SETUP': SetupValidationTest,
        'CONFIGURATION': ConfigurationTest,
        'SECURITY': SecurityTest,
        'CONNECTION': ConnectionTest,
        'QUERIES': QueriesTest,
        'PERFORMANCE': PerformanceTest,
        'TABLE_EXISTS': TableExistsTest,
        'TABLE_SELECT': TableSelectTest,
        'TABLE_ROWS': TableRowsTest,
        'TABLE_STRUCTURE': TableStructureTest,
    }
    
    @classmethod
    def create_test(cls, test_category: str, environment: str, application: str, parameters: Dict[str, Any] = None) -> DatabaseTest:
        """
        Create a database test instance based on test category.
        
        Args:
            test_category: Type of test to create
            environment: Environment name
            application: Application name
            parameters: Additional test parameters
            
        Returns:
            DatabaseTest instance or None if category not found
        """
        test_class = cls._test_classes.get(test_category.upper())
        if test_class:
            return test_class(environment, application, parameters)
        return None
    
    @classmethod
    def get_supported_categories(cls) -> list:
        """Get list of supported test categories."""
        return list(cls._test_classes.keys())