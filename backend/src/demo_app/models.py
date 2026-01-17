"""
Demo application models for task management
"""

from datetime import datetime
from typing import Optional
from enum import Enum


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task:
    """Task model for demo application"""
    
    def __init__(self, 
                 title: str,
                 description: str = "",
                 priority: TaskPriority = TaskPriority.MEDIUM,
                 status: TaskStatus = TaskStatus.PENDING,
                 due_date: Optional[datetime] = None,
                 created_at: Optional[datetime] = None,
                 id: Optional[int] = None):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.due_date = due_date
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create task from dictionary"""
        return cls(
            id=data.get('id'),
            title=data['title'],
            description=data.get('description', ''),
            priority=TaskPriority(data.get('priority', 'medium')),
            status=TaskStatus(data.get('status', 'pending')),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )


class User:
    """User model for demo application"""
    
    def __init__(self,
                 username: str,
                 email: str,
                 full_name: str = "",
                 id: Optional[int] = None,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> dict:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Create user from dictionary"""
        return cls(
            id=data.get('id'),
            username=data['username'],
            email=data['email'],
            full_name=data.get('full_name', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )