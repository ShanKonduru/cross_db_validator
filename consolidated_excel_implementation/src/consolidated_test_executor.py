#!/usr/bin/env python3
"""
Consolidated Excel Test Execution Main Script

This script reads the new consolidated Excel format and executes tests.
It references the existing codebase for test execution logic but uses
the new consolidated Excel reader.

Features:
1. Reads consolidated Excel format (no CONTROLLER sheet needed)
2. Supports all test types in single sheet with TEST_TYPE column
3. Enhanced parameter parsing for tolerance and expected columns
4. Maintains compatibility with existing test execution framework
5. Generates reports using existing report generators
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

# Add paths to import existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import existing modules
from src.data_validation_test_case import DataValidationTestCase
from src.cross_database_validation_test_case import CrossDatabaseValidationTestCase
from src.database_config_manager import DatabaseConfigManager
from src.enhanced_markdown_report_generator import EnhancedMarkdownReportGenerator
from src.html_report_generator import HTMLReportGenerator
from src.smoke_test_case import SmokeTestCase
from src.test_execution_data_collector import TestExecutionDataCollector
from src.execution_data_persistence import ExecutionDataPersistence

# Import new consolidated reader
from .consolidated_excel_reader import ConsolidatedExcelTestCaseReader


class ConsolidatedTestExecutor:
    """
    Executes tests from the consolidated Excel format.
    """
    
    def __init__(self, excel_file_path: str = None):
        """
        Initialize the test executor.
        
        Args:
            excel_file_path (str): Path to consolidated Excel file
        """
        self.excel_file_path = excel_file_path or "inputs/consolidated_test_suite_20251007_213209.xlsx"
        self.reader = ConsolidatedExcelTestCaseReader(self.excel_file_path)
        self.db_config_manager = DatabaseConfigManager()
        self.test_results = []
        self.execution_start_time = None
        self.execution_end_time = None
        
    def _create_smoke_test_case(self, test_row) -> SmokeTestCase:
        """
        Create a SmokeTestCase from consolidated Excel row.
        
        Args:
            test_row: Pandas Series containing test data
            
        Returns:
            SmokeTestCase: Configured smoke test case
        """
        # Parse parameters
        params = test_row.get('parsed_parameters', {})
        
        # Create smoke test case
        smoke_test = SmokeTestCase(
            test_case_id=test_row['Test_Case_ID'],
            test_case_name=test_row['Test_Case_Name'],
            test_category=test_row['Test_Category'],
            src_application_name=test_row['SRC_Application_Name'],
            src_environment_name=test_row['SRC_Environment_Name'],
            priority=test_row.get('Priority', 'Medium'),
            expected_result=test_row.get('Expected_Result', 'PASS'),
            description=test_row.get('Description', ''),
            prerequisites=test_row.get('Prerequisites', ''),
            tags=test_row.get('Tags', ''),
            expected_duration_mins=test_row.get('Expected_Duration_mins', 5),
            db_config_manager=self.db_config_manager
        )
        
        # Add table name if specified
        if pd.notna(test_row.get('SRC_Table_Name')):
            smoke_test.table_name = test_row['SRC_Table_Name']
            
        # Add connection timeout if specified
        if 'connection_timeout' in params:
            try:
                smoke_test.connection_timeout = int(params['connection_timeout'])
            except ValueError:
                pass
                
        return smoke_test
    
    def _create_data_validation_test_case(self, test_row) -> DataValidationTestCase:
        """
        Create a DataValidationTestCase from consolidated Excel row.
        
        Args:
            test_row: Pandas Series containing test data
            
        Returns:
            DataValidationTestCase: Configured data validation test case
        """
        # Parse parameters
        params = test_row.get('parsed_parameters', {})
        
        # Create data validation test case
        data_test = DataValidationTestCase(
            test_case_id=test_row['Test_Case_ID'],
            test_case_name=test_row['Test_Case_Name'],
            test_category=test_row['Test_Category'],
            src_application_name=test_row['SRC_Application_Name'],
            src_environment_name=test_row['SRC_Environment_Name'],
            tgt_application_name=test_row['TGT_Application_Name'],
            tgt_environment_name=test_row['TGT_Environment_Name'],
            priority=test_row.get('Priority', 'Medium'),
            expected_result=test_row.get('Expected_Result', 'PASS'),
            description=test_row.get('Description', ''),
            prerequisites=test_row.get('Prerequisites', ''),
            tags=test_row.get('Tags', ''),
            expected_duration_mins=test_row.get('Expected_Duration_mins', 5),
            db_config_manager=self.db_config_manager
        )
        
        # Add table names
        if pd.notna(test_row.get('SRC_Table_Name')):
            data_test.source_table = test_row['SRC_Table_Name']
        if pd.notna(test_row.get('TGT_Table_Name')):
            data_test.target_table = test_row['TGT_Table_Name']
            
        # Add tolerance parameters
        if 'tolerance' in params:
            data_test.tolerance = params['tolerance']
        if 'tolerance_type' in params:
            data_test.tolerance_type = params['tolerance_type']
            
        # Add schema validation parameters
        if 'validate_columns' in params:
            data_test.validate_columns = params['validate_columns'].split('|')
        if 'validate_datatypes' in params:
            data_test.validate_datatypes = params['validate_datatypes'].lower() == 'true'
            
        return data_test
    
    def _create_cross_db_validation_test_case(self, test_row) -> CrossDatabaseValidationTestCase:
        """
        Create a CrossDatabaseValidationTestCase from consolidated Excel row.
        
        Args:
            test_row: Pandas Series containing test data
            
        Returns:
            CrossDatabaseValidationTestCase: Configured cross-database validation test case
        """
        # Parse parameters
        params = test_row.get('parsed_parameters', {})
        
        # Create cross-database validation test case
        cross_test = CrossDatabaseValidationTestCase(
            test_case_id=test_row['Test_Case_ID'],
            test_case_name=test_row['Test_Case_Name'],
            test_category=test_row['Test_Category'],
            src_application_name=test_row['SRC_Application_Name'],
            src_environment_name=test_row['SRC_Environment_Name'],
            tgt_application_name=test_row['TGT_Application_Name'],
            tgt_environment_name=test_row['TGT_Environment_Name'],
            priority=test_row.get('Priority', 'Medium'),
            expected_result=test_row.get('Expected_Result', 'PASS'),
            description=test_row.get('Description', ''),
            prerequisites=test_row.get('Prerequisites', ''),
            tags=test_row.get('Tags', ''),
            expected_duration_mins=test_row.get('Expected_Duration_mins', 5),
            db_config_manager=self.db_config_manager
        )
        
        # Add table names
        if pd.notna(test_row.get('SRC_Table_Name')):
            cross_test.source_table = test_row['SRC_Table_Name']
        if pd.notna(test_row.get('TGT_Table_Name')):
            cross_test.target_table = test_row['TGT_Table_Name']
            
        # Add column comparison parameters
        if 'compare_columns' in params:
            cross_test.compare_columns = params['compare_columns'].split('|')
        if 'key_column' in params:
            cross_test.key_column = params['key_column']
            
        # Add expected columns (NEW FEATURE)
        if 'expect_cols' in params:
            cross_test.expected_different_columns = params['expect_cols'].split('|')
            
        # Add tolerance parameters
        if 'tolerance' in params:
            cross_test.tolerance = params['tolerance']
        if 'tolerance_type' in params:
            cross_test.tolerance_type = params['tolerance_type']
        if 'numeric_tolerance' in params:
            try:
                cross_test.numeric_tolerance = float(params['numeric_tolerance'])
            except ValueError:
                pass
                
        # Add advanced parameters
        if 'case_sensitive' in params:
            cross_test.case_sensitive = params['case_sensitive'].lower() == 'true'
        if 'allow_nulls' in params:
            cross_test.allow_nulls = params['allow_nulls'].lower() == 'true'
        if 'trim_spaces' in params:
            cross_test.trim_spaces = params['trim_spaces'].lower() == 'true'
        if 'decimal_precision' in params:
            try:
                cross_test.decimal_precision = int(params['decimal_precision'])
            except ValueError:
                pass
                
        return cross_test
    
    def execute_tests(self, test_types: List[str] = None) -> List:
        """
        Execute tests from the consolidated Excel file.
        
        Args:
            test_types (List[str]): List of test types to execute. If None, execute all.
            
        Returns:
            List: List of test execution results
        """
        print("🚀 Starting Consolidated Excel Test Execution")
        self.execution_start_time = datetime.now()
        
        # Read test cases
        test_data = self.reader.get_test_case_details()
        
        if not test_data:
            print("❌ No test cases found")
            return []
        
        # Filter test types if specified
        if test_types:
            test_data = {k: v for k, v in test_data.items() if k in test_types}
        
        # Execute tests by type
        for test_type, test_df in test_data.items():
            print(f"\n📋 Executing {test_type} tests ({len(test_df)} cases)")
            
            for _, test_row in test_df.iterrows():
                try:
                    # Create appropriate test case object
                    if test_type == 'SMOKE':
                        test_case = self._create_smoke_test_case(test_row)
                    elif test_type == 'DATA_VALIDATION':
                        test_case = self._create_data_validation_test_case(test_row)
                    elif test_type == 'CROSS_DB_VALIDATION':
                        test_case = self._create_cross_db_validation_test_case(test_row)
                    else:
                        print(f"⚠️ Unknown test type: {test_type}")
                        continue
                    
                    # Execute the test
                    print(f"   🔄 Executing: {test_row['Test_Case_ID']}")
                    result = test_case.execute()
                    self.test_results.append(result)
                    
                    # Print result
                    status_emoji = "✅" if result.status == "PASS" else "❌"
                    print(f"   {status_emoji} {result.test_case_id}: {result.status}")
                    
                except Exception as e:
                    print(f"   💥 Error executing {test_row['Test_Case_ID']}: {e}")
                    # Create failure result
                    error_result = type('TestResult', (), {
                        'test_case_id': test_row['Test_Case_ID'],
                        'test_case_name': test_row['Test_Case_Name'],
                        'status': 'ERROR',
                        'error_message': str(e),
                        'execution_time': 0,
                        'start_time': datetime.now(),
                        'end_time': datetime.now()
                    })()
                    self.test_results.append(error_result)
        
        self.execution_end_time = datetime.now()
        
        # Print summary
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status in ["FAIL", "ERROR"]])
        
        print(f"\n📊 Execution Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "   📈 Success Rate: 0%")
        
        return self.test_results
    
    def generate_report(self, report_format: str = 'enhanced-md'):
        """
        Generate test execution report.
        
        Args:
            report_format (str): Format for the report ('enhanced-md', 'html', 'md')
        """
        if not self.test_results:
            print("❌ No test results to generate report")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if report_format == 'enhanced-md':
            report_generator = EnhancedMarkdownReportGenerator(
                f"consolidated_excel_implementation/output/Consolidated_Test_Execution_Results_{timestamp}.md"
            )
        elif report_format == 'html':
            report_generator = HTMLReportGenerator(
                f"consolidated_excel_implementation/output/Consolidated_Test_Execution_Results_{timestamp}.html"
            )
        else:
            # Default to enhanced markdown
            report_generator = EnhancedMarkdownReportGenerator(
                f"consolidated_excel_implementation/output/Consolidated_Test_Execution_Results_{timestamp}.md"
            )
        
        # Generate report
        report_generator.generate_report(self.test_results)
        print(f"✅ Report generated successfully")


def main():
    """Main execution function."""
    print("🎯 Consolidated Excel Test Execution Framework")
    print("=" * 50)
    
    # Get Excel file path
    excel_file = input("Enter Excel file path (or press Enter for default): ").strip()
    if not excel_file:
        excel_file = "inputs/consolidated_test_suite_20251007_213209.xlsx"
    
    # Get test types to execute
    print("\n📋 Available Test Types:")
    print("1. SMOKE")
    print("2. DATA_VALIDATION") 
    print("3. CROSS_DB_VALIDATION")
    print("4. ALL (default)")
    
    choice = input("\nEnter choice (1-4) or test type names (comma-separated): ").strip()
    
    test_types = None
    if choice == '1':
        test_types = ['SMOKE']
    elif choice == '2':
        test_types = ['DATA_VALIDATION']
    elif choice == '3':
        test_types = ['CROSS_DB_VALIDATION']
    elif choice and choice != '4':
        # Parse comma-separated test types
        test_types = [t.strip().upper() for t in choice.split(',')]
    
    # Get report format
    print("\n🎨 Report Format:")
    print("1. Enhanced Markdown (default)")
    print("2. HTML")
    print("3. Standard Markdown")
    
    report_choice = input("Enter choice (1-3): ").strip()
    
    report_format = 'enhanced-md'
    if report_choice == '2':
        report_format = 'html'
    elif report_choice == '3':
        report_format = 'md'
    
    # Execute tests
    try:
        executor = ConsolidatedTestExecutor(excel_file)
        
        # Show test statistics
        stats = executor.reader.get_test_statistics()
        print(f"\n📈 Test File Statistics:")
        print(f"   Total tests: {stats.get('total_tests', 0)}")
        print(f"   Test types: {list(stats.get('by_test_type', {}).keys())}")
        print(f"   With tolerance: {stats.get('with_tolerance', 0)}")
        print(f"   With expected columns: {stats.get('with_expected_cols', 0)}")
        
        # Execute tests
        results = executor.execute_tests(test_types)
        
        # Generate report
        executor.generate_report(report_format)
        
    except Exception as e:
        print(f"💥 Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()