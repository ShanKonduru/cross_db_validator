import random
import pandas as pd
import time
import sys
import os

# Add src directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from database_config_manager import DatabaseConfigManager
    from database_connection_base import DatabaseConnectionBase
    from postgresql_connector import PostgreSQLConnector
    from oracle_connector import OracleConnector
    from sqlserver_connector import SQLServerConnector
except ImportError:
    # Fallback for different import contexts
    DatabaseConfigManager = None
    DatabaseConnectionBase = None
    PostgreSQLConnector = None
    OracleConnector = None
    SQLServerConnector = None


class MockDatabaseConnection:
    """Mock database connection for testing data validation logic."""
    
    def __init__(self, db_type, config):
        self.db_type = db_type
        self.config = config
    
    def execute_query(self, query, params=None):
        """Mock query execution with simulated results."""
        query_lower = query.lower().strip()
        
        # Handle schema queries
        if 'information_schema.columns' in query_lower:
            return self._mock_schema_query(query, params)
        
        # Handle count queries
        if query_lower.startswith('select count(*)'):
            return self._mock_count_query(query)
        
        # Handle column data queries for comparison
        if query_lower.startswith('select ') and ' from ' in query_lower and 'limit' in query_lower:
            return self._mock_column_data_query(query)
        
        return {'rows': [], 'columns': []}
    
    def _mock_schema_query(self, query, params):
        """Mock schema information query."""
        if params and len(params) >= 2:
            schema_name, table_name = params[0], params[1]
            
            # Simulate different schemas for source vs target tables
            if 'new_' in table_name:
                # Target table with slightly different schema
                return {
                    'rows': [
                        ('id', 'INTEGER', None, None, None, 'NO', None, 1),
                        ('name', 'VARCHAR', 100, None, None, 'YES', None, 2),  # Length increased
                        ('status', 'BOOLEAN', None, None, None, 'YES', None, 3),  # Type changed from VARCHAR(1)
                        ('created_at', 'TIMESTAMP', None, None, None, 'NO', 'CURRENT_TIMESTAMP', 4),
                    ],
                    'columns': ['column_name', 'data_type', 'character_maximum_length', 'numeric_precision', 'numeric_scale', 'is_nullable', 'column_default', 'ordinal_position']
                }
            else:
                # Source table
                return {
                    'rows': [
                        ('id', 'INTEGER', None, None, None, 'NO', None, 1),
                        ('name', 'VARCHAR', 50, None, None, 'YES', None, 2),  # Shorter length
                        ('status', 'VARCHAR', 1, None, None, 'YES', None, 3),  # Original VARCHAR(1)
                        ('created_at', 'TIMESTAMP', None, None, None, 'NO', 'CURRENT_TIMESTAMP', 4),
                    ],
                    'columns': ['column_name', 'data_type', 'character_maximum_length', 'numeric_precision', 'numeric_scale', 'is_nullable', 'column_default', 'ordinal_position']
                }
        
        return {'rows': [], 'columns': []}
    
    def _mock_count_query(self, query):
        """Mock count query with realistic results."""
        import random
        
        # Simulate different counts for source vs target
        if 'new_' in query.lower():
            # Target table - slightly different count
            base_count = 1250
            variance = random.randint(-50, 150)  # Some variance
            count = max(0, base_count + variance)
        else:
            # Source table - base count
            count = 1000 + random.randint(0, 200)
        
        return {
            'rows': [[count]],
            'columns': ['count']
        }

    def _mock_column_data_query(self, query):
        """Mock column data query for column comparison validation."""
        import random
        
        # Extract column name from query
        query_parts = query.lower().split()
        select_idx = query_parts.index('select')
        from_idx = query_parts.index('from')
        column_name = query_parts[select_idx + 1]
        
        # Extract table name
        table_name = query_parts[from_idx + 1]
        
        # Extract limit
        limit_idx = query_parts.index('limit')
        limit_value = int(query_parts[limit_idx + 1])
        
        # Generate mock data based on column name and table
        rows = []
        
        if column_name == 'id':
            # Generate sequential IDs with some variance between source and target
            start_id = 1 if 'new_' not in table_name else 1
            for i in range(limit_value):
                rows.append([start_id + i])
        
        elif column_name == 'name':
            # Generate sample names
            names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eva', 'Frank', 'Grace', 'Henry']
            for i in range(limit_value):
                # Source vs target might have slight differences
                if 'new_' in table_name and random.random() < 0.1:  # 10% different names in target
                    name = names[random.randint(0, len(names)-1)] + '_modified'
                else:
                    name = names[i % len(names)]
                rows.append([name])
        
        elif column_name == 'status':
            # Generate status values (some differences between source and target)
            for i in range(limit_value):
                if 'new_' in table_name:
                    # Target table has boolean values
                    status = random.choice([True, False])
                else:
                    # Source table has varchar values
                    status = random.choice(['A', 'I', 'P'])
                rows.append([status])
        
        elif 'price' in column_name or 'amount' in column_name:
            # Generate numeric data with tolerance testing
            for i in range(limit_value):
                base_value = 10.0 + (i * 0.5)
                if 'new_' in table_name and random.random() < 0.2:  # 20% slight differences in target
                    # Add small differences within/outside tolerance
                    variance = random.uniform(-0.002, 0.002) if random.random() < 0.8 else random.uniform(-0.1, 0.1)
                    value = base_value + variance
                else:
                    value = base_value
                rows.append([round(value, 4)])
        
        else:
            # Generic column data
            for i in range(limit_value):
                if 'new_' in table_name and random.random() < 0.05:  # 5% differences in target
                    value = f'value_{i}_modified'
                else:
                    value = f'value_{i}'
                rows.append([value])
        
        return {
            'rows': rows,
            'columns': [column_name]
        }


