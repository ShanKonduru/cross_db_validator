"""
Enhanced Test Execution Data Collector
Captures comprehensive test execution data for multi-level trend analysis.
Integrates with Excel test suite structure and execution results.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
import pandas as pd


class TestExecutionDataCollector:
    """
    Collects and structures test execution data from multiple sources:
    1. Excel test suite structure (categories, priorities, etc.)
    2. Execution results (status, timing, errors)
    3. Performance metrics (execution time per test case)
    
    Creates comprehensive data for persistent storage and trend analysis.
    """
    
    def __init__(self, excel_file: str = "inputs/test_suite.xlsx"):
        self.excel_file = excel_file
        self.test_metadata = {}
        self.sheet_structure = {}
        self._load_test_metadata()
    
    def _load_test_metadata(self):
        """Load test metadata from Excel file for enriching execution data."""
        try:
            # Load all sheets except CONTROLLER and INSTRUCTIONS
            xl = pd.ExcelFile(self.excel_file)
            test_sheets = [sheet for sheet in xl.sheet_names 
                          if sheet not in ['CONTROLLER', 'INSTRUCTIONS', 'REFERENCE']]
            
            for sheet_name in test_sheets:
                df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
                
                # Store sheet structure
                self.sheet_structure[sheet_name] = {
                    'total_defined_tests': len(df),
                    'enabled_tests': len(df[df.get('Enable', True) == True]),
                    'columns': list(df.columns)
                }
                
                # Store individual test metadata
                for _, row in df.iterrows():
                    if pd.isna(row.get('Test_Case_ID')):
                        continue
                        
                    test_id = str(row['Test_Case_ID'])
                    self.test_metadata[test_id] = {
                        'sheet_name': sheet_name,
                        'test_case_name': str(row.get('Test_Case_Name', '')),
                        'test_category': str(row.get('Test_Category', 'OTHER')),
                        'priority': str(row.get('Priority', 'MEDIUM')),
                        'application_name': str(row.get('Application_Name', '')),
                        'environment_name': str(row.get('Environment_Name', '')),
                        'expected_result': str(row.get('Expected_Result', '')),
                        'description': str(row.get('Description', '')),
                        'tags': str(row.get('Tags', '')).split(',') if pd.notna(row.get('Tags')) else [],
                        'enabled': bool(row.get('Enable', True))
                    }
            
            print(f"📊 Loaded metadata for {len(self.test_metadata)} test cases from {len(test_sheets)} sheets")
            
        except Exception as e:
            print(f"⚠️ Error loading test metadata: {e}")
            self.test_metadata = {}
            self.sheet_structure = {}
    
    def create_execution_record(self, execution_results: Dict, execution_start_time: datetime.datetime = None) -> Dict:
        """
        Create a comprehensive execution record from test results.
        
        Args:
            execution_results: Raw execution results (from test runner)
            execution_start_time: When the execution started
            
        Returns:
            Comprehensive execution record for persistent storage
        """
        if execution_start_time is None:
            execution_start_time = datetime.datetime.now()
        
        execution_id = execution_start_time.strftime('%Y%m%d_%H%M%S')
        
        # Initialize the execution record structure
        execution_record = {
            "execution_metadata": {
                "execution_id": execution_id,
                "execution_time": execution_start_time.isoformat(),
                "duration_seconds": execution_results.get('total_duration', 0),
                "environment": "default",  # Can be enhanced later
                "application": "cross_db_validator",
                "excel_file": self.excel_file,
                "data_collection_version": "1.0"
            },
            
            "overall_summary": self._calculate_overall_summary(execution_results),
            "sheet_level_results": self._organize_by_sheets(execution_results),
            "category_level_results": self._organize_by_categories(execution_results),
            "test_case_details": self._collect_test_case_details(execution_results),
            "performance_metrics": self._collect_performance_metrics(execution_results)
        }
        
        return execution_record
    
    def _calculate_overall_summary(self, execution_results: Dict) -> Dict:
        """Calculate overall execution summary statistics."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        
        # Count from all test results
        for sheet_data in execution_results.get('sheet_results', {}).values():
            for test_result in sheet_data.get('test_cases', []):
                total_tests += 1
                status = test_result.get('status', '').upper()
                if status == 'PASSED':
                    passed_tests += 1
                elif status == 'FAILED':
                    failed_tests += 1
                elif status == 'SKIPPED':
                    skipped_tests += 1
        
        # Calculate rates
        passed_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        failed_rate = (failed_tests / total_tests * 100) if total_tests > 0 else 0
        skipped_rate = (skipped_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "passed_rate": round(passed_rate, 2),
            "failed_rate": round(failed_rate, 2),
            "skipped_rate": round(skipped_rate, 2)
        }
    
    def _organize_by_sheets(self, execution_results: Dict) -> Dict:
        """Organize execution results by Excel sheets."""
        sheet_results = {}
        
        for sheet_name, sheet_data in execution_results.get('sheet_results', {}).items():
            test_cases = sheet_data.get('test_cases', [])
            
            # Calculate sheet-level summary
            total = len(test_cases)
            passed = sum(1 for tc in test_cases if tc.get('status', '').upper() == 'PASSED')
            failed = sum(1 for tc in test_cases if tc.get('status', '').upper() == 'FAILED')
            skipped = sum(1 for tc in test_cases if tc.get('status', '').upper() == 'SKIPPED')
            
            passed_rate = (passed / total * 100) if total > 0 else 0
            failed_rate = (failed / total * 100) if total > 0 else 0
            skipped_rate = (skipped / total * 100) if total > 0 else 0
            
            # Enrich test cases with metadata
            enriched_test_cases = []
            for test_case in test_cases:
                test_id = test_case.get('test_id')
                metadata = self.test_metadata.get(test_id, {})
                
                enriched_case = {
                    "test_case_id": test_id,
                    "test_case_name": metadata.get('test_case_name', test_case.get('test_name', '')),
                    "test_category": metadata.get('test_category', 'OTHER'),
                    "priority": metadata.get('priority', 'MEDIUM'),
                    "status": test_case.get('status', '').upper(),
                    "execution_time_ms": test_case.get('execution_time_ms', 0),
                    "tags": metadata.get('tags', []),
                    "error_message": None  # As requested - no error details for trends
                }
                enriched_test_cases.append(enriched_case)
            
            sheet_results[sheet_name] = {
                "summary": {
                    "total_tests": total,
                    "passed_tests": passed,
                    "failed_tests": failed,
                    "skipped_tests": skipped,
                    "passed_rate": round(passed_rate, 2),
                    "failed_rate": round(failed_rate, 2),
                    "skipped_rate": round(skipped_rate, 2)
                },
                "test_cases": enriched_test_cases
            }
        
        return sheet_results
    
    def _organize_by_categories(self, execution_results: Dict) -> Dict:
        """Organize execution results by test categories from Excel."""
        category_results = {}
        
        # Collect all test cases and group by category
        for sheet_data in execution_results.get('sheet_results', {}).values():
            for test_case in sheet_data.get('test_cases', []):
                test_id = test_case.get('test_id')
                metadata = self.test_metadata.get(test_id, {})
                category = metadata.get('test_category', 'OTHER')
                
                if category not in category_results:
                    category_results[category] = {
                        'total_tests': 0,
                        'passed_tests': 0,
                        'failed_tests': 0,
                        'skipped_tests': 0
                    }
                
                category_results[category]['total_tests'] += 1
                status = test_case.get('status', '').upper()
                if status == 'PASSED':
                    category_results[category]['passed_tests'] += 1
                elif status == 'FAILED':
                    category_results[category]['failed_tests'] += 1
                elif status == 'SKIPPED':
                    category_results[category]['skipped_tests'] += 1
        
        # Calculate rates for each category
        for category, data in category_results.items():
            total = data['total_tests']
            if total > 0:
                data['passed_rate'] = round(data['passed_tests'] / total * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / total * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / total * 100, 2)
            else:
                data['passed_rate'] = data['failed_rate'] = data['skipped_rate'] = 0.0
        
        return category_results
    
    def _collect_test_case_details(self, execution_results: Dict) -> Dict:
        """Collect individual test case execution details for historical tracking."""
        test_case_details = {}
        
        for sheet_data in execution_results.get('sheet_results', {}).values():
            for test_case in sheet_data.get('test_cases', []):
                test_id = test_case.get('test_id')
                
                test_case_details[test_id] = {
                    "last_status": test_case.get('status', '').upper(),
                    "execution_time_ms": test_case.get('execution_time_ms', 0),
                    "sheet_name": test_case.get('sheet_name', ''),
                    "test_category": self.test_metadata.get(test_id, {}).get('test_category', 'OTHER'),
                    "priority": self.test_metadata.get(test_id, {}).get('priority', 'MEDIUM')
                }
        
        return test_case_details
    
    def _collect_performance_metrics(self, execution_results: Dict) -> Dict:
        """Collect performance metrics for trend analysis."""
        performance_data = {
            "total_execution_time_ms": 0,
            "average_test_time_ms": 0,
            "slowest_tests": [],
            "fastest_tests": [],
            "sheet_performance": {},
            "category_performance": {}
        }
        
        all_test_times = []
        
        # Collect timing data
        for sheet_name, sheet_data in execution_results.get('sheet_results', {}).items():
            sheet_total_time = 0
            sheet_test_count = 0
            
            for test_case in sheet_data.get('test_cases', []):
                test_id = test_case.get('test_id')
                exec_time = test_case.get('execution_time_ms', 0)
                
                all_test_times.append({
                    'test_id': test_id,
                    'execution_time_ms': exec_time,
                    'sheet_name': sheet_name
                })
                
                sheet_total_time += exec_time
                sheet_test_count += 1
            
            # Sheet-level performance
            performance_data["sheet_performance"][sheet_name] = {
                "total_time_ms": sheet_total_time,
                "average_time_ms": round(sheet_total_time / sheet_test_count, 2) if sheet_test_count > 0 else 0,
                "test_count": sheet_test_count
            }
        
        # Overall performance metrics
        if all_test_times:
            performance_data["total_execution_time_ms"] = sum(t['execution_time_ms'] for t in all_test_times)
            performance_data["average_test_time_ms"] = round(
                performance_data["total_execution_time_ms"] / len(all_test_times), 2
            )
            
            # Sort by execution time
            sorted_times = sorted(all_test_times, key=lambda x: x['execution_time_ms'])
            performance_data["fastest_tests"] = sorted_times[:5]  # Top 5 fastest
            performance_data["slowest_tests"] = sorted_times[-5:]  # Top 5 slowest
        
        return performance_data
    
    def parse_execution_results_from_report(self, report_content: str, execution_time: datetime.datetime) -> Dict:
        """
        Parse execution results from a markdown report for backward compatibility.
        This allows importing existing reports into the new persistent format.
        """
        # This would be used to migrate existing reports to the new format
        # Implementation depends on your current report format
        pass