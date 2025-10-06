import os
import datetime
import json
from typing import Dict, List, Any


class HTMLReportGenerator:
    """
    A class for generating attractive, responsive HTML reports with Bootstrap styling.
    """

    def __init__(self, title="Test Execution Report", output_file="report.html"):
        self.title = title
        self.output_file = output_file
        self.test_results = []
        self.summary_stats = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0
        }
        self.sheets_data = {}
        self.markdown_report_filename = None  # Store markdown report filename for linking

    def set_markdown_report_filename(self, filename: str):
        """Set the markdown report filename for linking."""
        self.markdown_report_filename = filename

    def add_test_result(self, sheet_name: str, test_case_id: str, test_case_name: str, 
                       status: str, category: str = "", execution_time: str = "", 
                       error_message: str = "", failure_details: str = "", 
                       soft_failures: List[str] = None, hard_failures: List[str] = None):
        """Add a test result to the report with enhanced failure details."""
        test_result = {
            'sheet_name': sheet_name,
            'test_case_id': test_case_id,
            'test_case_name': test_case_name,
            'status': status.upper(),
            'category': category,
            'execution_time': execution_time,
            'error_message': error_message,
            'failure_details': failure_details,
            'soft_failures': soft_failures or [],
            'hard_failures': hard_failures or [],
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.test_results.append(test_result)
        
        # Update summary stats
        self.summary_stats['total'] += 1
        if status.upper() == 'PASSED':
            self.summary_stats['passed'] += 1
        elif status.upper() == 'FAILED':
            self.summary_stats['failed'] += 1
        elif status.upper() == 'SKIPPED':
            self.summary_stats['skipped'] += 1

        # Group by sheet
        if sheet_name not in self.sheets_data:
            self.sheets_data[sheet_name] = []
        self.sheets_data[sheet_name].append(test_result)

    def _get_status_badge(self, status: str) -> str:
        """Return Bootstrap badge HTML for status."""
        badge_map = {
            'PASSED': '<span class="badge bg-success"><i class="fas fa-check-circle"></i> PASSED</span>',
            'FAILED': '<span class="badge bg-danger"><i class="fas fa-times-circle"></i> FAILED</span>',
            'SKIPPED': '<span class="badge bg-warning"><i class="fas fa-minus-circle"></i> SKIPPED</span>'
        }
        return badge_map.get(status.upper(), f'<span class="badge bg-secondary">{status}</span>')

    def _get_progress_bar(self, passed: int, failed: int, skipped: int, total: int) -> str:
        """Generate progress bar HTML."""
        if total == 0:
            return '<div class="progress"><div class="progress-bar bg-secondary" style="width: 100%">No Tests</div></div>'
        
        passed_pct = (passed / total) * 100
        failed_pct = (failed / total) * 100
        skipped_pct = (skipped / total) * 100
        
        return f"""
        <div class="progress" style="height: 25px;">
            <div class="progress-bar bg-success" style="width: {passed_pct}%" title="Passed: {passed} ({passed_pct:.1f}%)">
                {passed} Passed
            </div>
            <div class="progress-bar bg-danger" style="width: {failed_pct}%" title="Failed: {failed} ({failed_pct:.1f}%)">
                {failed} Failed
            </div>
            <div class="progress-bar bg-warning" style="width: {skipped_pct}%" title="Skipped: {skipped} ({skipped_pct:.1f}%)">
                {skipped} Skipped
            </div>
        </div>
        """

    def _get_failure_details_html(self, test: Dict[str, Any]) -> str:
        """Generate failure details HTML with soft/hard failure indicators."""
        details_html = ""
        
        # Handle PASSED tests with soft failures (warnings)
        if test['status'] == 'PASSED' and test['soft_failures']:
            details_html += '<div class="text-warning small">'
            details_html += f'<i class="fas fa-exclamation-triangle"></i> {len(test["soft_failures"])} warnings<br>'
            for failure in test['soft_failures'][:3]:  # Show first 3
                details_html += f'• {failure}<br>'
            if len(test['soft_failures']) > 3:
                details_html += f'... and {len(test["soft_failures"]) - 3} more'
            details_html += '</div>'
        
        # Handle FAILED tests
        elif test['status'] == 'FAILED':
            if test['hard_failures']:
                details_html += '<div class="text-danger small">'
                details_html += f'<i class="fas fa-times-circle"></i> {len(test["hard_failures"])} critical issues<br>'
                for failure in test['hard_failures'][:2]:  # Show first 2
                    details_html += f'• {failure}<br>'
                if len(test['hard_failures']) > 2:
                    details_html += f'... and {len(test["hard_failures"]) - 2} more'
                details_html += '</div>'
            elif test['failure_details']:
                details_html += f'<div class="text-danger small">{test["failure_details"]}</div>'
            elif test['error_message']:
                details_html += f'<div class="text-danger small">{test["error_message"]}</div>'
        
        # Handle SKIPPED tests
        elif test['status'] == 'SKIPPED':
            details_html = '<span class="text-muted small">Test was skipped</span>'
        
        # Default for PASSED without issues
        else:
            details_html = '<span class="text-success small"><i class="fas fa-check"></i> No issues</span>'
        
        return details_html

    def _generate_chart_data(self) -> str:
        """Generate JavaScript data for charts."""
        # Overall status chart
        chart_data = {
            'labels': ['Passed', 'Failed', 'Skipped'],
            'datasets': [{
                'data': [self.summary_stats['passed'], self.summary_stats['failed'], self.summary_stats['skipped']],
                'backgroundColor': ['#28a745', '#dc3545', '#ffc107'],
                'borderWidth': 2
            }]
        }
        
        # Category breakdown
        category_stats = {}
        for result in self.test_results:
            category = result['category'] or 'Unknown'
            if category not in category_stats:
                category_stats[category] = {'passed': 0, 'failed': 0, 'skipped': 0}
            category_stats[category][result['status'].lower()] += 1

        category_chart_data = {
            'labels': list(category_stats.keys()),
            'datasets': [
                {
                    'label': 'Passed',
                    'data': [category_stats[cat]['passed'] for cat in category_stats],
                    'backgroundColor': '#28a745'
                },
                {
                    'label': 'Failed', 
                    'data': [category_stats[cat]['failed'] for cat in category_stats],
                    'backgroundColor': '#dc3545'
                },
                {
                    'label': 'Skipped',
                    'data': [category_stats[cat]['skipped'] for cat in category_stats],
                    'backgroundColor': '#ffc107'
                }
            ]
        }

        return f"""
        const overallData = {json.dumps(chart_data)};
        const categoryData = {json.dumps(category_chart_data)};
        """

    def generate_html(self) -> str:
        """Generate the complete HTML report."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate percentages
        total = self.summary_stats['total']
        passed_pct = (self.summary_stats['passed'] / total * 100) if total > 0 else 0
        failed_pct = (self.summary_stats['failed'] / total * 100) if total > 0 else 0
        skipped_pct = (self.summary_stats['skipped'] / total * 100) if total > 0 else 0

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .status-passed {{ color: #28a745; }}
        .status-failed {{ color: #dc3545; }}
        .status-skipped {{ color: #ffc107; }}
        .test-card {{ transition: all 0.3s ease; }}
        .test-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
        .summary-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .chart-container {{ position: relative; height: 300px; }}
        .table-container {{ max-height: 500px; overflow-y: auto; }}
        .category-filter {{ cursor: pointer; }}
        .category-filter:hover {{ background-color: #f8f9fa; }}
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-primary">
        <div class="container">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-line"></i> {self.title}
            </span>
            <div class="navbar-nav">
                {f'<a class="nav-link text-white" href="{self.markdown_report_filename}" target="_blank"><i class="fas fa-file-text"></i> Detailed MD Report</a>' if self.markdown_report_filename else ''}
                <span class="navbar-text text-white ms-3">
                    <i class="fas fa-clock"></i> Generated: {timestamp}
                </span>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Summary Cards -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center h-100 summary-card">
                    <div class="card-body">
                        <i class="fas fa-list-check fa-2x mb-2"></i>
                        <h4>{total}</h4>
                        <p class="mb-0">Total Tests</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100 bg-success text-white">
                    <div class="card-body">
                        <i class="fas fa-check-circle fa-2x mb-2"></i>
                        <h4>{self.summary_stats['passed']}</h4>
                        <p class="mb-0">Passed ({passed_pct:.1f}%)</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100 bg-danger text-white">
                    <div class="card-body">
                        <i class="fas fa-times-circle fa-2x mb-2"></i>
                        <h4>{self.summary_stats['failed']}</h4>
                        <p class="mb-0">Failed ({failed_pct:.1f}%)</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100 bg-warning text-white">
                    <div class="card-body">
                        <i class="fas fa-minus-circle fa-2x mb-2"></i>
                        <h4>{self.summary_stats['skipped']}</h4>
                        <p class="mb-0">Skipped ({skipped_pct:.1f}%)</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Progress Bar -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-bar"></i> Overall Test Results</h5>
                    </div>
                    <div class="card-body">
                        {self._get_progress_bar(self.summary_stats['passed'], self.summary_stats['failed'], self.summary_stats['skipped'], total)}
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts -->
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-pie-chart"></i> Status Distribution</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="statusChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-bar-chart"></i> Results by Category</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Test Results by Sheet -->
        """

        # Add test results by sheet
        for sheet_name, tests in self.sheets_data.items():
            sheet_passed = sum(1 for test in tests if test['status'] == 'PASSED')
            sheet_failed = sum(1 for test in tests if test['status'] == 'FAILED')
            sheet_skipped = sum(1 for test in tests if test['status'] == 'SKIPPED')
            sheet_total = len(tests)

            html_content += f"""
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-file-alt"></i> {sheet_name} 
                            <small class="text-muted">({sheet_total} tests)</small>
                        </h5>
                        <div>
                            {self._get_progress_bar(sheet_passed, sheet_failed, sheet_skipped, sheet_total)}
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="table-container">
                            <table class="table table-hover">
                                <thead class="table-dark">
                                    <tr>
                                        <th>Test ID</th>
                                        <th>Test Case</th>
                                        <th>Category</th>
                                        <th>Status</th>
                                        <th>Details</th>
                                        <th>Timestamp</th>
                                    </tr>
                                </thead>
                                <tbody>
            """

            for test in tests:
                html_content += f"""
                                    <tr class="{'table-success' if test['status'] == 'PASSED' else 'table-danger' if test['status'] == 'FAILED' else 'table-warning'}">
                                        <td><code>{test['test_case_id']}</code></td>
                                        <td>{test['test_case_name']}</td>
                                        <td>
                                            <span class="badge bg-info">{test['category']}</span>
                                        </td>
                                        <td>{self._get_status_badge(test['status'])}</td>
                                        <td>{self._get_failure_details_html(test)}</td>
                                        <td><small class="text-muted">{test['timestamp']}</small></td>
                                    </tr>
                """

            html_content += """
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
            """

        # Close HTML
        html_content += f"""
    </div>

    <footer class="bg-dark text-light text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0">
                <i class="fas fa-database"></i> Cross Database Validator Report | 
                Generated on {timestamp} | 
                <i class="fas fa-check"></i> {self.summary_stats['passed']} Passed | 
                <i class="fas fa-times"></i> {self.summary_stats['failed']} Failed | 
                <i class="fas fa-minus"></i> {self.summary_stats['skipped']} Skipped
            </p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        {self._generate_chart_data()}
        
        // Status Chart (Pie Chart)
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        const statusChart = new Chart(statusCtx, {{
            type: 'doughnut',
            data: overallData,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                    }},
                    title: {{
                        display: true,
                        text: 'Test Status Distribution'
                    }}
                }}
            }}
        }});

        // Category Chart (Bar Chart)
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        const categoryChart = new Chart(categoryCtx, {{
            type: 'bar',
            data: categoryData,
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        stacked: true,
                    }},
                    y: {{
                        stacked: true,
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'bottom',
                    }},
                    title: {{
                        display: true,
                        text: 'Test Results by Category'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
        """

        return html_content

    def save(self) -> bool:
        """Save the HTML report to file."""
        try:
            html_content = self.generate_html()
            output_path = os.path.abspath(self.output_file)
            
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print(f"🎉 HTML Report saved successfully to: `{output_path}`")
            return True
        except Exception as e:
            print(f"🛑 Error saving HTML report: {e}")
            return False