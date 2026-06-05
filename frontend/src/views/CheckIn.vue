<template>
  <div>
    <div class="page-title">
      <el-icon><User /></el-icon>
      射手登记 / 签到管理
    </div>

    <div class="card-row">
      <div class="stat-card blue">
        <div class="stat-label">今日签到</div>
        <div class="stat-value">{{ todayCount }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">在册射手</div>
        <div class="stat-value">{{ totalShooters }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">酒精异常</div>
        <div class="stat-value">{{ alcoholWarningCount }}</div>
      </div>
      <div class="stat-card red">
        <div class="stat-label">拒绝入场</div>
        <div class="stat-value">{{ rejectCount }}</div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="page-container">
      <el-tab-pane label="射手签到" name="checkin">
        <div class="section-title">
          <el-icon><DocumentAdd /></el-icon>
          快速签到
        </div>

        <el-steps :active="checkinStep" finish-status="success" class="step-container">
          <el-step title="选择射手" />
          <el-step title="身份核验" />
          <el-step title="酒精测试" />
          <el-step title="心理评估" />
          <el-step title="完成签到" />
        </el-steps>

        <div v-if="checkinStep === 0" class="form-section">
          <el-form :inline="true" :model="searchForm">
            <el-form-item label="搜索射手">
              <el-input
                v-model="searchForm.keyword"
                placeholder="输入姓名/身份证号"
                clearable
                style="width: 280px"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="searchShooters">
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </el-form-item>
          </el-form>

          <el-table :data="filteredShooters" style="width: 100%" @row-click="selectShooter">
            <el-table-column prop="id_card" label="身份证号" width="200" />
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="gender_display" label="性别" width="80" />
            <el-table-column prop="age" label="年龄" width="80" />
            <el-table-column prop="unit" label="所属单位" />
            <el-table-column prop="qualification_level" label="资质等级" width="120" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" effect="dark">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click.stop="selectShooter(row)" :disabled="row.status !== 'active'">
                  选择
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-divider>或</el-divider>

          <div class="section-title">
            <el-icon><Plus /></el-icon>
            新增射手
          </div>
          <el-form :model="newShooterForm" :inline="true" label-width="100px">
            <el-form-item label="身份证号" required>
              <el-input v-model="newShooterForm.id_card" maxlength="18" placeholder="18位身份证号" />
            </el-form-item>
            <el-form-item label="姓名" required>
              <el-input v-model="newShooterForm.name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="性别" required>
              <el-select v-model="newShooterForm.gender" placeholder="请选择">
                <el-option label="男" value="M" />
                <el-option label="女" value="F" />
              </el-select>
            </el-form-item>
            <el-form-item label="年龄" required>
              <el-input-number v-model="newShooterForm.age" :min="18" :max="70" />
            </el-form-item>
            <el-form-item label="所属单位">
              <el-input v-model="newShooterForm.unit" placeholder="请输入单位" />
            </el-form-item>
            <el-form-item label="联系电话">
              <el-input v-model="newShooterForm.phone" placeholder="请输入电话" />
            </el-form-item>
            <el-form-item label="资质等级">
              <el-input v-model="newShooterForm.qualification_level" placeholder="如：一级射手" />
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="addNewShooter">
                <el-icon><Plus /></el-icon>
                新增并选择
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <div v-if="checkinStep === 1" class="form-section step-container">
          <div v-if="selectedShooter" class="info-display">
            <div class="info-item">
              <span class="info-label">姓名</span>
              <span class="info-value">{{ selectedShooter.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">身份证号</span>
              <span class="info-value">{{ selectedShooter.id_card }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">性别</span>
              <span class="info-value">{{ selectedShooter.gender_display }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">年龄</span>
              <span class="info-value">{{ selectedShooter.age }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">所属单位</span>
              <span class="info-value">{{ selectedShooter.unit }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">资质等级</span>
              <span class="info-value">{{ selectedShooter.qualification_level }}</span>
            </div>
          </div>

          <el-form :model="checkinForm" label-width="120px">
            <el-form-item label="核验方式">
              <el-select v-model="checkinForm.id_verify_method" style="width: 300px">
                <el-option label="身份证核验" value="身份证核验" />
                <el-option label="人脸识别" value="人脸识别" />
                <el-option label="身份证+人脸识别" value="身份证+人脸识别" />
              </el-select>
            </el-form-item>
            <el-form-item label="核验结果">
              <el-radio-group v-model="checkinForm.id_verified">
                <el-radio :label="true">
                  <el-tag type="success" effect="dark">核验通过</el-tag>
                </el-radio>
                <el-radio :label="false">
                  <el-tag type="danger" effect="dark">核验失败</el-tag>
                </el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>

          <div style="text-align: center; margin-top: 24px">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="nextStep" :disabled="!checkinForm.id_verified">
              下一步
            </el-button>
          </div>
        </div>

        <div v-if="checkinStep === 2" class="form-section step-container">
          <div class="section-title">
            <el-icon><Warning /></el-icon>
            酒精含量测试
          </div>

          <el-alert
            title="安全提示"
            type="warning"
            :closable="false"
            style="margin-bottom: 24px"
          >
            酒精含量大于20mg/100ml将被拒绝入场
          </el-alert>

          <el-form :model="checkinForm" label-width="150px">
            <el-form-item label="酒精含量(mg/100ml)" required>
              <el-input-number
                v-model="checkinForm.alcohol_value"
                :min="0"
                :max="200"
                :step="0.1"
                :precision="1"
                size="large"
                style="width: 200px"
              />
            </el-form-item>
            <el-form-item label="测试结果">
              <div :class="['status-badge', getAlcoholClass()]" style="font-size: 16px; padding: 8px 24px">
                {{ getAlcoholText() }}
              </div>
            </el-form-item>
          </el-form>

          <div style="text-align: center; margin-top: 24px">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="nextStep">
              下一步
            </el-button>
          </div>
        </div>

        <div v-if="checkinStep === 3" class="form-section step-container">
          <div class="section-title">
            <el-icon><Reading /></el-icon>
            心理状态评估
          </div>

          <el-alert
            title="评估说明"
            type="info"
            :closable="false"
            style="margin-bottom: 24px"
          >
            根据射手当前精神状态进行评估，发现异常应及时干预
          </el-alert>

          <el-form :model="checkinForm" label-width="120px">
            <el-form-item label="心理状态" required>
              <el-radio-group v-model="checkinForm.psychological_status">
                <el-radio value="normal">
                  <el-tag type="success" effect="dark">正常</el-tag>
                </el-radio>
                <el-radio value="warning">
                  <el-tag type="warning" effect="dark">需关注</el-tag>
                </el-radio>
                <el-radio value="abnormal">
                  <el-tag type="danger" effect="dark">异常</el-tag>
                </el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="评估备注">
              <el-input
                v-model="checkinForm.psychological_note"
                type="textarea"
                :rows="3"
                placeholder="请输入心理评估备注信息..."
              />
            </el-form-item>
          </el-form>

          <div style="text-align: center; margin-top: 24px">
            <el-button @click="prevStep">上一步</el-button>
            <el-button type="primary" @click="confirmCheckIn">
              <el-icon><Check /></el-icon>
              确认签到
            </el-button>
          </div>
        </div>

        <div v-if="checkinStep === 4" class="form-section step-container">
          <div style="text-align: center; padding: 40px">
            <el-icon :size="80" :color="checkinForm.status === 'pass' ? '#67c23a' : '#f56c6c'">
              <CircleCheck v-if="checkinForm.status === 'pass'" />
              <CircleClose v-else />
            </el-icon>
            <h2 style="margin: 20px 0">
              {{ checkinForm.status === 'pass' ? '签到成功！' : '已拒绝入场' }}
            </h2>
            <p style="color: #909399; margin-bottom: 24px">
              {{ selectedShooter?.name }} - {{ checkinForm.status === 'pass' ? '可以进入靶场进行射击训练' : '不符合入场条件' }}
            </p>
            <el-button type="primary" @click="resetCheckIn">
              <el-icon><Refresh /></el-icon>
              继续签到
            </el-button>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="签到记录" name="records">
        <div class="section-title">
          <el-icon><List /></el-icon>
          签到历史记录
        </div>

        <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
          <el-form-item label="射手">
            <el-input
              v-model="filterForm.shooter_name"
              placeholder="输入姓名"
              clearable
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px">
              <el-option label="通过" value="pass" />
              <el-option label="拒绝" value="reject" />
              <el-option label="待检查" value="pending" />
            </el-select>
          </el-form-item>
          <el-form-item label="日期">
            <el-date-picker
              v-model="filterForm.date"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="loadCheckInRecords">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetFilter">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>

        <el-table :data="checkInRecords" style="width: 100%">
          <el-table-column prop="id" label="编号" width="80" />
          <el-table-column label="射手" width="120">
            <template #default="{ row }">
              {{ row.shooter_info?.name }}
            </template>
          </el-table-column>
          <el-table-column label="身份证号" width="200">
            <template #default="{ row }">
              {{ row.shooter_info?.id_card }}
            </template>
          </el-table-column>
          <el-table-column label="所属单位">
            <template #default="{ row }">
              {{ row.shooter_info?.unit }}
            </template>
          </el-table-column>
          <el-table-column label="身份核验" width="100">
            <template #default="{ row }">
              <el-tag :type="row.id_verified ? 'success' : 'danger'" effect="dark" size="small">
                {{ row.id_verified ? '通过' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="酒精测试" width="150">
            <template #default="{ row }">
              <span :class="['status-badge', row.alcohol_test === 'pass' ? 'status-pass' : row.alcohol_test === 'warning' ? 'status-warning' : 'status-fail']">
                {{ row.alcohol_value }}mg
              </span>
            </template>
          </el-table-column>
          <el-table-column label="心理状态" width="100">
            <template #default="{ row }">
              <el-tag
                :type="row.psychological_status === 'normal' ? 'success' : row.psychological_status === 'warning' ? 'warning' : 'danger'"
                effect="dark"
                size="small"
              >
                {{ row.psychological_status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="签到状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'pass' ? 'success' : 'danger'" effect="dark" size="small">
                {{ row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="operator" label="操作员" width="120" />
          <el-table-column prop="checkin_time" label="签到时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.checkin_time) }}
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          style="margin-top: 16px; justify-content: flex-end; display: flex"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { shootersApi, checkInApi } from '@/api'
import dayjs from 'dayjs'

const activeTab = ref('checkin')
const checkinStep = ref(0)
const selectedShooter = ref(null)
const shooters = ref([])
const checkInRecords = ref([])
const todayCount = ref(0)
const totalShooters = ref(0)
const alcoholWarningCount = ref(0)
const rejectCount = ref(0)

const searchForm = reactive({
  keyword: ''
})

const newShooterForm = reactive({
  id_card: '',
  name: '',
  gender: 'M',
  age: 25,
  unit: '',
  phone: '',
  qualification_level: ''
})

const checkinForm = reactive({
  id_verified: true,
  id_verify_method: '身份证+人脸识别',
  alcohol_test: 'pass',
  alcohol_value: 0,
  psychological_status: 'normal',
  psychological_note: '',
  status: 'pass',
  operator: '系统管理员',
  remarks: ''
})

const filterForm = reactive({
  shooter_name: '',
  status: '',
  date: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const filteredShooters = computed(() => {
  if (!searchForm.keyword) return shooters.value
  const keyword = searchForm.keyword.toLowerCase()
  return shooters.value.filter(s =>
    s.name.toLowerCase().includes(keyword) ||
    s.id_card.includes(keyword)
  )
})

const formatTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'
}

const getAlcoholClass = () => {
  const val = checkinForm.alcohol_value
  if (val > 20) return 'status-fail'
  if (val > 0) return 'status-warning'
  return 'status-pass'
}

const getAlcoholText = () => {
  const val = checkinForm.alcohol_value
  if (val > 20) return `不合格 (${val}mg/100ml)`
  if (val > 0) return `疑似饮酒 (${val}mg/100ml)`
  return `正常 (0.0mg/100ml)`
}

const loadShooters = async () => {
  try {
    const res = await shootersApi.list({ status: 'active' })
    shooters.value = res.data.results || res.data
    totalShooters.value = shooters.value.length
  } catch (e) {
    console.error(e)
  }
}

const searchShooters = () => {
}

const selectShooter = (shooter) => {
  selectedShooter.value = shooter
  checkinStep.value = 1
}

const addNewShooter = async () => {
  if (!newShooterForm.id_card || !newShooterForm.name) {
    ElMessage.warning('请填写必填信息')
    return
  }
  try {
    const res = await shootersApi.create(newShooterForm)
    ElMessage.success('射手信息添加成功')
    selectedShooter.value = res.data
    checkinStep.value = 1
    loadShooters()
  } catch (e) {
    console.error(e)
  }
}

const prevStep = () => {
  if (checkinStep.value > 0) {
    checkinStep.value--
  }
}

const nextStep = () => {
  if (checkinStep.value < 3) {
    if (checkinStep.value === 2) {
      const val = checkinForm.alcohol_value
      checkinForm.alcohol_test = val > 20 ? 'fail' : val > 0 ? 'warning' : 'pass'
    }
    checkinStep.value++
  }
}

const confirmCheckIn = async () => {
  try {
    await ElMessageBox.confirm('确认完成签到流程吗？', '确认', {
      type: 'info'
    })

    if (checkinForm.alcohol_test === 'fail' || checkinForm.psychological_status === 'abnormal') {
      checkinForm.status = 'reject'
    } else {
      checkinForm.status = 'pass'
    }

    await checkInApi.create({
      shooter: selectedShooter.value.id,
      ...checkinForm
    })

    checkinStep.value = 4
    ElMessage.success(checkinForm.status === 'pass' ? '签到成功' : '已记录拒绝入场')
    loadStatistics()
    loadCheckInRecords()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

const resetCheckIn = () => {
  checkinStep.value = 0
  selectedShooter.value = null
  checkinForm.id_verified = true
  checkinForm.alcohol_value = 0
  checkinForm.alcohol_test = 'pass'
  checkinForm.psychological_status = 'normal'
  checkinForm.psychological_note = ''
  Object.assign(newShooterForm, {
    id_card: '',
    name: '',
    gender: 'M',
    age: 25,
    unit: '',
    phone: '',
    qualification_level: ''
  })
}

const loadCheckInRecords = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size
    }
    if (filterForm.date) {
      params.checkin_time__date = filterForm.date
    }
    if (filterForm.status) {
      params.status = filterForm.status
    }
    if (filterForm.shooter_name) {
      params.search = filterForm.shooter_name
    }
    const res = await checkInApi.list(params)
    checkInRecords.value = res.data.results || res.data
    pagination.total = res.data.count || checkInRecords.value.length
  } catch (e) {
    console.error(e)
  }
}

const resetFilter = () => {
  filterForm.shooter_name = ''
  filterForm.status = ''
  filterForm.date = ''
  pagination.page = 1
  loadCheckInRecords()
}

const handlePageChange = () => {
  loadCheckInRecords()
}

const handleSizeChange = () => {
  pagination.page = 1
  loadCheckInRecords()
}

const loadStatistics = async () => {
  try {
    const res = await checkInApi.list({ page_size: 10000 })
    const allRecords = res.data.results || res.data
    const today = dayjs().format('YYYY-MM-DD')
    todayCount.value = allRecords.filter(r =>
      dayjs(r.checkin_time).format('YYYY-MM-DD') === today
    ).length
    alcoholWarningCount.value = allRecords.filter(r =>
      r.alcohol_test !== 'pass'
    ).length
    rejectCount.value = allRecords.filter(r => r.status === 'reject').length
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  loadShooters()
  loadCheckInRecords()
  loadStatistics()
})
</script>
