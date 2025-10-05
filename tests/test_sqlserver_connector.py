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

    def test_initialization_with_default_driver(self):
        """Test proper initialization with default driver"""
        host = "sqlserver-host"
        port = 1433
        username = "testuser"
        password = "testpass"
        database = "testdb"
        
        connector = SQLServerConnector(host, port, username, password, database)
        
        assert connector.host == host
        assert connector.port == port
        assert connector.username == username
        assert connector.password == password
        assert connector.database == database
        assert connector.driver == "ODBC Driver 17 for SQL Server"
        assert connector.connection is None
        assert connector.is_connected is False

    def test_initialization_with_custom_driver(self):
        """Test initialization with custom driver"""
        connector = SQLServerConnector(
            "host", 1433, "user", "pass", "db", "ODBC Driver 18 for SQL Server"
        )
        
        assert connector.driver == "ODBC Driver 18 for SQL Server"

    @patch('src.sqlserver_connector.pyodbc')
    def test_connect_success(self, mock_pyodbc):
        """Test successful connection"""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection
        
        connector = SQLServerConnector("sqlserver-host", 1433, "user", "pass", "testdb")
        success, message = connector.connect()
        
        assert success is True
        assert message == "Connected to SQL Server successfully"
        assert connector.is_connected is True
        assert connector.connection == mock_connection
        
        expected_connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=sqlserver-host,1433;"
            "DATABASE=testdb;"
            "UID=user;"
            "PWD=pass;"
            "TrustServerCertificate=yes;"
        )
        mock_pyodbc.connect.assert_called_once_with(
            expected_connection_string,
            timeout=10
        )

    @patch('src.sqlserver_connector.pyodbc')
    def test_connect_with_custom_driver(self, mock_pyodbc):
        """Test connection with custom driver"""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection
        
        connector = SQLServerConnector(
            "host", 1433, "user", "pass", "db", "Custom ODBC Driver"
        )
        success, message = connector.connect()
        
        expected_connection_string = (
            "DRIVER={Custom ODBC Driver};"
            "SERVER=host,1433;"
            "DATABASE=db;"
            "UID=user;"
            "PWD=pass;"
            "TrustServerCertificate=yes;"
        )
        mock_pyodbc.connect.assert_called_once_with(
            expected_connection_string,
            timeout=10
        )

    @patch('src.sqlserver_connector.pyodbc')
    def test_connect_failure(self, mock_pyodbc):
        """Test connection failure"""
        mock_pyodbc.connect.side_effect = Exception("SQL Server connection failed")
        
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        success, message = connector.connect()
        
        assert success is False
        assert "SQL Server connection failed: SQL Server connection failed" in message
        assert connector.is_connected is False

    def test_disconnect_with_connection(self):
        """Test disconnect when connection exists"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        mock_connection = MagicMock()
        connector.connection = mock_connection
        connector.is_connected = True
        
        connector.disconnect()
        
        mock_connection.close.assert_called_once()
        assert connector.is_connected is False

    def test_disconnect_without_connection(self):
        """Test disconnect when no connection exists"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        connector.connection = None
        
        # Should not raise an exception
        connector.disconnect()
        assert connector.is_connected is False

    def test_execute_query_not_connected(self):
        """Test execute_query when not connected"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        connector.is_connected = False
        
        success, result = connector.execute_query("SELECT 1")
        
        assert success is False
        assert result == "Not connected to database"

    def test_execute_query_success(self):
        """Test successful query execution"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [('result1',), ('result2',)]
        
        connector.connection = mock_connection
        connector.is_connected = True
        
        success, result = connector.execute_query("SELECT * FROM test")
        
        assert success is True
        assert result == [('result1',), ('result2',)]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test")
        mock_cursor.fetchall.assert_called_once()
        mock_cursor.close.assert_called_once()

    def test_execute_query_failure(self):
        """Test query execution failure"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = Exception("Query failed")
        
        connector.connection = mock_connection
        connector.is_connected = True
        
        success, result = connector.execute_query("INVALID QUERY")
        
        assert success is False
        assert result == "Query failed"

    def test_get_tables_success(self):
        """Test successful get_tables"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [('Table1',), ('Table2',), ('Table3',)])
            
            tables = connector.get_tables()
            
            assert tables == ['Table1', 'Table2', 'Table3']
            mock_execute.assert_called_once_with(
                "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' ORDER BY table_name"
            )

    def test_get_tables_failure(self):
        """Test get_tables when query fails"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            tables = connector.get_tables()
            
            assert tables == []

    def test_table_exists_true(self):
        """Test table_exists when table exists"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(1,)])
            
            exists = connector.table_exists("TestTable")
            
            assert exists is True
            mock_execute.assert_called_once_with(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'TestTable'"
            )

    def test_table_exists_false(self):
        """Test table_exists when table doesn't exist"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(0,)])
            
            exists = connector.table_exists("NonexistentTable")
            
            assert exists is False

    def test_table_exists_query_failure(self):
        """Test table_exists when query fails"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            exists = connector.table_exists("TestTable")
            
            assert exists is False

    def test_get_row_count_success(self):
        """Test successful get_row_count"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(150,)])
            
            count = connector.get_row_count("TestTable")
            
            assert count == 150
            mock_execute.assert_called_once_with("SELECT COUNT(*) FROM [TestTable]")

    def test_get_row_count_failure(self):
        """Test get_row_count when query fails"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            count = connector.get_row_count("TestTable")
            
            assert count == 0

    def test_get_row_count_no_result(self):
        """Test get_row_count when no result returned"""
        connector = SQLServerConnector("host", 1433, "user", "pass", "db")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [])
            
            count = connector.get_row_count("TestTable")
            
            assert count == 0

    @pytest.mark.edge
    def test_connection_string_with_special_characters(self):
        """Test connection string construction with special characters"""
        with patch('src.sqlserver_connector.pyodbc') as mock_pyodbc:
            connector = SQLServerConnector(
                "host-with-dashes", 1433, "user@domain", "pass!@#$%", "db-name"
            )
            connector.connect()
            
            expected_connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=host-with-dashes,1433;"
                "DATABASE=db-name;"
                "UID=user@domain;"
                "PWD=pass!@#$%;"
                "TrustServerCertificate=yes;"
            )
            mock_pyodbc.connect.assert_called_once_with(
                expected_connection_string,
                timeout=10
            )

    @pytest.mark.edge
    def test_connection_with_different_port(self):
        """Test connection string with non-standard port"""
        with patch('src.sqlserver_connector.pyodbc') as mock_pyodbc:
            connector = SQLServerConnector("host", 1434, "user", "pass", "db")
            connector.connect()
            
            expected_connection_string = (
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=host,1434;"
                "DATABASE=db;"
                "UID=user;"
                "PWD=pass;"
                "TrustServerCertificate=yes;"
            )
            mock_pyodbc.connect.assert_called_once_with(
                expected_connection_string,
                timeout=10
            )

    @pytest.mark.integration
    def test_full_workflow(self):
        """Test complete workflow with mocked dependencies"""
        with patch('src.sqlserver_connector.pyodbc') as mock_pyodbc:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_pyodbc.connect.return_value = mock_connection
            
            # Setup mock responses
            mock_cursor.fetchall.side_effect = [
                [('Orders',), ('Products',)],  # get_tables
                [(1,)],  # table_exists
                [(200,)]  # get_row_count
            ]
            
            connector = SQLServerConnector("host", 1433, "user", "pass", "db")
            
            # Test connect
            success, message = connector.connect()
            assert success is True
            
            # Test get_tables
            tables = connector.get_tables()
            assert tables == ['Orders', 'Products']
            
            # Test table_exists
            exists = connector.table_exists("Orders")
            assert exists is True
            
            # Test get_row_count
            count = connector.get_row_count("Orders")
            assert count == 200
            
            # Test disconnect
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


if __name__ == '__main__':
    pytest.main([__file__, '-v'])