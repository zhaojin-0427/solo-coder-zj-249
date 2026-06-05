import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000
})

request.interceptors.response.use(
  (response) => response,
  (error) => {
    ElMessage.error(error.response?.data?.error || '请求失败，请稍后重试')
    return Promise.reject(error)
  }
)

export const shootersApi = {
  list: (params) => request.get('/shooters/', { params }),
  create: (data) => request.post('/shooters/', data),
  update: (id, data) => request.put(`/shooters/${id}/`, data),
  delete: (id) => request.delete(`/shooters/${id}/`)
}

export const checkInApi = {
  list: (params) => request.get('/check-ins/', { params }),
  create: (data) => request.post('/check-ins/', data),
  update: (id, data) => request.put(`/check-ins/${id}/`, data)
}

export const ammunitionApi = {
  list: (params) => request.get('/ammunitions/', { params }),
  create: (data) => request.post('/ammunitions/', data),
  update: (id, data) => request.put(`/ammunitions/${id}/`, data)
}

export const firearmApi = {
  list: (params) => request.get('/firearms/', { params }),
  create: (data) => request.post('/firearms/', data),
  update: (id, data) => request.put(`/firearms/${id}/`, data)
}

export const targetLaneApi = {
  list: (params) => request.get('/target-lanes/', { params }),
  create: (data) => request.post('/target-lanes/', data),
  update: (id, data) => request.put(`/target-lanes/${id}/`, data)
}

export const ammoIssueApi = {
  list: (params) => request.get('/ammo-issues/', { params }),
  create: (data) => request.post('/ammo-issues/', data),
  update: (id, data) => request.put(`/ammo-issues/${id}/`, data)
}

export const safetyInspectionApi = {
  list: (params) => request.get('/safety-inspections/', { params }),
  create: (data) => request.post('/safety-inspections/', data),
  update: (id, data) => request.put(`/safety-inspections/${id}/`, data)
}

export const scoreRecordApi = {
  list: (params) => request.get('/score-records/', { params }),
  create: (data) => request.post('/score-records/', data),
  update: (id, data) => request.put(`/score-records/${id}/`, data)
}

export const ammoReturnApi = {
  list: (params) => request.get('/ammo-returns/', { params }),
  create: (data) => request.post('/ammo-returns/', data)
}

export const statisticsApi = {
  dashboard: () => request.get('/statistics/'),
  advanced: () => request.get('/advanced-statistics/')
}

export const ammoBatchApi = {
  list: (params) => request.get('/ammo-batches/', { params }),
  create: (data) => request.post('/ammo-batches/', data),
  update: (id, data) => request.put(`/ammo-batches/${id}/`, data),
  delete: (id) => request.delete(`/ammo-batches/${id}/`),
  export: (params) => request.get('/ammo-batches/export/', { params, responseType: 'blob' })
}

export const trainingPlanApi = {
  list: (params) => request.get('/training-plans/', { params }),
  create: (data) => request.post('/training-plans/', data),
  update: (id, data) => request.put(`/training-plans/${id}/`, data),
  delete: (id) => request.delete(`/training-plans/${id}/`),
  generateSchedules: (id) => request.post(`/training-plans/${id}/generate-schedules/`),
  export: (params) => request.get('/training-plans/export/', { params, responseType: 'blob' })
}

export const trainingScheduleApi = {
  list: (params) => request.get('/training-schedules/', { params }),
  create: (data) => request.post('/training-schedules/', data),
  update: (id, data) => request.put(`/training-schedules/${id}/`, data),
  delete: (id) => request.delete(`/training-schedules/${id}/`),
  export: (params) => request.get('/training-schedules/export/', { params, responseType: 'blob' })
}

export const laneReservationApi = {
  list: (params) => request.get('/lane-reservations/', { params }),
  create: (data) => request.post('/lane-reservations/', data),
  update: (id, data) => request.put(`/lane-reservations/${id}/`, data),
  delete: (id) => request.delete(`/lane-reservations/${id}/`),
  export: (params) => request.get('/lane-reservations/export/', { params, responseType: 'blob' })
}

export const riskWarningApi = {
  list: (params) => request.get('/risk-warnings/', { params }),
  update: (id, data) => request.put(`/risk-warnings/${id}/`, data),
  export: (params) => request.get('/risk-warnings/export/', { params, responseType: 'blob' })
}

export const violationDisposalApi = {
  list: (params) => request.get('/violation-disposals/', { params }),
  update: (id, data) => request.put(`/violation-disposals/${id}/`, data),
  export: (params) => request.get('/violation-disposals/export/', { params, responseType: 'blob' })
}

export const ammoBatchFlowApi = {
  list: (params) => request.get('/ammo-batch-flows/', { params }),
  export: (params) => request.get('/ammo-batch-flows/export/', { params, responseType: 'blob' })
}

export const scheduleRecommendationApi = {
  generate: (planId) => request.get('/generate-schedule-recommendations/', { params: { plan_id: planId } })
}

export default request
