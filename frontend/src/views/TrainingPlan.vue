<template>
  <div>
    <div class="page-title">
      <el-icon><Calendar /></el-icon>
      训练计划管理
    </div>

    <div class="card-row">
      <div class="stat-card blue">
        <div class="stat-label">总计划数</div>
        <div class="stat-value">{{ totalPlans }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">进行中</div>
        <div class="stat-value">{{ inProgressPlans }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">待排班</div>
        <div class="stat-value">{{ pendingPlans }}</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">已完成</div>
        <div class="stat-value">{{ completedPlans }}</div>
      </div>
    </div>

    <div class="page-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="训练计划列表" name="plans">
          <div class="section-title">
            <el-icon><List /></el-icon>
            训练计划
          </div>

          <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
            <el-form-item label="计划名称">
              <el-input v-model="filterForm.plan_name" placeholder="请输入" clearable style="width: 180px" />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 150px">
                <el-option label="草稿" value="draft" />
                <el-option label="已批准" value="approved" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
            <el-form-item label="训练类型">
              <el-select v-model="filterForm.plan_type" placeholder="全部" clearable style="width: 150px">
                <el-option label="基础训练" value="basic" />
                <el-option label="进阶训练" value="advanced" />
                <el-option label="考核训练" value="exam" />
                <el-option label="应急训练" value="emergency" />
              </el-select>
            </el-form-item>
            <el-form-item label="日期范围">
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
              <el-button type="primary" @click="loadPlans">
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
            <el-button type="primary" @click="openPlanDialog">
              <el-icon><Plus /></el-icon>
              新建训练计划
            </el-button>
          </div>

          <el-table :data="planList" style="width: 100%">
            <el-table-column prop="plan_name" label="计划名称" min-width="150" />
            <el-table-column prop="plan_type_display" label="训练类型" width="100" align="center" />
            <el-table-column label="时间范围" width="220">
              <template #default="{ row }">
                {{ formatDate(row.start_date) }} ~ {{ formatDate(row.end_date) }}
              </template>
            </el-table-column>
            <el-table-column label="目标射手" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="info" effect="dark">{{ row.target_shooters_count }}人</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="每人预计弹数" width="120" align="center">
              <template #default="{ row }">{{ row.total_rounds_per_shooter }}发</template>
            </el-table-column>
            <el-table-column label="完成率" width="150">
              <template #default="{ row }">
                <el-progress :percentage="row.completion_rate || 0" :status="row.completion_rate >= 100 ? 'success' : ''" />
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" effect="dark" size="small">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewSchedule(row)" :disabled="row.status === 'draft'">
                  排班
                </el-button>
                <el-button type="success" size="small" @click="generateSchedules(row)" :disabled="row.status === 'draft' || row.status === 'completed' || row.status === 'cancelled'">
                  智能排班
                </el-button>
                <el-button size="small" @click="editPlan(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deletePlan(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="planPagination.page"
            v-model:page-size="planPagination.size"
            :total="planPagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            style="margin-top: 16px; justify-content: flex-end; display: flex"
            @current-change="handlePlanPageChange"
            @size-change="handlePlanSizeChange"
          />
        </el-tab-pane>

        <el-tab-pane label="排班记录" name="schedules" v-if="selectedPlan">
          <div class="section-title">
            <el-icon><Calendar /></el-icon>
            {{ selectedPlan.plan_name }} - 排班记录
          </div>

          <el-form :inline="true" :model="scheduleFilter" style="margin-bottom: 16px">
            <el-form-item label="射手">
              <el-input v-model="scheduleFilter.shooter_name" placeholder="请输入" clearable style="width: 150px" />
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="scheduleFilter.status" placeholder="全部" clearable style="width: 130px">
                <el-option label="待执行" value="scheduled" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadSchedules">查询</el-button>
              <el-button @click="resetScheduleFilter">重置</el-button>
              <el-button type="success" @click="exportSchedules">导出</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="scheduleList" style="width: 100%">
            <el-table-column label="日期" width="120">
              <template #default="{ row }">{{ formatDate(row.schedule_date) }}</template>
            </el-table-column>
            <el-table-column label="时间段" width="150">
              <template #default="{ row }">{{ row.start_time }} - {{ row.end_time }}</template>
            </el-table-column>
            <el-table-column label="射手" width="100">
              <template #default="{ row }">{{ row.shooter_info?.name }}</template>
            </el-table-column>
            <el-table-column label="靶道" width="100" align="center">
              <template #default="{ row }">{{ row.target_lane_info?.lane_number }}号</template>
            </el-table-column>
            <el-table-column label="枪械" width="150">
              <template #default="{ row }">{{ row.firearm_info?.name }}</template>
            </el-table-column>
            <el-table-column label="分配弹药" width="100" align="center">
              <template #default="{ row }">{{ row.allocated_rounds }}发</template>
            </el-table-column>
            <el-table-column label="实际射击" width="100" align="center">
              <template #default="{ row }">
                <el-tag type="primary" effect="dark">{{ row.actual_rounds || 0 }}发</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getScheduleStatusType(row.status)" effect="dark" size="small">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="editSchedule(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteSchedule(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="schedulePagination.page"
            v-model:page-size="schedulePagination.size"
            :total="schedulePagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            style="margin-top: 16px; justify-content: flex-end; display: flex"
            @current-change="handleSchedulePageChange"
            @size-change="handleScheduleSizeChange"
          />
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="planDialogVisible" :title="isEditPlan ? '编辑训练计划' : '新建训练计划'" width="800px">
      <el-form :model="planForm" :rules="planRules" ref="planFormRef" label-width="120px">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="计划名称" prop="plan_name">
              <el-input v-model="planForm.plan_name" placeholder="请输入计划名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="训练类型" prop="plan_type">
              <el-select v-model="planForm.plan_type" placeholder="请选择" style="width: 100%">
                <el-option label="基础训练" value="basic" />
                <el-option label="进阶训练" value="advanced" />
                <el-option label="考核训练" value="exam" />
                <el-option label="应急训练" value="emergency" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="planForm.start_date"
                type="date"
                placeholder="选择开始日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker
                v-model="planForm.end_date"
                type="date"
                placeholder="选择结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="要求资质等级" prop="required_qualification">
              <el-select v-model="planForm.required_qualification" placeholder="请选择" style="width: 100%">
                <el-option label="初级" value="junior" />
                <el-option label="中级" value="intermediate" />
                <el-option label="高级" value="senior" />
                <el-option label="特级" value="expert" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每人预计弹数" prop="total_rounds_per_shooter">
              <el-input-number v-model="planForm.total_rounds_per_shooter" :min="1" :max="1000" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="每日训练时段" prop="daily_start_time">
              <el-time-picker
                v-model="planForm.daily_start_time"
                placeholder="开始时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 45%"
              />
              <span style="margin: 0 10px">至</span>
              <el-time-picker
                v-model="planForm.daily_end_time"
                placeholder="结束时间"
                format="HH:mm"
                value-format="HH:mm"
                style="width: 45%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="每次训练时长(分钟)" prop="session_duration">
              <el-input-number v-model="planForm.session_duration" :min="30" :max="480" :step="30" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="目标射手" prop="target_shooters">
          <el-select
            v-model="planForm.target_shooters"
            multiple
            filterable
            placeholder="选择目标射手"
            style="width: 100%"
          >
            <el-option
              v-for="shooter in shooterList"
              :key="shooter.id"
              :label="`${shooter.name} - ${shooter.unit} (${shooter.qualification_level_display})`"
              :value="shooter.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="计划弹药类型" prop="planned_ammo_types">
          <el-select
            v-model="planForm.planned_ammo_types"
            multiple
            filterable
            placeholder="选择弹药类型"
            style="width: 100%"
          >
            <el-option
              v-for="ammo in ammoList"
              :key="ammo.id"
              :label="`${ammo.name} (库存: ${ammo.stock_quantity}发)`"
              :value="ammo.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="计划状态" prop="status">
          <el-radio-group v-model="planForm.status">
            <el-radio value="draft">草稿</el-radio>
            <el-radio value="approved">已批准</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="planForm.remarks" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePlan" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="scheduleDialogVisible" :title="isEditSchedule ? '编辑排班' : '新增排班'" width="600px">
      <el-form :model="scheduleForm" :rules="scheduleRules" ref="scheduleFormRef" label-width="120px">
        <el-form-item label="训练日期" prop="schedule_date">
          <el-date-picker
            v-model="scheduleForm.schedule_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-time-picker
                v-model="scheduleForm.start_time"
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
                v-model="scheduleForm.end_time"
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
            <el-form-item label="射手" prop="shooter">
              <el-select v-model="scheduleForm.shooter" filterable placeholder="选择射手" style="width: 100%">
                <el-option
                  v-for="shooter in planShooters"
                  :key="shooter.id"
                  :label="`${shooter.name} (${shooter.qualification_level_display})`"
                  :value="shooter.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分配弹药" prop="allocated_rounds">
              <el-input-number v-model="scheduleForm.allocated_rounds" :min="1" :max="500" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="靶道" prop="target_lane">
              <el-select v-model="scheduleForm.target_lane" filterable placeholder="选择靶道" style="width: 100%">
                <el-option
                  v-for="lane in laneList"
                  :key="lane.id"
                  :label="`${lane.lane_number}号 - ${lane.name} (${lane.distance}米)`"
                  :value="lane.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="枪械" prop="firearm">
              <el-select v-model="scheduleForm.firearm" filterable placeholder="选择枪械" style="width: 100%">
                <el-option
                  v-for="gun in firearmList"
                  :key="gun.id"
                  :label="`${gun.name} (${gun.serial_number})`"
                  :value="gun.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="scheduleForm.status">
            <el-radio value="scheduled">待执行</el-radio>
            <el-radio value="in_progress">进行中</el-radio>
            <el-radio value="completed">已完成</el-radio>
            <el-radio value="cancelled">已取消</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSchedule" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="recommendationDialogVisible" title="智能排班推荐" width="900px">
      <div v-if="recommendations.length > 0">
        <el-alert
          title="以下是基于射手资质、枪械状态、靶道容量、弹药库存和历史违规记录生成的推荐排班"
          type="info"
          :closable="false"
          style="margin-bottom: 16px"
        />

        <el-tabs v-model="recommendationTab">
          <el-tab-pane label="推荐排班" name="recommendations">
            <el-table :data="recommendations" style="width: 100%" max-height="400px">
              <el-table-column type="selection" width="50" />
              <el-table-column label="日期" width="120">
                <template #default="{ row }">{{ formatDate(row.schedule_date) }}</template>
              </el-table-column>
              <el-table-column label="时间段" width="150">
                <template #default="{ row }">{{ row.start_time }} - {{ row.end_time }}</template>
              </el-table-column>
              <el-table-column label="射手" width="100">
                <template #default="{ row }">{{ row.shooter_info?.name }}</template>
              </el-table-column>
              <el-table-column label="靶道" width="80" align="center">
                <template #default="{ row }">{{ row.target_lane_info?.lane_number }}号</template>
              </el-table-column>
              <el-table-column label="枪械" width="120">
                <template #default="{ row }">{{ row.firearm_info?.name }}</template>
              </el-table-column>
              <el-table-column label="分配弹数" width="100" align="center">
                <template #default="{ row }">{{ row.allocated_rounds }}发</template>
              </el-table-column>
              <el-table-column label="匹配度" width="120">
                <template #default="{ row }">
                  <el-progress :percentage="row.match_score || 0" :color="getMatchColor(row.match_score)" />
                </template>
              </el-table-column>
              <el-table-column label="说明" min-width="150">
                <template #default="{ row }">
                  <el-tag v-for="(w, idx) in row.warnings" :key="idx" type="warning" size="small" style="margin-right: 4px">
                    {{ w }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="冲突提醒" name="conflicts">
            <el-table :data="conflicts" style="width: 100%" max-height="400px">
              <el-table-column label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.type === 'lane' ? 'danger' : 'warning'" effect="dark">{{ row.type_display }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column label="说明" prop="message" />
            </el-table>
          </el-tab-pane>
        </el-tabs>

        <div style="margin-top: 16px; text-align: right">
          <el-button @click="recommendationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="applyRecommendations" :disabled="selectedRecommendations.length === 0">
            应用选中的排班 ({{ selectedRecommendations.length }})
          </el-button>
        </div>
      </div>
      <div v-else style="text-align: center; padding: 40px">
        <el-icon :size="48" color="#909399"><Loading /></el-icon>
        <p style="margin-top: 16px; color: #909399">正在生成智能排班推荐...</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  trainingPlanApi, trainingScheduleApi, scheduleRecommendationApi,
  shootersApi, ammunitionApi, targetLaneApi, firearmApi
} from '@/api'
import dayjs from 'dayjs'

const activeTab = ref('plans')
const planDialogVisible = ref(false)
const scheduleDialogVisible = ref(false)
const recommendationDialogVisible = ref(false)
const recommendationTab = ref('recommendations')
const planFormRef = ref(null)
const scheduleFormRef = ref(null)
const submitting = ref(false)
const isEditPlan = ref(false)
const isEditSchedule = ref(false)
const selectedPlan = ref(null)

const planList = ref([])
const scheduleList = ref([])
const shooterList = ref([])
const ammoList = ref([])
const laneList = ref([])
const firearmList = ref([])
const recommendations = ref([])
const conflicts = ref([])
const selectedRecommendations = ref([])

const totalPlans = ref(0)
const inProgressPlans = ref(0)
const pendingPlans = ref(0)
const completedPlans = ref(0)

const filterForm = reactive({
  plan_name: '',
  status: '',
  plan_type: '',
  date_range: []
})

const scheduleFilter = reactive({
  shooter_name: '',
  status: ''
})

const planPagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const schedulePagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const planForm = reactive({
  id: null,
  plan_name: '',
  plan_type: 'basic',
  start_date: '',
  end_date: '',
  required_qualification: '',
  total_rounds_per_shooter: 50,
  daily_start_time: '09:00',
  daily_end_time: '17:00',
  session_duration: 60,
  target_shooters: [],
  planned_ammo_types: [],
  status: 'draft',
  remarks: ''
})

const scheduleForm = reactive({
  id: null,
  training_plan: null,
  schedule_date: '',
  start_time: '',
  end_time: '',
  shooter: null,
  target_lane: null,
  firearm: null,
  allocated_rounds: 50,
  status: 'scheduled'
})

const planRules = {
  plan_name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  plan_type: [{ required: true, message: '请选择训练类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }],
  total_rounds_per_shooter: [{ required: true, message: '请输入预计弹数', trigger: 'blur' }]
}

const scheduleRules = {
  schedule_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }],
  shooter: [{ required: true, message: '请选择射手', trigger: 'change' }],
  target_lane: [{ required: true, message: '请选择靶道', trigger: 'change' }],
  firearm: [{ required: true, message: '请选择枪械', trigger: 'change' }],
  allocated_rounds: [{ required: true, message: '请输入分配弹数', trigger: 'blur' }]
}

const planShooters = computed(() => {
  if (!selectedPlan.value) return []
  return shooterList.value.filter(s => selectedPlan.value.target_shooters?.includes(s.id))
})

const formatDate = (date) => date ? dayjs(date).format('YYYY-MM-DD') : '-'

const getStatusType = (status) => {
  const map = {
    draft: 'info',
    approved: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const getScheduleStatusType = (status) => {
  const map = {
    scheduled: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const getMatchColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

const disabledDate = (time) => {
  if (!selectedPlan.value) return false
  const start = dayjs(selectedPlan.value.start_date)
  const end = dayjs(selectedPlan.value.end_date)
  return time < start.startOf('day') || time > end.endOf('day')
}

const loadOptions = async () => {
  try {
    const [sRes, aRes, lRes, fRes] = await Promise.all([
      shootersApi.list({ page_size: 10000 }),
      ammunitionApi.list({ page_size: 10000 }),
      targetLaneApi.list({ page_size: 10000 }),
      firearmApi.list({ page_size: 10000 })
    ])
    shooterList.value = sRes.data.results || sRes.data
    ammoList.value = aRes.data.results || aRes.data
    laneList.value = lRes.data.results || lRes.data
    firearmList.value = fRes.data.results || fRes.data
  } catch (e) {
    console.error(e)
  }
}

const loadPlans = async () => {
  try {
    const params = {
      page: planPagination.page,
      page_size: planPagination.size
    }
    if (filterForm.plan_name) params.search = filterForm.plan_name
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.plan_type) params.plan_type = filterForm.plan_type
    if (filterForm.date_range?.length === 2) {
      params.start_date__gte = filterForm.date_range[0]
      params.end_date__lte = filterForm.date_range[1]
    }

    const res = await trainingPlanApi.list(params)
    planList.value = res.data.results || res.data
    planPagination.total = res.data.count || planList.value.length

    const all = res.data.results || res.data
    totalPlans.value = planPagination.total
    inProgressPlans.value = all.filter(p => p.status === 'in_progress').length
    pendingPlans.value = all.filter(p => p.status === 'approved' || p.status === 'draft').length
    completedPlans.value = all.filter(p => p.status === 'completed').length
  } catch (e) {
    console.error(e)
    ElMessage.error('加载训练计划失败')
  }
}

const loadSchedules = async () => {
  if (!selectedPlan.value) return
  try {
    const params = {
      page: schedulePagination.page,
      page_size: schedulePagination.size,
      training_plan: selectedPlan.value.id
    }
    if (scheduleFilter.shooter_name) params.search = scheduleFilter.shooter_name
    if (scheduleFilter.status) params.status = scheduleFilter.status

    const res = await trainingScheduleApi.list(params)
    scheduleList.value = res.data.results || res.data
    schedulePagination.total = res.data.count || scheduleList.value.length
  } catch (e) {
    console.error(e)
  }
}

const handlePlanPageChange = () => loadPlans()
const handlePlanSizeChange = () => {
  planPagination.page = 1
  loadPlans()
}

const handleSchedulePageChange = () => loadSchedules()
const handleScheduleSizeChange = () => {
  schedulePagination.page = 1
  loadSchedules()
}

const resetFilter = () => {
  filterForm.plan_name = ''
  filterForm.status = ''
  filterForm.plan_type = ''
  filterForm.date_range = []
  planPagination.page = 1
  loadPlans()
}

const resetScheduleFilter = () => {
  scheduleFilter.shooter_name = ''
  scheduleFilter.status = ''
  schedulePagination.page = 1
  loadSchedules()
}

const openPlanDialog = (row = null) => {
  isEditPlan.value = !!row
  if (row) {
    Object.assign(planForm, {
      id: row.id,
      plan_name: row.plan_name,
      plan_type: row.plan_type,
      start_date: row.start_date,
      end_date: row.end_date,
      required_qualification: row.required_qualification || '',
      total_rounds_per_shooter: row.total_rounds_per_shooter,
      daily_start_time: row.daily_start_time || '09:00',
      daily_end_time: row.daily_end_time || '17:00',
      session_duration: row.session_duration || 60,
      target_shooters: row.target_shooters || [],
      planned_ammo_types: row.planned_ammo_types || [],
      status: row.status,
      remarks: row.remarks || ''
    })
  } else {
    Object.assign(planForm, {
      id: null,
      plan_name: '',
      plan_type: 'basic',
      start_date: '',
      end_date: '',
      required_qualification: '',
      total_rounds_per_shooter: 50,
      daily_start_time: '09:00',
      daily_end_time: '17:00',
      session_duration: 60,
      target_shooters: [],
      planned_ammo_types: [],
      status: 'draft',
      remarks: ''
    })
  }
  planDialogVisible.value = true
}

const editPlan = (row) => openPlanDialog(row)

const savePlan = async () => {
  try {
    await planFormRef.value.validate()
    submitting.value = true

    if (isEditPlan.value) {
      await trainingPlanApi.update(planForm.id, planForm)
      ElMessage.success('更新成功')
    } else {
      await trainingPlanApi.create(planForm)
      ElMessage.success('创建成功')
    }
    planDialogVisible.value = false
    loadPlans()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const deletePlan = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该训练计划吗？', '确认删除', { type: 'warning' })
    await trainingPlanApi.delete(row.id)
    ElMessage.success('删除成功')
    loadPlans()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const viewSchedule = (row) => {
  selectedPlan.value = row
  activeTab.value = 'schedules'
  schedulePagination.page = 1
  loadSchedules()
}

const editSchedule = (row) => {
  isEditSchedule.value = true
  Object.assign(scheduleForm, {
    id: row.id,
    training_plan: row.training_plan,
    schedule_date: row.schedule_date,
    start_time: row.start_time,
    end_time: row.end_time,
    shooter: row.shooter,
    target_lane: row.target_lane,
    firearm: row.firearm,
    allocated_rounds: row.allocated_rounds,
    status: row.status
  })
  scheduleDialogVisible.value = true
}

const saveSchedule = async () => {
  try {
    await scheduleFormRef.value.validate()
    submitting.value = true
    scheduleForm.training_plan = selectedPlan.value.id

    if (isEditSchedule.value) {
      await trainingScheduleApi.update(scheduleForm.id, scheduleForm)
      ElMessage.success('更新成功')
    } else {
      await trainingScheduleApi.create(scheduleForm)
      ElMessage.success('创建成功')
    }
    scheduleDialogVisible.value = false
    loadSchedules()
    loadPlans()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const deleteSchedule = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该排班吗？', '确认删除', { type: 'warning' })
    await trainingScheduleApi.delete(row.id)
    ElMessage.success('删除成功')
    loadSchedules()
    loadPlans()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const generateSchedules = async (row) => {
  selectedPlan.value = row
  recommendationDialogVisible.value = true
  recommendations.value = []
  conflicts.value = []
  selectedRecommendations.value = []

  try {
    const res = await trainingPlanApi.generateSchedules(row.id)
    recommendations.value = res.data.recommendations || []
    conflicts.value = res.data.conflicts || []

    await nextTick()
    recommendationTab.value = 'recommendations'
  } catch (e) {
    console.error(e)
    ElMessage.error('生成智能排班失败')
    recommendationDialogVisible.value = false
  }
}

const applyRecommendations = async () => {
  try {
    await ElMessageBox.confirm(`确定要应用选中的 ${selectedRecommendations.value.length} 条排班吗？`, '确认', { type: 'info' })

    for (const rec of selectedRecommendations.value) {
      const data = {
        training_plan: selectedPlan.value.id,
        schedule_date: rec.schedule_date,
        start_time: rec.start_time,
        end_time: rec.end_time,
        shooter: rec.shooter,
        target_lane: rec.target_lane,
        firearm: rec.firearm,
        allocated_rounds: rec.allocated_rounds,
        status: 'scheduled'
      }
      await trainingScheduleApi.create(data)
    }

    ElMessage.success(`成功应用 ${selectedRecommendations.value.length} 条排班`)
    recommendationDialogVisible.value = false
    activeTab.value = 'schedules'
    loadSchedules()
    loadPlans()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const exportData = async () => {
  try {
    const params = {}
    if (filterForm.plan_name) params.search = filterForm.plan_name
    if (filterForm.status) params.status = filterForm.status
    if (filterForm.plan_type) params.plan_type = filterForm.plan_type

    const res = await trainingPlanApi.export(params)
    downloadFile(res, `训练计划_${dayjs().format('YYYYMMDD')}.csv`)
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  }
}

const exportSchedules = async () => {
  try {
    const params = { training_plan: selectedPlan.value.id }
    if (scheduleFilter.shooter_name) params.search = scheduleFilter.shooter_name
    if (scheduleFilter.status) params.status = scheduleFilter.status

    const res = await trainingScheduleApi.export(params)
    downloadFile(res, `排班记录_${dayjs().format('YYYYMMDD')}.csv`)
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
  loadOptions()
  loadPlans()
})
</script>
