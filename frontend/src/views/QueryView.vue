<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Query Editor</h1>
        <p class="text-gray-600">Write and execute SQL queries</p>
      </div>
      <div class="flex space-x-3">
        <button @click="saveQuery" class="btn-secondary">
          Save
        </button>
        <button @click="loadSample" class="btn-secondary">
          Sample
        </button>
        <button @click="clearEditor" class="btn-secondary">
          Clear
        </button>
      </div>
    </div>

    <!-- Query Editor -->
    <div class="card">
      <div class="border-b pb-4 mb-4">
        <div class="flex items-center justify-between">
          <h3 class="font-medium">SQL Query Editor</h3>
          <button @click="executeQuery" :disabled="executing" class="btn-primary flex items-center">
            <svg v-if="executing" class="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Execute Query
          </button>
        </div>
      </div>
      
      <textarea v-model="query" 
                class="w-full h-64 p-4 font-mono text-sm border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
                placeholder="Enter your SQL query here...
Examples:
SELECT * FROM users;
SELECT * FROM tasks WHERE completed = false;
INSERT INTO users (name, email, age) VALUES ('John', 'john@example.com', 30);"></textarea>
      
      <div class="mt-4 flex items-center justify-between text-sm text-gray-600">
        <div>
          {{ query.split('\n').length }} lines • {{ query.length }} characters
        </div>
        <div v-if="executionTime">
          Executed in {{ executionTime }}ms
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-red-400 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div>
          <h3 class="font-medium text-red-800">Query Error</h3>
          <p class="text-red-700 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Results -->
    <div v-if="results" class="card">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold">Query Results</h2>
        <div class="flex items-center space-x-4">
          <span class="text-sm text-gray-600">{{ results.count }} row(s) returned</span>
          <button @click="exportResults" class="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200">
            Export CSV
          </button>
        </div>
      </div>

      <div v-if="results.rows && results.rows.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="key in Object.keys(results.rows[0])" :key="key"
                  class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                {{ key }}
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="(row, index) in results.rows" :key="index">
              <td v-for="(value, key) in row" :key="key"
                  class="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                {{ value }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-else class="text-center py-8 text-gray-500">
        No rows returned
      </div>
    </div>

    <!-- Query History -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Query History</h2>
      
      <div v-if="history.length === 0" class="text-center py-4 text-gray-500">
        No query history yet
      </div>
      
      <div v-else class="space-y-2">
        <div v-for="(item, index) in history.slice(0, 5)" :key="index"
             @click="loadHistoryQuery(item.query)"
             class="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
          <div class="flex items-center justify-between">
            <div class="font-mono text-sm truncate">{{ item.query }}</div>
            <div class="text-xs text-gray-500">{{ formatTime(item.timestamp) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../services/api'
import { useAppStore } from '../store/index'

const route = useRoute()
const appStore = useAppStore()

const query = ref('SELECT * FROM users;')
const executing = ref(false)
const error = ref('')
const results = ref(null)
const executionTime = ref(0)
const history = ref([])

onMounted(() => {
  // Load query from URL if present
  if (route.query.query) {
    query.value = decodeURIComponent(route.query.query)
  }
  
  // Load history
  history.value = appStore.queryHistory
})

const executeQuery = async () => {
  if (!query.value.trim()) {
    error.value = 'Please enter a query'
    return
  }
  
  executing.value = true
  error.value = ''
  results.value = null
  executionTime.value = 0
  
  const startTime = Date.now()
  
  try {
    const response = await api.executeQuery(query.value)
    
    if (response.success) {
      results.value = response
      // Add to history
      appStore.addToQueryHistory(query.value)
      history.value = appStore.queryHistory
    } else {
      error.value = response.error || 'Query failed'
    }
  } catch (err) {
    error.value = err.message || 'Failed to execute query'
  } finally {
    executing.value = false
    executionTime.value = Date.now() - startTime
  }
}

const saveQuery = () => {
  const name = prompt('Enter a name for this query:')
  if (name) {
    const savedQueries = JSON.parse(localStorage.getItem('savedQueries') || '[]')
    savedQueries.push({ name, query: query.value, date: new Date().toISOString() })
    localStorage.setItem('savedQueries', JSON.stringify(savedQueries))
    alert('Query saved!')
  }
}

const loadSample = () => {
  query.value = `-- Sample queries
-- 1. Select all users
SELECT * FROM users;

-- 2. Select incomplete tasks
SELECT * FROM tasks WHERE completed = false;

-- 3. Insert new user
INSERT INTO users (name, email, age) VALUES ('Jane Doe', 'jane@example.com', 28);

-- 4. Update user age
UPDATE users SET age = 31 WHERE name = 'Bob Smith';

-- 5. Delete completed tasks
DELETE FROM tasks WHERE completed = true;`
}

const clearEditor = () => {
  query.value = ''
  error.value = ''
  results.value = null
}

const exportResults = () => {
  if (!results.value || !results.value.rows || results.value.rows.length === 0) {
    alert('No results to export')
    return
  }
  
  const headers = Object.keys(results.value.rows[0])
  const csvContent = [
    headers.join(','),
    ...results.value.rows.map(row => 
      headers.map(header => `"${row[header] || ''}"`).join(',')
    )
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'query_results.csv'
  a.click()
  window.URL.revokeObjectURL(url)
}

const loadHistoryQuery = (historyQuery) => {
  query.value = historyQuery
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>