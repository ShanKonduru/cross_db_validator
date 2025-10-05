import pandas as pd
import numpy as np


class ExcelTestCaseReader:
    """
    Reads an Excel workbook, identifies enabled sheets from a 'Controller'
    sheet, and extracts data (test cases) from those enabled sheets.
    """

    def __init__(
        self,
        file_path ="inputs\\test_suite.xlsx",
        controller_sheet_name="CONTROLLER",
        sheet_name_col="SHEET_NAME",
        enable_col="ENABLE",
        enable_value="TRUE",
    ):
        """
        Initializes the reader with file path and configuration.

        Args:
            file_path (str): Path to the Excel workbook.
            controller_sheet_name (str): Name of the sheet that lists other sheets.
            sheet_name_col (str): Column name in the controller sheet holding the sheet names.
            enable_col (str): Column name in the controller sheet for the enable status.
            enable_value (str): Value in the enable column that means 'enabled'.
        """
        self.file_path = file_path
        self.controller_sheet = controller_sheet_name
        self.sheet_name_col = sheet_name_col
        self.enable_col = enable_col
        self.enable_value = enable_value
        self.enabled_sheets = []
        self.test_case_data = {}

    def _get_enabled_sheets(self):
        """
        Reads the controller sheet and identifies which sheets are enabled.
        """
        try:
            # Read only the necessary columns from the Controller sheet
            df_controller = pd.read_excel(
                self.file_path,
                sheet_name=self.controller_sheet,
                usecols=[self.sheet_name_col, self.enable_col],
            )

            # Filter for enabled sheets, convert names to a list, and clean up (e.g., remove NaNs)
            self.enabled_sheets = (
                df_controller[
                    df_controller[self.enable_col].astype(str).str.lower()
                    == self.enable_value.lower()
                ][self.sheet_name_col]
                .dropna()
                .astype(str)
                .tolist()
            )
            print(
                f"✅ Found {len(self.enabled_sheets)} enabled sheets: {self.enabled_sheets}"
            )

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at: {self.file_path}")
        except KeyError as e:
            raise KeyError(
                f"Missing expected column in '{self.controller_sheet}' sheet: {e}"
            )
        except Exception as e:
            print(f"⚠️ Error reading controller sheet: {e}")
            self.enabled_sheets = []

    def get_test_case_details(self):
        """
        Iterates through enabled sheets and extracts the test case data.

        Returns:
            dict: A dictionary where keys are sheet names and values are pandas DataFrames
                  with the extracted test case details.
        """
        # Step 1: Get the list of enabled sheets
        self._get_enabled_sheets()

        if not self.enabled_sheets:
            print("🛑 No sheets were found to be enabled or an error occurred.")
            return {}

        # Step 2: Extract data from each enabled sheet
        for sheet_name in self.enabled_sheets:
            try:
                # Reading the entire sheet as a table/DataFrame
                # You might need to add logic here to find the *start* of the
                # test case table if it's not at A1 (e.g., skip initial rows).
                df_test_cases = pd.read_excel(self.file_path, sheet_name=sheet_name)

                # Optional: Add cleanup or validation logic here.
                # Example: Remove rows where the first column is empty (often used to define the table boundary)
                # df_test_cases.dropna(how='all', inplace=True)

                self.test_case_data[sheet_name] = df_test_cases
                print(f"   - Successfully read data from '{sheet_name}'")

            except Exception as e:
                print(f"   - ❌ Failed to read data from sheet '{sheet_name}': {e}")
                self.test_case_data[sheet_name] = None  # Or an empty DataFrame

        return self.test_case_data