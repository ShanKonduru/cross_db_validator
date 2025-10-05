"""
Unit tests for DataValidationTestCase
"""
import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.data_validation_test_case import DataValidationTestCase


@pytest.mark.unit
class TestDataValidationTestCase:
    """Test class for DataValidationTestCase"""

    def test_initialization_with_basic_data(self):
        """Test proper initialization with basic test case data"""
        test_data = {
            "Enable": True,
            "Test_Case_ID": "DV_001",
            "Test_Case_Name": "Data Count Validation",
            "Application_Name": "TestApp",
            "Environment_Name": "DEV",
            "Priority": "High",
            "Test_Category": "Data Validation",
            "Expected_Result": "Validation successful",
            "Description": "Test data validation",
            "Prerequisites": "Database available"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        assert test_case.enable is True
        assert test_case.test_case_id == "DV_001"
        assert test_case.test_case_name == "Data Count Validation"
        assert test_case.application_name == "TestApp"
        assert test_case.environment_name == "DEV"
        assert test_case.priority == "High"
        assert test_case.test_category == "Data Validation"
        assert test_case.expected_result == "Validation successful"
        assert test_case.description == "Test data validation"
        assert test_case.prerequisites == "Database available"

    def test_initialization_with_missing_fields(self):
        """Test initialization with missing optional fields"""
        test_data = {
            "Test_Case_ID": "DV_002",
            "Test_Case_Name": "Basic Validation Test"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        assert test_case.test_case_id == "DV_002"
        assert test_case.test_case_name == "Basic Validation Test"
        assert test_case.enable is None
        assert test_case.application_name is None
        assert test_case.environment_name is None

    def test_parse_tags_with_validation_specific_tags(self):
        """Test parsing tags with data validation specific tags"""
        test_data = {
            "Test_Case_ID": "DV_003",
            "Tags": "data_validation, count_check, critical, regression"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        assert test_case.tags == ["data_validation", "count_check", "critical", "regression"]

    def test_parse_parameters_with_validation_config(self):
        """Test parsing parameters with validation configuration"""
        test_data = {
            "Test_Case_ID": "DV_004",
            "Parameters": "tolerance=0.01,timeout=300,retry_count=3,comparison_type=exact"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        expected_params = {
            "tolerance": "0.01",
            "timeout": "300",
            "retry_count": "3",
            "comparison_type": "exact"
        }
        assert test_case.parameters == expected_params

    def test_parse_tags_with_spaces_and_empty_values(self):
        """Test parsing tags with spaces and empty values"""
        test_data = {
            "Test_Case_ID": "DV_005",
            "Tags": "data_validation,  , critical,   , regression"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        # Should filter out empty strings after stripping
        assert test_case.tags == ["data_validation", "critical", "regression"]

    def test_parse_tags_with_nan_value(self):
        """Test parsing tags with NaN value from pandas"""
        test_data = {
            "Test_Case_ID": "DV_006",
            "Tags": pd.NA
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        assert test_case.tags == []

    def test_parse_tags_with_float_nan(self):
        """Test parsing tags with float NaN"""
        test_data = {
            "Test_Case_ID": "DV_007",
            "Tags": float('nan')
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        assert test_case.tags == []

    def test_parse_parameters_with_spaces(self):
        """Test parsing parameters with spaces around keys and values"""
        test_data = {
            "Test_Case_ID": "DV_008",
            "Parameters": "  timeout = 30 , retry_count= 5,  host =localhost"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        expected_params = {
            "timeout": "30",
            "retry_count": "5",
            "host": "localhost"
        }
        assert test_case.parameters == expected_params

    def test_parse_parameters_with_invalid_format(self):
        """Test parsing parameters with invalid format (no equals sign)"""
        test_data = {
            "Test_Case_ID": "DV_009",
            "Parameters": "timeout=30,invalid_param,retry_count=3"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        # Should skip invalid parameters
        expected_params = {
            "timeout": "30",
            "retry_count": "3"
        }
        assert test_case.parameters == expected_params

    def test_parse_parameters_with_multiple_equals(self):
        """Test parsing parameters with multiple equals signs"""
        test_data = {
            "Test_Case_ID": "DV_010",
            "Parameters": "sql=SELECT COUNT(*) FROM table WHERE id=123,timeout=30"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        # Should split only on first equals sign
        expected_params = {
            "sql": "SELECT COUNT(*) FROM table WHERE id=123",
            "timeout": "30"
        }
        assert test_case.parameters == expected_params

    def test_parse_parameters_with_nan_value(self):
        """Test parsing parameters with NaN value"""
        test_data = {
            "Test_Case_ID": "DV_011",
            "Parameters": pd.NA
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        assert test_case.parameters == {}

    @patch('src.data_validation_test_case.random.choice')
    def test_execute_test_returns_passed(self, mock_choice):
        """Test execute_test returning PASSED"""
        mock_choice.return_value = "PASSED"
        
        test_case = DataValidationTestCase(
            Test_Case_ID="DV_012",
            Test_Case_Name="Test Execute"
        )
        
        with patch('builtins.print') as mock_print:
            result = test_case.execute_test()
        
        assert result == "PASSED"
        mock_print.assert_called_with("Executing test: Test Execute")

    @patch('src.data_validation_test_case.random.choice')
    def test_execute_test_returns_failed(self, mock_choice):
        """Test execute_test returning FAILED"""
        mock_choice.return_value = "FAILED"
        
        test_case = DataValidationTestCase(
            Test_Case_ID="DV_013",
            Test_Case_Name="Test Execute Failed"
        )
        
        result = test_case.execute_test()
        assert result == "FAILED"

    @patch('src.data_validation_test_case.random.choice')
    def test_execute_test_returns_skipped(self, mock_choice):
        """Test execute_test returning SKIPPED"""
        mock_choice.return_value = "SKIPPED"
        
        test_case = DataValidationTestCase(
            Test_Case_ID="DV_014",
            Test_Case_Name="Test Execute Skipped"
        )
        
        result = test_case.execute_test()
        assert result == "SKIPPED"

    def test_log_execution_status_passed(self):
        """Test logging execution status for passed test"""
        test_case = DataValidationTestCase(
            Test_Case_ID="DV_015",
            Test_Case_Name="Test Log Status"
        )
        
        with patch('builtins.print') as mock_print:
            test_case.log_execution_status(True)
        
        assert test_case.status == "PASSED"
        mock_print.assert_called_with("Test Case 'Test Log Status' Execution Status: PASSED")

    def test_log_execution_status_failed(self):
        """Test logging execution status for failed test"""
        test_case = DataValidationTestCase(
            Test_Case_ID="DV_016",
            Test_Case_Name="Test Log Status Failed"
        )
        
        with patch('builtins.print') as mock_print:
            test_case.log_execution_status(False)
        
        assert test_case.status == "FAILED"
        mock_print.assert_called_with("Test Case 'Test Log Status Failed' Execution Status: FAILED")

    def test_repr_method(self):
        """Test string representation of DataValidationTestCase"""
        test_case = DataValidationTestCase(
            Test_Case_ID="DV_017",
            Priority="High",
            Tags="data_validation,critical"
        )
        
        repr_str = repr(test_case)
        
        assert "DataValidationTestCase" in repr_str
        assert "ID='DV_017'" in repr_str
        assert "Priority='High'" in repr_str
        assert "Tags=['data_validation', 'critical']" in repr_str

    @pytest.mark.edge
    def test_initialization_with_numeric_values(self):
        """Test initialization with numeric values as strings"""
        test_data = {
            "Test_Case_ID": 123,  # Numeric ID
            "Priority": 1,        # Numeric priority
            "Tags": 456.789       # Numeric tags
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        assert test_case.test_case_id == 123
        assert test_case.priority == 1
        # Numeric values should be converted to string for parsing
        assert test_case.tags == ["456.789"]

    @pytest.mark.edge
    def test_parse_tags_with_single_tag(self):
        """Test parsing tags with single tag (no commas)"""
        test_data = {
            "Test_Case_ID": "DV_018",
            "Tags": "data_validation"
        }
        
        test_case = DataValidationTestCase(**test_data)
        
        assert test_case.tags == ["data_validation"]

    @pytest.mark.edge
    def test_parse_parameters_with_empty_values(self):
        """Test parsing parameters with empty values"""
        test_data = {
            "Test_Case_ID": "DV_019",
            "Parameters": "key1=value1,key2=,key3=value3,key4="
        }
        
        test_case = DataValidationTestCase(**test_data)
        
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
            "Test_Case_ID": ["DV_001", "DV_002", "DV_003"],
            "Test_Case_Name": ["Validation Test", "Auth Test", "Data Test"],
            "Application_Name": ["APP1", "APP2", "APP1"],
            "Environment_Name": ["DEV", "QA", "PROD"],
            "Priority": ["High", "Medium", "Low"],
            "Tags": ["data_validation,database", pd.NA, "data_validation,critical"],
            "Parameters": ["timeout=30,retry=3", "host=localhost", pd.NA]
        }
        
        df = pd.DataFrame(df_data)
        enabled_tests = df[df["Enable"] == True]
        
        test_objects = []
        for _, row in enabled_tests.iterrows():
            test_case = DataValidationTestCase(**row.to_dict())
            test_objects.append(test_case)
        
        # Verify we got the right number of enabled tests
        assert len(test_objects) == 2
        
        # Verify first test case
        assert test_objects[0].test_case_id == "DV_001"
        assert test_objects[0].tags == ["data_validation", "database"]
        assert test_objects[0].parameters == {"timeout": "30", "retry": "3"}
        
        # Verify second test case
        assert test_objects[1].test_case_id == "DV_003"
        assert test_objects[1].tags == ["data_validation", "critical"]
        assert test_objects[1].parameters == {}

    @pytest.mark.negative
    def test_parse_parameters_exception_handling(self):
        """Test that parse_parameters handles exceptions gracefully"""
        test_data = {
            "Test_Case_ID": "DV_020",
            "Parameters": "key1=value1,key2"  # Missing value causes ValueError in split
        }
        
        # Should not raise exception, just skip invalid parameters
        test_case = DataValidationTestCase(**test_data)
        
        # Should only include valid parameters
        assert test_case.parameters == {"key1": "value1"}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])