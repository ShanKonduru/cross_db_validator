from datetime import datetime
import os
import sys
from dotenv import load_dotenv
from src.data_validation_test_case import DataValidationTestCase
from src.excel_test_case_reader import ExcelTestCaseReader
from src.markdown_report_generator import MarkdownReportGenerator
from src.html_report_generator import HTMLReportGenerator
from src.enhanced_markdown_report_generator import EnhancedMarkdownReportGenerator
from src.smoke_test_case import SmokeTestCase
from src.test_execution_data_collector import TestExecutionDataCollector
from src.execution_data_persistence import ExecutionDataPersistence

load_dotenv()


def get_report_format():
    """Get the desired report format from user or command line arguments."""
    if len(sys.argv) > 1:
        format_arg = sys.argv[1].lower()
        if format_arg in ['html', 'md', 'enhanced-md', 'trends']:
            return format_arg
    
    print("\n🎨 Choose Report Format:")
    print("1. 📄 Standard Markdown (original)")
    print("2. 🚀 Enhanced Markdown (with emojis, tables, charts)")
    print("3. 🌐 HTML Report (Bootstrap dashboard with charts)")
    print("4. 📈 Trends Analysis (Historical execution trends)")
    
    while True:
        choice = input("\nEnter your choice (1-4) or format name (html/md/enhanced-md/trends): ").strip().lower()
        
        if choice == '1' or choice == 'md':
            return 'md'
        elif choice == '2' or choice == 'enhanced-md':
            return 'enhanced-md'
        elif choice == '3' or choice == 'html':
            return 'html'
        elif choice == '4' or choice == 'trends':
            return 'trends'
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, 4, or the format name.")


