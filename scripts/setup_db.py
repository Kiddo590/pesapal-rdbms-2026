#!/usr/bin/env python3
"""
Setup script for Pesapal RDBMS Challenge
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from src.rdbms.core.database import Database
from src.rdbms.core.table import ColumnDefinition
from src.rdbms.core.datatypes import DataType


def setup_demo_database():
    """Create demo database with sample data"""
    
    print("🚀 Setting up Pesapal RDBMS Demo Database...")
    print("=" * 60)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Initialize database
    db = Database("pesapal_demo")
    
    print("📊 Creating tables...")
    
    # 1. Create users table
    users_columns = [
        ColumnDefinition("id", DataType.INTEGER, is_primary=True),
        ColumnDefinition("username", DataType.TEXT, is_unique=True, nullable=False),
        ColumnDefinition("email", DataType.TEXT, nullable=False),
        ColumnDefinition("full_name", DataType.TEXT),
        ColumnDefinition("age", DataType.INTEGER),
        ColumnDefinition("created_at", DataType.TIMESTAMP),
    ]
    
    users_table = db.create_table("users", users_columns)
    print("✅ Created 'users' table")
    
    # 2. Create tasks table
    tasks_columns = [
        ColumnDefinition("id", DataType.INTEGER, is_primary=True),
        ColumnDefinition("title", DataType.TEXT, nullable=False),
        ColumnDefinition("description", DataType.TEXT),
        ColumnDefinition("priority", DataType.TEXT),
        ColumnDefinition("status", DataType.TEXT),
        ColumnDefinition("user_id", DataType.INTEGER),
        ColumnDefinition("due_date", DataType.TIMESTAMP),
        ColumnDefinition("created_at", DataType.TIMESTAMP),
    ]
    
    tasks_table = db.create_table("tasks", tasks_columns)
    print("✅ Created 'tasks' table")
    
    # 3. Create departments table
    dept_columns = [
        ColumnDefinition("id", DataType.INTEGER, is_primary=True),
        ColumnDefinition("name", DataType.TEXT, nullable=False),
        ColumnDefinition("location", DataType.TEXT),
    ]
    
    dept_table = db.create_table("departments", dept_columns)
    print("✅ Created 'departments' table")
    
    print("\n📝 Inserting sample data...")
    
    # Insert sample users
    sample_users = [
        {
            "username": "alice",
            "email": "alice@example.com",
            "full_name": "Alice Smith",
            "age": 28,
            "created_at": "2023-01-15T09:30:00"
        },
        {
            "username": "bob",
            "email": "bob@example.com",
            "full_name": "Bob Johnson",
            "age": 32,
            "created_at": "2023-02-20T14:45:00"
        },
        {
            "username": "charlie",
            "email": "charlie@example.com",
            "full_name": "Charlie Brown",
            "age": 24,
            "created_at": "2023-03-10T11:15:00"
        }
    ]
    
    for i, user in enumerate(sample_users, 1):
        user["id"] = i
        db.insert("users", user)
    print("✅ Inserted 3 users")
    
    # Insert sample tasks
    sample_tasks = [
        {
            "title": "Design database schema",
            "description": "Create initial schema for the RDBMS",
            "priority": "high",
            "status": "completed",
            "user_id": 1,
            "due_date": "2024-01-20T23:59:59",
            "created_at": "2024-01-10T09:00:00"
        },
        {
            "title": "Implement CRUD operations",
            "description": "Add create, read, update, delete functionality",
            "priority": "high",
            "status": "in_progress",
            "user_id": 2,
            "due_date": "2024-01-25T23:59:59",
            "created_at": "2024-01-12T14:30:00"
        },
        {
            "title": "Write unit tests",
            "description": "Create comprehensive test suite",
            "priority": "medium",
            "status": "pending",
            "user_id": 1,
            "due_date": "2024-02-05T23:59:59",
            "created_at": "2024-01-15T10:15:00"
        },
        {
            "title": "Create documentation",
            "description": "Write user and API documentation",
            "priority": "medium",
            "status": "pending",
            "user_id": 3,
            "due_date": "2024-02-10T23:59:59",
            "created_at": "2024-01-18T16:45:00"
        },
        {
            "title": "Performance optimization",
            "description": "Optimize query execution and indexing",
            "priority": "low",
            "status": "pending",
            "user_id": 2,
            "due_date": "2024-02-15T23:59:59",
            "created_at": "2024-01-20T11:30:00"
        }
    ]
    
    for i, task in enumerate(sample_tasks, 1):
        task["id"] = i
        db.insert("tasks", task)
    print("✅ Inserted 5 tasks")
    
    # Insert sample departments
    sample_depts = [
        {"id": 1, "name": "Engineering", "location": "Building A"},
        {"id": 2, "name": "Marketing", "location": "Building B"},
        {"id": 3, "name": "Sales", "location": "Building C"},
    ]
    
    for dept in sample_depts:
        db.insert("departments", dept)
    print("✅ Inserted 3 departments")
    
    # Create indexes
    db.create_index("tasks", "priority")
    db.create_index("tasks", "status")
    db.create_index("users", "username")
    print("✅ Created indexes on priority, status, and username")
    
    print("\n" + "=" * 60)
    print("🎉 Demo database setup complete!")
    print("\n📋 Database Summary:")
    print(f"   • Database: {db.name}")
    print(f"   • Tables: {', '.join(db.list_tables())}")
    print(f"   • Total rows: {sum(db.tables[table].row_count for table in db.list_tables())}")
    print("\n🚀 You can now:")
    print("   1. Start the backend server: uvicorn src.api.main:app --reload")
    print("   2. Start the frontend: cd frontend && npm run dev")
    print("   3. Use the REPL: python -m src.rdbms.repl.interactive")
    print("\n💡 Try these queries in the REPL:")
    print("   • SELECT * FROM users;")
    print("   • SELECT * FROM tasks WHERE priority = 'high';")
    print("   • SELECT username, title FROM users JOIN tasks ON users.id = tasks.user_id;")


if __name__ == "__main__":
    setup_demo_database()