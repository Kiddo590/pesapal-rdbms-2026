"""
Query executor for parsed queries
"""

from typing import Any, List, Dict
from ..core.database import Database
from ..core.table import ColumnDefinition
from .query_parser import QueryType


class QueryExecutor:
    """Execute parsed queries against database"""
    
    def __init__(self, database: Database):
        self.db = database
    
    def execute(self, query_plan: Dict[str, Any]) -> Any:
        """
        Execute query plan
        
        Args:
            query_plan: Parsed query structure
        
        Returns:
            Query result
        """
        query_type = query_plan['type']
        
        if query_type == QueryType.CREATE_TABLE:
            return self._execute_create_table(query_plan)
        elif query_type == QueryType.INSERT:
            return self._execute_insert(query_plan)
        elif query_type == QueryType.SELECT:
            return self._execute_select(query_plan)
        elif query_type == QueryType.UPDATE:
            return self._execute_update(query_plan)
        elif query_type == QueryType.DELETE:
            return self._execute_delete(query_plan)
        elif query_type == QueryType.DROP_TABLE:
            return self._execute_drop_table(query_plan)
        elif query_type == QueryType.SHOW_TABLES:
            return self._execute_show_tables(query_plan)
        elif query_type == QueryType.DESCRIBE:
            return self._execute_describe(query_plan)
        elif query_type == QueryType.CREATE_INDEX:
            return self._execute_create_index(query_plan)
        elif query_type == QueryType.DROP_INDEX:
            return self._execute_drop_index(query_plan)
        else:
            raise ValueError(f"Unsupported query type: {query_type}")
    
    def _execute_create_table(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CREATE TABLE"""
        table_name = query_plan['table_name']
        columns_def = []
        
        for col_info in query_plan['columns']:
            col_def = ColumnDefinition(
                name=col_info['name'],
                data_type=col_info['type'],
                is_primary=col_info.get('is_primary', False),
                is_unique=col_info.get('is_unique', False),
                default_value=col_info.get('default'),
                nullable=col_info.get('nullable', True)
            )
            columns_def.append(col_def)
        
        table = self.db.create_table(table_name, columns_def)
        return {
            'message': f"Table '{table_name}' created successfully",
            'table': table.describe()
        }
    
    def _execute_insert(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute INSERT"""
        table_name = query_plan['table_name']
        values = query_plan['values']
        columns = query_plan.get('columns')
        
        # Create data dictionary
        if columns:
            if len(columns) != len(values):
                raise ValueError(f"Column count ({len(columns)}) doesn't match value count ({len(values)})")
            data = dict(zip(columns, values))
        else:
            # Get table schema to map values to columns
            table_info = self.db.get_table_info(table_name)
            if not table_info:
                raise ValueError(f"Table '{table_name}' does not exist")
            
            # For now, assume values are in column order
            # In a real implementation, we'd need schema info
            data = {}
            # Simplified - just use column index
            raise NotImplementedError("INSERT without column list needs schema")
        
        row_id = self.db.insert(table_name, data)
        return {
            'message': f"Row inserted successfully with ID: {row_id}",
            'row_id': row_id
        }
    
    def _execute_select(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SELECT"""
        table_name = query_plan['table_name']
        columns = query_plan.get('columns')
        conditions = query_plan.get('conditions')
        
        rows = self.db.select(table_name, conditions, columns)
        
        # Apply ordering if specified
        if query_plan.get('order_by'):
            order_col = query_plan['order_by']
            reverse = query_plan.get('order_desc', False)
            
            def get_sort_key(row):
                val = row.get(order_col)
                # Handle None values for sorting
                return (val is None, val)
            
            rows.sort(key=get_sort_key, reverse=reverse)
        
        return {
            'rows': rows,
            'count': len(rows)
        }
    
    def _execute_update(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute UPDATE"""
        table_name = query_plan['table_name']
        updates = query_plan['updates']
        conditions = query_plan.get('conditions')
        
        updated = self.db.update(table_name, updates, conditions)
        return {
            'message': f"{updated} row(s) updated",
            'affected_rows': updated
        }
    
    def _execute_delete(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DELETE"""
        table_name = query_plan['table_name']
        conditions = query_plan.get('conditions')
        
        deleted = self.db.delete(table_name, conditions)
        return {
            'message': f"{deleted} row(s) deleted",
            'affected_rows': deleted
        }
    
    def _execute_drop_table(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DROP TABLE"""
        table_name = query_plan['table_name']
        success = self.db.drop_table(table_name)
        
        if success:
            return {'message': f"Table '{table_name}' dropped successfully"}
        else:
            return {'message': f"Table '{table_name}' does not exist"}
    
    def _execute_show_tables(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SHOW TABLES"""
        tables = self.db.list_tables()
        return {
            'tables': tables,
            'count': len(tables)
        }
    
    def _execute_describe(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DESCRIBE"""
        table_name = query_plan['table_name']
        table_info = self.db.get_table_info(table_name)
        
        if table_info:
            return table_info
        else:
            return {'message': f"Table '{table_name}' does not exist"}
    
    def _execute_create_index(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute CREATE INDEX"""
        table_name = query_plan['table_name']
        column_name = query_plan['column_name']
        
        self.db.create_index(table_name, column_name)
        return {
            'message': f"Index created on {table_name}.{column_name}"
        }
    
    def _execute_drop_index(self, query_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DROP INDEX"""
        table_name = query_plan['table_name']
        column_name = query_plan['column_name']
        
        self.db.drop_index(table_name, column_name)
        return {
            'message': f"Index dropped from {table_name}.{column_name}"
        }