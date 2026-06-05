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
      <el-tabs v-model="activeMainTab">
        <el-tab-pane label="基础统计" name="basic">
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
        </el-tab-pane>

        <el-tab-pane label="高级分析" name="advanced">
          <el-row :gutter="24">
            <el-col :span="24">
              <div class="section-title">
                <el-icon><Calendar /></el-icon>
                训练计划完成率
              </div>
              <div ref="planCompletionChart" class="chart-container"></div>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <div class="section-title">
                <el-icon><Tickets /></el-icon>
                靶道冲突率趋势
              </div>
              <div ref="laneConflictChart" class="chart-container"></div>
            </el-col>
            <el-col :span="12">
              <div class="section-title">
                <el-icon><CircleCheck /></el-icon>
                总体冲突率
              </div>
              <div ref="conflictGaugeChart" class="chart-container"></div>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <div class="section-title">
                <el-icon><Coin /></el-icon>
                弹药批次流向分布
              </div>
              <div ref="batchFlowChart" class="chart-container"></div>
            </el-col>
            <el-col :span="12">
              <div class="section-title">
                <el-icon><Histogram /></el-icon>
                弹药批次使用 TOP 10
              </div>
              <div ref="batchUsageChart" class="chart-container"></div>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="24">
              <div class="section-title">
                <el-icon><WarningFilled /></el-icon>
                风险射手排行 TOP 10
              </div>
              <div ref="riskShooterChart" class="chart-container"></div>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <div class="section-title">
                <el-icon><TrendCharts /></el-icon>
                违规闭环时效趋势
              </div>
              <div ref="closureTrendChart" class="chart-container"></div>
            </el-col>
            <el-col :span="12">
              <div class="section-title">
                <el-icon><DataLine /></el-icon>
                各等级违规闭环统计
              </div>
              <div ref="closureStatsChart" class="chart-container"></div>
            </el-col>
          </el-row>
        </el-tab-pane>
      </el-tabs>

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

        <el-tab-pane label="训练计划完成率" name="planCompletion">
          <el-table :data="planCompletionRates" style="width: 100%">
            <el-table-column prop="plan_name" label="计划名称" min-width="200" />
            <el-table-column prop="plan_type" label="计划类型" width="120" align="center" />
            <el-table-column prop="total_schedules" label="总排班数" width="120" align="center" />
            <el-table-column prop="completed_schedules" label="已完成" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="success" effect="dark">{{ row.completed_schedules }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="pending_schedules" label="待完成" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="warning" effect="dark">{{ row.pending_schedules }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="完成率" width="180">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.completion_rate"
                  :color="row.completion_rate >= 80 ? '#67c23a' : row.completion_rate >= 50 ? '#e6a23c' : '#f56c6c'"
                />
              </template>
            </el-table-column>
            <el-table-column prop="start_date" label="开始日期" width="140" align="center" />
            <el-table-column prop="end_date" label="结束日期" width="140" align="center" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="风险射手排行" name="riskShooters">
          <el-table :data="riskShooters" style="width: 100%">
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
            <el-table-column prop="shooter_name" label="射手姓名" width="120" />
            <el-table-column prop="unit" label="所属单位" min-width="180" />
            <el-table-column prop="qualification_level" label="资质等级" width="120" align="center" />
            <el-table-column prop="violation_count" label="累计违规" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="danger" effect="dark">{{ row.violation_count }}次</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="recent_violations" label="近30天违规" width="140" align="center">
              <template #default="{ row }">
                <el-tag :type="row.recent_violations > 0 ? 'warning' : 'success'" effect="dark">
                  {{ row.recent_violations }}次
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="风险等级" width="120" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="row.risk_level === 'critical' ? 'danger' : row.risk_level === 'high' ? 'warning' : row.risk_level === 'medium' ? 'info' : 'success'"
                  effect="dark"
                >
                  {{ row.risk_level === 'critical' ? '极高' : row.risk_level === 'high' ? '高' : row.risk_level === 'medium' ? '中' : '低' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="risk_score" label="风险分数" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="danger" effect="dark">{{ row.risk_score }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="违规闭环统计" name="closureStats">
          <el-table :data="closureStats" style="width: 100%">
            <el-table-column prop="violation_level_display" label="违规等级" width="140" align="center" />
            <el-table-column prop="total_count" label="总处置数" width="120" align="center" />
            <el-table-column prop="closed_count" label="已闭环" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="success" effect="dark">{{ row.closed_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="pending_count" label="处理中" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="warning" effect="dark">{{ row.pending_count }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="闭环率" width="180">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.closure_rate"
                  :color="row.closure_rate >= 80 ? '#67c23a' : row.closure_rate >= 50 ? '#e6a23c' : '#f56c6c'"
                />
              </template>
            </el-table-column>
            <el-table-column prop="avg_closure_hours" label="平均闭环时长(小时)" width="180" align="center">
              <template #default="{ row }">
                <el-tag effect="dark">{{ row.avg_closure_hours }}h</el-tag>
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
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { statisticsApi } from '@/api'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const loading = ref(false)
const activeMainTab = ref('basic')
const activeTab = ref('lanes')
const lastUpdateTime = ref('-')

const ammoTrendChart = ref(null)
const laneUsageChart = ref(null)
const violationChart = ref(null)
const attendanceChart = ref(null)
const monthlyAmmoChart = ref(null)
const violationTypeChart = ref(null)
const planCompletionChart = ref(null)
const laneConflictChart = ref(null)
const conflictGaugeChart = ref(null)
const batchFlowChart = ref(null)
const batchUsageChart = ref(null)
const riskShooterChart = ref(null)
const closureTrendChart = ref(null)
const closureStatsChart = ref(null)

let ammoTrendChartInstance = null
let laneUsageChartInstance = null
let violationChartInstance = null
let attendanceChartInstance = null
let monthlyAmmoChartInstance = null
let violationTypeChartInstance = null
let planCompletionChartInstance = null
let laneConflictChartInstance = null
let conflictGaugeChartInstance = null
let batchFlowChartInstance = null
let batchUsageChartInstance = null
let riskShooterChartInstance = null
let closureTrendChartInstance = null
let closureStatsChartInstance = null

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
const planCompletionRates = ref([])
const laneConflictRate = ref(0)
const dailyConflicts = ref([])
const batchFlowStats = ref([])
const batchUsage = ref([])
const riskShooters = ref([])
const closureStats = ref([])
const dailyClosureEfficiency = ref([])

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
  const initOrDispose = (ref, instance) => {
    if (!ref.value) return null
    if (instance) {
      instance.dispose()
    }
    const rect = ref.value.getBoundingClientRect()
    if (rect.width === 0 || rect.height === 0) {
      return null
    }
    return echarts.init(ref.value)
  }

  ammoTrendChartInstance = initOrDispose(ammoTrendChart, ammoTrendChartInstance)
  laneUsageChartInstance = initOrDispose(laneUsageChart, laneUsageChartInstance)
  violationChartInstance = initOrDispose(violationChart, violationChartInstance)
  attendanceChartInstance = initOrDispose(attendanceChart, attendanceChartInstance)
  monthlyAmmoChartInstance = initOrDispose(monthlyAmmoChart, monthlyAmmoChartInstance)
  violationTypeChartInstance = initOrDispose(violationTypeChart, violationTypeChartInstance)
  planCompletionChartInstance = initOrDispose(planCompletionChart, planCompletionChartInstance)
  laneConflictChartInstance = initOrDispose(laneConflictChart, laneConflictChartInstance)
  conflictGaugeChartInstance = initOrDispose(conflictGaugeChart, conflictGaugeChartInstance)
  batchFlowChartInstance = initOrDispose(batchFlowChart, batchFlowChartInstance)
  batchUsageChartInstance = initOrDispose(batchUsageChart, batchUsageChartInstance)
  riskShooterChartInstance = initOrDispose(riskShooterChart, riskShooterChartInstance)
  closureTrendChartInstance = initOrDispose(closureTrendChart, closureTrendChartInstance)
  closureStatsChartInstance = initOrDispose(closureStatsChart, closureStatsChartInstance)
}

const renderAmmoTrendChart = () => {
  if (!ammoTrendChartInstance) return

  const dates = ammoTrend.value.map(item => dayjs(item.date).format('MM-DD'))
  const issued = ammoTrend.value.map(item => item.total_issued || 0)
  const consumed = ammoTrend.value.map(item => item.total_consumed || 0)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['领用数量', '消耗数量'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: dates },
    yAxis: { type: 'value', name: '发' },
    series: [
      {
        name: '领用数量', type: 'line', smooth: true, data: issued,
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
        ])},
        lineStyle: { color: '#409EFF', width: 2 },
        itemStyle: { color: '#409EFF' }
      },
      {
        name: '消耗数量', type: 'line', smooth: true, data: consumed,
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
          { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
        ])},
        lineStyle: { color: '#67c23a', width: 2 },
        itemStyle: { color: '#67c23a' }
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
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: laneNames, axisLabel: { interval: 0 } },
    yAxis: { type: 'value', name: '使用次数' },
    series: [{
      type: 'bar',
      data: usageCounts.map((value, index) => ({
        value, itemStyle: { color: colors[index], borderRadius: [4, 4, 0, 0] }
      })),
      barWidth: '50%',
      label: { show: true, position: 'top', formatter: '{c}次' }
    }]
  }
  laneUsageChartInstance.setOption(option)
}

const renderViolationChart = () => {
  if (!violationChartInstance) return

  const levelMap = { none: '无违规', minor: '轻微违规', major: '严重违规', critical: '重大违规' }
  const colorMap = { none: '#67c23a', minor: '#e6a23c', major: '#f56c6c', critical: '#c0392b' }

  const data = violationStats.value.map(item => ({
    value: item.count,
    name: levelMap[item.violation_level] || item.violation_level,
    itemStyle: { color: colorMap[item.violation_level] || '#909399' }
  })).filter(item => item.value > 0)

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c}次 ({d}%)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {c}次' },
      labelLine: { show: true },
      data: data
    }]
  }
  violationChartInstance.setOption(option)
}

