<template>
  <div class="space-y-8">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Task Manager Demo</h1>
        <p class="text-gray-600">A practical CRUD application using the custom RDBMS</p>
      </div>
      <button @click="showCreateTask = true" class="btn-primary">
        + New Task
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card text-center">
        <div class="text-3xl font-bold text-blue-600">{{ stats.total || 0 }}</div>
        <div class="text-gray-600">Total Tasks</div>
      </div>
      <div class="card text-center">
        <div class="text-3xl font-bold text-green-600">{{ stats.completed || 0 }}</div>
        <div class="text-gray-600">Completed</div>
      </div>
      <div class="card text-center">
        <div class="text-3xl font-bold text-yellow-600">{{ stats.pending || 0 }}</div>
        <div class="text-gray-600">Pending</div>
      </div>
      <div class="card text-center">
        <div class="text-3xl font-bold text-purple-600">{{ stats.inProgress || 0 }}</div>
        <div class="text-gray-600">In Progress</div>
      </div>
    </div>

    <!-- Tasks List -->
    <div class="card">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-semibold">Tasks</h2>
        <div class="flex space-x-2">
          <button @click="filter = 'all'" :class="filter === 'all' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'"
                  class="px-3 py-1 rounded-lg text-sm">
            All
          </button>
          <button @click="filter = 'pending'" :class="filter === 'pending' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'"
                  class="px-3 py-1 rounded-lg text-sm">
            Pending
          </button>
          <button @click="filter = 'completed'" :class="filter === 'completed' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'"
                  class="px-3 py-1 rounded-lg text-sm">
            Completed
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600">Loading tasks...</p>
      </div>

      <div v-else-if="filteredTasks.length === 0" class="text-center py-8 text-gray-500">
        No tasks found. Create your first task!
      </div>

      <div v-else class="space-y-4">
        <div v-for="task in filteredTasks" :key="task.id"
             class="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center space-x-3">
                <input type="checkbox" :checked="task.completed" 
                       @change="toggleTask(task.id, !task.completed)"
                       class="h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                <h3 :class="{'line-through text-gray-500': task.completed}" class="font-medium text-lg">
                  {{ task.title }}
                </h3>
                <span :class="getPriorityClass(task.priority)"
                      class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ task.priority }}
                </span>
              </div>
              <p class="mt-2 text-gray-600">{{ task.description }}</p>
              <div class="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                <span>Created: {{ formatDate(task.created_at) }}</span>
                <span v-if="task.due_date">Due: {{ formatDate(task.due_date) }}</span>
              </div>
            </div>
            <div class="flex space-x-2">
              <button @click="editTask(task)" class="p-2 text-gray-500 hover:text-blue-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
              <button @click="deleteTask(task.id)" class="p-2 text-gray-500 hover:text-red-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Task Modal -->
    <div v-if="showCreateTask || editingTask" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg max-w-md w-full p-6">
        <h3 class="text-lg font-semibold mb-4">{{ editingTask ? 'Edit Task' : 'Create New Task' }}</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input v-model="newTask.title" type="text" class="input-field" placeholder="Task title" required>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="newTask.description" rows="3" class="input-field" placeholder="Task description"></textarea>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select v-model="newTask.priority" class="input-field">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select v-model="newTask.completed" class="input-field">
                <option :value="false">Pending</option>
                <option :value="true">Completed</option>
              </select>
            </div>
          </div>
          
          <div class="flex justify-end space-x-3 pt-4">
            <button @click="cancelTask" class="btn-secondary">
              Cancel
            </button>
            <button @click="saveTask" class="btn-primary">
              {{ editingTask ? 'Update' : 'Create' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../services/api'

const loading = ref(false)
const tasks = ref([])
const filter = ref('all')
const showCreateTask = ref(false)
const editingTask = ref(null)
const newTask = ref({
  title: '',
  description: '',
  priority: 'medium',
  completed: false
})
const stats = ref({
  total: 0,
  completed: 0,
  pending: 0,
  inProgress: 0
})

onMounted(() => {
  loadTasks()
})

const loadTasks = async () => {
  loading.value = true
  try {
    const data = await api.getDemoTasks()
    tasks.value = data.rows || []
    updateStats()
  } catch (error) {
    console.error('Error loading tasks:', error)
    // Fallback to demo data
    tasks.value = [
      { id: 1, title: 'Design database schema', description: 'Create RDBMS schema', priority: 'high', completed: true, created_at: new Date().toISOString() },
      { id: 2, title: 'Build API endpoints', description: 'Create REST API', priority: 'high', completed: false, created_at: new Date().toISOString() },
      { id: 3, title: 'Write documentation', description: 'Create user guide', priority: 'medium', completed: false, created_at: new Date().toISOString() }
    ]
    updateStats()
  } finally {
    loading.value = false
  }
}

const updateStats = () => {
  stats.value.total = tasks.value.length
  stats.value.completed = tasks.value.filter(t => t.completed).length
  stats.value.pending = tasks.value.filter(t => !t.completed).length
  stats.value.inProgress = 0 // This would come from a status field
}

const filteredTasks = computed(() => {
  if (filter.value === 'all') return tasks.value
  if (filter.value === 'completed') return tasks.value.filter(t => t.completed)
  if (filter.value === 'pending') return tasks.value.filter(t => !t.completed)
  return tasks.value
})

const getPriorityClass = (priority) => {
  switch (priority) {
    case 'high': return 'bg-red-100 text-red-800'
    case 'medium': return 'bg-yellow-100 text-yellow-800'
    case 'low': return 'bg-green-100 text-green-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const toggleTask = async (taskId, completed) => {
  try {
    await api.updateDemoTask(taskId, { completed })
    const task = tasks.value.find(t => t.id === taskId)
    if (task) {
      task.completed = completed
    }
    updateStats()
  } catch (error) {
    console.error('Error updating task:', error)
    alert('Failed to update task')
  }
}

const editTask = (task) => {
  editingTask.value = task.id
  newTask.value = {
    title: task.title,
    description: task.description || '',
    priority: task.priority || 'medium',
    completed: task.completed || false
  }
}

const deleteTask = async (taskId) => {
  if (!confirm('Are you sure you want to delete this task?')) return
  
  try {
    await api.deleteDemoTask(taskId)
    tasks.value = tasks.value.filter(t => t.id !== taskId)
    updateStats()
  } catch (error) {
    console.error('Error deleting task:', error)
    alert('Failed to delete task')
  }
}

const cancelTask = () => {
  showCreateTask.value = false
  editingTask.value = null
  resetNewTask()
}

const saveTask = async () => {
  if (!newTask.value.title.trim()) {
    alert('Please enter a task title')
    return
  }
  
  try {
    if (editingTask.value) {
      // Update existing task
      await api.updateDemoTask(editingTask.value, newTask.value)
      const task = tasks.value.find(t => t.id === editingTask.value)
      if (task) {
        Object.assign(task, newTask.value)
      }
    } else {
      // Create new task
      const response = await api.createDemoTask(newTask.value)
      const newTaskWithId = {
        id: response.row_id || Date.now(),
        ...newTask.value,
        created_at: new Date().toISOString()
      }
      tasks.value.push(newTaskWithId)
    }
    
    updateStats()
    cancelTask()
  } catch (error) {
    console.error('Error saving task:', error)
    alert('Failed to save task')
  }
}

const resetNewTask = () => {
  newTask.value = {
    title: '',
    description: '',
    priority: 'medium',
    completed: false
  }
}
</script>