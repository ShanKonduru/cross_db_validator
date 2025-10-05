#!/usr/bin/env python3
"""
Generate Test Execution Trends Report

This script analyzes historical test execution reports and generates comprehensive
trends analysis with visualizations for hourly, daily, weekly, monthly, and yearly patterns.

Usage:
    python generate_trends_report.py [output_format]
    
    output_format: html, json (default: html)
"""

import sys
import os
from datetime import datetime
from src.trends_html_report_generator import TrendsHTMLReportGenerator
from src.test_trends_analyzer import TestExecutionTrendsAnalyzer


def main():
    """Main function to generate trends report."""
    print("🚀 Cross Database Validator - Trends Analysis Generator")
    print("="*60)
    
    # Determine output format
    output_format = 'html'
    if len(sys.argv) > 1:
        format_arg = sys.argv[1].lower()
        if format_arg in ['html', 'json']:
            output_format = format_arg
        else:
            print(f"❌ Invalid format '{format_arg}'. Using default 'html'.")
    
    print(f"📊 Generating {output_format.upper()} trends report...")
    
    try:
        if output_format == 'html':
            # Generate HTML trends report
            generator = TrendsHTMLReportGenerator()
            output_file = generator.generate_trends_report()
            
            print(f"✅ HTML Trends report generated successfully!")
            print(f"📄 Report saved to: {os.path.abspath(output_file)}")
            print(f"🌐 Open the file in your browser to view the interactive dashboard!")
            
        elif output_format == 'json':
            # Generate JSON trends data
            analyzer = TestExecutionTrendsAnalyzer()
            trends_data = analyzer.generate_trends_analysis()
            output_file = analyzer.export_trends_data()
            
            print(f"✅ JSON Trends data generated successfully!")
            print(f"📄 Data saved to: {os.path.abspath(output_file)}")
            print(f"📊 Use this data for custom analysis or integration with other tools.")
    
    except Exception as e:
        print(f"❌ Error generating trends report: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)