const renderAttendanceChart = () => {
  if (!attendanceChartInstance) return

  const names = shooterAttendance.value.map(s => s.shooter__name).reverse()
  const counts = shooterAttendance.value.map(s => s.attendance_count).reverse()

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '出勤次数' },
    yAxis: { type: 'category', data: names },
    series: [{
      type: 'bar', data: counts, barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ]),
        borderRadius: [0, 4, 4, 0]
      },
      label: { show: true, position: 'right', formatter: '{c}次' }
    }]
  }
  attendanceChartInstance.setOption(option)
}

const renderMonthlyAmmoChart = () => {
  if (!monthlyAmmoChartInstance) return

  const months = ammoMonthly.value.map(item => dayjs(item.month).format('YYYY年MM月'))
  const totals = ammoMonthly.value.map(item => item.total || 0)

  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: months, axisLabel: { rotate: 30, interval: 0 } },
    yAxis: { type: 'value', name: '发' },
    series: [{
      type: 'bar', data: totals, barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(250, 112, 154, 0.9)' },
          { offset: 1, color: 'rgba(254, 225, 64, 0.9)' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      label: { show: true, position: 'top', formatter: '{c}' }
    }]
  }
  monthlyAmmoChartInstance.setOption(option)
}

const renderViolationTypeChart = () => {
  if (!violationTypeChartInstance) return

  const types = violationTypes.value.map(v => v.violation_type)
  const counts = violationTypes.value.map(v => v.count)

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '次数' },
    yAxis: { type: 'category', data: types.reverse() },
    series: [{
      type: 'bar', data: counts.reverse(), barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#f56c6c' },
          { offset: 1, color: '#e6a23c' }
        ]),
        borderRadius: [0, 4, 4, 0]
      },
      label: { show: true, position: 'right', formatter: '{c}次' }
    }]
  }
  violationTypeChartInstance.setOption(option)
}

