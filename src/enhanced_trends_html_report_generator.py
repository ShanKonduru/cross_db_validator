import os
import json
from datetime import datetime
from typing import Dict, Any


class EnhancedTrendsHTMLReportGenerator:
    """
    Generates comprehensive interactive HTML reports for test execution trends analysis.
    Features tab-based navigation, drill-down capabilities, and time-series visualizations.
    """
    
    def __init__(self, execution_history: list = None, output_file: str = None):
        self.execution_history = execution_history or []
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_file = f"output/Enhanced_Test_Trends_Report_{timestamp}.html"
        else:
            self.output_file = output_file
    
    def generate_comprehensive_trends_report(self, trends_data: Dict, output_file: str = None) -> str:
        """
        Generate comprehensive HTML trends report from persistent data.
        
        Args:
            trends_data: Comprehensive trends data from PersistentTrendsAnalyzer
            output_file: Optional specific output file path to override default
            
        Returns:
            str: Path to the generated HTML report
        """
        print("🌐 Generating comprehensive interactive trends dashboard...")
        
        # Use provided output file or default
        if output_file:
            self.output_file = output_file
        
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
        
        /* Enhanced Filter Styles */
        .filters-container {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
            margin-bottom: 30px;
        }}
        
        .filters-header {{
            background: rgba(255, 255, 255, 0.1);
            padding: 20px 30px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
        }}
        
        .filter-icon-wrapper {{
            background: rgba(255, 255, 255, 0.2);
            width: 50px;
            height: 50px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
        }}
        
        .filters-title {{
            color: white;
            font-weight: 600;
            font-size: 1.5rem;
        }}
        
        .filters-subtitle {{
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }}
        
        .filter-clear-btn {{
            border: 1px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.1);
            color: white;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}
        
        .filter-clear-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.5);
            color: white;
            transform: translateY(-2px);
        }}
        
        .filters-content {{
            padding: 30px;
            background: white;
        }}
        
        .filter-group {{
            position: relative;
        }}
        
        .filter-label {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            font-weight: 600;
            color: #495057;
        }}
        
        .filter-label label {{
            margin-bottom: 0;
            margin-left: 5px;
        }}
        
        .filter-select {{
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
            background: #f8f9fa;
        }}
        
        .filter-select:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.15);
            background: white;
        }}
        
        .filter-select:hover {{
            background: white;
            border-color: #667eea;
        }}
        
        .filter-status-container {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 15px;
            padding: 15px 20px;
            border: 1px solid #dee2e6;
        }}
        
        .filter-status-wrapper {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .filter-status-text {{
            color: #6c757d;
            font-weight: 500;
            font-size: 0.95rem;
        }}
        
        .filter-status-text.active {{
            color: #667eea;
            font-weight: 600;
        }}
        
        @media (max-width: 768px) {{
            .filters-header {{
                padding: 15px 20px;
            }}
            
            .filters-content {{
                padding: 20px;
            }}
            
            .filter-icon-wrapper {{
                width: 40px;
                height: 40px;
                font-size: 16px;
            }}
            
            .filters-title {{
                font-size: 1.25rem;
            }}
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

        <!-- Filters Section -->
        {self._generate_filters_section(trends_data.get('filter_data', {}))}

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

        <!-- Filters Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="chart-container">
                    <h4 class="mb-3"><i class="fas fa-filter text-primary"></i> Data Filters</h4>
                    <div class="row">
                        <div class="col-md-3">
                            <label for="applicationFilter" class="form-label"><i class="fas fa-cube"></i> Application</label>
                            <select class="form-select" id="applicationFilter" onchange="applyFilters()">
                                <option value="">All Applications</option>
                                {self._generate_application_options(trends_data.get('filter_data', {}))}
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label for="environmentFilter" class="form-label"><i class="fas fa-server"></i> Environment</label>
                            <select class="form-select" id="environmentFilter" onchange="applyFilters()">
                                <option value="">All Environments</option>
                                {self._generate_environment_options(trends_data.get('filter_data', {}))}
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label for="sourceFilter" class="form-label"><i class="fas fa-arrow-right"></i> Source DB</label>
                            <select class="form-select" id="sourceFilter" onchange="applyFilters()">
                                <option value="">All Source DBs</option>
                                {self._generate_source_db_options(trends_data.get('filter_data', {}))}
                            </select>
                        </div>
                        <div class="col-md-3">
                            <label for="targetFilter" class="form-label"><i class="fas fa-bullseye"></i> Target DB</label>
                            <select class="form-select" id="targetFilter" onchange="applyFilters()">
                                <option value="">All Target DBs</option>
                                {self._generate_target_db_options(trends_data.get('filter_data', {}))}
                            </select>
                        </div>
                    </div>
                    <div class="row mt-3">
                        <div class="col-12">
                            <button class="btn btn-outline-secondary btn-sm" onclick="clearAllFilters()">
                                <i class="fas fa-eraser"></i> Clear All Filters
                            </button>
                            <span class="ms-3 text-muted" id="filterStatus">No filters applied</span>
                        </div>
                    </div>
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
                                    <button type="button" class="btn btn-outline-primary btn-sm" data-timeframe="hourly">Hourly</button>
                                    <button type="button" class="btn btn-outline-primary btn-sm active" data-timeframe="daily">Daily</button>
                                    <button type="button" class="btn btn-outline-primary btn-sm" data-timeframe="weekly">Weekly</button>
                                    <button type="button" class="btn btn-outline-primary btn-sm" data-timeframe="monthly">Monthly</button>
                                    <button type="button" class="btn btn-outline-primary btn-sm" data-timeframe="yearly">Yearly</button>
                                </div>
                            </div>
                            <div id="trends-filter-notice" class="alert alert-info mb-3" style="display: none;">
                                <i class="fas fa-info-circle me-2"></i>
                                <strong>Filtered View:</strong> Trends are being filtered by your selected criteria. 
                                <em>Note: Full filtering implementation requires server-side processing.</em>
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
        hourly_data = json.dumps(time_trends.get('hourly', {}))
        daily_data = json.dumps(time_trends.get('daily', {}))
        weekly_data = json.dumps(time_trends.get('weekly', {}))
        monthly_data = json.dumps(time_trends.get('monthly', {}))
        yearly_data = json.dumps(time_trends.get('yearly', {}))
        category_executions = json.dumps([category_trends[cat].get('total_executions', 0) for cat in category_trends.keys()])
        
        return f"""
        // Store raw execution data for filtering
        window.rawExecutionData = {json.dumps(self.execution_history, indent=2, default=str)};
        
        // Chart configurations
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // Overview Charts
        function initOverviewCharts() {{
            try {{
                // Sheet Overview Chart
                const sheetData = {sheet_data};
                const sheetRates = {sheet_rates};
                
                const sheetCanvas = document.getElementById('sheetOverviewChart');
                if (!sheetCanvas) {{
                    console.error('Sheet overview chart canvas not found');
                    return;
                }}
                
                new Chart(sheetCanvas, {{
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
                
                const categoryCanvas = document.getElementById('categoryOverviewChart');
                if (!categoryCanvas) {{
                    console.error('Category overview chart canvas not found');
                    return;
                }}
                
                new Chart(categoryCanvas, {{
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
            }} catch (error) {{
                console.error('Error initializing overview charts:', error);
                showChartError('sheetOverviewChart', 'Error loading sheet performance chart');
                showChartError('categoryOverviewChart', 'Error loading category distribution chart');
            }}
        }}
        
        // Time Trends Charts
        function initTimeTrendsCharts() {{
            const hourlyData = {hourly_data};
            const dailyData = {daily_data};
            const weeklyData = {weekly_data};
            const monthlyData = {monthly_data};
            const yearlyData = {yearly_data};
            
            // Store original data for filtering
            window.originalTimeData = {{
                hourly: hourlyData,
                daily: dailyData,
                weekly: weeklyData,
                monthly: monthlyData,
                yearly: yearlyData
            }};
            
            // Main time trends chart
            const ctx = document.getElementById('timeTrendsChart').getContext('2d');
            window.timeTrendsChart = new Chart(ctx, {{
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
                        data: Object.values(dailyData).map(d => d.executions || 0),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        fill: false,
                        yAxisID: 'y1'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Test Execution Trends - Daily View',
                            font: {{ size: 16 }}
                        }},
                        legend: {{
                            position: 'top'
                        }}
                    }},
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
                    updateTimeTrendsChart(timeframe);
                }});
            }});
            
            // Hourly patterns chart
            window.hourlyTrendsChart = new Chart(document.getElementById('hourlyTrendsChart'), {{
                type: 'bar',
                data: {{
                    labels: Array.from({{length: 24}}, (_, i) => i + ':00'),
                    datasets: [{{
                        label: 'Executions by Hour',
                        data: Array.from({{length: 24}}, (_, i) => hourlyData[i]?.executions || 0),
                        backgroundColor: 'rgba(139, 92, 246, 0.8)',
                        borderColor: '#8b5cf6',
                        borderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Execution Pattern by Hour of Day'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{ display: true, text: 'Number of Executions' }}
                        }},
                        x: {{
                            title: {{ display: true, text: 'Hour of Day' }}
                        }}
                    }}
                }}
            }});
        }}
        
        function updateTimeTrendsChart(timeframe) {{
            if (!window.timeTrendsChart || !window.originalTimeData) return;
            
            let data = window.originalTimeData[timeframe] || window.originalTimeData.daily;
            let chartTitle = `Test Execution Trends - ${{timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}} View`;
            
            window.timeTrendsChart.data.labels = Object.keys(data);
            window.timeTrendsChart.data.datasets[0].data = Object.values(data).map(d => d.passed_rate || 0);
            window.timeTrendsChart.data.datasets[1].data = Object.values(data).map(d => d.executions || 0);
            window.timeTrendsChart.options.plugins.title.text = chartTitle;
            window.timeTrendsChart.update('active');
        }}
            
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
        
        // Error handling and fallback for Chart.js
        function showChartError(containerId, message) {{
            const container = document.getElementById(containerId);
            if (container) {{
                container.innerHTML = `<div class="alert alert-warning text-center">
                    <i class="fas fa-exclamation-triangle"></i> 
                    ${{message}}<br>
                    <small>Please check your internet connection or disable ad blockers</small>
                </div>`;
            }}
        }}
        
        function checkChartJsLoaded() {{
            return typeof Chart !== 'undefined';
        }}
        
        // Initialize all charts when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            // Check if Chart.js loaded successfully
            if (!checkChartJsLoaded()) {{
                console.error('Chart.js failed to load from CDN');
                showChartError('sheetOverviewChart', 'Charts unavailable - Chart.js library failed to load');
                showChartError('categoryOverviewChart', 'Charts unavailable - Chart.js library failed to load');
                showChartError('timeTrendsChart', 'Charts unavailable - Chart.js library failed to load');
                return;
            }}
            
            try {{
                initOverviewCharts();
            }} catch (error) {{
                console.error('Error initializing overview charts:', error);
                showChartError('sheetOverviewChart', 'Error initializing overview charts');
                showChartError('categoryOverviewChart', 'Error initializing overview charts');
            }}
            
            // Initialize other charts when their tabs are shown
            document.getElementById('time-trends-tab').addEventListener('shown.bs.tab', function() {{
                if (checkChartJsLoaded()) {{
                    setTimeout(initTimeTrendsCharts, 100);
                }} else {{
                    showChartError('timeTrendsChart', 'Charts unavailable - Chart.js library not loaded');
                }}
            }});
            
            document.getElementById('categories-tab').addEventListener('shown.bs.tab', function() {{
                if (checkChartJsLoaded()) {{
                    setTimeout(initCategoryDistributionChart, 100);
                }} else {{
                    showChartError('categoryChart', 'Charts unavailable - Chart.js library not loaded');
                }}
            }});
            
            document.getElementById('individual-tab').addEventListener('shown.bs.tab', function() {{
                setTimeout(initTestFilter, 100);
            }});
        }});
        
        // Filtering functionality
        function applyFilters() {{
            const appFilter = document.getElementById('applicationFilter').value;
            const envFilter = document.getElementById('environmentFilter').value;
            const sourceFilter = document.getElementById('sourceFilter').value;
            const targetFilter = document.getElementById('targetFilter').value;
            
            updateFilterStatus(appFilter, envFilter, sourceFilter, targetFilter);
            
            // Apply filters to all visible tables and charts
            filterIndividualTestsTable(appFilter, envFilter, sourceFilter, targetFilter);
            filterSheetsTable(appFilter, envFilter, sourceFilter, targetFilter);
            
            // Note: Chart filtering would require more complex data restructuring
            // For now, we focus on table filtering which is most useful
        }}
        
        function clearAllFilters() {{
            document.getElementById('applicationFilter').value = '';
            document.getElementById('environmentFilter').value = '';
            document.getElementById('sourceFilter').value = '';
            document.getElementById('targetFilter').value = '';
            updateFilterStatus('', '', '', '');
            
            // Show all rows
            const tables = ['individualTestsTable'];
            tables.forEach(tableId => {{
                const table = document.getElementById(tableId);
                if (table) {{
                    const rows = table.querySelectorAll('tbody tr');
                    rows.forEach(row => row.style.display = '');
                }}
            }});
        }}
        
        function updateFilterStatus(app, env, source, target) {{
            const filters = [];
            if (app) filters.push(`App: ${{app}}`);
            if (env) filters.push(`Env: ${{env}}`);
            if (source) filters.push(`Source: ${{source}}`);
            if (target) filters.push(`Target: ${{target}}`);
            
            const status = filters.length ? `Active filters: ${{filters.join(', ')}}` : 'No filters applied';
            document.getElementById('filterStatus').textContent = status;
        }}
        
        function filterIndividualTestsTable(app, env, source, target) {{
            const table = document.getElementById('individualTestsTable');
            if (!table) return;
            
            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {{
                let showRow = true;
                
                // Get test details from the row - this would need to be enhanced
                // based on how we store the database info in the table
                const testId = row.cells[0]?.textContent || '';
                const category = row.cells[1]?.textContent || '';
                
                // For now, basic filtering - this can be enhanced with more detailed data
                if (app && !testId.toLowerCase().includes(app.toLowerCase())) {{
                    showRow = false;
                }}
                if (env && !testId.toLowerCase().includes(env.toLowerCase())) {{
                    showRow = false;
                }}
                
                row.style.display = showRow ? '' : 'none';
            }});
        }}
        
        function applyFilters() {{
            const appFilter = document.getElementById('application-filter').value;
            const envFilter = document.getElementById('environment-filter').value;
            const sourceFilter = document.getElementById('source-db-filter').value;
            const targetFilter = document.getElementById('target-db-filter').value;
            
            // Apply filters to tables
            filterIndividualTestsTable(appFilter, envFilter, sourceFilter, targetFilter);
            filterSheetsTable(appFilter, envFilter, sourceFilter, targetFilter);
            
            // Apply filters to time trends charts
            updateTimeTrendsWithFilters(appFilter, envFilter, sourceFilter, targetFilter);
            
            // Update filter status
            updateFilterStatus();
        }}
        
        function updateTimeTrendsWithFilters(appFilter, envFilter, sourceFilter, targetFilter) {{
            const hasFilters = appFilter || envFilter || sourceFilter || targetFilter;
            const noticeElement = document.getElementById('trends-filter-notice');
            
            if (hasFilters) {{
                // Show filter notice
                if (noticeElement) {{
                    noticeElement.style.display = 'block';
                }}
                
                // Filter the original data based on selected criteria
                const filteredData = filterTimeData(appFilter, envFilter, sourceFilter, targetFilter);
                const activeTimeframe = document.querySelector('[data-timeframe].active')?.dataset.timeframe || 'daily';
                
                // Update chart with filtered data
                updateTimeTrendsChartWithData(activeTimeframe, filteredData[activeTimeframe]);
                
                // Update chart title
                const chartTitle = `Test Execution Trends - ${{activeTimeframe.charAt(0).toUpperCase() + activeTimeframe.slice(1)}} View (Filtered)`;
                if (window.timeTrendsChart) {{
                    window.timeTrendsChart.options.plugins.title.text = chartTitle;
                    window.timeTrendsChart.options.plugins.subtitle = {{
                        display: true,
                        text: `Active Filters: ${{[appFilter, envFilter, sourceFilter, targetFilter].filter(f => f).join(', ')}}`,
                        font: {{ size: 12, style: 'italic' }},
                        color: '#667eea'
                    }};
                    window.timeTrendsChart.update('none');
                }}
                
                console.log('🎯 Time trends filtered for:', {{ appFilter, envFilter, sourceFilter, targetFilter }});
            }} else {{
                // Hide filter notice
                if (noticeElement) {{
                    noticeElement.style.display = 'none';
                }}
                
                // Reset to original data when no filters
                const activeTimeframe = document.querySelector('[data-timeframe].active')?.dataset.timeframe || 'daily';
                updateTimeTrendsChart(activeTimeframe);
                
                if (window.timeTrendsChart) {{
                    window.timeTrendsChart.options.plugins.subtitle = {{ display: false }};
                    window.timeTrendsChart.update('none');
                }}
            }}
        }}
        
        function filterTimeData(appFilter, envFilter, sourceFilter, targetFilter) {{
            // Get access to the raw execution history data
            const rawData = window.rawExecutionData || [];
            
            // Filter the raw data based on criteria
            const filteredExecutions = rawData.filter(record => {{
                const metadata = record.execution_metadata || {{}};
                
                // Application filter
                if (appFilter && metadata.application !== appFilter) {{
                    return false;
                }}
                
                // Environment filter  
                if (envFilter && metadata.environment !== envFilter) {{
                    return false;
                }}
                
                // Source/Target DB filtering would require execution_details
                // For now, we'll skip these filters since they're not in the main metadata
                
                return true;
            }});
            
            // Regenerate time trends from filtered data
            return {{
                hourly: generateHourlyTrends(filteredExecutions),
                daily: generateDailyTrends(filteredExecutions),
                weekly: generateWeeklyTrends(filteredExecutions),
                monthly: generateMonthlyTrends(filteredExecutions),
                yearly: generateYearlyTrends(filteredExecutions)
            }};
        }}
        
        function generateDailyTrends(executions) {{
            const dailyData = {{}};
            
            executions.forEach(record => {{
                const execTime = new Date(record.execution_metadata.execution_time);
                const dayKey = execTime.toISOString().split('T')[0]; // YYYY-MM-DD
                const summary = record.overall_summary || {{}};
                
                if (!dailyData[dayKey]) {{
                    dailyData[dayKey] = {{
                        executions: 0, total_tests: 0, passed_tests: 0,
                        failed_tests: 0, skipped_tests: 0
                    }};
                }}
                
                dailyData[dayKey].executions += 1;
                dailyData[dayKey].total_tests += summary.total_tests || 0;
                dailyData[dayKey].passed_tests += summary.passed_tests || 0;
                dailyData[dayKey].failed_tests += summary.failed_tests || 0;
                dailyData[dayKey].skipped_tests += summary.skipped_tests || 0;
            }});
            
            // Calculate rates
            Object.keys(dailyData).forEach(day => {{
                const data = dailyData[day];
                if (data.total_tests > 0) {{
                    data.passed_rate = Math.round(data.passed_tests / data.total_tests * 100 * 100) / 100;
                    data.failed_rate = Math.round(data.failed_tests / data.total_tests * 100 * 100) / 100;
                    data.skipped_rate = Math.round(data.skipped_tests / data.total_tests * 100 * 100) / 100;
                }}
            }});
            
            return dailyData;
        }}
        
        function generateHourlyTrends(executions) {{
            const hourlyData = {{}};
            
            executions.forEach(record => {{
                const execTime = new Date(record.execution_metadata.execution_time);
                const hour = execTime.getHours();
                const summary = record.overall_summary || {{}};
                
                if (!hourlyData[hour]) {{
                    hourlyData[hour] = {{
                        executions: 0, total_tests: 0, passed_tests: 0,
                        failed_tests: 0, skipped_tests: 0
                    }};
                }}
                
                hourlyData[hour].executions += 1;
                hourlyData[hour].total_tests += summary.total_tests || 0;
                hourlyData[hour].passed_tests += summary.passed_tests || 0;
                hourlyData[hour].failed_tests += summary.failed_tests || 0;
                hourlyData[hour].skipped_tests += summary.skipped_tests || 0;
            }});
            
            // Calculate rates
            Object.keys(hourlyData).forEach(hour => {{
                const data = hourlyData[hour];
                if (data.total_tests > 0) {{
                    data.passed_rate = Math.round(data.passed_tests / data.total_tests * 100 * 100) / 100;
                }}
            }});
            
            return hourlyData;
        }}
        
        function generateWeeklyTrends(executions) {{
            const weeklyData = {{}};
            
            executions.forEach(record => {{
                const execTime = new Date(record.execution_metadata.execution_time);
                const year = execTime.getFullYear();
                const week = getWeekNumber(execTime);
                const weekKey = `${{year}}-W${{week.toString().padStart(2, '0')}}`;
                const summary = record.overall_summary || {{}};
                
                if (!weeklyData[weekKey]) {{
                    weeklyData[weekKey] = {{
                        executions: 0, total_tests: 0, passed_tests: 0,
                        failed_tests: 0, skipped_tests: 0
                    }};
                }}
                
                weeklyData[weekKey].executions += 1;
                weeklyData[weekKey].total_tests += summary.total_tests || 0;
                weeklyData[weekKey].passed_tests += summary.passed_tests || 0;
                weeklyData[weekKey].failed_tests += summary.failed_tests || 0;
                weeklyData[weekKey].skipped_tests += summary.skipped_tests || 0;
            }});
            
            // Calculate rates
            Object.keys(weeklyData).forEach(week => {{
                const data = weeklyData[week];
                if (data.total_tests > 0) {{
                    data.passed_rate = Math.round(data.passed_tests / data.total_tests * 100 * 100) / 100;
                }}
            }});
            
            return weeklyData;
        }}
        
        function generateMonthlyTrends(executions) {{
            const monthlyData = {{}};
            
            executions.forEach(record => {{
                const execTime = new Date(record.execution_metadata.execution_time);
                const monthKey = execTime.toISOString().substring(0, 7); // YYYY-MM
                const summary = record.overall_summary || {{}};
                
                if (!monthlyData[monthKey]) {{
                    monthlyData[monthKey] = {{
                        executions: 0, total_tests: 0, passed_tests: 0,
                        failed_tests: 0, skipped_tests: 0
                    }};
                }}
                
                monthlyData[monthKey].executions += 1;
                monthlyData[monthKey].total_tests += summary.total_tests || 0;
                monthlyData[monthKey].passed_tests += summary.passed_tests || 0;
                monthlyData[monthKey].failed_tests += summary.failed_tests || 0;
                monthlyData[monthKey].skipped_tests += summary.skipped_tests || 0;
            }});
            
            // Calculate rates
            Object.keys(monthlyData).forEach(month => {{
                const data = monthlyData[month];
                if (data.total_tests > 0) {{
                    data.passed_rate = Math.round(data.passed_tests / data.total_tests * 100 * 100) / 100;
                }}
            }});
            
            return monthlyData;
        }}
        
        function generateYearlyTrends(executions) {{
            const yearlyData = {{}};
            
            executions.forEach(record => {{
                const execTime = new Date(record.execution_metadata.execution_time);
                const year = execTime.getFullYear().toString();
                const summary = record.overall_summary || {{}};
                
                if (!yearlyData[year]) {{
                    yearlyData[year] = {{
                        executions: 0, total_tests: 0, passed_tests: 0,
                        failed_tests: 0, skipped_tests: 0
                    }};
                }}
                
                yearlyData[year].executions += 1;
                yearlyData[year].total_tests += summary.total_tests || 0;
                yearlyData[year].passed_tests += summary.passed_tests || 0;
                yearlyData[year].failed_tests += summary.failed_tests || 0;
                yearlyData[year].skipped_tests += summary.skipped_tests || 0;
            }});
            
            // Calculate rates
            Object.keys(yearlyData).forEach(year => {{
                const data = yearlyData[year];
                if (data.total_tests > 0) {{
                    data.passed_rate = Math.round(data.passed_tests / data.total_tests * 100 * 100) / 100;
                }}
            }});
            
            return yearlyData;
        }}
        
        function getWeekNumber(date) {{
            const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
            const dayNum = d.getUTCDay() || 7;
            d.setUTCDate(d.getUTCDate() + 4 - dayNum);
            const yearStart = new Date(Date.UTC(d.getUTCFullYear(),0,1));
            return Math.ceil((((d - yearStart) / 86400000) + 1)/7);
        }}
        
        function updateTimeTrendsChartWithData(timeframe, data) {{
            if (!window.timeTrendsChart || !data) return;
            
            const chartTitle = `Test Execution Trends - ${{timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}} View`;
            
            window.timeTrendsChart.data.labels = Object.keys(data);
            window.timeTrendsChart.data.datasets[0].data = Object.values(data).map(d => d.passed_rate || 0);
            window.timeTrendsChart.data.datasets[1].data = Object.values(data).map(d => d.executions || 0);
            window.timeTrendsChart.options.plugins.title.text = chartTitle;
            window.timeTrendsChart.update('active');
        }}
        
        function clearAllFilters() {{
            document.getElementById('application-filter').value = '';
            document.getElementById('environment-filter').value = '';
            document.getElementById('source-db-filter').value = '';
            document.getElementById('target-db-filter').value = '';
            applyFilters();
        }}
        
        function updateFilterStatus() {{
            const activeFilters = [];
            const filterSelects = [
                {{ id: 'application-filter', name: '🔹 Application', icon: 'fas fa-cube' }},
                {{ id: 'environment-filter', name: '🔹 Environment', icon: 'fas fa-server' }},
                {{ id: 'source-db-filter', name: '🔹 Source DB', icon: 'fas fa-database' }},
                {{ id: 'target-db-filter', name: '🔹 Target DB', icon: 'fas fa-hdd' }}
            ];
            
            filterSelects.forEach(filter => {{
                const element = document.getElementById(filter.id);
                if (element && element.value) {{
                    activeFilters.push(`${{filter.name}} ${{element.value}}`);
                }}
            }});
            
            const statusEl = document.getElementById('filter-status');
            if (activeFilters.length > 0) {{
                statusEl.innerHTML = `<strong>🎯 Active:</strong> ${{activeFilters.join(' • ')}}`;
                statusEl.className = 'filter-status-text active';
            }} else {{
                statusEl.innerHTML = '🔍 Ready to filter • Select options above to drill down';
                statusEl.className = 'filter-status-text';
            }}
        }}
        
        function filterSheetsTable(app, env, source, target) {{
            // Similar filtering for sheets table
            // Implementation would depend on sheet data structure
        }}
        """
    
    def _generate_filters_section(self, filter_data: Dict) -> str:
        """Generate the enhanced filters section HTML with improved styling."""
        return f"""
        <div class="row mb-5">
            <div class="col-12">
                <div class="filters-container">
                    <div class="filters-header">
                        <div class="row align-items-center">
                            <div class="col-auto">
                                <div class="filter-icon-wrapper">
                                    <i class="fas fa-sliders-h"></i>
                                </div>
                            </div>
                            <div class="col">
                                <h4 class="filters-title mb-0">Smart Filters</h4>
                                <p class="filters-subtitle mb-0">Drill down into your test execution data</p>
                            </div>
                            <div class="col-auto">
                                <button class="btn btn-outline-light btn-sm filter-clear-btn" onclick="clearAllFilters()">
                                    <i class="fas fa-undo me-1"></i>Reset All
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="filters-content">
                        <div class="row g-4">
                            <div class="col-lg-3 col-md-6">
                                <div class="filter-group">
                                    <div class="filter-label">
                                        <i class="fas fa-cube text-primary me-2"></i>
                                        <label for="application-filter" class="form-label">Application</label>
                                    </div>
                                    <select id="application-filter" class="form-select filter-select" onchange="applyFilters()">
                                        <option value="">🌐 All Applications</option>
                                        {self._generate_application_options(filter_data)}
                                    </select>
                                </div>
                            </div>
                            
                            <div class="col-lg-3 col-md-6">
                                <div class="filter-group">
                                    <div class="filter-label">
                                        <i class="fas fa-server text-success me-2"></i>
                                        <label for="environment-filter" class="form-label">Environment</label>
                                    </div>
                                    <select id="environment-filter" class="form-select filter-select" onchange="applyFilters()">
                                        <option value="">🏗️ All Environments</option>
                                        {self._generate_environment_options(filter_data)}
                                    </select>
                                </div>
                            </div>
                            
                            <div class="col-lg-3 col-md-6">
                                <div class="filter-group">
                                    <div class="filter-label">
                                        <i class="fas fa-database text-info me-2"></i>
                                        <label for="source-db-filter" class="form-label">Source Database</label>
                                    </div>
                                    <select id="source-db-filter" class="form-select filter-select" onchange="applyFilters()">
                                        <option value="">📤 All Source DBs</option>
                                        {self._generate_source_db_options(filter_data)}
                                    </select>
                                </div>
                            </div>
                            
                            <div class="col-lg-3 col-md-6">
                                <div class="filter-group">
                                    <div class="filter-label">
                                        <i class="fas fa-hdd text-warning me-2"></i>
                                        <label for="target-db-filter" class="form-label">Target Database</label>
                                    </div>
                                    <select id="target-db-filter" class="form-select filter-select" onchange="applyFilters()">
                                        <option value="">📥 All Target DBs</option>
                                        {self._generate_target_db_options(filter_data)}
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div class="row mt-4">
                            <div class="col-12">
                                <div class="filter-status-container">
                                    <div class="filter-status-wrapper">
                                        <i class="fas fa-info-circle me-2"></i>
                                        <span id="filter-status" class="filter-status-text">No filters applied</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_application_options(self, filter_data: Dict) -> str:
        """Generate enhanced HTML options for application filter."""
        applications = filter_data.get('applications', [])
        options = []
        app_icons = {
            'DUMMY': '🎯',
            'cross_db_validator': '⚡',
            'default': '📦'
        }
        
        for app in applications:
            icon = app_icons.get(app, '🔧')
            options.append(f'<option value="{app}">{icon} {app}</option>')
        return ''.join(options)
    
    def _generate_environment_options(self, filter_data: Dict) -> str:
        """Generate enhanced HTML options for environment filter."""
        environments = filter_data.get('environments', [])
        options = []
        env_icons = {
            'DEV': '🛠️',
            'NP1': '🧪',
            'production': '🏭',
            'default': '🌐'
        }
        
        for env in environments:
            icon = env_icons.get(env, '⚙️')
            options.append(f'<option value="{env}">{icon} {env.upper()}</option>')
        return ''.join(options)
    
    def _generate_source_db_options(self, filter_data: Dict) -> str:
        """Generate enhanced HTML options for source database filter."""
        source_apps = filter_data.get('source_applications', [])
        source_envs = filter_data.get('source_environments', [])
        options = []
        
        # Combine applications and environments for source databases
        for app in source_apps:
            for env in source_envs:
                db_combo = f"{app}.{env}"
                options.append(f'<option value="{db_combo}">📤 {db_combo}</option>')
        
        return ''.join(options)
    
    def _generate_target_db_options(self, filter_data: Dict) -> str:
        """Generate enhanced HTML options for target database filter."""
        target_apps = filter_data.get('target_applications', [])
        target_envs = filter_data.get('target_environments', [])
        options = []
        
        # Combine applications and environments for target databases
        for app in target_apps:
            for env in target_envs:
                db_combo = f"{app}.{env}"
                options.append(f'<option value="{db_combo}">📥 {db_combo}</option>')
        
        return ''.join(options)