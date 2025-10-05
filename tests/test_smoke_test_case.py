"""
Unit tests for SmokeTestCase
"""
import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.smoke_test_case import SmokeTestCase


@pytest.mark.unit
class TestSmokeTestCase:
    """Test class for SmokeTestCase"""

    def test_initialization_with_basic_data(self):
        """Test proper initialization with basic test case data"""
        test_data = {
            "Enable": True,
            "Test_Case_ID": "SMOKE_001",
            "Test_Case_Name": "Database Connection Test",
            "Application_Name": "TestApp",
            "Environment_Name": "DEV",
            "Priority": "High",
            "Test_Category": "Smoke",
            "Expected_Result": "Connection Successful",
            "Description": "Test database connectivity",
            "Prerequisites": "Database server running"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.enable is True
        assert test_case.test_case_id == "SMOKE_001"
        assert test_case.test_case_name == "Database Connection Test"
        assert test_case.application_name == "TestApp"
        assert test_case.environment_name == "DEV"
        assert test_case.priority == "High"
        assert test_case.test_category == "Smoke"
        assert test_case.expected_result == "Connection Successful"
        assert test_case.description == "Test database connectivity"
        assert test_case.prerequisites == "Database server running"

    def test_initialization_with_missing_fields(self):
        """Test initialization with missing optional fields"""
        test_data = {
            "Test_Case_ID": "SMOKE_002",
            "Test_Case_Name": "Basic Test"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.test_case_id == "SMOKE_002"
        assert test_case.test_case_name == "Basic Test"
        assert test_case.enable is None
        assert test_case.application_name is None
        assert test_case.environment_name is None
        assert test_case.priority is None

    def test_parse_tags_with_valid_string(self):
        """Test parsing tags from comma-separated string"""
        test_data = {
            "Test_Case_ID": "SMOKE_003",
            "Tags": "smoke, database, connectivity, integration"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.tags == ["smoke", "database", "connectivity", "integration"]

    def test_parse_tags_with_spaces_and_empty_values(self):
        """Test parsing tags with spaces and empty values"""
        test_data = {
            "Test_Case_ID": "SMOKE_004",
            "Tags": "smoke,  , database,   , connectivity"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        # Should filter out empty strings after stripping
        assert test_case.tags == ["smoke", "database", "connectivity"]

    def test_parse_tags_with_nan_value(self):
        """Test parsing tags with NaN value from pandas"""
        test_data = {
            "Test_Case_ID": "SMOKE_005",
            "Tags": pd.NA
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.tags == []

    def test_parse_tags_with_float_nan(self):
        """Test parsing tags with float NaN"""
        test_data = {
            "Test_Case_ID": "SMOKE_006",
            "Tags": float('nan')
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.tags == []

    def test_parse_tags_with_none_value(self):
        """Test parsing tags with None value"""
        test_data = {
            "Test_Case_ID": "SMOKE_007",
            "Tags": None
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.tags == []

    def test_parse_parameters_with_valid_string(self):
        """Test parsing parameters from key=value string"""
        test_data = {
            "Test_Case_ID": "SMOKE_008",
            "Parameters": "timeout=30,retry_count=3,host=localhost,port=5432"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        expected_params = {
            "timeout": "30",
            "retry_count": "3",
            "host": "localhost",
            "port": "5432"
        }
        assert test_case.parameters == expected_params

    def test_parse_parameters_with_spaces(self):
        """Test parsing parameters with spaces around keys and values"""
        test_data = {
            "Test_Case_ID": "SMOKE_009",
            "Parameters": "  timeout = 30 , retry_count= 5,  host =localhost"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        expected_params = {
            "timeout": "30",
            "retry_count": "5",
            "host": "localhost"
        }
        assert test_case.parameters == expected_params

    def test_parse_parameters_with_invalid_format(self):
        """Test parsing parameters with invalid format (no equals sign)"""
        test_data = {
            "Test_Case_ID": "SMOKE_010",
            "Parameters": "timeout=30,invalid_param,retry_count=3"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        # Should skip invalid parameters
        expected_params = {
            "timeout": "30",
            "retry_count": "3"
        }
        assert test_case.parameters == expected_params

    def test_parse_parameters_with_multiple_equals(self):
        """Test parsing parameters with multiple equals signs"""
        test_data = {
            "Test_Case_ID": "SMOKE_011",
            "Parameters": "sql=SELECT COUNT(*) FROM table WHERE id=123,timeout=30"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        # Should split only on first equals sign
        expected_params = {
            "sql": "SELECT COUNT(*) FROM table WHERE id=123",
            "timeout": "30"
        }
        assert test_case.parameters == expected_params

    def test_parse_parameters_with_nan_value(self):
        """Test parsing parameters with NaN value"""
        test_data = {
            "Test_Case_ID": "SMOKE_012",
            "Parameters": pd.NA
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.parameters == {}

    def test_parse_parameters_with_empty_string(self):
        """Test parsing parameters with empty string"""
        test_data = {
            "Test_Case_ID": "SMOKE_013",
            "Parameters": ""
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.parameters == {}

    @patch('src.smoke_test_case.choice')
    def test_execute_test_returns_passed(self, mock_choice):
        """Test execute_test returning PASSED"""
        mock_choice.return_value = "PASSED"
        
        test_case = SmokeTestCase(
            Test_Case_ID="SMOKE_014",
            Test_Case_Name="Test Execute"
        )
        
        with patch('builtins.print') as mock_print:
            result = test_case.execute_test()
        
        assert result == "PASSED"
        mock_print.assert_called_with("Executing test: Test Execute")

    @patch('src.smoke_test_case.choice')
    def test_execute_test_returns_failed(self, mock_choice):
        """Test execute_test returning FAILED"""
        mock_choice.return_value = "FAILED"
        
        test_case = SmokeTestCase(
            Test_Case_ID="SMOKE_015",
            Test_Case_Name="Test Execute Failed"
        )
        
        result = test_case.execute_test()
        assert result == "FAILED"

    @patch('src.smoke_test_case.choice')
    def test_execute_test_returns_skipped(self, mock_choice):
        """Test execute_test returning SKIPPED"""
        mock_choice.return_value = "SKIPPED"
        
        test_case = SmokeTestCase(
            Test_Case_ID="SMOKE_016",
            Test_Case_Name="Test Execute Skipped"
        )
        
        result = test_case.execute_test()
        assert result == "SKIPPED"

    def test_log_execution_status_passed(self):
        """Test logging execution status for passed test"""
        test_case = SmokeTestCase(
            Test_Case_ID="SMOKE_017",
            Test_Case_Name="Test Log Status"
        )
        
        with patch('builtins.print') as mock_print:
            test_case.log_execution_status(True)
        
        assert test_case.status == "PASSED"
        mock_print.assert_called_with("Test Case 'Test Log Status' Execution Status: PASSED")

    def test_log_execution_status_failed(self):
        """Test logging execution status for failed test"""
        test_case = SmokeTestCase(
            Test_Case_ID="SMOKE_018",
            Test_Case_Name="Test Log Status Failed"
        )
        
        with patch('builtins.print') as mock_print:
            test_case.log_execution_status(False)
        
        assert test_case.status == "FAILED"
        mock_print.assert_called_with("Test Case 'Test Log Status Failed' Execution Status: FAILED")

    def test_repr_method(self):
        """Test string representation of SmokeTestCase"""
        test_case = SmokeTestCase(
            Test_Case_ID="SMOKE_019",
            Priority="High",
            Tags="smoke,critical"
        )
        
        repr_str = repr(test_case)
        
        assert "SmokeTestCase" in repr_str
        assert "ID='SMOKE_019'" in repr_str
        assert "Priority='High'" in repr_str
        assert "Tags=['smoke', 'critical']" in repr_str

    @pytest.mark.edge
    def test_initialization_with_numeric_values(self):
        """Test initialization with numeric values as strings"""
        test_data = {
            "Test_Case_ID": 123,  # Numeric ID
            "Priority": 1,        # Numeric priority
            "Tags": 456.789       # Numeric tags
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.test_case_id == 123
        assert test_case.priority == 1
        # Numeric values should be converted to string for parsing
        assert test_case.tags == ["456.789"]

    @pytest.mark.edge
    def test_parse_tags_with_single_tag(self):
        """Test parsing tags with single tag (no commas)"""
        test_data = {
            "Test_Case_ID": "SMOKE_020",
            "Tags": "smoke"
        }
        
        test_case = SmokeTestCase(**test_data)
        
        assert test_case.tags == ["smoke"]

    @pytest.mark.edge
    def test_parse_parameters_with_empty_values(self):
        """Test parsing parameters with empty values"""
        test_data = {
            "Test_Case_ID": "SMOKE_021",
            "Parameters": "key1=value1,key2=,key3=value3,key4="
        }
        
        test_case = SmokeTestCase(**test_data)
        
        expected_params = {
            "key1": "value1",
            "key2": "",
            "key3": "value3",
            "key4": ""
        }
        assert test_case.parameters == expected_params

    @pytest.mark.integration
    def test_complete_workflow_with_pandas_data(self):
        """Test complete workflow using pandas DataFrame data"""
        # Simulate data from Excel reading
        df_data = {
            "Enable": [True, False, True],
            "Test_Case_ID": ["SMOKE_001", "SMOKE_002", "SMOKE_003"],
            "Test_Case_Name": ["Connection Test", "Auth Test", "Data Test"],
            "Application_Name": ["APP1", "APP2", "APP1"],
            "Environment_Name": ["DEV", "QA", "PROD"],
            "Priority": ["High", "Medium", "Low"],
            "Tags": ["smoke,database", pd.NA, "smoke,data,validation"],
            "Parameters": ["timeout=30,retry=3", "host=localhost", pd.NA]
        }
        
        df = pd.DataFrame(df_data)
        enabled_tests = df[df["Enable"] == True]
        
        test_objects = []
        for _, row in enabled_tests.iterrows():
            test_case = SmokeTestCase(**row.to_dict())
            test_objects.append(test_case)
        
        # Verify we got the right number of enabled tests
        assert len(test_objects) == 2
        
        # Verify first test case
        assert test_objects[0].test_case_id == "SMOKE_001"
        assert test_objects[0].tags == ["smoke", "database"]
        assert test_objects[0].parameters == {"timeout": "30", "retry": "3"}
        
        # Verify second test case
        assert test_objects[1].test_case_id == "SMOKE_003"
        assert test_objects[1].tags == ["smoke", "data", "validation"]
        assert test_objects[1].parameters == {}

    @pytest.mark.negative
    def test_parse_parameters_exception_handling(self):
        """Test that parse_parameters handles exceptions gracefully"""
        test_data = {
            "Test_Case_ID": "SMOKE_022",
            "Parameters": "key1=value1,key2"  # Missing value causes ValueError in split
        }
        
        # Should not raise exception, just skip invalid parameters
        test_case = SmokeTestCase(**test_data)
        
        # Should only include valid parameters
        assert test_case.parameters == {"key1": "value1"}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])