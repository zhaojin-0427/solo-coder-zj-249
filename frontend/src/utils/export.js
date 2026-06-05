export const downloadFile = (response, filename) => {
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export const exportToCsv = (data, columns, filename) => {
  const header = columns.map(c => c.label).join(',')
  const rows = data.map(row => {
    return columns.map(col => {
      let value = row[col.prop]
      if (typeof value === 'string' && value.includes(',')) {
        value = `"${value}"`
      }
      return value || ''
    }).join(',')
  })
  const csv = [header, ...rows].join('\n')
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export default {
  downloadFile,
  exportToCsv
}
