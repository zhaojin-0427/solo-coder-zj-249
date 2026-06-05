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
            <el-option
              v-for="opt in warningTypeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="风险等级">
          <el-select v-model="filterForm.warning_level" placeholder="全部" clearable style="width: 130px">
            <el-option
              v-for="opt in warningLevelOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 130px">
            <el-option
              v-for="opt in warningStatusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
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
            <el-tag :type="getLevelType(row.warning_level)" effect="dark" size="small">
              {{ row.warning_level_display }}
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
        <el-table-column prop="description" label="预警详情" min-width="250" />
        <el-table-column label="关联对象" width="150">
          <template #default="{ row }">
            <span v-if="row.related_model">
              {{ row.related_model }}
              <el-tag v-if="row.related_id" size="small">#{{ row.related_id }}</el-tag>
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
            <el-tag :type="getLevelType(selectedWarning.warning_level)" effect="dark">
              {{ selectedWarning.warning_level_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预警类型">
            <el-tag :type="getTypeColor(selectedWarning.warning_type)" effect="dark">
              {{ selectedWarning.warning_type_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预警标题">{{ selectedWarning.title }}</el-descriptions-item>
          <el-descriptions-item label="预警时间">{{ formatDateTime(selectedWarning.created_at) }}</el-descriptions-item>
          <el-descriptions-item :span="2" label="预警详情">{{ selectedWarning.description }}</el-descriptions-item>
        </el-descriptions>

        <el-form :model="processForm" :rules="processRules" ref="processFormRef" label-width="100px">
          <el-form-item label="处理结果" prop="status">
            <el-radio-group v-model="processForm.status">
              <el-radio value="resolved">已解决</el-radio>
              <el-radio value="processing">处理中</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="处理措施" prop="handle_result">
            <el-input
              v-model="processForm.handle_result"
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
            <el-tag :type="getLevelType(selectedWarning.warning_level)" effect="dark">
              {{ selectedWarning.warning_level_display }}
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
          <el-descriptions-item label="预警详情" :span="2">{{ selectedWarning.description }}</el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.related_model" label="关联对象">
            {{ selectedWarning.related_model }} #{{ selectedWarning.related_id }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.deadline" label="处理时限">
            {{ formatDateTime(selectedWarning.deadline) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.handled_by" label="处理人">
            {{ selectedWarning.handled_by }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.handle_time" label="处理时间">
            {{ formatDateTime(selectedWarning.handle_time) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedWarning.handle_result" label="处理备注" :span="2">
            {{ selectedWarning.handle_result }}
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
import {
  formatDateTime, getRiskLevelType, getRiskLevelText,
  getRiskTypeColor, getRiskStatusType, isOverdue, downloadFile
} from '@/utils'
import { getFilterOptions, buildFilterParams, buildPaginationParams } from '@/adapters'
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
  warning_level: '',
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
  handle_result: '',
  handled_by: ''
})

const processRules = {
  status: [{ required: true, description: '请选择处理结果', trigger: 'change' }],
  handle_result: [{ required: true, description: '请输入处理措施', trigger: 'blur' }]
}

const warningTypeOptions = getFilterOptions('riskWarning', 'warning_type')
const warningLevelOptions = getFilterOptions('riskWarning', 'warning_level')
const warningStatusOptions = getFilterOptions('riskWarning', 'status')

const getLevelType = getRiskLevelType
const getTypeColor = getRiskTypeColor
const getStatusType = getRiskStatusType

const loadWarnings = async () => {
  try {
    const params = {
      ...buildPaginationParams(pagination),
      ...buildFilterParams(filterForm, {
        date_range: 'created_at'
      }),
      ordering: '-created_at'
    }

    const res = await riskWarningApi.list(params)
    warningList.value = res.data.results || res.data
    pagination.total = res.data.count || warningList.value.length

    const all = res.data.results || res.data
    criticalCount.value = all.filter(w => w.warning_level === 'critical' && w.status !== 'resolved' && w.status !== 'ignored').length
    highCount.value = all.filter(w => w.warning_level === 'high' && w.status !== 'resolved' && w.status !== 'ignored').length
    mediumCount.value = all.filter(w => w.warning_level === 'medium' && w.status !== 'resolved' && w.status !== 'ignored').length
    lowCount.value = all.filter(w => w.warning_level === 'low' && w.status !== 'resolved' && w.status !== 'ignored').length
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
  filterForm.warning_level = ''
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
  processForm.handle_result = ''
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
      handle_result: processForm.handle_result,
      handled_by: processForm.handled_by,
      handle_time: dayjs().format('YYYY-MM-DD HH:mm:ss')
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
    const params = {
      ...buildFilterParams(filterForm, {
        date_range: 'created_at'
      }),
      ordering: '-created_at'
    }

    const res = await riskWarningApi.export(params)
    downloadFile(res, `风险预警_${dayjs().format('YYYYMMDD')}.csv`)
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadWarnings()
})
</script>
