<template>
  <div class="schema-visualizer">
    <div class="header">
      <h1>🗺️ Database Schema Visualizer</h1>
      <p>Interactive visualization of your database structure</p>
    </div>

    <div class="controls">
      <button @click="refreshSchema" :disabled="loading" class="refresh-btn">
        🔄 Refresh Schema
      </button>
      <div class="view-options">
        <label>
          <input type="checkbox" v-model="showColumnTypes" />
          Show Data Types
        </label>
        <label>
          <input type="checkbox" v-model="showConstraints" />
          Show Constraints
        </label>
        <label>
          <input type="checkbox" v-model="autoLayout" />
          Auto Layout
        </label>
      </div>
    </div>

    <!-- Main Visualization Area -->
    <div class="visualization-container" ref="container">
      <svg :width="svgWidth" :height="svgHeight" class="schema-svg">
        <!-- Background Grid -->
        <defs>
          <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#e0e0e0" stroke-width="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        
        <!-- Draw connections between tables (foreign keys) -->
        <g v-if="relationships.length > 0">
          <path
            v-for="(rel, index) in relationships"
            :key="`rel-${index}`"
            :d="calculateConnectionPath(rel)"
            fill="none"
            stroke="#4f46e5"
            stroke-width="2"
            marker-end="url(#arrowhead)"
            class="relationship-line"
          />
        </g>

        <!-- Draw table nodes -->
        <g v-for="table in tables" :key="table.name">
          <!-- Table Card -->
          <foreignObject
            :x="table.x"
            :y="table.y"
            :width="table.width"
            :height="table.height"
          >
            <div 
              class="table-node"
              :style="{ 
                width: table.width + 'px', 
                height: table.height + 'px',
                borderColor: tableColor(table)
              }"
              @mousedown="startDrag(table, $event)"
              @dblclick="showTableDetails(table)"
            >
              <!-- Table Header -->
              <div class="table-header" :style="{ backgroundColor: tableColor(table) }">
                <div class="table-name">
                  <strong>{{ table.name }}</strong>
                  <span class="row-count">{{ table.row_count }} rows</span>
                </div>
              </div>

              <!-- Columns List -->
              <div class="columns-list">
                <div 
                  v-for="col in table.columns" 
                  :key="col.name"
                  class="column-item"
                  :class="{ 
                    'primary-key': col.primary,
                    'foreign-key': isForeignKey(table.name, col.name)
                  }"
                >
                  <div class="column-name">
                    <span v-if="col.primary" class="pk-indicator">🔑</span>
                    <span v-if="isForeignKey(table.name, col.name)" class="fk-indicator">🔗</span>
                    {{ col.name }}
                  </div>
                  <div v-if="showColumnTypes" class="column-type">
                    {{ col.type }}
                    <span v-if="showConstraints">
                      <span v-if="col.primary" class="constraint">PK</span>
                      <span v-if="col.unique" class="constraint">UQ</span>
                      <span v-if="!col.nullable" class="constraint">NN</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </foreignObject>

          <!-- Table Label (outside for better positioning) -->
          <text
            :x="table.x + table.width / 2"
            :y="table.y - 10"
            text-anchor="middle"
            class="table-label"
          >
            {{ table.name }}
          </text>
        </g>
      </svg>

      <!-- Legend -->
      <div class="legend">
        <h4>Legend</h4>
        <div class="legend-item">
          <div class="legend-color pk"></div>
          <span>Primary Key</span>
        </div>
        <div class="legend-item">
          <div class="legend-color fk"></div>
          <span>Foreign Key</span>
        </div>
        <div class="legend-item">
          <div class="legend-color unique"></div>
          <span>Unique Constraint</span>
        </div>
        <div class="legend-item">
          <span class="constraint-badge">PK</span>
          <span>Primary Key</span>
        </div>
        <div class="legend-item">
          <span class="constraint-badge">UQ</span>
          <span>Unique</span>
        </div>
        <div class="legend-item">
          <span class="constraint-badge">NN</span>
          <span>Not Null</span>
        </div>
      </div>
    </div>

    <!-- Table Details Modal -->
    <div v-if="selectedTable" class="modal-overlay" @click="selectedTable = null">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Table Details: {{ selectedTable.name }}</h3>
          <button @click="selectedTable = null" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <div class="table-info">
            <div class="info-item">
              <strong>Row Count:</strong> {{ selectedTable.row_count }}
            </div>
            <div class="info-item">
              <strong>Columns:</strong> {{ selectedTable.columns.length }}
            </div>
          </div>
          
          <table class="columns-table">
            <thead>
              <tr>
                <th>Column</th>
                <th>Type</th>
                <th>Constraints</th>
                <th>Nullable</th>
                <th>Default</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="col in selectedTable.columns" :key="col.name">
                <td>
                  <span v-if="col.primary" class="pk-badge">PK</span>
                  <span v-if="isForeignKey(selectedTable.name, col.name)" class="fk-badge">FK</span>
                  {{ col.name }}
                </td>
                <td><code>{{ col.type }}</code></td>
                <td>
                  <span v-if="col.primary" class="constraint-chip">Primary</span>
                  <span v-if="col.unique" class="constraint-chip">Unique</span>
                </td>
                <td>{{ col.nullable ? 'Yes' : 'No' }}</td>
                <td>{{ col.default || '-' }}</td>
              </tr>
            </tbody>
          </table>

          <!-- Related Tables -->
          <div v-if="getRelatedTables(selectedTable.name).length > 0" class="related-tables">
            <h4>Related Tables</h4>
            <ul>
              <li v-for="rel in getRelatedTables(selectedTable.name)" :key="rel.table">
                {{ rel.type }} relationship with <strong>{{ rel.table }}</strong>
                <span v-if="rel.columns">({{ rel.columns.join(', ') }})</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Side Panel for Schema Information -->
    <div class="side-panel">
      <h3>Schema Summary</h3>
      <div class="summary-stats">
        <div class="stat">
          <div class="stat-value">{{ tables.length }}</div>
          <div class="stat-label">Tables</div>
        </div>
        <div class="stat">
          <div class="stat-value">{{ totalColumns }}</div>
          <div class="stat-label">Columns</div>
        </div>
        <div class="stat">
          <div class="stat-value">{{ primaryKeys }}</div>
          <div class="stat-label">Primary Keys</div>
        </div>
        <div class="stat">
          <div class="stat-value">{{ relationships.length }}</div>
          <div class="stat-label">Relationships</div>
        </div>
      </div>

      <div class="table-list">
        <h4>Tables</h4>
        <div 
          v-for="table in tables" 
          :key="table.name"
          class="table-list-item"
          @click="focusTable(table)"
          :class="{ active: selectedTable?.name === table.name }"
        >
          <div class="table-list-header">
            <strong>{{ table.name }}</strong>
            <span class="table-row-count">{{ table.row_count }} rows</span>
          </div>
          <div class="table-list-columns">
            <span v-for="col in table.columns.slice(0, 3)" :key="col.name" class="column-tag">
              {{ col.name }}
            </span>
            <span v-if="table.columns.length > 3" class="more-columns">
              +{{ table.columns.length - 3 }} more
            </span>
          </div>
        </div>
      </div>

      <!-- Schema Export -->
      <div class="export-options">
        <h4>Export Schema</h4>
        <button @click="exportAsJSON" class="export-btn">📥 JSON</button>
        <button @click="exportAsSQL" class="export-btn">🐬 SQL</button>
        <button @click="exportAsImage" class="export-btn">🖼️ Image</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8000/api'

