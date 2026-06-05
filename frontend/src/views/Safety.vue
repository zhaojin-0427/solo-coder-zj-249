<template>
  <div>
    <div class="page-title">
      <el-icon><Warning /></el-icon>
      安全巡查管理
    </div>

    <div class="card-row">
      <div class="stat-card blue">
        <div class="stat-label">今日巡查</div>
        <div class="stat-value">{{ todayInspectionCount }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">轻微违规</div>
        <div class="stat-value">{{ minorCount }}</div>
      </div>
      <div class="stat-card red">
        <div class="stat-label">严重违规</div>
        <div class="stat-value">{{ majorCount }}</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">已暂停训练</div>
        <div class="stat-value">{{ suspendedCount }}</div>
      </div>
    </div>

    <div class="page-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="新增巡查" name="add">
          <div class="section-title">
            <el-icon><DocumentAdd /></el-icon>
            安全巡查登记
          </div>

          <el-form :model="inspectionForm" :rules="inspectionRules" ref="inspectionFormRef" label-width="120px">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="领用记录" prop="ammo_issue">
                  <el-select
                    v-model="inspectionForm.ammo_issue"
                    filterable
                    placeholder="选择正在进行的射击"
                    style="width: 100%"
                    @change="onIssueChange"
                  >
                    <el-option
                      v-for="item in activeIssues"
                      :key="item.id"
                      :label="`${item.shooter_info?.name} - ${item.target_lane_info?.lane_number}号靶道`"
                      :value="item.id"
                    >
                      <span style="float: left">{{ item.shooter_info?.name }}</span>
                      <span style="float: right; color: #8492a6; font-size: 13px">
                        {{ item.target_lane_info?.lane_number }}号靶道
                      </span>
                    </el-option>
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="安全员" prop="inspector">
                  <el-input v-model="inspectionForm.inspector" placeholder="请输入安全员姓名" />
                </el-form-item>
              </el-col>
            </el-row>

            <div v-if="selectedIssue" class="info-display" style="background: #f5f7fa; padding: 16px; border-radius: 8px; margin-bottom: 24px">
              <div class="info-item">
                <span class="info-label">射手</span>
                <span class="info-value">{{ selectedIssue.shooter_info?.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">所属单位</span>
                <span class="info-value">{{ selectedIssue.shooter_info?.unit }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">靶道</span>
                <span class="info-value">{{ selectedIssue.target_lane_info?.lane_number }}号 - {{ selectedIssue.target_lane_info?.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">枪械</span>
                <span class="info-value">{{ selectedIssue.firearm_info?.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">弹药</span>
                <span class="info-value">{{ selectedIssue.ammunition_info?.name }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">领用数量</span>
                <span class="info-value">{{ selectedIssue.issue_quantity }}发</span>
              </div>
            </div>

            <el-alert
              title="安全检查要点"
              type="info"
              :closable="false"
              style="margin-bottom: 24px"
            >
              <ul style="margin: 0; padding-left: 20px">
                <li>是否正确佩戴护目镜、耳塞等防护装备</li>
                <li>枪口指向是否安全，有无违规操作</li>
                <li>是否遵守射击纪律，有无擅自离开射击位</li>
                <li>装弹、退弹操作是否规范</li>
                <li>有无擅自捡拾弹壳等危险行为</li>
              </ul>
            </el-alert>

            <el-row :gutter="24">
              <el-col :span="8">
                <el-form-item label="违规等级" prop="violation_level">
                  <el-radio-group v-model="inspectionForm.violation_level">
                    <el-radio value="none">
                      <el-tag type="success" effect="dark">无违规</el-tag>
                    </el-radio>
                    <el-radio value="minor">
                      <el-tag type="warning" effect="dark">轻微</el-tag>
                    </el-radio>
                    <el-radio value="major">
                      <el-tag type="danger" effect="dark">严重</el-tag>
                    </el-radio>
                    <el-radio value="critical">
                      <el-tag type="danger" effect="dark">重大</el-tag>
                    </el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="违规类型" v-if="inspectionForm.violation_level !== 'none'">
                  <el-select v-model="inspectionForm.violation_type" placeholder="请选择" style="width: 100%">
                    <el-option label="枪口指向违规" value="枪口指向违规" />
                    <el-option label="未戴护具" value="未戴护具" />
                    <el-option label="装弹操作不规范" value="装弹操作不规范" />
                    <el-option label="擅自捡拾弹壳" value="擅自捡拾弹壳" />
                    <el-option label="未经许可进入射击位" value="未经许可进入射击位" />
                    <el-option label="射击纪律散漫" value="射击纪律散漫" />
                    <el-option label="其他违规" value="其他违规" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="扣分" v-if="inspectionForm.violation_level !== 'none'">
                  <el-input-number v-model="inspectionForm.score_deduction" :min="0" :max="100" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24" v-if="inspectionForm.violation_level !== 'none'">
              <el-col :span="12">
                <el-form-item label="违规描述">
                  <el-input
                    v-model="inspectionForm.violation_description"
                    type="textarea"
                    :rows="3"
                    placeholder="请详细描述违规情况..."
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="整改措施">
                  <el-input
                    v-model="inspectionForm.corrective_action"
                    type="textarea"
                    :rows="3"
                    placeholder="请描述采取的整改措施..."
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-row :gutter="24" v-if="inspectionForm.violation_level !== 'none'">
              <el-col :span="12">
                <el-form-item label="是否暂停训练">
                  <el-switch
                    v-model="inspectionForm.is_training_suspended"
                    active-text="是"
                    inactive-text="否"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <el-form-item label="备注">
              <el-input v-model="inspectionForm.remarks" type="textarea" :rows="2" placeholder="其他需要说明的情况..." />
            </el-form-item>

            <el-form-item style="text-align: center">
              <el-button type="primary" size="large" @click="submitInspection" :loading="submitting">
                <el-icon><Check /></el-icon>
                提交巡查记录
              </el-button>
              <el-button size="large" @click="resetForm">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="巡查记录" name="records">
          <div class="section-title">
            <el-icon><List /></el-icon>
            巡查历史记录
          </div>

          <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
            <el-form-item label="射手">
              <el-input v-model="filterForm.shooter_name" placeholder="输入姓名" clearable style="width: 150px" />
            </el-form-item>
            <el-form-item label="违规等级">
              <el-select v-model="filterForm.violation_level" placeholder="全部" clearable style="width: 150px">
                <el-option label="无违规" value="none" />
                <el-option label="轻微违规" value="minor" />
                <el-option label="严重违规" value="major" />
                <el-option label="重大违规" value="critical" />
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
              <el-button type="primary" @click="loadInspections">
                <el-icon><Search /></el-icon>
                查询
              </el-button>
              <el-button @click="resetFilter">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>

          <el-table :data="inspectionRecords" style="width: 100%">
            <el-table-column label="射手" width="100">
              <template #default="{ row }">
                {{ row.shooter_info?.name }}
              </template>
            </el-table-column>
            <el-table-column label="所属单位" width="150">
              <template #default="{ row }">
                {{ row.shooter_info?.unit }}
              </template>
            </el-table-column>
            <el-table-column label="靶道" width="100" align="center">
              <template #default="{ row }">
                {{ row.target_lane_info?.lane_number }}号
              </template>
            </el-table-column>
            <el-table-column label="违规等级" width="100">
              <template #default="{ row }">
                <el-tag
                  :type="getViolationType(row.violation_level)"
                  effect="dark"
                  size="small"
                >
                  {{ row.violation_level_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="违规类型" width="150" prop="violation_type">
              <template #default="{ row }">
                {{ row.violation_type || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="扣分" width="80" align="center" prop="score_deduction">
              <template #default="{ row }">
                <span v-if="row.score_deduction > 0" style="color: #f56c6c; font-weight: bold">
                  -{{ row.score_deduction }}
                </span>
                <span v-else style="color: #909399">-</span>
              </template>
            </el-table-column>
            <el-table-column label="暂停训练" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.is_training_suspended ? 'danger' : 'success'" effect="dark" size="small">
                  {{ row.is_training_suspended ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="安全员" width="100" prop="inspector" />
            <el-table-column label="巡查时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.inspection_time) }}
              </template>
            </el-table-column>
            <el-table-column label="违规描述" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.violation_description || '-' }}
              </template>
            </el-table-column>
            <el-table-column label="整改措施" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.corrective_action || '-' }}
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ammoIssueApi, safetyInspectionApi } from '@/api'
import dayjs from 'dayjs'

const activeTab = ref('add')
const inspectionFormRef = ref(null)
const submitting = ref(false)

const activeIssues = ref([])
const selectedIssue = ref(null)
const inspectionRecords = ref([])
const todayInspectionCount = ref(0)
const minorCount = ref(0)
const majorCount = ref(0)
const suspendedCount = ref(0)

const inspectionForm = reactive({
  ammo_issue: null,
  shooter: null,
  target_lane: null,
  inspector: '',
  violation_level: 'none',
  violation_type: '',
  violation_description: '',
  corrective_action: '',
  score_deduction: 0,
  is_training_suspended: false,
  remarks: ''
})

const inspectionRules = {
  ammo_issue: [{ required: true, message: '请选择射击记录', trigger: 'change' }],
  inspector: [{ required: true, message: '请输入安全员姓名', trigger: 'blur' }],
  violation_level: [{ required: true, message: '请选择违规等级', trigger: 'change' }]
}

const filterForm = reactive({
  shooter_name: '',
  violation_level: '',
  date: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const formatTime = (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'

const getViolationType = (level) => {
  const map = { none: 'success', minor: 'warning', major: 'danger', critical: 'danger' }
  return map[level] || 'info'
}

const loadActiveIssues = async () => {
  try {
    const res = await ammoIssueApi.list({ status: 'issued' })
    activeIssues.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const loadInspections = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size
    }
    if (filterForm.date) params.inspection_time__date = filterForm.date
    if (filterForm.violation_level) params.violation_level = filterForm.violation_level
    if (filterForm.shooter_name) params.search = filterForm.shooter_name

    const res = await safetyInspectionApi.list(params)
    inspectionRecords.value = res.data.results || res.data
    pagination.total = res.data.count || inspectionRecords.value.length

    const today = dayjs().format('YYYY-MM-DD')
    todayInspectionCount.value = inspectionRecords.value.filter(r =>
      dayjs(r.inspection_time).format('YYYY-MM-DD') === today
    ).length
    minorCount.value = inspectionRecords.value.filter(r => r.violation_level === 'minor').length
    majorCount.value = inspectionRecords.value.filter(r =>
      ['major', 'critical'].includes(r.violation_level)
    ).length
    suspendedCount.value = inspectionRecords.value.filter(r => r.is_training_suspended).length
  } catch (e) {
    console.error(e)
  }
}

const handlePageChange = (page) => {
  pagination.page = page
  loadInspections()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadInspections()
}

const onIssueChange = (val) => {
  const issue = activeIssues.value.find(i => i.id === val)
  if (issue) {
    selectedIssue.value = issue
    inspectionForm.shooter = issue.shooter
    inspectionForm.target_lane = issue.target_lane
  }
}

const submitInspection = async () => {
  try {
    await inspectionFormRef.value.validate()
    await ElMessageBox.confirm('确认提交巡查记录吗？', '确认', { type: 'info' })

    submitting.value = true
    await safetyInspectionApi.create(inspectionForm)
    ElMessage.success('巡查记录提交成功')
    resetForm()
    loadInspections()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  Object.assign(inspectionForm, {
    ammo_issue: null,
    shooter: null,
    target_lane: null,
    inspector: '',
    violation_level: 'none',
    violation_type: '',
    violation_description: '',
    corrective_action: '',
    score_deduction: 0,
    is_training_suspended: false,
    remarks: ''
  })
  selectedIssue.value = null
  inspectionFormRef.value?.resetFields()
}

const resetFilter = () => {
  filterForm.shooter_name = ''
  filterForm.violation_level = ''
  filterForm.date = ''
  pagination.page = 1
  loadInspections()
}

onMounted(() => {
  loadActiveIssues()
  loadInspections()
})
</script>
