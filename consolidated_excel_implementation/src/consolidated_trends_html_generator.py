#!/usr/bin/env python3
"""
Consolidated Test Execution Trends HTML Generator

Generates comprehensive HTML reports with interactive visualizations for 
consolidated Excel test execution data. Includes metrics, trends, and analytics.

Features:
1. Test distribution by type, category, priority
2. Environment distribution analysis
3. Parameter usage statistics (tolerance, expected columns)
4. Interactive charts with Chart.js
5. Detailed metrics tables
6. Export capabilities
7. Responsive design with modern CSS
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd


class ConsolidatedTrendsHTMLGenerator:
    """Generate comprehensive HTML trends reports for consolidated test data."""
    
    def __init__(self, test_data: pd.DataFrame, output_dir: str = "output"):
        """
        Initialize the trends generator.
        
        Args:
            test_data: DataFrame containing consolidated test case data
            output_dir: Directory to save HTML reports
        """
        self.test_data = test_data
        self.output_dir = output_dir
        self.report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate analytics
        self.analytics = self._generate_analytics()
    
    def _generate_analytics(self) -> Dict:
        """Generate comprehensive analytics from test data."""
        analytics = {
            'total_tests': len(self.test_data),
            'enabled_tests': len(self.test_data[self.test_data['Enable'] == True]),
            'disabled_tests': len(self.test_data[self.test_data['Enable'] == False]),
            'test_types': {},
            'categories': {},
            'priorities': {},
            'environments': {'source': {}, 'target': {}},
            'parameters': {
                'with_tolerance': 0,
                'with_expected_cols': 0,
                'parameter_types': {}
            },
            'tables': {'source_tables': set(), 'target_tables': set()},
            'execution_readiness': {
                'complete_configs': 0,
                'missing_configs': 0
            }
        }
        
        # Analyze each test case
        for _, test in self.test_data.iterrows():
            # Test type distribution
            test_type = test.get('TEST_TYPE', 'Unknown')
            analytics['test_types'][test_type] = analytics['test_types'].get(test_type, 0) + 1
            
            # Category distribution
            category = test.get('Test_Category', 'Unknown')
            analytics['categories'][category] = analytics['categories'].get(category, 0) + 1
            
            # Priority distribution
            priority = test.get('Priority', 'Unknown')
            analytics['priorities'][priority] = analytics['priorities'].get(priority, 0) + 1
            
            # Environment distribution
            src_env = test.get('SRC_Environment_Name', 'Unknown')
            tgt_env = test.get('TGT_Environment_Name', 'Unknown')
            analytics['environments']['source'][src_env] = analytics['environments']['source'].get(src_env, 0) + 1
            analytics['environments']['target'][tgt_env] = analytics['environments']['target'].get(tgt_env, 0) + 1
            
            # Parameter analysis - use the pre-parsed fields
            if test.get('has_tolerance', False):
                analytics['parameters']['with_tolerance'] += 1
            if test.get('has_expected_cols', False):
                analytics['parameters']['with_expected_cols'] += 1
            
            # Parse parameter types from parsed_parameters
            parsed_params = test.get('parsed_parameters', {})
            if isinstance(parsed_params, dict):
                for param_name in parsed_params.keys():
                    analytics['parameters']['parameter_types'][param_name] = \
                        analytics['parameters']['parameter_types'].get(param_name, 0) + 1
            
            # Table analysis
            src_table = test.get('SRC_Table_Name', '')
            tgt_table = test.get('TGT_Table_Name', '')
            if src_table and str(src_table) != 'nan':
                analytics['tables']['source_tables'].add(src_table)
            if tgt_table and str(tgt_table) != 'nan':
                analytics['tables']['target_tables'].add(tgt_table)
            
            # Execution readiness
            if self._is_complete_config(test):
                analytics['execution_readiness']['complete_configs'] += 1
            else:
                analytics['execution_readiness']['missing_configs'] += 1
        
        # Convert sets to lists for JSON serialization
        analytics['tables']['source_tables'] = list(analytics['tables']['source_tables'])
        analytics['tables']['target_tables'] = list(analytics['tables']['target_tables'])
        
        return analytics
    
    def _is_complete_config(self, test: pd.Series) -> bool:
        """Check if test has complete configuration."""
        required_fields = ['Test_Case_ID', 'Test_Case_Name', 'TEST_TYPE', 'Test_Category']
        return all(test.get(field) and str(test.get(field)).strip() and str(test.get(field)) != 'nan' for field in required_fields)
    
    def generate_html_report(self, filename: Optional[str] = None) -> str:
        """Generate comprehensive HTML trends report."""
        if not filename:
            filename = f"consolidated_trends_report_{self.report_timestamp}.html"
        
        filepath = os.path.join(self.output_dir, filename)
        
        html_content = self._build_html_content()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _build_html_content(self) -> str:
        """Build the complete HTML content."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consolidated Test Execution Trends - {self.report_timestamp}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        {self._build_header()}
        {self._build_summary_section()}
        {self._build_charts_section()}
        {self._build_detailed_metrics()}
        {self._build_data_tables()}
        {self._build_footer()}
    </div>
    
    <script>
        {self._build_javascript()}
    </script>
