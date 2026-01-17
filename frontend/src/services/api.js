import axios from 'axios'

const API_BASE = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // Health check
  async getHealth() {
    const response = await api.get('/health')
    return response.data
  },
  
  // ===== TABLE OPERATIONS =====
  
  // List all tables
  async listTables() {
    const response = await api.get('/api/tables')
    return response.data
  },
  
  // Create a new table
  async createTable(tableName, columns) {
    const response = await api.post('/api/tables', {
      name: tableName,
      columns: columns
    })
    return response.data
  },
  
  // Delete a table
  async deleteTable(tableName) {
    const response = await api.delete(`/api/tables/${tableName}`)
    return response.data
  },
  
  // ===== ROW OPERATIONS =====
  
  // Get rows from a table
  async getTableRows(tableName, limit = 100, offset = 0, where = null) {
    const params = { limit, offset }
    if (where) {
      params.where = JSON.stringify(where)
    }
    const response = await api.get(`/api/tables/${tableName}`, { params })
    return response.data
  },
  
  // Insert a row
  async insertRow(tableName, data) {
    const response = await api.post(`/api/tables/${tableName}/rows`, { data })
    return response.data
  },
  
  // Update rows
  async updateRows(tableName, data, where = null) {
    const response = await api.put(`/api/tables/${tableName}/rows`, { data, where })
    return response.data
  },
  
  // Delete rows
  async deleteRows(tableName, where = null) {
    const params = {}
    if (where) {
      params.where = JSON.stringify(where)
    }
    const response = await api.delete(`/api/tables/${tableName}/rows`, { params })
    return response.data
  },
  
  // ===== SQL QUERIES =====
  
  // Execute SQL query
  async executeQuery(sql) {
    const response = await api.get('/api/query', { params: { sql } })
    return response.data
  },
  
  // Execute SQL query via POST
  async executeQueryPost(sql) {
    const response = await api.post('/api/query', { sql })
    return response.data
  },
  
  // ===== DEMO APP SPECIFIC =====
  
  // Get all tasks
  async getTasks() {
    return this.getTableRows('tasks')
  },
  
  // Create a task
  async createTask(taskData) {
    return this.insertRow('tasks', taskData)
  },
  
  // Update a task
  async updateTask(taskId, updates) {
    return this.updateRows('tasks', updates, { id: taskId })
  },
  
  // Delete a task
  async deleteTask(taskId) {
    return this.deleteRows('tasks', { id: taskId })
  },
  
  // Get all users
  async getUsers() {
    return this.getTableRows('users')
  },
  
  // Create a user
  async createUser(userData) {
    return this.insertRow('users', userData)
  }
}