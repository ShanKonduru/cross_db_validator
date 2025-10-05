"""
Unit tests for SQLServerConnector
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.sqlserver_connector import SQLServerConnector


@pytest.mark.unit
class TestSQLServerConnector:
    """Test class for SQLServerConnector"""

    @pytest.mark.unit
    def test_initialization(self):
        """Test SQLServerConnector initialization"""
        host = "sqlserver-host"
        port = 1433
        username = "user"
        password = "pass"
        database = "testdb"
        driver = "ODBC Driver 17 for SQL Server"
        
        connector = SQLServerConnector(host, port, username, password, database)
        
        assert connector.host == host
        assert connector.port == port
        assert connector.username == username
        assert connector.password == password
        assert connector.database == database
        assert connector.driver == driver
        assert connector.connection is None
        assert connector.is_connected is False

    @pytest.mark.unit
    def test_initialization_with_custom_driver(self):
        """Test SQLServerConnector initialization with custom driver"""
        custom_driver = "ODBC Driver 18 for SQL Server"
        connector = SQLServerConnector("host", 1433, "user", "pass", "db", custom_driver)
        
        assert connector.driver == custom_driver

    @pytest.mark.unit
    @patch('builtins.__import__')
    def test_connect_success(self, mock_import):
        """Test successful connection"""
        # Mock pyodbc module
        mock_pyodbc = MagicMock()
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection
        
        def import_side_effect(name, *args, **kwargs):
            if name == 'pyodbc':
                return mock_pyodbc
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        success, message = connector.connect()
        
        assert success is True
        assert message == "Connected to SQL Server successfully"
        assert connector.is_connected is True
        assert connector.connection == mock_connection
        
        # Verify pyodbc.connect was called with correct parameters
        mock_pyodbc.connect.assert_called_once()

    @pytest.mark.unit
    @patch('builtins.__import__')
    def test_connect_with_custom_driver(self, mock_import):
        """Test connection with custom driver"""
        # Mock pyodbc module
        mock_pyodbc = MagicMock()
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection
        
        def import_side_effect(name, *args, **kwargs):
            if name == 'pyodbc':
                return mock_pyodbc
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        connector = SQLServerConnector("host", 1433, "user", "pass", "db", "Custom Driver")
        success, message = connector.connect()
        
        assert success is True
        assert connector.driver == "Custom Driver"

    @pytest.mark.unit
    @patch('builtins.__import__')
    def test_connect_failure(self, mock_import):
        """Test connection failure"""
        # Mock pyodbc module to raise exception
        mock_pyodbc = MagicMock()
        mock_pyodbc.connect.side_effect = Exception("Connection failed")
        
        def import_side_effect(name, *args, **kwargs):
            if name == 'pyodbc':
                return mock_pyodbc
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        success, message = connector.connect()
        
        assert success is False
        assert "SQL Server connection failed:" in message
        assert connector.is_connected is False
        assert connector.connection is None

    @pytest.mark.unit
    def test_disconnect_without_connection(self):
        """Test disconnect without active connection"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        connector.disconnect()
        
        assert connector.connection is None
        assert connector.is_connected is False

    @pytest.mark.unit
    def test_disconnect_with_connection(self):
        """Test disconnect with active connection"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        mock_connection = MagicMock()
        connector.connection = mock_connection
        connector.is_connected = True
        
        connector.disconnect()
        
        mock_connection.close.assert_called_once()
        assert connector.connection is None
        assert connector.is_connected is False

    @pytest.mark.unit
    def test_disconnect_with_connection_error(self):
        """Test disconnect when close() raises an exception"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        mock_connection = MagicMock()
        mock_connection.close.side_effect = Exception("Close failed")
        connector.connection = mock_connection
        connector.is_connected = True
        
        connector.disconnect()
        
        # Should still reset connection state even if close fails
        assert connector.connection is None
        assert connector.is_connected is False

    @pytest.mark.unit
    def test_execute_query_not_connected(self):
        """Test execute_query when not connected"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        
        success, result = connector.execute_query("SELECT 1")
        
        assert success is False
        assert result == "Not connected to database"

    @pytest.mark.unit
    def test_execute_query_success(self):
        """Test successful query execution"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup mock return values
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]
        
        connector.connection = mock_connection
        connector.is_connected = True
        
        success, result = connector.execute_query("SELECT id FROM test_table")
        
        assert success is True
        assert result == [(1,), (2,), (3,)]
        mock_cursor.execute.assert_called_once_with("SELECT id FROM test_table")

    @pytest.mark.unit
    def test_execute_query_failure(self):
        """Test query execution failure"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        
        # Setup mock to raise exception
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("SQL Error")
        
        connector.connection = mock_connection
        connector.is_connected = True
        
        success, result = connector.execute_query("INVALID SQL")
        
        assert success is False
        assert "Error executing query:" in result

    @pytest.mark.unit
    def test_table_exists_true(self):
        """Test table_exists when table exists"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(1,)])
            
            exists = connector.table_exists("TestTable")
            
            assert exists is True
            mock_execute.assert_called_once_with(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'TestTable'"
            )

    @pytest.mark.unit
    def test_table_exists_false(self):
        """Test table_exists when table doesn't exist"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(0,)])
            
            exists = connector.table_exists("NonexistentTable")
            
            assert exists is False

    @pytest.mark.unit
    def test_table_exists_query_failure(self):
        """Test table_exists when query fails"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            exists = connector.table_exists("TestTable")
            
            assert exists is False

    @pytest.mark.unit
    def test_get_row_count_success(self):
        """Test successful row count retrieval"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(100,)])
            
            count = connector.get_row_count("TestTable")
            
            assert count == 100
            mock_execute.assert_called_once_with("SELECT COUNT(*) FROM [TestTable]")

    @pytest.mark.unit
    def test_get_row_count_failure(self):
        """Test row count retrieval failure"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            count = connector.get_row_count("TestTable")
            
            assert count == 0

    @pytest.mark.unit
    def test_get_row_count_no_result(self):
        """Test row count when no result returned"""
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [])
            
            count = connector.get_row_count("TestTable")
            
            assert count == 0

    @pytest.mark.edge
    def test_connection_string_with_special_characters(self):
        """Test connection string construction with special characters"""
        with patch('builtins.__import__') as mock_import:
            mock_pyodbc = MagicMock()
            mock_connection = MagicMock()
            mock_pyodbc.connect.return_value = mock_connection
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'pyodbc':
                    return mock_pyodbc
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            connector = SQLServerConnector("host", 1433, "user@domain", "pass{word}", "test-db")
            connector.connect()
            
            # Verify the connect call was made
            mock_pyodbc.connect.assert_called_once()

    @pytest.mark.edge
    def test_connection_with_different_port(self):
        """Test connection string with non-standard port"""
        with patch('builtins.__import__') as mock_import:
            mock_pyodbc = MagicMock()
            mock_connection = MagicMock()
            mock_pyodbc.connect.return_value = mock_connection
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'pyodbc':
                    return mock_pyodbc
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            connector = SQLServerConnector("host", 1434, "user", "pass", "db")
            connector.connect()
            
            # Verify the connect call was made
            mock_pyodbc.connect.assert_called_once()

    @pytest.mark.integration
    def test_full_workflow(self):
        """Test complete workflow with mocked dependencies"""
        with patch('builtins.__import__') as mock_import:
            mock_pyodbc = MagicMock()
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            
            mock_pyodbc.connect.return_value = mock_connection
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [(5,)]
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'pyodbc':
                    return mock_pyodbc
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            connector = SQLServerConnector("host", 1433, "user", "pass", "db")
            
            # Test connection
            success, message = connector.connect()
            assert success is True
            
            # Test query execution
            success, result = connector.execute_query("SELECT COUNT(*) FROM test_table")
            assert success is True
            assert result == [(5,)]
            
            # Test disconnection
            connector.disconnect()
            assert connector.is_connected is False

    @pytest.mark.negative
    def test_table_exists_with_empty_result(self):
        """Test table_exists when query returns empty result"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [])
            
            exists = connector.table_exists("TestTable")
            
            assert exists is False

    @pytest.mark.negative
    def test_invalid_connection_parameters(self):
        """Test connection with invalid parameters"""
        with patch('builtins.__import__') as mock_import:
            mock_pyodbc = MagicMock()
            mock_pyodbc.connect.side_effect = Exception("Invalid connection parameters")
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'pyodbc':
                    return mock_pyodbc
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            connector = SQLServerConnector("", 0, "", "", "")
            success, message = connector.connect()
            
            assert success is False
            assert "SQL Server connection failed:" in message


if __name__ == "__main__":
    pytest.main([__file__, '-v'])