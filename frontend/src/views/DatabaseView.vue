<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Database Explorer</h1>
        <p class="text-gray-600">Manage database tables and data</p>
      </div>
      <div class="flex space-x-3">
        <button @click="refreshTables" class="btn-secondary">
          Refresh
        </button>
        <button @click="showCreateTable = true" class="btn-primary">
          + Create Table
        </button>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" :class="messageType === 'success' ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'"
         class="p-4 rounded-lg border">
      {{ message }}
    </div>

    <!-- Tables List -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Tables in Database</h2>
      
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600">Loading tables...</p>
      </div>
      
      <div v-else-if="tables.length === 0" class="text-center py-8 text-gray-500">
        No tables found. Create your first table!
      </div>
      
      <div v-else class="space-y-4">
        <div v-for="table in tables" :key="table.name" 
             class="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <h3 class="font-semibold text-lg">{{ table.name }}</h3>
                <span class="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                  {{ table.row_count }} rows
                </span>
              </div>
              <p class="text-sm text-gray-600 mt-1">
                Columns: {{ table.columns.map(c => c.name).join(', ') }}
              </p>
            </div>
            <div class="flex space-x-2">
              <button @click="viewTable(table.name)" class="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200">
                View Data
              </button>
              <button @click="showInsertRow(table.name)" class="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200">
                + Add Row
              </button>
              <button @click="deleteTable(table.name)" class="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Data Viewer -->
    <div v-if="selectedTable" class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold">Table: {{ selectedTable.name }}</h2>
        <div class="flex space-x-3">
          <button @click="showInsertRow(selectedTable.name)" class="btn-primary text-sm">
            + Add Row
          </button>
          <button @click="selectedTable = null" class="btn-secondary text-sm">
            Close
          </button>
        </div>
      </div>
      
      <div v-if="selectedTable.rows.length === 0" class="text-center py-8 text-gray-500">
        No data in this table
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="table">
          <thead>
            <tr>
              <th v-for="column in selectedTable.columns" :key="column.name">
                {{ column.name }}
                <span class="text-xs text-gray-400 ml-1">({{ column.type }})</span>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in selectedTable.rows" :key="index">
              <td v-for="column in selectedTable.columns" :key="column.name">
                {{ row[column.name] }}
              </td>
              <td>
                <div class="flex space-x-2">
                  <button @click="editRow(selectedTable.name, row)" class="text-blue-600 hover:text-blue-800 text-sm">
                    Edit
                  </button>
                  <button @click="deleteRow(selectedTable.name, row)" class="text-red-600 hover:text-red-800 text-sm">
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Table Modal -->
    <div v-if="showCreateTable" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <h3 class="text-lg font-semibold mb-4">Create New Table</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Table Name *</label>
            <input v-model="newTable.name" type="text" class="input-field" placeholder="users">
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Columns</label>
            <div class="space-y-2 mb-3">
              <div v-for="(col, index) in newTable.columns" :key="index" class="flex items-center space-x-2">
                <input v-model="col.name" type="text" class="input-field flex-1" placeholder="column_name">
                <select v-model="col.type" class="input-field w-24">
                  <option value="INT">INT</option>
                  <option value="TEXT">TEXT</option>
                  <option value="BOOLEAN">BOOLEAN</option>
                  <option value="FLOAT">FLOAT</option>
                  <option value="TIMESTAMP">TIMESTAMP</option>
                </select>
                <div class="flex space-x-1">
                  <input type="checkbox" v-model="col.primary" class="h-4 w-4" title="Primary Key">
                  <input type="checkbox" v-model="col.unique" class="h-4 w-4" title="Unique">
                </div>
                <button @click="removeColumn(index)" class="p-2 text-red-600 hover:text-red-800">
                  ×
                </button>
              </div>
            </div>
            <button @click="addColumn" class="text-sm text-blue-600 hover:text-blue-800">
              + Add Column
            </button>
          </div>
          
          <div class="flex justify-end space-x-3 pt-4">
            <button @click="showCreateTable = false" class="btn-secondary">
              Cancel
            </button>
            <button @click="createTable" class="btn-primary">
              Create Table
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Insert/Edit Row Modal -->
    <div v-if="showRowModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <h3 class="text-lg font-semibold mb-4">
          {{ editingRow ? 'Edit Row' : 'Insert New Row' }} in {{ rowModalTable }}
        </h3>
        
        <div class="space-y-4">
          <div v-for="column in rowModalColumns" :key="column.name" class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              {{ column.name }}
              <span class="text-xs text-gray-500">({{ column.type }})</span>
              <span v-if="column.primary" class="text-xs text-blue-600 ml-1">PK</span>
            </label>
            <input v-model="rowData[column.name]" 
                   :type="getInputType(column.type)"
                   class="input-field"
                   :placeholder="column.primary && !editingRow ? 'Auto-generated' : 'Enter value'"
                   :disabled="column.primary && !editingRow">
          </div>
          
          <div class="flex justify-end space-x-3 pt-4">
            <button @click="cancelRowModal" class="btn-secondary">
              Cancel
            </button>
            <button @click="saveRow" class="btn-primary">
              {{ editingRow ? 'Update' : 'Insert' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const loading = ref(false)
const tables = ref([])
const selectedTable = ref(null)
const showCreateTable = ref(false)
const showRowModal = ref(false)
const rowModalTable = ref('')
const rowModalColumns = ref([])
const editingRow = ref(null)
const rowData = ref({})
const message = ref('')
const messageType = ref('')

const newTable = ref({
  name: '',
  columns: [
    { name: 'id', type: 'INT', primary: true, unique: false }
  ]
})

onMounted(() => {
  loadTables()
})

const loadTables = async () => {
  loading.value = true
  try {
    const data = await api.listTables()
    if (data.success) {
      tables.value = data.tables || []
    }
  } catch (error) {
    showMessage('Error loading tables: ' + error.message, 'error')
  } finally {
    loading.value = false
  }
}

const refreshTables = () => {
  loadTables()
  selectedTable.value = null
}

const viewTable = async (tableName) => {
  try {
    const data = await api.getTableRows(tableName)
    if (data.success) {
      selectedTable.value = {
        name: tableName,
        columns: data.columns || [],
        rows: data.rows || []
      }
    }
  } catch (error) {
    showMessage('Error loading table data: ' + error.message, 'error')
  }
}

const deleteTable = async (tableName) => {
  if (!confirm(`Are you sure you want to delete table '${tableName}'? This will delete all data.`)) {
    return
  }
  
  try {
    const data = await api.deleteTable(tableName)
    if (data.success) {
      showMessage(`Table '${tableName}' deleted successfully`, 'success')
      loadTables()
      selectedTable.value = null
    }
  } catch (error) {
    showMessage('Error deleting table: ' + error.message, 'error')
  }
}

const addColumn = () => {
  newTable.value.columns.push({ name: '', type: 'TEXT', primary: false, unique: false })
}

const removeColumn = (index) => {
  newTable.value.columns.splice(index, 1)
}

const createTable = async () => {
  if (!newTable.value.name.trim()) {
    showMessage('Please enter a table name', 'error')
    return
  }
  
  if (newTable.value.columns.length === 0) {
    showMessage('Please add at least one column', 'error')
    return
  }
  
  // Validate column names
  for (const col of newTable.value.columns) {
    if (!col.name.trim()) {
      showMessage('All columns must have a name', 'error')
      return
    }
  }
  
  try {
    const data = await api.createTable(newTable.value.name, newTable.value.columns)
    if (data.success) {
      showMessage(`Table '${newTable.value.name}' created successfully`, 'success')
      showCreateTable.value = false
      newTable.value = {
        name: '',
        columns: [{ name: 'id', type: 'INT', primary: true, unique: false }]
      }
      loadTables()
    }
  } catch (error) {
    showMessage('Error creating table: ' + error.message, 'error')
  }
}

const showInsertRow = async (tableName) => {
  try {
    const data = await api.getTableRows(tableName, 1)
    if (data.success) {
      rowModalTable.value = tableName
      rowModalColumns.value = data.columns || []
      rowData.value = {}
      editingRow.value = null
      showRowModal.value = true
    }
  } catch (error) {
    showMessage('Error: ' + error.message, 'error')
  }
}

const editRow = (tableName, row) => {
  rowModalTable.value = tableName
  rowData.value = { ...row }
  editingRow.value = row
  
  // Get columns for the table
  if (selectedTable.value && selectedTable.value.name === tableName) {
    rowModalColumns.value = selectedTable.value.columns
  } else {
    // If table not loaded, use basic columns
    rowModalColumns.value = Object.keys(row).map(key => ({
      name: key,
      type: 'TEXT'
    }))
  }
  
  showRowModal.value = true
}

const cancelRowModal = () => {
  showRowModal.value = false
  rowData.value = {}
  editingRow.value = null
}

const saveRow = async () => {
  try {
    if (editingRow.value) {
      // Update existing row
      const where = {}
      if (editingRow.value.id !== undefined) {
        where.id = editingRow.value.id
      }
      
      const data = await api.updateRows(rowModalTable.value, rowData.value, where)
      if (data.success) {
        showMessage(`Row updated successfully`, 'success')
        cancelRowModal()
        if (selectedTable.value && selectedTable.value.name === rowModalTable.value) {
          viewTable(rowModalTable.value)
        }
      }
    } else {
      // Insert new row
      const data = await api.insertRow(rowModalTable.value, rowData.value)
      if (data.success) {
        showMessage(`Row inserted successfully with ID: ${data.row_id}`, 'success')
        cancelRowModal()
        if (selectedTable.value && selectedTable.value.name === rowModalTable.value) {
          viewTable(rowModalTable.value)
        }
      }
    }
  } catch (error) {
    showMessage('Error: ' + error.message, 'error')
  }
}

const deleteRow = async (tableName, row) => {
  if (!confirm('Are you sure you want to delete this row?')) {
    return
  }
  
  try {
    const where = {}
    if (row.id !== undefined) {
      where.id = row.id
    }
    
    const data = await api.deleteRows(tableName, where)
    if (data.success) {
      showMessage(`Row deleted successfully`, 'success')
      if (selectedTable.value && selectedTable.value.name === tableName) {
        viewTable(tableName)
      }
    }
  } catch (error) {
    showMessage('Error deleting row: ' + error.message, 'error')
  }
}

const getInputType = (columnType) => {
  switch (columnType) {
    case 'INT': return 'number'
    case 'FLOAT': return 'number'
    case 'BOOLEAN': return 'checkbox'
    default: return 'text'
  }
}

const showMessage = (msg, type = 'success') => {
  message.value = msg
  messageType.value = type
  setTimeout(() => {
    message.value = ''
  }, 5000)
}
</script>