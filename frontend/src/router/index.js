import { createRouter, createWebHistory } from 'vue-router'

// Import views
import HomeView from '../views/HomeView.vue'
import DatabaseView from '../views/DatabaseView.vue'
import QueryView from '../views/QueryView.vue'
import DemoAppView from '../views/DemoAppView.vue'
import TestDashboard from '../views/TestDashboard.vue'
import SchemaVisualizer from '../views/SchemaVisualizer.vue'


const routes = [

   {
  path: '/tests',
  name: 'Tests',
  component: TestDashboard
}, 
  {

    
    path: '/',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/schema',
    name: 'Schema',
    component: SchemaVisualizer
  },
  {
    path: '/database',
    name: 'Database',
    component: DatabaseView
  },
  {
    path: '/query',
    name: 'Query',
    component: QueryView
  },
  {
    path: '/demo',
    name: 'Demo',
    component: DemoAppView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router