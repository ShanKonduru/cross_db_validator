"""
Unit tests for OracleConnector
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.oracle_connector import OracleConnector


@pytest.mark.unit
class TestOracleConnector:
    """Test class for OracleConnector"""

    def test_initialization(self):
        """Test proper initialization"""
        host = "oracle-host"
        port = 1521
        username = "testuser"
        password = "testpass"
        service_name = "ORCL"
        
        connector = OracleConnector(host, port, username, password, service_name)
        
        assert connector.host == host
        assert connector.port == port
        assert connector.username == username
        assert connector.password == password
        assert connector.service_name == service_name
        assert connector.connection is None
        assert connector.is_connected is False

    @patch('src.oracle_connector.oracledb')
    def test_connect_success(self, mock_oracledb):
        """Test successful connection"""
        mock_connection = MagicMock()
        mock_oracledb.connect.return_value = mock_connection
        
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        success, message = connector.connect()
        
        assert success is True
        assert message == "Connected to Oracle successfully"
        assert connector.is_connected is True
        assert connector.connection == mock_connection
        
        expected_dsn = "oracle-host:1521/ORCL"
        mock_oracledb.connect.assert_called_once_with(
            user="user",
            password="pass",
            dsn=expected_dsn
        )

    @patch('src.oracle_connector.oracledb')
    def test_connect_failure(self, mock_oracledb):
        """Test connection failure"""
        mock_oracledb.connect.side_effect = Exception("Oracle connection failed")
        
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        success, message = connector.connect()
        
        assert success is False
        assert "Oracle connection failed: Oracle connection failed" in message
        assert connector.is_connected is False

    def test_disconnect_with_connection(self):
        """Test disconnect when connection exists"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        mock_connection = MagicMock()
        connector.connection = mock_connection
        connector.is_connected = True
        
        connector.disconnect()
        
        mock_connection.close.assert_called_once()
        assert connector.is_connected is False

    def test_disconnect_without_connection(self):
        """Test disconnect when no connection exists"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        connector.connection = None
        
        # Should not raise an exception
        connector.disconnect()
        assert connector.is_connected is False

    def test_execute_query_not_connected(self):
        """Test execute_query when not connected"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        connector.is_connected = False
        
        success, result = connector.execute_query("SELECT 1 FROM DUAL")
        
        assert success is False
        assert result == "Not connected to database"

    def test_execute_query_success(self):
        """Test successful query execution"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
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
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
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
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [('TABLE1',), ('TABLE2',), ('TABLE3',)])
            
            tables = connector.get_tables()
            
            assert tables == ['TABLE1', 'TABLE2', 'TABLE3']
            mock_execute.assert_called_once_with(
                "SELECT table_name FROM user_tables ORDER BY table_name"
            )

    def test_get_tables_failure(self):
        """Test get_tables when query fails"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            tables = connector.get_tables()
            
            assert tables == []

    def test_table_exists_true(self):
        """Test table_exists when table exists"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(1,)])
            
            exists = connector.table_exists("TEST_TABLE")
            
            assert exists is True
            mock_execute.assert_called_once_with(
                "SELECT COUNT(*) FROM user_tables WHERE table_name = UPPER('TEST_TABLE')"
            )

    def test_table_exists_false(self):
        """Test table_exists when table doesn't exist"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(0,)])
            
            exists = connector.table_exists("NONEXISTENT_TABLE")
            
            assert exists is False

    def test_table_exists_query_failure(self):
        """Test table_exists when query fails"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            exists = connector.table_exists("TEST_TABLE")
            
            assert exists is False

    def test_get_row_count_success(self):
        """Test successful get_row_count"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [(100,)])
            
            count = connector.get_row_count("TEST_TABLE")
            
            assert count == 100
            mock_execute.assert_called_once_with("SELECT COUNT(*) FROM TEST_TABLE")

    def test_get_row_count_failure(self):
        """Test get_row_count when query fails"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (False, "Query failed")
            
            count = connector.get_row_count("TEST_TABLE")
            
            assert count == 0

    def test_get_row_count_no_result(self):
        """Test get_row_count when no result returned"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [])
            
            count = connector.get_row_count("TEST_TABLE")
            
            assert count == 0

    @pytest.mark.edge
    def test_initialization_with_special_service_name(self):
        """Test initialization with different service name formats"""
        connector = OracleConnector(
            "oracle-prod.company.com", 1521, "user", "pass", "PROD.WORLD"
        )
        
        assert connector.service_name == "PROD.WORLD"

    @pytest.mark.edge
    def test_dsn_construction_with_different_ports(self):
        """Test DSN construction with different port numbers"""
        with patch('src.oracle_connector.oracledb') as mock_oracledb:
            connector = OracleConnector("oracle-host", 1522, "user", "pass", "ORCL")
            connector.connect()
            
            expected_dsn = "oracle-host:1522/ORCL"
            mock_oracledb.connect.assert_called_once_with(
                user="user",
                password="pass",
                dsn=expected_dsn
            )

    @pytest.mark.integration
    def test_full_workflow(self):
        """Test complete workflow with mocked dependencies"""
        with patch('src.oracle_connector.oracledb') as mock_oracledb:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_oracledb.connect.return_value = mock_connection
            
            # Setup mock responses
            mock_cursor.fetchall.side_effect = [
                [('TABLE1',), ('TABLE2',)],  # get_tables
                [(1,)],  # table_exists
                [(75,)]  # get_row_count
            ]
            
            connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
            
            # Test connect
            success, message = connector.connect()
            assert success is True
            
            # Test get_tables
            tables = connector.get_tables()
            assert tables == ['TABLE1', 'TABLE2']
            
            # Test table_exists
            exists = connector.table_exists("TABLE1")
            assert exists is True
            
            # Test get_row_count
            count = connector.get_row_count("TABLE1")
            assert count == 75
            
            # Test disconnect
            connector.disconnect()
            assert connector.is_connected is False

    @pytest.mark.negative
    def test_table_exists_with_empty_result(self):
        """Test table_exists when query returns empty result"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            mock_execute.return_value = (True, [])
            
            exists = connector.table_exists("TEST_TABLE")
            
            assert exists is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])