</body>
</html>"""
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            margin-top: 20px;
            margin-bottom: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px 0;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 10px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
        }
        
        .summary-card h3 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .summary-card p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .charts-section {
            margin-bottom: 40px;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        
        .chart-container h3 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
            font-size: 1.3em;
        }
        
        .chart-wrapper {
            position: relative;
            height: 300px;
        }
        
        .metrics-section {
            margin-bottom: 40px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .metric-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #007bff;
        }
        
        .metric-card h4 {
            color: #007bff;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .metric-list {
            list-style: none;
        }
        
        .metric-list li {
            padding: 5px 0;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
        }
        
        .metric-list li:last-child {
            border-bottom: none;
        }
        
        .data-tables {
            margin-bottom: 40px;
        }
        
        .table-container {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .table-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            font-weight: bold;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            color: #666;
            margin-top: 40px;
        }
        
        .error-message {
            background: #ff6b6b;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
        }
        
        .section-title {
            font-size: 2em;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        
        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .summary-grid {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2em;
            }
        }
        """
    
    def _build_header(self) -> str:
        """Build the header section."""
        return f"""
        <div class="header">
            <h1>🚀 Consolidated Test Execution Trends</h1>
            <p>Comprehensive Analytics Dashboard - Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        """
    
    def _build_summary_section(self) -> str:
        """Build the summary cards section."""
        analytics = self.analytics
        
        return f"""
        <div class="summary-grid">
            <div class="summary-card">
                <h3>{analytics['total_tests']}</h3>
                <p>Total Test Cases</p>
            </div>
            <div class="summary-card">
                <h3>{analytics['enabled_tests']}</h3>
                <p>Enabled Tests</p>
            </div>
            <div class="summary-card">
                <h3>{len(analytics['test_types'])}</h3>
                <p>Test Types</p>
            </div>
            <div class="summary-card">
                <h3>{len(analytics['categories'])}</h3>
                <p>Categories</p>
            </div>
            <div class="summary-card">
                <h3>{analytics['parameters']['with_tolerance']}</h3>
                <p>With Tolerance</p>
            </div>
            <div class="summary-card">
                <h3>{analytics['parameters']['with_expected_cols']}</h3>
                <p>Expected Columns</p>
            </div>
        </div>
        """
    
    def _build_charts_section(self) -> str:
        """Build the charts section."""
        return f"""
        <h2 class="section-title">📊 Visual Analytics</h2>
        <div class="charts-section">
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Test Type Distribution</h3>
                    <div class="chart-wrapper">
                        <canvas id="testTypeChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <h3>Category Distribution</h3>
                    <div class="chart-wrapper">
                        <canvas id="categoryChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <h3>Priority Distribution</h3>
                    <div class="chart-wrapper">
                        <canvas id="priorityChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <h3>Environment Distribution</h3>
                    <div class="chart-wrapper">
                        <canvas id="environmentChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <h3>Parameter Usage</h3>
                    <div class="chart-wrapper">
                        <canvas id="parameterChart"></canvas>
                    </div>
                </div>
                <div class="chart-container">
                    <h3>Execution Readiness</h3>
                    <div class="chart-wrapper">
                        <canvas id="readinessChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _build_detailed_metrics(self) -> str:
        """Build the detailed metrics section."""
        analytics = self.analytics
        
        # Format parameter types
        param_types_html = ""
        for param, count in sorted(analytics['parameters']['parameter_types'].items(), 
                                 key=lambda x: x[1], reverse=True)[:10]:
            param_types_html += f"<li><span>{param}</span><span>{count}</span></li>"
        
        # Format environments
        src_env_html = ""
        for env, count in sorted(analytics['environments']['source'].items(), 
                               key=lambda x: x[1], reverse=True):
            src_env_html += f"<li><span>{env}</span><span>{count}</span></li>"
        
        tgt_env_html = ""
        for env, count in sorted(analytics['environments']['target'].items(), 
                               key=lambda x: x[1], reverse=True):
            tgt_env_html += f"<li><span>{env}</span><span>{count}</span></li>"
        
        return f"""
        <h2 class="section-title">📈 Detailed Metrics</h2>
        <div class="metrics-section">
            <div class="metrics-grid">
                <div class="metric-card">
                    <h4>Top Parameter Types</h4>
                    <ul class="metric-list">
                        {param_types_html}
                    </ul>
                </div>
                <div class="metric-card">
                    <h4>Source Environments</h4>
                    <ul class="metric-list">
                        {src_env_html}
                    </ul>
                </div>
                <div class="metric-card">
                    <h4>Target Environments</h4>
                    <ul class="metric-list">
                        {tgt_env_html}
                    </ul>
                </div>
                <div class="metric-card">
                    <h4>Table Coverage</h4>
                    <ul class="metric-list">
                        <li><span>Source Tables</span><span>{len(analytics['tables']['source_tables'])}</span></li>
                        <li><span>Target Tables</span><span>{len(analytics['tables']['target_tables'])}</span></li>
                        <li><span>Unique Tables</span><span>{len(set(analytics['tables']['source_tables'] + analytics['tables']['target_tables']))}</span></li>
                    </ul>
                </div>
            </div>
        </div>
        """
    
    def _build_data_tables(self) -> str:
        """Build the data tables section."""
        # Create test type breakdown table
        test_type_rows = ""
        for test_type, count in sorted(self.analytics['test_types'].items(), 
                                     key=lambda x: x[1], reverse=True):
            percentage = (count / self.analytics['total_tests']) * 100
            test_type_rows += f"""
            <tr>
                <td>{test_type}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>"""
        
        # Create category breakdown table
        category_rows = ""
        for category, count in sorted(self.analytics['categories'].items(), 
                                    key=lambda x: x[1], reverse=True):
            percentage = (count / self.analytics['total_tests']) * 100
            category_rows += f"""
            <tr>
                <td>{category}</td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>"""
        
        return f"""
        <h2 class="section-title">📋 Data Breakdown</h2>
        <div class="data-tables">
            <div class="table-container">
                <div class="table-header">Test Type Distribution</div>
                <table>
                    <thead>
                        <tr>
                            <th>Test Type</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {test_type_rows}
                    </tbody>
                </table>
            </div>
            
            <div class="table-container">
                <div class="table-header">Category Distribution</div>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Count</th>
                            <th>Percentage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {category_rows}
                    </tbody>
                </table>
            </div>
        </div>
        """
    
    def _build_footer(self) -> str:
        """Build the footer section."""
        return f"""
        <div class="footer">
            <p>Report generated by Consolidated Test Execution Trends Analyzer</p>
            <p>Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M:%S %p')}</p>
            <p>Total test cases analyzed: {self.analytics['total_tests']}</p>
        </div>
        """
    
    def _build_javascript(self) -> str:
        """Build JavaScript for interactive charts."""
        return f"""
        // Chart.js error handling
        function checkChartJsLoaded() {{
            if (typeof Chart === 'undefined') {{
                document.querySelectorAll('.chart-wrapper').forEach(wrapper => {{
                    wrapper.innerHTML = '<div class="error-message">Chart.js failed to load. Please check your internet connection.</div>';
                }});
                return false;
            }}
            return true;
        }}
        
        // Chart configurations
        const chartConfig = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{
                legend: {{
                    position: 'bottom'
                }}
            }}
        }};
        
        // Initialize charts when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            if (!checkChartJsLoaded()) return;
            
            // Test Type Distribution Chart
            const testTypeCtx = document.getElementById('testTypeChart').getContext('2d');
            new Chart(testTypeCtx, {{
                type: 'doughnut',
                data: {{
                    labels: {json.dumps(list(self.analytics['test_types'].keys()))},
                    datasets: [{{
                        data: {json.dumps(list(self.analytics['test_types'].values()))},
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
                    }}]
                }},
                options: chartConfig
            }});
            
            // Category Distribution Chart
            const categoryCtx = document.getElementById('categoryChart').getContext('2d');
            new Chart(categoryCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(list(self.analytics['categories'].keys()))},
                    datasets: [{{
                        label: 'Count',
                        data: {json.dumps(list(self.analytics['categories'].values()))},
                        backgroundColor: '#36A2EB'
                    }}]
                }},
                options: {{
                    ...chartConfig,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            
            // Priority Distribution Chart
            const priorityCtx = document.getElementById('priorityChart').getContext('2d');
            new Chart(priorityCtx, {{
                type: 'pie',
                data: {{
                    labels: {json.dumps(list(self.analytics['priorities'].keys()))},
                    datasets: [{{
                        data: {json.dumps(list(self.analytics['priorities'].values()))},
                        backgroundColor: ['#FF6384', '#FFCE56', '#4BC0C0', '#9966FF']
                    }}]
                }},
                options: chartConfig
            }});
            
            // Environment Distribution Chart
            const environmentCtx = document.getElementById('environmentChart').getContext('2d');
            new Chart(environmentCtx, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(list(self.analytics['environments']['source'].keys()))},
                    datasets: [{{
                        label: 'Source Environments',
                        data: {json.dumps(list(self.analytics['environments']['source'].values()))},
                        backgroundColor: '#FF6384'
                    }}, {{
                        label: 'Target Environments',
                        data: {json.dumps(list(self.analytics['environments']['target'].values()))},
                        backgroundColor: '#36A2EB'
                    }}]
                }},
                options: {{
                    ...chartConfig,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
            
            // Parameter Usage Chart
            const parameterCtx = document.getElementById('parameterChart').getContext('2d');
            new Chart(parameterCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['With Tolerance', 'With Expected Columns', 'Basic Parameters'],
                    datasets: [{{
                        data: [
                            {self.analytics['parameters']['with_tolerance']}, 
                            {self.analytics['parameters']['with_expected_cols']}, 
                            {self.analytics['total_tests'] - self.analytics['parameters']['with_tolerance'] - self.analytics['parameters']['with_expected_cols']}
                        ],
                        backgroundColor: ['#FFCE56', '#4BC0C0', '#9966FF']
                    }}]
                }},
                options: chartConfig
            }});
            
            // Execution Readiness Chart
            const readinessCtx = document.getElementById('readinessChart').getContext('2d');
            new Chart(readinessCtx, {{
                type: 'doughnut',
                data: {{
                    labels: ['Complete Config', 'Missing Config'],
                    datasets: [{{
                        data: [
                            {self.analytics['execution_readiness']['complete_configs']}, 
                            {self.analytics['execution_readiness']['missing_configs']}
                        ],
                        backgroundColor: ['#4BC0C0', '#FF6384']
                    }}]
                }},
                options: chartConfig
            }});
        }});
        """
    
    def export_analytics_json(self, filename: Optional[str] = None) -> str:
        """Export analytics data as JSON."""
        if not filename:
            filename = f"consolidated_analytics_{self.report_timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.analytics, f, indent=2, default=str)
        
        return filepath