const renderPlanCompletionChart = () => {
  if (!planCompletionChartInstance) return

  const planNames = planCompletionRates.value.map(p => p.plan_name)
  const completionRates = planCompletionRates.value.map(p => p.completion_rate)
  const completed = planCompletionRates.value.map(p => p.completed_schedules)
  const pending = planCompletionRates.value.map(p => p.pending_schedules)

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['完成率', '已完成', '待完成'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: planNames, axisLabel: { rotate: 15, interval: 0 } },
    yAxis: [
      { type: 'value', name: '百分比(%)', max: 100 },
      { type: 'value', name: '数量' }
    ],
    series: [
      {
        name: '完成率', type: 'line', yAxisIndex: 0, data: completionRates,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        itemStyle: { color: '#409EFF' },
        label: { show: true, formatter: '{c}%', position: 'top' }
      },
      {
        name: '已完成', type: 'bar', yAxisIndex: 1, data: completed,
        barWidth: '30%',
        itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '待完成', type: 'bar', yAxisIndex: 1, data: pending,
        barWidth: '30%',
        itemStyle: { color: '#e6a23c', borderRadius: [4, 4, 0, 0] }
      }
    ]
  }
  planCompletionChartInstance.setOption(option)
}

const renderLaneConflictChart = () => {
  if (!laneConflictChartInstance) return

  const dates = dailyConflicts.value.map(item => dayjs(item.date).format('MM-DD'))
  const conflictCounts = dailyConflicts.value.map(item => item.conflict_count || 0)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['冲突次数'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: dates },
    yAxis: { type: 'value', name: '次' },
    series: [{
      name: '冲突次数', type: 'line', smooth: true, data: conflictCounts,
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
        { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
      ])},
      lineStyle: { color: '#f56c6c', width: 2 },
      itemStyle: { color: '#f56c6c' },
      label: { show: true, formatter: '{c}次' }
    }]
  }
  laneConflictChartInstance.setOption(option)
}

