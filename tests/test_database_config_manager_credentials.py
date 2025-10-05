"""
Unit tests for DatabaseConfigManager.get_credentials() static method
"""
import os
import sys
import pytest
from unittest.mock import patch, mock_open

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.database_config_manager import DatabaseConfigManager


class TestDatabaseConfigManagerCredentials:
    """Test class for DatabaseConfigManager credential functionality"""

    @patch('src.database_config_manager.load_dotenv')
    @patch('src.database_config_manager.os.getenv')
    def test_get_credentials_success(self, mock_getenv, mock_load_dotenv):
        """Test successful credential retrieval"""
        # Setup mock return values
        mock_getenv.side_effect = lambda key: {
            'DEV_DUMMY_USERNAME': 'test_user',
            'DEV_DUMMY_PASSWORD': 'test_pass'
        }.get(key)
        
        # Call the static method
        username, password = DatabaseConfigManager.get_credentials('DEV', 'DUMMY')
        
        # Assertions
        assert username == 'test_user'
        assert password == 'test_pass'
        mock_load_dotenv.assert_called_once()
        assert mock_getenv.call_count == 2

    @patch('src.database_config_manager.load_dotenv')
    @patch('src.database_config_manager.os.getenv')
    def test_get_credentials_missing_username(self, mock_getenv, mock_load_dotenv):
        """Test when username is missing"""
        # Setup mock to return None for username, password for password
        mock_getenv.side_effect = lambda key: {
            'DEV_DUMMY_USERNAME': None,
            'DEV_DUMMY_PASSWORD': 'test_pass'
        }.get(key)
        
        # Call the static method
        username, password = DatabaseConfigManager.get_credentials('DEV', 'DUMMY')
        
        # Assertions
        assert username is None
        assert password is None
        mock_load_dotenv.assert_called_once()

    @patch('src.database_config_manager.load_dotenv')
    @patch('src.database_config_manager.os.getenv')
    def test_get_credentials_missing_password(self, mock_getenv, mock_load_dotenv):
        """Test when password is missing"""
        # Setup mock to return username but None for password
        mock_getenv.side_effect = lambda key: {
            'DEV_DUMMY_USERNAME': 'test_user',
            'DEV_DUMMY_PASSWORD': None
        }.get(key)
        
        # Call the static method
        username, password = DatabaseConfigManager.get_credentials('DEV', 'DUMMY')
        
        # Assertions
        assert username is None
        assert password is None
        mock_load_dotenv.assert_called_once()

    @patch('src.database_config_manager.load_dotenv')
    @patch('src.database_config_manager.os.getenv')
    def test_get_credentials_case_insensitive(self, mock_getenv, mock_load_dotenv):
        """Test that environment and application names are normalized to uppercase"""
        # Setup mock return values
        mock_getenv.side_effect = lambda key: {
            'DEV_DUMMY_USERNAME': 'test_user',
            'DEV_DUMMY_PASSWORD': 'test_pass'
        }.get(key)
        
        # Call with lowercase parameters
        username, password = DatabaseConfigManager.get_credentials('dev', 'dummy')
        
        # Assertions
        assert username == 'test_user'
        assert password == 'test_pass'
        mock_load_dotenv.assert_called_once()

    @patch('src.database_config_manager.load_dotenv')
    @patch('src.database_config_manager.os.getenv')
    def test_get_credentials_different_environments(self, mock_getenv, mock_load_dotenv):
        """Test credentials for different environments"""
        # Setup mock return values for multiple environments
        mock_getenv.side_effect = lambda key: {
            'QA_TPS_USERNAME': 'qa_user',
            'QA_TPS_PASSWORD': 'qa_pass',
            'PRE_PROD_RED_USERNAME': 'prod_user',
            'PRE_PROD_RED_PASSWORD': 'prod_pass'
        }.get(key)
        
        # Test QA environment
        username, password = DatabaseConfigManager.get_credentials('QA', 'TPS')
        assert username == 'qa_user'
        assert password == 'qa_pass'
        
        # Test PRE_PROD environment
        username, password = DatabaseConfigManager.get_credentials('PRE_PROD', 'RED')
        assert username == 'prod_user'
        assert password == 'prod_pass'

    @patch('src.database_config_manager.load_dotenv')
    @patch('src.database_config_manager.os.getenv')
    def test_get_credentials_all_missing(self, mock_getenv, mock_load_dotenv):
        """Test when both credentials are missing"""
        # Setup mock to return None for both
        mock_getenv.return_value = None
        
        # Call the static method
        username, password = DatabaseConfigManager.get_credentials('INVALID', 'APP')
        
        # Assertions
        assert username is None
        assert password is None
        mock_load_dotenv.assert_called_once()


@pytest.mark.integration
class TestDatabaseConfigManagerIntegration:
    """Integration tests using actual .env file"""

    def test_actual_env_file_credentials(self):
        """Test with actual .env file if available"""
        # This test will only pass if the actual .env file exists and has DEV_DUMMY credentials
        username, password = DatabaseConfigManager.get_credentials('DEV', 'DUMMY')
        
        # Check if we got actual values from the .env file
        if username and password:
            assert isinstance(username, str)
            assert isinstance(password, str)
            assert len(username) > 0
            assert len(password) > 0
        else:
            pytest.skip("No .env file or DEV_DUMMY credentials not found")

    def test_multiple_applications_dev_environment(self):
        """Test multiple applications in DEV environment"""
        applications = ['RED', 'MREE', 'SADB', 'TPS', 'MDW', 'DUMMY']
        
        for app in applications:
            username, password = DatabaseConfigManager.get_credentials('DEV', app)
            # Note: This might fail if not all credentials are set in .env
            if username and password:
                assert isinstance(username, str)
                assert isinstance(password, str)


if __name__ == '__main__':
    # Run the tests
    pytest.main([__file__, '-v'])