<template>
  <div>
    <div class="page-title">
      <el-icon><BellFilled /></el-icon>
      风险预警中心
    </div>

    <div class="card-row">
      <div class="stat-card red">
        <div class="stat-label">紧急预警</div>
        <div class="stat-value">{{ criticalCount }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">高风险</div>
        <div class="stat-value">{{ highCount }}</div>
      </div>
      <div class="stat-card blue">
        <div class="stat-label">中风险</div>
        <div class="stat-value">{{ mediumCount }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">低风险</div>
        <div class="stat-value">{{ lowCount }}</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">已处理</div>
        <div class="stat-value">{{ resolvedCount }}</div>
      </div>
    </div>

    <div class="page-container">
      <div class="section-title">
        <el-icon><List /></el-icon>
        预警列表
      </div>

      <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
        <el-form-item label="预警类型">
          <el-select v-model="filterForm.warning_type" placeholder="全部" clearable style="width: 150px">
            <el-option label="弹药库存" value="ammo_stock" />
            <el-option label="弹药过期" value="ammo_expiry" />
            <el-option label="靶道冲突" value="lane_conflict" />
            <el-option label="射手风险" value="shooter_risk" />
            <el-option label="枪械状态" value="firearm_status" />
            <el-option label="违规预警" value="violation" />
            <el-option label="安全阈值" value="safety_threshold" />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="filterForm.risk_level" placeholder="全部" clearable style="width: 130px">
            <el-option label="紧急" value="critical" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 130px">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已处理" value="resolved" />
            <el-option label="已忽略" value="ignored" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filterForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 280px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadWarnings">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="resetFilter">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
          <el-button type="success" @click="exportData">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-form-item>
      </el-form>

      <div style="margin-bottom: 16px">
        <el-button type="primary" @click="refreshWarnings">
          <el-icon><RefreshRight /></el-icon>
          刷新预警
        </el-button>
        <el-button type="warning" @click="handleBatchProcess" :disabled="selectedRows.length === 0">
          <el-icon><Check /></el-icon>
          批量处理 ({{ selectedRows.length }})
        </el-button>
      </div>

      <el-table
        :data="warningList"
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column label="风险等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.risk_level)" effect="dark" size="small">
              {{ row.risk_level_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预警类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeColor(row.warning_type)" effect="dark" size="small">
              {{ row.warning_type_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="预警标题" min-width="180" />
        <el-table-column prop="message" label="预警详情" min-width="250" />
        <el-table-column label="关联对象" width="150">
          <template #default="{ row }">
            <span v-if="row.related_entity_type">
              {{ row.related_entity_type }}
              <el-tag v-if="row.related_entity_id" size="small">#{{ row.related_entity_id }}</el-tag>
            </span>
            <span v-else style="color: #909399">无</span>
          </template>
        </el-table-column>
        <el-table-column label="预警时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="处理时限" width="160">
          <template #default="{ row }">
            <el-tag v-if="row.deadline" :type="isOverdue(row.deadline) ? 'danger' : 'info'" effect="dark" size="small">
              {{ formatDateTime(row.deadline) }}
            </el-tag>
            <span v-else style="color: #909399">无</span>
          </template>
        </el-table-column>
        <el-table-column label="处理人" width="100" prop="handled_by" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending' || row.status === 'processing'"
              type="primary"
              size="small"
              @click="openProcessDialog(row)"
            >
              处理
            </el-button>
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="info"
              size="small"
              @click="ignoreWarning(row)"
            >
              忽略
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end; display: flex"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
      />
    </div>

    <el-dialog v-model="processDialogVisible" title="处理预警" width="600px">
      <div v-if="selectedWarning">
        <el-descriptions :column="2" border style="margin-bottom: 16px">
          <el-descriptions-item label="预警等级">
            <el-tag :type="getLevelType(selectedWarning.risk_level)" effect="dark">
              {{ selectedWarning.risk_level_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预警类型">
            <el-tag :type="getTypeColor(selectedWarning.warning_type)" effect="dark">
              {{ selectedWarning.warning_type_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预警标题">{{ selectedWarning.title }}</el-descriptions-item>
          <el-descriptions-item label="预警时间">{{ formatDateTime(selectedWarning.created_at) }}</el-descriptions-item>
          <el-descriptions-item :span="2" label="预警详情">{{ selectedWarning.message }}</el-descriptions-item>
        </el-descriptions>

        <el-form :model="processForm" :rules="processRules" ref="processFormRef" label-width="100px">
          <el-form-item label="处理结果" prop="status">
            <el-radio-group v-model="processForm.status">
              <el-radio value="resolved">已解决</el-radio>
              <el-radio value="processing">处理中</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="处理措施" prop="handling_notes">
            <el-input
              v-model="processForm.handling_notes"
              type="textarea"
              :rows="4"
              placeholder="请详细描述处理措施和结果..."
            />
          </el-form-item>
          <el-form-item label="处理人">
            <el-input v-model="processForm.handled_by" placeholder="请输入处理人姓名" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="processDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProcess" :loading="submitting">确认处理</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="预警详情" width="600px">
      <div v-if="selectedWarning">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="预警等级">
            <el-tag :type="getLevelType(selectedWarning.risk_level)" effect="dark">
              {{ selectedWarning.risk_level_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预警类型">
            <el-tag :type="getTypeColor(selectedWarning.warning_type)" effect="dark">
              {{ selectedWarning.warning_type_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(selectedWarning.status)" effect="dark">
              {{ selectedWarning.status_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预警时间">{{ formatDateTime(selectedWarning.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="预警标题" :span="2">{{ selectedWarning.title }}</el-descriptions-item>
          <el-descriptions-item label="预警详情" :span="2">{{ selectedWarning.message }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.related_entity_type" label="关联对象">
            {{ selectedWarning.related_entity_type }} #{{ selectedWarning.related_entity_id }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.deadline" label="处理时限">
            {{ formatDateTime(selectedWarning.deadline) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.handled_by" label="处理人">
            {{ selectedWarning.handled_by }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.handled_at" label="处理时间">
            {{ formatDateTime(selectedWarning.handled_at) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.handling_notes" label="处理备注" :span="2">
            {{ selectedWarning.handling_notes }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { riskWarningApi } from '@/api'
import dayjs from 'dayjs'

const processDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const processFormRef = ref(null)
const submitting = ref(false)
const selectedWarning = ref(null)
const selectedRows = ref([])

const warningList = ref([])
const criticalCount = ref(0)
const highCount = ref(0)
const mediumCount = ref(0)
const lowCount = ref(0)
const resolvedCount = ref(0)

const filterForm = reactive({
  warning_type: '',
  risk_level: '',
  status: '',
  date_range: []
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const processForm = reactive({
  status: 'resolved',
  handling_notes: '',
  handled_by: ''
})

const processRules = {
  status: [{ required: true, message: '请选择处理结果', trigger: 'change' }],
  handling_notes: [{ required: true, message: '请输入处理措施', trigger: 'blur' }]
}

const formatDateTime = (date) => date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'

const getLevelType = (level) => {
  const map = {
    critical: 'danger',
    high: 'warning',
    medium: 'primary',
    low: 'info'
  }
  return map[level] || 'info'
}

const getTypeColor = (type) => {
  const map = {
    ammo_stock: 'warning',
    ammo_expiry: 'danger',
    lane_conflict: 'danger',
    shooter_risk: 'warning',
    firearm_status: 'primary',
    violation: 'danger',
    safety_threshold: 'warning'
  }
  return map[type] || 'info'
}

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    processing: 'primary',
    resolved: 'success',
    ignored: 'info'
  }
  return map[status] || 'info'
}

const isOverdue = (deadline) => {
  if (!deadline) return false
  return dayjs(deadline).isBefore(dayjs())
}

const loadWarnings = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      ordering: '-created_at'
    }
    if (filterForm.warning_type) params.warning_type = filterForm.warning_type
    if (filterForm.risk_level) params.risk_level = filterForm.risk_level
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.date_range?.length === 2) {
      params.created_at__gte = filterForm.date_range[0]
      params.created_at__lte = filterForm.date_range[1]
    }

    const res = await riskWarningApi.list(params)
    warningList.value = res.data.results || res.data
    pagination.total = res.data.count || warningList.value.length

    const all = res.data.results || res.data
    criticalCount.value = all.filter(w => w.risk_level === 'critical' && w.status !== 'resolved' && w.status !== 'ignored').length
    highCount.value = all.filter(w => w.risk_level === 'high' && w.status !== 'resolved' && w.status !== 'ignored').length
    mediumCount.value = all.filter(w => w.risk_level === 'medium' && w.status !== 'resolved' && w.status !== 'ignored').length
    lowCount.value = all.filter(w => w.risk_level === 'low' && w.status !== 'resolved' && w.status !== 'ignored').length
    resolvedCount.value = all.filter(w => w.status === 'resolved').length
  } catch (e) {
    console.error(e)
    ElMessage.error('加载预警列表失败')
  }
}

const handlePageChange = () => loadWarnings()
const handleSizeChange = () => {
  pagination.page = 1
  loadWarnings()
}

const resetFilter = () => {
  filterForm.warning_type = ''
  filterForm.risk_level = ''
  filterForm.status = ''
  filterForm.date_range = []
  pagination.page = 1
  loadWarnings()
}

const refreshWarnings = () => {
  loadWarnings()
  ElMessage.success('预警列表已刷新')
}

const handleSelectionChange = (val) => {
  selectedRows.value = val
}

const openProcessDialog = (row) => {
  selectedWarning.value = row
  processForm.status = 'resolved'
  processForm.handling_notes = ''
  processForm.handled_by = ''
  processDialogVisible.value = true
}

const viewDetail = (row) => {
  selectedWarning.value = row
  detailDialogVisible.value = true
}

const submitProcess = async () => {
  try {
    await processFormRef.value.validate()
    submitting.value = true

    const data = {
      ...selectedWarning.value,
      status: processForm.status,
      handling_notes: processForm.handling_notes,
      handled_by: processForm.handled_by,
      handled_at: dayjs().format('YYYY-MM-DD HH:mm:ss')
    }

    await riskWarningApi.update(selectedWarning.value.id, data)
    ElMessage.success('处理成功')
    processDialogVisible.value = false
    loadWarnings()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const ignoreWarning = async (row) => {
  try {
    await ElMessageBox.confirm('确定要忽略该预警吗？', '确认', { type: 'warning' })
    await riskWarningApi.update(row.id, { ...row, status: 'ignored' })
    ElMessage.success('已忽略')
    loadWarnings()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const handleBatchProcess = () => {
  ElMessage.info(`选中 ${selectedRows.value.length} 条预警，批量处理功能开发中`)
}

const exportData = async () => {
  try {
    const params = { ordering: '-created_at' }
    if (filterForm.warning_type) params.warning_type = filterForm.warning_type
    if (filterForm.risk_level) params.risk_level = filterForm.risk_level
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.date_range?.length === 2) {
      params.created_at__gte = filterForm.date_range[0]
      params.created_at__lte = filterForm.date_range[1]
    }

    const res = await riskWarningApi.export(params)
    downloadFile(res, `风险预警_${dayjs().format('YYYYMMDD')}.csv`)
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  }
}

const downloadFile = (response, filename) => {
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

onMounted(() => {
  loadWarnings()
})
</script>
