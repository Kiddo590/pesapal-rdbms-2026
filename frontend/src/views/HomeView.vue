<template>
  <div class="home">
    <!-- Hero Section -->
    <div class="hero">
      <div class="hero-content">
        <h1 class="hero-title">Pesapal Custom RDBMS</h1>
        <p class="hero-subtitle">
          A complete relational database management system built from scratch
        </p>
        <div class="hero-actions">
          <router-link to="/query" class="btn-primary">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Try Query Editor
          </router-link>
          <router-link to="/demo" class="btn-secondary">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            View Demo App
          </router-link>
          <a href="http://localhost:8000/docs" target="_blank" class="btn-outline">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            API Documentation
          </a>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 class="feature-title">SQL-like Interface</h3>
          <p class="feature-description">
            Supports CREATE, SELECT, INSERT, UPDATE, DELETE with familiar SQL syntax
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </div>
          <h3 class="feature-title">Full CRUD Operations</h3>
          <p class="feature-description">
            Create, Read, Update, and Delete operations with transaction support
          </p>
        </div>

        <div class="feature-card">
          <div class="feature-icon">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 class="feature-title">Indexing & Joins</h3>
          <p class="feature-description">
            Basic indexing for performance and JOIN operations between tables
          </p>
        </div>
      </div>
    </div>

    <!-- Stats & Actions -->
    <div class="stats-actions">
      <div class="stats-section">
        <h2 class="section-title">Database Statistics</h2>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ stats.tables }}</div>
            <div class="stat-label">Tables</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.totalRows }}</div>
            <div class="stat-label">Total Rows</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.queries }}</div>
            <div class="stat-label">Queries Executed</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">
              <span :class="`status-dot ${databaseConnected ? 'connected' : 'disconnected'}`"></span>
              {{ databaseConnected ? 'Live' : 'Offline' }}
            </div>
            <div class="stat-label">Database Status</div>
          </div>
        </div>
      </div>

      <div class="actions-section">
        <h2 class="section-title">Quick Actions</h2>
        <div class="actions-grid">
          <router-link to="/database" class="action-card">
            <div class="action-icon">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
            </div>
            <div class="action-content">
              <h3 class="action-title">Browse Tables</h3>
              <p class="action-description">Explore database structure</p>
            </div>
          </router-link>

          <router-link to="/query" class="action-card">
            <div class="action-icon">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <div class="action-content">
              <h3 class="action-title">Run Sample Query</h3>
              <p class="action-description">SELECT * FROM users</p>
            </div>
          </router-link>

          <a href="http://localhost:8000/docs" target="_blank" class="action-card">
            <div class="action-icon">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <div class="action-content">
              <h3 class="action-title">API Playground</h3>
              <p class="action-description">Test API endpoints</p>
            </div>
          </a>

          <router-link to="/tests" class="action-card">
            <div class="action-icon">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div class="action-content">
              <h3 class="action-title">Test Dashboard</h3>
              <p class="action-description">Run comprehensive tests</p>
            </div>
          </router-link>
        </div>
      </div>
    </div>

    <!-- Test Dashboard Preview -->
    <div class="test-preview">
      <div class="test-preview-header">
        <h2 class="section-title">Ready to Test?</h2>
        <p class="section-subtitle">Run comprehensive tests on all RDBMS features from our Test Dashboard</p>
      </div>
      <div class="test-features">
        <div class="test-feature">
          <span class="test-feature-icon">✅</span>
          <span class="test-feature-text">CRUD Operations Testing</span>
        </div>
        <div class="test-feature">
          <span class="test-feature-icon">✅</span>
          <span class="test-feature-text">SQL Query Validation</span>
        </div>
        <div class="test-feature">
          <span class="test-feature-icon">✅</span>
          <span class="test-feature-text">JOIN Operations</span>
        </div>
        <div class="test-feature">
          <span class="test-feature-icon">✅</span>
          <span class="test-feature-text">Index Performance</span>
        </div>
      </div>
      <div class="test-actions">
        <router-link to="/tests" class="btn-primary">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
          </svg>
          Go to Test Dashboard
        </router-link>
        <button @click="runQuickTest" class="btn-secondary" :disabled="loading">
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ loading ? 'Running...' : 'Run Quick Test' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

const databaseConnected = ref(false)
const loading = ref(false)
const stats = reactive({
  tables: 0,
  totalRows: 0,
  queries: 0
})

