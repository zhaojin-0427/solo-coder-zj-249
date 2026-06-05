const FIELD_MAPPINGS = {
  trainingPlan: {
    plan_type: {
      frontend: ['basic', 'advanced', 'assessment', 'emergency', 'special'],
      backend: ['basic', 'advanced', 'assessment', 'emergency', 'special'],
      displayMap: {
        basic: '基础训练',
        advanced: '进阶训练',
        assessment: '考核评估',
        emergency: '应急训练',
        special: '专项训练'
      }
    },
    status: {
      frontend: ['draft', 'approved', 'in_progress', 'completed', 'cancelled'],
      backend: ['draft', 'approved', 'in_progress', 'completed', 'cancelled'],
      displayMap: {
        draft: '草稿',
        approved: '已批准',
        in_progress: '进行中',
        completed: '已完成',
        cancelled: '已取消'
      }
    }
  },
  trainingSchedule: {
    status: {
      frontend: ['pending', 'scheduled', 'checked_in', 'in_progress', 'completed', 'cancelled', 'no_show'],
      backend: ['pending', 'checked_in', 'in_progress', 'completed', 'cancelled', 'no_show'],
      displayMap: {
        pending: '待签到',
        scheduled: '待签到',
        checked_in: '已签到',
        in_progress: '进行中',
        completed: '已完成',
        cancelled: '已取消',
        no_show: '未出席'
      }
    }
  },
  riskWarning: {
    warning_type: {
      frontend: ['ammo_stock', 'ammo_expiry', 'lane_conflict', 'shooter_risk', 'firearm_maintenance', 'violation_risk', 'other'],
      backend: ['ammo_stock', 'ammo_expiry', 'lane_conflict', 'shooter_risk', 'firearm_maintenance', 'violation_risk', 'other'],
      displayMap: {
        ammo_stock: '弹药库存预警',
        ammo_expiry: '弹药过期预警',
        lane_conflict: '靶道冲突预警',
        shooter_risk: '射手风险预警',
        firearm_maintenance: '枪械维护预警',
        violation_risk: '违规风险预警',
        other: '其他预警'
      }
    },
    warning_level: {
      frontend: ['low', 'medium', 'high', 'critical'],
      backend: ['low', 'medium', 'high', 'critical'],
      displayMap: {
        low: '低风险',
        medium: '中风险',
        high: '高风险',
        critical: '严重风险'
      }
    },
    status: {
      frontend: ['pending', 'processing', 'resolved', 'ignored'],
      backend: ['pending', 'processing', 'resolved', 'ignored'],
      displayMap: {
        pending: '待处理',
        processing: '处理中',
        resolved: '已解决',
        ignored: '已忽略'
      }
    }
  },
  laneReservation: {
    status: {
      frontend: ['pending', 'confirmed', 'in_use', 'completed', 'cancelled', 'no_show', 'conflict'],
      backend: ['pending', 'confirmed', 'in_use', 'completed', 'cancelled', 'no_show'],
      displayMap: {
        pending: '待确认',
        confirmed: '已确认',
        in_use: '使用中',
        completed: '已完成',
        cancelled: '已取消',
        no_show: '未到',
        conflict: '已冲突'
      }
    }
  },
  ammoBatch: {
    quality_status: {
      frontend: ['normal', 'in_stock', 'partial', 'warning', 'expired', 'damaged', 'scrapped'],
      backend: ['normal', 'warning', 'expired', 'damaged'],
      displayMap: {
        normal: '正常',
        in_stock: '在库',
        partial: '部分使用',
        warning: '预警',
        expired: '已过期',
        damaged: '破损',
        scrapped: '已报废',
        exhausted: '已用完'
      }
    }
  }
}

export const normalizeField = (module, fieldName, value, direction = 'toFrontend') => {
  const mapping = FIELD_MAPPINGS[module]?.[fieldName]
  if (!mapping) return value

  if (direction === 'toFrontend') {
    if (value === 'scheduled' && fieldName === 'status') return 'pending'
    if (value === 'exam' && fieldName === 'plan_type') return 'assessment'
    return value
  } else {
    if (value === 'scheduled' && fieldName === 'status') return 'pending'
    if (value === 'exam' && fieldName === 'plan_type') return 'assessment'
    return value
  }
}

export const getDisplayValue = (module, fieldName, value) => {
  const mapping = FIELD_MAPPINGS[module]?.[fieldName]
  if (!mapping?.displayMap) return value
  return mapping.displayMap[value] || value
}

export const getFilterOptions = (module, fieldName) => {
  const mapping = FIELD_MAPPINGS[module]?.[fieldName]
  if (!mapping?.displayMap) return []
  return Object.entries(mapping.displayMap).map(([value, label]) => ({ value, label }))
}

export const adaptTrainingPlan = (data) => {
  if (!data) return data
  return {
    ...data,
    plan_type: normalizeField('trainingPlan', 'plan_type', data.plan_type),
    status: normalizeField('trainingPlan', 'status', data.status),
    plan_type_display: data.plan_type_display || getDisplayValue('trainingPlan', 'plan_type', data.plan_type),
    status_display: data.status_display || getDisplayValue('trainingPlan', 'status', data.status)
  }
}

