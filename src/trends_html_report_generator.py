import os
import json
from datetime import datetime
from typing import Dict, Any
from src.test_trends_analyzer import TestExecutionTrendsAnalyzer


class TrendsHTMLReportGenerator:
    """
    Generates interactive HTML reports for test execution trends analysis.
    Supports both legacy file-based trends and new persistent data trends.
    """
    
    def __init__(self, output_file: str = None):
        self.analyzer = TestExecutionTrendsAnalyzer()
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_file = f"output/Test_Trends_Report_{timestamp}.html"
        else:
            self.output_file = output_file
    
    def generate_persistent_trends_report(self, trends_data: Dict) -> str:
        """
        Generate comprehensive HTML trends report from persistent data.
        
        Args:
            trends_data: Comprehensive trends data from PersistentTrendsAnalyzer
            
        Returns:
            str: Path to the generated HTML report
        """
        print("🌐 Generating persistent trends HTML dashboard...")
        
        # Generate HTML content from persistent trends data
        html_content = self._generate_persistent_html_content(trends_data)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        # Save report
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.output_file
    
    def _generate_persistent_html_content(self, trends_data: Dict) -> str:
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
                            <canvas id="sheetOverviewChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h4><i class="fas fa-tags text-warning"></i> Category Distribution</h4>
                            <canvas id="categoryOverviewChart"></canvas>
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
                            <canvas id="timeTrendsChart" style="height: 400px;"></canvas>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h4><i class="fas fa-clock text-info"></i> Hourly Execution Pattern</h4>
                            <canvas id="hourlyTrendsChart"></canvas>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="chart-container">
                            <h4><i class="fas fa-calendar-week text-success"></i> Day of Week Pattern</h4>
                            <canvas id="weeklyPatternChart"></canvas>
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
    
    def generate_trends_report(self) -> str:
        """Generate comprehensive HTML trends report."""
        # Analyze trends data
        print("📊 Analyzing historical test execution data...")
        trends_data = self.analyzer.generate_trends_analysis()
        
        if 'error' in trends_data:
            return self._generate_no_data_report()
        
        # Generate HTML report
        html_content = self._generate_html_content(trends_data)
        
        # Save report
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.output_file
    
    def _generate_no_data_report(self) -> str:
        """Generate report when no historical data is available."""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Trends - No Data</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card text-center">
                    <div class="card-body">
                        <i class="fas fa-chart-line fa-5x text-muted mb-4"></i>
                        <h2 class="card-title">No Historical Data Available</h2>
                        <p class="card-text text-muted">
                            Trends analysis requires multiple test execution reports. 
                            Run more tests to start seeing trends data.
                        </p>
                        <p class="text-info">
                            <i class="fas fa-info-circle"></i> 
                            Execute tests regularly to build historical data for trend analysis.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
        """
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return self.output_file
    
    def _generate_html_content(self, trends_data: Dict[str, Any]) -> str:
        """Generate the complete HTML content for trends report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Execution Trends Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <style>
        .trend-card {{ transition: all 0.3s ease; }}
        .trend-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
        .chart-container {{ position: relative; height: 400px; }}
        .metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }}
        .insight-card {{ border-left: 4px solid #28a745; }}
        .warning-card {{ border-left: 4px solid #ffc107; }}
        .danger-card {{ border-left: 4px solid #dc3545; }}
        .nav-pills .nav-link.active {{ background-color: #667eea; }}
        .table-hover tbody tr:hover {{ background-color: rgba(102, 126, 234, 0.1); }}
        .badge-trend-up {{ background-color: #28a745; }}
        .badge-trend-down {{ background-color: #dc3545; }}
        .badge-trend-stable {{ background-color: #6c757d; }}
    </style>
</head>
<body class="bg-light">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-dark" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
        <div class="container">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-line"></i> Test Execution Trends Analysis
            </span>
            <span class="navbar-text">
                <i class="fas fa-clock"></i> Generated: {timestamp}
            </span>
        </div>
    </nav>

    <div class="container mt-4">
        {self._generate_summary_section(trends_data.get('summary', {}))}
        {self._generate_performance_insights_section(trends_data.get('performance_insights', {}))}
        {self._generate_time_trends_section(trends_data)}
        {self._generate_category_trends_section(trends_data.get('category_trends', {}))}
        {self._generate_detailed_analysis_section(trends_data)}
    </div>

    <!-- Footer -->
    <footer class="bg-dark text-light text-center py-3 mt-5">
        <div class="container">
            <p class="mb-0">
                <i class="fas fa-database"></i> Cross Database Validator - Trends Analysis | 
                Generated on {timestamp}
            </p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        {self._generate_chart_scripts(trends_data)}
    </script>
</body>
</html>
        """
        
        return html_content
    
    def _generate_summary_section(self, summary: Dict) -> str:
        """Generate summary statistics section."""
        if not summary:
            return ""
        
        trend_badge = ""
        insights = summary.get('performance_insights', {})
        if insights:
            trend_direction = insights.get('trend_direction', 'stable')
            if trend_direction == 'improving':
                trend_badge = '<span class="badge badge-trend-up"><i class="fas fa-arrow-up"></i> Improving</span>'
            elif trend_direction == 'declining':
                trend_badge = '<span class="badge badge-trend-down"><i class="fas fa-arrow-down"></i> Declining</span>'
            else:
                trend_badge = '<span class="badge badge-trend-stable"><i class="fas fa-minus"></i> Stable</span>'
        
        return f"""
        <!-- Summary Section -->
        <div class="row mb-4">
            <div class="col-12">
                <h2><i class="fas fa-tachometer-alt"></i> Executive Summary</h2>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-3">
                <div class="card text-center h-100 metric-card">
                    <div class="card-body">
                        <i class="fas fa-play-circle fa-2x mb-2"></i>
                        <h4>{summary.get('total_executions', 0)}</h4>
                        <p class="mb-0">Total Executions</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100 bg-success text-white">
                    <div class="card-body">
                        <i class="fas fa-percentage fa-2x mb-2"></i>
                        <h4>{summary.get('average_success_rate', 0):.1f}%</h4>
                        <p class="mb-0">Avg Success Rate</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100 bg-info text-white">
                    <div class="card-body">
                        <i class="fas fa-calendar-alt fa-2x mb-2"></i>
                        <h4>{summary.get('latest_execution', {}).get('success_rate', 0):.1f}%</h4>
                        <p class="mb-0">Latest Success Rate</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center h-100 bg-warning text-white">
                    <div class="card-body">
                        <i class="fas fa-trend-up fa-2x mb-2"></i>
                        <h4>{trend_badge}</h4>
                        <p class="mb-0">Trend Status</p>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_performance_insights_section(self, insights: Dict) -> str:
        """Generate performance insights section."""
        if not insights or insights.get('message'):
            return f"""
            <div class="row mb-4">
                <div class="col-12">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i> 
                        {insights.get('message', 'Performance insights will be available after more test executions.')}
                    </div>
                </div>
            </div>
            """
        
        trend_direction = insights.get('trend_direction', 'stable')
        trend_icon = '📈' if trend_direction == 'improving' else '📉' if trend_direction == 'declining' else '➡️'
        
        card_class = 'insight-card' if trend_direction == 'improving' else 'danger-card' if trend_direction == 'declining' else 'warning-card'
        
        return f"""
        <!-- Performance Insights -->
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="fas fa-lightbulb"></i> Performance Insights</h3>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-6">
                <div class="card {card_class}">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-line"></i> Trend Analysis</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Trend Direction:</strong> {trend_icon} {trend_direction.title()}</p>
                        <p><strong>Magnitude:</strong> {insights.get('trend_magnitude', 0):.2f}% change</p>
                        <p><strong>Recent Average:</strong> {insights.get('recent_avg_success', 0):.2f}%</p>
                        <p><strong>Historical Average:</strong> {insights.get('historical_avg_success', 0):.2f}%</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-exclamation-triangle"></i> Problem Areas</h5>
                    </div>
                    <div class="card-body">
                        <h6>Most Problematic Categories:</h6>
                        <ul class="list-unstyled">
        """
        
        for item in insights.get('most_problematic_categories', [])[:3]:
            html_content += f"""
                            <li><span class="badge bg-danger">{item['category']}</span> - {item['total_failures']} failures</li>
            """
        
        html_content += """
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html_content
    
    def _generate_time_trends_section(self, trends_data: Dict) -> str:
        """Generate time-based trends section."""
        return f"""
        <!-- Time-based Trends -->
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="fas fa-clock"></i> Time-based Trends</h3>
            </div>
        </div>
        
        <!-- Trend Navigation -->
        <div class="row mb-3">
            <div class="col-12">
                <ul class="nav nav-pills" id="trendTabs" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="daily-tab" data-bs-toggle="pill" data-bs-target="#daily" type="button">
                            <i class="fas fa-calendar-day"></i> Daily
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="hourly-tab" data-bs-toggle="pill" data-bs-target="#hourly" type="button">
                            <i class="fas fa-clock"></i> Hourly
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="weekly-tab" data-bs-toggle="pill" data-bs-target="#weekly" type="button">
                            <i class="fas fa-calendar-week"></i> Weekly
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="monthly-tab" data-bs-toggle="pill" data-bs-target="#monthly" type="button">
                            <i class="fas fa-calendar-alt"></i> Monthly
                        </button>
                    </li>
                </ul>
            </div>
        </div>
        
        <!-- Trend Charts -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="tab-content" id="trendTabContent">
                    <div class="tab-pane fade show active" id="daily" role="tabpanel">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-calendar-day"></i> Daily Success Rate Trends</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="dailyChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="tab-pane fade" id="hourly" role="tabpanel">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-clock"></i> Hourly Execution Patterns</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="hourlyChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="tab-pane fade" id="weekly" role="tabpanel">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-calendar-week"></i> Weekly Trends</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="weeklyChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="tab-pane fade" id="monthly" role="tabpanel">
                        <div class="card">
                            <div class="card-header">
                                <h5><i class="fas fa-calendar-alt"></i> Monthly Overview</h5>
                            </div>
                            <div class="card-body">
                                <div class="chart-container">
                                    <canvas id="monthlyChart"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_category_trends_section(self, category_trends: Dict) -> str:
        """Generate category trends section."""
        if not category_trends:
            return ""
        
        return f"""
        <!-- Category Trends -->
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="fas fa-layer-group"></i> Category Performance Trends</h3>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-chart-area"></i> Success Rate by Category Over Time</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="categoryTrendsChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_detailed_analysis_section(self, trends_data: Dict) -> str:
        """Generate detailed analysis tables."""
        daily_data = trends_data.get('daily', {})
        
        if not daily_data:
            return ""
        
        return f"""
        <!-- Detailed Analysis -->
        <div class="row mb-4">
            <div class="col-12">
                <h3><i class="fas fa-table"></i> Detailed Analysis</h3>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-calendar-day"></i> Daily Execution Summary</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover table-striped">
                                <thead class="table-dark">
                                    <tr>
                                        <th>Date</th>
                                        <th>Executions</th>
                                        <th>Avg Success Rate</th>
                                        <th>Total Tests</th>
                                        <th>Best Run</th>
                                        <th>Worst Run</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
        """
        
        for date, data in sorted(daily_data.items(), reverse=True):
            success_rate = data.get('avg_success_rate', 0)
            status_icon = "🟢" if success_rate >= 90 else "🟡" if success_rate >= 70 else "🔴"
            status_class = "success" if success_rate >= 90 else "warning" if success_rate >= 70 else "danger"
            
            html_content += f"""
                                    <tr class="table-{status_class}">
                                        <td><strong>{date}</strong></td>
                                        <td>{data.get('executions', 0)}</td>
                                        <td>{success_rate:.1f}%</td>
                                        <td>{data.get('total_tests', 0)}</td>
                                        <td>{data.get('best_run', 0):.1f}%</td>
                                        <td>{data.get('worst_run', 0):.1f}%</td>
                                        <td>{status_icon}</td>
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
        
        return html_content
    
    def _generate_chart_scripts(self, trends_data: Dict) -> str:
        """Generate JavaScript for interactive charts."""
        # Prepare data for charts
        daily_data = trends_data.get('daily', {})
        hourly_data = trends_data.get('hourly', {})
        weekly_data = trends_data.get('weekly', {})
        monthly_data = trends_data.get('monthly', {})
        category_trends = trends_data.get('category_trends', {})
        
        # Convert to JSON for JavaScript
        daily_json = json.dumps(daily_data)
        hourly_json = json.dumps(hourly_data)
        weekly_json = json.dumps(weekly_data)
        monthly_json = json.dumps(monthly_data)
        category_json = json.dumps(category_trends)
        
        return f"""
        // Data preparation
        const dailyData = {daily_json};
        const hourlyData = {hourly_json};
        const weeklyData = {weekly_json};
        const monthlyData = {monthly_json};
        const categoryData = {category_json};
        
        // Chart configurations
        const chartOptions = {{
            responsive: true,
            maintainAspectRatio: false,
            scales: {{
                y: {{
                    beginAtZero: true,
                    max: 100,
                    ticks: {{
                        callback: function(value) {{
                            return value + '%';
                        }}
                    }}
                }}
            }},
            plugins: {{
                legend: {{
                    position: 'bottom'
                }}
            }}
        }};
        
        // Daily Chart
        const dailyCtx = document.getElementById('dailyChart');
        if (dailyCtx) {{
            new Chart(dailyCtx, {{
                type: 'line',
                data: {{
                    labels: Object.keys(dailyData).sort(),
                    datasets: [{{
                        label: 'Success Rate (%)',
                        data: Object.keys(dailyData).sort().map(date => dailyData[date].avg_success_rate),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        fill: true,
                        tension: 0.4
                    }}]
                }},
                options: chartOptions
            }});
        }}
        
        // Hourly Chart
        const hourlyCtx = document.getElementById('hourlyChart');
        if (hourlyCtx) {{
            new Chart(hourlyCtx, {{
                type: 'bar',
                data: {{
                    labels: Object.keys(hourlyData).sort(),
                    datasets: [{{
                        label: 'Executions',
                        data: Object.keys(hourlyData).sort().map(hour => hourlyData[hour].executions),
                        backgroundColor: '#667eea'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}
        
        // Weekly Chart
        const weeklyCtx = document.getElementById('weeklyChart');
        if (weeklyCtx) {{
            new Chart(weeklyCtx, {{
                type: 'line',
                data: {{
                    labels: Object.keys(weeklyData).sort(),
                    datasets: [{{
                        label: 'Success Rate (%)',
                        data: Object.keys(weeklyData).sort().map(week => weeklyData[week].avg_success_rate),
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        fill: true
                    }}]
                }},
                options: chartOptions
            }});
        }}
        
        // Monthly Chart
        const monthlyCtx = document.getElementById('monthlyChart');
        if (monthlyCtx) {{
            new Chart(monthlyCtx, {{
                type: 'bar',
                data: {{
                    labels: Object.keys(monthlyData).sort(),
                    datasets: [{{
                        label: 'Success Rate (%)',
                        data: Object.keys(monthlyData).sort().map(month => monthlyData[month].avg_success_rate),
                        backgroundColor: '#dc3545'
                    }}]
                }},
                options: chartOptions
            }});
        }}
        
        // Category Trends Chart
        const categoryCtx = document.getElementById('categoryTrendsChart');
        if (categoryCtx && Object.keys(categoryData).length > 0) {{
            const categories = Object.keys(categoryData);
            const colors = ['#28a745', '#dc3545', '#ffc107', '#17a2b8', '#6f42c1', '#e83e8c', '#fd7e14', '#20c997'];
            
            const datasets = categories.map((category, index) => ({{
                label: category,
                data: categoryData[category].map(item => ({{
                    x: item.timestamp,
                    y: item.success_rate
                }})),
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                fill: false
            }}));
            
            new Chart(categoryCtx, {{
                type: 'line',
                data: {{
                    datasets: datasets
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        x: {{
                            type: 'time',
                            time: {{
                                unit: 'day'
                            }}
                        }},
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            ticks: {{
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}
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
                                    <span class="drill-down-btn" data-bs-toggle="collapse" data-bs-target="#sheet-{sheet_name}">
                                        <i class="fas fa-search-plus"></i> Drill Down
                                    </span>
                                </td>
                            </tr>
                            <tr>
                                <td colspan="5" class="p-0">
                                    <div class="collapse" id="sheet-{sheet_name}">
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
                    <canvas id="categoryDistributionChart"></canvas>
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
        
        return f'''
        // Chart configurations
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // Overview Charts
        function initOverviewCharts() {{
            // Sheet Overview Chart
            const sheetData = {json.dumps(list(sheet_trends.keys()))};
            const sheetRates = {json.dumps([sheet_trends[sheet].get('overall_passed_rate', 0) for sheet in sheet_trends.keys()])};
            
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
            const categoryData = {json.dumps(list(category_trends.keys()))};
            const categoryRates = {json.dumps([category_trends[cat].get('overall_passed_rate', 0) for cat in category_trends.keys()])};
            
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
            const dailyData = {json.dumps(time_trends.get('daily', {}))};
            const weeklyData = {json.dumps(time_trends.get('weekly', {}))};
            const monthlyData = {json.dumps(time_trends.get('monthly', {}))};
            const hourlyData = {json.dumps(time_trends.get('hourly', {}))};
            
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
                    plugins: {{ legend: {{ display: false }} }}
                }}
            }});
            
            // Weekly pattern chart
            const weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
            const weeklyPattern = weekDays.map(day => {{
                const dayData = Object.values(dailyData).filter(d => new Date(d.date || '').getDay() === weekDays.indexOf(day));
                return dayData.reduce((sum, d) => sum + (d.execution_count || 0), 0);
            }});
            
            new Chart(document.getElementById('weeklyPatternChart'), {{
                type: 'radar',
                data: {{
                    labels: weekDays,
                    datasets: [{{
                        label: 'Executions by Day',
                        data: weeklyPattern,
                        backgroundColor: 'rgba(34, 197, 94, 0.2)',
                        borderColor: '#22c55e',
                        pointBackgroundColor: '#22c55e'
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        r: {{ beginAtZero: true }}
                    }}
                }}
            }});
        }}
        
        // Category distribution chart
        function initCategoryDistributionChart() {{
            const categoryData = {json.dumps(list(category_trends.keys()))};
            const categoryExecutions = {json.dumps([category_trends[cat].get('total_executions', 0) for cat in category_trends.keys()])};
            
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

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

"""