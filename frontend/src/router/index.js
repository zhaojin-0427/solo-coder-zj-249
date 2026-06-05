import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/checkin'
  },
  {
    path: '/checkin',
    name: 'CheckIn',
    component: () => import('@/views/CheckIn.vue')
  },
  {
    path: '/ammo-issue',
    name: 'AmmoIssue',
    component: () => import('@/views/AmmoIssue.vue')
  },
  {
    path: '/safety',
    name: 'Safety',
    component: () => import('@/views/Safety.vue')
  },
  {
    path: '/score',
    name: 'Score',
    component: () => import('@/views/Score.vue')
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('@/views/Statistics.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