// State
const loading = ref(false)
const tables = ref([])
const relationships = ref([])
const selectedTable = ref(null)
const showColumnTypes = ref(true)
const showConstraints = ref(true)
const autoLayout = ref(true)
const svgWidth = ref(1200)
const svgHeight = ref(800)
const container = ref(null)

// Color palette for tables
const tableColors = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#06b6d4', '#84cc16', '#f97316', '#6366f1', '#ec4899'
]

// Computed properties
const totalColumns = computed(() => 
  tables.value.reduce((sum, table) => sum + table.columns.length, 0)
)

const primaryKeys = computed(() => 
  tables.value.reduce((sum, table) => 
    sum + table.columns.filter(col => col.primary).length, 0
  )
)

// Initialize
onMounted(() => {
  loadSchema()
  if (container.value) {
    svgWidth.value = container.value.clientWidth
    svgHeight.value = container.value.clientHeight
  }
})

// Load schema from API
const loadSchema = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_BASE}/tables`)
    tables.value = response.data.tables || []
    
    // Initialize positions if not set
    if (autoLayout.value) {
      applyAutoLayout()
    } else if (!tables.value[0]?.x) {
      // Set default positions
      tables.value.forEach((table, index) => {
        table.x = 100 + (index % 3) * 350
        table.y = 100 + Math.floor(index / 3) * 250
        table.width = 280
        table.height = 200 + (table.columns.length * 25)
      })
    }
    
    // Detect relationships (simple heuristic: columns ending with _id)
    detectRelationships()
    
  } catch (error) {
    console.error('Error loading schema:', error)
  } finally {
    loading.value = false
  }
}

// Auto-layout tables (force-directed simulation)
const applyAutoLayout = () => {
  const centerX = svgWidth.value / 2
  const centerY = svgHeight.value / 2
  const radius = Math.min(svgWidth.value, svgHeight.value) / 3
  
  tables.value.forEach((table, index) => {
    const angle = (index * 2 * Math.PI) / tables.value.length
    table.x = centerX + radius * Math.cos(angle) - 140
    table.y = centerY + radius * Math.sin(angle) - 100
    table.width = 280
    table.height = 200 + (table.columns.length * 25)
  })
}

// Detect relationships between tables
const detectRelationships = () => {
  relationships.value = []
  
  // Simple detection: columns named like `othertable_id`
  for (const table of tables.value) {
    for (const column of table.columns) {
      if (column.name.endsWith('_id') || column.name === 'id') {
        const referencedTable = column.name.replace(/_id$/, '')
        
        // Check if referenced table exists
        if (tables.value.some(t => t.name === referencedTable)) {
          relationships.value.push({
            from: referencedTable,
            to: table.name,
            column: column.name,
            type: 'foreign_key'
          })
        }
      }
    }
  }
}

// Check if a column is a foreign key
const isForeignKey = (tableName, columnName) => {
  return relationships.value.some(rel => 
    rel.to === tableName && rel.column === columnName
  )
}

// Get related tables for a given table
const getRelatedTables = (tableName) => {
  return relationships.value
    .filter(rel => rel.from === tableName || rel.to === tableName)
    .map(rel => ({
      table: rel.from === tableName ? rel.to : rel.from,
      type: rel.from === tableName ? 'outgoing' : 'incoming',
      columns: [rel.column]
    }))
}

// Calculate connection path between tables
const calculateConnectionPath = (relationship) => {
  const fromTable = tables.value.find(t => t.name === relationship.from)
  const toTable = tables.value.find(t => t.name === relationship.to)
  
  if (!fromTable || !toTable) return ''
  
  const fromX = fromTable.x + fromTable.width
  const fromY = fromTable.y + fromTable.height / 2
  const toX = toTable.x
  const toY = toTable.y + toTable.height / 2
  
  // Create a curved path
  const midX = (fromX + toX) / 2
  return `M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`
}

// Get color for table
const tableColor = (table) => {
  const index = tables.value.findIndex(t => t.name === table.name)
  return tableColors[index % tableColors.length]
}

// Drag and drop functionality
let dragTable = null
let dragOffset = { x: 0, y: 0 }

const startDrag = (table, event) => {
  if (autoLayout.value) return // Disable drag in auto-layout mode
  
  dragTable = table
  const rect = event.target.getBoundingClientRect()
  dragOffset.x = event.clientX - rect.left
  dragOffset.y = event.clientY - rect.top
  
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

const handleDrag = (event) => {
  if (!dragTable) return
  
  const containerRect = container.value.getBoundingClientRect()
  dragTable.x = event.clientX - containerRect.left - dragOffset.x
  dragTable.y = event.clientY - containerRect.top - dragOffset.y
  
  // Keep within bounds
  dragTable.x = Math.max(0, Math.min(svgWidth.value - dragTable.width, dragTable.x))
  dragTable.y = Math.max(0, Math.min(svgHeight.value - dragTable.height, dragTable.y))
}

const stopDrag = () => {
  dragTable = null
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// Show table details
const showTableDetails = (table) => {
  selectedTable.value = table
}

// Focus on table (center view)
const focusTable = (table) => {
  // In a real implementation, you would animate the view to center on this table
  selectedTable.value = table
}

// Export functions
const exportAsJSON = () => {
  const schemaData = {
    tables: tables.value,
    relationships: relationships.value,
    exportedAt: new Date().toISOString()
  }
  
  const dataStr = JSON.stringify(schemaData, null, 2)
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
  
  const exportFileDefaultName = `schema-${new Date().toISOString().split('T')[0]}.json`
  
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', exportFileDefaultName)
  linkElement.click()
}

const exportAsSQL = () => {
  let sql = '-- Database Schema Export\n'
  sql += `-- Generated: ${new Date().toISOString()}\n\n`
  
  tables.value.forEach(table => {
    sql += `-- Table: ${table.name}\n`
    sql += `CREATE TABLE ${table.name} (\n`
    
    table.columns.forEach((col, index) => {
      sql += `  ${col.name} ${col.type}`
      if (col.primary) sql += ' PRIMARY KEY'
      if (col.unique) sql += ' UNIQUE'
      if (!col.nullable) sql += ' NOT NULL'
      if (col.default) sql += ` DEFAULT ${col.default}`
      if (index < table.columns.length - 1) sql += ','
      sql += '\n'
    })
    
    sql += ');\n\n'
  })
  
  // Download SQL file
  const dataUri = 'data:application/sql;charset=utf-8,'+ encodeURIComponent(sql)
  const linkElement = document.createElement('a')
  linkElement.setAttribute('href', dataUri)
  linkElement.setAttribute('download', `schema-${new Date().toISOString().split('T')[0]}.sql`)
  linkElement.click()
}

const exportAsImage = () => {
  alert('Image export would require a canvas library like html2canvas')
  // In production, you would use html2canvas or similar
}

const refreshSchema = () => {
  loadSchema()
}
</script>

<style scoped>
.schema-visualizer {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8fafc;
}

.header {
  background: white;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
  text-align: center;
}

.header h1 {
  margin: 0;
  color: #1e293b;
  font-size: 2rem;
}

.header p {
  margin: 8px 0 0;
  color: #64748b;
}

.controls {
  background: white;
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.refresh-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.view-options {
  display: flex;
  gap: 20px;
}

.view-options label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #475569;
}

.visualization-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: white;
}

.schema-svg {
  display: block;
}

.table-node {
  background: white;
  border: 2px solid;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  cursor: move;
  transition: transform 0.2s, box-shadow 0.2s;
}

.table-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

.table-header {
  padding: 12px;
  color: white;
}

.table-name {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.row-count {
  font-size: 0.8rem;
  opacity: 0.9;
}

.columns-list {
  padding: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.column-item {
  padding: 8px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.column-item:last-child {
  border-bottom: none;
}

.column-item.primary-key {
  background: #eff6ff;
  border-left: 3px solid #3b82f6;
}

.column-item.foreign-key {
  background: #f0f9ff;
  border-left: 3px solid #0ea5e9;
}

.column-name {
  font-weight: 500;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 4px;
}

.pk-indicator, .fk-indicator {
  font-size: 0.8rem;
}

.column-type {
  font-size: 0.8rem;
  color: #64748b;
  font-family: 'Courier New', monospace;
}

.constraint {
  margin-left: 4px;
  padding: 2px 4px;
  background: #e2e8f0;
  border-radius: 3px;
  font-size: 0.7rem;
}

.table-label {
  font-size: 12px;
  fill: #475569;
  font-weight: 500;
}

.legend {
  position: absolute;
  top: 20px;
  right: 20px;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-width: 180px;
}

.legend h4 {
  margin: 0 0 12px;
  color: #1e293b;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 0.9rem;
  color: #475569;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-color.pk {
  background: #3b82f6;
}

.legend-color.fk {
  background: #0ea5e9;
}

.legend-color.unique {
  background: #10b981;
}

.constraint-badge {
  display: inline-block;
  width: 24px;
  height: 16px;
  background: #e2e8f0;
  border-radius: 3px;
  text-align: center;
  font-size: 0.7rem;
  font-weight: bold;
  line-height: 16px;
}

/* Side Panel */
.side-panel {
  position: absolute;
  left: 20px;
  top: 20px;
  width: 280px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  max-height: calc(100% - 40px);
  overflow-y: auto;
}

.side-panel h3 {
  margin: 0 0 20px;
  color: #1e293b;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat {
  text-align: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 6px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #3b82f6;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.8rem;
  color: #64748b;
}

.table-list {
  margin-bottom: 24px;
}

.table-list h4 {
  margin: 0 0 12px;
  color: #475569;
}

.table-list-item {
  padding: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.table-list-item:hover {
  background: #e2e8f0;
}

.table-list-item.active {
  background: #dbeafe;
  border-left: 3px solid #3b82f6;
}

.table-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.table-row-count {
  font-size: 0.8rem;
  color: #64748b;
}

.table-list-columns {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.column-tag {
  padding: 2px 6px;
  background: white;
  border-radius: 3px;
  font-size: 0.7rem;
  color: #475569;
}

.more-columns {
  font-size: 0.7rem;
  color: #94a3b8;
  align-self: center;
}

.export-options {
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.export-options h4 {
  margin: 0 0 12px;
  color: #475569;
}

.export-btn {
  width: 100%;
  padding: 8px;
  margin-bottom: 8px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
}

.export-btn:hover {
  background: #e2e8f0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  border-radius: 12px;
  overflow: hidden;
}

.modal-header {
  padding: 20px;
  background: #3b82f6;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(90vh - 70px);
}

.table-info {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.info-item {
  font-size: 0.9rem;
}

.columns-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.columns-table th {
  background: #f8fafc;
  padding: 12px;
  text-align: left;
  border-bottom: 2px solid #e2e8f0;
  color: #475569;
  font-weight: 600;
}

.columns-table td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.pk-badge, .fk-badge {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.7rem;
  font-weight: bold;
  margin-right: 6px;
}

.pk-badge {
  background: #dbeafe;
  color: #1e40af;
}

.fk-badge {
  background: #e0f2fe;
  color: #0c4a6e;
}

.constraint-chip {
  display: inline-block;
  padding: 2px 8px;
  background: #e2e8f0;
  border-radius: 12px;
  font-size: 0.8rem;
  margin-right: 4px;
}

.related-tables {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  margin-top: 20px;
}

.related-tables h4 {
  margin: 0 0 12px;
  color: #475569;
}

.related-tables ul {
  margin: 0;
  padding-left: 20px;
}

.related-tables li {
  margin-bottom: 8px;
  color: #64748b;
}

/* Arrowhead for relationship lines */
#arrowhead {
  fill: #4f46e5;
}
</style>