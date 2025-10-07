from random import choice, random
import pandas as pd
import sys
import os
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from src.database_test_framework import DatabaseTestFactory

class SmokeTestCase:
    """
    Represents a single smoke test case loaded from an enabled row in the Excel sheet,
    with explicit attributes matching the DataFrame columns.
    Enhanced with execution tracking for persistent trends analysis.
    """

    def __init__(self, **kwargs):
        self.enable = kwargs.get("Enable")  # Should be True
        self.test_case_id = kwargs.get("Test_Case_ID")
        self.test_case_name = kwargs.get("Test_Case_Name")
        self.application_name = kwargs.get("Application_Name")
        self.environment_name = kwargs.get("Environment_Name")
        self.priority = kwargs.get("Priority")
        self.test_category = kwargs.get("Test_Category")
        self.expected_result = kwargs.get("Expected_Result")
        self.description = kwargs.get("Description")
        self.prerequisites = kwargs.get("Prerequisites")

        # 2. Parsing for Structured Data (Tags and Parameters)
        self.tags = self._parse_tags(kwargs.get("Tags"))
        self.parameters = self._parse_parameters(kwargs.get("Parameters"))
        
        # 3. Execution tracking for persistent trends
        self._last_execution_status = None
        self._execution_time_ms = 0
        self._execution_start_time = None

    def execute_test(self) -> str:
        """
        Execute the smoke test based on the test category.
        Uses the database test framework to perform actual database operations.
        Enhanced with execution time tracking and expected vs actual result evaluation.
        """
        self._execution_start_time = time.time()
        
        try:
            print(f"Executing test: {self.test_case_name} (Category: {self.test_category})")
            
            # Validate required parameters
            if not self.application_name or not self.environment_name:
                self._record_execution_result("SKIPPED")
                return "SKIPPED: Missing application or environment name"
            
            if not self.test_category:
                self._record_execution_result("SKIPPED")
                return "SKIPPED: Missing test category"
            
            # Create the appropriate test instance using the factory
            test_instance = DatabaseTestFactory.create_test(
                test_category=self.test_category,
                environment=self.environment_name,
                application=self.application_name,
                parameters=self.parameters
            )
            
            if not test_instance:
                return f"SKIPPED: Unsupported test category '{self.test_category}'"
            
            # Execute the test and get functional result
            functional_result = test_instance.execute()
            
            # Determine the basic functional outcome
            if functional_result.startswith("PASSED"):
                test_passed_functionally = True
                basic_status = "PASSED"
            elif functional_result.startswith("SKIPPED"):
                # For skipped tests, return as-is without expected result comparison
                print(f"⏭️  {self.test_case_name}: {functional_result}")
                self._record_execution_result("SKIPPED")
                return "SKIPPED"
            else:  # FAILED
                test_passed_functionally = False
                basic_status = "FAILED"
            
            # Compare with expected result (if available)
            if hasattr(self, 'expected_result') and self.expected_result:
                expected_to_pass = (self.expected_result.upper() == "PASS")
                
                # Determine final status based on expected vs actual
                if expected_to_pass and test_passed_functionally:
                    # Expected to pass and did pass
                    final_result = "PASSED"
                    print(f"✅ {self.test_case_name}: PASSED (Expected: PASS, Result: PASS)")
                elif expected_to_pass and not test_passed_functionally:
                    # Expected to pass but failed
                    final_result = "FAILED"
                    print(f"❌ {self.test_case_name}: FAILED (Expected: PASS, Result: FAIL)")
                elif not expected_to_pass and not test_passed_functionally:
                    # Expected to fail and did fail (negative test case)
                    final_result = "PASSED"
                    print(f"✅ {self.test_case_name}: PASSED (Expected: FAIL, Result: FAIL) - Negative test case worked correctly")
                else:
                    # Expected to fail but passed
                    final_result = "FAILED"
                    print(f"❌ {self.test_case_name}: FAILED (Expected: FAIL, Result: PASS) - Negative test case should have failed")
                    
                self._record_execution_result(final_result)
                return final_result
            else:
                # No expected result specified, return basic functional result
                if basic_status == "PASSED":
                    print(f"✅ {self.test_case_name}: {functional_result}")
                else:
                    print(f"❌ {self.test_case_name}: {functional_result}")
                    
                self._record_execution_result(basic_status)
                return basic_status
                
        except Exception as e:
            error_msg = f"FAILED: Unexpected error during test execution - {str(e)}"
            print(f"❌ {self.test_case_name}: {error_msg}")
            self._record_execution_result("FAILED")
            return error_msg

    def _record_execution_result(self, status: str):
        """Record execution result and timing for persistent trends analysis."""
        self._last_execution_status = status
        if self._execution_start_time:
            execution_time = time.time() - self._execution_start_time
            self._execution_time_ms = int(execution_time * 1000)  # Convert to milliseconds

    def log_execution_status(self, execution_status):
        """Logs the execution status of the test case."""
        # Handle the case where execution_status is a string (new implementation)
        if isinstance(execution_status, str):
            if execution_status.upper().startswith("PASSED"):
                self.status = "PASSED"
            elif execution_status.upper().startswith("SKIPPED"):
                self.status = "SKIPPED"
            else:
                self.status = "FAILED"
        else:
            # Legacy boolean handling
            self.status = "PASSED" if execution_status else "FAILED"
        
        print(f"Test Case '{self.test_case_name}' Execution Status: {self.status}")

    def _parse_tags(self, tags_str):
        """Converts the comma-separated Tags string into a list of strings."""
        # Use str() to handle potential NaN/float values from Excel
        if isinstance(tags_str, (str, float)) and pd.notna(tags_str):
            return [tag.strip() for tag in str(tags_str).split(",") if tag.strip()]
        return []

    def _parse_parameters(self, params_str):
        """Converts the key=value,key=value Parameters string into a dictionary."""
        params = {}
        # Use str() and pd.notna() to handle NaN/missing values
        if isinstance(params_str, (str, float)) and pd.notna(params_str):
            for item in str(params_str).split(","):
                if "=" in item:
                    try:
                        key, value = item.split("=", 1)
                        params[key.strip()] = value.strip()
                    except ValueError:
                        # Handle cases where split fails unexpectedly
                        pass
        return params

    def __repr__(self):
        """A friendly string representation of the object."""
        return f"<SmokeTestCase ID='{self.test_case_id}' Priority='{self.priority}' Tags={self.tags}>"
