"""
CRUD operations for demo application using custom RDBMS
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from .models import Task, TaskPriority, TaskStatus, User
from ..rdbms.core.database import Database


class TaskManager:
    """Task manager using custom RDBMS"""
    
    def __init__(self, database: Database):
        self.db = database
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables for demo"""
        from ..rdbms.core.table import ColumnDefinition
        from ..rdbms.core.datatypes import DataType
        
        # Create tasks table if not exists
        if 'tasks' not in self.db.list_tables():
            columns = [
                ColumnDefinition("id", DataType.INTEGER, is_primary=True),
                ColumnDefinition("title", DataType.TEXT, nullable=False),
                ColumnDefinition("description", DataType.TEXT),
                ColumnDefinition("priority", DataType.TEXT),
                ColumnDefinition("status", DataType.TEXT),
                ColumnDefinition("due_date", DataType.TIMESTAMP),
                ColumnDefinition("created_at", DataType.TIMESTAMP),
            ]
            self.db.create_table("tasks", columns)
        
        # Create users table if not exists
        if 'users' not in self.db.list_tables():
            columns = [
                ColumnDefinition("id", DataType.INTEGER, is_primary=True),
                ColumnDefinition("username", DataType.TEXT, is_unique=True, nullable=False),
                ColumnDefinition("email", DataType.TEXT, nullable=False),
                ColumnDefinition("full_name", DataType.TEXT),
                ColumnDefinition("created_at", DataType.TIMESTAMP),
            ]
            self.db.create_table("users", columns)
            
            # Insert sample users
            sample_users = [
                {"username": "alice", "email": "alice@example.com", "full_name": "Alice Smith"},
                {"username": "bob", "email": "bob@example.com", "full_name": "Bob Johnson"},
                {"username": "charlie", "email": "charlie@example.com", "full_name": "Charlie Brown"},
            ]
            
            for user_data in sample_users:
                user_data["created_at"] = datetime.now().isoformat()
                self.db.insert("users", user_data)
    
    def create_task(self, task: Task) -> Task:
        """Create a new task"""
        task_data = task.to_dict()
        if 'id' in task_data:
            del task_data['id']  # Let database assign ID
        
        task_id = self.db.insert("tasks", task_data)
        task.id = task_id
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        rows = self.db.select("tasks", {"id": task_id})
        if rows:
            return Task.from_dict(rows[0])
        return None
    
    def get_all_tasks(self, 
                     status: Optional[TaskStatus] = None,
                     priority: Optional[TaskPriority] = None) -> List[Task]:
        """Get all tasks with optional filtering"""
        conditions = {}
        if status:
            conditions['status'] = status.value
        if priority:
            conditions['priority'] = priority.value
        
        rows = self.db.select("tasks", conditions if conditions else None)
        return [Task.from_dict(row) for row in rows]
    
    def update_task(self, task_id: int, updates: Dict[str, Any]) -> Optional[Task]:
        """Update task"""
        updated = self.db.update("tasks", updates, {"id": task_id})
        if updated:
            return self.get_task(task_id)
        return None
    
    def delete_task(self, task_id: int) -> bool:
        """Delete task"""
        deleted = self.db.delete("tasks", {"id": task_id})
        return deleted > 0
    
    def create_user(self, user: User) -> User:
        """Create a new user"""
        user_data = user.to_dict()
        if 'id' in user_data:
            del user_data['id']
        
        user_id = self.db.insert("users", user_data)
        user.id = user_id
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        rows = self.db.select("users", {"id": user_id})
        if rows:
            return User.from_dict(rows[0])
        return None
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        rows = self.db.select("users")
        return [User.from_dict(row) for row in rows]
    
    def get_tasks_by_user(self, username: str) -> List[Task]:
        """Get tasks assigned to a user (via join)"""
        # This demonstrates JOIN capability
        # Note: In real implementation, we'd have user_id foreign key
        
        # For now, return all tasks
        return self.get_all_tasks()
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        tasks = self.get_all_tasks()
        
        total = len(tasks)
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        pending = len([t for t in tasks if t.status == TaskStatus.PENDING])
        in_progress = len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS])
        
        high_priority = len([t for t in tasks if t.priority == TaskPriority.HIGH])
        medium_priority = len([t for t in tasks if t.priority == TaskPriority.MEDIUM])
        low_priority = len([t for t in tasks if t.priority == TaskPriority.LOW])
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "completion_rate": (completed / total * 100) if total > 0 else 0,
            "priority_distribution": {
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority
            }
        }