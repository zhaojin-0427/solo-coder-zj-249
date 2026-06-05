<template>
  <div>
    <div class="page-title">
      <el-icon><Tickets /></el-icon>
      靶道预约管理
    </div>

    <div class="card-row">
      <div class="stat-card blue">
        <div class="stat-label">总预约数</div>
        <div class="stat-value">{{ totalReservations }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">今日预约</div>
        <div class="stat-value">{{ todayReservations }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">进行中</div>
        <div class="stat-value">{{ activeReservations }}</div>
      </div>
      <div class="stat-card red">
        <div class="stat-label">待处理冲突</div>
        <div class="stat-value">{{ conflictCount }}</div>
      </div>
    </div>

    <div class="page-container">
      <div class="section-title">
        <el-icon><List /></el-icon>
        预约列表
      </div>

      <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
        <el-form-item label="射手">
          <el-input v-model="filterForm.shooter_name" placeholder="请输入" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="靶道">
          <el-select v-model="filterForm.target_lane" placeholder="全部" clearable style="width: 130px">
            <el-option
              v-for="lane in laneList"
              :key="lane.id"
              :label="`${lane.lane_number}号`"
              :value="lane.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 130px">
            <el-option label="待确认" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已冲突" value="conflict" />
          </el-select>
        </el-form-item>
        <el-form-item label="预约日期">
          <el-date-picker
            v-model="filterForm.reservation_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadReservations">
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
        <el-button type="primary" @click="openDialog">
          <el-icon><Plus /></el-icon>
          新增预约
        </el-button>
        <el-button type="warning" @click="viewCalendar">
          <el-icon><Calendar /></el-icon>
          日历视图
        </el-button>
      </div>

      <el-table :data="reservationList" style="width: 100%">
        <el-table-column label="预约日期" width="120">
          <template #default="{ row }">{{ formatDate(row.reservation_date) }}</template>
        </el-table-column>
        <el-table-column label="时间段" width="150">
          <template #default="{ row }">{{ row.start_time }} - {{ row.end_time }}</template>
        </el-table-column>
        <el-table-column label="射手" width="100">
          <template #default="{ row }">{{ row.shooter_info?.name }}</template>
        </el-table-column>
        <el-table-column label="所属单位" width="150">
          <template #default="{ row }">{{ row.shooter_info?.unit }}</template>
        </el-table-column>
        <el-table-column label="靶道" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="primary" effect="dark">{{ row.target_lane_info?.lane_number }}号</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="用途" prop="purpose" min-width="150" />
        <el-table-column label="预约人数" width="100" align="center">
          <template #default="{ row }">{{ row.number_of_people }}人</template>
        </el-table-column>
        <el-table-column label="关联训练计划" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.training_plan_info" type="info" effect="dark" size="small">
              {{ row.training_plan_info?.plan_name }}
            </el-tag>
            <span v-else style="color: #909399">无</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark" size="small">
              {{ row.status_display }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="冲突检测" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_conflict" type="danger" effect="dark" size="small">
              有冲突
            </el-tag>
            <el-tag v-else type="success" effect="dark" size="small">
              正常
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              size="small"
              @click="confirmReservation(row)"
            >
              确认
            </el-button>
            <el-button
              v-if="row.status === 'confirmed'"
              type="primary"
              size="small"
              @click="completeReservation(row)"
            >
              完成
            </el-button>
            <el-button size="small" @click="editReservation(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="deleteReservation(row)">取消</el-button>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑预约' : '新增预约'" width="700px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="预约日期" prop="reservation_date">
              <el-date-picker
                v-model="form.reservation_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                :disabled-date="disabledDate"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="靶道" prop="target_lane">
              <el-select v-model="form.target_lane" filterable placeholder="选择靶道" style="width: 100%">
                <el-option
                  v-for="lane in laneList"
                  :key="lane.id"
                  :label="`${lane.lane_number}号 - ${lane.name} (${lane.distance}米)`"
                  :value="lane.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-time-picker
                v-model="form.start_time"
                placeholder="选择开始时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="end_time">
              <el-time-picker
                v-model="form.end_time"
                placeholder="选择结束时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="预约射手" prop="shooter">
              <el-select v-model="form.shooter" filterable placeholder="选择射手" style="width: 100%">
                <el-option
                  v-for="shooter in shooterList"
                  :key="shooter.id"
                  :label="`${shooter.name} - ${shooter.unit}`"
                  :value="shooter.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预约人数" prop="number_of_people">
              <el-input-number v-model="form.number_of_people" :min="1" :max="50" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="关联训练计划" prop="training_plan">
          <el-select v-model="form.training_plan" filterable placeholder="选择训练计划（可选）" clearable style="width: 100%">
            <el-option
              v-for="plan in planList"
              :key="plan.id"
              :label="`${plan.plan_name} (${formatDate(plan.start_date)}~${formatDate(plan.end_date)})`"
              :value="plan.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="用途" prop="purpose">
          <el-input v-model="form.purpose" placeholder="请输入预约用途" />
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.remarks" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>

        <div v-if="conflictWarning" style="margin-bottom: 16px">
          <el-alert
            :title="conflictWarning"
            type="warning"
            :closable="false"
            show-icon
          />
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="checkConflict" :loading="checking">检测冲突</el-button>
        <el-button type="success" @click="save" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { laneReservationApi, shootersApi, targetLaneApi, trainingPlanApi } from '@/api'
import dayjs from 'dayjs'

const dialogVisible = ref(false)
const formRef = ref(null)
const submitting = ref(false)
const checking = ref(false)
const isEdit = ref(false)
const conflictWarning = ref('')

const reservationList = ref([])
const shooterList = ref([])
const laneList = ref([])
const planList = ref([])

const totalReservations = ref(0)
const todayReservations = ref(0)
const activeReservations = ref(0)
const conflictCount = ref(0)

const filterForm = reactive({
  shooter_name: '',
  target_lane: '',
  status: '',
  reservation_date: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const form = reactive({
  id: null,
  reservation_date: '',
  start_time: '',
  end_time: '',
  shooter: null,
  target_lane: null,
  training_plan: null,
  purpose: '',
  number_of_people: 1,
  remarks: '',
  status: 'pending'
})

const rules = {
  reservation_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  shooter: [{ required: true, message: '请选择射手', trigger: 'change' }],
  target_lane: [{ required: true, message: '请选择靶道', trigger: 'change' }],
  purpose: [{ required: true, message: '请输入用途', trigger: 'blur' }]
}

const formatDate = (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
const formatDateTime = (date) => date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'

const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    confirmed: 'primary',
    completed: 'success',
    cancelled: 'info',
    conflict: 'danger'
  }
  return map[status] || 'info'
}

const disabledDate = (time) => {
  return time < dayjs().subtract(1, 'day').endOf('day')
}

const loadOptions = async () => {
  try {
    const [sRes, lRes, pRes] = await Promise.all([
      shootersApi.list({ page_size: 10000 }),
      targetLaneApi.list({ page_size: 10000 }),
      trainingPlanApi.list({ page_size: 10000, status: 'approved' })
    ])
    shooterList.value = sRes.data.results || sRes.data
    laneList.value = lRes.data.results || lRes.data
    planList.value = pRes.data.results || pRes.data
  } catch (e) {
    console.error(e)
  }
}

const loadReservations = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size
    }
    if (filterForm.shooter_name) params.search = filterForm.shooter_name
    if (filterForm.target_lane) params.target_lane = filterForm.target_lane
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.reservation_date) params.reservation_date = filterForm.reservation_date

    const res = await laneReservationApi.list(params)
    reservationList.value = res.data.results || res.data
    pagination.total = res.data.count || reservationList.value.length

    const all = res.data.results || res.data
    totalReservations.value = pagination.total
    todayReservations.value = all.filter(r => dayjs(r.reservation_date).isSame(dayjs(), 'day')).length
    activeReservations.value = all.filter(r => r.status === 'confirmed').length
    conflictCount.value = all.filter(r => r.has_conflict).length
  } catch (e) {
    console.error(e)
    ElMessage.error('加载预约列表失败')
  }
}

const handlePageChange = () => loadReservations()
const handleSizeChange = () => {
  pagination.page = 1
  loadReservations()
}

const resetFilter = () => {
  filterForm.shooter_name = ''
  filterForm.target_lane = ''
  filterForm.status = ''
  filterForm.reservation_date = ''
  pagination.page = 1
  loadReservations()
}

const openDialog = (row = null) => {
  isEdit.value = !!row
  conflictWarning.value = ''
  if (row) {
    Object.assign(form, {
      id: row.id,
      reservation_date: row.reservation_date,
      start_time: row.start_time,
      end_time: row.end_time,
      shooter: row.shooter,
      target_lane: row.target_lane,
      training_plan: row.training_plan,
      purpose: row.purpose,
      number_of_people: row.number_of_people,
      remarks: row.remarks || '',
      status: row.status
    })
  } else {
    Object.assign(form, {
      id: null,
      reservation_date: dayjs().format('YYYY-MM-DD'),
      start_time: '09:00',
      end_time: '10:00',
      shooter: null,
      target_lane: null,
      training_plan: null,
      purpose: '',
      number_of_people: 1,
      remarks: '',
      status: 'pending'
    })
  }
  dialogVisible.value = true
}

const editReservation = (row) => openDialog(row)

const checkConflict = async () => {
  try {
    checking.value = true
    conflictWarning.value = ''

    const params = {
      target_lane: form.target_lane,
      reservation_date: form.reservation_date,
      start_time: form.start_time,
      end_time: form.end_time
    }
    if (form.id) params.exclude_id = form.id

    const res = await laneReservationApi.list(params)
    const conflicts = (res.data.results || res.data).filter(r => r.id !== form.id)

    if (conflicts.length > 0) {
      conflictWarning.value = `检测到 ${conflicts.length} 个时间冲突，请调整预约时间或靶道。冲突预约：${conflicts.map(c => `${c.shooter_info?.name} ${c.start_time}-${c.end_time}`).join('、')}`
    } else {
      conflictWarning.value = ''
      ElMessage.success('未检测到冲突')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('冲突检测失败')
  } finally {
    checking.value = false
  }
}

const save = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    if (isEdit.value) {
      await laneReservationApi.update(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await laneReservationApi.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadReservations()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const confirmReservation = async (row) => {
  try {
    await ElMessageBox.confirm('确定要确认该预约吗？', '确认', { type: 'info' })
    await laneReservationApi.update(row.id, { ...row, status: 'confirmed' })
    ElMessage.success('预约已确认')
    loadReservations()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const completeReservation = async (row) => {
  try {
    await ElMessageBox.confirm('确定要标记该预约为已完成吗？', '确认', { type: 'info' })
    await laneReservationApi.update(row.id, { ...row, status: 'completed' })
    ElMessage.success('预约已完成')
    loadReservations()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const deleteReservation = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消该预约吗？', '确认取消', { type: 'warning' })
    if (row.status === 'cancelled') {
      await laneReservationApi.delete(row.id)
    } else {
      await laneReservationApi.update(row.id, { ...row, status: 'cancelled' })
    }
    ElMessage.success('预约已取消')
    loadReservations()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const viewCalendar = () => {
  ElMessage.info('日历视图功能开发中')
}

const exportData = async () => {
  try {
    const params = {}
    if (filterForm.shooter_name) params.search = filterForm.shooter_name
    if (filterForm.target_lane) params.target_lane = filterForm.target_lane
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.reservation_date) params.reservation_date = filterForm.reservation_date

    const res = await laneReservationApi.export(params)
    downloadFile(res, `靶道预约_${dayjs().format('YYYYMMDD')}.csv`)
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

watch([() => form.target_lane, () => form.reservation_date, () => form.start_time, () => form.end_time], () => {
  conflictWarning.value = ''
})

onMounted(() => {
  loadOptions()
  loadReservations()
})
</script>
