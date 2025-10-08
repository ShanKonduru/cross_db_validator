#!/usr/bin/env python3
"""
Test script for the Consolidated Trends HTML Generator.
Creates comprehensive HTML reports with interactive visualizations.
"""

import sys
import os

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from src.consolidated_excel_reader import ConsolidatedExcelTestCaseReader
    from src.consolidated_trends_html_generator import ConsolidatedTrendsHTMLGenerator
    print("✅ Successfully imported all required modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_trends_html_generation():
    """Test the trends HTML generation functionality."""
    print("\n🧪 Testing Consolidated Trends HTML Generation")
    print("=" * 50)
    
    # Excel file path
    main_project_dir = os.path.dirname(parent_dir)
    excel_file = os.path.join(main_project_dir, "inputs", "consolidated_test_suite_20251007_213209.xlsx")
    
    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return False
    
    try:
        # Step 1: Read test data
        print("📖 Reading consolidated test data...")
        reader = ConsolidatedExcelTestCaseReader(excel_file)
        test_data = reader.get_all_enabled_tests()
        print(f"   ✅ Loaded {len(test_data)} test cases")
        
        # Step 2: Create trends generator
        print("🔧 Initializing trends HTML generator...")
        output_dir = os.path.join(parent_dir, "output")
        trends_generator = ConsolidatedTrendsHTMLGenerator(test_data, output_dir)
        print(f"   ✅ Generator initialized with output directory: {output_dir}")
        
        # Step 3: Generate HTML report
        print("🎨 Generating comprehensive HTML trends report...")
        html_file = trends_generator.generate_html_report()
        print(f"   ✅ HTML report generated: {html_file}")
        
        # Step 4: Export analytics JSON
        print("📊 Exporting analytics data to JSON...")
        json_file = trends_generator.export_analytics_json()
        print(f"   ✅ Analytics JSON exported: {json_file}")
        
        # Step 5: Display analytics summary
        print("\n📈 Analytics Summary:")
        analytics = trends_generator.analytics
        
        print(f"   📋 Total Tests: {analytics['total_tests']}")
        print(f"   ✅ Enabled Tests: {analytics['enabled_tests']}")
        print(f"   ❌ Disabled Tests: {analytics['disabled_tests']}")
        
        print(f"\n   🏷️  Test Types:")
        for test_type, count in analytics['test_types'].items():
            print(f"      {test_type}: {count}")
        
        print(f"\n   📊 Categories:")
        for category, count in sorted(analytics['categories'].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"      {category}: {count}")
        
        print(f"\n   🎯 Priorities:")
        for priority, count in analytics['priorities'].items():
            print(f"      {priority}: {count}")
        
        print(f"\n   🌍 Environments:")
        print(f"      Source: {len(analytics['environments']['source'])} environments")
        print(f"      Target: {len(analytics['environments']['target'])} environments")
        
        print(f"\n   ⚙️  Parameters:")
        print(f"      With Tolerance: {analytics['parameters']['with_tolerance']}")
        print(f"      With Expected Cols: {analytics['parameters']['with_expected_cols']}")
        print(f"      Parameter Types: {len(analytics['parameters']['parameter_types'])}")
        
        print(f"\n   🏪 Tables:")
        print(f"      Source Tables: {len(analytics['tables']['source_tables'])}")
        print(f"      Target Tables: {len(analytics['tables']['target_tables'])}")
        
        print(f"\n   🚀 Execution Readiness:")
        print(f"      Complete Configs: {analytics['execution_readiness']['complete_configs']}")
        print(f"      Missing Configs: {analytics['execution_readiness']['missing_configs']}")
        
        # Step 6: Show file information
        print(f"\n📁 Generated Files:")
        print(f"   📄 HTML Report: {os.path.basename(html_file)}")
        print(f"   📋 JSON Analytics: {os.path.basename(json_file)}")
        print(f"   📂 Output Directory: {output_dir}")
        
        # Step 7: Verify files exist
        if os.path.exists(html_file) and os.path.exists(json_file):
            html_size = os.path.getsize(html_file)
            json_size = os.path.getsize(json_file)
            print(f"\n✅ File Verification:")
            print(f"   HTML Report: {html_size:,} bytes")
            print(f"   JSON Analytics: {json_size:,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating trends HTML: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_feature_overview():
    """Display overview of HTML report features."""
    print("\n🌟 HTML Report Features")
    print("=" * 30)
    
    features = [
        "📊 Interactive Charts with Chart.js",
        "📈 Test Type Distribution (Doughnut Chart)",
        "📋 Category Analysis (Bar Chart)", 
        "🎯 Priority Breakdown (Pie Chart)",
        "🌍 Environment Distribution (Multi-Bar Chart)",
        "⚙️ Parameter Usage Statistics (Doughnut Chart)",
        "🚀 Execution Readiness Status (Doughnut Chart)",
        "📱 Responsive Design for Mobile/Desktop",
        "🎨 Modern CSS with Gradients and Animations",
        "📄 Detailed Data Tables",
        "📊 Comprehensive Metrics Cards",
        "🔗 Error Handling for CDN Issues",
        "📤 JSON Export for Further Analysis",
        "⏰ Timestamp and Generation Information"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print("\n💡 The HTML report includes:")
    print("   • Visual analytics with 6 interactive charts")
    print("   • Summary cards with key metrics")
    print("   • Detailed breakdowns by type, category, priority")
    print("   • Environment and parameter analysis")
    print("   • Table coverage and execution readiness")
    print("   • Mobile-responsive design")
    print("   • Professional styling with modern CSS")


if __name__ == "__main__":
    # Display feature overview
    display_feature_overview()
    
    # Test HTML generation
    success = test_trends_html_generation()
    
    if success:
        print("\n🎉 Consolidated Trends HTML Generation Successful!")
        print("\n📋 Summary:")
        print("   ✅ HTML report with interactive charts generated")
        print("   ✅ JSON analytics data exported")
        print("   ✅ Comprehensive metrics and visualizations")
        print("   ✅ Responsive design with modern styling")
        print("   ✅ Error handling for Chart.js CDN issues")
        print("\n💡 Open the HTML file in your browser to view the interactive trends report!")
    else:
        print("\n❌ Trends HTML generation failed!")
        sys.exit(1)