export const adaptTrainingSchedule = (data) => {
  if (!data) return data
  return {
    ...data,
    status: normalizeField('trainingSchedule', 'status', data.status),
    status_display: data.status_display || getDisplayValue('trainingSchedule', 'status', data.status),
    actual_rounds: data.actual_rounds ?? data.used_rounds,
    has_conflict: data.has_conflict ?? data.conflict_warning
  }
}

export const adaptRiskWarning = (data) => {
  if (!data) return data
  return {
    ...data,
    warning_type: normalizeField('riskWarning', 'warning_type', data.warning_type),
    warning_level: normalizeField('riskWarning', 'warning_level', data.warning_level),
    status: normalizeField('riskWarning', 'status', data.status),
    warning_type_display: data.warning_type_display || getDisplayValue('riskWarning', 'warning_type', data.warning_type),
    warning_level_display: data.warning_level_display || getDisplayValue('riskWarning', 'warning_level', data.warning_level),
    status_display: data.status_display || getDisplayValue('riskWarning', 'status', data.status),
    created_at: data.created_at || data.create_time,
    handled_by: data.handled_by || data.handler,
    handle_time: data.handle_time
  }
}

export const adaptLaneReservation = (data) => {
  if (!data) return data
  return {
    ...data,
    status: normalizeField('laneReservation', 'status', data.status),
    status_display: data.status_display || getDisplayValue('laneReservation', 'status', data.status),
    has_conflict: data.has_conflict ?? data.conflict_detected,
    training_plan_info: data.training_plan_info
  }
}

export const adaptAmmoBatch = (data) => {
  if (!data) return data
  let derivedStatus = data.quality_status
  if (data.current_quantity === 0 && data.quality_status === 'normal') {
    derivedStatus = 'exhausted'
  } else if (data.current_quantity > 0 && data.current_quantity < (data.initial_quantity || 0) && data.quality_status === 'normal') {
    derivedStatus = 'partial'
  } else if (data.current_quantity === (data.initial_quantity || 0) && data.quality_status === 'normal') {
    derivedStatus = 'in_stock'
  }
  return {
    ...data,
    quality_status: normalizeField('ammoBatch', 'quality_status', derivedStatus),
    quality_status_display: data.quality_status_display || getDisplayValue('ammoBatch', 'quality_status', derivedStatus),
    supplier: data.supplier || data.manufacturer
  }
}

export const adaptAmmoBatchFlow = (data) => {
  if (!data) return data
  return {
    ...data,
    operation_time: data.operation_time || data.create_time,
    related_record: data.related_record,
    related_record_type: data.related_record_type
  }
}

export const adaptList = (data, adapterFn) => {
  if (!data) return data
  if (Array.isArray(data)) {
    return data.map(item => adapterFn(item))
  }
  if (data.results && Array.isArray(data.results)) {
    return {
      ...data,
      results: data.results.map(item => adapterFn(item))
    }
  }
  return adapterFn(data)
}

export const adaptPaginatedResponse = (response, adapterFn) => {
  if (!response?.data) return response
  const data = response.data
  if (data.results && Array.isArray(data.results)) {
    return {
      ...response,
      data: {
        ...data,
        results: data.results.map(item => adapterFn(item))
      }
    }
  }
  if (Array.isArray(data)) {
    return {
      ...response,
      data: data.map(item => adapterFn(item))
    }
  }
  return {
    ...response,
    data: adapterFn(data)
  }
}

export const buildFilterParams = (filters, fieldMap = {}) => {
  const params = {}
  Object.entries(filters).forEach(([key, value]) => {
    if (value === '' || value === null || value === undefined) return
    if (Array.isArray(value) && value.length === 0) return

    const mappedKey = fieldMap[key] || key

    if (key === 'date_range' && Array.isArray(value) && value.length === 2) {
      const [start, end] = value
      if (start) params[`${mappedKey}__gte`] = start
      if (end) params[`${mappedKey}__lte`] = end
      return
    }

    if (key === 'date' && Array.isArray(value) && value.length === 2) {
      const [start, end] = value
      if (start) params[`${mappedKey}__gte`] = start
      if (end) params[`${mappedKey}__lte`] = end
      return
    }

    params[mappedKey] = value
  })
  return params
}

export const buildPaginationParams = (pagination) => {
  return {
    page: pagination.page,
    page_size: pagination.size
  }
}

export default {
  normalizeField,
  getDisplayValue,
  getFilterOptions,
  adaptTrainingPlan,
  adaptTrainingSchedule,
  adaptRiskWarning,
  adaptLaneReservation,
  adaptAmmoBatch,
  adaptAmmoBatchFlow,
  adaptList,
  adaptPaginatedResponse,
  buildFilterParams,
  buildPaginationParams
}
