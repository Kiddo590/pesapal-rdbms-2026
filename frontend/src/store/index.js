import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    databaseConnected: false,
    currentDatabase: 'pesapal_demo',
    tables: [],
    queryHistory: [],
    darkMode: false,
  }),
  actions: {
    addToQueryHistory(query) {
      this.queryHistory.unshift({
        query,
        timestamp: new Date().toISOString(),
      })
      
      // Keep only last 20 queries
      if (this.queryHistory.length > 20) {
        this.queryHistory = this.queryHistory.slice(0, 20)
      }
      
      // Save to localStorage
      localStorage.setItem('queryHistory', JSON.stringify(this.queryHistory))
    },
    loadQueryHistory() {
      const saved = localStorage.getItem('queryHistory')
      if (saved) {
        this.queryHistory = JSON.parse(saved)
      }
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode
      if (this.darkMode) {
        document.documentElement.classList.add('dark')
      } else {
        document.documentElement.classList.remove('dark')
      }
    }
  }
})