onMounted(async () => {
  await checkDatabaseConnection()
  await loadStats()
})

const checkDatabaseConnection = async () => {
  try {
    const response = await axios.get(`${API_BASE}/tables`, { timeout: 5000 })
    databaseConnected.value = true
    return response.data
  } catch (error) {
    console.error('Database connection error:', error)
    databaseConnected.value = false
    return null
  }
}

const loadStats = async () => {
  try {
    // Get tables
    const tablesResponse = await axios.get(`${API_BASE}/tables`)
    const tablesData = tablesResponse.data
    
    stats.tables = tablesData.count || tablesData.tables?.length || 0
    
    // Calculate total rows
    let totalRows = 0
    if (tablesData.tables) {
      tablesData.tables.forEach(table => {
        totalRows += table.row_count || 0
      })
    }
    stats.totalRows = totalRows
    
    // For queries executed, you might want to track this in your backend
    // For now, we'll use a placeholder
    stats.queries = 0
    
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

const runQuickTest = async () => {
  loading.value = true
  try {
    // Create a simple test table
    const tableResponse = await axios.post(`${API_BASE}/tables`, {
      name: 'quick_test_' + Date.now(),
      columns: [
        { name: 'id', type: 'INT', primary: true },
        { name: 'name', type: 'TEXT' },
        { name: 'value', type: 'INT' }
      ]
    })
    
    // Insert test data
    const insertResponse = await axios.post(`${API_BASE}/tables/${tableResponse.data.table}/rows`, {
      data: { name: 'Test Data', value: 100 }
    })
    
    // Update the data
    const updateResponse = await axios.put(`${API_BASE}/tables/${tableResponse.data.table}/rows`, {
      data: { value: 200 },
      where: { id: insertResponse.data.row_id || 1 }
    })
    
    // Read the data
    const readResponse = await axios.get(`${API_BASE}/tables/${tableResponse.data.table}`)
    
    alert(`Quick Test Complete!\n
      Table Created: ${tableResponse.data.table}\n
      Row Inserted: ${insertResponse.data.row_id}\n
      Row Updated: ${updateResponse.data.updated_count}\n
      Current Value: ${readResponse.data.rows[0]?.value || 'N/A'}`)
    
    // Refresh stats
    await loadStats()
    
  } catch (error) {
    alert(`Test failed: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

/* Hero Section */
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 60px 40px;
  margin-bottom: 40px;
  color: white;
  text-align: center;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 16px;
}

.hero-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
  margin-bottom: 32px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary, .btn-outline {
  display: inline-flex;
  align-items: center;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-primary {
  background: white;
  color: #667eea;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.btn-outline {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-outline:hover {
  background: white;
  color: #667eea;
  transform: translateY(-2px);
}

/* Features Section */
.features-section {
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.feature-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-icon {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.feature-icon svg {
  color: white;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 8px;
}

.feature-description {
  color: #7f8c8d;
  line-height: 1.6;
}

/* Stats & Actions */
.stats-actions {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 40px;
  margin-bottom: 40px;
}

@media (max-width: 768px) {
  .stats-actions {
    grid-template-columns: 1fr;
  }
}

.section-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 24px;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.connected {
  background-color: #10b981;
  animation: pulse 2s infinite;
}

.status-dot.disconnected {
  background-color: #ef4444;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Actions Grid */
.actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

@media (max-width: 640px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
}

.action-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.action-icon {
  width: 48px;
  height: 48px;
  background: #f3f4f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon svg {
  color: #667eea;
}

.action-title {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
}

.action-description {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Test Preview */
.test-preview {
  background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%);
  border-radius: 12px;
  padding: 40px;
  margin-bottom: 40px;
}

.test-preview-header {
  text-align: center;
  margin-bottom: 32px;
}

.section-subtitle {
  color: #6b7280;
  font-size: 1.125rem;
  max-width: 600px;
  margin: 0 auto;
}

.test-features {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-bottom: 32px;
}

.test-feature {
  display: flex;
  align-items: center;
  gap: 8px;
  background: white;
  padding: 8px 16px;
  border-radius: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.test-feature-icon {
  font-size: 1.25rem;
}

.test-feature-text {
  font-weight: 500;
  color: #2c3e50;
}

.test-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}
</style>