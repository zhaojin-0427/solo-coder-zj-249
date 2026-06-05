<template>
  <div>
    <div class="page-title">
      <el-icon><Box /></el-icon>
      弹药领用 / 归还管理
    </div>

    <div class="card-row">
      <div class="stat-card blue">
        <div class="stat-label">今日领用</div>
        <div class="stat-value">{{ todayIssueCount }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">弹药库存</div>
        <div class="stat-value">{{ totalStock }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">使用中</div>
        <div class="stat-value">{{ activeCount }}</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">今日归还</div>
        <div class="stat-value">{{ todayReturnCount }}</div>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="page-container">
      <el-tab-pane label="弹药领用" name="issue">
        <div class="section-title">
          <el-icon><DocumentAdd /></el-icon>
          新增领用
        </div>

        <el-form :model="issueForm" :rules="issueRules" ref="issueFormRef" label-width="120px">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="签到射手" prop="checkin">
                <el-select
                  v-model="issueForm.checkin"
                  filterable
                  placeholder="选择已签到的射手"
                  style="width: 100%"
                  @change="onCheckinChange"
                >
                  <el-option
                    v-for="item in availableCheckins"
                    :key="item.id"
                    :label="`${item.shooter_info?.name} - ${item.shooter_info?.unit}`"
                    :value="item.id"
                  >
                    <span style="float: left">{{ item.shooter_info?.name }}</span>
                    <span style="float: right; color: #8492a6; font-size: 13px">
                      {{ item.shooter_info?.unit }}
                    </span>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="弹药类型" prop="ammunition">
                <el-select
                  v-model="issueForm.ammunition"
                  filterable
                  placeholder="选择弹药"
                  style="width: 100%"
                  @change="onAmmoChange"
                >
                  <el-option
                    v-for="item in ammunitions"
                    :key="item.id"
                    :label="`${item.name} (库存: ${item.stock_quantity}发)`"
                    :value="item.id"
                    :disabled="item.stock_quantity === 0"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="领用数量" prop="issue_quantity">
                <el-input-number
                  v-model="issueForm.issue_quantity"
                  :min="1"
                  :max="maxAmmoQuantity"
                  style="width: 100%"
                />
                <div v-if="selectedAmmo" style="font-size: 12px; color: #909399; margin-top: 4px">
                  当前库存: {{ selectedAmmo.stock_quantity }}发
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="靶道编号" prop="target_lane">
                <el-select
                  v-model="issueForm.target_lane"
                  filterable
                  placeholder="选择靶道"
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in availableLanes"
                    :key="item.id"
                    :label="`${item.lane_number}号 - ${item.name} (${item.distance}米)`"
                    :value="item.id"
                    :disabled="item.status !== 'available'"
                  >
                    <span>{{ item.lane_number }}号 - {{ item.name }}</span>
                    <el-tag
                      :type="item.status === 'available' ? 'success' : 'info'"
                      effect="dark"
                      size="small"
                      style="margin-left: 8px"
                    >
                      {{ item.status_display }}
                    </el-tag>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="枪械" prop="firearm">
                <el-select
                  v-model="issueForm.firearm"
                  filterable
                  placeholder="选择枪械"
                  style="width: 100%"
                >
                  <el-option
                    v-for="item in availableFirearms"
                    :key="item.id"
                    :label="`${item.name} (${item.serial_number})`"
                    :value="item.id"
                    :disabled="item.status !== 'available'"
                  >
                    <span>{{ item.name }}</span>
                    <el-tag
                      :type="item.status === 'available' ? 'success' : 'info'"
                      effect="dark"
                      size="small"
                      style="margin-left: 8px"
                    >
                      {{ item.status_display }}
                    </el-tag>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="发弹员">
                <el-input v-model="issueForm.issuer" placeholder="请输入发弹员姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="预计归还时间">
                <el-date-picker
                  v-model="issueForm.expected_return_time"
                  type="datetime"
                  placeholder="选择预计归还时间"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="备注">
            <el-input v-model="issueForm.remarks" type="textarea" :rows="2" placeholder="请输入备注" />
          </el-form-item>

          <el-form-item style="text-align: center">
            <el-button type="primary" size="large" @click="submitIssue" :loading="submitting">
              <el-icon><Check /></el-icon>
              确认领用
            </el-button>
            <el-button size="large" @click="resetIssueForm">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>

        <el-divider />

        <div class="section-title">
          <el-icon><List /></el-icon>
          待归还记录
        </div>

        <el-table :data="activeIssues" style="width: 100%">
          <el-table-column label="射手" width="120">
            <template #default="{ row }">
              {{ row.shooter_info?.name }}
            </template>
          </el-table-column>
          <el-table-column label="所属单位" width="150">
            <template #default="{ row }">
              {{ row.shooter_info?.unit }}
            </template>
          </el-table-column>
          <el-table-column label="弹药" width="150">
            <template #default="{ row }">
              {{ row.ammunition_info?.name }}
            </template>
          </el-table-column>
          <el-table-column label="领用数量" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="primary" effect="dark">{{ row.issue_quantity }}发</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="靶道" width="120">
            <template #default="{ row }">
              {{ row.target_lane_info?.lane_number }}号
            </template>
          </el-table-column>
          <el-table-column label="枪械" width="180">
            <template #default="{ row }">
              {{ row.firearm_info?.name }}
            </template>
          </el-table-column>
          <el-table-column label="领用时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.issue_time) }}
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'issued' ? 'warning' : 'success'" effect="dark" size="small">
                {{ row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="openReturnDialog(row)">
                归还
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="弹药归还" name="return">
        <div class="section-title">
          <el-icon><RefreshRight /></el-icon>
          弹药归还登记
        </div>

        <el-alert
          title="请仔细核对弹药消耗数量和弹壳回收情况"
          type="warning"
          :closable="false"
          style="margin-bottom: 24px"
        />

        <el-form :model="returnForm" :rules="returnRules" ref="returnFormRef" label-width="140px">
          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="领用记录" prop="ammo_issue">
                <el-select
                  v-model="returnForm.ammo_issue"
                  filterable
                  placeholder="选择领用记录"
                  style="width: 100%"
                  @change="onIssueChange"
                >
                  <el-option
                    v-for="item in activeIssues"
                    :key="item.id"
                    :label="`${item.shooter_info?.name} - ${item.ammunition_info?.name} x${item.issue_quantity}`"
                    :value="item.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="领用数量">
                <el-input v-model="returnForm.issued_quantity" disabled />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="收弹员" prop="receiver">
                <el-input v-model="returnForm.receiver" placeholder="请输入收弹员姓名" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">弹药核对</el-divider>

          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="实际消耗数量" prop="consumed_quantity">
                <el-input-number
                  v-model="returnForm.consumed_quantity"
                  :min="0"
                  :max="returnForm.issued_quantity"
                  style="width: 100%"
                  @change="calculateReturn"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="应归还数量">
                <el-input v-model="returnForm.returned_quantity" disabled />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="数量核对">
                <el-tag :type="returnForm.quantity_verified ? 'success' : 'danger'" effect="dark" size="large">
                  {{ returnForm.quantity_verified ? '已核对' : '待核对' }}
                </el-tag>
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">弹壳回收</el-divider>

          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="消耗数量">
                <el-input v-model="returnForm.consumed_quantity" disabled />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="实际回收弹壳" prop="shell_casing_returned">
                <el-input-number
                  v-model="returnForm.shell_casing_returned"
                  :min="0"
                  :max="returnForm.consumed_quantity"
                  style="width: 100%"
                  @change="calculateShellMissing"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="缺失弹壳">
                <el-tag
                  :type="returnForm.shell_casing_missing === 0 ? 'success' : 'danger'"
                  effect="dark"
                  size="large"
                >
                  {{ returnForm.shell_casing_missing }}发
                </el-tag>
              </el-form-item>
            </el-col>
          </el-row>

          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="弹壳核对">
                <el-tag :type="returnForm.shell_casing_verified ? 'success' : 'warning'" effect="dark" size="large">
                  {{ returnForm.shell_casing_verified ? '全部回收' : '有缺失' }}
                </el-tag>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="备注">
            <el-input
              v-model="returnForm.remarks"
              type="textarea"
              :rows="2"
              placeholder="如有弹壳缺失，请注明原因..."
            />
          </el-form-item>

          <el-form-item style="text-align: center">
            <el-button type="success" size="large" @click="submitReturn" :loading="returning">
              <el-icon><Check /></el-icon>
              确认归还
            </el-button>
            <el-button size="large" @click="resetReturnForm">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="领用记录" name="records">
        <div class="section-title">
          <el-icon><List /></el-icon>
          领用/归还历史记录
        </div>

        <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
          <el-form-item label="射手">
            <el-input v-model="filterForm.shooter_name" placeholder="输入姓名" clearable style="width: 150px" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px">
              <el-option label="已领用" value="issued" />
              <el-option label="归还中" value="returning" />
              <el-option label="已完成" value="completed" />
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
            <el-button type="primary" @click="loadIssueRecords">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
            <el-button @click="resetFilter">
              <el-icon><Refresh /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>

        <el-table :data="issueRecords" style="width: 100%">
          <el-table-column label="射手" width="100">
            <template #default="{ row }">
              {{ row.shooter_info?.name }}
            </template>
          </el-table-column>
          <el-table-column label="弹药" width="150">
            <template #default="{ row }">
              {{ row.ammunition_info?.name }}
            </template>
          </el-table-column>
          <el-table-column label="领用" width="80" align="center">
            <template #default="{ row }">{{ row.issue_quantity }}</template>
          </el-table-column>
          <el-table-column label="靶道" width="80" align="center">
            <template #default="{ row }">{{ row.target_lane_info?.lane_number }}号</template>
          </el-table-column>
          <el-table-column label="枪械" width="150">
            <template #default="{ row }">
              {{ row.firearm_info?.name }}
            </template>
          </el-table-column>
          <el-table-column label="领用时间" width="160">
            <template #default="{ row }">{{ formatTime(row.issue_time) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag
                :type="row.status === 'completed' ? 'success' : row.status === 'issued' ? 'warning' : 'info'"
                effect="dark"
                size="small"
              >
                {{ row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="发弹员" width="100" prop="issuer" />
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

    <el-dialog v-model="returnDialogVisible" title="弹药归还" width="600px">
      <div v-if="selectedIssue">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="射手">{{ selectedIssue.shooter_info?.name }}</el-descriptions-item>
          <el-descriptions-item label="所属单位">{{ selectedIssue.shooter_info?.unit }}</el-descriptions-item>
          <el-descriptions-item label="弹药">{{ selectedIssue.ammunition_info?.name }}</el-descriptions-item>
          <el-descriptions-item label="领用数量">{{ selectedIssue.issue_quantity }}发</el-descriptions-item>
          <el-descriptions-item label="靶道">{{ selectedIssue.target_lane_info?.lane_number }}号</el-descriptions-item>
          <el-descriptions-item label="枪械">{{ selectedIssue.firearm_info?.name }}</el-descriptions-item>
        </el-descriptions>

        <el-form :model="quickReturnForm" label-width="120px" style="margin-top: 20px">
          <el-form-item label="实际消耗" required>
            <el-input-number
              v-model="quickReturnForm.consumed_quantity"
              :min="0"
              :max="selectedIssue.issue_quantity"
            />
          </el-form-item>
          <el-form-item label="弹壳回收" required>
            <el-input-number
              v-model="quickReturnForm.shell_casing_returned"
              :min="0"
              :max="quickReturnForm.consumed_quantity"
            />
          </el-form-item>
          <el-form-item label="收弹员">
            <el-input v-model="quickReturnForm.receiver" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="quickReturnForm.remarks" type="textarea" :rows="2" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="returnDialogVisible = false">取消</el-button>
        <el-button type="success" @click="quickReturn">确认归还</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  checkInApi, ammunitionApi, firearmApi, targetLaneApi,
  ammoIssueApi, ammoReturnApi
} from '@/api'
import dayjs from 'dayjs'

const activeTab = ref('issue')
const issueFormRef = ref(null)
const returnFormRef = ref(null)
const submitting = ref(false)
const returning = ref(false)
const returnDialogVisible = ref(false)
const selectedIssue = ref(null)

const availableCheckins = ref([])
const ammunitions = ref([])
const firearms = ref([])
const targetLanes = ref([])
const activeIssues = ref([])
const issueRecords = ref([])
const todayIssueCount = ref(0)
const todayReturnCount = ref(0)
const totalStock = ref(0)
const activeCount = ref(0)

const issueForm = reactive({
  checkin: null,
  shooter: null,
  ammunition: null,
  issue_quantity: 10,
  target_lane: null,
  firearm: null,
  issuer: '',
  expected_return_time: '',
  remarks: ''
})

const issueRules = {
  checkin: [{ required: true, message: '请选择射手', trigger: 'change' }],
  ammunition: [{ required: true, message: '请选择弹药', trigger: 'change' }],
  issue_quantity: [{ required: true, message: '请输入领用数量', trigger: 'blur' }],
  target_lane: [{ required: true, message: '请选择靶道', trigger: 'change' }],
  firearm: [{ required: true, message: '请选择枪械', trigger: 'change' }]
}

const returnForm = reactive({
  ammo_issue: null,
  shooter: null,
  ammunition: null,
  issued_quantity: 0,
  consumed_quantity: 0,
  returned_quantity: 0,
  shell_casing_returned: 0,
  shell_casing_missing: 0,
  receiver: '',
  quantity_verified: false,
  shell_casing_verified: false,
  remarks: ''
})

const returnRules = {
  ammo_issue: [{ required: true, message: '请选择领用记录', trigger: 'change' }],
  consumed_quantity: [{ required: true, message: '请输入消耗数量', trigger: 'blur' }],
  shell_casing_returned: [{ required: true, message: '请输入回收弹壳数量', trigger: 'blur' }],
  receiver: [{ required: true, message: '请输入收弹员', trigger: 'blur' }]
}

const quickReturnForm = reactive({
  consumed_quantity: 0,
  shell_casing_returned: 0,
  receiver: '',
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

const selectedAmmo = computed(() => {
  return ammunitions.value.find(a => a.id === issueForm.ammunition)
})

const maxAmmoQuantity = computed(() => {
  return selectedAmmo.value?.stock_quantity || 100
})

const availableLanes = computed(() => targetLanes.value)
const availableFirearms = computed(() => firearms.value)

const formatTime = (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'

const loadData = async () => {
  try {
    const [checkinsRes, ammoRes, firearmRes, lanesRes] = await Promise.all([
      checkInApi.list({ status: 'pass' }),
      ammunitionApi.list(),
      firearmApi.list(),
      targetLaneApi.list()
    ])
    
    availableCheckins.value = (checkinsRes.data.results || checkinsRes.data).filter(c => {
      return !activeIssues.value.some(ai => ai.checkin === c.id)
    })
    ammunitions.value = ammoRes.data.results || ammoRes.data
    firearms.value = firearmRes.data.results || firearmRes.data
    targetLanes.value = lanesRes.data.results || lanesRes.data
    
    totalStock.value = ammunitions.value.reduce((sum, a) => sum + a.stock_quantity, 0)
  } catch (e) {
    console.error(e)
  }
}

const loadActiveIssues = async () => {
  try {
    const res = await ammoIssueApi.list({ status: 'issued' })
    activeIssues.value = res.data.results || res.data
    activeCount.value = activeIssues.value.length
  } catch (e) {
    console.error(e)
  }
}

const loadIssueRecords = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size
    }
    if (filterForm.date) params.issue_time__date = filterForm.date
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.shooter_name) params.search = filterForm.shooter_name
    
    const res = await ammoIssueApi.list(params)
    issueRecords.value = res.data.results || res.data
    pagination.total = res.data.count || issueRecords.value.length
    
    const today = dayjs().format('YYYY-MM-DD')
    todayIssueCount.value = issueRecords.value.filter(r =>
      dayjs(r.issue_time).format('YYYY-MM-DD') === today
    ).length
  } catch (e) {
    console.error(e)
  }
}

const handlePageChange = (page) => {
  pagination.page = page
  loadIssueRecords()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadIssueRecords()
}

const loadReturnRecords = async () => {
  try {
    const res = await ammoReturnApi.list()
    const returns = res.data.results || res.data
    const today = dayjs().format('YYYY-MM-DD')
    todayReturnCount.value = returns.filter(r =>
      dayjs(r.return_time).format('YYYY-MM-DD') === today
    ).length
  } catch (e) {
    console.error(e)
  }
}

const onCheckinChange = (val) => {
  const checkin = availableCheckins.value.find(c => c.id === val)
  if (checkin) {
    issueForm.shooter = checkin.shooter
  }
}

const onAmmoChange = () => {
  issueForm.issue_quantity = Math.min(issueForm.issue_quantity, maxAmmoQuantity.value)
}

const calculateReturn = () => {
  returnForm.returned_quantity = returnForm.issued_quantity - returnForm.consumed_quantity
  returnForm.quantity_verified = returnForm.returned_quantity >= 0
}

const calculateShellMissing = () => {
  returnForm.shell_casing_missing = returnForm.consumed_quantity - returnForm.shell_casing_returned
  returnForm.shell_casing_verified = returnForm.shell_casing_missing === 0
}

const onIssueChange = (val) => {
  const issue = activeIssues.value.find(i => i.id === val)
  if (issue) {
    returnForm.ammo_issue = issue.id
    returnForm.shooter = issue.shooter
    returnForm.ammunition = issue.ammunition
    returnForm.issued_quantity = issue.issue_quantity
    returnForm.consumed_quantity = issue.issue_quantity
    calculateReturn()
    returnForm.shell_casing_returned = issue.issue_quantity
    calculateShellMissing()
  }
}

const openReturnDialog = (row) => {
  selectedIssue.value = row
  quickReturnForm.consumed_quantity = row.issue_quantity
  quickReturnForm.shell_casing_returned = row.issue_quantity
  quickReturnForm.receiver = ''
  quickReturnForm.remarks = ''
  returnDialogVisible.value = true
}

const quickReturn = async () => {
  try {
    const data = {
      ammo_issue: selectedIssue.value.id,
      shooter: selectedIssue.value.shooter,
      ammunition: selectedIssue.value.ammunition,
      issued_quantity: selectedIssue.value.issue_quantity,
      consumed_quantity: quickReturnForm.consumed_quantity,
      returned_quantity: selectedIssue.value.issue_quantity - quickReturnForm.consumed_quantity,
      shell_casing_returned: quickReturnForm.shell_casing_returned,
      shell_casing_missing: quickReturnForm.consumed_quantity - quickReturnForm.shell_casing_returned,
      receiver: quickReturnForm.receiver || '系统管理员',
      quantity_verified: true,
      shell_casing_verified: quickReturnForm.consumed_quantity === quickReturnForm.shell_casing_returned,
      remarks: quickReturnForm.remarks
    }
    
    await ammoReturnApi.create(data)
    ElMessage.success('弹药归还成功')
    returnDialogVisible.value = false
    loadAll()
  } catch (e) {
    console.error(e)
  }
}

const submitIssue = async () => {
  try {
    await issueFormRef.value.validate()
    await ElMessageBox.confirm('确认领用弹药吗？', '确认', { type: 'info' })
    
    submitting.value = true
    await ammoIssueApi.create(issueForm)
    ElMessage.success('弹药领用成功')
    resetIssueForm()
    loadAll()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const submitReturn = async () => {
  try {
    await returnFormRef.value.validate()
    await ElMessageBox.confirm('确认归还弹药吗？', '确认', { type: 'info' })
    
    returning.value = true
    await ammoReturnApi.create(returnForm)
    ElMessage.success('弹药归还成功')
    resetReturnForm()
    loadAll()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    returning.value = false
  }
}

const resetIssueForm = () => {
  Object.assign(issueForm, {
    checkin: null,
    shooter: null,
    ammunition: null,
    issue_quantity: 10,
    target_lane: null,
    firearm: null,
    issuer: '',
    expected_return_time: '',
    remarks: ''
  })
  issueFormRef.value?.resetFields()
}

const resetReturnForm = () => {
  Object.assign(returnForm, {
    ammo_issue: null,
    shooter: null,
    ammunition: null,
    issued_quantity: 0,
    consumed_quantity: 0,
    returned_quantity: 0,
    shell_casing_returned: 0,
    shell_casing_missing: 0,
    receiver: '',
    quantity_verified: false,
    shell_casing_verified: false,
    remarks: ''
  })
  returnFormRef.value?.resetFields()
}

const resetFilter = () => {
  filterForm.shooter_name = ''
  filterForm.status = ''
  filterForm.date = ''
  pagination.page = 1
  loadIssueRecords()
}

const loadAll = () => {
  loadActiveIssues()
  loadData()
  loadIssueRecords()
  loadReturnRecords()
}

onMounted(() => {
  loadActiveIssues().then(() => loadData())
  loadIssueRecords()
  loadReturnRecords()
})
</script>
