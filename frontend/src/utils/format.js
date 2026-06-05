import dayjs from 'dayjs'

export const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

export const formatDateTime = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

export const formatTime = (date) => {
  if (!date) return '-'
  return dayjs(date).format('HH:mm')
}

export const formatMonth = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY年MM月')
}

export const formatShortDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('MM-DD')
}

export const isOverdue = (deadline) => {
  if (!deadline) return false
  return dayjs(deadline).isBefore(dayjs())
}

export const isExpiring = (date, months = 3) => {
  if (!date) return false
  return dayjs(date).diff(dayjs(), 'month') <= months
}

export const isDateInRange = (date, start, end) => {
  if (!date) return false
  const d = dayjs(date)
  return d.isAfter(dayjs(start).subtract(1, 'day')) && d.isBefore(dayjs(end).add(1, 'day'))
}

export const getDurationHours = (start, end) => {
  if (!start || !end) return 0
  return dayjs(end).diff(dayjs(start), 'hour', true)
}

export default {
  formatDate,
  formatDateTime,
  formatTime,
  formatMonth,
  formatShortDate,
  isOverdue,
  isExpiring,
  isDateInRange,
  getDurationHours
}
