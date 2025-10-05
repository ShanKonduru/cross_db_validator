"""
Unit tests for DatabaseConnectionBase abstract class
"""
import os
import sys
import pytest
from abc import ABC
from unittest.mock import MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.database_connection_base import DatabaseConnectionBase


class ConcreteDatabaseConnection(DatabaseConnectionBase):
    """Concrete implementation for testing the abstract base class"""
    
    def connect(self):
        """Mock implementation"""
        self.is_connected = True
        return True, "Connected successfully"
    
    def disconnect(self):
        """Mock implementation"""
        self.is_connected = False
    
    def execute_query(self, query):
        """Mock implementation"""
        if not self.is_connected:
            return False, "Not connected"
        return True, [("result",)]
    
    def get_tables(self):
        """Mock implementation"""
        return ["table1", "table2"]
    
    def table_exists(self, table_name):
        """Mock implementation"""
        return table_name in ["table1", "table2"]
    
    def get_row_count(self, table_name):
        """Mock implementation"""
        return 100 if table_name in ["table1", "table2"] else 0


@pytest.mark.unit
class TestDatabaseConnectionBase:
    """Test class for DatabaseConnectionBase"""

    def test_initialization(self):
        """Test proper initialization of base class"""
        host = "localhost"
        port = 5432
        username = "testuser"
        password = "testpass"
        
        connection = ConcreteDatabaseConnection(host, port, username, password)
        
        assert connection.host == host
        assert connection.port == port
        assert connection.username == username
        assert connection.password == password
        assert connection.connection is None
        assert connection.is_connected is False

    def test_initialization_with_kwargs(self):
        """Test initialization with additional keyword arguments"""
        connection = ConcreteDatabaseConnection(
            "localhost", 5432, "user", "pass", 
            database="testdb", schema="public"
        )
        
        assert connection.host == "localhost"
        assert connection.port == 5432
        assert connection.username == "user"
        assert connection.password == "pass"

    def test_concrete_implementation_connect(self):
        """Test concrete implementation of connect method"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        
        success, message = connection.connect()
        
        assert success is True
        assert message == "Connected successfully"
        assert connection.is_connected is True

    def test_concrete_implementation_disconnect(self):
        """Test concrete implementation of disconnect method"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        connection.is_connected = True
        
        connection.disconnect()
        
        assert connection.is_connected is False

    def test_concrete_implementation_execute_query_connected(self):
        """Test execute_query when connected"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        connection.is_connected = True
        
        success, result = connection.execute_query("SELECT * FROM test")
        
        assert success is True
        assert result == [("result",)]

    def test_concrete_implementation_execute_query_not_connected(self):
        """Test execute_query when not connected"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        connection.is_connected = False
        
        success, result = connection.execute_query("SELECT * FROM test")
        
        assert success is False
        assert result == "Not connected"

    def test_concrete_implementation_get_tables(self):
        """Test get_tables implementation"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        
        tables = connection.get_tables()
        
        assert tables == ["table1", "table2"]

    def test_concrete_implementation_table_exists_true(self):
        """Test table_exists when table exists"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        
        exists = connection.table_exists("table1")
        
        assert exists is True

    def test_concrete_implementation_table_exists_false(self):
        """Test table_exists when table doesn't exist"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        
        exists = connection.table_exists("nonexistent")
        
        assert exists is False

    def test_concrete_implementation_get_row_count_existing_table(self):
        """Test get_row_count for existing table"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        
        count = connection.get_row_count("table1")
        
        assert count == 100

    def test_concrete_implementation_get_row_count_nonexistent_table(self):
        """Test get_row_count for non-existent table"""
        connection = ConcreteDatabaseConnection("localhost", 5432, "user", "pass")
        
        count = connection.get_row_count("nonexistent")
        
        assert count == 0

    def test_abstract_class_cannot_be_instantiated(self):
        """Test that the abstract base class cannot be instantiated directly"""
        with pytest.raises(TypeError):
            DatabaseConnectionBase("localhost", 5432, "user", "pass")

    @pytest.mark.edge
    def test_initialization_with_empty_strings(self):
        """Test initialization with empty string parameters"""
        connection = ConcreteDatabaseConnection("", 0, "", "")
        
        assert connection.host == ""
        assert connection.port == 0
        assert connection.username == ""
        assert connection.password == ""

    @pytest.mark.edge
    def test_initialization_with_none_values(self):
        """Test initialization with None values"""
        connection = ConcreteDatabaseConnection(None, None, None, None)
        
        assert connection.host is None
        assert connection.port is None
        assert connection.username is None
        assert connection.password is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])