const renderConflictGaugeChart = () => {
  if (!conflictGaugeChartInstance) return

  const rate = laneConflictRate.value || 0
  const color = rate >= 20 ? '#f56c6c' : rate >= 10 ? '#e6a23c' : '#67c23a'

  const option = {
    series: [{
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: 0,
      max: 100,
      splitNumber: 5,
      itemStyle: { color: color },
      progress: { show: true, width: 18 },
      pointer: { show: false },
      axisLine: { lineStyle: { width: 18 } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      title: { show: true, offsetCenter: [0, '20%'], fontSize: 14, color: '#666' },
      detail: {
        valueAnimation: true,
        fontSize: 24,
        offsetCenter: [0, 0],
        formatter: '{value}%',
        color: color
      },
      data: [{ value: rate, name: '靶道冲突率' }]
    }]
  }
  conflictGaugeChartInstance.setOption(option)
}

const renderBatchFlowChart = () => {
  if (!batchFlowChartInstance) return

  const flowTypeMap = {
    'in': '入库',
    'out': '出库',
    'issue': '领用',
    'return': '归还',
    'consume': '消耗',
    'adjust': '调整',
    'scrap': '报废'
  }

  const colorMap = {
    'in': '#67c23a',
    'out': '#e6a23c',
    'issue': '#409EFF',
    'return': '#909399',
    'consume': '#f56c6c',
    'adjust': '#9b59b6',
    'scrap': '#c0392b'
  }

  const data = batchFlowStats.value.map(item => ({
    value: item.total_quantity || 0,
    name: flowTypeMap[item.flow_type] || item.flow_type,
    itemStyle: { color: colorMap[item.flow_type] || '#909399' }
  })).filter(item => item.value > 0)

  const option = {
    tooltip: { trigger: 'item', formatter: '{b}: {c}发 ({d}%)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie', radius: ['40%', '70%'], center: ['60%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {c}发' },
      labelLine: { show: true },
      data: data
    }]
  }
  batchFlowChartInstance.setOption(option)
}

const renderBatchUsageChart = () => {
  if (!batchUsageChartInstance) return

  const batchNames = batchUsage.value.map(b => `${b.ammo_batch__batch_number}\n(${b.ammo_batch__ammunition__name})`).reverse()
  const usedQuantities = batchUsage.value.map(b => b.total_used || 0).reverse()

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'value', name: '发' },
    yAxis: { type: 'category', data: batchNames, axisLabel: { interval: 0 } },
    series: [{
      type: 'bar', data: usedQuantities, barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ]),
        borderRadius: [0, 4, 4, 0]
      },
      label: { show: true, position: 'right', formatter: '{c}发' }
    }]
  }
  batchUsageChartInstance.setOption(option)
}