class DataValidationTestCase:
    """
    Represents a single data validation test case loaded from an enabled row in the Excel sheet,
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
        self._last_execution_details = {}  # Store detailed execution results

    def execute_test(self) -> str:
        """
        Execute the data validation test.
        Enhanced with execution time tracking and real validation logic.
        """
        self._execution_start_time = time.time()
        
        print(f"Executing test: {self.test_case_name}")
        
        try:
            # Route to appropriate validation based on test category
            if self.test_category == "SCHEMA_VALIDATION":
                result = self._execute_schema_validation()
            elif self.test_category == "ROW_COUNT_VALIDATION":
                result = self._execute_row_count_validation()
            elif self.test_category == "COL_COL_VALIDATION":
                result = self._execute_column_comparison_validation()
            else:
                # Legacy test execution for other categories
                result = self._execute_legacy_test()
                self._record_execution_result(result)
        except Exception as e:
            print(f"❌ Test execution failed: {str(e)}")
            result = "FAILED"
            self._record_execution_result(result, {'error_message': str(e)})
        
        return result

    def _record_execution_result(self, status: str, details: dict = None):
        """Record execution result and timing for persistent trends analysis."""
        self._last_execution_status = status
        self._last_execution_details = details or {}
        if self._execution_start_time:
            execution_time = time.time() - self._execution_start_time
            self._execution_time_ms = int(execution_time * 1000)  # Convert to milliseconds

    def get_last_execution_details(self) -> dict:
        """Get detailed results from the last execution."""
        return self._last_execution_details

    def _execute_legacy_test(self) -> str:
        """Execute legacy random test for non-data validation categories."""
        return random.choice(["PASSED", "FAILED", "SKIPPED"])

    def _execute_schema_validation(self) -> str:
        """Execute schema validation between source and target tables."""
        try:
            # Parse parameters
            source_table = self.parameters.get('source_table', '')
            target_table = self.parameters.get('target_table', '')
            ignore_sequence = self.parameters.get('ignore_sequence', 'false').lower() == 'true'
            check_constraints = self.parameters.get('check_constraints', 'false').lower() == 'true'
            
            if not source_table or not target_table:
                print(f"❌ Missing table parameters: source={source_table}, target={target_table}")
                return "FAILED"
            
            print(f"🔍 Comparing schema: {source_table} vs {target_table}")
            
            # Get database connection
            db_connection = self._get_database_connection()
            if not db_connection:
                return "FAILED"
            
            # Get schema information for both tables
            source_schema = self._get_table_schema(db_connection, source_table)
            target_schema = self._get_table_schema(db_connection, target_table)
            
            if not source_schema or not target_schema:
                print(f"❌ Could not retrieve schema for one or both tables")
                return "FAILED"
            
            # Compare schemas
            validation_result = self._compare_schemas(source_schema, target_schema, ignore_sequence)
            
            # Report results
            if validation_result['hard_failures']:
                print(f"❌ Schema validation failed with {len(validation_result['hard_failures'])} critical issues")
                for failure in validation_result['hard_failures']:
                    print(f"   • {failure}")
                self._record_execution_result("FAILED", {
                    'hard_failures': validation_result['hard_failures'],
                    'soft_failures': validation_result['soft_failures']
                })
                return "FAILED"
            else:
                if validation_result['soft_failures']:
                    print(f"⚠️ Schema validation passed with {len(validation_result['soft_failures'])} warnings")
                    for warning in validation_result['soft_failures']:
                        print(f"   • {warning}")
                else:
                    print("✅ Schema validation passed - schemas match perfectly")
                self._record_execution_result("PASSED", {
                    'hard_failures': validation_result['hard_failures'],
                    'soft_failures': validation_result['soft_failures']
                })
                return "PASSED"
                
        except Exception as e:
            print(f"❌ Schema validation error: {str(e)}")
            self._record_execution_result("FAILED", {'error_message': str(e)})
            return "FAILED"

    def _execute_row_count_validation(self) -> str:
        """Execute row count validation between source and target tables."""
        try:
            # Parse parameters
            source_table = self.parameters.get('source_table', '')
            target_table = self.parameters.get('target_table', '')
            source_where = self.parameters.get('source_where', '').strip()
            target_where = self.parameters.get('target_where', '').strip()
            tolerance_percent = float(self.parameters.get('tolerance_percent', '0'))
            
            if not source_table or not target_table:
                print(f"❌ Missing table parameters: source={source_table}, target={target_table}")
                return "FAILED"
            
            print(f"📊 Comparing row counts: {source_table} vs {target_table}")
            if source_where:
                print(f"   Source condition: {source_where}")
            if target_where:
                print(f"   Target condition: {target_where}")
            
            # Get database connection
            db_connection = self._get_database_connection()
            if not db_connection:
                return "FAILED"
            
            # Build count queries
            source_query = f"SELECT COUNT(*) FROM {source_table}"
            if source_where:
                source_query += f" WHERE {source_where}"
                
            target_query = f"SELECT COUNT(*) FROM {target_table}"
            if target_where:
                target_query += f" WHERE {target_where}"
            
            # Execute count queries
            source_count = self._execute_count_query(db_connection, source_query, "source")
            target_count = self._execute_count_query(db_connection, target_query, "target")
            
            if source_count is None or target_count is None:
                return "FAILED"
            
            # Compare counts
            result = self._compare_row_counts(source_count, target_count, tolerance_percent)
            self._record_execution_result(result, {
                'source_count': source_count,
                'target_count': target_count,
                'tolerance_percent': tolerance_percent,
                'difference': abs(source_count - target_count),
                'variance_percent': (abs(source_count - target_count) / source_count * 100) if source_count > 0 else 0
            })
            return result
                
        except Exception as e:
            print(f"❌ Row count validation error: {str(e)}")
            self._record_execution_result("FAILED", {'error_message': str(e)})
            return "FAILED"

    def _execute_column_comparison_validation(self) -> str:
        """Execute column-to-column comparison validation between source and target tables."""
        try:
            # Parse parameters
            source_table = self.parameters.get('source_table', '')
            target_table = self.parameters.get('target_table', '')
            tolerance_numeric = float(self.parameters.get('tolerance_numeric', '0.001'))  # Default tolerance for numeric comparison
            exclude_columns = self.parameters.get('exclude_columns', '').split(',') if self.parameters.get('exclude_columns') else []
            exclude_columns = [col.strip() for col in exclude_columns]
            sample_size = int(self.parameters.get('sample_size', '1000'))  # Default sample size
            
            # Parse column mappings (new feature)
            column_mappings = {}
            if self.parameters.get('column_mappings'):
                mappings_str = self.parameters.get('column_mappings', '')
                for mapping in mappings_str.split(','):
                    if '=' in mapping:
                        source_col, target_col = mapping.split('=', 1)
                        column_mappings[source_col.strip()] = target_col.strip()
            
            if not source_table or not target_table:
                print(f"❌ Missing table parameters: source={source_table}, target={target_table}")
                self._record_execution_result("FAILED", {'error_message': 'Missing source or target table parameters'})
                return "FAILED"
            
            print(f"🔍 Comparing column values: {source_table} vs {target_table}")
            print(f"   📊 Sample size: {sample_size:,} rows")
            print(f"   🔢 Numeric tolerance: {tolerance_numeric}")
            if exclude_columns:
                print(f"   ⚠️ Excluding columns: {', '.join(exclude_columns)}")
            if column_mappings:
                print(f"   🔄 Column mappings: {len(column_mappings)} defined")
                for src, tgt in list(column_mappings.items())[:3]:
                    print(f"      • {src} → {tgt}")
                if len(column_mappings) > 3:
                    print(f"      ... and {len(column_mappings) - 3} more mappings")
            
            # Get database connection
            db_connection = self._get_database_connection()
            if not db_connection:
                return "FAILED"
            
            # Get table schemas to identify common columns
            source_schema = self._get_table_schema(db_connection, source_table)
            target_schema = self._get_table_schema(db_connection, target_table)
            
            if not source_schema or not target_schema:
                print(f"❌ Could not retrieve schema for one or both tables")
                self._record_execution_result("FAILED", {'error_message': 'Schema retrieval failed'})
                return "FAILED"
            
            # Find columns to compare using mappings
            source_cols = {col[0]: col for col in source_schema}  # column_name as key
            target_cols = {col[0]: col for col in target_schema}
            
            # Show exclusion information
            if exclude_columns:
                print(f"   ⚠️ Exclusion analysis:")
                for excl_col in exclude_columns:
                    in_source = excl_col in source_cols
                    in_target = excl_col in target_cols
                    if in_source or in_target:
                        location = []
                        if in_source: location.append("source")
                        if in_target: location.append("target")
                        print(f"      • {excl_col}: Found in {' and '.join(location)} - EXCLUDED")
                    else:
                        print(f"      • {excl_col}: Not found in either table - IGNORED")
            
            # Build comparison pairs using column mappings
            comparison_pairs = []
            
            # First, add mapped columns
            for source_col, target_col in column_mappings.items():
                if source_col in source_cols and target_col in target_cols:
                    if source_col not in exclude_columns and target_col not in exclude_columns:
                        comparison_pairs.append((source_col, target_col))
                        print(f"   ✅ Mapped: {source_col} → {target_col}")
                    else:
                        excluded_reason = []
                        if source_col in exclude_columns: excluded_reason.append(f"source '{source_col}' excluded")
                        if target_col in exclude_columns: excluded_reason.append(f"target '{target_col}' excluded")
                        print(f"   ❌ Skipped mapping {source_col} → {target_col}: {' and '.join(excluded_reason)}")
                else:
                    if source_col not in source_cols:
                        print(f"   ⚠️ Warning: Source column '{source_col}' not found in schema")
                    if target_col not in target_cols:
                        print(f"   ⚠️ Warning: Target column '{target_col}' not found in schema")
            
            # Then, add common columns that aren't already mapped
            mapped_source_cols = set(column_mappings.keys())
            mapped_target_cols = set(column_mappings.values())
            
            common_columns = set(source_cols.keys()) & set(target_cols.keys())
            excluded_common = []
            excluded_common = []
            for col in common_columns:
                if (col not in mapped_source_cols and col not in mapped_target_cols):
                    if col not in exclude_columns:
                        comparison_pairs.append((col, col))
                    else:
                        excluded_common.append(col)
            
            # Show what common columns were excluded
            if excluded_common:
                print(f"   ❌ Excluded common columns: {', '.join(excluded_common)}")
            
            if not comparison_pairs:
                print(f"❌ No columns found for comparison (after mappings and exclusions)")
                self._record_execution_result("FAILED", {'error_message': 'No columns found for comparison'})
                return "FAILED"
            
            print(f"   📋 Comparing {len(comparison_pairs)} column pairs:")
            for src, tgt in comparison_pairs[:5]:
                if src == tgt:
                    print(f"      • {src}")
                else:
                    print(f"      • {src} → {tgt}")
            if len(comparison_pairs) > 5:
                print(f"      ... and {len(comparison_pairs) - 5} more pairs")
            
            # Perform column comparison with mappings
            comparison_results = self._compare_table_columns_with_mappings(
                db_connection, source_table, target_table, 
                comparison_pairs, source_cols, target_cols, 
                tolerance_numeric, sample_size
            )
            
            # Analyze results
            total_columns = len(comparison_pairs)
            passed_columns = len([r for r in comparison_results if r['status'] == 'PASSED'])
            failed_columns = len([r for r in comparison_results if r['status'] == 'FAILED'])
            warnings = [r for r in comparison_results if r.get('warnings')]
            
            print(f"   📊 Column comparison summary:")
            print(f"      ✅ Passed: {passed_columns}/{total_columns}")
            print(f"      ❌ Failed: {failed_columns}/{total_columns}")
            print(f"      ⚠️ Warnings: {len(warnings)}")
            
            # Determine overall result
            if failed_columns == 0:
                status = "PASSED"
                print(f"✅ Column comparison validation: PASSED")
            else:
                status = "FAILED"
                print(f"❌ Column comparison validation: FAILED")
                
                # Show failed columns details
                failed_results = [r for r in comparison_results if r['status'] == 'FAILED']
                for failure in failed_results[:3]:  # Show first 3 failures
                    print(f"      • {failure['column']}: {failure['reason']}")
                if len(failed_results) > 3:
                    print(f"      ... and {len(failed_results) - 3} more failures")
            
            # Record execution results
            execution_details = {
                'total_columns': total_columns,
                'passed_columns': passed_columns,
                'failed_columns': failed_columns,
                'warnings_count': len(warnings),
                'tolerance_numeric': tolerance_numeric,
                'sample_size': sample_size,
                'column_mappings_count': len(column_mappings),
                'comparison_results': comparison_results[:10],  # Store first 10 for reporting
                'soft_failures': [],  # Column comparison warnings
                'hard_failures': []   # Column comparison failures
            }
            
            # Classify failures as soft/hard
            for result in comparison_results:
                if result['status'] == 'FAILED':
                    execution_details['hard_failures'].append(f"Column '{result['column']}': {result['reason']}")
                elif result.get('warnings'):
                    execution_details['soft_failures'].extend([f"Column '{result['column']}': {w}" for w in result['warnings']])
            
            self._record_execution_result(status, execution_details)
            return status
                
        except Exception as e:
            print(f"❌ Column comparison validation error: {str(e)}")
            self._record_execution_result("FAILED", {'error_message': str(e)})
            return "FAILED"

    def _get_database_connection(self):
        """Get database connection using real database connectors."""
        try:
            if DatabaseConfigManager is None:
                print("❌ DatabaseConfigManager not available")
                return None
                
            config_manager = DatabaseConfigManager("configs/database_connections.json")
            
            # Get connection details
            config = config_manager.get_connection_details(
                self.environment_name.upper(), 
                self.application_name.upper()
            )
            
            if not config:
                print(f"❌ No configuration found for {self.environment_name}/{self.application_name}")
                return None
            
            # Get credentials from environment variables
            username, password = DatabaseConfigManager.get_credentials(
                self.environment_name.upper(), 
                self.application_name.upper()
            )
            
            if not username or not password:
                print(f"❌ Credentials not found for {self.environment_name}/{self.application_name}")
                print(f"   Please set environment variables: {self.environment_name.upper()}_{self.application_name.upper()}_USERNAME and {self.environment_name.upper()}_{self.application_name.upper()}_PASSWORD")
                return None
            
            # Get database type and connection parameters
            db_type = config.get('db_type', '').lower()
            host = config.get('host')
            port = config.get('port')
            
            print(f"🔗 Connecting to {db_type} database: {host}:{port}")
            
            # Create appropriate connector based on database type
            connector = None
            if db_type == 'postgresql':
                database = config.get('database')
                if not database:
                    print(f"❌ Database name not specified for PostgreSQL connection")
                    return None
                connector = PostgreSQLConnector(host, port, username, password, database)
                
            elif db_type == 'oracle':
                service_name = config.get('service_name')
                if not service_name:
                    print(f"❌ Service name not specified for Oracle connection")
                    return None
                connector = OracleConnector(host, port, username, password, service_name)
                
            elif db_type == 'sqlserver':
                database = config.get('database', 'master')  # Default to master if not specified
                connector = SQLServerConnector(host, port, username, password, database)
                
            else:
                print(f"❌ Unsupported database type: {db_type}")
                return None
            
            # Test the connection
            success, message = connector.connect()
            if success:
                print(f"✅ Database connection established: {message}")
                return connector
            else:
                print(f"❌ Database connection failed: {message}")
                return None
            
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return None

    def _get_table_schema(self, db_connection, table_name):
        """Get table schema information using database-agnostic SQL."""
        try:
            # Parse schema and table name
            if '.' in table_name:
                schema_name, table_name_only = table_name.split('.', 1)
            else:
                schema_name = 'public'  # Default for PostgreSQL
                table_name_only = table_name
            
            # Check if we have a real database connection or mock
            if hasattr(db_connection, 'connection') and db_connection.connection is not None:
                # Real database connection - determine database type
                connector_type = type(db_connection).__name__.lower()
                
                if 'oracle' in connector_type:
                    # Oracle uses different schema query
                    schema_query = f"""
                        SELECT 
                            column_name,
                            data_type,
                            char_length as character_maximum_length,
                            data_precision as numeric_precision,
                            data_scale as numeric_scale,
                            nullable as is_nullable,
                            data_default as column_default,
                            column_id as ordinal_position
                        FROM user_tab_columns 
                        WHERE table_name = '{table_name_only.upper()}'
                        ORDER BY column_id
                    """
                elif 'sqlserver' in connector_type:
                    # SQL Server uses different schema query
                    schema_query = f"""
                        SELECT 
                            COLUMN_NAME,
                            DATA_TYPE,
                            CHARACTER_MAXIMUM_LENGTH,
                            NUMERIC_PRECISION,
                            NUMERIC_SCALE,
                            IS_NULLABLE,
                            COLUMN_DEFAULT,
                            ORDINAL_POSITION
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = '{schema_name}' AND TABLE_NAME = '{table_name_only}'
                        ORDER BY ORDINAL_POSITION
                    """
                else:
                    # PostgreSQL and others
                    schema_query = f"""
                        SELECT 
                            column_name,
                            data_type,
                            character_maximum_length,
                            numeric_precision,
                            numeric_scale,
                            is_nullable,
                            column_default,
                            ordinal_position
                        FROM information_schema.columns 
                        WHERE table_schema = '{schema_name}' AND table_name = '{table_name_only}'
                        ORDER BY ordinal_position
                    """
                
                success, result = db_connection.execute_query(schema_query)
                
                if success and result:
                    return result
                else:
                    print(f"❌ No schema found for table: {table_name}")
                    return None
            else:
                # MockDatabaseConnection - fallback for testing
                schema_query = """
                    SELECT 
                        column_name,
                        data_type,
                        character_maximum_length,
                        numeric_precision,
                        numeric_scale,
                        is_nullable,
                        column_default,
                        ordinal_position
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                """
                result = db_connection.execute_query(schema_query, (schema_name, table_name_only))
                if not result or not result.get('rows'):
                    print(f"❌ No schema found for table: {table_name}")
                    return None
                return result['rows']
                
        except Exception as e:
            print(f"❌ Error getting schema for {table_name}: {str(e)}")
            return None

    def _execute_count_query(self, db_connection, query, table_type):
        """Execute count query and return result."""
        try:
            if hasattr(db_connection, 'connection') and db_connection.connection is not None:
                # Real database connection
                success, result = db_connection.execute_query(query)
                
                if success and result:
                    count = result[0][0]
                    print(f"   {table_type.title()} count: {count:,}")
                    return count
                else:
                    print(f"❌ No result from {table_type} count query")
                    return None
            else:
                # MockDatabaseConnection - fallback for testing
                result = db_connection.execute_query(query)
                
                if not result or not result.get('rows'):
                    print(f"❌ No result from {table_type} count query")
                    return None
                    
                count = result['rows'][0][0]
                print(f"   {table_type.title()} count: {count:,}")
                return count
                
        except Exception as e:
            print(f"❌ Error executing {table_type} count query: {str(e)}")
            return None

    def _compare_schemas(self, source_schema, target_schema, ignore_sequence=False):
        """Compare source and target schemas with soft/hard failure classification."""
        hard_failures = []
        soft_failures = []
        
        # Convert to dictionaries for easier comparison
        source_cols = {col[0]: col for col in source_schema}  # column_name as key
        target_cols = {col[0]: col for col in target_schema}
        
        # Check for missing columns (hard failures)
        source_only = set(source_cols.keys()) - set(target_cols.keys())
        target_only = set(target_cols.keys()) - set(source_cols.keys())
        
        if source_only:
            hard_failures.append(f"Columns missing in target: {', '.join(source_only)}")
        if target_only:
            hard_failures.append(f"Columns missing in source: {', '.join(target_only)}")
        
        # Compare common columns
        common_cols = set(source_cols.keys()) & set(target_cols.keys())
        
        for col_name in common_cols:
            source_col = source_cols[col_name]
            target_col = target_cols[col_name]
            
            # Compare data types with soft failure logic
            source_type = source_col[1].upper()  # data_type
            target_type = target_col[1].upper()
            
            if source_type != target_type:
                if self._is_compatible_type_change(source_type, target_type):
                    soft_failures.append(f"Column '{col_name}': Compatible type change {source_type} → {target_type}")
                else:
                    hard_failures.append(f"Column '{col_name}': Incompatible type change {source_type} → {target_type}")
            
            # Compare lengths for character types (soft failure for increases)
            source_length = source_col[2]  # character_maximum_length
            target_length = target_col[2]
            
            if source_length and target_length and source_length != target_length:
                if target_length > source_length:
                    soft_failures.append(f"Column '{col_name}': Length increased from {source_length} to {target_length}")
                else:
                    soft_failures.append(f"Column '{col_name}': Length decreased from {source_length} to {target_length}")
            
            # Compare nullable (soft failure)
            source_nullable = source_col[5]  # is_nullable
            target_nullable = target_col[5]
            
            if source_nullable != target_nullable:
                soft_failures.append(f"Column '{col_name}': Nullable changed from {source_nullable} to {target_nullable}")
        
        return {
            'hard_failures': hard_failures,
            'soft_failures': soft_failures
        }

    def _is_compatible_type_change(self, source_type, target_type):
        """Determine if a data type change is compatible (soft failure)."""
        compatible_changes = {
            ('VARCHAR', 'TEXT'),
            ('CHAR', 'VARCHAR'),
            ('INTEGER', 'BIGINT'),
            ('DECIMAL', 'NUMERIC'),
            ('TIMESTAMP', 'TIMESTAMPTZ'),
        }
        
        # Check for VARCHAR(1) to BOOLEAN
        if source_type.startswith('VARCHAR') and target_type == 'BOOLEAN':
            return True
            
        # Check if it's in our compatible changes list
        return (source_type, target_type) in compatible_changes

    def _compare_row_counts(self, source_count, target_count, tolerance_percent):
        """Compare row counts with tolerance handling."""
        if source_count == target_count:
            print(f"✅ Perfect match: {source_count:,} rows")
            return "PASSED"
        
        # Calculate difference and percentage
        difference = abs(source_count - target_count)
        if source_count > 0:
            variance_percent = (difference / source_count) * 100
        else:
            variance_percent = 100 if target_count > 0 else 0
        
        print(f"📊 Row count difference: {difference:,} ({variance_percent:.2f}%)")
        
        # Check tolerance
        if variance_percent <= tolerance_percent:
            print(f"✅ Within tolerance ({tolerance_percent}%): PASSED")
            return "PASSED"
        else:
            print(f"❌ Exceeds tolerance ({tolerance_percent}%): FAILED")
            return "FAILED"

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
        """Converts the key=value;key=value Parameters string into a dictionary."""
        params = {}
        # Use str() and pd.notna() to handle NaN/missing values
        if isinstance(params_str, (str, float)) and pd.notna(params_str):
            # Split by semicolon for data validation parameters
            separator = ';' if ';' in str(params_str) else ','
            for item in str(params_str).split(separator):
                if "=" in item:
                    try:
                        key, value = item.split("=", 1)
                        params[key.strip()] = value.strip()
                    except ValueError:
                        # Handle cases where split fails unexpectedly
                        pass
        return params

    def _compare_table_columns(self, db_connection, source_table, target_table, 
                              common_columns, source_cols, target_cols, 
                              tolerance_numeric, sample_size):
        """Compare column values between source and target tables."""
        comparison_results = []
        
        for column_name in common_columns:
            try:
                # Get column data type for appropriate comparison strategy
                source_col_info = source_cols[column_name]
                target_col_info = target_cols[column_name]
                source_data_type = source_col_info[1].upper()  # data_type
                
                # Build sample queries
                source_query = f"SELECT {column_name} FROM {source_table} ORDER BY {column_name} LIMIT {sample_size}"
                target_query = f"SELECT {column_name} FROM {target_table} ORDER BY {column_name} LIMIT {sample_size}"
                
                # Execute queries
                if hasattr(db_connection, 'connection') and db_connection.connection is not None:
                    # Real database connection
                    source_success, source_result = db_connection.execute_query(source_query)
                    target_success, target_result = db_connection.execute_query(target_query)
                    
                    if not source_success or not target_success or not source_result or not target_result:
                        comparison_results.append({
                            'column': column_name,
                            'status': 'FAILED',
                            'reason': 'Failed to retrieve column data',
                            'source_count': 0,
                            'target_count': 0,
                            'match_count': 0,
                            'warnings': []
                        })
                        continue
                    
                    # Extract column values from real database results
                    source_values = [row[0] for row in source_result]
                    target_values = [row[0] for row in target_result]
                else:
                    # MockDatabaseConnection - fallback for testing
                    source_result = db_connection.execute_query(source_query)
                    target_result = db_connection.execute_query(target_query)
                    
                    if not source_result or not target_result:
                        comparison_results.append({
                            'column': column_name,
                            'status': 'FAILED',
                            'reason': 'Failed to retrieve column data',
                            'source_count': 0,
                            'target_count': 0,
                            'match_count': 0,
                            'warnings': []
                        })
                        continue
                    
                    # Extract column values from mock database results
                    source_values = [row[0] for row in source_result.get('rows', [])]
                    target_values = [row[0] for row in target_result.get('rows', [])]
                
                # Compare values based on data type
                if self._is_numeric_type(source_data_type):
                    result = self._compare_numeric_column(column_name, source_values, target_values, tolerance_numeric)
                elif self._is_text_type(source_data_type):
                    result = self._compare_text_column(column_name, source_values, target_values)
                else:
                    result = self._compare_generic_column(column_name, source_values, target_values)
                
                comparison_results.append(result)
                
            except Exception as e:
                comparison_results.append({
                    'column': column_name,
                    'status': 'FAILED',
                    'reason': f'Comparison error: {str(e)}',
                    'source_count': 0,
                    'target_count': 0,
                    'match_count': 0,
                    'warnings': []
                })
        
        return comparison_results

    def _compare_table_columns_with_mappings(self, db_connection, source_table, target_table, 
                                           comparison_pairs, source_cols, target_cols, 
                                           tolerance_numeric, sample_size):
        """Compare column values between source and target tables using column mappings."""
        comparison_results = []
        
        for source_column, target_column in comparison_pairs:
            try:
                # Get column data type for appropriate comparison strategy
                source_col_info = source_cols[source_column]
                target_col_info = target_cols[target_column]
                source_data_type = source_col_info[1].upper()  # data_type
                
                # Build sample queries with mapped column names
                source_query = f"SELECT {source_column} FROM {source_table} ORDER BY {source_column} LIMIT {sample_size}"
                target_query = f"SELECT {target_column} FROM {target_table} ORDER BY {target_column} LIMIT {sample_size}"
                
                # Execute queries
                if hasattr(db_connection, 'connection') and db_connection.connection is not None:
                    # Real database connection
                    source_success, source_result = db_connection.execute_query(source_query)
                    target_success, target_result = db_connection.execute_query(target_query)
                    
                    if not source_success or not target_success or not source_result or not target_result:
                        comparison_results.append({
                            'column': f"{source_column} → {target_column}" if source_column != target_column else source_column,
                            'status': 'FAILED',
                            'reason': 'Failed to retrieve column data',
                            'source_count': 0,
                            'target_count': 0,
                            'match_count': 0,
                            'warnings': []
                        })
                        continue
                    
                    # Extract column values from real database results
                    source_values = [row[0] for row in source_result]
                    target_values = [row[0] for row in target_result]
                else:
                    # MockDatabaseConnection - fallback for testing
                    source_result = db_connection.execute_query(source_query)
                    target_result = db_connection.execute_query(target_query)
                    
                    if not source_result or not target_result:
                        comparison_results.append({
                            'column': f"{source_column} → {target_column}" if source_column != target_column else source_column,
                            'status': 'FAILED',
                            'reason': 'Failed to retrieve column data',
                            'source_count': 0,
                            'target_count': 0,
                            'match_count': 0,
                            'warnings': []
                        })
                        continue
                    
                    # Extract column values from mock database results
                    source_values = [row[0] for row in source_result.get('rows', [])]
                    target_values = [row[0] for row in target_result.get('rows', [])]
                
                # Compare values based on data type
                if self._is_numeric_type(source_data_type):
                    result = self._compare_numeric_column(f"{source_column} → {target_column}" if source_column != target_column else source_column, 
                                                        source_values, target_values, tolerance_numeric)
                elif self._is_text_type(source_data_type):
                    result = self._compare_text_column(f"{source_column} → {target_column}" if source_column != target_column else source_column, 
                                                     source_values, target_values)
                else:
                    result = self._compare_generic_column(f"{source_column} → {target_column}" if source_column != target_column else source_column, 
                                                        source_values, target_values)
                
                comparison_results.append(result)
                
            except Exception as e:
                comparison_results.append({
                    'column': f"{source_column} → {target_column}" if source_column != target_column else source_column,
                    'status': 'FAILED',
                    'reason': f'Comparison error: {str(e)}',
                    'source_count': 0,
                    'target_count': 0,
                    'match_count': 0,
                    'warnings': []
                })
        
        return comparison_results

    def _is_numeric_type(self, data_type):
        """Check if data type is numeric."""
        numeric_types = ['INTEGER', 'BIGINT', 'SMALLINT', 'DECIMAL', 'NUMERIC', 
                        'FLOAT', 'DOUBLE', 'REAL', 'NUMBER', 'INT', 'MONEY']
        return any(nt in data_type for nt in numeric_types)

    def _is_text_type(self, data_type):
        """Check if data type is text/string."""
        text_types = ['VARCHAR', 'CHAR', 'TEXT', 'STRING', 'CLOB', 'NVARCHAR', 'NCHAR']
        return any(tt in data_type for tt in text_types)

    def _compare_numeric_column(self, column_name, source_values, target_values, tolerance):
        """Compare numeric column values with tolerance."""
        source_count = len(source_values)
        target_count = len(target_values)
        warnings = []
        
        if source_count != target_count:
            warnings.append(f'Row count mismatch: source={source_count}, target={target_count}')
        
        # Compare common values with tolerance
        min_count = min(source_count, target_count)
        match_count = 0
        mismatches = []
        detailed_mismatches = []  # Store detailed mismatch info
        
        for i in range(min_count):
            source_val = source_values[i]
            target_val = target_values[i]
            
            # Handle NULL values
            if source_val is None and target_val is None:
                match_count += 1
            elif source_val is None or target_val is None:
                mismatch_detail = {
                    'row': i + 1,
                    'source_value': source_val,
                    'target_value': target_val,
                    'issue': 'NULL mismatch'
                }
                mismatches.append(f'Row {i+1}: NULL mismatch - Source: {source_val}, Target: {target_val}')
                detailed_mismatches.append(mismatch_detail)
            else:
                try:
                    # Convert to float for comparison
                    source_num = float(source_val)
                    target_num = float(target_val)
                    difference = abs(source_num - target_num)
                    
                    # Check if within tolerance
                    if difference <= tolerance:
                        match_count += 1
                    else:
                        mismatch_detail = {
                            'row': i + 1,
                            'source_value': source_num,
                            'target_value': target_num,
                            'difference': difference,
                            'tolerance': tolerance,
                            'issue': f'Exceeds tolerance by {difference - tolerance:.6f}'
                        }
                        mismatches.append(f'Row {i+1}: {source_num} vs {target_num} (diff: {difference:.6f}, tolerance: {tolerance})')
                        detailed_mismatches.append(mismatch_detail)
                except (ValueError, TypeError):
                    mismatch_detail = {
                        'row': i + 1,
                        'source_value': source_val,
                        'target_value': target_val,
                        'issue': 'Non-numeric values'
                    }
                    mismatches.append(f'Row {i+1}: Non-numeric values - Source: {source_val}, Target: {target_val}')
                    detailed_mismatches.append(mismatch_detail)
        
        # Calculate match percentage
        match_percentage = (match_count / min_count * 100) if min_count > 0 else 0
        
        # Determine status (90% match threshold for numeric columns)
        if match_percentage >= 90:
            status = 'PASSED'
            reason = f'{match_percentage:.1f}% match rate within tolerance {tolerance}'
        else:
            status = 'FAILED'
            reason = f'{match_percentage:.1f}% match rate below threshold (90%)'
        
        return {
            'column': column_name,
            'status': status,
            'reason': reason,
            'source_count': source_count,
            'target_count': target_count,
            'match_count': match_count,
            'match_percentage': match_percentage,
            'warnings': warnings,
            'mismatches': mismatches,
            'detailed_mismatches': detailed_mismatches[:20]  # Store first 20 detailed mismatches
        }

    def _compare_text_column(self, column_name, source_values, target_values):
        """Compare text column values with exact matching and checksum for long texts."""
        source_count = len(source_values)
        target_count = len(target_values)
        warnings = []
        
        if source_count != target_count:
            warnings.append(f'Row count mismatch: source={source_count}, target={target_count}')
        
        # Compare common values
        min_count = min(source_count, target_count)
        exact_match_count = 0
        checksum_match_count = 0
        mismatches = []
        detailed_mismatches = []  # Store detailed mismatch info
        
        for i in range(min_count):
            source_val = source_values[i]
            target_val = target_values[i]
            
            # Handle NULL values
            if source_val is None and target_val is None:
                exact_match_count += 1
                checksum_match_count += 1
            elif source_val is None or target_val is None:
                mismatch_detail = {
                    'row': i + 1,
                    'source_value': source_val,
                    'target_value': target_val,
                    'issue': 'NULL mismatch'
                }
                mismatches.append(f'Row {i+1}: NULL mismatch - Source: {source_val}, Target: {target_val}')
                detailed_mismatches.append(mismatch_detail)
            else:
                # Convert to string
                source_str = str(source_val).strip()
                target_str = str(target_val).strip()
                
                # Exact match
                if source_str == target_str:
                    exact_match_count += 1
                    checksum_match_count += 1
                else:
                    # For long texts (>100 chars), compare checksums
                    if len(source_str) > 100 and len(target_str) > 100:
                        import hashlib
                        source_hash = hashlib.md5(source_str.encode()).hexdigest()
                        target_hash = hashlib.md5(target_str.encode()).hexdigest()
                        
                        if source_hash == target_hash:
                            checksum_match_count += 1
                            warnings.append(f'Row {i+1}: Different text but matching checksum')
                            mismatch_detail = {
                                'row': i + 1,
                                'source_value': f'{source_str[:100]}...',
                                'target_value': f'{target_str[:100]}...',
                                'source_checksum': source_hash,
                                'target_checksum': target_hash,
                                'issue': 'Different text but matching checksum'
                            }
                            detailed_mismatches.append(mismatch_detail)
                        else:
                            mismatch_detail = {
                                'row': i + 1,
                                'source_value': f'{source_str[:100]}...',
                                'target_value': f'{target_str[:100]}...',
                                'source_checksum': source_hash,
                                'target_checksum': target_hash,
                                'issue': 'Text and checksum mismatch'
                            }
                            mismatches.append(f'Row {i+1}: Text and checksum mismatch - Source: "{source_str[:50]}...", Target: "{target_str[:50]}..."')
                            detailed_mismatches.append(mismatch_detail)
                    else:
                        mismatch_detail = {
                            'row': i + 1,
                            'source_value': source_str,
                            'target_value': target_str,
                            'issue': 'Text values differ'
                        }
                        mismatches.append(f'Row {i+1}: Text mismatch - Source: "{source_str}", Target: "{target_str}"')
                        detailed_mismatches.append(mismatch_detail)
        
        # Calculate match percentages
        exact_match_percentage = (exact_match_count / min_count * 100) if min_count > 0 else 0
        checksum_match_percentage = (checksum_match_count / min_count * 100) if min_count > 0 else 0
        
        # Determine status (95% checksum match threshold for text columns)
        if checksum_match_percentage >= 95:
            status = 'PASSED'
            if exact_match_percentage == checksum_match_percentage:
                reason = f'{exact_match_percentage:.1f}% exact match rate'
            else:
                reason = f'{exact_match_percentage:.1f}% exact, {checksum_match_percentage:.1f}% checksum match'
        else:
            status = 'FAILED'
            reason = f'{checksum_match_percentage:.1f}% match rate below threshold (95%)'
        
        return {
            'column': column_name,
            'status': status,
            'reason': reason,
            'source_count': source_count,
            'target_count': target_count,
            'match_count': checksum_match_count,
            'exact_match_count': exact_match_count,
            'match_percentage': checksum_match_percentage,
            'warnings': warnings,
            'mismatches': mismatches,
            'detailed_mismatches': detailed_mismatches[:20]  # Store first 20 detailed mismatches
        }

    def _compare_generic_column(self, column_name, source_values, target_values):
        """Compare generic column values with exact matching."""
        source_count = len(source_values)
        target_count = len(target_values)
        warnings = []
        
        if source_count != target_count:
            warnings.append(f'Row count mismatch: source={source_count}, target={target_count}')
        
        # Compare common values
        min_count = min(source_count, target_count)
        match_count = 0
        mismatches = []
        detailed_mismatches = []  # Store detailed mismatch info
        
        for i in range(min_count):
            source_val = source_values[i]
            target_val = target_values[i]
            
            # Direct comparison
            if source_val == target_val:
                match_count += 1
            else:
                mismatch_detail = {
                    'row': i + 1,
                    'source_value': source_val,
                    'target_value': target_val,
                    'issue': 'Values differ'
                }
                mismatches.append(f'Row {i+1}: Value mismatch - Source: {source_val}, Target: {target_val}')
                detailed_mismatches.append(mismatch_detail)
        
        # Calculate match percentage
        match_percentage = (match_count / min_count * 100) if min_count > 0 else 0
        
        # Determine status (100% match threshold for generic columns)
        if match_percentage == 100:
            status = 'PASSED'
            reason = f'{match_percentage:.1f}% exact match'
        else:
            status = 'FAILED'
            reason = f'{match_percentage:.1f}% match rate below threshold (100%)'
        
        return {
            'column': column_name,
            'status': status,
            'reason': reason,
            'source_count': source_count,
            'target_count': target_count,
            'match_count': match_count,
            'match_percentage': match_percentage,
            'warnings': warnings,
            'mismatches': mismatches,
            'detailed_mismatches': detailed_mismatches[:20]  # Store first 20 detailed mismatches
        }

    def __repr__(self):
        """A friendly string representation of the object."""
        return f"<DataValidationTestCase ID='{self.test_case_id}' Priority='{self.priority}' Tags={self.tags}>"
