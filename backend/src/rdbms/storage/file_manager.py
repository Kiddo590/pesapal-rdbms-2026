"""
File-based storage manager for the RDBMS
"""

import os
import json
import pickle
from typing import Dict, List, Any
from datetime import datetime
from ..core.table import Table
from ..core.row import Row
from ..core.datatypes import DataType, TypeConverter


class FileManager:
    """Manage database file storage"""
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def create_table(self, table: Table):
        """Create storage for a table"""
        table_file = self._get_table_file(table.name)
        # Just create empty file for now
        with open(table_file, 'w') as f:
            json.dump([], f)
    
    def save_table(self, table: Table):
        """Save table data to disk"""
        table_file = self._get_table_file(table.name)
        
        # Serialize table data
        data = []
        for row in table.rows:
            row_data = row.to_dict()
            data.append(row_data)
        
        with open(table_file, 'w') as f:
            json.dump(data, f, indent=2, default=self._json_serializer)
    
    def load_table_data(self, table: Table):
        """Load table data from disk"""
        table_file = self._get_table_file(table.name)
        
        if not os.path.exists(table_file):
            return
        
        with open(table_file, 'r') as f:
            data = json.load(f)
        
        # Insert rows into table
        for row_data in data:
            try:
                table.insert(row_data)
            except Exception as e:
                print(f"Warning: Failed to load row: {e}")
    
    def drop_table(self, table_name: str):
        """Remove table storage"""
        table_file = self._get_table_file(table_name)
        if os.path.exists(table_file):
            os.remove(table_file)
    
    def _get_table_file(self, table_name: str) -> str:
        """Get path for table data file"""
        return os.path.join(self.storage_path, f"{table_name}.json")
    
    def _json_serializer(self, obj):
        """Custom JSON serializer for datetime objects"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")