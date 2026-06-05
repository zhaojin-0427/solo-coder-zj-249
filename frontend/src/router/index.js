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
    path: '/training-plan',
    name: 'TrainingPlan',
    component: () => import('@/views/TrainingPlan.vue')
  },
  {
    path: '/lane-reservation',
    name: 'LaneReservation',
    component: () => import('@/views/LaneReservation.vue')
  },
  {
    path: '/ammo-issue',
    name: 'AmmoIssue',
    component: () => import('@/views/AmmoIssue.vue')
  },
  {
    path: '/ammo-batch',
    name: 'AmmoBatch',
    component: () => import('@/views/AmmoBatch.vue')
  },
  {
    path: '/safety',
    name: 'Safety',
    component: () => import('@/views/Safety.vue')
  },
  {
    path: '/violation-disposal',
    name: 'ViolationDisposal',
    component: () => import('@/views/ViolationDisposal.vue')
  },
  {
    path: '/risk-warning',
    name: 'RiskWarning',
    component: () => import('@/views/RiskWarning.vue')
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
