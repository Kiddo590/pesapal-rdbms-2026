"""
Enhanced RDBMS Backend with Full CRUD Support
"""
import uvicorn
import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional, Union
import json
from enum import Enum
from datetime import datetime

# ========== ENHANCED RDBMS CORE ==========

class DataType(Enum):
    INT = "INT"
    TEXT = "TEXT"
    BOOLEAN = "BOOLEAN"
    FLOAT = "FLOAT"
    TIMESTAMP = "TIMESTAMP"

class Column:
    def __init__(self, name: str, type: Union[DataType, str], primary=False, unique=False, nullable=True, default=None):
        self.name = name
        # Ensure type is always a DataType enum
        if isinstance(type, str):
            try:
                self.type = DataType(type.upper())
            except ValueError:
                # Default to TEXT if invalid type
                self.type = DataType.TEXT
        else:
            self.type = type
        self.primary = primary
        self.unique = unique
        self.nullable = nullable
        self.default = default

class Table:
    def __init__(self, name: str, columns: List[Dict]):
        self.name = name
        # Convert column definitions to Column objects
        self.columns = []
        for col_def in columns:
            # Handle both string and DataType enum for type
            col_type = col_def.get('type')
            if isinstance(col_type, DataType):
                col_def['type'] = col_type
            elif isinstance(col_type, str):
                try:
                    col_def['type'] = DataType(col_type.upper())
                except:
                    col_def['type'] = DataType.TEXT
            self.columns.append(Column(**col_def))
        self.rows = []
        self.next_id = 1
        self._load_data()
    
    def _load_data(self):
        """Load table data from file"""
        filename = f"data/{self.name}.json"
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    data = json.load(f)
                    self.rows = data.get('rows', [])
                    self.next_id = data.get('next_id', 1)
                    # Note: We don't reload columns from file to maintain consistency
            except:
                self.rows = []
                self.next_id = 1
    
    def _save_data(self):
        """Save table data to file"""
        os.makedirs("data", exist_ok=True)
        filename = f"data/{self.name}.json"
        with open(filename, 'w') as f:
            json.dump({
                'rows': self.rows,
                'next_id': self.next_id,
                'columns': [{'name': col.name, 'type': col.type.value, 'primary': col.primary} 
                           for col in self.columns]
            }, f, indent=2)
    
    def insert(self, data: Dict) -> Dict:
        """Insert a new row with validation"""
        # Validate data against columns
        row_data = {}
        
        for col in self.columns:
            if col.name in data:
                value = data[col.name]
                # Type validation
                if col.type == DataType.INT and value is not None:
                    try:
                        value = int(value)
                    except:
                        raise ValueError(f"Column '{col.name}' must be integer")
                elif col.type == DataType.FLOAT and value is not None:
                    try:
                        value = float(value)
                    except:
                        raise ValueError(f"Column '{col.name}' must be float")
                elif col.type == DataType.BOOLEAN and value is not None:
                    if isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes', 't')
                    value = bool(value)
                
                row_data[col.name] = value
            elif col.primary and col.name == 'id':
                # Auto-increment primary key
                row_data['id'] = self.next_id
                self.next_id += 1
            elif col.default is not None:
                row_data[col.name] = col.default
            elif not col.nullable:
                raise ValueError(f"Column '{col.name}' cannot be null")
            else:
                row_data[col.name] = None
        
        # Check unique constraints
        for col in self.columns:
            if col.unique and col.name in row_data and row_data[col.name] is not None:
                for row in self.rows:
                    if row.get(col.name) == row_data[col.name]:
                        raise ValueError(f"Duplicate value for unique column '{col.name}'")
        
        self.rows.append(row_data)
        self._save_data()
        return row_data
    
    def select(self, where: Optional[Dict] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Select rows with filtering"""
        results = []
        
        for row in self.rows:
            if not where or all(row.get(k) == v for k, v in where.items()):
                results.append(row.copy())
        
        return results[offset:offset + limit]
    
    def update(self, data: Dict, where: Optional[Dict] = None) -> int:
        """Update rows"""
        count = 0
        
        for row in self.rows:
            if not where or all(row.get(k) == v for k, v in where.items()):
                # Validate updates
                for col in self.columns:
                    if col.name in data:
                        value = data[col.name]
                        if col.type == DataType.INT and value is not None:
                            value = int(value)
                        elif col.type == DataType.FLOAT and value is not None:
                            value = float(value)
                        elif col.type == DataType.BOOLEAN and value is not None:
                            value = bool(value)
                        
                        # Check unique constraint
                        if col.unique and value is not None:
                            for other_row in self.rows:
                                if other_row is not row and other_row.get(col.name) == value:
                                    raise ValueError(f"Duplicate value for unique column '{col.name}'")
                        
                        row[col.name] = value
                count += 1
        
        if count > 0:
            self._save_data()
        
        return count
    
    def delete(self, where: Optional[Dict] = None) -> int:
        """Delete rows"""
        to_delete = []
        
        for i, row in enumerate(self.rows):
            if not where or all(row.get(k) == v for k, v in where.items()):
                to_delete.append(i)
        
        for i in reversed(to_delete):
            del self.rows[i]
        
        if to_delete:
            self._save_data()
        
        return len(to_delete)

# ========== CREATE APP ==========

app = FastAPI(
    title="Pesapal RDBMS API",
    description="Full CRUD RDBMS with SQL-like interface",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db = {}

def initialize_database():
    """Initialize database with sample tables"""
    global db
    
    # Create users table
    db["users"] = Table("users", [
        {"name": "id", "type": DataType.INT, "primary": True},
        {"name": "name", "type": DataType.TEXT},
        {"name": "email", "type": DataType.TEXT, "unique": True},
        {"name": "age", "type": DataType.INT, "nullable": True},
        {"name": "created_at", "type": DataType.TIMESTAMP, "default": datetime.now().isoformat()}
    ])
    
    # Create tasks table
    db["tasks"] = Table("tasks", [
        {"name": "id", "type": DataType.INT, "primary": True},
        {"name": "title", "type": DataType.TEXT},
        {"name": "description", "type": DataType.TEXT, "nullable": True},
        {"name": "completed", "type": DataType.BOOLEAN, "default": False},
        {"name": "priority", "type": DataType.TEXT, "default": "medium"},
        {"name": "created_at", "type": DataType.TIMESTAMP, "default": datetime.now().isoformat()}
    ])
    
    # Add sample data if tables are empty
    if len(db["users"].rows) == 0:
        db["users"].insert({"name": "Alice Johnson", "email": "alice@example.com", "age": 28})
        db["users"].insert({"name": "Bob Smith", "email": "bob@example.com", "age": 32})
        db["users"].insert({"name": "Charlie Brown", "email": "charlie@example.com", "age": 24})
    
    if len(db["tasks"].rows) == 0:
        db["tasks"].insert({"title": "Design RDBMS", "description": "Create database schema", "completed": True, "priority": "high"})
        db["tasks"].insert({"title": "Build API", "description": "Create REST endpoints", "completed": False, "priority": "high"})
        db["tasks"].insert({"title": "Write Tests", "description": "Create unit tests", "completed": False, "priority": "medium"})
        db["tasks"].insert({"title": "Documentation", "description": "Write user guide", "completed": False, "priority": "low"})

# ========== PYDANTIC MODELS ==========

class CreateTableRequest(BaseModel):
    name: str
    columns: List[Dict]

class InsertRowRequest(BaseModel):
    data: Dict

class UpdateRowRequest(BaseModel):
    data: Dict
    where: Optional[Dict] = None

class QueryRequest(BaseModel):
    sql: str

# ========== HELPER FUNCTIONS ==========

def get_column_type_str(col_type):
    """Safely get column type as string"""
    if hasattr(col_type, 'value'):
        return col_type.value
    else:
        return str(col_type)

# ========== API ENDPOINTS ==========

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    initialize_database()
    print("✅ Database initialized with tables:", list(db.keys()))

@app.get("/")
def root():
    return {
        "message": "Pesapal RDBMS API v2.0",
        "version": "2.0.0",
        "status": "running",
        "features": ["Full CRUD", "SQL-like queries", "Data persistence", "Table management"],
        "tables": list(db.keys()),
        "endpoints": {
            "/": "This info",
            "/health": "Health check",
            "/api/tables": "List/Create tables",
            "/api/tables/{name}": "Table operations",
            "/api/query": "Execute SQL",
            "/docs": "API documentation"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "tables": len(db),
        "total_rows": sum(len(table.rows) for table in db.values())
    }

# ========== TABLE MANAGEMENT ==========

@app.get("/api/tables")
def list_tables():
    """List all tables"""
    tables_info = []
    for name, table in db.items():
        tables_info.append({
            "name": name,
            "columns": [{"name": col.name, "type": get_column_type_str(col.type), "primary": col.primary}
                       for col in table.columns],
            "row_count": len(table.rows)
        })
    
    return {
        "success": True,
        "tables": tables_info,
        "count": len(db)
    }

@app.post("/api/tables")
def create_table(request: CreateTableRequest):
    """Create a new table"""
    if request.name in db:
        raise HTTPException(400, detail=f"Table '{request.name}' already exists")
    
    # Validate columns
    for col in request.columns:
        if 'name' not in col or 'type' not in col:
            raise HTTPException(400, detail="Column must have 'name' and 'type'")
        
        # Convert string type to DataType enum
        col_type = col['type']
        if isinstance(col_type, str):
            try:
                col['type'] = DataType(col_type.upper())
            except:
                raise HTTPException(400, detail=f"Invalid data type: {col_type}")
    
    # Create table
    db[request.name] = Table(request.name, request.columns)
    
    return {
        "success": True,
        "message": f"Table '{request.name}' created successfully",
        "table": request.name,
        "columns": [{"name": col['name'], "type": get_column_type_str(col['type']), "primary": col.get('primary', False)}
                   for col in request.columns]
    }

@app.delete("/api/tables/{table_name}")
def delete_table(table_name: str):
    """Delete a table"""
    if table_name not in db:
        raise HTTPException(404, detail=f"Table '{table_name}' not found")
    
    # Remove from database
    del db[table_name]
    
    # Remove data file
    filename = f"data/{table_name}.json"
    if os.path.exists(filename):
        os.remove(filename)
    
    return {
        "success": True,
        "message": f"Table '{table_name}' deleted successfully"
    }

# ========== ROW OPERATIONS ==========

@app.get("/api/tables/{table_name}")
def get_table_rows(table_name: str, limit: int = 100, offset: int = 0, where: Optional[str] = None):
    """Get rows from a table"""
    if table_name not in db:
        raise HTTPException(404, detail=f"Table '{table_name}' not found")
    
    table = db[table_name]
    
    # Parse where clause
    where_dict = None
    if where:
        try:
            where_dict = json.loads(where)
        except:
            raise HTTPException(400, detail="Invalid WHERE clause format")
    
    rows = table.select(where_dict, limit, offset)
    
    return {
        "success": True,
        "table": table_name,
        "columns": [{"name": col.name, "type": get_column_type_str(col.type), "primary": col.primary}
                   for col in table.columns],
        "rows": rows,
        "count": len(rows),
        "total": len(table.rows)
    }

@app.post("/api/tables/{table_name}/rows")
def insert_table_row(table_name: str, request: InsertRowRequest):
    """Insert a row into table"""
    if table_name not in db:
        raise HTTPException(404, detail=f"Table '{table_name}' not found")
    
    try:
        row = db[table_name].insert(request.data)
        return {
            "success": True,
            "message": "Row inserted successfully",
            "row": row,
            "row_id": row.get('id')
        }
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.put("/api/tables/{table_name}/rows")
def update_table_rows(table_name: str, request: UpdateRowRequest):
    """Update rows in table"""
    if table_name not in db:
        raise HTTPException(404, detail=f"Table '{table_name}' not found")
    
    try:
        updated = db[table_name].update(request.data, request.where)
        return {
            "success": True,
            "message": f"{updated} row(s) updated successfully",
            "updated_count": updated
        }
    except Exception as e:
        raise HTTPException(400, detail=str(e))

@app.delete("/api/tables/{table_name}/rows")
def delete_table_rows(table_name: str, where: Optional[str] = None):
    """Delete rows from table"""
    if table_name not in db:
        raise HTTPException(404, detail=f"Table '{table_name}' not found")
    
    # Parse where clause
    where_dict = None
    if where:
        try:
            where_dict = json.loads(where)
        except:
            raise HTTPException(400, detail="Invalid WHERE clause format")
    
    deleted = db[table_name].delete(where_dict)
    
    return {
        "success": True,
        "message": f"{deleted} row(s) deleted successfully",
        "deleted_count": deleted
    }

# ========== SQL QUERY INTERFACE ==========

@app.get("/api/query")
def execute_sql_query(sql: str):
    """Execute SQL-like query"""
    sql = sql.strip().upper()
    
    try:
        # SELECT * FROM table
        if sql.startswith("SELECT * FROM"):
            table_part = sql[13:].strip()
            
            if " WHERE " in table_part:
                table_name, condition = table_part.split(" WHERE ", 1)
                table_name = table_name.strip().rstrip(";")
                condition = condition.strip().rstrip(";")
                
                # Simple equality condition
                if "=" in condition:
                    col, val = condition.split("=", 1)
                    col = col.strip()
                    val = val.strip().strip("'\"")
                    
                    if table_name in db:
                        rows = db[table_name].select({col: val})
                        return {
                            "success": True,
                            "query": sql,
                            "rows": rows,
                            "count": len(rows)
                        }
            else:
                table_name = table_part.strip().rstrip(";")
                if table_name in db:
                    rows = db[table_name].select()
                    return {
                        "success": True,
                        "query": sql,
                        "rows": rows,
                        "count": len(rows)
                    }
        
        # INSERT INTO table (col1, col2) VALUES (val1, val2)
        elif sql.startswith("INSERT INTO"):
            import re
            pattern = r"INSERT INTO (\w+) \((.*?)\) VALUES \((.*?)\)"
            match = re.search(pattern, sql, re.IGNORECASE)
            
            if match:
                table_name = match.group(1)
                columns = [c.strip() for c in match.group(2).split(",")]
                values = [v.strip().strip("'\"") for v in match.group(3).split(",")]
                
                if table_name in db and len(columns) == len(values):
                    data = dict(zip(columns, values))
                    row = db[table_name].insert(data)
                    return {
                        "success": True,
                        "message": "Row inserted",
                        "row": row,
                        "row_id": row.get('id')
                    }
        
        # UPDATE table SET col=val WHERE condition
        elif sql.startswith("UPDATE"):
            import re
            pattern = r"UPDATE (\w+) SET (.*?)(?: WHERE (.*))?$"
            match = re.search(pattern, sql, re.IGNORECASE)
            
            if match:
                table_name = match.group(1)
                set_clause = match.group(2).strip().rstrip(";")
                where_clause = match.group(3)
                
                # Parse SET clause
                updates = {}
                for pair in set_clause.split(","):
                    if "=" in pair:
                        col, val = pair.split("=", 1)
                        col = col.strip()
                        val = val.strip().strip("'\"")
                        updates[col] = val
                
                # Parse WHERE clause
                where_dict = None
                if where_clause:
                    where_clause = where_clause.strip().rstrip(";")
                    if "=" in where_clause:
                        col, val = where_clause.split("=", 1)
                        col = col.strip()
                        val = val.strip().strip("'\"")
                        where_dict = {col: val}
                
                if table_name in db:
                    updated = db[table_name].update(updates, where_dict)
                    return {
                        "success": True,
                        "message": f"{updated} row(s) updated",
                        "updated_count": updated
                    }
        
        # DELETE FROM table WHERE condition
        elif sql.startswith("DELETE FROM"):
            import re
            pattern = r"DELETE FROM (\w+)(?: WHERE (.*))?$"
            match = re.search(pattern, sql, re.IGNORECASE)
            
            if match:
                table_name = match.group(1)
                where_clause = match.group(2)
                
                # Parse WHERE clause
                where_dict = None
                if where_clause:
                    where_clause = where_clause.strip().rstrip(";")
                    if "=" in where_clause:
                        col, val = where_clause.split("=", 1)
                        col = col.strip()
                        val = val.strip().strip("'\"")
                        where_dict = {col: val}
                
                if table_name in db:
                    deleted = db[table_name].delete(where_dict)
                    return {
                        "success": True,
                        "message": f"{deleted} row(s) deleted",
                        "deleted_count": deleted
                    }
        
        # CREATE TABLE
        elif sql.startswith("CREATE TABLE"):
            import re
            pattern = r"CREATE TABLE (\w+) \((.*)\)"
            match = re.search(pattern, sql, re.IGNORECASE | re.DOTALL)
            
            if match:
                table_name = match.group(1)
                columns_str = match.group(2)
                
                if table_name in db:
                    return {
                        "success": False,
                        "error": f"Table '{table_name}' already exists"
                    }
                
                # Parse columns
                columns = []
                for col_def in columns_str.split(","):
                    col_def = col_def.strip()
                    if not col_def:
                        continue
                    
                    parts = col_def.split()
                    if len(parts) >= 2:
                        col_name = parts[0]
                        col_type_str = parts[1].upper()
                        
                        # Convert to DataType enum
                        try:
                            col_type = DataType(col_type_str)
                        except:
                            col_type = DataType.TEXT
                        
                        column = {
                            "name": col_name,
                            "type": col_type,  # Store as DataType enum
                            "primary": "PRIMARY" in col_def.upper() and "KEY" in col_def.upper(),
                            "unique": "UNIQUE" in col_def.upper(),
                            "nullable": "NOT NULL" not in col_def.upper()
                        }
                        columns.append(column)
                
                # Create table
                db[table_name] = Table(table_name, columns)
                return {
                    "success": True,
                    "message": f"Table '{table_name}' created",
                    "table": table_name,
                    "columns": [{"name": c["name"], "type": get_column_type_str(c["type"]), "primary": c["primary"]} 
                               for c in columns]
                }
        
        return {
            "success": False,
            "error": "Query syntax not supported",
            "supported": [
                "SELECT * FROM table",
                "SELECT * FROM table WHERE column=value",
                "INSERT INTO table (col1, col2) VALUES (val1, val2)",
                "UPDATE table SET col=val WHERE condition",
                "DELETE FROM table WHERE condition",
                "CREATE TABLE name (col1 TYPE, col2 TYPE)"
            ]
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/query")
def execute_sql_query_post(request: QueryRequest):
    """Execute SQL query via POST"""
    return execute_sql_query(request.sql)

# ========== TEST ENDPOINT ==========

@app.get("/api/test-comprehensive")
def run_comprehensive_tests():
    """Run comprehensive test suite"""
    try:
        import subprocess
        import sys
        
        # Run the test script
        result = subprocess.run(
            [sys.executable, "test_rdbms.py"],
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
            "return_code": result.returncode
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# ========== MAIN ==========

if __name__ == "__main__":
    print("🚀 PESAPAL RDBMS v2.0 - FULL CRUD")
    print("=" * 60)
    print("🌐 API Server: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("💾 Data Directory: data/")
    print("💡 Features: Create/Delete tables, Full CRUD, SQL queries")
    print("=" * 60)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)