# Consolidated Excel Implementation

This directory contains the new implementation for reading and executing tests from the consolidated Excel format.

## 🏗️ Architecture

### Key Differences from Original Implementation

1. **No CONTROLLER Sheet**: Reads directly from `CONSOLIDATED_TESTS` sheet
2. **Single Sheet Format**: All test types (SMOKE, DATA_VALIDATION, CROSS_DB_VALIDATION) in one sheet
3. **TEST_TYPE Column**: Distinguishes between test types
4. **Enhanced Parameters**: Support for expected columns and tolerance limits
5. **Table Name Columns**: Dedicated `SRC_Table_Name` and `TGT_Table_Name` columns

## 📁 Directory Structure

```
consolidated_excel_implementation/
├── src/
│   ├── __init__.py
│   ├── consolidated_excel_reader.py      # New Excel reader for consolidated format
│   └── consolidated_test_executor.py     # Main execution engine
├── tests/
│   └── test_consolidated_reader.py       # Test script for the reader
├── output/                               # Generated reports and summaries
└── README.md                            # This file
```

## 🚀 Features

### ConsolidatedExcelTestCaseReader

- **Flexible Enable Detection**: Supports True/FALSE, "TRUE"/"FALSE", 1/0
- **Parameter Parsing**: Converts parameter strings to structured dictionaries
- **Test Type Grouping**: Automatically groups tests by TEST_TYPE
- **Statistics Generation**: Provides comprehensive test statistics
- **Export Functionality**: Export test summaries to Excel

### Enhanced Parameter Support

The new implementation supports advanced parameter configurations:

#### Tolerance Parameters
```
tolerance=5%,tolerance_type=percentage
tolerance=100,tolerance_type=absolute
numeric_tolerance=0.01
decimal_precision=3
```

#### Expected Column Differences
```
compare_columns=emp_id|first_name|last_name,expect_cols=bonus|total_salary,key_column=emp_id
```

#### Advanced Options
```
case_sensitive=false,allow_nulls=true,trim_spaces=true
currency_conversion=true
batch_size=10000
```

## 📊 Supported Test Types

### SMOKE Tests
- Connection validation
- Table existence checks
- Basic SELECT operations

### DATA_VALIDATION Tests
- Row count validation (with/without tolerance)
- Schema structure validation
- Data type validation

### CROSS_DB_VALIDATION Tests
- Column-to-column comparison
- Expected differences with tolerance
- Cross-database row count validation
- Multi-currency price comparisons
- Financial data with precision requirements

## 🔧 Usage

### Basic Usage

```python
from src.consolidated_excel_reader import ConsolidatedExcelTestCaseReader

# Create reader
reader = ConsolidatedExcelTestCaseReader("path/to/consolidated_test_suite.xlsx")

# Read all test cases
test_data = reader.get_test_case_details()

# Get specific test type
smoke_tests = reader.get_tests_by_type('SMOKE')

# Get statistics
stats = reader.get_test_statistics()
```

### Full Execution

```python
from src.consolidated_test_executor import ConsolidatedTestExecutor

# Create executor
executor = ConsolidatedTestExecutor("path/to/consolidated_test_suite.xlsx")

# Execute all tests
results = executor.execute_tests()

# Execute specific test types
results = executor.execute_tests(['SMOKE', 'DATA_VALIDATION'])

# Generate report
executor.generate_report('enhanced-md')
```

### Command Line Usage

```bash
# Run the test script
python consolidated_excel_implementation/tests/test_consolidated_reader.py

# Run the full executor
python consolidated_excel_implementation/src/consolidated_test_executor.py
```

## 📈 New Parameter Features

### Expected Columns (`expect_cols`)

Define columns that are expected to have differences within tolerance limits:

```
compare_columns=transaction_id|amount,expect_cols=tax_amount|total_amount,numeric_tolerance=0.05
```

This allows testing scenarios where:
- Core data should match exactly (`compare_columns`)
- Calculated fields may differ within tolerance (`expect_cols`)

### Tolerance Types

1. **Percentage Tolerance**: `tolerance=5%,tolerance_type=percentage`
2. **Absolute Tolerance**: `tolerance=100,tolerance_type=absolute`
3. **Numeric Precision**: `numeric_tolerance=0.001,decimal_precision=4`

### Advanced Comparison Options

- **Case Sensitivity**: `case_sensitive=false`
- **Null Handling**: `allow_nulls=true`
- **Space Trimming**: `trim_spaces=true`
- **Currency Conversion**: `currency_conversion=true`

## 🔄 Migration from Original Format

### Key Changes

1. **File Structure**:
   - Old: Multiple sheets + CONTROLLER sheet
   - New: Single CONSOLIDATED_TESTS sheet

2. **Test Identification**:
   - Old: Sheet name determines test type
   - New: TEST_TYPE column determines test type

3. **Table Names**:
   - Old: Embedded in Parameters column
   - New: Dedicated SRC_Table_Name and TGT_Table_Name columns

4. **Enable Control**:
   - Old: CONTROLLER sheet ENABLE column
   - New: Enable column (first column) in test data

### Example Parameter Migration

**Old Format**:
```
Parameters: source_table=public.employees,target_table=public.employees,tolerance=5%,tolerance_type=percentage
```

**New Format**:
```
SRC_Table_Name: public.employees
TGT_Table_Name: public.employees
Parameters: tolerance=5%,tolerance_type=percentage
```

## 🧪 Testing

Run the test script to verify functionality:

```bash
cd consolidated_excel_implementation
python tests/test_consolidated_reader.py
```

Expected output:
- ✅ Reader imports successfully
- 📊 Test statistics and counts
- 🔍 Individual test type retrieval
- 💾 Export functionality verification

## 📝 Reports

The implementation generates reports in the `output/` directory:

- **Enhanced Markdown**: Rich reports with emojis and formatting
- **HTML**: Interactive dashboard with charts
- **Test Summary Excel**: Structured test data export

## 🔗 Integration

The new implementation maintains compatibility with existing:
- Database connectors
- Test case execution logic
- Report generators
- Configuration management

It simply provides a new way to read and structure test data from the consolidated Excel format.

## 🚨 Important Notes

1. **File Paths**: Update file paths to point to new consolidated Excel files
2. **Dependencies**: Requires pandas, openpyxl (same as original)
3. **Compatibility**: Does not modify existing codebase
4. **Testing**: Always test with sample data before production use

## 📋 Example Excel Structure

| Enable | Test_Case_ID | Test_Case_Name | TEST_TYPE | Test_Category | SRC_Table_Name | TGT_Table_Name | Parameters |
|--------|--------------|----------------|-----------|---------------|----------------|----------------|------------|
| TRUE   | SMOKE_001    | Connection Test | SMOKE     | CONNECTION    |                |                | connection_timeout=30 |
| TRUE   | DVAL_001     | Row Count      | DATA_VALIDATION | ROW_COUNT_VALIDATION | public.employees | public.employees | tolerance=5%,tolerance_type=percentage |
| TRUE   | CROSS_001    | Column Compare | CROSS_DB_VALIDATION | COL_COL_VALIDATION | public.employees | public.employees | compare_columns=emp_id\|name,expect_cols=bonus,key_column=emp_id |