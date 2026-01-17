"""
Table management API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from ...rdbms.core.database import Database

router = APIRouter()


class CreateTableRequest(BaseModel):
    name: str
    columns: List[Dict[str, Any]]


class InsertRowRequest(BaseModel):
    data: Dict[str, Any]


class UpdateRowRequest(BaseModel):
    data: Dict[str, Any]
    where: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_tables():
    """List all tables in database"""
    from ..main import default_db
    
    if default_db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    tables = default_db.list_tables()
    return {"tables": tables, "count": len(tables)}


@router.post("/")
async def create_table(request: CreateTableRequest):
    """Create a new table"""
    from ..main import default_db
    
    if default_db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        # Convert column definitions
        from ...rdbms.core.table import ColumnDefinition
        from ...rdbms.core.datatypes import DataType
        
        columns = []
        for col_def in request.columns:
            column = ColumnDefinition(
                name=col_def['name'],
                data_type=DataType(col_def['type']),
                is_primary=col_def.get('is_primary', False),
                is_unique=col_def.get('is_unique', False),
                default_value=col_def.get('default'),
                nullable=col_def.get('nullable', True)
            )
            columns.append(column)
        
        table = default_db.create_table(request.name, columns)
        return {"message": f"Table '{request.name}' created", "table": table.describe()}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{table_name}")
async def get_table(table_name: str, limit: int = 100, offset: int = 0):
    """Get table data"""
    from ..main import default_db
    
    if default_db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        # Get table info
        table_info = default_db.get_table_info(table_name)
        if not table_info:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get rows (simplified - no pagination in core yet)
        rows = default_db.select(table_name)
        
        # Apply simple pagination
        paginated_rows = rows[offset:offset + limit]
        
        return {
            "table": table_info,
            "rows": paginated_rows,
            "total_rows": len(rows),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{table_name}/rows")
async def insert_row(table_name: str, request: InsertRowRequest):
    """Insert a row into table"""
    from ..main import default_db
    
    if default_db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        row_id = default_db.insert(table_name, request.data)
        return {"message": "Row inserted", "row_id": row_id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{table_name}/rows")
async def update_rows(table_name: str, request: UpdateRowRequest):
    """Update rows in table"""
    from ..main import default_db
    
    if default_db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        updated = default_db.update(table_name, request.data, request.where)
        return {"message": f"{updated} row(s) updated"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{table_name}/rows")
async def delete_rows(table_name: str, where: Optional[Dict[str, Any]] = None):
    """Delete rows from table"""
    from ..main import default_db
    
    if default_db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    try:
        deleted = default_db.delete(table_name, where)
        return {"message": f"{deleted} row(s) deleted"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{table_name}/schema")
async def get_table_schema(table_name: str):
    """Get table schema"""
    from ..main import default_db
    
    if default_db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    
    table_info = default_db.get_table_info(table_name)
    if not table_info:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    return {"schema": table_info}