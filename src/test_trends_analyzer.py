import os
import re
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import glob


class TestExecutionTrendsAnalyzer:
    """
    Analyzes test execution trends over time by parsing historical reports.
    Provides insights into test performance across hourly, daily, weekly, monthly, and yearly periods.
    """
    
    def __init__(self, reports_directory: str = "output"):
        self.reports_directory = reports_directory
        self.historical_data = []
        self.trends_data = {}
        
    def parse_historical_reports(self) -> List[Dict]:
        """Parse all historical reports from the output directory."""
        historical_data = []
        
        # Get all markdown reports (excluding HTML and enhanced markdown for now)
        md_files = glob.glob(os.path.join(self.reports_directory, "Test_Execution_Results_*.md"))
        
        for file_path in md_files:
            # Skip enhanced markdown files
            if "Enhanced" in file_path:
                continue
                
            try:
                report_data = self._parse_single_report(file_path)
                if report_data:
                    historical_data.append(report_data)
            except Exception as e:
                print(f"⚠️ Error parsing {file_path}: {e}")
                continue
        
        # Sort by execution time
        historical_data.sort(key=lambda x: x['execution_time'])
        self.historical_data = historical_data
        
        return historical_data
    
    def _parse_single_report(self, file_path: str) -> Dict:
        """Parse a single report file and extract key metrics."""
        # Extract timestamp from filename
        filename = os.path.basename(file_path)
        timestamp_match = re.search(r'(\d{8}_\d{6})', filename)
        
        if not timestamp_match:
            return None
            
        timestamp_str = timestamp_match.group(1)
        execution_time = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        
        # Read and parse the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract summary statistics
        summary_pattern = r'Total Test Cases:\s*(\d+).*?Passed Test Cases:\s*(\d+).*?pass rate:\s*([\d.]+)%.*?Failed Test Cases:\s*(\d+).*?fail rate:\s*([\d.]+)%.*?Skipped Test Cases:\s*(\d+).*?skip rate:\s*([\d.]+)%'
        summary_match = re.search(summary_pattern, content, re.DOTALL)
        
        if not summary_match:
            return None
        
        total_tests = int(summary_match.group(1))
        passed_tests = int(summary_match.group(2))
        passed_rate = float(summary_match.group(3))
        failed_tests = int(summary_match.group(4))
        failed_rate = float(summary_match.group(5))
        skipped_tests = int(summary_match.group(6))
        skipped_rate = float(summary_match.group(7))
        
        # Extract test cases by category
        categories = self._extract_test_categories(content)
        
        # Extract test cases by sheet
        sheets = self._extract_sheet_data(content)
        
        return {
            'execution_time': execution_time,
            'file_path': file_path,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'passed_rate': passed_rate,
            'failed_rate': failed_rate,
            'skipped_rate': skipped_rate,
            'categories': categories,
            'sheets': sheets
        }
    
    def _extract_test_categories(self, content: str) -> Dict[str, Dict[str, int]]:
        """Extract test results by category from report content."""
        categories = defaultdict(lambda: {'passed': 0, 'failed': 0, 'skipped': 0})
        
        # This is a simplified parser - in a real implementation, you'd want more robust parsing
        test_case_pattern = r'### Test Case ID: ([^\n]+).*?#### Test Case: ([^\n]+).*?#### Status: (PASSED|FAILED|SKIPPED)'
        matches = re.findall(test_case_pattern, content, re.DOTALL)
        
        for test_id, test_name, status in matches:
            # Try to determine category from test name or ID
            category = self._determine_category(test_id, test_name)
            categories[category][status.lower()] += 1
        
        return dict(categories)
    
    def _extract_sheet_data(self, content: str) -> Dict[str, Dict[str, int]]:
        """Extract test results by sheet from report content."""
        sheets = defaultdict(lambda: {'passed': 0, 'failed': 0, 'skipped': 0})
        
        # Extract data by sheet sections
        sheet_sections = re.findall(r'## Data from ([^:]+):(.*?)(?=## |$)', content, re.DOTALL)
        
        for sheet_name, section_content in sheet_sections:
            sheet_name = sheet_name.strip()
            test_results = re.findall(r'#### Status: (PASSED|FAILED|SKIPPED)', section_content)
            
            for status in test_results:
                sheets[sheet_name][status.lower()] += 1
        
        return dict(sheets)
    
    def _determine_category(self, test_id: str, test_name: str) -> str:
        """Determine test category from test ID or name."""
        test_name_lower = test_name.lower()
        test_id_lower = test_id.lower()
        
        if 'setup' in test_name_lower or 'environment' in test_name_lower:
            return 'SETUP'
        elif 'config' in test_name_lower:
            return 'CONFIGURATION'
        elif 'credential' in test_name_lower or 'security' in test_name_lower:
            return 'SECURITY'
        elif 'connect' in test_name_lower:
            return 'CONNECTION'
        elif 'quer' in test_name_lower:
            return 'QUERIES'
        elif 'exist' in test_name_lower:
            return 'TABLE_EXISTS'
        elif 'select' in test_name_lower:
            return 'TABLE_SELECT'
        elif 'data' in test_name_lower and 'has' in test_name_lower:
            return 'TABLE_ROWS'
        elif 'structure' in test_name_lower:
            return 'TABLE_STRUCTURE'
        elif 'schema' in test_name_lower or 'validation' in test_name_lower:
            return 'DATAVALIDATION'
        else:
            return 'OTHER'
    
    def generate_trends_analysis(self) -> Dict:
        """Generate comprehensive trends analysis."""
        if not self.historical_data:
            self.parse_historical_reports()
        
        if not self.historical_data:
            return {'error': 'No historical data available'}
        
        trends = {
            'summary': self._generate_summary_stats(),
            'hourly': self._generate_hourly_trends(),
            'daily': self._generate_daily_trends(),
            'weekly': self._generate_weekly_trends(),
            'monthly': self._generate_monthly_trends(),
            'yearly': self._generate_yearly_trends(),
            'category_trends': self._generate_category_trends(),
            'sheet_trends': self._generate_sheet_trends(),
            'performance_insights': self._generate_performance_insights()
        }
        
        self.trends_data = trends
        return trends
    
    def _generate_summary_stats(self) -> Dict:
        """Generate overall summary statistics."""
        if not self.historical_data:
            return {}
        
        total_executions = len(self.historical_data)
        latest_execution = max(self.historical_data, key=lambda x: x['execution_time'])
        earliest_execution = min(self.historical_data, key=lambda x: x['execution_time'])
        
        avg_success_rate = sum(d['passed_rate'] for d in self.historical_data) / total_executions
        avg_failure_rate = sum(d['failed_rate'] for d in self.historical_data) / total_executions
        avg_skip_rate = sum(d['skipped_rate'] for d in self.historical_data) / total_executions
        
        return {
            'total_executions': total_executions,
            'date_range': {
                'start': earliest_execution['execution_time'].isoformat(),
                'end': latest_execution['execution_time'].isoformat()
            },
            'average_success_rate': round(avg_success_rate, 2),
            'average_failure_rate': round(avg_failure_rate, 2),
            'average_skip_rate': round(avg_skip_rate, 2),
            'latest_execution': {
                'timestamp': latest_execution['execution_time'].isoformat(),
                'success_rate': latest_execution['passed_rate'],
                'total_tests': latest_execution['total_tests']
            }
        }
    
    def _generate_hourly_trends(self) -> Dict:
        """Generate hourly execution trends."""
        hourly_data = defaultdict(list)
        
        for data in self.historical_data:
            hour = data['execution_time'].hour
            hourly_data[hour].append(data)
        
        hourly_stats = {}
        for hour, executions in hourly_data.items():
            if executions:
                avg_success = sum(e['passed_rate'] for e in executions) / len(executions)
                hourly_stats[f"{hour:02d}:00"] = {
                    'executions': len(executions),
                    'avg_success_rate': round(avg_success, 2),
                    'total_tests': sum(e['total_tests'] for e in executions)
                }
        
        return hourly_stats
    
    def _generate_daily_trends(self) -> Dict:
        """Generate daily execution trends."""
        daily_data = defaultdict(list)
        
        for data in self.historical_data:
            date_key = data['execution_time'].strftime('%Y-%m-%d')
            daily_data[date_key].append(data)
        
        daily_stats = {}
        for date, executions in daily_data.items():
            if executions:
                avg_success = sum(e['passed_rate'] for e in executions) / len(executions)
                daily_stats[date] = {
                    'executions': len(executions),
                    'avg_success_rate': round(avg_success, 2),
                    'total_tests': sum(e['total_tests'] for e in executions),
                    'best_run': max(executions, key=lambda x: x['passed_rate'])['passed_rate'],
                    'worst_run': min(executions, key=lambda x: x['passed_rate'])['passed_rate']
                }
        
        return daily_stats
    
    def _generate_weekly_trends(self) -> Dict:
        """Generate weekly execution trends."""
        weekly_data = defaultdict(list)
        
        for data in self.historical_data:
            # Get week start (Monday)
            week_start = data['execution_time'] - timedelta(days=data['execution_time'].weekday())
            week_key = week_start.strftime('%Y-W%U')
            weekly_data[week_key].append(data)
        
        weekly_stats = {}
        for week, executions in weekly_data.items():
            if executions:
                avg_success = sum(e['passed_rate'] for e in executions) / len(executions)
                weekly_stats[week] = {
                    'executions': len(executions),
                    'avg_success_rate': round(avg_success, 2),
                    'total_tests': sum(e['total_tests'] for e in executions)
                }
        
        return weekly_stats
    
    def _generate_monthly_trends(self) -> Dict:
        """Generate monthly execution trends."""
        monthly_data = defaultdict(list)
        
        for data in self.historical_data:
            month_key = data['execution_time'].strftime('%Y-%m')
            monthly_data[month_key].append(data)
        
        monthly_stats = {}
        for month, executions in monthly_data.items():
            if executions:
                avg_success = sum(e['passed_rate'] for e in executions) / len(executions)
                monthly_stats[month] = {
                    'executions': len(executions),
                    'avg_success_rate': round(avg_success, 2),
                    'total_tests': sum(e['total_tests'] for e in executions)
                }
        
        return monthly_stats
    
    def _generate_yearly_trends(self) -> Dict:
        """Generate yearly execution trends."""
        yearly_data = defaultdict(list)
        
        for data in self.historical_data:
            year_key = str(data['execution_time'].year)
            yearly_data[year_key].append(data)
        
        yearly_stats = {}
        for year, executions in yearly_data.items():
            if executions:
                avg_success = sum(e['passed_rate'] for e in executions) / len(executions)
                yearly_stats[year] = {
                    'executions': len(executions),
                    'avg_success_rate': round(avg_success, 2),
                    'total_tests': sum(e['total_tests'] for e in executions)
                }
        
        return yearly_stats
    
    def _generate_category_trends(self) -> Dict:
        """Generate category-wise trends over time."""
        category_trends = defaultdict(list)
        
        for data in self.historical_data:
            timestamp = data['execution_time'].isoformat()
            for category, stats in data['categories'].items():
                total = stats['passed'] + stats['failed'] + stats['skipped']
                if total > 0:
                    success_rate = (stats['passed'] / total) * 100
                    category_trends[category].append({
                        'timestamp': timestamp,
                        'success_rate': round(success_rate, 2),
                        'total_tests': total,
                        'passed': stats['passed'],
                        'failed': stats['failed'],
                        'skipped': stats['skipped']
                    })
        
        return dict(category_trends)
    
    def _generate_sheet_trends(self) -> Dict:
        """Generate sheet-wise trends over time."""
        sheet_trends = defaultdict(list)
        
        for data in self.historical_data:
            timestamp = data['execution_time'].isoformat()
            for sheet, stats in data['sheets'].items():
                total = stats['passed'] + stats['failed'] + stats['skipped']
                if total > 0:
                    success_rate = (stats['passed'] / total) * 100
                    sheet_trends[sheet].append({
                        'timestamp': timestamp,
                        'success_rate': round(success_rate, 2),
                        'total_tests': total,
                        'passed': stats['passed'],
                        'failed': stats['failed'],
                        'skipped': stats['skipped']
                    })
        
        return dict(sheet_trends)
    
    def _generate_performance_insights(self) -> Dict:
        """Generate performance insights and recommendations."""
        if len(self.historical_data) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Calculate recent vs historical performance
        recent_data = self.historical_data[-5:] if len(self.historical_data) >= 5 else self.historical_data[-2:]
        historical_data = self.historical_data[:-len(recent_data)]
        
        recent_avg = sum(d['passed_rate'] for d in recent_data) / len(recent_data)
        historical_avg = sum(d['passed_rate'] for d in historical_data) / len(historical_data) if historical_data else recent_avg
        
        trend_direction = "improving" if recent_avg > historical_avg else "declining" if recent_avg < historical_avg else "stable"
        trend_magnitude = abs(recent_avg - historical_avg)
        
        # Identify best and worst performing periods
        best_execution = max(self.historical_data, key=lambda x: x['passed_rate'])
        worst_execution = min(self.historical_data, key=lambda x: x['passed_rate'])
        
        # Find most problematic categories
        category_issues = defaultdict(int)
        for data in self.historical_data:
            for category, stats in data['categories'].items():
                category_issues[category] += stats['failed']
        
        most_problematic = sorted(category_issues.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'trend_direction': trend_direction,
            'trend_magnitude': round(trend_magnitude, 2),
            'recent_avg_success': round(recent_avg, 2),
            'historical_avg_success': round(historical_avg, 2),
            'best_execution': {
                'timestamp': best_execution['execution_time'].isoformat(),
                'success_rate': best_execution['passed_rate']
            },
            'worst_execution': {
                'timestamp': worst_execution['execution_time'].isoformat(),
                'success_rate': worst_execution['passed_rate']
            },
            'most_problematic_categories': [{'category': cat, 'total_failures': failures} for cat, failures in most_problematic]
        }
    
    def export_trends_data(self, output_file: str = None) -> str:
        """Export trends data to JSON file."""
        if not self.trends_data:
            self.generate_trends_analysis()
        
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"output/Test_Trends_Analysis_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.trends_data, f, indent=2, default=str)
        
        return output_file