<template>
  <div>
    <div class="page-title">
      <el-icon><DataAnalysis /></el-icon>
      数据统计分析
    </div>

    <div class="card-row">
      <div class="stat-card blue">
        <div class="stat-label">在册射手</div>
        <div class="stat-value">{{ overview.total_active_shooters }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">今日签到</div>
        <div class="stat-value">{{ overview.today_checkins }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">今日领用弹药</div>
        <div class="stat-value">{{ overview.today_ammo_issued }}发</div>
      </div>
      <div class="stat-card red">
        <div class="stat-label">近期违规</div>
        <div class="stat-value">{{ overview.recent_violations }}次</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">进行中训练</div>
        <div class="stat-value">{{ overview.active_sessions }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">30天平均成绩</div>
        <div class="stat-value">{{ overview.avg_score_30d }}环</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">弹药总库存</div>
        <div class="stat-value">{{ overview.total_ammo_stock }}发</div>
      </div>
    </div>

    <div class="page-container">
      <el-row :gutter="24">
        <el-col :span="12">
          <div class="section-title">
            <el-icon><TrendCharts /></el-icon>
            近30天弹药消耗趋势
          </div>
          <div ref="ammoTrendChart" class="chart-container"></div>
        </el-col>
        <el-col :span="12">
          <div class="section-title">
            <el-icon><Histogram /></el-icon>
            各靶道使用率统计
          </div>
          <div ref="laneUsageChart" class="chart-container"></div>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <div class="section-title">
            <el-icon><PieChart /></el-icon>
            安全违规等级分布
          </div>
          <div ref="violationChart" class="chart-container"></div>
        </el-col>
        <el-col :span="12">
          <div class="section-title">
            <el-icon><Trophy /></el-icon>
            射手出勤频次排行
          </div>
          <div ref="attendanceChart" class="chart-container"></div>
        </el-col>
      </el-row>

      <el-row :gutter="24">
        <el-col :span="12">
          <div class="section-title">
            <el-icon><TrendCharts /></el-icon>
            近一年弹药领用月度趋势
          </div>
          <div ref="monthlyAmmoChart" class="chart-container"></div>
        </el-col>
        <el-col :span="12">
          <div class="section-title">
            <el-icon><Warning /></el-icon>
            违规类型统计 TOP 5
          </div>
          <div ref="violationTypeChart" class="chart-container"></div>
        </el-col>
      </el-row>

      <el-divider content-position="left">详细数据表格</el-divider>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="靶道使用详情" name="lanes">
          <el-table :data="laneUsage" style="width: 100%">
            <el-table-column prop="lane_number" label="靶道编号" width="120" align="center" />
            <el-table-column prop="name" label="靶道名称" />
            <el-table-column prop="distance" label="射击距离(米)" width="140" align="center" />
            <el-table-column prop="usage_count" label="近30天使用次数" width="160" align="center">
              <template #default="{ row }">
                <el-tag type="primary" effect="dark">{{ row.usage_count }}次</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="使用率" width="160">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round((row.usage_count / maxLaneUsage) * 100)"
                  :color="getUsageColor(row.usage_count, maxLaneUsage)"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="射手出勤排行" name="attendance">
          <el-table :data="shooterAttendance" style="width: 100%">
            <el-table-column label="排名" width="80" align="center">
              <template #default="{ $index }">
                <el-tag
                  :type="$index < 3 ? 'warning' : 'info'"
                  effect="dark"
                  size="large"
                >
                  {{ $index + 1 }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="射手" width="120">
              <template #default="{ row }">
                {{ row.shooter__name }}
              </template>
            </el-table-column>
            <el-table-column prop="shooter__unit" label="所属单位" />
            <el-table-column prop="attendance_count" label="近30天出勤次数" width="160" align="center">
              <template #default="{ row }">
                <el-tag type="success" effect="dark">{{ row.attendance_count }}次</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="出勤率" width="160">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round((row.attendance_count / maxAttendance) * 100)"
                  color="#67c23a"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="违规记录统计" name="violations">
          <el-table :data="violationTypes" style="width: 100%">
            <el-table-column label="排名" width="80" align="center">
              <template #default="{ $index }">
                <el-tag
                  :type="$index === 0 ? 'danger' : $index < 3 ? 'warning' : 'info'"
                  effect="dark"
                  size="large"
                >
                  {{ $index + 1 }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="violation_type" label="违规类型" />
            <el-table-column prop="count" label="违规次数" width="160" align="center">
              <template #default="{ row }">
                <el-tag :type="row.count > 5 ? 'danger' : 'warning'" effect="dark">
                  {{ row.count }}次
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="占比" width="200">
              <template #default="{ row }">
                <el-progress
                  :percentage="totalViolations > 0 ? Math.round((row.count / totalViolations) * 100) : 0"
                  :color="row.count > 5 ? '#f56c6c' : '#e6a23c'"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div style="text-align: center; margin-top: 24px">
      <el-button type="primary" size="large" @click="refreshData" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
      <span style="margin-left: 16px; color: #909399; font-size: 12px">
        数据更新时间: {{ lastUpdateTime }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { statisticsApi } from '@/api'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const loading = ref(false)
const activeTab = ref('lanes')
const lastUpdateTime = ref('-')

const ammoTrendChart = ref(null)
const laneUsageChart = ref(null)
const violationChart = ref(null)
const attendanceChart = ref(null)
const monthlyAmmoChart = ref(null)
const violationTypeChart = ref(null)

let ammoTrendChartInstance = null
let laneUsageChartInstance = null
let violationChartInstance = null
let attendanceChartInstance = null
let monthlyAmmoChartInstance = null
let violationTypeChartInstance = null

const overview = reactive({
  total_active_shooters: 0,
  today_checkins: 0,
  today_ammo_issued: 0,
  recent_violations: 0,
  active_sessions: 0,
  avg_score_30d: 0,
  total_ammo_stock: 0
})

const laneUsage = ref([])
const ammoTrend = ref([])
const ammoMonthly = ref([])
const violationStats = ref([])
const shooterAttendance = ref([])
const violationTypes = ref([])

const maxLaneUsage = computed(() => {
  if (laneUsage.value.length === 0) return 1
  return Math.max(...laneUsage.value.map(l => l.usage_count), 1)
})

const maxAttendance = computed(() => {
  if (shooterAttendance.value.length === 0) return 1
  return Math.max(...shooterAttendance.value.map(s => s.attendance_count), 1)
})

const totalViolations = computed(() => {
  return violationTypes.value.reduce((sum, v) => sum + v.count, 0)
})

const getUsageColor = (value, max) => {
  const percent = value / max
  if (percent >= 0.8) return '#f56c6c'
  if (percent >= 0.5) return '#e6a23c'
  return '#67c23a'
}

const initCharts = () => {
  if (ammoTrendChart.value) {
    ammoTrendChartInstance = echarts.init(ammoTrendChart.value)
  }
  if (laneUsageChart.value) {
    laneUsageChartInstance = echarts.init(laneUsageChart.value)
  }
  if (violationChart.value) {
    violationChartInstance = echarts.init(violationChart.value)
  }
  if (attendanceChart.value) {
    attendanceChartInstance = echarts.init(attendanceChart.value)
  }
  if (monthlyAmmoChart.value) {
    monthlyAmmoChartInstance = echarts.init(monthlyAmmoChart.value)
  }
  if (violationTypeChart.value) {
    violationTypeChartInstance = echarts.init(violationTypeChart.value)
  }
}

const renderAmmoTrendChart = () => {
  if (!ammoTrendChartInstance) return

  const dates = ammoTrend.value.map(item => dayjs(item.date).format('MM-DD'))
  const issued = ammoTrend.value.map(item => item.total_issued || 0)
  const consumed = ammoTrend.value.map(item => item.total_consumed || 0)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['领用数量', '消耗数量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '发'
    },
    series: [
      {
        name: '领用数量',
        type: 'line',
        smooth: true,
        data: issued,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        lineStyle: {
          color: '#409EFF',
          width: 2
        },
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '消耗数量',
        type: 'line',
        smooth: true,
        data: consumed,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        },
        lineStyle: {
          color: '#67c23a',
          width: 2
        },
        itemStyle: {
          color: '#67c23a'
        }
      }
    ]
  }

  ammoTrendChartInstance.setOption(option)
}

const renderLaneUsageChart = () => {
  if (!laneUsageChartInstance) return

  const laneNames = laneUsage.value.map(l => `${l.lane_number}号`)
  const usageCounts = laneUsage.value.map(l => l.usage_count)
  const colors = usageCounts.map(count => {
    const max = Math.max(...usageCounts, 1)
    const percent = count / max
    if (percent >= 0.8) return '#f56c6c'
    if (percent >= 0.5) return '#e6a23c'
    return '#67c23a'
  })

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: laneNames,
      axisLabel: {
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '使用次数'
    },
    series: [
      {
        type: 'bar',
        data: usageCounts.map((value, index) => ({
          value,
          itemStyle: {
            color: colors[index],
            borderRadius: [4, 4, 0, 0]
          }
        })),
        barWidth: '50%',
        label: {
          show: true,
          position: 'top',
          formatter: '{c}次'
        }
      }
    ]
  }

  laneUsageChartInstance.setOption(option)
}

const renderViolationChart = () => {
  if (!violationChartInstance) return

  const levelMap = {
    none: '无违规',
    minor: '轻微违规',
    major: '严重违规',
    critical: '重大违规'
  }

  const colorMap = {
    none: '#67c23a',
    minor: '#e6a23c',
    major: '#f56c6c',
    critical: '#c0392b'
  }

  const data = violationStats.value.map(item => ({
    value: item.count,
    name: levelMap[item.violation_level] || item.violation_level,
    itemStyle: {
      color: colorMap[item.violation_level] || '#909399'
    }
  })).filter(item => item.value > 0)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}次 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {c}次'
        },
        labelLine: {
          show: true
        },
        data: data
      }
    ]
  }

  violationChartInstance.setOption(option)
}

