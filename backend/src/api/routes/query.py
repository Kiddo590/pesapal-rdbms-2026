"""
Query execution API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time

from ...rdbms.core.database import Database
from ...rdbms.query.query_parser import QueryParser
from ...rdbms.query.executor import QueryExecutor

router = APIRouter()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


# Global instances (in production, use dependency injection)
parser = QueryParser()


@router.post("/execute", response_model=QueryResponse)
async def execute_query(request: QueryRequest):
    """Execute a SQL query"""
    try:
        start_time = time.time()
        
        # Parse query
        parsed_query = parser.parse(request.query)
        
        # Get database (for now, use default)
        # In production, this would come from session/request
        from ..main import default_db
        
        if default_db is None:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # Execute query
        executor = QueryExecutor(default_db)
        result = executor.execute(parsed_query)
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            success=True,
            result=result,
            execution_time=execution_time
        )
        
    except Exception as e:
        return QueryResponse(
            success=False,
            error=str(e)
        )


@router.post("/batch")
async def execute_batch_queries(queries: list[str]):
    """Execute multiple queries in batch"""
    results = []
    
    for query_str in queries:
        try:
            result = await execute_query(QueryRequest(query=query_str))
            results.append(result.dict())
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e)
            })
    
    return {"results": results}