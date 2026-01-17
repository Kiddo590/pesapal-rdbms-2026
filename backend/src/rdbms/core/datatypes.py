"""
Data types supported by the RDBMS
"""

from enum import Enum
from datetime import datetime
from typing import Any, Union


class DataType(Enum):
    """Supported data types"""
    INTEGER = "INT"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    FLOAT = "FLOAT"
    TIMESTAMP = "TIMESTAMP"
    DATE = "DATE"


class TypeConverter:
    """Convert values between Python types and database storage"""
    
    @staticmethod
    def validate(value: Any, data_type: DataType) -> bool:
        """Validate if value matches data type"""
        try:
            TypeConverter.convert(value, data_type)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def convert(value: Any, data_type: DataType) -> Any:
        """Convert value to appropriate Python type"""
        if value is None:
            return None
        
        if data_type == DataType.INTEGER:
            return int(value)
        elif data_type == DataType.FLOAT:
            return float(value)
        elif data_type == DataType.TEXT:
            return str(value)
        elif data_type == DataType.BOOLEAN:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 't', 'y')
            return bool(value)
        elif data_type == DataType.TIMESTAMP:
            if isinstance(value, str):
                # Parse ISO format string
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value
        elif data_type == DataType.DATE:
            if isinstance(value, str):
                return datetime.strptime(value, '%Y-%m-%d').date()
            return value
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    @staticmethod
    def serialize(value: Any, data_type: DataType) -> str:
        """Serialize value for storage"""
        if value is None:
            return "NULL"
        
        if data_type == DataType.TEXT:
            # Escape quotes
            escaped = str(value).replace("'", "''")
            return f"'{escaped}'"
        elif data_type == DataType.TIMESTAMP:
            if isinstance(value, datetime):
                return f"'{value.isoformat()}'"
            return f"'{value}'"
        elif data_type == DataType.DATE:
            if hasattr(value, 'isoformat'):
                return f"'{value.isoformat()}'"
            return f"'{value}'"
        elif data_type == DataType.BOOLEAN:
            return 'TRUE' if value else 'FALSE'
        else:
            return str(value)