def create_report_generator(report_format):
    """Create appropriate report generator based on format."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if report_format == 'html':
        return HTMLReportGenerator(
            title="Cross Database Validator - Test Execution Report",
            output_file=f"output\\Test_Execution_Results_{timestamp}.html"
        )
    elif report_format == 'enhanced-md':
        return EnhancedMarkdownReportGenerator(
            title="Cross Database Validator - Test Execution Report",
            output_file=f"output\\Test_Execution_Results_Enhanced_{timestamp}.md"
        )
    else:  # default to standard markdown
        return MarkdownReportGenerator(
            title="Test Execution Results",
            output_file=f"output\\Test_Execution_Results_{timestamp}.md"
        )


def main():
    # Get report format preference
    report_format = get_report_format()
    print(f"\n📊 Generating {report_format.upper()} report...")
    
    # Handle trends analysis separately
    if report_format == 'trends':
        from src.persistent_trends_analyzer import PersistentTrendsAnalyzer
        from src.enhanced_trends_html_report_generator import EnhancedTrendsHTMLReportGenerator
        print("📈 Analyzing historical test execution trends from persistent data...")
        try:
            # Use persistent trends analyzer instead of file-based one
            trends_analyzer = PersistentTrendsAnalyzer()
            trends_data = trends_analyzer.generate_comprehensive_trends()
            
            if 'error' in trends_data:
                print(f"⚠️ {trends_data['message']}")
                print("💡 Run some test executions first to generate trend data!")
                return
            
            # Generate enhanced interactive HTML report from persistent trends data
            generator = EnhancedTrendsHTMLReportGenerator()
            output_file = generator.generate_comprehensive_trends_report(trends_data)
            print(f"✅ Enhanced comprehensive trends analysis report generated successfully!")
            print(f"📄 Report saved to: {output_file}")
            print(f"🌐 Open the HTML file in your browser to view the comprehensive trends dashboard!")
            return
        except Exception as e:
            print(f"❌ Error generating persistent trends report: {e}")
            import traceback
            traceback.print_exc()
            return
    
    total_test_cases = 0
    passed_test_cases = 0
    failed_test_cases = 0
    skipped_test_cases = 0
    
    # Create appropriate report generator
    report = create_report_generator(report_format)
    reader = ExcelTestCaseReader()

    all_test_cases = reader.get_test_case_details()

    # Create an empty list to store the SmokeTestCase and DataValidationTestCase objects
    smoke_test_objects = []
    data_validation_test_objects = []

    for sheet_name in list(all_test_cases.keys()):
        print(f"\n{'='*50}")
        print(f"✅ ENABLED TESTS ONLY from {sheet_name}:")
        print("="*50)

        # To view the data from a specific enabled sheet:
        smoke_df = all_test_cases.get(sheet_name)

        if smoke_df is not None:
            enabled_smoke_tests = smoke_df[smoke_df["Enable"] == True]

            # For old markdown format, add section header
            if not hasattr(report, 'add_test_result'):
                report.add_heading(f"Data from {sheet_name}:", level=2)

            # Convert the filtered DataFrame to a list of dictionaries (one dictionary per row)
            test_case_records = enabled_smoke_tests.to_dict("records")

            # Iterate over the list of records and instantiate the class
            for record in test_case_records:
                total_test_cases += 1
                
                if sheet_name.lower() == "datavalidations":
                    test_case_obj = DataValidationTestCase(**record)
                    data_validation_test_objects.append(test_case_obj)
                    
                    # Execute the test case
                    execution_status = test_case_obj.execute_test()
                    
                    # Add to report (for new report generators)
                    if hasattr(report, 'add_test_result'):
                        report.add_test_result(
                            sheet_name=sheet_name,
                            test_case_id=test_case_obj.test_case_id,
                            test_case_name=test_case_obj.test_case_name,
                            status=execution_status,
                            category=getattr(test_case_obj, 'category', 'DATAVALIDATION')
                        )
                    else:
                        # Old format for standard markdown
                        report.add_heading(f"Test Case ID: {test_case_obj.test_case_id}", level=3)
                        report.add_heading(f"Test Case: {test_case_obj.test_case_name}", level=4)
                        report.add_heading(f"Status: {execution_status}", level=4)
                    
                    # Update counters
                    if execution_status == "PASSED":
                        passed_test_cases += 1
                    elif execution_status == "FAILED":
                        failed_test_cases += 1
                    elif execution_status == "SKIPPED":
                        skipped_test_cases += 1

                else:  # SMOKE tests
                    test_case_obj = SmokeTestCase(**record)
                    smoke_test_objects.append(test_case_obj)
                    
                    print(f"Executing test: {test_case_obj.test_case_name} (Category: {test_case_obj.test_category})")
                    execution_status = test_case_obj.execute_test()
                    
                    # Add to report (for new report generators)
                    if hasattr(report, 'add_test_result'):
                        report.add_test_result(
                            sheet_name=sheet_name,
                            test_case_id=test_case_obj.test_case_id,
                            test_case_name=test_case_obj.test_case_name,
                            status=execution_status,
                            category=test_case_obj.test_category or 'UNKNOWN'
                        )
                    else:
                        # Old format for standard markdown
                        report.add_heading(f"Test Case ID: {test_case_obj.test_case_id}", level=3)
                        report.add_heading(f"Test Case: {test_case_obj.test_case_name}", level=4)
                        report.add_heading(f"Status: {execution_status}", level=4)
                    
                    # Update counters
                    if execution_status == "PASSED":
                        passed_test_cases += 1
                    elif execution_status == "FAILED":
                        failed_test_cases += 1
                    elif execution_status == "SKIPPED":
                        skipped_test_cases += 1

    # Generate summary for old markdown format if needed
    if not hasattr(report, 'add_test_result'):
        report.add_heading("Summary:", level=2)
        report.add_paragraph(f"Total Test Cases: {total_test_cases}")
        report.add_paragraph(f"Passed Test Cases: {passed_test_cases} pass rate: {passed_test_cases / total_test_cases * 100 if total_test_cases > 0 else 0:.2f}%")
        report.add_paragraph(f"Failed Test Cases: {failed_test_cases} fail rate: {failed_test_cases / total_test_cases * 100 if total_test_cases > 0 else 0:.2f}%")
        report.add_paragraph(f"Skipped Test Cases: {skipped_test_cases} skip rate: {skipped_test_cases / total_test_cases * 100 if total_test_cases > 0 else 0:.2f}%")

    # Save the report
    if report.save():
        print("Test report saved successfully.")
        
        # 💾 PERSISTENT DATA COLLECTION - NEW FEATURE
        print("\n💾 Saving execution data to persistent storage...")
        try:
            execution_start_time = datetime.now()
            
            # Collect comprehensive execution data
            data_collector = TestExecutionDataCollector()
            
            # Prepare execution results data structure
            execution_results = {
                'total_duration': 0,  # Could be enhanced to track actual duration
                'sheet_results': {}
            }
            
            # Organize results by sheets
            for sheet_name in all_test_cases.keys():
                sheet_test_cases = []
                
                # Get test objects for this sheet
                if sheet_name.lower() == "datavalidations":
                    test_objects = data_validation_test_objects
                else:
                    test_objects = smoke_test_objects
                
                # Convert test objects to results format
                for test_obj in test_objects:
                    # Get the last execution status
                    status = getattr(test_obj, '_last_execution_status', 'UNKNOWN')
                    
                    sheet_test_cases.append({
                        'test_id': test_obj.test_case_id,
                        'test_name': test_obj.test_case_name,
                        'status': status,
                        'execution_time_ms': getattr(test_obj, '_execution_time_ms', 1000),  # Default 1s
                        'sheet_name': sheet_name
                    })
                
                execution_results['sheet_results'][sheet_name] = {
                    'test_cases': sheet_test_cases
                }
            
            # Create comprehensive execution record
            execution_record = data_collector.create_execution_record(
                execution_results=execution_results,
                execution_start_time=execution_start_time
            )
            
            # Save to persistent storage
            persistence = ExecutionDataPersistence()
            if persistence.save_execution_record(execution_record):
                print("✅ Execution data saved to persistent storage successfully!")
                print("📈 Data will be used for future trends analysis")
            else:
                print("⚠️ Failed to save execution data to persistent storage")
                
        except Exception as e:
            print(f"⚠️ Error saving to persistent storage: {e}")
            # Don't fail the main execution if persistence fails
            pass
        
        # Print summary
        print(f"\n📊 Test Execution Summary:")
        print(f"   Total: {total_test_cases}")
        print(f"   ✅ Passed: {passed_test_cases}")
        print(f"   ❌ Failed: {failed_test_cases}")
        print(f"   ⏭️ Skipped: {skipped_test_cases}")
        
        if report_format == 'html':
            print(f"\n🌐 Open the HTML report in your browser to view the interactive dashboard!")
    else:
        print("Failed to save test report.")


if __name__ == "__main__":
    main()