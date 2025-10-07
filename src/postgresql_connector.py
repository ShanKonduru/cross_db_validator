"""
PostgreSQL Database Connector
Implementation of DatabaseConnectionBase for PostgreSQL databases
"""
from typing import List, Any, Tuple
from src.database_connection_base import DatabaseConnectionBase


class PostgreSQLConnector(DatabaseConnectionBase):
    """PostgreSQL database connector"""
    
    def __init__(self, host: str, port: int, username: str, password: str, database: str):
        super().__init__(host, port, username, password)
        self.database = database
    
    def connect(self) -> Tuple[bool, str]:
        """Connect to PostgreSQL database"""
        try:
            import psycopg2
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                connect_timeout=10
            )
            self.is_connected = True
            return True, "Connected to PostgreSQL successfully"
        except Exception as e:
            return False, f"PostgreSQL connection failed: {str(e)}"
    
    def disconnect(self) -> None:
        """Disconnect from PostgreSQL"""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass  # Ignore close errors
            finally:
                self.connection = None
                self.is_connected = False
    
    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """Execute PostgreSQL query"""
        if not self.is_connected:
            return False, "Not connected to database"
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                return True, result
        except Exception as e:
            return False, f"Error executing query: {str(e)}"
    
    def get_tables(self) -> List[str]:
        """Get PostgreSQL table names"""
        success, result = self.execute_query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        if success:
            return [row[0] for row in result]
        return []
    
    def get_table_schema(self, table_name: str) -> List[Tuple[str, str]]:
        """Get table schema information for PostgreSQL table"""
        try:
            # Handle schema-qualified table names (e.g., 'public.products')
            if '.' in table_name:
                schema_name, table_name_only = table_name.split('.', 1)
                schema_name = schema_name.replace("'", "''")
                table_name_only = table_name_only.replace("'", "''")
                query = f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = '{schema_name}' AND table_name = '{table_name_only}'
                ORDER BY ordinal_position
                """
            else:
                # No schema specified, use current schema
                table_name_clean = table_name.replace("'", "''")
                query = f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name_clean}' AND table_schema = current_schema()
                ORDER BY ordinal_position
                """
            
            success, result = self.execute_query(query)
            if success and result:
                # Return tuples of (column_name, data_type) for compatibility
                return [(row[0], row[1]) for row in result]
            return []
        except Exception as e:
            print(f"Error getting table schema for {table_name}: {e}")
            return []
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists in PostgreSQL - handles schema-qualified names"""
        try:
            # Handle schema-qualified table names (e.g., 'public.products')
            if '.' in table_name:
                schema_name, table_only = table_name.split('.', 1)
                # Remove quotes if present and sanitize
                schema_name = schema_name.strip('\'"').replace("'", "''")
                table_only = table_only.strip('\'"').replace("'", "''")
                
                query = f"""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = '{schema_name}' AND table_name = '{table_only}'
                """
            else:
                # No schema specified, check current schema
                # Sanitize table name
                table_name_clean = table_name.replace("'", "''")
                query = f"""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = '{table_name_clean}' AND table_schema = current_schema()
                """
            
            success, result = self.execute_query(query)
            if success and result and len(result) > 0:
                return result[0][0] > 0
            return False
        except Exception as e:
            print(f"Error checking table existence: {e}")
            return False
    
    def get_row_count(self, table_name: str) -> int:
        """Get row count for PostgreSQL table"""
        success, result = self.execute_query(f"SELECT COUNT(*) FROM {table_name}")
        if success and result:
            return result[0][0]
        return 0
    
    def get_row_count_with_where(self, table_name: str, where_clause: str = None) -> int:
        """Get row count for PostgreSQL table with optional WHERE clause"""
        if where_clause:
            # Ensure WHERE clause starts with WHERE if not already present
            if not where_clause.strip().upper().startswith('WHERE'):
                where_clause = f"WHERE {where_clause}"
            query = f"SELECT COUNT(*) FROM {table_name} {where_clause}"
        else:
            query = f"SELECT COUNT(*) FROM {table_name}"
            
        success, result = self.execute_query(query)
        if success and result:
            return result[0][0]
        return 0
    
    def close(self) -> None:
        """Close the PostgreSQL database connection. Alias for disconnect method."""
        self.disconnect()