const renderAttendanceChart = () => {
  if (!attendanceChartInstance) return

  const names = shooterAttendance.value.map(s => s.shooter__name).reverse()
  const counts = shooterAttendance.value.map(s => s.attendance_count).reverse()

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '出勤次数'
    },
    yAxis: {
      type: 'category',
      data: names
    },
    series: [
      {
        type: 'bar',
        data: counts,
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}次'
        }
      }
    ]
  }

  attendanceChartInstance.setOption(option)
}

const renderMonthlyAmmoChart = () => {
  if (!monthlyAmmoChartInstance) return

  const months = ammoMonthly.value.map(item => dayjs(item.month).format('YYYY年MM月'))
  const totals = ammoMonthly.value.map(item => item.total || 0)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: months,
      axisLabel: {
        rotate: 30,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      name: '发'
    },
    series: [
      {
        type: 'bar',
        data: totals,
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(250, 112, 154, 0.9)' },
            { offset: 1, color: 'rgba(254, 225, 64, 0.9)' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        }
      }
    ]
  }

  monthlyAmmoChartInstance.setOption(option)
}

const renderViolationTypeChart = () => {
  if (!violationTypeChartInstance) return

  const types = violationTypes.value.map(v => v.violation_type)
  const counts = violationTypes.value.map(v => v.count)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '次数'
    },
    yAxis: {
      type: 'category',
      data: types.reverse()
    },
    series: [
      {
        type: 'bar',
        data: counts.reverse(),
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#f56c6c' },
            { offset: 1, color: '#e6a23c' }
          ]),
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}次'
        }
      }
    ]
  }

  violationTypeChartInstance.setOption(option)
}

