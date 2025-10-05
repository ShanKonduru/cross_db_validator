"""
Unit tests for PostgreSQLConnector
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.postgresql_connector import PostgreSQLConnector


@pytest.mark.unit
class TestPostgreSQLConnector:
    """Test class for PostgreSQLConnector"""

    def test_initialization(self):
        """Test proper initialization"""
        host = "localhost"
        port = 5432
        username = "testuser"
        password = "testpass"
        database = "testdb"
        
        connector = PostgreSQLConnector(host, port, username, password, database)
        
        assert connector.host == host
        assert connector.port == port
        assert connector.username == username
        assert connector.password == password
        assert connector.database == database
        assert connector.connection is None
        assert connector.is_connected is False

    @patch('src.postgresql_connector.psycopg2')
    def test_connect_success(self, mock_psycopg2):
        """Test successful connection"""
        mock_connection = MagicMock()
        mock_psycopg2.connect.return_value = mock_connection
        
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        success, message = connector.connect()
        
        assert success is True
        assert message == "Connected to PostgreSQL successfully"
        assert connector.is_connected is True
        assert connector.connection == mock_connection
        
        mock_psycopg2.connect.assert_called_once_with(
            host="localhost",
            port=5432,
            database="testdb",
            user="user",
            password="pass",
            connect_timeout=10
        )

    @patch('src.postgresql_connector.psycopg2')
    def test_connect_failure(self, mock_psycopg2):
        """Test connection failure"""
        mock_psycopg2.connect.side_effect = Exception("Connection failed")
        
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        success, message = connector.connect()
        
        assert success is False
        assert "PostgreSQL connection failed: Connection failed" in message
        assert connector.is_connected is False

    def test_disconnect_with_connection(self):
        """Test disconnect when connection exists"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        mock_connection = MagicMock()
        connector.connection = mock_connection
        connector.is_connected = True
        
        connector.disconnect()
        
        mock_connection.close.assert_called_once()
        assert connector.is_connected is False

    def test_disconnect_without_connection(self):
        """Test disconnect when no connection exists"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        connector.connection = None
        
        # Should not raise an exception
        connector.disconnect()
        assert connector.is_connected is False

    def test_execute_query_not_connected(self):
        """Test execute_query when not connected"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        connector.is_connected = False
        
        success, result = connector.execute_query("SELECT 1")
        
        assert success is False
        assert result == "Not connected to database"

    def test_execute_query_success(self):
        """Test successful query execution"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
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
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
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
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [('table1',), ('table2',), ('table3',)])
            
            tables = connector.get_tables()
            
            assert tables == ['table1', 'table2', 'table3']
            mock_execute.assert_called_once_with(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )

    def test_get_tables_failure(self):
        """Test get_tables when query fails"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            tables = connector.get_tables()
            
            assert tables == []

    def test_table_exists_true(self):
        """Test table_exists when table exists"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(1,)])
            
            exists = connector.table_exists("test_table")
            
            assert exists is True
            mock_execute.assert_called_once_with(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'test_table'"
            )

    def test_table_exists_false(self):
        """Test table_exists when table doesn't exist"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(0,)])
            
            exists = connector.table_exists("nonexistent_table")
            
            assert exists is False

    def test_table_exists_query_failure(self):
        """Test table_exists when query fails"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            exists = connector.table_exists("test_table")
            
            assert exists is False

    def test_get_row_count_success(self):
        """Test successful get_row_count"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(100,)])
            
            count = connector.get_row_count("test_table")
            
            assert count == 100
            mock_execute.assert_called_once_with("SELECT COUNT(*) FROM test_table")

    def test_get_row_count_failure(self):
        """Test get_row_count when query fails"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            count = connector.get_row_count("test_table")
            
            assert count == 0

    def test_get_row_count_no_result(self):
        """Test get_row_count when no result returned"""
        connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [])
            
            count = connector.get_row_count("test_table")
            
            assert count == 0

    @pytest.mark.edge
    def test_initialization_with_special_characters(self):
        """Test initialization with special characters in parameters"""
        connector = PostgreSQLConnector(
            "host-with-dashes", 5432, "user@domain", "pass!@#$%", "db-name_123"
        )
        
        assert connector.host == "host-with-dashes"
        assert connector.username == "user@domain"
        assert connector.password == "pass!@#$%"
        assert connector.database == "db-name_123"

    @pytest.mark.integration
    def test_full_workflow(self):
        """Test complete workflow with mocked dependencies"""
        with patch('src.postgresql_connector.psycopg2') as mock_psycopg2:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_psycopg2.connect.return_value = mock_connection
            
            # Setup mock responses
            mock_cursor.fetchall.side_effect = [
                [('table1',), ('table2',)],  # get_tables
                [(1,)],  # table_exists
                [(50,)]  # get_row_count
            ]
            
            connector = PostgreSQLConnector("localhost", 5432, "user", "pass", "testdb")
            
            # Test connect
            success, message = connector.connect()
            assert success is True
            
            # Test get_tables
            tables = connector.get_tables()
            assert tables == ['table1', 'table2']
            
            # Test table_exists
            exists = connector.table_exists("table1")
            assert exists is True
            
            # Test get_row_count
            count = connector.get_row_count("table1")
            assert count == 50
            
            # Test disconnect
            connector.disconnect()
            assert connector.is_connected is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])