const renderRiskShooterChart = () => {
  if (!riskShooterChartInstance) return

  const names = riskShooters.value.map(s => s.shooter_name).reverse()
  const riskScores = riskShooters.value.map(s => s.risk_score).reverse()
  const violationCounts = riskShooters.value.map(s => s.violation_count).reverse()

  const riskColors = riskShooters.value.map(s => {
    const level = s.risk_level
    if (level === 'critical') return '#c0392b'
    if (level === 'high') return '#f56c6c'
    if (level === 'medium') return '#e6a23c'
    return '#67c23a'
  }).reverse()

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['风险分数', '违规次数'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: [
      { type: 'value', name: '分数' },
      { type: 'value', name: '次数' }
    ],
    yAxis: { type: 'category', data: names },
    series: [
      {
        name: '风险分数', type: 'bar', xAxisIndex: 0,
        barWidth: '35%',
        data: riskScores.map((value, index) => ({
          value,
          itemStyle: { color: riskColors[index], borderRadius: [0, 4, 4, 0] }
        })),
        label: { show: true, position: 'right', formatter: '{c}分' }
      },
      {
        name: '违规次数', type: 'bar', xAxisIndex: 1, data: violationCounts,
        barWidth: '35%',
        itemStyle: { color: '#909399', borderRadius: [0, 4, 4, 0] },
        label: { show: true, position: 'right', formatter: '{c}次' }
      }
    ]
  }
  riskShooterChartInstance.setOption(option)
}

const renderClosureTrendChart = () => {
  if (!closureTrendChartInstance) return

  const dates = dailyClosureEfficiency.value.map(item => dayjs(item.date).format('MM-DD'))
  const created = dailyClosureEfficiency.value.map(item => item.total_created || 0)
  const closed = dailyClosureEfficiency.value.map(item => item.total_closed || 0)

  const option = {
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增违规', '闭环完成'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: dates },
    yAxis: { type: 'value', name: '件' },
    series: [
      {
        name: '新增违规', type: 'line', smooth: true, data: created,
        lineStyle: { color: '#f56c6c', width: 2 },
        itemStyle: { color: '#f56c6c' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(245, 108, 108, 0.2)' },
          { offset: 1, color: 'rgba(245, 108, 108, 0.02)' }
        ])}
      },
      {
        name: '闭环完成', type: 'line', smooth: true, data: closed,
        lineStyle: { color: '#67c23a', width: 2 },
        itemStyle: { color: '#67c23a' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(103, 194, 58, 0.2)' },
          { offset: 1, color: 'rgba(103, 194, 58, 0.02)' }
        ])}
      }
    ]
  }
  closureTrendChartInstance.setOption(option)
}