const loadStatistics = async () => {
  try {
    loading.value = true
    const res = await statisticsApi.dashboard()
    const data = res.data

    Object.assign(overview, data.overview)
    laneUsage.value = data.lane_usage || []
    ammoTrend.value = data.ammo_trend || []
    ammoMonthly.value = data.ammo_monthly || []
    violationStats.value = data.violation_stats || []
    shooterAttendance.value = data.shooter_attendance || []
    violationTypes.value = data.violation_types || []

    lastUpdateTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')

    await nextTick()
    renderAllCharts()
  } catch (e) {
    console.error(e)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

const renderAllCharts = () => {
  renderAmmoTrendChart()
  renderLaneUsageChart()
  renderViolationChart()
  renderAttendanceChart()
  renderMonthlyAmmoChart()
  renderViolationTypeChart()
}

const refreshData = () => {
  loadStatistics()
  ElMessage.success('数据已刷新')
}

const handleResize = () => {
  ammoTrendChartInstance?.resize()
  laneUsageChartInstance?.resize()
  violationChartInstance?.resize()
  attendanceChartInstance?.resize()
  monthlyAmmoChartInstance?.resize()
  violationTypeChartInstance?.resize()
}

onMounted(async () => {
  await nextTick()
  initCharts()
  loadStatistics()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  ammoTrendChartInstance?.dispose()
  laneUsageChartInstance?.dispose()
  violationChartInstance?.dispose()
  attendanceChartInstance?.dispose()
  monthlyAmmoChartInstance?.dispose()
  violationTypeChartInstance?.dispose()
})
</script>
