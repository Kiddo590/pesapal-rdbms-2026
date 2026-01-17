<template>
  <div class="test-dashboard">
    <h1>🧪 RDBMS Test Dashboard</h1>
    
    <div class="test-sections">
      <!-- Section 1: Database Info -->
      <section class="test-section">
        <h2>📊 Database Information</h2>
        <button @click="getTables" :disabled="loading">List All Tables</button>
        <div v-if="tables" class="results">
          <h3>Tables in Database:</h3>
          <ul>
            <li v-for="table in tables" :key="table.name">
              <strong>{{ table.name }}</strong> - {{ table.row_count }} rows
              <button @click="getTableSchema(table.name)" class="small-btn">View Schema</button>
              <button @click="setActiveTable(table.name)" class="small-btn">Select</button>
            </li>
          </ul>
        </div>
      </section>

      <!-- Section 2: CRUD Operations -->
      <section class="test-section">
        <h2>🔄 CRUD Operations</h2>
        
        <div class="current-table">
          <h3>Current Table: <span class="table-name">{{ activeTable || 'None selected' }}</span></h3>
          <div v-if="activeTable">
            <button @click="getTableData" class="small-btn">Refresh Data</button>
          </div>
        </div>
        
        <div class="crud-controls">
          <div class="form-group">
            <label>Table Name:</label>
            <input v-model="crudTable" placeholder="e.g., users" />
          </div>
          
          <div class="button-group">
            <button @click="createTestTable">Create Test Table</button>
            <button @click="insertTestData">Insert Test Data</button>
            <button @click="readTableData">Read Data</button>
            <button @click="showUpdateForm = true">Update Data</button>
            <button @click="deleteTestData">Delete Data</button>
          </div>
        </div>

        <!-- Update Data Form -->
        <div v-if="showUpdateForm" class="update-form">
          <h3>📝 Update Data</h3>
          <div class="form-group">
            <label>Row ID to Update:</label>
            <input v-model="updateRowId" type="number" placeholder="Enter row ID" />
          </div>
          
          <div class="form-group">
            <label>New Name:</label>
            <input v-model="updateData.name" placeholder="New name" />
          </div>
          
          <div class="form-group">
            <label>New Email:</label>
            <input v-model="updateData.email" placeholder="New email" />
          </div>
          
          <div class="form-group">
            <label>New Age:</label>
            <input v-model="updateData.age" type="number" placeholder="New age" />
          </div>
          
          <div class="button-group">
            <button @click="updateRowData" :disabled="!updateRowId">Update Row</button>
            <button @click="updateMultipleRows" class="secondary">Update Multiple Rows</button>
            <button @click="showUpdateForm = false" class="cancel">Cancel</button>
          </div>
        </div>
        
        <!-- Table Data Display -->
        <div v-if="tableData" class="results">
          <h3>Table Data: {{ activeTable }}</h3>
          <div class="table-container">
            <table v-if="tableData.rows && tableData.rows.length > 0">
              <thead>
                <tr>
                  <th v-for="col in tableData.columns" :key="col.name">{{ col.name }}</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in tableData.rows" :key="row.id">
                  <td v-for="col in tableData.columns" :key="col.name">
                    {{ row[col.name] }}
                  </td>
                  <td class="actions">
                    <button @click="editRow(row)" class="edit-btn">✏️ Edit</button>
                    <button @click="deleteRow(row.id)" class="delete-btn">🗑️ Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-else>No data in table</p>
          </div>
        </div>
        
        <div v-if="crudResult" class="results">
          <pre>{{ crudResult }}</pre>
        </div>
      </section>

      <!-- Section 3: SQL Interface -->
      <section class="test-section">
        <h2>📝 SQL UPDATE Examples</h2>
        
        <div class="sql-examples">
          <h3>Try these UPDATE queries:</h3>
          
          <div class="sql-query" @click="runSqlQuery(sqlExamples.updateSingle)">
            <code>{{ sqlExamples.updateSingle }}</code>
            <span>Update single row by ID</span>
          </div>
          
          <div class="sql-query" @click="runSqlQuery(sqlExamples.updateMultiple)">
            <code>{{ sqlExamples.updateMultiple }}</code>
            <span>Update multiple rows with WHERE</span>
          </div>
          
          <div class="sql-query" @click="runSqlQuery(sqlExamples.updateWithCondition)">
            <code>{{ sqlExamples.updateWithCondition }}</code>
            <span>Update with complex condition</span>
          </div>
          
          <div class="sql-query" @click="runSqlQuery(sqlExamples.updateAll)">
            <code>{{ sqlExamples.updateAll }}</code>
            <span>Update all rows</span>
          </div>
        </div>
        
        <div class="sql-editor">
          <h3>Custom SQL UPDATE</h3>
          <textarea v-model="sqlUpdateQuery" placeholder="Enter UPDATE SQL query..."></textarea>
          <button @click="executeSqlUpdate" :disabled="!sqlUpdateQuery">Execute UPDATE</button>
        </div>
        
        <div v-if="sqlResult" class="results">
          <h3>SQL Results:</h3>
          <pre>{{ sqlResult }}</pre>
        </div>
      </section>

      <!-- Section 4: Test Scenarios -->
      <section class="test-section">
        <h2>🧪 UPDATE Test Scenarios</h2>
        
        <div class="test-scenarios">
          <div class="scenario">
            <h4>Test 1: Basic UPDATE</h4>
            <p>Update a single field in a single row</p>
            <button @click="testBasicUpdate">Run Test</button>
          </div>
          
          <div class="scenario">
            <h4>Test 2: Multiple Field UPDATE</h4>
            <p>Update multiple fields in a single row</p>
            <button @click="testMultiFieldUpdate">Run Test</button>
          </div>
          
          <div class="scenario">
            <h4>Test 3: Conditional UPDATE</h4>
            <p>Update rows based on a condition</p>
            <button @click="testConditionalUpdate">Run Test</button>
          </div>
          
          <div class="scenario">
            <h4>Test 4: UPDATE with Validation</h4>
            <p>Test UPDATE with unique constraint validation</p>
            <button @click="testUpdateValidation">Run Test</button>
          </div>
        </div>
        
        <div v-if="testScenarioResult" class="results">
          <h3>Test Results:</h3>
          <pre>{{ testScenarioResult }}</pre>
        </div>
      </section>

      <!-- Section 5: Comprehensive Tests -->
      <section class="test-section">
        <h2>🚀 Comprehensive Test Suite</h2>
        <button @click="runComprehensiveTests" :disabled="runningTests">
          {{ runningTests ? 'Running...' : 'Run All Tests' }}
        </button>
        
        <div v-if="comprehensiveResults" class="results">
          <h3>Test Results:</h3>
          <pre>{{ comprehensiveResults }}</pre>
        </div>
      </section>
    </div>

    <!-- Status Display -->
    <div v-if="error" class="error">
      <h3>❌ Error</h3>
      <pre>{{ error }}</pre>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Processing...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

