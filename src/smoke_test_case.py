from random import choice, random
import pandas as pd

class SmokeTestCase:
    """
    Represents a single smoke test case loaded from an enabled row in the Excel sheet,
    with explicit attributes matching the DataFrame columns.
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

    def execute_test(self) -> bool:
        # Simulate test execution logic
        print(f"Executing test: {self.test_case_name}")
        return choice([True, False])

    def log_execution_status(self, execution_status):
        """Logs the execution status of the test case."""
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
