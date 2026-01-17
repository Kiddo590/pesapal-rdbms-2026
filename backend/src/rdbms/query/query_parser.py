"""
SQL-like query parser for the custom RDBMS
"""

import re
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple, Union
from ..core.datatypes import DataType


class QueryType(Enum):
    """Types of SQL queries"""
    CREATE_TABLE = "CREATE_TABLE"
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    DROP_TABLE = "DROP_TABLE"
    SHOW_TABLES = "SHOW_TABLES"
    DESCRIBE = "DESCRIBE"
    CREATE_INDEX = "CREATE_INDEX"
    DROP_INDEX = "DROP_INDEX"
    JOIN = "JOIN"


class QueryParser:
    """Parse SQL-like queries into structured format"""
    
    def __init__(self):
        self.keywords = {
            'SELECT', 'FROM', 'WHERE', 'INSERT', 'INTO', 'VALUES',
            'UPDATE', 'SET', 'DELETE', 'CREATE', 'TABLE', 'DROP',
            'SHOW', 'TABLES', 'DESCRIBE', 'INDEX', 'ON', 'JOIN',
            'INNER', 'LEFT', 'RIGHT', 'OUTER', 'PRIMARY', 'KEY',
            'UNIQUE', 'NOT', 'NULL', 'DEFAULT', 'AND', 'OR',
            'INT', 'TEXT', 'BOOLEAN', 'FLOAT', 'TIMESTAMP', 'DATE'
        }
    
    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse SQL query into structured format
        
        Args:
            query: SQL query string
        
        Returns:
            Parsed query structure
        """
        query = query.strip().upper()
        
        if query.startswith('CREATE TABLE'):
            return self._parse_create_table(query)
        elif query.startswith('INSERT INTO'):
            return self._parse_insert(query)
        elif query.startswith('SELECT'):
            return self._parse_select(query)
        elif query.startswith('UPDATE'):
            return self._parse_update(query)
        elif query.startswith('DELETE FROM'):
            return self._parse_delete(query)
        elif query.startswith('DROP TABLE'):
            return self._parse_drop_table(query)
        elif query.startswith('SHOW TABLES'):
            return {'type': QueryType.SHOW_TABLES}
        elif query.startswith('DESCRIBE'):
            return self._parse_describe(query)
        elif query.startswith('CREATE INDEX'):
            return self._parse_create_index(query)
        elif query.startswith('DROP INDEX'):
            return self._parse_drop_index(query)
        else:
            raise ValueError(f"Unsupported query: {query}")
    
    def _parse_create_table(self, query: str) -> Dict[str, Any]:
        """Parse CREATE TABLE query"""
        # Extract table name
        match = re.match(r'CREATE TABLE (\w+)\s*\((.*)\)', query, re.DOTALL | re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        
        table_name = match.group(1).lower()
        columns_str = match.group(2).strip()
        
        # Parse column definitions
        columns = []
        column_defs = self._split_columns(columns_str)
        
        for col_def in column_defs:
            col_parts = col_def.strip().split()
            col_name = col_parts[0].lower()
            col_type = col_parts[1].upper()
            
            # Parse constraints
            is_primary = 'PRIMARY KEY' in col_def.upper()
            is_unique = 'UNIQUE' in col_def.upper()
            nullable = 'NOT NULL' not in col_def.upper()
            
            # Parse default value
            default_match = re.search(r'DEFAULT\s+(\S+)', col_def, re.IGNORECASE)
            default_value = default_match.group(1) if default_match else None
            
            columns.append({
                'name': col_name,
                'type': DataType(col_type),
                'is_primary': is_primary,
                'is_unique': is_unique,
                'nullable': nullable,
                'default': default_value
            })
        
        return {
            'type': QueryType.CREATE_TABLE,
            'table_name': table_name,
            'columns': columns
        }
    
    def _split_columns(self, columns_str: str) -> List[str]:
        """Split column definitions, handling nested parentheses"""
        parts = []
        current = []
        paren_depth = 0
        
        for char in columns_str:
            if char == '(':
                paren_depth += 1
                current.append(char)
            elif char == ')':
                paren_depth -= 1
                current.append(char)
            elif char == ',' and paren_depth == 0:
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(char)
        
        if current:
            parts.append(''.join(current).strip())
        
        return parts
    
    def _parse_insert(self, query: str) -> Dict[str, Any]:
        """Parse INSERT query"""
        # Extract table name and values
        match = re.match(r'INSERT INTO (\w+)\s*(?:\((.*?)\))?\s*VALUES\s*\((.*)\)', 
                        query, re.DOTALL | re.IGNORECASE)
        if not match:
            raise ValueError("Invalid INSERT syntax")
        
        table_name = match.group(1).lower()
        columns_str = match.group(2)
        values_str = match.group(3)
        
        # Parse column names (if specified)
        columns = None
        if columns_str:
            columns = [col.strip().lower() for col in columns_str.split(',')]
        
        # Parse values
        values = self._parse_values(values_str)
        
        return {
            'type': QueryType.INSERT,
            'table_name': table_name,
            'columns': columns,
            'values': values
        }
    
    def _parse_values(self, values_str: str) -> List[Any]:
        """Parse comma-separated values, handling quoted strings"""
        values = []
        current = []
        in_quote = False
        quote_char = None
        
        for char in values_str:
            if char in ("'", '"') and (not in_quote or char == quote_char):
                in_quote = not in_quote
                quote_char = char if in_quote else None
                current.append(char)
            elif char == ',' and not in_quote:
                val_str = ''.join(current).strip()
                values.append(self._parse_value(val_str))
                current = []
            else:
                current.append(char)
        
        if current:
            val_str = ''.join(current).strip()
            values.append(self._parse_value(val_str))
        
        return values
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse a single value"""
        if not value_str:
            return None
        
        # Remove quotes from strings
        if (value_str.startswith("'") and value_str.endswith("'")) or \
           (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]
        
        # Parse numbers
        if value_str.isdigit():
            return int(value_str)
        try:
            return float(value_str)
        except ValueError:
            pass
        
        # Parse booleans
        if value_str.upper() in ('TRUE', 'FALSE'):
            return value_str.upper() == 'TRUE'
        
        # Parse NULL
        if value_str.upper() == 'NULL':
            return None
        
        return value_str
    
    def _parse_select(self, query: str) -> Dict[str, Any]:
        """Parse SELECT query"""
        # Extract parts
        select_match = re.match(
            r'SELECT\s+(.*?)\s+FROM\s+(\w+)(?:\s+WHERE\s+(.*?))?(?:\s+ORDER BY\s+(.*))?$',
            query, re.DOTALL | re.IGNORECASE
        )
        
        if not select_match:
            raise ValueError("Invalid SELECT syntax")
        
        columns_str = select_match.group(1).strip()
        table_name = select_match.group(2).lower()
        where_clause = select_match.group(3)
        order_by = select_match.group(4)
        
        # Parse columns
        if columns_str == '*':
            columns = None
        else:
            columns = [col.strip().lower() for col in columns_str.split(',')]
        
        # Parse WHERE conditions
        conditions = None
        if where_clause:
            conditions = self._parse_conditions(where_clause)
        
        # Parse ORDER BY
        order_by_col = None
        order_desc = False
        if order_by:
            if order_by.upper().endswith(' DESC'):
                order_by_col = order_by[:-5].strip().lower()
                order_desc = True
            else:
                order_by_col = order_by.replace(' ASC', '').strip().lower()
        
        return {
            'type': QueryType.SELECT,
            'table_name': table_name,
            'columns': columns,
            'conditions': conditions,
            'order_by': order_by_col,
            'order_desc': order_desc
        }
    
    def _parse_conditions(self, where_clause: str) -> Dict[str, Any]:
        """Parse WHERE conditions"""
        conditions = {}
        
        # Simple equality conditions for now
        if ' AND ' in where_clause.upper():
            parts = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)
            for part in parts:
                self._parse_single_condition(part, conditions)
        elif ' OR ' in where_clause.upper():
            # For simplicity, treat OR as multiple conditions
            parts = re.split(r'\s+OR\s+', where_clause, flags=re.IGNORECASE)
            for part in parts:
                self._parse_single_condition(part, conditions)
        else:
            self._parse_single_condition(where_clause, conditions)
        
        return conditions
    
    def _parse_single_condition(self, condition: str, conditions_dict: Dict[str, Any]):
        """Parse a single condition"""
        operators = ['=', '!=', '<', '>', '<=', '>=', 'LIKE']
        
        for op in operators:
            if op in condition:
                col, val = condition.split(op, 1)
                col = col.strip().lower()
                val = self._parse_value(val.strip())
                conditions_dict[col] = val
                return
        
        raise ValueError(f"Could not parse condition: {condition}")
    
    def _parse_update(self, query: str) -> Dict[str, Any]:
        """Parse UPDATE query"""
        match = re.match(
            r'UPDATE\s+(\w+)\s+SET\s+(.*?)(?:\s+WHERE\s+(.*))?$',
            query, re.DOTALL | re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Invalid UPDATE syntax")
        
        table_name = match.group(1).lower()
        set_clause = match.group(2)
        where_clause = match.group(3)
        
        # Parse SET clause
        updates = {}
        assignments = set_clause.split(',')
        for assignment in assignments:
            col, val = assignment.split('=', 1)
            col = col.strip().lower()
            val = self._parse_value(val.strip())
            updates[col] = val
        
        # Parse WHERE conditions
        conditions = None
        if where_clause:
            conditions = self._parse_conditions(where_clause)
        
        return {
            'type': QueryType.UPDATE,
            'table_name': table_name,
            'updates': updates,
            'conditions': conditions
        }
    
    def _parse_delete(self, query: str) -> Dict[str, Any]:
        """Parse DELETE query"""
        match = re.match(
            r'DELETE FROM\s+(\w+)(?:\s+WHERE\s+(.*))?$',
            query, re.DOTALL | re.IGNORECASE
        )
        
        if not match:
            raise ValueError("Invalid DELETE syntax")
        
        table_name = match.group(1).lower()
        where_clause = match.group(2)
        
        conditions = None
        if where_clause:
            conditions = self._parse_conditions(where_clause)
        
        return {
            'type': QueryType.DELETE,
            'table_name': table_name,
            'conditions': conditions
        }
    
    def _parse_drop_table(self, query: str) -> Dict[str, Any]:
        """Parse DROP TABLE query"""
        match = re.match(r'DROP TABLE (\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DROP TABLE syntax")
        
        return {
            'type': QueryType.DROP_TABLE,
            'table_name': match.group(1).lower()
        }
    
    def _parse_describe(self, query: str) -> Dict[str, Any]:
        """Parse DESCRIBE query"""
        match = re.match(r'DESCRIBE (\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DESCRIBE syntax")
        
        return {
            'type': QueryType.DESCRIBE,
            'table_name': match.group(1).lower()
        }
    
    def _parse_create_index(self, query: str) -> Dict[str, Any]:
        """Parse CREATE INDEX query"""
        match = re.match(r'CREATE INDEX ON (\w+)\s*\((.*?)\)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE INDEX syntax")
        
        return {
            'type': QueryType.CREATE_INDEX,
            'table_name': match.group(1).lower(),
            'column_name': match.group(2).strip().lower()
        }
    
    def _parse_drop_index(self, query: str) -> Dict[str, Any]:
        """Parse DROP INDEX query"""
        match = re.match(r'DROP INDEX ON (\w+)\s*\((.*?)\)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DROP INDEX syntax")
        
        return {
            'type': QueryType.DROP_INDEX,
            'table_name': match.group(1).lower(),
            'column_name': match.group(2).strip().lower()
        }