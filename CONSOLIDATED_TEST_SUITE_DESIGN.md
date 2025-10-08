# 📋 Consolidated Test Suite Design Documentation

## 🎯 **Overview**

The new consolidated test suite replaces the previous multi-sheet approach with a single, unified design that:
- ✅ Eliminates the need for the CONTROLLER sheet
- ✅ Consolidates all test types (SMOKE, DATA_VALIDATION, CROSS_DB_VALIDATION) into one sheet
- ✅ Adds a TEST_TYPE column to distinguish test categories
- ✅ Provides a manual entry form with cascading dropdowns and color coding
- ✅ Maintains all existing functionality while improving usability

## 📊 **Sheet Structure**

### 1. **CONSOLIDATED_TESTS Sheet**

This is the main sheet containing all test cases across all test types.

#### **Key Columns:**
| Column | Description | Example Values |
|--------|-------------|----------------|
| `Test_Case_ID` | Unique identifier | SMOKE_PG_001, DVAL_001, CROSS_DB_001 |
| `Test_Case_Name` | Descriptive name | "PostgreSQL Connection Test - QA Environment" |
| **`TEST_TYPE`** | **NEW:** Test type indicator | SMOKE, DATA_VALIDATION, CROSS_DB_VALIDATION |
| `Test_Category` | Specific test category | CONNECTION, SCHEMA_VALIDATION, ROW_COUNT_VALIDATION |
| `SRC_Application_Name` | Source application | DUMMY, MyApp |
| `SRC_Environment_Name` | Source environment | QA, DEV, UAT, PROD |
| `TGT_Application_Name` | Target application | DUMMY, MyApp |
| `TGT_Environment_Name` | Target environment | QA, DEV, UAT, PROD |
| `Parameters` | Test-specific parameters | `source_table=public.employees,tolerance=5%` |
| `Enable` | Test enabled status | TRUE, FALSE |

#### **Color Coding:**
- 🟢 **SMOKE** tests: Light green background (`#E8F5E8`)
- 🔵 **DATA_VALIDATION** tests: Light blue background (`#E8F0FF`)
- 🟠 **CROSS_DB_VALIDATION** tests: Light orange background (`#FFF0E8`)

### 2. **REFERENCE Sheet**

Interactive form for manual test case entry with:

#### **Features:**
- 📝 **Manual Entry Form**: Structured form layout for easy data entry
- 🎨 **Color-Coded Dropdowns**: Visual distinction between test types
- ✅ **Data Validation**: Prevents invalid entries
- 📚 **Reference Data**: Built-in help and valid values

#### **Dropdown Validations:**
- **TEST_TYPE**: SMOKE, DATA_VALIDATION, CROSS_DB_VALIDATION
- **Test_Category**: CONNECTION, TABLE_EXISTS, SCHEMA_VALIDATION, etc.
- **Environment**: QA, DEV, UAT, NP1, ACC, PROD
- **Priority**: High, Medium, Low
- **Expected_Result**: PASS, FAIL
- **Enable**: TRUE, FALSE

## 🔄 **Migration from Old Structure**

### **Before (Multiple Sheets):**
```
📁 test_suite.xlsx
├── 📄 CONTROLLER (sheet control)
├── 📄 SMOKE (smoke tests)
├── 📄 DATA_VALIDATIONS (data validation tests)
└── 📄 CROSS_DB_VALIDATIONS (cross-db tests)
```

### **After (Consolidated):**
```
📁 consolidated_test_suite.xlsx
├── 📄 CONSOLIDATED_TESTS (all test types)
└── 📄 REFERENCE (manual entry form)
```

## 📋 **Test Type Mappings**

### **SMOKE Tests**
- **Purpose**: Basic connectivity and functionality validation
- **Categories**: CONNECTION, TABLE_EXISTS, TABLE_SELECT, SETUP
- **Typical Parameters**: `connection_timeout=30`, `table_name=public.employees`

### **DATA_VALIDATION Tests**
- **Purpose**: Data consistency and validation between environments
- **Categories**: SCHEMA_VALIDATION, ROW_COUNT_VALIDATION, COL_COL_VALIDATION
- **Typical Parameters**: `source_table=...,target_table=...,tolerance=5%`

### **CROSS_DB_VALIDATION Tests**
- **Purpose**: Cross-database comparison and validation
- **Categories**: SCHEMA_VALIDATION, ROW_COUNT_VALIDATION, COL_COL_VALIDATION
- **Typical Parameters**: Complex cross-database parameters with multiple sources

## 🛠 **Parameter Format Guidelines**

### **Common Parameter Patterns:**

#### **Row Count Validation:**
```
source_table=public.employees,target_table=public.employees,tolerance=5%,tolerance_type=percentage
```

#### **Schema Validation:**
```
source_table=public.employees,target_table=public.employees
```

#### **Column Comparison:**
```
source_table=public.employees,target_table=public.employees,compare_columns=emp_id|first_name|last_name,key_column=emp_id
```

#### **Connection Test:**
```
connection_timeout=30,max_retries=3
```

## 🎨 **Visual Design Features**

### **Header Styling:**
- Bold white text on blue background (`#366092`)
- Centered alignment with borders

### **Data Rows:**
- Conditional formatting based on TEST_TYPE
- Thin borders for clear separation
- Auto-fitted column widths

### **Reference Form:**
- Professional form layout
- Clear field labels and placeholders
- Dropdown validations with error messages
- Color-coded reference data section

## 🔧 **Implementation Benefits**

### **For Users:**
1. **Simplified Structure**: Single sheet for all tests
2. **Visual Clarity**: Color coding for quick identification
3. **Easy Entry**: Form-based manual entry with validation
4. **Better Organization**: Logical grouping by TEST_TYPE

### **For System:**
1. **No Controller Logic**: Eliminates sheet management complexity
2. **Consistent Format**: Uniform column structure across all test types
3. **Enhanced Filtering**: Easy filtering by TEST_TYPE column
4. **Better Reporting**: Clearer categorization in reports

## 🚀 **Next Steps**

1. **Review** the new Excel file design
2. **Test** manual entry using the REFERENCE sheet
3. **Update** code to read from CONSOLIDATED_TESTS sheet
4. **Migrate** existing test cases to new format
5. **Deploy** the new structure

## 📝 **Sample Test Cases Included**

The generated file includes representative examples:
- 2 SMOKE tests (connection and table access)
- 2 DATA_VALIDATION tests (row count and schema)
- 2 CROSS_DB_VALIDATION tests (column comparison and cross-db count)

Each example demonstrates proper parameter formatting and includes realistic test scenarios.