// API configuration
const API_BASE = 'http://localhost:8000/api'

// State
const loading = ref(false)
const runningTests = ref(false)
const error = ref(null)
const tables = ref([])
const activeTable = ref('users')
const crudTable = ref('test_users')
const tableData = ref(null)
const crudResult = ref(null)
const sqlResult = ref(null)
const comprehensiveResults = ref(null)
const testScenarioResult = ref(null)

// Update form state
const showUpdateForm = ref(false)
const updateRowId = ref('')
const updateData = reactive({
  name: '',
  email: '',
  age: ''
})
const sqlUpdateQuery = ref('UPDATE users SET name = "Updated Name" WHERE id = 1')

// SQL examples
const sqlExamples = reactive({
  updateSingle: 'UPDATE users SET email = "updated@example.com" WHERE id = 1',
  updateMultiple: 'UPDATE users SET age = 30 WHERE age < 25',
  updateWithCondition: 'UPDATE users SET name = "VIP User" WHERE email LIKE "%@example.com"',
  updateAll: 'UPDATE tasks SET completed = true'
})

onMounted(() => {
  getTables()
})

// 1. Get all tables
const getTables = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`${API_BASE}/tables`)
    tables.value = response.data.tables || response.data
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 2. Get table schema
const getTableSchema = async (tableName) => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/tables/${tableName}`)
    crudResult.value = `Schema for ${tableName}:\n${JSON.stringify(response.data.columns, null, 2)}`
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 3. Set active table
const setActiveTable = (tableName) => {
  activeTable.value = tableName
  crudTable.value = tableName
  getTableData()
}

// 4. Get table data
const getTableData = async () => {
  if (!activeTable.value) return
  
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/tables/${activeTable.value}`)
    tableData.value = response.data
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 5. Create test table
const createTestTable = async () => {
  loading.value = true
  try {
    const tableDef = {
      name: crudTable.value,
      columns: [
        { name: 'id', type: 'INT', primary: true },
        { name: 'name', type: 'TEXT' },
        { name: 'email', type: 'TEXT', unique: true },
        { name: 'age', type: 'INT' },
        { name: 'active', type: 'BOOLEAN', default: true },
        { name: 'updated_at', type: 'TIMESTAMP' }
      ]
    }
    const response = await axios.post(`${API_BASE}/tables`, tableDef)
    crudResult.value = `Table created:\n${JSON.stringify(response.data, null, 2)}`
    getTables() // Refresh table list
    activeTable.value = crudTable.value
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 6. Insert test data
const insertTestData = async () => {
  if (!activeTable.value) {
    error.value = 'Please select or create a table first'
    return
  }
  
  loading.value = true
  try {
    const testData = {
      name: 'Test User ' + Date.now(),
      email: `test${Date.now()}@example.com`,
      age: Math.floor(Math.random() * 50) + 20,
      active: true,
      updated_at: new Date().toISOString()
    }
    const response = await axios.post(`${API_BASE}/tables/${activeTable.value}/rows`, { data: testData })
    crudResult.value = `Data inserted:\n${JSON.stringify(response.data, null, 2)}`
    getTableData() // Refresh table data
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 7. Read table data
const readTableData = async () => {
  await getTableData()
}

// 8. UPDATE ROW DATA - This is the main UPDATE operation
const updateRowData = async () => {
  if (!activeTable.value || !updateRowId.value) {
    error.value = 'Please select a table and enter a row ID'
    return
  }
  
  loading.value = true
  try {
    // Prepare update data
    const updatePayload = {}
    if (updateData.name) updatePayload.name = updateData.name
    if (updateData.email) updatePayload.email = updateData.email
    if (updateData.age) updatePayload.age = parseInt(updateData.age)
    updatePayload.updated_at = new Date().toISOString()
    
    // Call UPDATE endpoint
    const response = await axios.put(`${API_BASE}/tables/${activeTable.value}/rows`, {
      data: updatePayload,
      where: { id: parseInt(updateRowId.value) }
    })
    
    crudResult.value = `UPDATE Result:\n${JSON.stringify(response.data, null, 2)}`
    
    // Clear form
    updateRowId.value = ''
    updateData.name = ''
    updateData.email = ''
    updateData.age = ''
    
    // Refresh data
    getTableData()
    
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 9. Update multiple rows
const updateMultipleRows = async () => {
  if (!activeTable.value) {
    error.value = 'Please select a table first'
    return
  }
  
  loading.value = true
  try {
    const response = await axios.put(`${API_BASE}/tables/${activeTable.value}/rows`, {
      data: { active: false, updated_at: new Date().toISOString() },
      where: { age: { $gt: 40 } } // Note: Your backend might need to parse this
    })
    
    crudResult.value = `Multiple UPDATE Result:\n${JSON.stringify(response.data, null, 2)}`
    getTableData()
    
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 10. Edit row (pre-fill update form)
const editRow = (row) => {
  showUpdateForm.value = true
  updateRowId.value = row.id
  updateData.name = row.name || ''
  updateData.email = row.email || ''
  updateData.age = row.age || ''
}

// 11. Delete row
const deleteRow = async (rowId) => {
  if (!confirm('Are you sure you want to delete this row?')) return
  
  loading.value = true
  try {
    const response = await axios.delete(`${API_BASE}/tables/${activeTable.value}/rows`, {
      params: { where: JSON.stringify({ id: rowId }) }
    })
    
    crudResult.value = `DELETE Result:\n${JSON.stringify(response.data, null, 2)}`
    getTableData()
    
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 12. Delete test data
const deleteTestData = async () => {
  if (!activeTable.value) {
    error.value = 'Please select a table first'
    return
  }
  
  if (!confirm('Delete all rows from this table?')) return
  
  loading.value = true
  try {
    const response = await axios.delete(`${API_BASE}/tables/${activeTable.value}/rows`, {
      params: { where: '{}' } // Delete all rows
    })
    
    crudResult.value = `DELETE Result:\n${JSON.stringify(response.data, null, 2)}`
    getTableData()
    
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 13. Execute SQL UPDATE query
const executeSqlUpdate = async () => {
  loading.value = true
  try {
    const response = await axios.post(`${API_BASE}/query`, {
      sql: sqlUpdateQuery.value
    })
    sqlResult.value = `SQL UPDATE Result:\n${JSON.stringify(response.data, null, 2)}`
    getTableData() // Refresh to see changes
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

// 14. Run SQL query from examples
const runSqlQuery = async (query) => {
  sqlUpdateQuery.value = query
  await executeSqlUpdate()
}

// 15. Test Scenarios
const testBasicUpdate = async () => {
  loading.value = true
  try {
    // First insert a test row
    const insertResponse = await axios.post(`${API_BASE}/tables/test_users/rows`, {
      data: { name: 'Original Name', email: 'original@test.com', age: 25 }
    })
    
    const rowId = insertResponse.data.row_id || 1
    
    // Then update it
    const updateResponse = await axios.put(`${API_BASE}/tables/test_users/rows`, {
      data: { name: 'Updated Name', age: 30 },
      where: { id: rowId }
    })
    
    testScenarioResult.value = `Basic UPDATE Test:\n
    Inserted row ID: ${rowId}
    UPDATE Result: ${JSON.stringify(updateResponse.data, null, 2)}`
    
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

const testMultiFieldUpdate = async () => {
  loading.value = true
  try {
    const response = await axios.put(`${API_BASE}/tables/users/rows`, {
      data: { 
        name: 'Multi Updated',
        email: 'multi@updated.com',
        age: 35,
        updated_at: new Date().toISOString()
      },
      where: { id: 1 }
    })
    
    testScenarioResult.value = `Multi-field UPDATE Test:\n${JSON.stringify(response.data, null, 2)}`
    getTableData()
    
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

const testConditionalUpdate = async () => {
  loading.value = true
  try {
    const response = await axios.put(`${API_BASE}/tables/users/rows`, {
      data: { age: 99 },
      where: { name: 'Alice Johnson' }
    })
    
    testScenarioResult.value = `Conditional UPDATE Test:\n${JSON.stringify(response.data, null, 2)}`
    getTableData()
    
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    loading.value = false
  }
}

const testUpdateValidation = async () => {
  loading.value = true
  try {
    // Try to update with duplicate email (should fail due to unique constraint)
    const response = await axios.put(`${API_BASE}/tables/users/rows`, {
      data: { email: 'alice@example.com' }, // Duplicate email
      where: { id: 2 } // Trying to set Bob's email to Alice's email
    })
    
    testScenarioResult.value = `UPDATE Validation Test:\n${JSON.stringify(response.data, null, 2)}`
    
  } catch (err) {
    testScenarioResult.value = `UPDATE Validation Test (Expected to fail):\n${err.response?.data?.detail || err.message}`
  } finally {
    loading.value = false
  }
}

// 16. Run comprehensive tests
const runComprehensiveTests = async () => {
  runningTests.value = true
  error.value = null
  comprehensiveResults.value = null
  
  try {
    const response = await axios.get(`${API_BASE}/test-comprehensive`, {
      timeout: 60000 // 60 second timeout for comprehensive tests
    })
    comprehensiveResults.value = response.data.output || response.data
  } catch (err) {
    error.value = err.response?.data || err.message
  } finally {
    runningTests.value = false
  }
}
</script>

<style scoped>
/* Add these styles to your existing CSS */

.test-dashboard {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.current-table {
  background: #e8f4fc;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 4px solid #3498db;
}

.table-name {
  color: #2980b9;
  font-weight: bold;
  background: white;
  padding: 4px 12px;
  border-radius: 20px;
  border: 1px solid #3498db;
}

.update-form {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  border: 1px solid #dee2e6;
}

.update-form h3 {
  margin-top: 0;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #495057;
}

.form-group input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
}

.button-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.button-group button {
  flex: 1;
  min-width: 120px;
}

button.secondary {
  background-color: #6c757d;
}

button.secondary:hover:not(:disabled) {
  background-color: #5a6268;
}

button.cancel {
  background-color: #dc3545;
}

button.cancel:hover:not(:disabled) {
  background-color: #c82333;
}

.table-container {
  overflow-x: auto;
  margin: 20px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

thead {
  background: #2c3e50;
  color: white;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

tbody tr:hover {
  background-color: #f8f9fa;
}

.actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn {
  padding: 4px 8px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.edit-btn {
  background-color: #ffc107;
  color: #212529;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.sql-examples {
  margin: 20px 0;
}

.sql-query {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin: 10px 0;
  border-left: 3px solid #17a2b8;
  cursor: pointer;
  transition: all 0.3s;
}

.sql-query:hover {
  background: #e8f4fc;
  transform: translateX(5px);
}

.sql-query code {
  font-family: 'Courier New', monospace;
  color: #2c3e50;
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
}

.sql-query span {
  font-size: 12px;
  color: #6c757d;
  font-style: italic;
}

.sql-editor {
  margin: 20px 0;
}

.sql-editor textarea {
  width: 100%;
  height: 100px;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  resize: vertical;
  margin-bottom: 10px;
}

.test-scenarios {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.scenario {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-top: 4px solid #28a745;
}

.scenario h4 {
  margin-top: 0;
  color: #2c3e50;
}

.scenario p {
  color: #6c757d;
  font-size: 14px;
  margin: 10px 0;
}

.scenario button {
  width: 100%;
  margin-top: 10px;
}

/* Responsive design */
@media (max-width: 768px) {
  .test-scenarios {
    grid-template-columns: 1fr;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .button-group button {
    width: 100%;
  }
  
  .actions {
    flex-direction: column;
  }
}
</style>