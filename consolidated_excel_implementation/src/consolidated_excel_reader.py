#!/usr/bin/env python3
"""
Consolidated Excel Test Case Reader

This module reads the new consolidated Excel format where all test types 
(SMOKE, DATA_VALIDATION, CROSS_DB_VALIDATION) are in a single sheet with
a TEST_TYPE column to distinguish between test types.

Key differences from the original ExcelTestCaseReader:
1. No CONTROLLER sheet - reads directly from CONSOLIDATED_TESTS sheet
2. Uses TEST_TYPE column to filter tests by type
3. Support for new columns: SRC_Table_Name, TGT_Table_Name  
4. Enhanced parameter parsing for expected columns and tolerances
5. Enable column controls test execution (first column)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add the parent directory to the path to import from existing src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


class ConsolidatedExcelTestCaseReader:
    """
    Reads the new consolidated Excel format with all test types in one sheet.
    """

    def __init__(
        self,
        file_path: str = "inputs/consolidated_test_suite_20251007_213209.xlsx",
        consolidated_sheet_name: str = "CONSOLIDATED_TESTS",
        test_type_col: str = "TEST_TYPE",
        enable_col: str = "Enable",
        enable_value=True,
    ):
        """
        Initialize the consolidated Excel reader.

        Args:
            file_path (str): Path to the consolidated Excel workbook
            consolidated_sheet_name (str): Name of the sheet containing all tests
            test_type_col (str): Column name for test type
            enable_col (str): Column name for enable/disable status
            enable_value: Value that indicates test is enabled (True/FALSE/"TRUE")
        """
        self.file_path = file_path
        self.consolidated_sheet = consolidated_sheet_name
        self.test_type_col = test_type_col
        self.enable_col = enable_col
        self.enable_value = enable_value
        self.test_case_data = {}
        self.raw_data = None

    def _normalize_enable_value(self, value) -> bool:
        """
        Normalize various enable value formats to boolean.
        
        Args:
            value: The enable value (True, "TRUE", "true", False, "FALSE", etc.)
            
        Returns:
            bool: True if enabled, False otherwise
        """
        if pd.isna(value):
            return False
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.upper() == "TRUE"
        
        # Handle numeric values (1 = True, 0 = False)
        try:
            return bool(int(value))
        except (ValueError, TypeError):
            return False

    def _read_consolidated_sheet(self) -> pd.DataFrame:
        """
        Read the consolidated tests sheet.
        
        Returns:
            pd.DataFrame: DataFrame containing all test data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If required columns are missing
        """
        try:
            # Read the consolidated sheet
            df = pd.read_excel(self.file_path, sheet_name=self.consolidated_sheet)
            
            # Validate required columns
            required_columns = [self.enable_col, self.test_type_col, 'Test_Case_ID']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            print(f"✅ Successfully read {len(df)} test cases from {self.consolidated_sheet}")
            return df
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error reading consolidated sheet: {e}")

    def _filter_enabled_tests(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter for enabled tests only.
        
        Args:
            df (pd.DataFrame): Raw test data
            
        Returns:
            pd.DataFrame: Filtered DataFrame with only enabled tests
        """
        # Normalize enable values
        df['_normalized_enable'] = df[self.enable_col].apply(self._normalize_enable_value)
        
        # Filter for enabled tests
        enabled_df = df[df['_normalized_enable'] == True].copy()
        
        # Remove the temporary column
        enabled_df = enabled_df.drop('_normalized_enable', axis=1)
        
        print(f"🔍 Filtered to {len(enabled_df)} enabled test cases")
        return enabled_df

    def _group_by_test_type(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Group tests by TEST_TYPE.
        
        Args:
            df (pd.DataFrame): Filtered test data
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary with test types as keys
        """
        grouped_data = {}
        
        for test_type in df[self.test_type_col].unique():
            if pd.notna(test_type):
                type_df = df[df[self.test_type_col] == test_type].copy()
                grouped_data[test_type] = type_df
                print(f"   📋 {test_type}: {len(type_df)} test cases")
        
        return grouped_data

    def _parse_parameters(self, params_str: str) -> Dict[str, str]:
        """
        Parse the Parameters column into a dictionary.
        
        Args:
            params_str (str): Parameter string (e.g., "tolerance=5%,tolerance_type=percentage")
            
        Returns:
            Dict[str, str]: Parsed parameters
        """
        if pd.isna(params_str) or not params_str.strip():
            return {}
        
        params = {}
        try:
            # Split by comma and parse key=value pairs
            for param_pair in params_str.split(','):
                if '=' in param_pair:
                    key, value = param_pair.split('=', 1)
                    params[key.strip()] = value.strip()
                else:
                    # Handle standalone parameters
                    params[param_pair.strip()] = True
        except Exception as e:
            print(f"⚠️ Warning: Could not parse parameters '{params_str}': {e}")
        
        return params

    def _enhance_test_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Enhance test data with parsed parameters and additional fields.
        
        Args:
            df (pd.DataFrame): Test data
            
        Returns:
            pd.DataFrame: Enhanced test data
        """
        enhanced_df = df.copy()
        
        # Parse parameters into structured format
        enhanced_df['parsed_parameters'] = enhanced_df['Parameters'].apply(self._parse_parameters)
        
        # Add convenience fields for common parameters
        enhanced_df['has_tolerance'] = enhanced_df['parsed_parameters'].apply(
            lambda x: 'tolerance' in x or 'numeric_tolerance' in x
        )
        
        enhanced_df['tolerance_type'] = enhanced_df['parsed_parameters'].apply(
            lambda x: x.get('tolerance_type', 'exact')
        )
        
        enhanced_df['has_expected_cols'] = enhanced_df['parsed_parameters'].apply(
            lambda x: 'expect_cols' in x
        )
        
        return enhanced_df

    def get_test_case_details(self) -> Dict[str, pd.DataFrame]:
        """
        Main method to read and process the consolidated Excel file.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary with test types as keys and 
                                   DataFrames containing test cases as values
        """
        print(f"📖 Reading consolidated Excel file: {self.file_path}")
        
        # Step 1: Read the consolidated sheet
        self.raw_data = self._read_consolidated_sheet()
        
        # Step 2: Filter for enabled tests
        enabled_tests = self._filter_enabled_tests(self.raw_data)
        
        # Step 3: Enhance with parsed parameters
        enhanced_tests = self._enhance_test_data(enabled_tests)
        
        # Step 4: Group by test type
        self.test_case_data = self._group_by_test_type(enhanced_tests)
        
        print(f"\n📊 Summary:")
        print(f"   Total test cases read: {len(self.raw_data)}")
        print(f"   Enabled test cases: {len(enabled_tests)}")
        print(f"   Test types found: {list(self.test_case_data.keys())}")
        
        return self.test_case_data

    def get_tests_by_type(self, test_type: str) -> Optional[pd.DataFrame]:
        """
        Get tests of a specific type.
        
        Args:
            test_type (str): Type of test (SMOKE, DATA_VALIDATION, CROSS_DB_VALIDATION)
            
        Returns:
            Optional[pd.DataFrame]: DataFrame containing tests of the specified type
        """
        return self.test_case_data.get(test_type)

    def get_all_enabled_tests(self) -> pd.DataFrame:
        """
        Get all enabled tests regardless of type.
        
        Returns:
            pd.DataFrame: DataFrame containing all enabled tests
        """
        if not self.test_case_data:
            self.get_test_case_details()
        
        all_tests = []
        for test_type, df in self.test_case_data.items():
            all_tests.append(df)
        
        if all_tests:
            return pd.concat(all_tests, ignore_index=True)
        else:
            return pd.DataFrame()

    def get_test_statistics(self) -> Dict:
        """
        Get statistics about the test cases.
        
        Returns:
            Dict: Statistics including counts by type, category, priority, etc.
        """
        if not self.test_case_data:
            self.get_test_case_details()
        
        all_tests = self.get_all_enabled_tests()
        
        if all_tests.empty:
            return {}
        
        stats = {
            'total_tests': len(all_tests),
            'by_test_type': all_tests[self.test_type_col].value_counts().to_dict(),
            'by_category': all_tests['Test_Category'].value_counts().to_dict(),
            'by_priority': all_tests['Priority'].value_counts().to_dict(),
            'with_tolerance': len(all_tests[all_tests['has_tolerance'] == True]),
            'with_expected_cols': len(all_tests[all_tests['has_expected_cols'] == True]),
            'by_environment': {
                'source': all_tests['SRC_Environment_Name'].value_counts().to_dict(),
                'target': all_tests['TGT_Environment_Name'].value_counts().to_dict()
            }
        }
        
        return stats

    def export_test_summary(self, output_path: str = "output/test_summary.xlsx"):
        """
        Export a summary of tests to Excel.
        
        Args:
            output_path (str): Path for the output Excel file
        """
        if not self.test_case_data:
            self.get_test_case_details()
        
        all_tests = self.get_all_enabled_tests()
        
        if all_tests.empty:
            print("❌ No tests to export")
            return
        
        # Create summary data
        summary_cols = [
            self.enable_col, 'Test_Case_ID', 'Test_Case_Name', self.test_type_col,
            'Test_Category', 'Priority', 'Expected_Result', 'SRC_Table_Name', 
            'TGT_Table_Name', 'Parameters', 'has_tolerance', 'has_expected_cols'
        ]
        
        summary_df = all_tests[summary_cols].copy()
        
        # Export to Excel
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            summary_df.to_excel(writer, sheet_name='Test_Summary', index=False)
            
            # Add statistics sheet
            stats = self.get_test_statistics()
            stats_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        print(f"✅ Test summary exported to: {output_path}")


if __name__ == "__main__":
    # Example usage
    reader = ConsolidatedExcelTestCaseReader()
    test_data = reader.get_test_case_details()
    
    # Print statistics
    stats = reader.get_test_statistics()
    print(f"\n📈 Test Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Export summary
    reader.export_test_summary()