"""
Row implementation for database records
"""

from typing import Dict, Any, List
from .datatypes import DataType, TypeConverter


class Row:
    """Represents a single row in a table"""
    
    def __init__(self, data: Dict[str, Any], schema: Dict[str, DataType]):
        """
        Initialize a row with data and schema
        
        Args:
            data: Dictionary of column name -> value
            schema: Dictionary of column name -> data type
        """
        self.data = {}
        self.schema = schema
        
        # Validate and convert all values
        for col_name, col_type in schema.items():
            if col_name in data:
                self.data[col_name] = TypeConverter.convert(data[col_name], col_type)
            else:
                self.data[col_name] = None
    
    def __getitem__(self, column: str) -> Any:
        """Get value by column name"""
        return self.data.get(column)
    
    def __setitem__(self, column: str, value: Any):
        """Set value for column"""
        if column not in self.schema:
            raise KeyError(f"Column '{column}' not in schema")
        self.data[column] = TypeConverter.convert(value, self.schema[column])
    
    def __contains__(self, column: str) -> bool:
        """Check if column exists in row"""
        return column in self.data
    
    def get(self, column: str, default: Any = None) -> Any:
        """Get value with default"""
        return self.data.get(column, default)
    
    def items(self):
        """Get items iterator"""
        return self.data.items()
    
    def keys(self):
        """Get column names"""
        return self.data.keys()
    
    def values(self):
        """Get values"""
        return self.data.values()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert row to dictionary"""
        return self.data.copy()
    
    def matches_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Check if row matches condition
        
        Args:
            condition: Dictionary of column -> expected value
        
        Returns:
            bool: True if all conditions match
        """
        for column, expected_value in condition.items():
            if column not in self.data:
                return False
            
            # Handle None/NULL values
            if expected_value is None:
                if self.data[column] is not None:
                    return False
            elif self.data[column] != expected_value:
                return False
        
        return True
    
    def serialize(self) -> Dict[str, str]:
        """Serialize row for storage"""
        serialized = {}
        for col_name, value in self.data.items():
            if value is None:
                serialized[col_name] = "NULL"
            else:
                col_type = self.schema[col_name]
                serialized[col_name] = TypeConverter.serialize(value, col_type)
        return serialized