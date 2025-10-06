from datetime import datetime
import os
import sys
from dotenv import load_dotenv
from src.data_validation_test_case import DataValidationTestCase
from src.database_config_manager import DatabaseConfigManager
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
    print("🚀 Cross Database Validator - Single Execution, All Report Formats")
    print("=" * 65)
    
    # Execute tests once and collect all data
    print("\n� Executing test suite...")
    test_execution_data = execute_tests_once()
    
    if not test_execution_data:
        print("❌ Test execution failed. Aborting report generation.")
        return
    
    print(f"\n📊 Test execution completed successfully!")
    print(f"   Total: {test_execution_data['summary']['total']}")
    print(f"   ✅ Passed: {test_execution_data['summary']['passed']}")
    print(f"   ❌ Failed: {test_execution_data['summary']['failed']}")
    print(f"   ⏭️ Skipped: {test_execution_data['summary']['skipped']}")
    
    # Generate all report formats from the single execution
    print(f"\n📋 Generating all report formats from single execution...")
    
    # Generate standard markdown report
    print("📄 Generating Standard Markdown report...")
    generate_report_from_data('md', test_execution_data)
    
    # Generate enhanced markdown report
    print("� Generating Enhanced Markdown report...")
    generate_report_from_data('enhanced-md', test_execution_data)
    
    # Generate HTML report with companion enhanced markdown
    print("🌐 Generating HTML report...")
    generate_report_from_data('html', test_execution_data)
    
    # Generate trends analysis from persistent data
    print("📈 Generating Trends Analysis report...")
    generate_trends_report()
    
    print(f"\n🎉 All report formats generated successfully from single execution!")
    print("📁 Check the 'output' folder for all generated reports.")


