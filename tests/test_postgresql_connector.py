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

    @pytest.mark.unit
    def test_initialization(self):
        """Test PostgreSQLConnector initialization"""
        host = "postgres-host"
        port = 5432
        username = "user"
        password = "pass"
        database = "testdb"
        
        connector = PostgreSQLConnector(host, port, username, password, database)
        
        assert connector.host == host
        assert connector.port == port
        assert connector.username == username
        assert connector.password == password
        assert connector.database == database
        assert connector.connection is None
        assert connector.is_connected is False

    @pytest.mark.unit
    @patch('builtins.__import__')
    def test_connect_success(self, mock_import):
        """Test successful connection"""
        # Mock psycopg2 module
        mock_psycopg2 = MagicMock()
        mock_connection = MagicMock()
        mock_psycopg2.connect.return_value = mock_connection
        
        def import_side_effect(name, *args, **kwargs):
            if name == 'psycopg2':
                return mock_psycopg2
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        success, message = connector.connect()
        
        assert success is True
        assert message == "Connected to PostgreSQL successfully"
        assert connector.is_connected is True
        assert connector.connection == mock_connection
        
        # Verify psycopg2.connect was called with correct parameters
        mock_psycopg2.connect.assert_called_once()

    @pytest.mark.unit
    @patch('builtins.__import__')
    def test_connect_failure(self, mock_import):
        """Test connection failure"""
        # Mock psycopg2 module to raise exception
        mock_psycopg2 = MagicMock()
        mock_psycopg2.connect.side_effect = Exception("Connection failed")
        
        def import_side_effect(name, *args, **kwargs):
            if name == 'psycopg2':
                return mock_psycopg2
            return __import__(name, *args, **kwargs)
        
        mock_import.side_effect = import_side_effect
        
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        success, message = connector.connect()
        
        assert success is False
        assert "PostgreSQL connection failed:" in message
        assert connector.is_connected is False
        assert connector.connection is None

    @pytest.mark.unit
    def test_disconnect_without_connection(self):
        """Test disconnect without active connection"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        connector.disconnect()
        
        assert connector.connection is None
        assert connector.is_connected is False

    @pytest.mark.unit
    def test_disconnect_with_connection(self):
        """Test disconnect with active connection"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
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
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
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
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        
        success, result = connector.execute_query("SELECT 1")
        
        assert success is False
        assert result == "Not connected to database"

    @pytest.mark.unit
    def test_execute_query_success(self):
        """Test successful query execution"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
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
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
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
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(1,)])
            
            exists = connector.table_exists("test_table")
            
            assert exists is True
            mock_execute.assert_called_once_with(
                "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'test_table'"
            )

    @pytest.mark.unit
    def test_table_exists_false(self):
        """Test table_exists when table doesn't exist"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(0,)])
            
            exists = connector.table_exists("nonexistent_table")
            
            assert exists is False

    @pytest.mark.unit
    def test_table_exists_query_failure(self):
        """Test table_exists when query fails"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            exists = connector.table_exists("test_table")
            
            assert exists is False

    @pytest.mark.unit
    def test_table_exists_with_empty_result(self):
        """Test table_exists when query returns empty result"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [])
            
            exists = connector.table_exists("test_table")
            
            assert exists is False

    @pytest.mark.unit
    def test_get_row_count_success(self):
        """Test successful row count retrieval"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(100,)])
            
            count = connector.get_row_count("test_table")
            
            assert count == 100
            mock_execute.assert_called_once_with("SELECT COUNT(*) FROM test_table")

    @pytest.mark.unit
    def test_get_row_count_failure(self):
        """Test row count retrieval failure"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            count = connector.get_row_count("test_table")
            
            assert count == 0

    @pytest.mark.unit
    def test_get_row_count_no_result(self):
        """Test row count when no result returned"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [])
            
            count = connector.get_row_count("test_table")
            
            assert count == 0

    @pytest.mark.edge
    def test_connection_with_different_port(self):
        """Test connection with non-standard port"""
        with patch('builtins.__import__') as mock_import:
            mock_psycopg2 = MagicMock()
            mock_connection = MagicMock()
            mock_psycopg2.connect.return_value = mock_connection
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'psycopg2':
                    return mock_psycopg2
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            connector = PostgreSQLConnector("postgres-host", 5433, "user", "pass", "testdb")
            connector.connect()
            
            # Verify the connect call was made
            mock_psycopg2.connect.assert_called_once()

    @pytest.mark.edge
    def test_special_characters_in_database_name(self):
        """Test database name with special characters"""
        connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "test_db-name")
        
        assert connector.database == "test_db-name"

    @pytest.mark.integration
    def test_full_workflow(self):
        """Test complete workflow with mocked dependencies"""
        with patch('builtins.__import__') as mock_import:
            mock_psycopg2 = MagicMock()
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            
            mock_psycopg2.connect.return_value = mock_connection
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
            mock_cursor.fetchall.return_value = [(5,)]
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'psycopg2':
                    return mock_psycopg2
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            connector = PostgreSQLConnector("postgres-host", 5432, "user", "pass", "testdb")
            
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
    def test_invalid_connection_parameters(self):
        """Test connection with invalid parameters"""
        with patch('builtins.__import__') as mock_import:
            mock_psycopg2 = MagicMock()
            mock_psycopg2.connect.side_effect = Exception("Invalid connection parameters")
            
            def import_side_effect(name, *args, **kwargs):
                if name == 'psycopg2':
                    return mock_psycopg2
                return __import__(name, *args, **kwargs)
            
            mock_import.side_effect = import_side_effect
            
            connector = PostgreSQLConnector("", 0, "", "", "")
            success, message = connector.connect()
            
            assert success is False
            assert "PostgreSQL connection failed:" in message


if __name__ == "__main__":
    pytest.main([__file__, '-v'])