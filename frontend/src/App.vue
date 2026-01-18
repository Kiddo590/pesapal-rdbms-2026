<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-md border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0 flex items-center">
              <div class="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold">DB</span>
              </div>
              <span class="ml-3 text-xl font-bold text-gray-900">
                Pesapal RDBMS
              </span>
              <span class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                Challenge 2026
              </span>
            </div>
            <div class="hidden sm:ml-10 sm:flex sm:space-x-8">
              <router-link 
                to="/" 
                class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                :class="{'bg-blue-100 text-blue-700': $route.name === 'Home', 'text-gray-700 hover:bg-gray-100 hover:text-gray-900': $route.name !== 'Home'}">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Dashboard
              </router-link>
              <router-link 
                to="/database" 
                class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                :class="{'bg-blue-100 text-blue-700': $route.name === 'Database', 'text-gray-700 hover:bg-gray-100 hover:text-gray-900': $route.name !== 'Database'}">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                Database Explorer
              </router-link>
              <router-link 
  to="/schema" 
  class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
  :class="{'bg-blue-100 text-blue-700': $route.name === 'Schema', 'text-gray-700 hover:bg-gray-100 hover:text-gray-900': $route.name !== 'Schema'}">
  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
  </svg>
  Schema Visualizer
</router-link>
              <router-link 
                to="/query" 
                class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                :class="{'bg-blue-100 text-blue-700': $route.name === 'Query', 'text-gray-700 hover:bg-gray-100 hover:text-gray-900': $route.name !== 'Query'}">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                Query Editor
              </router-link>
              <router-link 
                to="/demo" 
                class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                :class="{'bg-blue-100 text-blue-700': $route.name === 'Demo', 'text-gray-700 hover:bg-gray-100 hover:text-gray-900': $route.name !== 'Demo'}">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Demo App
              </router-link>
              
              <router-link 
                to="/tests" 
                class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors"
                :class="{'bg-blue-100 text-blue-700': $route.name === 'Tests', 'text-gray-700 hover:bg-gray-100 hover:text-gray-900': $route.name !== 'Tests'}">
                <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                
              </router-link>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <div :class="`w-2 h-2 rounded-full ${databaseConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`"></div>
              <span class="text-sm text-gray-600">{{ databaseConnected ? 'Connected' : 'Disconnected' }}</span>
            </div>
            <button @click="toggleDarkMode" class="p-2 rounded-lg bg-gray-100 hover:bg-gray-200">
              <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t mt-12">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <div class="text-sm text-gray-500">
            <p>Pesapal Junior Dev Challenge 2026 • Custom RDBMS Implementation</p>
            <p class="mt-1">Built with Vue.js, Tailwind CSS, and Python</p>
          </div>
          <div class="flex space-x-6">
            <a href="http://localhost:8000/docs" target="_blank" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </a>
            <a href="https://github.com" target="_blank" class="text-gray-400 hover:text-gray-500">
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from './services/api'
import { useAppStore } from './store/index'

const router = useRouter()
const appStore = useAppStore()
const databaseConnected = ref(false)

onMounted(async () => {
  // Load query history
  appStore.loadQueryHistory()
  
  // Check database connection
  try {
    const health = await api.getHealth()
    databaseConnected.value = health.status === 'healthy'
    appStore.databaseConnected = databaseConnected.value
  } catch (error) {
    console.error('Database connection error:', error)
    databaseConnected.value = false
  }
})

const toggleDarkMode = () => {
  appStore.toggleDarkMode()
}
</script>