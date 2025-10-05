"""
Unit tests for OracleConnector - Simplified version focusing on actual class structure
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.oracle_connector import OracleConnector


@pytest.mark.unit
class TestOracleConnectorSimplified:
    """Test class for OracleConnector - focusing on structure and basic functionality"""

    def test_initialization(self):
        """Test proper initialization of OracleConnector"""
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

    def test_dsn_construction_concept(self):
        """Test that DSN components are available for construction"""
        connector = OracleConnector("localhost", 1521, "user", "pass", "XE")
        
        # Test that we can construct a DSN from the components
        expected_dsn = f"{connector.host}:{connector.port}/{connector.service_name}"
        assert expected_dsn == "localhost:1521/XE"

    def test_inheritance_from_base_class(self):
        """Test that OracleConnector properly inherits from DatabaseConnectionBase"""
        from src.database_connection_base import DatabaseConnectionBase
        
        connector = OracleConnector("host", 1521, "user", "pass", "ORCL")
        
        assert isinstance(connector, DatabaseConnectionBase)
        assert hasattr(connector, 'connect')
        assert hasattr(connector, 'disconnect')
        assert hasattr(connector, 'execute_query')
        assert hasattr(connector, 'get_tables')
        assert hasattr(connector, 'table_exists')
        assert hasattr(connector, 'get_row_count')

    def test_table_exists_with_mock_execute_query(self):
        """Test table_exists method using mocked execute_query"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")

        with patch.object(connector, 'execute_query') as mock_execute:
            # Mock successful query with result indicating table exists (row-based data)
            mock_execute.return_value = (True, [(1,)])  # COUNT returns 1 as tuple
            exists = connector.table_exists("TEST_TABLE")
            assert exists is True
            
            # Test table doesn't exist
            mock_execute.return_value = (True, [(0,)])  # COUNT returns 0
            exists = connector.table_exists("NON_EXISTENT_TABLE")
            assert exists is False

    def test_get_tables_with_mock_execute_query(self):
        """Test get_tables method using mocked execute_query"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            # Mock successful query (row-based data)
            mock_execute.return_value = (True, [('TABLE1',), ('TABLE2',)])
            
            tables = connector.get_tables()
            assert tables == ['TABLE1', 'TABLE2']
            
            # Test failed query
            mock_execute.return_value = (False, "Query failed")
            tables = connector.get_tables()
            assert tables == []

    def test_get_row_count_with_mock_execute_query(self):
        """Test get_row_count method using mocked execute_query"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        with patch.object(connector, 'execute_query') as mock_execute:
            # Mock successful query (row-based data)
            mock_execute.return_value = (True, [(100,)])
            
            count = connector.get_row_count("TEST_TABLE")
            assert count == 100
            
            # Test failed query
            mock_execute.return_value = (False, "Query failed")
            count = connector.get_row_count("TEST_TABLE")
            assert count == 0

    @pytest.mark.edge
    def test_initialization_with_different_service_names(self):
        """Test initialization with various service name formats"""
        connector1 = OracleConnector("host", 1521, "user", "pass", "ORCL")
        connector2 = OracleConnector("host", 1521, "user", "pass", "XE")
        connector3 = OracleConnector("host", 1521, "user", "pass", "SERVICE.DOMAIN")
        
        assert connector1.service_name == "ORCL"
        assert connector2.service_name == "XE"
        assert connector3.service_name == "SERVICE.DOMAIN"

    @pytest.mark.integration
    def test_method_call_structure(self):
        """Test that all expected methods can be called without errors in structure"""
        connector = OracleConnector("test-host", 1521, "test_user", "test_pass", "TEST_DB")
        
        # Test that methods exist and are callable
        assert callable(connector.connect)
        assert callable(connector.disconnect)
        assert callable(connector.execute_query)
        assert callable(connector.get_tables)
        assert callable(connector.table_exists)
        assert callable(connector.get_row_count)

    @pytest.mark.negative
    def test_connection_methods_when_not_connected(self):
        """Test behavior of methods when not connected"""
        connector = OracleConnector("oracle-host", 1521, "user", "pass", "ORCL")
        
        # These should handle the not-connected state gracefully
        success, result = connector.execute_query("SELECT 1 FROM dual")
        assert success is False
        
        # get_tables returns empty list on failure
        tables = connector.get_tables()
        assert tables == []
        
        # get_row_count returns 0 on failure
        count = connector.get_row_count("TEST_TABLE")
        assert count == 0

    def test_repr_method(self):
        """Test string representation of OracleConnector"""
        connector = OracleConnector("oracle-host", 1521, "testuser", "testpass", "ORCL")
        repr_str = repr(connector)
        
        # Should contain key identifying information
        assert "OracleConnector" in repr_str or "oracle" in repr_str.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])