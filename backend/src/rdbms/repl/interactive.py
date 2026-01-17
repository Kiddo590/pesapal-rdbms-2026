"""
Interactive REPL for the RDBMS
"""

import sys
import traceback
from typing import Optional
from ..core.database import Database
from ..query.query_parser import QueryParser
from ..query.executor import QueryExecutor


class REPL:
    """Read-Eval-Print Loop for interactive SQL"""
    
    def __init__(self, db_name: str = "default"):
        self.db = Database(db_name)
        self.parser = QueryParser()
        self.executor = QueryExecutor(self.db)
        self.running = True
        self.prompt = "rdbms> "
        self.multiline = False
        self.current_query = ""
    
    def run(self):
        """Start the REPL"""
        print("=" * 60)
        print("PESAPAL RDBMS INTERACTIVE SHELL")
        print("=" * 60)
        print("Type 'exit' to quit, 'help' for commands")
        print("Use semicolon (;) to end multi-line queries")
        print()
        
        while self.running:
            try:
                # Get input
                if self.multiline:
                    line = input("... ")
                else:
                    line = input(self.prompt)
                
                # Handle special commands
                if not self.multiline:
                    if line.lower() == 'exit':
                        self.running = False
                        continue
                    elif line.lower() == 'help':
                        self._show_help()
                        continue
                    elif line.lower() == 'clear':
                        import os
                        os.system('cls' if os.name == 'nt' else 'clear')
                        continue
                    elif line.lower() == 'tables':
                        self._list_tables()
                        continue
                
                # Add to current query
                self.current_query += line + " "
                
                # Check if query is complete
                if ';' in line or (not self.multiline and line.strip()):
                    if self.multiline:
                        # Remove semicolon for multiline
                        self.current_query = self.current_query.replace(';', '')
                    
                    self._execute_current_query()
                    self.current_query = ""
                    self.multiline = False
                else:
                    self.multiline = True
                    
            except KeyboardInterrupt:
                print("\nInterrupted. Type 'exit' to quit.")
                self.current_query = ""
                self.multiline = False
            except EOFError:
                print("\nExiting...")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")
                if self.multiline:
                    self.current_query = ""
                    self.multiline = False
    
    def _execute_current_query(self):
        """Execute the current query"""
        query = self.current_query.strip()
        if not query:
            return
        
        try:
            # Parse query
            parsed = self.parser.parse(query)
            
            # Execute query
            result = self.executor.execute(parsed)
            
            # Display result
            self._display_result(result)
            
        except Exception as e:
            print(f"Error executing query: {e}")
            traceback.print_exc()
    
    def _display_result(self, result):
        """Display query result in readable format"""
        if 'rows' in result:
            rows = result['rows']
            if rows:
                # Get column names from first row
                columns = list(rows[0].keys())
                
                # Calculate column widths
                col_widths = []
                for col in columns:
                    max_len = max(len(str(row.get(col, ''))) for row in rows)
                    col_widths.append(max(max_len, len(col)))
                
                # Print header
                header = " | ".join(col.ljust(width) for col, width in zip(columns, col_widths))
                print(header)
                print("-" * len(header))
                
                # Print rows
                for row in rows:
                    row_str = " | ".join(str(row.get(col, '')).ljust(width) 
                                       for col, width in zip(columns, col_widths))
                    print(row_str)
                
                print(f"\n{result['count']} row(s) returned")
            else:
                print("No rows returned")
        
        elif 'tables' in result:
            tables = result['tables']
            if tables:
                print("Tables in database:")
                for table in tables:
                    print(f"  - {table}")
                print(f"\nTotal: {result['count']} table(s)")
            else:
                print("No tables in database")
        
        elif 'table' in result:
            table_info = result['table']
            print(f"\nTable: {table_info['name']}")
            print(f"Rows: {table_info['row_count']}")
            print("Columns:")
            for col in table_info['columns']:
                print(f"  {col}")
            if table_info['primary_key']:
                print(f"Primary Key: {table_info['primary_key']}")
            if table_info['unique_columns']:
                print(f"Unique Columns: {', '.join(table_info['unique_columns'])}")
        
        elif 'message' in result:
            print(result['message'])
        
        else:
            print(result)
    
    def _show_help(self):
        """Show help message"""
        help_text = """
        Available Commands:
        
        SQL Commands:
          CREATE TABLE <name> (col1 TYPE [PRIMARY KEY], col2 TYPE, ...)
          INSERT INTO <table> [(col1, col2, ...)] VALUES (val1, val2, ...)
          SELECT * FROM <table> [WHERE condition] [ORDER BY col]
          UPDATE <table> SET col=val [WHERE condition]
          DELETE FROM <table> [WHERE condition]
          DROP TABLE <name>
          SHOW TABLES
          DESCRIBE <table>
          CREATE INDEX ON <table> (column)
          DROP INDEX ON <table> (column)
        
        REPL Commands:
          exit           - Exit the REPL
          help           - Show this help message
          clear          - Clear the screen
          tables         - List all tables
        
        Data Types:
          INT, TEXT, BOOLEAN, FLOAT, TIMESTAMP, DATE
        
        Examples:
          CREATE TABLE users (id INT PRIMARY KEY, name TEXT, age INT)
          INSERT INTO users VALUES (1, 'Alice', 25)
          SELECT * FROM users WHERE age > 20
          UPDATE users SET age = 26 WHERE name = 'Alice'
          DELETE FROM users WHERE id = 1
        
        Multi-line queries:
          End query with semicolon (;)
          Example:
            CREATE TABLE tasks (
                id INT PRIMARY KEY,
                title TEXT,
                completed BOOLEAN DEFAULT FALSE
            );
        """
        print(help_text)
    
    def _list_tables(self):
        """List all tables in database"""
        tables = self.db.list_tables()
        if tables:
            print("Tables in database:")
            for table in tables:
                print(f"  - {table}")
        else:
            print("No tables in database")


def main():
    """Main entry point for REPL"""
    if len(sys.argv) > 1:
        db_name = sys.argv[1]
    else:
        db_name = "default"
    
    repl = REPL(db_name)
    repl.run()


if __name__ == "__main__":
    main()