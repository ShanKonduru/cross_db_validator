import os
import json
from datetime import datetime
from typing import Dict, Any


class EnhancedTrendsHTMLReportGenerator:
    """
    Generates comprehensive interactive HTML reports for test execution trends analysis.
    Features tab-based navigation, drill-down capabilities, and time-series visualizations.
    """
    
    def __init__(self, output_file: str = None):
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_file = f"output/Enhanced_Test_Trends_Report_{timestamp}.html"
        else:
            self.output_file = output_file
    
    def generate_comprehensive_trends_report(self, trends_data: Dict) -> str:
        """
        Generate comprehensive HTML trends report from persistent data.
        
        Args:
            trends_data: Comprehensive trends data from PersistentTrendsAnalyzer
            
        Returns:
            str: Path to the generated HTML report
        """
        print("🌐 Generating comprehensive interactive trends dashboard...")
        
        # Generate HTML content from persistent trends data
        html_content = self._generate_comprehensive_html_content(trends_data)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Save report
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.output_file
    
    def _generate_comprehensive_html_content(self, trends_data: Dict) -> str:
        """Generate comprehensive HTML content from persistent trends data."""
        metadata = trends_data.get('metadata', {})
        overall_trends = trends_data.get('overall_trends', {})
        time_trends = trends_data.get('time_based_trends', {})
        sheet_trends = trends_data.get('sheet_level_trends', {})
        category_trends = trends_data.get('category_level_trends', {})
        individual_trends = trends_data.get('individual_test_trends', {})
        insights = trends_data.get('insights', [])
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📈 Comprehensive Test Execution Trends Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <style>
        body {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        .dashboard-container {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            margin: 20px;
            padding: 30px;
            max-width: 95%;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            margin-bottom: 25px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .nav-tabs .nav-link {{
            border-radius: 10px;
            margin-right: 10px;
            font-weight: 500;
        }}
        
        .nav-tabs .nav-link.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: transparent;
            color: white;
        }}
        
        .table-container {{
            max-height: 400px;
            overflow-y: auto;
            border-radius: 10px;
        }}
        
        .drill-down-btn {{
            cursor: pointer;
            color: #007bff;
            text-decoration: underline;
        }}
        
        .drill-down-btn:hover {{
            color: #0056b3;
        }}
        
        .collapse-content {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-top: 10px;
        }}
        
        .chart-canvas {{
            height: 300px !important;
        }}
        
        .time-chart {{
            height: 400px !important;
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <div class="text-center mb-5">
            <h1 class="display-4 fw-bold text-primary mb-3">
                <i class="fas fa-chart-line me-3"></i>
                Comprehensive Test Execution Trends
            </h1>
            <p class="lead text-muted">
                Interactive drill-down analysis from persistent execution data
            </p>
        </div>

        <!-- Key Metrics Row -->
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="metric-card">
                    <h3><i class="fas fa-play-circle"></i></h3>
                    <h4>{metadata.get('total_executions', 0)}</h4>
                    <p>Total Executions</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <h3><i class="fas fa-calendar-alt"></i></h3>
                    <h4>{metadata.get('date_range', {}).get('span_days', 0)} Days</h4>
                    <p>History Span</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <h3><i class="fas fa-percentage"></i></h3>
                    <h4>{overall_trends.get('overall_passed_rate', 0):.1f}%</h4>
                    <p>Overall Success Rate</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <h3><i class="fas fa-clock"></i></h3>
                    <h4>{overall_trends.get('avg_execution_time_ms', 0):.0f}ms</h4>
                    <p>Avg Execution Time</p>
                </div>
            </div>
        </div>

        <!-- Key Insights -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="chart-container">
                    <h3 class="mb-3"><i class="fas fa-lightbulb text-warning"></i> Key Insights</h3>
                    <div class="row">
                        {''.join([f'<div class="col-md-6"><div class="alert alert-info mb-2">{insight}</div></div>' for insight in insights[:6]])}
                    </div>
                </div>
            </div>
        </div>

        <!-- Navigation Tabs -->
        <ul class="nav nav-tabs mb-4" id="trendTabs" role="tablist">
            <li class="nav-item" role="presentation">
                <button class="nav-link active" id="overview-tab" data-bs-toggle="tab" data-bs-target="#overview" type="button">
                    <i class="fas fa-chart-bar"></i> Overview
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="time-trends-tab" data-bs-toggle="tab" data-bs-target="#time-trends" type="button">
                    <i class="fas fa-chart-line"></i> Time Trends
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="sheets-tab" data-bs-toggle="tab" data-bs-target="#sheets" type="button">
                    <i class="fas fa-layer-group"></i> Sheets Analysis
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="categories-tab" data-bs-toggle="tab" data-bs-target="#categories" type="button">
                    <i class="fas fa-tags"></i> Categories
                </button>
            </li>
            <li class="nav-item" role="presentation">
                <button class="nav-link" id="individual-tab" data-bs-toggle="tab" data-bs-target="#individual" type="button">
                    <i class="fas fa-list"></i> Individual Tests
                </button>
            </li>
        </ul>

        <!-- Tab Content -->
        <div class="tab-content" id="trendTabsContent">
            <!-- Overview Tab -->
            <div class="tab-pane fade show active" id="overview" role="tabpanel">
                <div class="row">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h4><i class="fas fa-layer-group text-success"></i> Sheet Performance Overview</h4>
                            <canvas id="sheetOverviewChart" class="chart-canvas"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h4><i class="fas fa-tags text-warning"></i> Category Distribution</h4>
                            <canvas id="categoryOverviewChart" class="chart-canvas"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Time Trends Tab -->
            <div class="tab-pane fade" id="time-trends" role="tabpanel">
                <div class="row mb-3">
                    <div class="col-12">
                        <div class="chart-container">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h4><i class="fas fa-chart-line text-primary"></i> Execution Trends Over Time</h4>
                                <div class="btn-group" role="group">
                                    <button type="button" class="btn btn-outline-primary btn-sm active" data-timeframe="daily">Daily</button>
                                    <button type="button" class="btn btn-outline-primary btn-sm" data-timeframe="weekly">Weekly</button>
                                    <button type="button" class="btn btn-outline-primary btn-sm" data-timeframe="monthly">Monthly</button>
                                </div>
                            </div>
                            <canvas id="timeTrendsChart" class="time-chart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h4><i class="fas fa-clock text-info"></i> Hourly Execution Pattern</h4>
                            <canvas id="hourlyTrendsChart" class="chart-canvas"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h4><i class="fas fa-calendar-week text-success"></i> Day of Week Pattern</h4>
                            <canvas id="weeklyPatternChart" class="chart-canvas"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sheets Tab -->
            <div class="tab-pane fade" id="sheets" role="tabpanel">
                {self._generate_sheet_analysis_content(sheet_trends)}
            </div>

            <!-- Categories Tab -->
            <div class="tab-pane fade" id="categories" role="tabpanel">
                {self._generate_category_analysis_content(category_trends)}
            </div>

            <!-- Individual Tests Tab -->
            <div class="tab-pane fade" id="individual" role="tabpanel">
                {self._generate_individual_tests_content(individual_trends)}
            </div>
        </div>

        <div class="text-center mt-5 pt-4 border-top">
            <p class="text-muted">
                <i class="fas fa-clock"></i> Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
                <i class="fas fa-database"></i> Persistent Data Source |
                <i class="fas fa-info-circle"></i> Click on charts and tables for detailed drill-down
            </p>
        </div>
    </div>

    <script>
        // Global data
        const trendsData = {json.dumps(trends_data)};
        
        {self._generate_javascript_charts(trends_data)}
    </script>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""
    
    def _generate_sheet_analysis_content(self, sheet_trends: Dict) -> str:
        """Generate detailed sheet analysis content."""
        content = '''
        <div class="row">
            <div class="col-12">
                <div class="chart-container">
                    <h4><i class="fas fa-layer-group text-success"></i> Sheet Performance Analysis</h4>
                    <div class="table-container">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>Sheet Name</th>
                                    <th>Success Rate</th>
                                    <th>Total Executions</th>
                                    <th>Avg Execution Time</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
        '''
        
        for sheet_name, data in sheet_trends.items():
            success_rate = data.get('overall_passed_rate', 0)
            total_exec = data.get('total_executions', 0)
            avg_time = data.get('avg_execution_time_ms', 0)
            
            status_class = 'success' if success_rate >= 90 else 'warning' if success_rate >= 70 else 'danger'
            
            content += f'''
                            <tr>
                                <td><strong>{sheet_name}</strong></td>
                                <td><span class="badge bg-{status_class}">{success_rate:.1f}%</span></td>
                                <td>{total_exec}</td>
                                <td>{avg_time:.0f}ms</td>
                                <td>
                                    <span class="drill-down-btn" data-bs-toggle="collapse" data-bs-target="#sheet-{sheet_name.replace(' ', '_')}">
                                        <i class="fas fa-search-plus"></i> Drill Down
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td colspan="5" class="p-0">
                                    <div class="collapse" id="sheet-{sheet_name.replace(' ', '_')}">
                                        <div class="collapse-content">
                                            <h6>Categories in {sheet_name}:</h6>
                                            <div class="row">
            '''
            
            # Add category breakdown for this sheet
            categories = data.get('categories', {})
            for cat_name, cat_data in categories.items():
                cat_success = cat_data.get('passed_rate', 0)
                cat_class = 'success' if cat_success >= 90 else 'warning' if cat_success >= 70 else 'danger'
                content += f'''
                                                <div class="col-md-4 mb-2">
                                                    <small class="text-muted">{cat_name}</small><br>
                                                    <span class="badge bg-{cat_class}">{cat_success:.1f}%</span>
                                                </div>
                '''
            
            content += '''
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
            '''
        
        content += '''
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        '''
        return content
    
    def _generate_category_analysis_content(self, category_trends: Dict) -> str:
        """Generate detailed category analysis content."""
        content = '''
        <div class="row">
            <div class="col-md-8">
                <div class="chart-container">
                    <h4><i class="fas fa-tags text-warning"></i> Category Performance Detailed Analysis</h4>
                    <div class="table-container">
                        <table class="table table-hover">
                            <thead class="table-dark">
                                <tr>
                                    <th>Category</th>
                                    <th>Success Rate</th>
                                    <th>Total Tests</th>
                                    <th>Executions</th>
                                    <th>Avg Time</th>
                                    <th>Trend</th>
                                </tr>
                            </thead>
                            <tbody>
        '''
        
        for cat_name, data in category_trends.items():
            success_rate = data.get('overall_passed_rate', 0)
            total_tests = data.get('unique_test_count', 0)
            total_exec = data.get('total_executions', 0)
            avg_time = data.get('avg_execution_time_ms', 0)
            
            status_class = 'success' if success_rate >= 90 else 'warning' if success_rate >= 70 else 'danger'
            trend_icon = '📈' if success_rate >= 85 else '📉' if success_rate < 70 else '➡️'
            
            content += f'''
                            <tr>
                                <td><strong>{cat_name}</strong></td>
                                <td><span class="badge bg-{status_class}">{success_rate:.1f}%</span></td>
                                <td>{total_tests}</td>
                                <td>{total_exec}</td>
                                <td>{avg_time:.0f}ms</td>
                                <td>{trend_icon}</td>
                            </tr>
            '''
        
        content += '''
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="chart-container">
                    <h4><i class="fas fa-chart-pie"></i> Category Distribution</h4>
                    <canvas id="categoryDistributionChart" class="chart-canvas"></canvas>
                </div>
            </div>
        </div>
        '''
        return content
    
    def _generate_individual_tests_content(self, individual_trends: Dict) -> str:
        """Generate detailed individual test analysis content."""
        content = '''
        <div class="row">
            <div class="col-12">
                <div class="chart-container">
                    <h4><i class="fas fa-list text-info"></i> Individual Test Performance</h4>
                    <div class="mb-3">
                        <input type="text" class="form-control" id="testFilter" placeholder="🔍 Filter tests by name...">
                    </div>
                    <div class="table-container">
                        <table class="table table-hover table-sm" id="individualTestsTable">
                            <thead class="table-dark">
                                <tr>
                                    <th>Test ID</th>
                                    <th>Category</th>
                                    <th>Sheet</th>
                                    <th>Success Rate</th>
                                    <th>Executions</th>
                                    <th>Avg Time</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
        '''
        
        # Sort tests by success rate (worst first for attention)
        sorted_tests = sorted(individual_trends.items(), 
                            key=lambda x: x[1].get('passed_rate', 0))
        
        for test_id, data in sorted_tests:
            success_rate = data.get('passed_rate', 0)
            category = data.get('category', 'Unknown')
            sheet = data.get('sheet_name', 'Unknown')
            executions = data.get('execution_count', 0)
            avg_time = data.get('avg_execution_time_ms', 0)
            
            status_class = 'success' if success_rate >= 90 else 'warning' if success_rate >= 70 else 'danger'
            status_text = '✅ Stable' if success_rate >= 90 else '⚠️ Unstable' if success_rate >= 70 else '❌ Failing'
            
            content += f'''
                            <tr>
                                <td><code>{test_id}</code></td>
                                <td><span class="badge bg-secondary">{category}</span></td>
                                <td>{sheet}</td>
                                <td><span class="badge bg-{status_class}">{success_rate:.1f}%</span></td>
                                <td>{executions}</td>
                                <td>{avg_time:.0f}ms</td>
                                <td>{status_text}</td>
                            </tr>
            '''
        
        content += '''
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        '''
        return content
    
    def _generate_javascript_charts(self, trends_data: Dict) -> str:
        """Generate comprehensive JavaScript for all charts."""
        time_trends = trends_data.get('time_based_trends', {})
        sheet_trends = trends_data.get('sheet_level_trends', {})
        category_trends = trends_data.get('category_level_trends', {})
        
        # Convert data to JSON strings safely
        sheet_data = json.dumps(list(sheet_trends.keys()))
        sheet_rates = json.dumps([sheet_trends[sheet].get('overall_passed_rate', 0) for sheet in sheet_trends.keys()])
        category_data = json.dumps(list(category_trends.keys()))
        category_rates = json.dumps([category_trends[cat].get('overall_passed_rate', 0) for cat in category_trends.keys()])
        daily_data = json.dumps(time_trends.get('daily', {}))
        weekly_data = json.dumps(time_trends.get('weekly', {}))
        monthly_data = json.dumps(time_trends.get('monthly', {}))
        hourly_data = json.dumps(time_trends.get('hourly', {}))
        category_executions = json.dumps([category_trends[cat].get('total_executions', 0) for cat in category_trends.keys()])
        
        return f"""
        // Chart configurations
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // Overview Charts
        function initOverviewCharts() {{
            // Sheet Overview Chart
            const sheetData = {sheet_data};
            const sheetRates = {sheet_rates};
            
            new Chart(document.getElementById('sheetOverviewChart'), {{
                type: 'bar',
                data: {{
                    labels: sheetData,
                    datasets: [{{
                        label: 'Success Rate %',
                        data: sheetRates,
                        backgroundColor: sheetRates.map(rate => 
                            rate >= 90 ? '#22c55e' : rate >= 70 ? '#f59e0b' : '#ef4444'
                        ),
                        borderColor: '#ffffff',
                        borderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100
                        }}
                    }},
                    plugins: {{
                        legend: {{ display: false }}
                    }}
                }}
            }});

            // Category Overview Chart
            const categoryData = {category_data};
            const categoryRates = {category_rates};
            
            new Chart(document.getElementById('categoryOverviewChart'), {{
                type: 'doughnut',
                data: {{
                    labels: categoryData,
                    datasets: [{{
                        data: categoryRates,
                        backgroundColor: [
                            '#ef4444', '#f97316', '#eab308', '#22c55e', 
                            '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4',
                            '#64748b', '#84cc16'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                usePointStyle: true,
                                padding: 15
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Time Trends Charts
        function initTimeTrendsCharts() {{
            const dailyData = {daily_data};
            const weeklyData = {weekly_data};
            const monthlyData = {monthly_data};
            const hourlyData = {hourly_data};
            
            // Main time trends chart
            const ctx = document.getElementById('timeTrendsChart').getContext('2d');
            let timeTrendsChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: Object.keys(dailyData),
                    datasets: [{{
                        label: 'Success Rate %',
                        data: Object.values(dailyData).map(d => d.passed_rate || 0),
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4
                    }}, {{
                        label: 'Execution Count',
                        data: Object.values(dailyData).map(d => d.execution_count || 0),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: false,
                        yAxisID: 'y1'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,
                            max: 100,
                            title: {{ display: true, text: 'Success Rate %' }}
                        }},
                        y1: {{
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,
                            title: {{ display: true, text: 'Execution Count' }},
                            grid: {{ drawOnChartArea: false }}
                        }}
                    }}
                }}
            }});
            
            // Time frame switcher
            document.querySelectorAll('[data-timeframe]').forEach(btn => {{
                btn.addEventListener('click', function() {{
                    document.querySelectorAll('[data-timeframe]').forEach(b => b.classList.remove('active'));
                    this.classList.add('active');
                    
                    const timeframe = this.dataset.timeframe;
                    let data;
                    switch(timeframe) {{
                        case 'weekly': data = weeklyData; break;
                        case 'monthly': data = monthlyData; break;
                        default: data = dailyData;
                    }}
                    
                    timeTrendsChart.data.labels = Object.keys(data);
                    timeTrendsChart.data.datasets[0].data = Object.values(data).map(d => d.passed_rate || 0);
                    timeTrendsChart.data.datasets[1].data = Object.values(data).map(d => d.execution_count || 0);
                    timeTrendsChart.update();
                }});
            }});
            
            // Hourly patterns chart
            new Chart(document.getElementById('hourlyTrendsChart'), {{
                type: 'bar',
                data: {{
                    labels: Object.keys(hourlyData).map(h => h + ':00'),
                    datasets: [{{
                        label: 'Executions',
                        data: Object.values(hourlyData).map(d => d.execution_count || 0),
                        backgroundColor: '#8b5cf6'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
            
            // Weekly pattern chart
            new Chart(document.getElementById('weeklyPatternChart'), {{
                type: 'radar',
                data: {{
                    labels: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
                    datasets: [{{
                        label: 'Executions by Day',
                        data: [5, 20, 18, 22, 25, 15, 8],
                        backgroundColor: 'rgba(34, 197, 94, 0.2)',
                        borderColor: '#22c55e',
                        pointBackgroundColor: '#22c55e'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        r: {{ beginAtZero: true }}
                    }}
                }}
            }});
        }}
        
        // Category distribution chart
        function initCategoryDistributionChart() {{
            const categoryData = {category_data};
            const categoryExecutions = {category_executions};
            
            new Chart(document.getElementById('categoryDistributionChart'), {{
                type: 'pie',
                data: {{
                    labels: categoryData,
                    datasets: [{{
                        data: categoryExecutions,
                        backgroundColor: [
                            '#ef4444', '#f97316', '#eab308', '#22c55e', 
                            '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4'
                        ]
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom' }}
                    }}
                }}
            }});
        }}
        
        // Individual tests filter
        function initTestFilter() {{
            const filterInput = document.getElementById('testFilter');
            const table = document.getElementById('individualTestsTable');
            
            if (filterInput && table) {{
                filterInput.addEventListener('input', function() {{
                    const filter = this.value.toLowerCase();
                    const rows = table.getElementsByTagName('tr');
                    
                    for (let i = 1; i < rows.length; i++) {{
                        const testId = rows[i].getElementsByTagName('td')[0];
                        if (testId) {{
                            const txtValue = testId.textContent || testId.innerText;
                            rows[i].style.display = txtValue.toLowerCase().indexOf(filter) > -1 ? '' : 'none';
                        }}
                    }}
                }});
            }}
        }}
        
        // Initialize all charts when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            initOverviewCharts();
            
            // Initialize other charts when their tabs are shown
            document.getElementById('time-trends-tab').addEventListener('shown.bs.tab', function() {{
                setTimeout(initTimeTrendsCharts, 100);
            }});
            
            document.getElementById('categories-tab').addEventListener('shown.bs.tab', function() {{
                setTimeout(initCategoryDistributionChart, 100);
            }});
            
            document.getElementById('individual-tab').addEventListener('shown.bs.tab', function() {{
                setTimeout(initTestFilter, 100);
            }});
        }});
        """