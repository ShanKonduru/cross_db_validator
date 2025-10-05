"""
Unit tests for ExcelTestCaseReader
"""
import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.excel_test_case_reader import ExcelTestCaseReader


@pytest.mark.unit
class TestExcelTestCaseReader:
    """Test class for ExcelTestCaseReader"""

    def test_initialization_with_defaults(self):
        """Test proper initialization with default parameters"""
        reader = ExcelTestCaseReader()
        
        assert reader.file_path == "inputs\\test_suite.xlsx"
        assert reader.controller_sheet == "CONTROLLER"
        assert reader.sheet_name_col == "SHEET_NAME"
        assert reader.enable_col == "ENABLE"
        assert reader.enable_value == "TRUE"
        assert reader.enabled_sheets == []
        assert reader.test_case_data == {}

    def test_initialization_with_custom_parameters(self):
        """Test initialization with custom parameters"""
        reader = ExcelTestCaseReader(
            file_path="custom/path.xlsx",
            controller_sheet_name="CONTROL",
            sheet_name_col="NAME",
            enable_col="ACTIVE",
            enable_value="YES"
        )
        
        assert reader.file_path == "custom/path.xlsx"
        assert reader.controller_sheet == "CONTROL"
        assert reader.sheet_name_col == "NAME"
        assert reader.enable_col == "ACTIVE"
        assert reader.enable_value == "YES"

    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_enabled_sheets_success(self, mock_read_excel):
        """Test successful retrieval of enabled sheets"""
        # Mock controller sheet data
        controller_data = pd.DataFrame({
            'SHEET_NAME': ['Sheet1', 'Sheet2', 'Sheet3', 'Sheet4'],
            'ENABLE': ['TRUE', 'FALSE', 'true', 'True']
        })
        mock_read_excel.return_value = controller_data
        
        reader = ExcelTestCaseReader()
        reader._get_enabled_sheets()
        
        assert reader.enabled_sheets == ['Sheet1', 'Sheet3', 'Sheet4']
        mock_read_excel.assert_called_once_with(
            "inputs\\test_suite.xlsx",
            sheet_name="CONTROLLER",
            usecols=['SHEET_NAME', 'ENABLE']
        )

    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_enabled_sheets_with_nan_values(self, mock_read_excel):
        """Test get_enabled_sheets with NaN values in data"""
        # Mock controller sheet data with NaN values
        controller_data = pd.DataFrame({
            'SHEET_NAME': ['Sheet1', 'Sheet2', pd.NA, 'Sheet4'],
            'ENABLE': ['TRUE', 'FALSE', 'TRUE', pd.NA]
        })
        mock_read_excel.return_value = controller_data
        
        reader = ExcelTestCaseReader()
        reader._get_enabled_sheets()
        
        # Should only include valid sheets with TRUE enable status
        assert reader.enabled_sheets == ['Sheet1']

    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_enabled_sheets_file_not_found(self, mock_read_excel):
        """Test get_enabled_sheets when file is not found"""
        mock_read_excel.side_effect = FileNotFoundError("File not found")
        
        reader = ExcelTestCaseReader()
        
        with pytest.raises(FileNotFoundError, match="File not found at: inputs\\\\test_suite.xlsx"):
            reader._get_enabled_sheets()

    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_enabled_sheets_missing_column(self, mock_read_excel):
        """Test get_enabled_sheets when required column is missing"""
        controller_data = pd.DataFrame({
            'SHEET_NAME': ['Sheet1', 'Sheet2'],
            'WRONG_COLUMN': ['TRUE', 'FALSE']
        })
        mock_read_excel.return_value = controller_data
        
        reader = ExcelTestCaseReader()
        
        with pytest.raises(KeyError, match="Missing expected column in 'CONTROLLER' sheet"):
            reader._get_enabled_sheets()

    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_enabled_sheets_general_exception(self, mock_read_excel):
        """Test get_enabled_sheets with general exception"""
        mock_read_excel.side_effect = Exception("General error")
        
        reader = ExcelTestCaseReader()
        
        # Should not raise, but set enabled_sheets to empty list
        with patch('builtins.print') as mock_print:
            reader._get_enabled_sheets()
            
        assert reader.enabled_sheets == []
        mock_print.assert_called_with("⚠️ Error reading controller sheet: General error")

    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_test_case_details_success(self, mock_read_excel):
        """Test successful test case details retrieval"""
        # Mock controller sheet
        controller_data = pd.DataFrame({
            'SHEET_NAME': ['Sheet1', 'Sheet2'],
            'ENABLE': ['TRUE', 'TRUE']
        })
        
        # Mock test case sheets
        sheet1_data = pd.DataFrame({
            'Test_Case_ID': ['TC001', 'TC002'],
            'Test_Case_Name': ['Test 1', 'Test 2'],
            'Enable': [True, True]
        })
        
        sheet2_data = pd.DataFrame({
            'Test_Case_ID': ['TC003'],
            'Test_Case_Name': ['Test 3'],
            'Enable': [True]
        })
        
        # Configure mock to return different data based on sheet_name
        def mock_read_excel_side_effect(file_path, sheet_name=None, usecols=None):
            if sheet_name == "CONTROLLER":
                return controller_data
            elif sheet_name == "Sheet1":
                return sheet1_data
            elif sheet_name == "Sheet2":
                return sheet2_data
            else:
                raise ValueError(f"Unknown sheet: {sheet_name}")
        
        mock_read_excel.side_effect = mock_read_excel_side_effect
        
        reader = ExcelTestCaseReader()
        result = reader.get_test_case_details()
        
        assert 'Sheet1' in result
        assert 'Sheet2' in result
        assert len(result['Sheet1']) == 2
        assert len(result['Sheet2']) == 1
        assert result['Sheet1']['Test_Case_ID'].tolist() == ['TC001', 'TC002']

    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_test_case_details_no_enabled_sheets(self, mock_read_excel):
        """Test get_test_case_details when no sheets are enabled"""
        controller_data = pd.DataFrame({
            'SHEET_NAME': ['Sheet1', 'Sheet2'],
            'ENABLE': ['FALSE', 'FALSE']
        })
        mock_read_excel.return_value = controller_data
        
        reader = ExcelTestCaseReader()
        
        with patch('builtins.print') as mock_print:
            result = reader.get_test_case_details()
            
        assert result == {}
        mock_print.assert_any_call("🛑 No sheets were found to be enabled or an error occurred.")

    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_test_case_details_sheet_read_failure(self, mock_read_excel):
        """Test get_test_case_details when reading a test sheet fails"""
        controller_data = pd.DataFrame({
            'SHEET_NAME': ['Sheet1'],
            'ENABLE': ['TRUE']
        })
        
        def mock_read_excel_side_effect(file_path, sheet_name=None, usecols=None):
            if sheet_name == "CONTROLLER":
                return controller_data
            elif sheet_name == "Sheet1":
                raise Exception("Sheet read error")
            else:
                raise ValueError(f"Unknown sheet: {sheet_name}")
        
        mock_read_excel.side_effect = mock_read_excel_side_effect
        
        reader = ExcelTestCaseReader()
        
        with patch('builtins.print') as mock_print:
            result = reader.get_test_case_details()
            
        assert result['Sheet1'] is None
        mock_print.assert_any_call("   - ❌ Failed to read data from sheet 'Sheet1': Sheet read error")

    @pytest.mark.edge
    def test_initialization_with_empty_strings(self):
        """Test initialization with empty string parameters"""
        reader = ExcelTestCaseReader(
            file_path="",
            controller_sheet_name="",
            sheet_name_col="",
            enable_col="",
            enable_value=""
        )
        
        assert reader.file_path == ""
        assert reader.controller_sheet == ""
        assert reader.sheet_name_col == ""
        assert reader.enable_col == ""
        assert reader.enable_value == ""

    @pytest.mark.edge
    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_get_enabled_sheets_case_insensitive_enable_value(self, mock_read_excel):
        """Test that enable value comparison is case insensitive"""
        controller_data = pd.DataFrame({
            'SHEET_NAME': ['Sheet1', 'Sheet2', 'Sheet3', 'Sheet4', 'Sheet5'],
            'ENABLE': ['TRUE', 'true', 'True', 'TrUe', 'false']
        })
        mock_read_excel.return_value = controller_data
        
        reader = ExcelTestCaseReader()
        reader._get_enabled_sheets()
        
        # All variations of 'true' should be considered enabled
        assert reader.enabled_sheets == ['Sheet1', 'Sheet2', 'Sheet3', 'Sheet4']

    @pytest.mark.integration
    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_full_workflow_integration(self, mock_read_excel):
        """Test complete workflow from initialization to data retrieval"""
        # Setup comprehensive test data
        controller_data = pd.DataFrame({
            'SHEET_NAME': ['SMOKE', 'DATAVALIDATIONS', 'DISABLED_SHEET'],
            'ENABLE': ['TRUE', 'TRUE', 'FALSE']
        })
        
        smoke_data = pd.DataFrame({
            'Test_Case_ID': ['SMOKE_001', 'SMOKE_002'],
            'Test_Case_Name': ['Smoke Test 1', 'Smoke Test 2'],
            'Enable': [True, False],
            'Application_Name': ['APP1', 'APP2'],
            'Environment_Name': ['DEV', 'QA']
        })
        
        validation_data = pd.DataFrame({
            'Test_Case_ID': ['VAL_001'],
            'Test_Case_Name': ['Validation Test 1'],
            'Enable': [True],
            'Application_Name': ['APP1'],
            'Environment_Name': ['PROD']
        })
        
        def mock_read_excel_side_effect(file_path, sheet_name=None, usecols=None):
            if sheet_name == "CONTROLLER":
                return controller_data
            elif sheet_name == "SMOKE":
                return smoke_data
            elif sheet_name == "DATAVALIDATIONS":
                return validation_data
            else:
                raise ValueError(f"Sheet not found: {sheet_name}")
        
        mock_read_excel.side_effect = mock_read_excel_side_effect
        
        reader = ExcelTestCaseReader()
        result = reader.get_test_case_details()
        
        # Verify complete workflow
        assert len(result) == 2  # Only enabled sheets
        assert 'SMOKE' in result
        assert 'DATAVALIDATIONS' in result
        assert 'DISABLED_SHEET' not in result
        
        assert len(result['SMOKE']) == 2
        assert len(result['DATAVALIDATIONS']) == 1
        
        # Verify data integrity
        assert result['SMOKE']['Test_Case_ID'].iloc[0] == 'SMOKE_001'
        assert result['DATAVALIDATIONS']['Test_Case_ID'].iloc[0] == 'VAL_001'

    @pytest.mark.performance
    @patch('src.excel_test_case_reader.pd.read_excel')
    def test_large_dataset_handling(self, mock_read_excel):
        """Test handling of large datasets"""
        # Create large controller data
        large_sheet_names = [f'Sheet_{i:03d}' for i in range(100)]
        large_enable_values = ['TRUE'] * 50 + ['FALSE'] * 50
        
        controller_data = pd.DataFrame({
            'SHEET_NAME': large_sheet_names,
            'ENABLE': large_enable_values
        })
        mock_read_excel.return_value = controller_data
        
        reader = ExcelTestCaseReader()
        reader._get_enabled_sheets()
        
        # Should efficiently handle large datasets
        assert len(reader.enabled_sheets) == 50
        assert all(sheet.startswith('Sheet_') for sheet in reader.enabled_sheets)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])