"""
Basic indexing implementation for faster lookups
"""

from typing import Dict, List, Set, Any
from collections import defaultdict


class Index:
    """Simple index for column values"""
    
    def __init__(self, column_name: str):
        self.column_name = column_name
        self.index: Dict[Any, Set[int]] = defaultdict(set)
    
    def add(self, value: Any, row_index: int):
        """Add value to index"""
        self.index[value].add(row_index)
    
    def remove(self, value: Any, row_index: int):
        """Remove value from index"""
        if value in self.index:
            self.index[value].discard(row_index)
            if not self.index[value]:
                del self.index[value]
    
    def update(self, old_value: Any, new_value: Any, row_index: int):
        """Update index when value changes"""
        if old_value is not None:
            self.remove(old_value, row_index)
        if new_value is not None:
            self.add(new_value, row_index)
    
    def get(self, value: Any) -> List[int]:
        """Get row indices for value"""
        return list(self.index.get(value, set()))
    
    def contains(self, value: Any) -> bool:
        """Check if value exists in index"""
        return value in self.index and len(self.index[value]) > 0
    
    def get_all_values(self) -> List[Any]:
        """Get all indexed values"""
        return list(self.index.keys())
    
    def size(self) -> int:
        """Get number of indexed entries"""
        return sum(len(indices) for indices in self.index.values())