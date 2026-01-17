"""
Main database class implementing RDBMS core functionality
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .table import Table, ColumnDefinition
from .datatypes import DataType
from ..storage.file_manager import FileManager
from ..query.executor import QueryExecutor
from ..query.planner import QueryPlanner


class Database:
    """Main database class"""
    
    def __init__(self, name: str, storage_path: str = "data"):
        """
        Initialize database
        
        Args:
            name: Database name
            storage_path: Path for database files
        """
        self.name = name
        self.tables: Dict[str, Table] = {}
        self.storage_path = os.path.join(storage_path, name)
        self.file_manager = FileManager(self.storage_path)
        self.query_planner = QueryPlanner()
        self.query_executor = QueryExecutor(self)
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Load existing tables
        self._load_tables()
    
    def _load_tables(self):
        """Load tables from storage"""
        if not os.path.exists(self.storage_path):
            return
        
        # Load table definitions
        schema_file = os.path.join(self.storage_path, "schema.json")
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema_data = json.load(f)
                
            for table_name, table_info in schema_data.items():
                # Recreate table structure
                columns = []
                for col_info in table_info['columns']:
                    col_def = ColumnDefinition(
                        name=col_info['name'],
                        data_type=DataType(col_info['type']),
                        is_primary=col_info.get('is_primary', False),
                        is_unique=col_info.get('is_unique', False),
                        default_value=col_info.get('default'),
                        nullable=col_info.get('nullable', True)
                    )
                    columns.append(col_def)
                
                table = Table(table_name, columns)
                self.tables[table_name] = table
                
                # Load table data
                self.file_manager.load_table_data(table)
    
    def _save_schema(self):
        """Save database schema to disk"""
        schema_data = {}
        for table_name, table in self.tables.items():
            schema_data[table_name] = {
                'columns': [
                    {
                        'name': col.name,
                        'type': col.data_type.value,
                        'is_primary': col.is_primary,
                        'is_unique': col.is_unique,
                        'default': col.default_value,
                        'nullable': col.nullable
                    }
                    for col in table.columns.values()
                ]
            }
        
        schema_file = os.path.join(self.storage_path, "schema.json")
        with open(schema_file, 'w') as f:
            json.dump(schema_data, f, indent=2)
    
    def create_table(self, table_name: str, columns: List[ColumnDefinition]) -> Table:
        """
        Create a new table
        
        Args:
            table_name: Name of the table
            columns: List of column definitions
        
        Returns:
            Table: Created table object
        
        Raises:
            ValueError: If table already exists
        """
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists")
        
        table = Table(table_name, columns)
        self.tables[table_name] = table
        
        # Save schema
        self._save_schema()
        
        # Create storage for table
        self.file_manager.create_table(table)
        
        return table
    
    def drop_table(self, table_name: str) -> bool:
        """
        Drop a table
        
        Args:
            table_name: Name of table to drop
        
        Returns:
            bool: True if dropped successfully
        """
        if table_name not in self.tables:
            return False
        
        # Remove from memory
        del self.tables[table_name]
        
        # Remove from storage
        self.file_manager.drop_table(table_name)
        
        # Update schema
        self._save_schema()
        
        return True
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> int:
        """
        Insert row into table
        
        Args:
            table_name: Table name
            data: Row data
        
        Returns:
            int: Row ID
        
        Raises:
            ValueError: If table doesn't exist
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        table = self.tables[table_name]
        row_id = table.insert(data)
        
        # Save to storage
        self.file_manager.save_table(table)
        
        return row_id
    
    def select(self, table_name: str, conditions: Optional[Dict[str, Any]] = None,
               columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Select rows from table
        
        Args:
            table_name: Table name
            conditions: WHERE conditions
            columns: Columns to return
        
        Returns:
            List of rows
        
        Raises:
            ValueError: If table doesn't exist
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        return self.tables[table_name].select(conditions, columns)
    
    def update(self, table_name: str, data: Dict[str, Any], 
               conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        Update rows in table
        
        Args:
            table_name: Table name
            data: Data to update
            conditions: WHERE conditions
        
        Returns:
            int: Number of rows updated
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        table = self.tables[table_name]
        updated = table.update(data, conditions)
        
        if updated > 0:
            self.file_manager.save_table(table)
        
        return updated
    
    def delete(self, table_name: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        Delete rows from table
        
        Args:
            table_name: Table name
            conditions: WHERE conditions
        
        Returns:
            int: Number of rows deleted
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        table = self.tables[table_name]
        deleted = table.delete(conditions)
        
        if deleted > 0:
            self.file_manager.save_table(table)
        
        return deleted
    
    def execute_query(self, query: str) -> Any:
        """
        Execute SQL-like query
        
        Args:
            query: SQL query string
        
        Returns:
            Query result
        """
        # Parse and plan query
        query_plan = self.query_planner.plan(query)
        
        # Execute query
        return self.query_executor.execute(query_plan)
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a table"""
        if table_name not in self.tables:
            return None
        return self.tables[table_name].describe()
    
    def list_tables(self) -> List[str]:
        """List all tables in database"""
        return list(self.tables.keys())
    
    def join(self, table1: str, table2: str, 
             on_condition: Tuple[str, str]) -> List[Dict[str, Any]]:
        """
        Perform INNER JOIN between two tables
        
        Args:
            table1: First table name
            table2: Second table name
            on_condition: Tuple of (table1.column, table2.column)
        
        Returns:
            List of joined rows
        """
        if table1 not in self.tables or table2 not in self.tables:
            raise ValueError("One or both tables do not exist")
        
        t1 = self.tables[table1]
        t2 = self.tables[table2]
        
        col1, col2 = on_condition
        
        results = []
        t1_rows = t1.select()
        t2_rows = t2.select()
        
        # Simple nested loop join (can be optimized)
        for row1 in t1_rows:
            for row2 in t2_rows:
                if row1.get(col1) == row2.get(col2):
                    # Merge rows
                    merged = {f"{table1}.{k}": v for k, v in row1.items()}
                    merged.update({f"{table2}.{k}": v for k, v in row2.items()})
                    results.append(merged)
        
        return results
    
    def create_index(self, table_name: str, column_name: str):
        """Create index on table column"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        self.tables[table_name].create_index(column_name)
    
    def drop_index(self, table_name: str, column_name: str):
        """Drop index from table column"""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' does not exist")
        
        self.tables[table_name].drop_index(column_name)