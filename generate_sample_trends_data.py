"""
Sample Data Generator for Persistent Trends Analysis
Generates realistic historical test execution data spanning days, weeks, and months
to demonstrate comprehensive trends analysis capabilities.
"""

import json
import datetime
import random
from typing import Dict, List
import os


class SampleTrendsDataGenerator:
    """
    Generates sample historical execution data for trends analysis demonstration.
    Creates realistic patterns including:
    - Daily variations in test performance
    - Weekly patterns (weekends vs weekdays)
    - Monthly trends and seasonal variations
    - Different performance patterns for different test categories
    """
    
    def __init__(self):
        self.test_categories = [
            'SETUP', 'CONFIGURATION', 'SECURITY', 'CONNECTION', 
            'QUERIES', 'TABLE_EXISTS', 'TABLE_SELECT', 'TABLE_ROWS',
            'TABLE_STRUCTURE', 'DATAVALIDATION'
        ]
        
        self.test_sheets = ['SMOKE', 'DATAVALIDATIONS']
        
        # Sample test cases for each sheet
        self.smoke_tests = [
            {'id': 'SMOKE_PG_001', 'name': 'Environment Setup Validation', 'category': 'SETUP'},
            {'id': 'SMOKE_PG_002', 'name': 'Configuration Availability', 'category': 'CONFIGURATION'},
            {'id': 'SMOKE_PG_003', 'name': 'Credentials Validation', 'category': 'SECURITY'},
            {'id': 'SMOKE_PG_004', 'name': 'Database Connectivity', 'category': 'CONNECTION'},
            {'id': 'SMOKE_PG_005', 'name': 'Basic Database Queries', 'category': 'QUERIES'},
            {'id': 'SMOKE_PG_007', 'name': 'Products Table Exists', 'category': 'TABLE_EXISTS'},
            {'id': 'SMOKE_PG_008', 'name': 'Employees Table Exists', 'category': 'TABLE_EXISTS'},
            {'id': 'SMOKE_PG_009', 'name': 'Orders Table Exists', 'category': 'TABLE_EXISTS'},
            {'id': 'SMOKE_PG_010', 'name': 'Products Table Select Test', 'category': 'TABLE_SELECT'},
            {'id': 'SMOKE_PG_011', 'name': 'Employees Table Select Test', 'category': 'TABLE_SELECT'},
            {'id': 'SMOKE_PG_012', 'name': 'Orders Table Select Test', 'category': 'TABLE_SELECT'},
            {'id': 'SMOKE_PG_013', 'name': 'Products Table Has Data', 'category': 'TABLE_ROWS'},
            {'id': 'SMOKE_PG_014', 'name': 'Employees Table Has Data', 'category': 'TABLE_ROWS'},
            {'id': 'SMOKE_PG_015', 'name': 'Orders Table Has Data', 'category': 'TABLE_ROWS'},
            {'id': 'SMOKE_PG_016', 'name': 'Products Table Structure', 'category': 'TABLE_STRUCTURE'},
            {'id': 'SMOKE_PG_017', 'name': 'Employees Table Structure', 'category': 'TABLE_STRUCTURE'},
            {'id': 'SMOKE_PG_018', 'name': 'Orders Table Structure', 'category': 'TABLE_STRUCTURE'},
        ]
        
        self.datavalidation_tests = [
            {'id': 'DVAL_001', 'name': 'Products Schema Validation', 'category': 'DATAVALIDATION'},
            {'id': 'DVAL_002', 'name': 'Employees Schema Validation', 'category': 'DATAVALIDATION'},
            {'id': 'DVAL_003', 'name': 'Orders Schema Validation', 'category': 'DATAVALIDATION'},
            {'id': 'DVAL_004', 'name': 'Products Row Count Validation', 'category': 'DATAVALIDATION'},
            {'id': 'DVAL_005', 'name': 'Employees Row Count Validation', 'category': 'DATAVALIDATION'},
            {'id': 'DVAL_006', 'name': 'Orders Row Count Validation', 'category': 'DATAVALIDATION'},
            {'id': 'DVAL_007', 'name': 'Products NULL Value Validation', 'category': 'DATAVALIDATION'},
            {'id': 'DVAL_008', 'name': 'Employees NULL Value Validation', 'category': 'DATAVALIDATION'},
            {'id': 'DVAL_009', 'name': 'Orders NULL Value Validation', 'category': 'DATAVALIDATION'},
        ]
    
    def generate_sample_data(self, days_back: int = 90) -> Dict:
        """
        Generate sample historical data for the specified number of days.
        
        Args:
            days_back: Number of days of historical data to generate
            
        Returns:
            Dict: Complete execution history in persistent format
        """
        print(f"🎲 Generating {days_back} days of sample historical data...")
        
        execution_history = []
        end_date = datetime.datetime.now()
        
        # Generate data for each day
        for day_offset in range(days_back, 0, -1):
            current_date = end_date - datetime.timedelta(days=day_offset)
            
            # Generate 1-3 executions per day (more on weekdays)
            executions_per_day = self._get_executions_for_day(current_date)
            
            for exec_num in range(executions_per_day):
                # Add some time variation within the day
                exec_time = current_date.replace(
                    hour=random.randint(8, 18),
                    minute=random.randint(0, 59),
                    second=random.randint(0, 59)
                ) + datetime.timedelta(hours=exec_num * 2)
                
                execution_record = self._generate_execution_record(exec_time, day_offset)
                execution_history.append(execution_record)
        
        # Sort by execution time
        execution_history.sort(key=lambda x: x['execution_metadata']['execution_time'])
        
        # Generate metadata
        metadata = self._generate_metadata(execution_history)
        
        sample_data = {
            "execution_history": execution_history,
            "trends_metadata": metadata
        }
        
        print(f"✅ Generated {len(execution_history)} execution records")
        print(f"📅 Date range: {metadata['date_range']['earliest']} to {metadata['date_range']['latest']}")
        
        return sample_data
    
    def _get_executions_for_day(self, date: datetime.datetime) -> int:
        """Determine number of executions for a given day based on realistic patterns."""
        # Weekends: fewer executions
        if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return random.choices([0, 1], weights=[30, 70])[0]
        
        # Weekdays: more executions, with Friday being lighter
        if date.weekday() == 4:  # Friday
            return random.choices([1, 2], weights=[60, 40])[0]
        
        # Monday to Thursday: most active
        return random.choices([1, 2, 3], weights=[30, 50, 20])[0]
    
    def _generate_execution_record(self, exec_time: datetime.datetime, day_offset: int) -> Dict:
        """Generate a single execution record with realistic patterns."""
        execution_id = exec_time.strftime('%Y%m%d_%H%M%S')
        
        # Create realistic success rate patterns
        base_success_rate = self._get_base_success_rate(exec_time, day_offset)
        
        # Generate test results for each sheet
        smoke_results = self._generate_sheet_results('SMOKE', self.smoke_tests, base_success_rate + 0.1)
        dataval_results = self._generate_sheet_results('DATAVALIDATIONS', self.datavalidation_tests, base_success_rate - 0.05)
        
        # Calculate overall summary
        all_tests = smoke_results['test_cases'] + dataval_results['test_cases']
        overall_summary = self._calculate_overall_summary(all_tests)
        
        # Generate category-level results
        category_results = self._generate_category_results(all_tests)
        
        # Generate test case details
        test_case_details = self._generate_test_case_details(all_tests)
        
        # Generate performance metrics
        performance_metrics = self._generate_performance_metrics(all_tests, exec_time)
        
        return {
            "execution_metadata": {
                "execution_id": execution_id,
                "execution_time": exec_time.isoformat(),
                "duration_seconds": random.uniform(30, 90),
                "environment": "production",
                "application": "cross_db_validator",
                "excel_file": "inputs/test_suite.xlsx",
                "data_collection_version": "1.0"
            },
            "overall_summary": overall_summary,
            "sheet_level_results": {
                "SMOKE": smoke_results,
                "DATAVALIDATIONS": dataval_results
            },
            "category_level_results": category_results,
            "test_case_details": test_case_details,
            "performance_metrics": performance_metrics
        }
    
    def _get_base_success_rate(self, exec_time: datetime.datetime, day_offset: int) -> float:
        """Calculate base success rate with realistic patterns."""
        # Start with base rate
        base_rate = 0.75
        
        # Monthly trend - gradually improving over time
        monthly_improvement = (90 - day_offset) * 0.002  # 0.2% improvement per day
        
        # Weekly pattern - Monday struggles, Friday pre-weekend issues
        weekday_factor = {
            0: -0.05,  # Monday
            1: 0.02,   # Tuesday
            2: 0.03,   # Wednesday  
            3: 0.02,   # Thursday
            4: -0.03,  # Friday
            5: -0.08,  # Saturday
            6: -0.10   # Sunday
        }
        
        # Time of day factor - early morning and late evening have more issues
        hour = exec_time.hour
        if hour < 9 or hour > 17:
            time_factor = -0.05
        elif 10 <= hour <= 16:
            time_factor = 0.03
        else:
            time_factor = 0.0
        
        # Add some randomness
        random_factor = random.uniform(-0.08, 0.08)
        
        success_rate = base_rate + monthly_improvement + weekday_factor[exec_time.weekday()] + time_factor + random_factor
        
        # Ensure rate stays within realistic bounds
        return max(0.55, min(0.95, success_rate))
    
    def _generate_sheet_results(self, sheet_name: str, test_list: List[Dict], success_rate: float) -> Dict:
        """Generate test results for a specific sheet."""
        test_cases = []
        
        for test in test_list:
            # Individual test success rate with some variation
            test_success_rate = success_rate + random.uniform(-0.15, 0.15)
            test_success_rate = max(0.0, min(1.0, test_success_rate))
            
            # Determine status
            rand = random.random()
            if rand < test_success_rate:
                status = "PASSED"
            elif rand < test_success_rate + 0.05:  # Small chance of skip
                status = "SKIPPED"
            else:
                status = "FAILED"
            
            # Generate realistic execution time based on test type
            base_time = self._get_base_execution_time(test['category'])
            execution_time_ms = int(base_time + random.uniform(-200, 500))
            
            test_cases.append({
                "test_case_id": test['id'],
                "test_case_name": test['name'],
                "test_category": test['category'],
                "priority": random.choice(['HIGH', 'MEDIUM', 'LOW']),
                "status": status,
                "execution_time_ms": execution_time_ms,
                "tags": [test['category'].lower()],
                "error_message": None
            })
        
        # Calculate summary
        total = len(test_cases)
        passed = sum(1 for tc in test_cases if tc['status'] == 'PASSED')
        failed = sum(1 for tc in test_cases if tc['status'] == 'FAILED')
        skipped = sum(1 for tc in test_cases if tc['status'] == 'SKIPPED')
        
        summary = {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "passed_rate": round(passed / total * 100, 2) if total > 0 else 0,
            "failed_rate": round(failed / total * 100, 2) if total > 0 else 0,
            "skipped_rate": round(skipped / total * 100, 2) if total > 0 else 0
        }
        
        return {
            "summary": summary,
            "test_cases": test_cases
        }
    
    def _get_base_execution_time(self, category: str) -> int:
        """Get base execution time in milliseconds for different test categories."""
        base_times = {
            'SETUP': 800,
            'CONFIGURATION': 600,
            'SECURITY': 1200,
            'CONNECTION': 1500,
            'QUERIES': 2000,
            'TABLE_EXISTS': 800,
            'TABLE_SELECT': 1000,
            'TABLE_ROWS': 1200,
            'TABLE_STRUCTURE': 900,
            'DATAVALIDATION': 2500
        }
        return base_times.get(category, 1000)
    
    def _calculate_overall_summary(self, all_tests: List[Dict]) -> Dict:
        """Calculate overall summary from all test cases."""
        total = len(all_tests)
        passed = sum(1 for tc in all_tests if tc['status'] == 'PASSED')
        failed = sum(1 for tc in all_tests if tc['status'] == 'FAILED')
        skipped = sum(1 for tc in all_tests if tc['status'] == 'SKIPPED')
        
        return {
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "passed_rate": round(passed / total * 100, 2) if total > 0 else 0,
            "failed_rate": round(failed / total * 100, 2) if total > 0 else 0,
            "skipped_rate": round(skipped / total * 100, 2) if total > 0 else 0
        }
    
    def _generate_category_results(self, all_tests: List[Dict]) -> Dict:
        """Generate category-level results."""
        category_data = {}
        
        for category in self.test_categories:
            category_tests = [tc for tc in all_tests if tc['test_category'] == category]
            
            if category_tests:
                total = len(category_tests)
                passed = sum(1 for tc in category_tests if tc['status'] == 'PASSED')
                failed = sum(1 for tc in category_tests if tc['status'] == 'FAILED')
                skipped = sum(1 for tc in category_tests if tc['status'] == 'SKIPPED')
                
                category_data[category] = {
                    "total_tests": total,
                    "passed_tests": passed,
                    "failed_tests": failed,
                    "skipped_tests": skipped,
                    "passed_rate": round(passed / total * 100, 2) if total > 0 else 0,
                    "failed_rate": round(failed / total * 100, 2) if total > 0 else 0,
                    "skipped_rate": round(skipped / total * 100, 2) if total > 0 else 0
                }
        
        return category_data
    
    def _generate_test_case_details(self, all_tests: List[Dict]) -> Dict:
        """Generate individual test case details."""
        test_details = {}
        
        for test in all_tests:
            test_details[test['test_case_id']] = {
                "last_status": test['status'],
                "execution_time_ms": test['execution_time_ms'],
                "sheet_name": "SMOKE" if test['test_case_id'].startswith('SMOKE') else "DATAVALIDATIONS",
                "test_category": test['test_category'],
                "priority": test['priority']
            }
        
        return test_details
    
    def _generate_performance_metrics(self, all_tests: List[Dict], exec_time: datetime.datetime) -> Dict:
        """Generate performance metrics."""
        execution_times = [tc['execution_time_ms'] for tc in all_tests]
        total_time = sum(execution_times)
        avg_time = total_time / len(execution_times) if execution_times else 0
        
        # Sort for fastest/slowest
        sorted_tests = sorted(all_tests, key=lambda x: x['execution_time_ms'])
        
        return {
            "total_execution_time_ms": total_time,
            "average_test_time_ms": round(avg_time, 2),
            "slowest_tests": [
                {
                    "test_id": tc['test_case_id'],
                    "execution_time_ms": tc['execution_time_ms'],
                    "sheet_name": "SMOKE" if tc['test_case_id'].startswith('SMOKE') else "DATAVALIDATIONS"
                } for tc in sorted_tests[-5:]
            ],
            "fastest_tests": [
                {
                    "test_id": tc['test_case_id'],
                    "execution_time_ms": tc['execution_time_ms'],
                    "sheet_name": "SMOKE" if tc['test_case_id'].startswith('SMOKE') else "DATAVALIDATIONS"
                } for tc in sorted_tests[:5]
            ],
            "sheet_performance": {
                "SMOKE": self._calculate_sheet_performance([tc for tc in all_tests if tc['test_case_id'].startswith('SMOKE')]),
                "DATAVALIDATIONS": self._calculate_sheet_performance([tc for tc in all_tests if tc['test_case_id'].startswith('DVAL')])
            }
        }
    
    def _calculate_sheet_performance(self, sheet_tests: List[Dict]) -> Dict:
        """Calculate performance metrics for a specific sheet."""
        if not sheet_tests:
            return {"total_time_ms": 0, "average_time_ms": 0, "test_count": 0}
        
        total_time = sum(tc['execution_time_ms'] for tc in sheet_tests)
        count = len(sheet_tests)
        
        return {
            "total_time_ms": total_time,
            "average_time_ms": round(total_time / count, 2),
            "test_count": count
        }
    
    def _generate_metadata(self, execution_history: List[Dict]) -> Dict:
        """Generate metadata for the sample data."""
        if not execution_history:
            return {}
        
        execution_times = [datetime.datetime.fromisoformat(record['execution_metadata']['execution_time']) 
                          for record in execution_history]
        
        return {
            "data_version": "2.0",
            "last_updated": datetime.datetime.now().isoformat(),
            "total_executions": len(execution_history),
            "date_range": {
                "earliest": min(execution_times).isoformat(),
                "latest": max(execution_times).isoformat(),
                "span_days": (max(execution_times) - min(execution_times)).days
            },
            "retention_policy": {
                "keep_days": 365,
                "auto_cleanup": True
            },
            "analysis_capabilities": [
                "overall_trends", "sheet_level_trends", "category_level_trends", 
                "individual_test_trends", "performance_trends", "time_based_aggregation"
            ]
        }
    
    def save_sample_data(self, data_file: str = "data/test_execution_history.json", days_back: int = 90):
        """Generate and save sample data to the persistent storage file."""
        # Generate sample data
        sample_data = self.generate_sample_data(days_back)
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        
        # Save to file
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sample data saved to {data_file}")
        print(f"📊 {len(sample_data['execution_history'])} execution records generated")
        print(f"🗓️ Spanning {sample_data['trends_metadata']['date_range']['span_days']} days")
        
        return data_file


if __name__ == "__main__":
    generator = SampleTrendsDataGenerator()
    generator.save_sample_data(days_back=90)  # Generate 90 days of sample data
    print("✅ Sample historical data generation complete!")
    print("🚀 Run 'python main.py' and choose option 4 to see comprehensive trends!")