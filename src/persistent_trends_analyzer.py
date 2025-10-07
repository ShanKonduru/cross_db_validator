"""
Persistent Trends Analyzer
Analyzes test execution trends from persistent JSON data file.
Supports multi-level trend analysis: Overall, Sheet-level, Category-level, and Individual test case trends.
Provides time-based aggregation: Hourly, Daily, Weekly, Monthly, and Yearly trends.
"""

import os
import json
import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime as dt, timedelta


class PersistentTrendsAnalyzer:
    """
    Analyzes trends from persistent execution data.
    Provides comprehensive trend analysis at multiple levels and time periods.
    """
    
    def __init__(self, data_file: str = "data/test_execution_history.json"):
        self.data_file = data_file
        self.execution_history = []
        self.load_execution_history()
    
    def load_execution_history(self) -> List[Dict]:
        """Load execution history from persistent JSON file."""
        if not os.path.exists(self.data_file):
            print(f"📄 No persistent data file found at {self.data_file}")
            return []
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.execution_history = data.get('execution_history', [])
                print(f"📊 Loaded {len(self.execution_history)} execution records from persistent storage")
                return self.execution_history
        except Exception as e:
            print(f"⚠️ Error loading execution history: {e}")
            return []
    
    def generate_comprehensive_trends(self) -> Dict:
        """Generate comprehensive trends analysis across all levels and time periods."""
        if not self.execution_history:
            return {
                'error': 'No execution history available',
                'message': 'Run some tests first to generate trend data'
            }
        
        trends_analysis = {
            'metadata': self._generate_trends_metadata(),
            'overall_trends': self._generate_overall_trends(),
            'filter_data': self._generate_filter_data(),
            'time_based_trends': {
                'hourly': self._generate_hourly_trends(),
                'daily': self._generate_daily_trends(),
                'weekly': self._generate_weekly_trends(),
                'monthly': self._generate_monthly_trends(),
                'yearly': self._generate_yearly_trends()
            },
            'sheet_level_trends': self._generate_sheet_trends(),
            'category_level_trends': self._generate_category_trends(),
            'individual_test_trends': self._generate_individual_test_trends(),
            'performance_trends': self._generate_performance_trends(),
            'insights': self._generate_trend_insights()
        }
        
        return trends_analysis
    
    def _generate_trends_metadata(self) -> Dict:
        """Generate metadata about the trends analysis."""
        if not self.execution_history:
            return {}
        
        execution_times = [dt.fromisoformat(record['execution_metadata']['execution_time']) 
                          for record in self.execution_history]
        
        return {
            'total_executions': len(self.execution_history),
            'analysis_generated': datetime.datetime.now().isoformat(),
            'date_range': {
                'earliest': min(execution_times).isoformat(),
                'latest': max(execution_times).isoformat(),
                'span_days': (max(execution_times) - min(execution_times)).days
            },
            'data_source': self.data_file,
            'analysis_levels': [
                'overall_summary', 'sheet_level', 'category_level', 
                'individual_test_case', 'performance_metrics'
            ],
            'time_aggregations': ['hourly', 'daily', 'weekly', 'monthly', 'yearly']
        }
    
    def _generate_overall_trends(self) -> Dict:
        """Generate overall execution trends across all time."""
        overall_stats = {
            'total_executions': len(self.execution_history),
            'average_metrics': defaultdict(list),
            'trend_direction': {},
            'execution_frequency': {}
        }
        
        # Collect metrics from each execution
        for record in self.execution_history:
            summary = record.get('overall_summary', {})
            overall_stats['average_metrics']['total_tests'].append(summary.get('total_tests', 0))
            overall_stats['average_metrics']['passed_rate'].append(summary.get('passed_rate', 0))
            overall_stats['average_metrics']['failed_rate'].append(summary.get('failed_rate', 0))
            overall_stats['average_metrics']['skipped_rate'].append(summary.get('skipped_rate', 0))
        
        # Calculate averages
        for metric, values in overall_stats['average_metrics'].items():
            if values:
                overall_stats['average_metrics'][metric] = {
                    'average': round(sum(values) / len(values), 2),
                    'minimum': min(values),
                    'maximum': max(values),
                    'latest': values[-1] if values else 0,
                    'trend': self._calculate_trend_direction(values)
                }
        
        return overall_stats
    
    def _generate_filter_data(self) -> Dict:
        """Generate filter data for applications and environments."""
        applications = set()
        environments = set()
        source_applications = set()
        source_environments = set()
        target_applications = set()
        target_environments = set()
        
        print(f"🔍 Debug: Processing {len(self.execution_history)} execution records for filter data...")
        
        for record in self.execution_history:
            # Standard application and environment from metadata
            metadata = record.get('execution_metadata', {})
            if 'application' in metadata:
                applications.add(metadata['application'])
                print(f"🔍 Found application: {metadata['application']}")
            if 'environment' in metadata:
                environments.add(metadata['environment'])
                print(f"🔍 Found environment: {metadata['environment']}")
            
            # Extract cross-database application/environment info from test cases
            for sheet_name, sheet_data in record.get('sheet_level_results', {}).items():
                for test_case in sheet_data.get('test_cases', []):
                    test_id = test_case.get('test_case_id', 'unknown')
                    test_name = test_case.get('test_case_name', '')
                    
                    # Look for cross-database test execution details (current format)
                    if 'execution_details' in test_case:
                        details = test_case['execution_details']
                        
                        # Parse source_db and target_db (format: "APP.ENV")
                        if 'source_db' in details:
                            source_db = details['source_db']
                            if '.' in source_db:
                                src_app, src_env = source_db.split('.', 1)
                                source_applications.add(src_app)
                                source_environments.add(src_env)
                                applications.add(src_app)
                                environments.add(src_env)
                        
                        if 'target_db' in details:
                            target_db = details['target_db']
                            if '.' in target_db:
                                tgt_app, tgt_env = target_db.split('.', 1)
                                target_applications.add(tgt_app)
                                target_environments.add(tgt_env)
                                applications.add(tgt_app)
                                environments.add(tgt_env)
            
            # Also check in individual test trends data structure
            individual_tests = record.get('individual_test_results', {})
            for test_id, test_data in individual_tests.items():
                if 'execution_details' in test_data:
                    details = test_data['execution_details']
                    print(f"🔍 Debug: Found execution_details in individual test {test_id}: {details}")
                    
                    # Parse source_db and target_db (format: "APP.ENV")
                    if 'source_db' in details:
                        source_db = details['source_db']
                        if '.' in source_db:
                            src_app, src_env = source_db.split('.', 1)
                            source_applications.add(src_app)
                            source_environments.add(src_env)
                            applications.add(src_app)
                            environments.add(src_env)
                    
                    if 'target_db' in details:
                        target_db = details['target_db']
                        if '.' in target_db:
                            tgt_app, tgt_env = target_db.split('.', 1)
                            target_applications.add(tgt_app)
                            target_environments.add(tgt_env)
                            applications.add(tgt_app)
                            environments.add(tgt_env)
        
        result = {
            'applications': sorted(list(applications)),
            'environments': sorted(list(environments)),
            'source_applications': sorted(list(source_applications)),
            'source_environments': sorted(list(source_environments)),
            'target_applications': sorted(list(target_applications)),
            'target_environments': sorted(list(target_environments))
        }
        
        return result
    
    def _generate_hourly_trends(self) -> Dict:
        """Generate hourly trend analysis."""
        hourly_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0, 
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in self.execution_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            hour_key = exec_time.hour
            summary = record.get('overall_summary', {})
            
            hourly_data[hour_key]['executions'] += 1
            hourly_data[hour_key]['total_tests'] += summary.get('total_tests', 0)
            hourly_data[hour_key]['passed_tests'] += summary.get('passed_tests', 0)
            hourly_data[hour_key]['failed_tests'] += summary.get('failed_tests', 0)
            hourly_data[hour_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate success rates for each hour
        for hour, data in hourly_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(hourly_data)
    
    def _generate_daily_trends(self) -> Dict:
        """Generate daily trend analysis."""
        daily_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in self.execution_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            day_key = exec_time.strftime('%Y-%m-%d')
            summary = record.get('overall_summary', {})
            
            daily_data[day_key]['executions'] += 1
            daily_data[day_key]['total_tests'] += summary.get('total_tests', 0)
            daily_data[day_key]['passed_tests'] += summary.get('passed_tests', 0)
            daily_data[day_key]['failed_tests'] += summary.get('failed_tests', 0)
            daily_data[day_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate rates
        for day, data in daily_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(daily_data)
    
    def _generate_weekly_trends(self) -> Dict:
        """Generate weekly trend analysis."""
        weekly_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in self.execution_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            # Get year and week number
            year, week, _ = exec_time.isocalendar()
            week_key = f"{year}-W{week:02d}"
            summary = record.get('overall_summary', {})
            
            weekly_data[week_key]['executions'] += 1
            weekly_data[week_key]['total_tests'] += summary.get('total_tests', 0)
            weekly_data[week_key]['passed_tests'] += summary.get('passed_tests', 0)
            weekly_data[week_key]['failed_tests'] += summary.get('failed_tests', 0)
            weekly_data[week_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate rates
        for week, data in weekly_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(weekly_data)
    
    def _generate_monthly_trends(self) -> Dict:
        """Generate monthly trend analysis."""
        monthly_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in self.execution_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            month_key = exec_time.strftime('%Y-%m')
            summary = record.get('overall_summary', {})
            
            monthly_data[month_key]['executions'] += 1
            monthly_data[month_key]['total_tests'] += summary.get('total_tests', 0)
            monthly_data[month_key]['passed_tests'] += summary.get('passed_tests', 0)
            monthly_data[month_key]['failed_tests'] += summary.get('failed_tests', 0)
            monthly_data[month_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate rates
        for month, data in monthly_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(monthly_data)
    
    def _generate_yearly_trends(self) -> Dict:
        """Generate yearly trend analysis."""
        yearly_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in self.execution_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            year_key = str(exec_time.year)
            summary = record.get('overall_summary', {})
            
            yearly_data[year_key]['executions'] += 1
            yearly_data[year_key]['total_tests'] += summary.get('total_tests', 0)
            yearly_data[year_key]['passed_tests'] += summary.get('passed_tests', 0)
            yearly_data[year_key]['failed_tests'] += summary.get('failed_tests', 0)
            yearly_data[year_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate rates
        for year, data in yearly_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(yearly_data)
    
    def _generate_sheet_trends(self) -> Dict:
        """Generate sheet-level trend analysis."""
        sheet_trends = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0, 'history': []
        })
        
        for record in self.execution_history:
            exec_time = record['execution_metadata']['execution_time']
            sheet_results = record.get('sheet_level_results', {})
            
            for sheet_name, sheet_data in sheet_results.items():
                summary = sheet_data.get('summary', {})
                
                sheet_trends[sheet_name]['executions'] += 1
                sheet_trends[sheet_name]['total_tests'] += summary.get('total_tests', 0)
                sheet_trends[sheet_name]['passed_tests'] += summary.get('passed_tests', 0)
                sheet_trends[sheet_name]['failed_tests'] += summary.get('failed_tests', 0)
                sheet_trends[sheet_name]['skipped_tests'] += summary.get('skipped_tests', 0)
                
                # Keep historical data points
                sheet_trends[sheet_name]['history'].append({
                    'execution_time': exec_time,
                    'passed_rate': summary.get('passed_rate', 0),
                    'total_tests': summary.get('total_tests', 0)
                })
        
        # Calculate overall rates for each sheet
        for sheet_name, data in sheet_trends.items():
            if data['total_tests'] > 0:
                data['overall_passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['overall_failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['overall_skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(sheet_trends)
    
    def _generate_category_trends(self) -> Dict:
        """Generate category-level trend analysis."""
        category_trends = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0, 'history': []
        })
        
        for record in self.execution_history:
            exec_time = record['execution_metadata']['execution_time']
            category_results = record.get('category_level_results', {})
            
            for category, category_data in category_results.items():
                category_trends[category]['executions'] += 1
                category_trends[category]['total_tests'] += category_data.get('total_tests', 0)
                category_trends[category]['passed_tests'] += category_data.get('passed_tests', 0)
                category_trends[category]['failed_tests'] += category_data.get('failed_tests', 0)
                category_trends[category]['skipped_tests'] += category_data.get('skipped_tests', 0)
                
                # Keep historical data points
                category_trends[category]['history'].append({
                    'execution_time': exec_time,
                    'passed_rate': category_data.get('passed_rate', 0),
                    'total_tests': category_data.get('total_tests', 0)
                })
        
        # Calculate overall rates for each category
        for category, data in category_trends.items():
            if data['total_tests'] > 0:
                data['overall_passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['overall_failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['overall_skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(category_trends)
    
    def _generate_individual_test_trends(self) -> Dict:
        """Generate individual test case trend analysis."""
        test_trends = defaultdict(lambda: {
            'executions': 0, 'passed_count': 0, 'failed_count': 0, 'skipped_count': 0,
            'consecutive_passes': 0, 'consecutive_fails': 0, 'history': [],
            'avg_execution_time_ms': 0, 'execution_times': []
        })
        
        for record in self.execution_history:
            exec_time = record['execution_metadata']['execution_time']
            test_details = record.get('test_case_details', {})
            
            for test_id, test_data in test_details.items():
                status = test_data.get('last_status', '')
                exec_time_ms = test_data.get('execution_time_ms', 0)
                
                test_trends[test_id]['executions'] += 1
                test_trends[test_id]['execution_times'].append(exec_time_ms)
                
                if status == 'PASSED':
                    test_trends[test_id]['passed_count'] += 1
                elif status == 'FAILED':
                    test_trends[test_id]['failed_count'] += 1
                elif status == 'SKIPPED':
                    test_trends[test_id]['skipped_count'] += 1
                
                # Keep historical data points
                test_trends[test_id]['history'].append({
                    'execution_time': exec_time,
                    'status': status,
                    'execution_time_ms': exec_time_ms
                })
        
        # Calculate rates and averages for each test
        for test_id, data in test_trends.items():
            total_execs = data['executions']
            if total_execs > 0:
                data['success_rate'] = round(data['passed_count'] / total_execs * 100, 2)
                data['failure_rate'] = round(data['failed_count'] / total_execs * 100, 2)
                data['skip_rate'] = round(data['skipped_count'] / total_execs * 100, 2)
            
            if data['execution_times']:
                data['avg_execution_time_ms'] = round(sum(data['execution_times']) / len(data['execution_times']), 2)
        
        return dict(test_trends)
    
    def _generate_performance_trends(self) -> Dict:
        """Generate performance trend analysis."""
        performance_trends = {
            'execution_time_trends': [],
            'performance_regression': [],
            'fastest_improving_tests': [],
            'slowest_degrading_tests': []
        }
        
        for record in self.execution_history:
            exec_time = record['execution_metadata']['execution_time']
            perf_metrics = record.get('performance_metrics', {})
            
            performance_trends['execution_time_trends'].append({
                'execution_time': exec_time,
                'total_time_ms': perf_metrics.get('total_execution_time_ms', 0),
                'average_test_time_ms': perf_metrics.get('average_test_time_ms', 0)
            })
        
        return performance_trends
    
    def _generate_trend_insights(self) -> List[str]:
        """Generate automated insights about the trends."""
        insights = []
        
        if not self.execution_history:
            return ["No execution data available for insights"]
        
        # Overall trend insights
        recent_executions = self.execution_history[-5:] if len(self.execution_history) >= 5 else self.execution_history
        recent_success_rates = [exec_record.get('overall_summary', {}).get('passed_rate', 0) 
                               for exec_record in recent_executions]
        
        if recent_success_rates:
            avg_recent_success = sum(recent_success_rates) / len(recent_success_rates)
            if avg_recent_success > 80:
                insights.append(f"🟢 Test suite health is excellent with {avg_recent_success:.1f}% average success rate")
            elif avg_recent_success > 60:
                insights.append(f"🟡 Test suite health is moderate with {avg_recent_success:.1f}% average success rate")
            else:
                insights.append(f"🔴 Test suite health needs attention with {avg_recent_success:.1f}% average success rate")
        
        # Execution frequency insights
        if len(self.execution_history) > 1:
            exec_times = [dt.fromisoformat(record['execution_metadata']['execution_time']) 
                         for record in self.execution_history]
            time_span = (max(exec_times) - min(exec_times)).days
            if time_span > 0:
                frequency = len(self.execution_history) / time_span
                insights.append(f"📊 Test execution frequency: {frequency:.1f} runs per day over {time_span} days")
        
        return insights
    
    def _calculate_trend_direction(self, values: List[float]) -> str:
        """Calculate trend direction (improving, declining, stable)."""
        if len(values) < 2:
            return "insufficient_data"
        
        # Simple trend calculation using first half vs second half
        mid_point = len(values) // 2
        first_half_avg = sum(values[:mid_point]) / mid_point if mid_point > 0 else 0
        second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
        
        diff_percentage = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
        
        if diff_percentage > 5:
            return "improving"
        elif diff_percentage < -5:
            return "declining"
        else:
            return "stable"
    
    def generate_filtered_time_trends(self, application: str = None, environment: str = None, 
                                    source_db: str = None, target_db: str = None) -> Dict:
        """Generate time-based trends filtered by application, environment, and/or databases."""
        filtered_history = self._filter_execution_history(application, environment, source_db, target_db)
        
        if not filtered_history:
            return {
                'error': 'No data matches the selected filters',
                'filters_applied': {
                    'application': application,
                    'environment': environment,
                    'source_db': source_db,
                    'target_db': target_db
                }
            }
        
        return {
            'metadata': {
                'total_filtered_executions': len(filtered_history),
                'filters_applied': {
                    'application': application,
                    'environment': environment,
                    'source_db': source_db,
                    'target_db': target_db
                }
            },
            'hourly': self._generate_filtered_hourly_trends(filtered_history),
            'daily': self._generate_filtered_daily_trends(filtered_history),
            'weekly': self._generate_filtered_weekly_trends(filtered_history),
            'monthly': self._generate_filtered_monthly_trends(filtered_history),
            'yearly': self._generate_filtered_yearly_trends(filtered_history)
        }
    
    def _filter_execution_history(self, application: str = None, environment: str = None, 
                                 source_db: str = None, target_db: str = None) -> List[Dict]:
        """Filter execution history based on the provided criteria."""
        filtered_records = []
        
        for record in self.execution_history:
            # Check application filter
            if application:
                record_app = self._extract_application_from_record(record)
                if record_app != application:
                    continue
            
            # Check environment filter
            if environment:
                record_env = self._extract_environment_from_record(record)
                if record_env != environment:
                    continue
            
            # Check source database filter
            if source_db:
                record_source = self._extract_source_db_from_record(record)
                if record_source != source_db:
                    continue
            
            # Check target database filter
            if target_db:
                record_target = self._extract_target_db_from_record(record)
                if record_target != target_db:
                    continue
            
            filtered_records.append(record)
        
        return filtered_records
    
    def _extract_application_from_record(self, record: Dict) -> str:
        """Extract application from execution record."""
        # Try to get from execution details first
        for sheet_group in record.get('sheet_groups', []):
            for test_case in sheet_group.get('test_cases', []):
                execution_details = test_case.get('execution_details', {})
                if execution_details.get('source_application'):
                    return execution_details['source_application']
        
        # Fallback to pattern matching from test names
        for sheet_group in record.get('sheet_groups', []):
            for test_case in sheet_group.get('test_cases', []):
                test_name = test_case.get('test_name', '')
                if 'DUMMY' in test_name.upper():
                    return 'DUMMY'
                elif 'cross_db_validator' in test_name:
                    return 'cross_db_validator'
        
        return 'default'
    
    def _extract_environment_from_record(self, record: Dict) -> str:
        """Extract environment from execution record."""
        # Try to get from execution details first
        for sheet_group in record.get('sheet_groups', []):
            for test_case in sheet_group.get('test_cases', []):
                execution_details = test_case.get('execution_details', {})
                if execution_details.get('source_environment'):
                    return execution_details['source_environment']
        
        # Fallback to pattern matching
        for sheet_group in record.get('sheet_groups', []):
            for test_case in sheet_group.get('test_cases', []):
                test_name = test_case.get('test_name', '')
                if 'NP1' in test_name.upper():
                    return 'NP1'
                elif 'DEV' in test_name.upper():
                    return 'DEV'
                elif 'PROD' in test_name.upper():
                    return 'production'
        
        return 'default'
    
    def _extract_source_db_from_record(self, record: Dict) -> str:
        """Extract source database from execution record."""
        for sheet_group in record.get('sheet_groups', []):
            for test_case in sheet_group.get('test_cases', []):
                execution_details = test_case.get('execution_details', {})
                source_app = execution_details.get('source_application', '')
                source_env = execution_details.get('source_environment', '')
                if source_app and source_env:
                    return f"{source_app}.{source_env}"
        
        return None
    
    def _extract_target_db_from_record(self, record: Dict) -> str:
        """Extract target database from execution record."""
        for sheet_group in record.get('sheet_groups', []):
            for test_case in sheet_group.get('test_cases', []):
                execution_details = test_case.get('execution_details', {})
                target_app = execution_details.get('target_application', '')
                target_env = execution_details.get('target_environment', '')
                if target_app and target_env:
                    return f"{target_app}.{target_env}"
        
        return None
    
    def _generate_filtered_hourly_trends(self, filtered_history: List[Dict]) -> Dict:
        """Generate hourly trends from filtered data."""
        hourly_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0, 
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in filtered_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            hour_key = exec_time.hour
            summary = record.get('overall_summary', {})
            
            hourly_data[hour_key]['executions'] += 1
            hourly_data[hour_key]['total_tests'] += summary.get('total_tests', 0)
            hourly_data[hour_key]['passed_tests'] += summary.get('passed_tests', 0)
            hourly_data[hour_key]['failed_tests'] += summary.get('failed_tests', 0)
            hourly_data[hour_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate success rates
        for hour, data in hourly_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(hourly_data)
    
    def _generate_filtered_daily_trends(self, filtered_history: List[Dict]) -> Dict:
        """Generate daily trends from filtered data."""
        daily_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in filtered_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            day_key = exec_time.strftime('%Y-%m-%d')
            summary = record.get('overall_summary', {})
            
            daily_data[day_key]['executions'] += 1
            daily_data[day_key]['total_tests'] += summary.get('total_tests', 0)
            daily_data[day_key]['passed_tests'] += summary.get('passed_tests', 0)
            daily_data[day_key]['failed_tests'] += summary.get('failed_tests', 0)
            daily_data[day_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate rates
        for day, data in daily_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(daily_data)
    
    def _generate_filtered_weekly_trends(self, filtered_history: List[Dict]) -> Dict:
        """Generate weekly trends from filtered data."""
        weekly_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in filtered_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            year, week, _ = exec_time.isocalendar()
            week_key = f"{year}-W{week:02d}"
            summary = record.get('overall_summary', {})
            
            weekly_data[week_key]['executions'] += 1
            weekly_data[week_key]['total_tests'] += summary.get('total_tests', 0)
            weekly_data[week_key]['passed_tests'] += summary.get('passed_tests', 0)
            weekly_data[week_key]['failed_tests'] += summary.get('failed_tests', 0)
            weekly_data[week_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate rates
        for week, data in weekly_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(weekly_data)
    
    def _generate_filtered_monthly_trends(self, filtered_history: List[Dict]) -> Dict:
        """Generate monthly trends from filtered data."""
        monthly_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in filtered_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            month_key = exec_time.strftime('%Y-%m')
            summary = record.get('overall_summary', {})
            
            monthly_data[month_key]['executions'] += 1
            monthly_data[month_key]['total_tests'] += summary.get('total_tests', 0)
            monthly_data[month_key]['passed_tests'] += summary.get('passed_tests', 0)
            monthly_data[month_key]['failed_tests'] += summary.get('failed_tests', 0)
            monthly_data[month_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate rates
        for month, data in monthly_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(monthly_data)
    
    def _generate_filtered_yearly_trends(self, filtered_history: List[Dict]) -> Dict:
        """Generate yearly trends from filtered data."""
        yearly_data = defaultdict(lambda: {
            'executions': 0, 'total_tests': 0, 'passed_tests': 0,
            'failed_tests': 0, 'skipped_tests': 0
        })
        
        for record in filtered_history:
            exec_time = dt.fromisoformat(record['execution_metadata']['execution_time'])
            year_key = str(exec_time.year)
            summary = record.get('overall_summary', {})
            
            yearly_data[year_key]['executions'] += 1
            yearly_data[year_key]['total_tests'] += summary.get('total_tests', 0)
            yearly_data[year_key]['passed_tests'] += summary.get('passed_tests', 0)
            yearly_data[year_key]['failed_tests'] += summary.get('failed_tests', 0)
            yearly_data[year_key]['skipped_tests'] += summary.get('skipped_tests', 0)
        
        # Calculate rates
        for year, data in yearly_data.items():
            if data['total_tests'] > 0:
                data['passed_rate'] = round(data['passed_tests'] / data['total_tests'] * 100, 2)
                data['failed_rate'] = round(data['failed_tests'] / data['total_tests'] * 100, 2)
                data['skipped_rate'] = round(data['skipped_tests'] / data['total_tests'] * 100, 2)
        
        return dict(yearly_data)