const renderClosureStatsChart = () => {
  if (!closureStatsChartInstance) return

  const levels = closureStats.value.map(s => s.violation_level_display)
  const totalCounts = closureStats.value.map(s => s.total_count)
  const closedCounts = closureStats.value.map(s => s.closed_count)
  const pendingCounts = closureStats.value.map(s => s.pending_count)
  const avgHours = closureStats.value.map(s => s.avg_closure_hours)

  const option = {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['总数', '已闭环', '处理中', '平均时长(h)'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: levels },
    yAxis: [
      { type: 'value', name: '数量' },
      { type: 'value', name: '小时' }
    ],
    series: [
      {
        name: '总数', type: 'bar', yAxisIndex: 0, data: totalCounts,
        barWidth: '20%',
        itemStyle: { color: '#909399', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '已闭环', type: 'bar', yAxisIndex: 0, data: closedCounts,
        barWidth: '20%',
        itemStyle: { color: '#67c23a', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '处理中', type: 'bar', yAxisIndex: 0, data: pendingCounts,
        barWidth: '20%',
        itemStyle: { color: '#e6a23c', borderRadius: [4, 4, 0, 0] }
      },
      {
        name: '平均时长(h)', type: 'line', yAxisIndex: 1, data: avgHours,
        smooth: true,
        lineStyle: { color: '#409EFF', width: 3 },
        itemStyle: { color: '#409EFF' },
        label: { show: true, formatter: '{c}h' }
      }
    ]
  }
  closureStatsChartInstance.setOption(option)
}

const loadStatistics = async () => {
  try {
    loading.value = true
    const [basicRes, advancedRes] = await Promise.all([
      statisticsApi.dashboard(),
      statisticsApi.advanced()
    ])

    const basicData = basicRes.data
    const advancedData = advancedRes.data

    Object.assign(overview, basicData.overview)
    laneUsage.value = basicData.lane_usage || []
    ammoTrend.value = basicData.ammo_trend || []
    ammoMonthly.value = basicData.ammo_monthly || []
    violationStats.value = basicData.violation_stats || []
    shooterAttendance.value = basicData.shooter_attendance || []
    violationTypes.value = basicData.violation_types || []

    planCompletionRates.value = advancedData.plan_completion_rates || []
    laneConflictRate.value = advancedData.lane_conflict_rate || 0
    dailyConflicts.value = advancedData.daily_conflicts || []
    batchFlowStats.value = advancedData.batch_flow_stats || []
    batchUsage.value = advancedData.batch_usage || []
    riskShooters.value = advancedData.risk_shooters || []
    closureStats.value = advancedData.closure_stats || []
    dailyClosureEfficiency.value = advancedData.daily_closure_efficiency || []

    lastUpdateTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')

    await nextTick()
    setTimeout(() => {
      initCharts()
      renderAllCharts()
    }, 100)
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
  renderPlanCompletionChart()
  renderLaneConflictChart()
  renderConflictGaugeChart()
  renderBatchFlowChart()
  renderBatchUsageChart()
  renderRiskShooterChart()
  renderClosureTrendChart()
  renderClosureStatsChart()
}

const refreshData = () => {
  loadStatistics()
  ElMessage.success('数据已刷新')
}

watch(activeMainTab, (newVal) => {
  if (newVal === 'advanced') {
    nextTick(() => {
      setTimeout(() => {
        initCharts()
        renderPlanCompletionChart()
        renderLaneConflictChart()
        renderConflictGaugeChart()
        renderBatchFlowChart()
        renderBatchUsageChart()
        renderRiskShooterChart()
        renderClosureTrendChart()
        renderClosureStatsChart()
      }, 100)
    })
  } else {
    nextTick(() => {
      setTimeout(() => {
        initCharts()
        renderAmmoTrendChart()
        renderLaneUsageChart()
        renderViolationChart()
        renderAttendanceChart()
        renderMonthlyAmmoChart()
        renderViolationTypeChart()
      }, 100)
    })
  }
})

const handleResize = () => {
  ammoTrendChartInstance?.resize()
  laneUsageChartInstance?.resize()
  violationChartInstance?.resize()
  attendanceChartInstance?.resize()
  monthlyAmmoChartInstance?.resize()
  violationTypeChartInstance?.resize()
  planCompletionChartInstance?.resize()
  laneConflictChartInstance?.resize()
  conflictGaugeChartInstance?.resize()
  batchFlowChartInstance?.resize()
  batchUsageChartInstance?.resize()
  riskShooterChartInstance?.resize()
  closureTrendChartInstance?.resize()
  closureStatsChartInstance?.resize()
}

onMounted(async () => {
  await nextTick()
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
  planCompletionChartInstance?.dispose()
  laneConflictChartInstance?.dispose()
  conflictGaugeChartInstance?.dispose()
  batchFlowChartInstance?.dispose()
  batchUsageChartInstance?.dispose()
  riskShooterChartInstance?.dispose()
  closureTrendChartInstance?.dispose()
  closureStatsChartInstance?.dispose()
})
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #303133;
}

.card-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 150px;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  border-left: 4px solid #409EFF;
}

.stat-card.blue {
  border-left-color: #409EFF;
}

.stat-card.green {
  border-left-color: #67c23a;
}

.stat-card.orange {
  border-left-color: #e6a23c;
}

.stat-card.red {
  border-left-color: #f56c6c;
}

.stat-card.purple {
  border-left-color: #9b59b6;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.page-container {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #303133;
}

.chart-container {
  height: 350px;
  width: 100%;
  margin-bottom: 24px;
}
</style>