def execute_tests_once():
    """Execute all tests once and return comprehensive test data."""
    try:
        config_manager = DatabaseConfigManager("configs/database_connections.json")
        test_results = []
        
        print("📄 Reading test cases from Excel file...")
        reader = ExcelTestCaseReader()
        all_test_cases = reader.get_test_case_details()
        
        if not all_test_cases:
            print("❌ Error: Could not read test cases from Excel file.")
            return None
        
        total_test_count = sum(len(df[df["Enable"] == True]) for df in all_test_cases.values())
        print(f"✅ Found {total_test_count} enabled test cases across {len(all_test_cases)} sheets.")
        
        # Create lists to store test objects
        smoke_test_objects = []
        data_validation_test_objects = []
        
        # Process each sheet
        for sheet_name in list(all_test_cases.keys()):
            print(f"\n{'='*50}")
            print(f"✅ ENABLED TESTS ONLY from {sheet_name}:")
            print("="*50)

            # Get enabled tests from this sheet
            smoke_df = all_test_cases.get(sheet_name)
            if smoke_df is not None:
                enabled_smoke_tests = smoke_df[smoke_df["Enable"] == True]
                test_case_records = enabled_smoke_tests.to_dict("records")

                for test_case in test_case_records:
                    test_id = test_case.get("Test_Case_ID", "N/A")
                    test_type = test_case.get("Test_Category", "SMOKE").upper()
                    description = test_case.get("Description", "No description")
                    environment_name = test_case.get("Environment_Name", "")
                    application_name = test_case.get("Application_Name", "")
                    
                    print(f"\n🔍 Processing Test Case: {test_id} - {description}")
                    print(f"   Type: {test_type}")
                    
                    try:
                        if test_type == "DATA_VALIDATION" or test_type in ["SCHEMA_VALIDATION", "ROW_COUNT_VALIDATION", "COL_COL_VALIDATION"]:
                            # Create DataValidationTestCase
                            data_test = DataValidationTestCase(
                                test_id=test_id,
                                Test_Case_ID=test_id,
                                Test_Case_Name=test_case.get("Test_Case_Name", test_id),
                                Environment_Name=environment_name,
                                Application_Name=application_name,
                                Priority=test_case.get("Priority", "Medium"),
                                Test_Category=test_type,
                                Expected_Result=test_case.get("Expected_Result", "PASS"),
                                Description=description,
                                Prerequisites=test_case.get("Prerequisites", ""),
                                Tags=test_case.get("Tags", ""),
                                Parameters=test_case.get("Parameters", ""),
                                Enable=True
                            )
                            data_validation_test_objects.append(data_test)
                            
                            # Execute the test
                            execution_status = data_test.execute_test()
                            
                            # Get detailed execution details (available for data validation tests)
                            try:
                                execution_details = data_test.get_last_execution_details()
                            except AttributeError:
                                execution_details = {}
                            
                            # Create result object
                            result = {
                                'test_id': test_id,
                                'status': execution_status,
                                'description': description,
                                'execution_time': datetime.now(),
                                'execution_details': execution_details,
                                'test_case_obj': data_test,
                                'sheet_name': sheet_name,
                                'test_type': test_type
                            }
                            test_results.append(result)
                            
                        else:
                            # Create SmokeTestCase
                            smoke_test = SmokeTestCase(
                                test_id=test_id,
                                Test_Case_ID=test_id,
                                Environment_Name=environment_name,
                                Application_Name=application_name,
                                Test_Category=test_type,
                                Description=description,
                                Test_Case_Name=test_case.get("Test_Case_Name", test_id),
                                Priority=test_case.get("Priority", "Medium"),
                                Expected_Result=test_case.get("Expected_Result", ""),
                                Prerequisites=test_case.get("Prerequisites", ""),
                                Tags=test_case.get("Tags", ""),
                                Parameters=test_case.get("Parameters", ""),
                                Enable=True
                            )
                            smoke_test_objects.append(smoke_test)
                            
                            # Execute the test
                            execution_status = smoke_test.execute_test()
                            
                            # Create simplified execution details for smoke tests
                            execution_details = {
                                'error_message': '' if execution_status == 'PASSED' else 'Test execution failed',
                                'execution_time_ms': getattr(smoke_test, '_execution_time_ms', 1000),
                                'test_type': 'SMOKE'
                            }
                            
                            # Create result object
                            result = {
                                'test_id': test_id,
                                'status': execution_status,
                                'description': description,
                                'execution_time': datetime.now(),
                                'execution_details': execution_details,
                                'test_case_obj': smoke_test,
                                'sheet_name': sheet_name,
                                'test_type': test_type
                            }
                            test_results.append(result)
                        
                        # Print execution status
                        status_emoji = "✅" if result['status'] == 'PASSED' else "❌" if result['status'] == 'FAILED' else "⏭️"
                        print(f"   {status_emoji} Status: {result['status']}")
                        
                        if result['status'] == 'FAILED' and result['execution_details'].get('error_message'):
                            print(f"   📝 Reason: {result['execution_details']['error_message']}")
                            
                    except Exception as e:
                        print(f"   ❌ Error executing test {test_id}: {e}")
                        # Create a failed result for this test
                        failed_result = {
                            'test_id': test_id,
                            'status': 'FAILED',
                            'description': description,
                            'execution_time': datetime.now(),
                            'execution_details': {'error_message': f"Execution error: {str(e)}"},
                            'test_case_obj': None,
                            'sheet_name': sheet_name,
                            'test_type': test_type
                        }
                        test_results.append(failed_result)
        
        # Calculate summary statistics
        summary = {
            'total': len(test_results),
            'passed': len([r for r in test_results if r['status'] == 'PASSED']),
            'failed': len([r for r in test_results if r['status'] == 'FAILED']),
            'skipped': len([r for r in test_results if r['status'].startswith('SKIPPED')])
        }
        
        # Return comprehensive test execution data
        return {
            'test_results': test_results,
            'summary': summary,
            'timestamp': datetime.now().strftime("%Y%m%d_%H%M%S"),
            'execution_time': datetime.now(),
            'smoke_test_objects': smoke_test_objects,
            'data_validation_test_objects': data_validation_test_objects
        }
        
    except Exception as e:
        print(f"❌ Error during test execution: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_report_from_data(report_format, test_execution_data):
    """Generate a specific report format from pre-executed test data."""
    try:
        # Create the appropriate report generator
        report = create_report_generator(report_format)
        
        # Generate enhanced markdown for HTML linking if needed
        markdown_report_filename = None
        if report_format == 'html':
            # Generate enhanced markdown first for HTML linking
            enhanced_md_report = create_report_generator('enhanced-md')
            
            # Add all test results to enhanced markdown report
            for result in test_execution_data['test_results']:
                add_test_result_to_report(enhanced_md_report, result)
            
            # Save enhanced markdown and get filename
            if enhanced_md_report.save():
                # Extract filename from the full path
                import os
                markdown_report_filename = os.path.basename(enhanced_md_report.output_file)
        
        # Add all test results to the main report
        for result in test_execution_data['test_results']:
            add_test_result_to_report(report, result)
        
        # Add summary for standard markdown format if needed
        if not hasattr(report, 'add_test_result'):
            total = test_execution_data['summary']['total']
            passed = test_execution_data['summary']['passed']
            failed = test_execution_data['summary']['failed']
            skipped = test_execution_data['summary']['skipped']
            
            report.add_separator()
            report.add_heading("Test Execution Summary", level=2)
            report.add_paragraph(f"Total Test Cases: {total}")
            report.add_paragraph(f"Passed Test Cases: {passed} pass rate: {passed / total * 100 if total > 0 else 0:.2f}%")
            report.add_paragraph(f"Failed Test Cases: {failed} fail rate: {failed / total * 100 if total > 0 else 0:.2f}%")
            report.add_paragraph(f"Skipped Test Cases: {skipped} skip rate: {skipped / total * 100 if total > 0 else 0:.2f}%")
        
        # Set markdown filename for HTML reports
        if hasattr(report, 'set_markdown_report_filename') and markdown_report_filename:
            report.set_markdown_report_filename(markdown_report_filename)
        
        # Save the final report
        if report.save():
            print(f"   ✅ {report_format.upper()} report generated: {report.output_file}")
            return report.output_file
        else:
            print(f"   ❌ Failed to save {report_format} report")
            return None
        
    except Exception as e:
        print(f"   ❌ Error generating {report_format} report: {e}")
        import traceback
        traceback.print_exc()
        return None


def add_test_result_to_report(report, result):
    """Add a test result to the appropriate report generator."""
    test_case_obj = result.get('test_case_obj')
    execution_details = result.get('execution_details', {})
    
    if hasattr(report, 'add_test_result'):
        # Extract failure details for HTML/Enhanced report
        soft_failures = execution_details.get('soft_failures', [])
        hard_failures = execution_details.get('hard_failures', [])
        error_message = execution_details.get('error_message', '')
        
        # Format failure details for display
        failure_details = ""
        if result['status'] == "FAILED":
            if 'source_count' in execution_details:
                # Row count validation failure
                failure_details = f"Row count variance: {execution_details.get('variance_percent', 0):.1f}% (tolerance: {execution_details.get('tolerance_percent', 0)}%)"
            elif error_message:
                failure_details = error_message
        
        # Check if this is HTML report generator (has enhanced features)
        if hasattr(report, 'markdown_report_filename'):
            # HTML Report Generator with full feature set
            report.add_test_result(
                sheet_name=result.get('sheet_name', 'Unknown'),
                test_case_id=test_case_obj.test_case_id if test_case_obj else result.get('test_id', 'N/A'),
                test_case_name=test_case_obj.test_case_name if test_case_obj else result.get('description', 'N/A'),
                status=result['status'],
                category=getattr(test_case_obj, 'category', result.get('test_type', 'SMOKE')),
                failure_details=failure_details,
                soft_failures=soft_failures,
                hard_failures=hard_failures,
                error_message=error_message
            )
        else:
            # Enhanced Markdown Report Generator with basic feature set
            report.add_test_result(
                sheet_name=result.get('sheet_name', 'Unknown'),
                test_case_id=test_case_obj.test_case_id if test_case_obj else result.get('test_id', 'N/A'),
                test_case_name=test_case_obj.test_case_name if test_case_obj else result.get('description', 'N/A'),
                status=result['status'],
                category=getattr(test_case_obj, 'category', result.get('test_type', 'SMOKE')),
                execution_time=f"{getattr(test_case_obj, '_execution_time_ms', 1000)}ms",
                error_message=error_message
            )
    else:
        # Old format for standard markdown
        report.add_heading(f"Test Case ID: {test_case_obj.test_case_id if test_case_obj else result.get('test_id', 'N/A')}", level=3)
        report.add_heading(f"Test Case: {test_case_obj.test_case_name if test_case_obj else result.get('description', 'N/A')}", level=4)
        report.add_heading(f"Status: {result['status']}", level=4)


def generate_trends_report():
    """Generate trends analysis from persistent data."""
    try:
        from src.persistent_trends_analyzer import PersistentTrendsAnalyzer
        from src.enhanced_trends_html_report_generator import EnhancedTrendsHTMLReportGenerator
        
        # Use persistent trends analyzer
        trends_analyzer = PersistentTrendsAnalyzer()
        trends_data = trends_analyzer.generate_comprehensive_trends()
        
        if 'error' in trends_data:
            print(f"   ⚠️ {trends_data['message']}")
            print("   💡 Run some test executions first to generate trend data!")
            return None
        
        # Generate enhanced interactive HTML report from persistent trends data
        generator = EnhancedTrendsHTMLReportGenerator()
        output_file = generator.generate_comprehensive_trends_report(trends_data)
        print(f"   ✅ Trends analysis report generated: {output_file}")
        return output_file
        
    except Exception as e:
        print(f"   ❌ Error generating trends report: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_test_execution_report(report_format="md"):
    """Legacy function - kept for backward compatibility.
    
    Note: This function is no longer used by main() which now uses
    the optimized execute_tests_once() approach for better efficiency.
    """
    
    total_test_cases = 0
    passed_test_cases = 0
    failed_test_cases = 0
    skipped_test_cases = 0
    
    # Create appropriate report generator
    report = create_report_generator(report_format)
    reader = ExcelTestCaseReader()
    
    # For HTML reports, also generate enhanced markdown report for linking
    markdown_report_filename = None
    if report_format == 'html':
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        markdown_report_filename = f"Test_Execution_Results_Enhanced_{timestamp}.md"

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
                    
                    # Get detailed execution results
                    execution_details = test_case_obj.get_last_execution_details()
                    
                    # Add to report (for new report generators)
                    if hasattr(report, 'add_test_result'):
                        # Extract failure details for HTML report
                        soft_failures = execution_details.get('soft_failures', [])
                        hard_failures = execution_details.get('hard_failures', [])
                        error_message = execution_details.get('error_message', '')
                        
                        # Format failure details for display
                        failure_details = ""
                        if execution_status == "FAILED":
                            if 'source_count' in execution_details:
                                # Row count validation failure
                                failure_details = f"Row count variance: {execution_details.get('variance_percent', 0):.1f}% (tolerance: {execution_details.get('tolerance_percent', 0)}%)"
                            elif error_message:
                                failure_details = error_message
                        
                        # Check if this is HTML report generator (has enhanced features)
                        if hasattr(report, 'markdown_report_filename'):
                            # HTML Report Generator with full feature set
                            report.add_test_result(
                                sheet_name=sheet_name,
                                test_case_id=test_case_obj.test_case_id,
                                test_case_name=test_case_obj.test_case_name,
                                status=execution_status,
                                category=getattr(test_case_obj, 'category', 'DATAVALIDATION'),
                                failure_details=failure_details,
                                soft_failures=soft_failures,
                                hard_failures=hard_failures,
                                error_message=error_message
                            )
                        else:
                            # Enhanced Markdown Report Generator with basic feature set
                            report.add_test_result(
                                sheet_name=sheet_name,
                                test_case_id=test_case_obj.test_case_id,
                                test_case_name=test_case_obj.test_case_name,
                                status=execution_status,
                                category=getattr(test_case_obj, 'category', 'DATAVALIDATION'),
                                execution_time=f"{getattr(test_case_obj, '_execution_time_ms', 1000)}ms",
                                error_message=error_message
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
                        # Check if this is HTML report generator (has enhanced features)
                        if hasattr(report, 'markdown_report_filename'):
                            # HTML Report Generator with full feature set
                            report.add_test_result(
                                sheet_name=sheet_name,
                                test_case_id=test_case_obj.test_case_id,
                                test_case_name=test_case_obj.test_case_name,
                                status=execution_status,
                                category=test_case_obj.test_category or 'UNKNOWN'
                            )
                        else:
                            # Enhanced Markdown Report Generator with basic feature set
                            report.add_test_result(
                                sheet_name=sheet_name,
                                test_case_id=test_case_obj.test_case_id,
                                test_case_name=test_case_obj.test_case_name,
                                status=execution_status,
                                category=test_case_obj.test_category or 'UNKNOWN',
                                execution_time=f"{getattr(test_case_obj, '_execution_time_ms', 1000)}ms"
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
    if hasattr(report, 'set_markdown_report_filename') and markdown_report_filename:
        report.set_markdown_report_filename(markdown_report_filename)
    
    if report.save():
        print("Test report saved successfully.")
        
        # Generate enhanced markdown report for HTML format (for linking)
        if report_format == 'html' and markdown_report_filename:
            print("📄 Generating companion enhanced markdown report for detailed analysis...")
            try:
                # Create an enhanced markdown report
                md_report = EnhancedMarkdownReportGenerator(
                    title="Test Execution Results",
                    output_file=f"output\\{markdown_report_filename}"
                )
                
                # Add all test results to enhanced markdown report
                for sheet_name in all_test_cases.keys():
                    if sheet_name.lower() == "datavalidations":
                        test_objects = data_validation_test_objects
                    else:
                        test_objects = smoke_test_objects
                    
                    for test_obj in test_objects:
                        execution_status = getattr(test_obj, '_last_execution_status', 'UNKNOWN')
                        
                        # Add enhanced test result with detailed information
                        md_report.add_test_result(
                            test_case_id=test_obj.test_case_id,
                            test_case_name=test_obj.test_case_name,
                            status=execution_status,
                            category=getattr(test_obj, 'test_category', 'UNKNOWN'),
                            execution_time=f"{getattr(test_obj, '_execution_time_ms', 1000)}ms",
                            sheet_name=sheet_name
                        )
                
                if md_report.save():
                    print(f"📄 Companion enhanced markdown report saved: output\\{markdown_report_filename}")
                else:
                    print("⚠️ Failed to save companion enhanced markdown report")
                    
            except Exception as e:
                print(f"⚠️ Error generating companion markdown report: {e}")
                # Don't fail the main execution if markdown generation fails
        
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