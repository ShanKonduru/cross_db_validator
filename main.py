from datetime import datetime
import os
from dotenv import load_dotenv
from src.data_validation_test_case import DataValidationTestCase
from src.excel_test_case_reader import ExcelTestCaseReader
from src.markdown_report_generator import MarkdownReportGenerator
from src.smoke_test_case import SmokeTestCase

load_dotenv()
# openai_api_key = os.getenv("OPENAI_API_KEY")

def main():
# 1. Instantiate the generator
    report = MarkdownReportGenerator(
        title="Test Execution Results", 
        output_file=f"output\\Test_Execution_Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    )
    reader = ExcelTestCaseReader()

    all_test_cases = reader.get_test_case_details()

    # 2. Create an empty list to store the SmokeTestCase and DataValidationTestCase objects
    smoke_test_objects = []
    data_validation_test_objects = []

    # To get a list of all sheets that were processed:
    print("\nList of enabled sheets processed:")
    for sheet_name in list(all_test_cases.keys()):
        print(f" - {sheet_name}")
        report.add_heading(f"Data from {sheet_name}:", level=2)

        # To view the data from a specific enabled sheet:
        print(f"\nData from {sheet_name }:")
        smoke_df = all_test_cases.get(sheet_name)

        if smoke_df is not None:
            enabled_smoke_tests = smoke_df[smoke_df["Enable"] == True]

            print("\n" + "=" * 50)
            print(f"✅ ENABLED TESTS ONLY from {sheet_name}:")
            print("=" * 50)
            # print(enabled_smoke_tests)

            # 1. Convert the filtered DataFrame to a list of dictionaries (one dictionary per row)
            test_case_records = enabled_smoke_tests.to_dict("records")

            # 3. Iterate over the list of records and instantiate the class
            for record in test_case_records:
                if sheet_name.lower() == "datavalidation":
                    test_case_obj = DataValidationTestCase(**record)
                    report.add_heading(f"Test Case ID: {test_case_obj.test_case_id}", level=3)
                    report.add_heading(f"Test Case: {test_case_obj.test_case_name}", level=4)
                    data_validation_test_objects.append(test_case_obj)
                    execution_status = test_case_obj.execute_test()
                    report.add_heading(f"Status: {execution_status }", level=4)
                    test_case_obj.log_execution_status(execution_status)
                elif sheet_name.lower() == "smoke":
                    test_case_obj = SmokeTestCase(**record)
                    report.add_heading(f"Test Case ID: {test_case_obj.test_case_id}", level=3)
                    report.add_heading(f"Test Case: {test_case_obj.test_case_name}", level=4)
                    smoke_test_objects.append(test_case_obj)
                    execution_status = test_case_obj.execute_test()
                    report.add_heading(f"Status: {execution_status }", level=4)
                    test_case_obj.log_execution_status(execution_status)
        else:
            print(
                f"\nError: '{sheet_name}' sheet data was not found or failed to load."
            )
            
    report.save()

if __name__ == "__main__":
    main()
