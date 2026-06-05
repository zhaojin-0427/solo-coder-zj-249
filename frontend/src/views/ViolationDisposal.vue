<template>
  <div>
    <div class="page-title">
      <el-icon><CircleCheck /></el-icon>
      违规闭环处置
    </div>

    <div class="card-row">
      <div class="stat-card red">
        <div class="stat-label">待处置</div>
        <div class="stat-value">{{ pendingCount }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">已通知</div>
        <div class="stat-value">{{ notifiedCount }}</div>
      </div>
      <div class="stat-card blue">
        <div class="stat-label">责任人确认</div>
        <div class="stat-value">{{ confirmedCount }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">已整改</div>
        <div class="stat-value">{{ rectifiedCount }}</div>
      </div>
      <div class="stat-card blue">
        <div class="stat-label">已验证</div>
        <div class="stat-value">{{ verifiedCount }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">已闭环</div>
        <div class="stat-value">{{ closedCount }}</div>
      </div>
    </div>

    <div class="page-container">
      <div class="section-title">
        <el-icon><List /></el-icon>
        违规处置列表
      </div>

      <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
        <el-form-item label="射手">
          <el-input v-model="filterForm.shooter_name" placeholder="请输入" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="处置状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 130px">
            <el-option label="待处置" value="pending" />
            <el-option label="已通知" value="notified" />
            <el-option label="责任人确认" value="confirmed" />
            <el-option label="已整改" value="rectified" />
            <el-option label="已验证" value="verified" />
            <el-option label="已闭环" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item label="违规等级">
          <el-select v-model="filterForm.violation_level" placeholder="全部" clearable style="width: 130px">
            <el-option label="轻微" value="minor" />
            <el-option label="严重" value="major" />
            <el-option label="重大" value="critical" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否暂停领弹">
          <el-select v-model="filterForm.is_ammo_suspended" placeholder="全部" clearable style="width: 130px">
            <el-option label="是" :value="true" />
            <el-option label="否" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadDisposals">
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

      <el-table :data="disposalList" style="width: 100%">
        <el-table-column label="违规编号" width="120">
          <template #default="{ row }">#{{ row.id }}</template>
        </el-table-column>
        <el-table-column label="射手" width="100">
          <template #default="{ row }">{{ row.shooter_info?.name }}</template>
        </el-table-column>
        <el-table-column label="所属单位" width="150">
          <template #default="{ row }">{{ row.shooter_info?.unit }}</template>
        </el-table-column>
        <el-table-column label="违规类型" width="150">
          <template #default="{ row }">{{ row.safety_inspection_info?.violation_type }}</template>
        </el-table-column>
        <el-table-column label="违规等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getViolationLevelType(row.safety_inspection_info?.violation_level)" effect="dark" size="small">
              {{ row.safety_inspection_info?.violation_level_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处置状态" width="120" align="center">
          <template #default="{ row }">
            <el-steps :active="getStepIndex(row.status)" simple size="small">
              <el-step title="待处置" />
              <el-step title="已通知" />
              <el-step title="已确认" />
              <el-step title="已整改" />
              <el-step title="已验证" />
              <el-step title="已闭环" />
            </el-steps>
          </template>
        </el-table-column>
        <el-table-column label="暂停领弹" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_ammo_suspended ? 'danger' : 'success'" effect="dark" size="small">
              {{ row.is_ammo_suspended ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="锁定成绩" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_score_locked ? 'danger' : 'success'" effect="dark" size="small">
              {{ row.is_score_locked ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="处置时效" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status !== 'closed'" :type="isOverdue(row.created_at, row.status) ? 'danger' : 'warning'" effect="dark" size="small">
              {{ getDuration(row.created_at) }}
            </el-tag>
            <el-tag v-else type="success" effect="dark" size="small">
              {{ getDuration(row.created_at, row.closed_at) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="primary"
              size="small"
              @click="notifyResponsible(row)"
            >
              通知
            </el-button>
            <el-button
              v-if="row.status === 'notified'"
              type="warning"
              size="small"
              @click="confirmResponsible(row)"
            >
              确认
            </el-button>
            <el-button
              v-if="row.status === 'confirmed'"
              type="primary"
              size="small"
              @click="recordRectification(row)"
            >
              整改
            </el-button>
            <el-button
              v-if="row.status === 'rectified'"
              type="success"
              size="small"
              @click="verifyRectification(row)"
            >
              验证
            </el-button>
            <el-button
              v-if="row.status === 'verified'"
              type="success"
              size="small"
              @click="closeDisposal(row)"
            >
              闭环
            </el-button>
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
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

    <el-dialog v-model="detailDialogVisible" title="违规处置详情" width="700px">
      <div v-if="selectedDisposal">
        <el-descriptions :column="2" border style="margin-bottom: 16px">
          <el-descriptions-item label="违规编号">#{{ selectedDisposal.id }}</el-descriptions-item>
          <el-descriptions-item label="射手">{{ selectedDisposal.shooter_info?.name }}</el-descriptions-item>
          <el-descriptions-item label="所属单位">{{ selectedDisposal.shooter_info?.unit }}</el-descriptions-item>
          <el-descriptions-item label="资质等级">{{ selectedDisposal.shooter_info?.qualification_level_display }}</el-descriptions-item>
          <el-descriptions-item label="违规类型">
            {{ selectedDisposal.safety_inspection_info?.violation_type }}
          </el-descriptions-item>
          <el-descriptions-item label="违规等级">
            <el-tag :type="getViolationLevelType(selectedDisposal.safety_inspection_info?.violation_level)" effect="dark">
              {{ selectedDisposal.safety_inspection_info?.violation_level_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="违规时间">
            {{ formatDateTime(selectedDisposal.safety_inspection_info?.inspection_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="安全员">
            {{ selectedDisposal.safety_inspection_info?.inspector }}
          </el-descriptions-item>
          <el-descriptions-item label="靶道">
            {{ selectedDisposal.safety_inspection_info?.target_lane_info?.lane_number }}号靶道
          </el-descriptions-item>
          <el-descriptions-item label="枪械">
            {{ selectedDisposal.safety_inspection_info?.firearm_info?.name }}
          </el-descriptions-item>
          <el-descriptions-item label="暂停领弹">
            <el-tag :type="selectedDisposal.is_ammo_suspended ? 'danger' : 'success'" effect="dark">
              {{ selectedDisposal.is_ammo_suspended ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="锁定成绩">
            <el-tag :type="selectedDisposal.is_score_locked ? 'danger' : 'success'" effect="dark">
              {{ selectedDisposal.is_score_locked ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="违规详情" :span="2">
            {{ selectedDisposal.safety_inspection_info?.violation_description }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">处置流程</el-divider>
        <el-steps :active="getStepIndex(selectedDisposal.status)" finish-status="success" align-center>
          <el-step title="待处置" :description="formatDateTime(selectedDisposal.created_at)" icon="Clock" />
          <el-step title="已通知" :description="formatDateTime(selectedDisposal.notified_at)" icon="Bell" />
          <el-step title="责任人确认" :description="formatDateTime(selectedDisposal.confirmed_at)" icon="User" />
          <el-step title="已整改" :description="formatDateTime(selectedDisposal.rectified_at)" icon="Tools" />
          <el-step title="已验证" :description="formatDateTime(selectedDisposal.verified_at)" icon="CircleCheck" />
          <el-step title="已闭环" :description="formatDateTime(selectedDisposal.closed_at)" icon="Check" />
        </el-steps>

        <el-descriptions :column="1" border style="margin-top: 16px" v-if="selectedDisposal.closure_summary">
          <el-descriptions-item label="责任人">
            {{ selectedDisposal.responsible_person || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="整改措施">
            {{ selectedDisposal.rectification_measures || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="验证结果">
            {{ selectedDisposal.verification_result || '未填写' }}
          </el-descriptions-item>
          <el-descriptions-item label="闭环总结">
            {{ selectedDisposal.closure_summary || '未填写' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="processDialogVisible" :title="processDialogTitle" width="600px">
      <el-form :model="processForm" :rules="processRules" ref="processFormRef" label-width="120px">
        <el-form-item v-if="currentStep === 'notify'" label="通知方式">
          <el-radio-group v-model="processForm.notification_method">
            <el-radio value="system">系统通知</el-radio>
            <el-radio value="sms">短信</el-radio>
            <el-radio value="phone">电话</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="currentStep === 'notify'" label="通知内容">
          <el-input v-model="processForm.notification_content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item v-if="currentStep === 'confirm'" label="责任人">
          <el-input v-model="processForm.responsible_person" placeholder="请输入责任人姓名" />
        </el-form-item>
        <el-form-item v-if="currentStep === 'confirm'" label="确认意见">
          <el-input v-model="processForm.confirmation_notes" type="textarea" :rows="3" placeholder="请输入确认意见..." />
        </el-form-item>
        <el-form-item v-if="currentStep === 'rectify'" label="整改措施">
          <el-input v-model="processForm.rectification_measures" type="textarea" :rows="4" placeholder="请详细描述整改措施..." />
        </el-form-item>
        <el-form-item v-if="currentStep === 'rectify'" label="预计完成时间">
          <el-date-picker
            v-model="processForm.rectification_deadline"
            type="datetime"
            placeholder="选择预计完成时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item v-if="currentStep === 'verify'" label="验证结果">
          <el-radio-group v-model="processForm.verification_passed">
            <el-radio :value="true">通过</el-radio>
            <el-radio :value="false">不通过</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="currentStep === 'verify'" label="验证说明">
          <el-input v-model="processForm.verification_result" type="textarea" :rows="3" placeholder="请输入验证说明..." />
        </el-form-item>
        <el-form-item v-if="currentStep === 'close'" label="闭环总结">
          <el-input v-model="processForm.closure_summary" type="textarea" :rows="4" placeholder="请输入闭环总结..." />
        </el-form-item>
        <el-form-item v-if="currentStep === 'close'" label="处理人">
          <el-input v-model="processForm.closed_by" placeholder="请输入处理人姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="processDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitProcess" :loading="submitting">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { violationDisposalApi } from '@/api'
import dayjs from 'dayjs'

const detailDialogVisible = ref(false)
const processDialogVisible = ref(false)
const processFormRef = ref(null)
const submitting = ref(false)
const selectedDisposal = ref(null)
const currentStep = ref('')

const disposalList = ref([])
const pendingCount = ref(0)
const notifiedCount = ref(0)
const confirmedCount = ref(0)
const rectifiedCount = ref(0)
const verifiedCount = ref(0)
const closedCount = ref(0)

const filterForm = reactive({
  shooter_name: '',
  status: '',
  violation_level: '',
  is_ammo_suspended: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const processForm = reactive({
  notification_method: 'system',
  notification_content: '',
  responsible_person: '',
  confirmation_notes: '',
  rectification_measures: '',
  rectification_deadline: '',
  verification_passed: true,
  verification_result: '',
  closure_summary: '',
  closed_by: ''
})

const processRules = {
  notification_content: [{ required: true, message: '请输入通知内容', trigger: 'blur' }],
  responsible_person: [{ required: true, message: '请输入责任人', trigger: 'blur' }],
  confirmation_notes: [{ required: true, message: '请输入确认意见', trigger: 'blur' }],
  rectification_measures: [{ required: true, message: '请输入整改措施', trigger: 'blur' }],
  verification_result: [{ required: true, message: '请输入验证说明', trigger: 'blur' }],
  closure_summary: [{ required: true, message: '请输入闭环总结', trigger: 'blur' }],
  closed_by: [{ required: true, message: '请输入处理人', trigger: 'blur' }]
}

const processDialogTitle = computed(() => {
  const map = {
    notify: '通知责任人',
    confirm: '责任人确认',
    rectify: '记录整改',
    verify: '验证整改',
    close: '闭环处置'
  }
  return map[currentStep.value] || '处置'
})

const formatDateTime = (date) => date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'

const getViolationLevelType = (level) => {
  const map = {
    minor: 'warning',
    major: 'danger',
    critical: 'danger'
  }
  return map[level] || 'info'
}

const getStepIndex = (status) => {
  const map = {
    pending: 0,
    notified: 1,
    confirmed: 2,
    rectified: 3,
    verified: 4,
    closed: 5
  }
  return map[status] || 0
}

const getDuration = (start, end = null) => {
  const startDate = dayjs(start)
  const endDate = end ? dayjs(end) : dayjs()
  const hours = endDate.diff(startDate, 'hour')
  if (hours < 24) return `${hours}小时`
  const days = Math.floor(hours / 24)
  const remainHours = hours % 24
  return remainHours > 0 ? `${days}天${remainHours}小时` : `${days}天`
}

const isOverdue = (start, status) => {
  const hours = dayjs().diff(dayjs(start), 'hour')
  if (status === 'pending' && hours > 2) return true
  if (status === 'notified' && hours > 24) return true
  if (status === 'confirmed' && hours > 48) return true
  if (status === 'rectified' && hours > 72) return true
  if (status === 'verified' && hours > 96) return true
  return false
}

const loadDisposals = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size,
      ordering: '-created_at'
    }
    if (filterForm.shooter_name) params.search = filterForm.shooter_name
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.violation_level) params.violation_level = filterForm.violation_level
    if (filterForm.is_ammo_suspended !== '') params.is_ammo_suspended = filterForm.is_ammo_suspended

    const res = await violationDisposalApi.list(params)
    disposalList.value = res.data.results || res.data
    pagination.total = res.data.count || disposalList.value.length

    const all = res.data.results || res.data
    pendingCount.value = all.filter(d => d.status === 'pending').length
    notifiedCount.value = all.filter(d => d.status === 'notified').length
    confirmedCount.value = all.filter(d => d.status === 'confirmed').length
    rectifiedCount.value = all.filter(d => d.status === 'rectified').length
    verifiedCount.value = all.filter(d => d.status === 'verified').length
    closedCount.value = all.filter(d => d.status === 'closed').length
  } catch (e) {
    console.error(e)
    ElMessage.error('加载处置列表失败')
  }
}

const handlePageChange = () => loadDisposals()
const handleSizeChange = () => {
  pagination.page = 1
  loadDisposals()
}

const resetFilter = () => {
  filterForm.shooter_name = ''
  filterForm.status = ''
  filterForm.violation_level = ''
  filterForm.is_ammo_suspended = ''
  pagination.page = 1
  loadDisposals()
}

const viewDetail = (row) => {
  selectedDisposal.value = row
  detailDialogVisible.value = true
}

const notifyResponsible = (row) => {
  selectedDisposal.value = row
  currentStep.value = 'notify'
  processForm.notification_content = `您在${formatDateTime(row.safety_inspection_info?.inspection_time)}因${row.safety_inspection_info?.violation_type}被记录违规，请及时处理。`
  processDialogVisible.value = true
}

const confirmResponsible = (row) => {
  selectedDisposal.value = row
  currentStep.value = 'confirm'
  processForm.responsible_person = row.shooter_info?.name || ''
  processForm.confirmation_notes = ''
  processDialogVisible.value = true
}

const recordRectification = (row) => {
  selectedDisposal.value = row
  currentStep.value = 'rectify'
  processForm.rectification_measures = ''
  processForm.rectification_deadline = dayjs().add(3, 'day').format('YYYY-MM-DD HH:mm:ss')
  processDialogVisible.value = true
}

const verifyRectification = (row) => {
  selectedDisposal.value = row
  currentStep.value = 'verify'
  processForm.verification_passed = true
  processForm.verification_result = ''
  processDialogVisible.value = true
}

const closeDisposal = (row) => {
  selectedDisposal.value = row
  currentStep.value = 'close'
  processForm.closure_summary = ''
  processForm.closed_by = ''
  processDialogVisible.value = true
}

const submitProcess = async () => {
  try {
    if (currentStep.value !== 'verify') {
      await processFormRef.value.validate()
    }
    submitting.value = true

    const data = { ...selectedDisposal.value }
    const now = dayjs().format('YYYY-MM-DD HH:mm:ss')

    switch (currentStep.value) {
      case 'notify':
        data.status = 'notified'
        data.notification_method = processForm.notification_method
        data.notification_content = processForm.notification_content
        data.notified_at = now
        break
      case 'confirm':
        data.status = 'confirmed'
        data.responsible_person = processForm.responsible_person
        data.confirmation_notes = processForm.confirmation_notes
        data.confirmed_at = now
        break
      case 'rectify':
        data.status = 'rectified'
        data.rectification_measures = processForm.rectification_measures
        data.rectification_deadline = processForm.rectification_deadline
        data.rectified_at = now
        break
      case 'verify':
        if (processForm.verification_passed) {
          data.status = 'verified'
        } else {
          data.status = 'confirmed'
          processForm.verification_result += '（整改不通过，要求重新整改）'
        }
        data.verification_result = processForm.verification_result
        data.verified_at = now
        break
      case 'close':
        data.status = 'closed'
        data.closure_summary = processForm.closure_summary
        data.closed_by = processForm.closed_by
        data.closed_at = now
        data.is_ammo_suspended = false
        data.is_score_locked = false
        break
    }

    await violationDisposalApi.update(selectedDisposal.value.id, data)
    ElMessage.success('操作成功')
    processDialogVisible.value = false
    loadDisposals()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const exportData = async () => {
  try {
    const params = { ordering: '-created_at' }
    if (filterForm.shooter_name) params.search = filterForm.shooter_name
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.violation_level) params.violation_level = filterForm.violation_level
    if (filterForm.is_ammo_suspended !== '') params.is_ammo_suspended = filterForm.is_ammo_suspended

    const res = await violationDisposalApi.export(params)
    downloadFile(res, `违规处置_${dayjs().format('YYYYMMDD')}.csv`)
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
  loadDisposals()
})
</script>
