"""
Table implementation with schema, constraints, and indexing
"""

import os
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from .datatypes import DataType, TypeConverter
from .row import Row
from .index import Index


class ColumnDefinition:
    """Definition for a single column"""
    
    def __init__(self, name: str, data_type: DataType, 
                 is_primary: bool = False, is_unique: bool = False,
                 default_value: Any = None, nullable: bool = True):
        self.name = name
        self.data_type = data_type
        self.is_primary = is_primary
        self.is_unique = is_unique
        self.default_value = default_value
        self.nullable = nullable
    
    def __repr__(self) -> str:
        constraints = []
        if self.is_primary:
            constraints.append("PRIMARY KEY")
        if self.is_unique:
            constraints.append("UNIQUE")
        if not self.nullable:
            constraints.append("NOT NULL")
        if self.default_value is not None:
            constraints.append(f"DEFAULT {self.default_value}")
        
        constraints_str = " ".join(constraints)
        return f"{self.name} {self.data_type.value}" + (f" {constraints_str}" if constraints_str else "")


class Table:
    """Database table with schema, constraints, and data"""
    
    def __init__(self, name: str, columns: List[ColumnDefinition]):
        """
        Initialize a table
        
        Args:
            name: Table name
            columns: List of column definitions
        """
        self.name = name
        self.columns = {col.name: col for col in columns}
        self.rows: List[Row] = []
        self.next_id = 1
        
        # Create indexes for primary and unique keys
        self.indexes: Dict[str, Index] = {}
        self.primary_key: Optional[str] = None
        self.unique_columns: Set[str] = set()
        
        # Setup constraints
        self._setup_constraints()
        
        # Statistics
        self.created_at = datetime.now()
        self.last_modified = datetime.now()
        self.row_count = 0
    
    def _setup_constraints(self):
        """Setup primary key and unique constraints"""
        for col_name, col_def in self.columns.items():
            if col_def.is_primary:
                if self.primary_key is not None:
                    raise ValueError("Multiple primary keys not supported")
                self.primary_key = col_name
                # Create index for primary key
                self.indexes[col_name] = Index(col_name)
            
            if col_def.is_unique:
                self.unique_columns.add(col_name)
                if col_name not in self.indexes:
                    self.indexes[col_name] = Index(col_name)
    
    def get_schema(self) -> Dict[str, DataType]:
        """Get column schema"""
        return {name: col.data_type for name, col in self.columns.items()}
    
    def insert(self, data: Dict[str, Any]) -> int:
        """
        Insert a new row
        
        Args:
            data: Column name -> value mapping
        
        Returns:
            int: Row ID (if primary key is INT)
        
        Raises:
            ValueError: If constraints violated
        """
        # Validate all columns exist
        for col_name in data.keys():
            if col_name not in self.columns:
                raise ValueError(f"Column '{col_name}' does not exist")
        
        # Apply defaults for missing columns
        row_data = {}
        for col_name, col_def in self.columns.items():
            if col_name in data:
                value = data[col_name]
            else:
                if col_def.default_value is not None:
                    value = col_def.default_value
                elif col_def.nullable:
                    value = None
                else:
                    raise ValueError(f"Column '{col_name}' cannot be NULL")
            
            # Validate data type
            if not TypeConverter.validate(value, col_def.data_type):
                raise ValueError(f"Invalid value for column '{col_name}': {value}")
            
            row_data[col_name] = value
        
        # Check constraints
        self._check_constraints(row_data)
        
        # Create row
        row = Row(row_data, self.get_schema())
        
        # Auto-increment primary key if needed
        if self.primary_key and self.columns[self.primary_key].data_type == DataType.INTEGER:
            if row_data.get(self.primary_key) is None:
                row[self.primary_key] = self.next_id
                self.next_id += 1
        
        # Add to rows list
        self.rows.append(row)
        
        # Update indexes
        for col_name, index in self.indexes.items():
            if col_name in row_data:
                index.add(row_data[col_name], len(self.rows) - 1)
        
        # Update statistics
        self.row_count += 1
        self.last_modified = datetime.now()
        
        return row.get(self.primary_key) if self.primary_key else len(self.rows)
    
    def _check_constraints(self, row_data: Dict[str, Any]):
        """Check all constraints before insertion"""
        # Check primary key uniqueness
        if self.primary_key and self.primary_key in row_data:
            pk_value = row_data[self.primary_key]
            if pk_value is not None:
                if self.primary_key in self.indexes:
                    if self.indexes[self.primary_key].contains(pk_value):
                        raise ValueError(f"Primary key violation: {pk_value} already exists")
        
        # Check unique constraints
        for col_name in self.unique_columns:
            if col_name in row_data and row_data[col_name] is not None:
                if col_name in self.indexes:
                    if self.indexes[col_name].contains(row_data[col_name]):
                        raise ValueError(f"Unique constraint violation on '{col_name}': {row_data[col_name]} already exists")
    
    def select(self, conditions: Optional[Dict[str, Any]] = None,
               columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Select rows matching conditions
        
        Args:
            conditions: Column -> value mapping for WHERE clause
            columns: List of columns to return (None for all)
        
        Returns:
            List of rows as dictionaries
        """
        results = []
        
        # Use index if available for single condition
        if conditions and len(conditions) == 1:
            col_name, value = next(iter(conditions.items()))
            if col_name in self.indexes:
                row_indices = self.indexes[col_name].get(value)
                for idx in row_indices:
                    if idx < len(self.rows):
                        row = self.rows[idx]
                        if row.matches_condition(conditions):
                            results.append(self._format_row(row, columns))
                return results
        
        # Otherwise scan all rows
        for row in self.rows:
            if not conditions or row.matches_condition(conditions):
                results.append(self._format_row(row, columns))
        
        return results
    
    def _format_row(self, row: Row, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Format row for output"""
        if columns:
            return {col: row[col] for col in columns if col in row}
        return row.to_dict()
    
    def update(self, data: Dict[str, Any], conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        Update rows matching conditions
        
        Args:
            data: Column -> new value mapping
            conditions: WHERE clause conditions
        
        Returns:
            int: Number of rows updated
        """
        updated_count = 0
        
        for i, row in enumerate(self.rows):
            if not conditions or row.matches_condition(conditions):
                # Check constraints for updated values
                new_data = row.to_dict()
                new_data.update(data)
                self._check_update_constraints(row, new_data)
                
                # Update row
                for col_name, value in data.items():
                    if col_name in self.columns:
                        row[col_name] = value
                
                # Update indexes
                for col_name in data.keys():
                    if col_name in self.indexes:
                        old_value = row.to_dict().get(col_name)
                        new_value = data[col_name]
                        self.indexes[col_name].update(old_value, new_value, i)
                
                updated_count += 1
        
        if updated_count > 0:
            self.last_modified = datetime.now()
        
        return updated_count
    
    def _check_update_constraints(self, original_row: Row, new_data: Dict[str, Any]):
        """Check constraints for update operation"""
        # Skip checking the row itself for uniqueness
        pass  # Simplified for now
    
    def delete(self, conditions: Optional[Dict[str, Any]] = None) -> int:
        """
        Delete rows matching conditions
        
        Args:
            conditions: WHERE clause conditions
        
        Returns:
            int: Number of rows deleted
        """
        # Mark rows for deletion
        to_delete = []
        for i, row in enumerate(self.rows):
            if not conditions or row.matches_condition(conditions):
                to_delete.append((i, row))
        
        # Remove from end to avoid index shifting issues
        for i, row in reversed(to_delete):
            # Remove from indexes
            for col_name, index in self.indexes.items():
                if col_name in row:
                    index.remove(row[col_name], i)
            
            # Remove row
            del self.rows[i]
        
        deleted_count = len(to_delete)
        self.row_count -= deleted_count
        
        if deleted_count > 0:
            self.last_modified = datetime.now()
        
        return deleted_count
    
    def describe(self) -> Dict[str, Any]:
        """Get table description"""
        return {
            "name": self.name,
            "columns": [str(col) for col in self.columns.values()],
            "primary_key": self.primary_key,
            "unique_columns": list(self.unique_columns),
            "row_count": self.row_count,
            "created_at": self.created_at.isoformat(),
            "last_modified": self.last_modified.isoformat()
        }
    
    def create_index(self, column_name: str):
        """Create index on column"""
        if column_name not in self.columns:
            raise ValueError(f"Column '{column_name}' does not exist")
        
        if column_name not in self.indexes:
            self.indexes[column_name] = Index(column_name)
            
            # Build index from existing data
            for i, row in enumerate(self.rows):
                if column_name in row:
                    self.indexes[column_name].add(row[column_name], i)
    
    def drop_index(self, column_name: str):
        """Drop index on column"""
        if column_name in self.indexes and column_name != self.primary_key:
            del self.indexes[column_name]
            if column_name in self.unique_columns:
                self.unique_columns.remove(column_name)