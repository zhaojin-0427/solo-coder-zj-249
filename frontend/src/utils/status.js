export const getPlanStatusType = (status) => {
  const map = {
    draft: 'info',
    approved: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

export const getScheduleStatusType = (status) => {
  const map = {
    pending: 'info',
    scheduled: 'info',
    checked_in: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger',
    no_show: 'danger'
  }
  return map[status] || 'info'
}

export const getRiskLevelType = (level) => {
  const map = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return map[level] || 'info'
}

export const getRiskLevelText = (level) => {
  const map = {
    critical: '极高',
    high: '高',
    medium: '中',
    low: '低'
  }
  return map[level] || level
}

export const getRiskTypeColor = (type) => {
  const map = {
    ammo_stock: 'warning',
    ammo_expiry: 'danger',
    lane_conflict: 'danger',
    shooter_risk: 'warning',
    firearm_status: 'primary',
    firearm_maintenance: 'primary',
    violation_risk: 'danger',
    violation: 'danger',
    safety_threshold: 'warning',
    other: 'info'
  }
  return map[type] || 'info'
}

export const getRiskStatusType = (status) => {
  const map = {
    pending: 'warning',
    processing: 'primary',
    resolved: 'success',
    ignored: 'info'
  }
  return map[status] || 'info'
}

export const getReservationStatusType = (status) => {
  const map = {
    pending: 'warning',
    confirmed: 'primary',
    in_use: 'warning',
    completed: 'success',
    cancelled: 'info',
    no_show: 'danger',
    conflict: 'danger'
  }
  return map[status] || 'info'
}

export const getBatchStatusType = (status) => {
  const map = {
    normal: 'success',
    in_stock: 'success',
    partial: 'warning',
    exhausted: 'info',
    warning: 'warning',
    expired: 'danger',
    damaged: 'danger',
    scrapped: 'danger'
  }
  return map[status] || 'info'
}

export const getFlowType = (type) => {
  const map = {
    in: 'success',
    out: 'warning',
    issue: 'primary',
    return: 'info',
    consume: 'danger',
    adjust: 'warning',
    scrap: 'danger'
  }
  return map[type] || 'primary'
}

export const getFlowColor = (type) => {
  const map = {
    in: '#67c23a',
    out: '#e6a23c',
    issue: '#409EFF',
    return: '#909399',
    consume: '#f56c6c',
    adjust: '#e6a23c',
    scrap: '#c0392b'
  }
  return map[type] || '#409EFF'
}

export const getViolationLevelType = (level) => {
  const map = {
    none: 'success',
    minor: 'warning',
    major: 'danger',
    critical: 'danger'
  }
  return map[level] || 'info'
}

export const getDisposalStatusType = (status) => {
  const map = {
    pending: 'warning',
    notified: 'primary',
    confirmed: 'primary',
    rectified: 'warning',
    verified: 'primary',
    closed: 'success'
  }
  return map[status] || 'info'
}

export const getMatchColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

export const getUsageColor = (value, max) => {
  const percent = value / max
  if (percent >= 0.8) return '#f56c6c'
  if (percent >= 0.5) return '#e6a23c'
  return '#67c23a'
}

export const getConflictRateColor = (rate) => {
  if (rate >= 20) return '#f56c6c'
  if (rate >= 10) return '#e6a23c'
  return '#67c23a'
}

export default {
  getPlanStatusType,
  getScheduleStatusType,
  getRiskLevelType,
  getRiskLevelText,
  getRiskTypeColor,
  getRiskStatusType,
  getReservationStatusType,
  getBatchStatusType,
  getFlowType,
  getFlowColor,
  getViolationLevelType,
  getDisposalStatusType,
  getMatchColor,
  getUsageColor,
  getConflictRateColor
}
