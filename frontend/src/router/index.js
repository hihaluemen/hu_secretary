import { createRouter, createWebHistory } from 'vue-router'

import DemoDashboard from '../views/DemoDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: DemoDashboard,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

