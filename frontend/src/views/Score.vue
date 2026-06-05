<template>
  <div>
    <div class="page-title">
      <el-icon><Trophy /></el-icon>
      射击成绩记录
    </div>

    <div class="card-row">
      <div class="stat-card blue">
        <div class="stat-label">今日记录</div>
        <div class="stat-value">{{ todayCount }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">平均成绩</div>
        <div class="stat-value">{{ avgScore }}环</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">最高成绩</div>
        <div class="stat-value">{{ maxScore }}环</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">总发射弹数</div>
        <div class="stat-value">{{ totalShots }}</div>
      </div>
    </div>

    <div class="page-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="新增成绩" name="add">
          <div class="section-title">
            <el-icon><DocumentAdd /></el-icon>
            成绩登记
          </div>

          <el-form :model="scoreForm" :rules="scoreRules" ref="scoreFormRef" label-width="120px">
            <el-row :gutter="24">
              <el-col :span="12">
                <el-form-item label="领用记录" prop="ammo_issue">
                  <el-select
                    v-model="scoreForm.ammo_issue"
                    filterable
                    placeholder="选择射击记录"
                    style="width: 100%"
                    @change="onIssueChange"
                  >
                    <el-option
                      v-for="item in activeIssues"
                      :key="item.id"
                      :label="`${item.shooter_info?.name} - ${item.target_lane_info?.lane_number}号靶道`"
                      :value="item.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="记录员" prop="recorder">
                  <el-input v-model="scoreForm.recorder" placeholder="请输入记录员姓名" />
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
                <span class="info-value">{{ selectedIssue.target_lane_info?.lane_number }}号 ({{ selectedIssue.target_lane_info?.distance }}米)</span>
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

            <el-row :gutter="24">
              <el-col :span="6">
                <el-form-item label="发射弹数" prop="shots_fired">
                  <el-input-number
                    v-model="scoreForm.shots_fired"
                    :min="1"
                    :max="maxShots"
                    style="width: 100%"
                    @change="generateScoreDetail"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="总环数" prop="total_score">
                  <el-input-number
                    v-model="scoreForm.total_score"
                    :min="0"
                    :max="scoreForm.shots_fired * 10"
                    :step="0.1"
                    :precision="1"
                    style="width: 100%"
                    @change="updateStats"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="平均环数">
                  <el-input v-model="avgScoreDisplay" disabled />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="命中率">
                  <el-input v-model="hitRateDisplay" disabled />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">环数分布</el-divider>

            <el-row :gutter="24">
              <el-col :span="4">
                <el-form-item label="10环">
                  <el-input-number v-model="scoreForm.ten_ring_count" :min="0" :max="scoreForm.shots_fired" style="width: 100%" @change="updateTotalFromDetail" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="9环">
                  <el-input-number v-model="scoreForm.nine_ring_count" :min="0" :max="scoreForm.shots_fired" style="width: 100%" @change="updateTotalFromDetail" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="8环">
                  <el-input-number v-model="scoreForm.eight_ring_count" :min="0" :max="scoreForm.shots_fired" style="width: 100%" @change="updateTotalFromDetail" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="7环">
                  <el-input-number v-model="scoreForm.seven_ring_count" :min="0" :max="scoreForm.shots_fired" style="width: 100%" @change="updateTotalFromDetail" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="6环">
                  <el-input-number v-model="scoreForm.six_ring_count" :min="0" :max="scoreForm.shots_fired" style="width: 100%" @change="updateTotalFromDetail" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="脱靶">
                  <el-input-number v-model="scoreForm.miss_count" :min="0" :max="scoreForm.shots_fired" style="width: 100%" @change="updateTotalFromDetail" />
                </el-form-item>
              </el-col>
            </el-row>

            <el-divider content-position="left">逐发成绩录入</el-divider>

            <div style="margin-bottom: 16px">
              <el-button type="primary" size="small" @click="generateRandomScores">
                <el-icon><MagicStick /></el-icon>
                随机生成成绩
              </el-button>
              <el-button size="small" @click="clearScores">
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
              <span style="margin-left: 16px; color: #909399; font-size: 12px">
                点击下方输入框可直接录入每发成绩（0-10环）
              </span>
            </div>

            <div class="score-grid">
              <div
                v-for="(score, index) in scoreForm.score_detail"
                :key="index"
                class="score-item"
                :class="getScoreClass(score.score)"
              >
                <div class="shot-num">第{{ index + 1 }}发</div>
                <el-input-number
                  v-model="score.score"
                  :min="0"
                  :max="10"
                  size="small"
                  :controls="false"
                  @change="updateStats"
                  style="width: 80px"
                />
              </div>
            </div>

            <el-form-item label="备注" style="margin-top: 24px">
              <el-input v-model="scoreForm.remarks" type="textarea" :rows="2" placeholder="其他需要说明的情况..." />
            </el-form-item>

            <el-form-item style="text-align: center">
              <el-button type="primary" size="large" @click="submitScore" :loading="submitting">
                <el-icon><Check /></el-icon>
                提交成绩
              </el-button>
              <el-button size="large" @click="resetForm">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="成绩记录" name="records">
          <div class="section-title">
            <el-icon><List /></el-icon>
            成绩历史记录
          </div>

          <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
            <el-form-item label="射手">
              <el-input v-model="filterForm.shooter_name" placeholder="输入姓名" clearable style="width: 150px" />
            </el-form-item>
            <el-form-item label="靶道">
              <el-select v-model="filterForm.target_lane" placeholder="全部" clearable style="width: 150px">
                <el-option v-for="i in 8" :key="i" :label="`${i}号靶道`" :value="i" />
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
              <el-button type="primary" @click="loadRecords">
                <el-icon><Search /></el-icon>
                查询
              </el-button>
              <el-button @click="resetFilter">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </el-form-item>
          </el-form>

          <el-table :data="scoreRecords" style="width: 100%">
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
            <el-table-column label="靶道" width="80" align="center">
              <template #default="{ row }">
                {{ row.target_lane_info?.lane_number }}号
              </template>
            </el-table-column>
            <el-table-column label="枪械" width="150">
              <template #default="{ row }">
                {{ row.firearm_info?.name }}
              </template>
            </el-table-column>
            <el-table-column label="发射" width="80" align="center" prop="shots_fired" />
            <el-table-column label="总环" width="80" align="center" prop="total_score">
              <template #default="{ row }">
                <span style="font-weight: bold; color: #409EFF">{{ row.total_score }}</span>
              </template>
            </el-table-column>
            <el-table-column label="平均" width="80" align="center" prop="average_score">
              <template #default="{ row }">
                {{ row.average_score }}
              </template>
            </el-table-column>
            <el-table-column label="命中" width="80" align="center" prop="hit_count" />
            <el-table-column label="脱靶" width="80" align="center" prop="miss_count">
              <template #default="{ row }">
                <span v-if="row.miss_count > 0" style="color: #f56c6c">{{ row.miss_count }}</span>
                <span v-else style="color: #67c23a">0</span>
              </template>
            </el-table-column>
            <el-table-column label="10环" width="80" align="center" prop="ten_ring_count">
              <template #default="{ row }">
                <span v-if="row.ten_ring_count > 0" style="color: #e6a23c; font-weight: bold">{{ row.ten_ring_count }}</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="记录员" width="100" prop="recorder" />
            <el-table-column label="记录时间" width="160">
              <template #default="{ row }">
                {{ formatTime(row.record_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewDetail(row)">
                  详情
                </el-button>
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

    <el-dialog v-model="detailDialogVisible" title="成绩详情" width="600px">
      <div v-if="currentScore">
        <el-descriptions :column="2" border style="margin-bottom: 20px">
          <el-descriptions-item label="射手">{{ currentScore.shooter_info?.name }}</el-descriptions-item>
          <el-descriptions-item label="所属单位">{{ currentScore.shooter_info?.unit }}</el-descriptions-item>
          <el-descriptions-item label="靶道">{{ currentScore.target_lane_info?.lane_number }}号</el-descriptions-item>
          <el-descriptions-item label="枪械">{{ currentScore.firearm_info?.name }}</el-descriptions-item>
          <el-descriptions-item label="发射弹数">{{ currentScore.shots_fired }}发</el-descriptions-item>
          <el-descriptions-item label="总环数">{{ currentScore.total_score }}环</el-descriptions-item>
          <el-descriptions-item label="平均环数">{{ currentScore.average_score }}环</el-descriptions-item>
          <el-descriptions-item label="命中率">{{ ((currentScore.hit_count / currentScore.shots_fired) * 100).toFixed(1) }}%</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">环数分布</el-divider>
        <el-row :gutter="12" style="margin-bottom: 20px">
          <el-col :span="4"><div class="ring-stat"><span class="ring-num" style="color: #e6a23c">10</span><span class="ring-count">{{ currentScore.ten_ring_count }}</span></div></el-col>
          <el-col :span="4"><div class="ring-stat"><span class="ring-num" style="color: #67c23a">9</span><span class="ring-count">{{ currentScore.nine_ring_count }}</span></div></el-col>
          <el-col :span="4"><div class="ring-stat"><span class="ring-num" style="color: #409EFF">8</span><span class="ring-count">{{ currentScore.eight_ring_count }}</span></div></el-col>
          <el-col :span="4"><div class="ring-stat"><span class="ring-num" style="color: #909399">7</span><span class="ring-count">{{ currentScore.seven_ring_count }}</span></div></el-col>
          <el-col :span="4"><div class="ring-stat"><span class="ring-num" style="color: #909399">6</span><span class="ring-count">{{ currentScore.six_ring_count }}</span></div></el-col>
          <el-col :span="4"><div class="ring-stat"><span class="ring-num" style="color: #f56c6c">脱靶</span><span class="ring-count">{{ currentScore.miss_count }}</span></div></el-col>
        </el-row>

        <el-divider content-position="left">逐发成绩</el-divider>
        <div class="score-grid">
          <div
            v-for="(score, index) in currentScore.score_detail"
            :key="index"
            class="score-item"
            :class="getScoreClass(score.score)"
          >
            <div class="shot-num">第{{ index + 1 }}发</div>
            <div class="shot-score">{{ score.score }}</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ammoIssueApi, scoreRecordApi } from '@/api'
import dayjs from 'dayjs'

const activeTab = ref('add')
const scoreFormRef = ref(null)
const submitting = ref(false)
const detailDialogVisible = ref(false)
const currentScore = ref(null)

const activeIssues = ref([])
const selectedIssue = ref(null)
const scoreRecords = ref([])
const todayCount = ref(0)
const avgScore = ref(0)
const maxScore = ref(0)
const totalShots = ref(0)

const scoreForm = reactive({
  ammo_issue: null,
  shooter: null,
  target_lane: null,
  firearm: null,
  ammunition: null,
  shots_fired: 10,
  total_score: 0,
  average_score: 0,
  hit_count: 0,
  miss_count: 0,
  ten_ring_count: 0,
  nine_ring_count: 0,
  eight_ring_count: 0,
  seven_ring_count: 0,
  six_ring_count: 0,
  below_six_count: 0,
  score_detail: [],
  recorder: '',
  remarks: ''
})

const scoreRules = {
  ammo_issue: [{ required: true, message: '请选择射击记录', trigger: 'change' }],
  shots_fired: [{ required: true, message: '请输入发射弹数', trigger: 'blur' }],
  total_score: [{ required: true, message: '请输入总环数', trigger: 'blur' }],
  recorder: [{ required: true, message: '请输入记录员', trigger: 'blur' }]
}

const filterForm = reactive({
  shooter_name: '',
  target_lane: '',
  date: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const maxShots = computed(() => selectedIssue.value?.issue_quantity || 100)

const avgScoreDisplay = computed(() => {
  if (scoreForm.shots_fired === 0) return '0'
  return (scoreForm.total_score / scoreForm.shots_fired).toFixed(2)
})

const hitRateDisplay = computed(() => {
  if (scoreForm.shots_fired === 0) return '0%'
  const hit = scoreForm.shots_fired - scoreForm.miss_count
  return ((hit / scoreForm.shots_fired) * 100).toFixed(1) + '%'
})

const formatTime = (time) => time ? dayjs(time).format('YYYY-MM-DD HH:mm:ss') : '-'

const getScoreClass = (score) => {
  if (score === 10) return 'score-ten'
  if (score >= 9) return 'score-nine'
  if (score >= 8) return 'score-eight'
  if (score >= 6) return 'score-normal'
  if (score > 0) return 'score-low'
  return 'score-miss'
}

const loadActiveIssues = async () => {
  try {
    const res = await ammoIssueApi.list({ status: 'issued' })
    activeIssues.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const loadRecords = async () => {
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.size
    }
    if (filterForm.date) params.record_time__date = filterForm.date
    if (filterForm.target_lane) params.target_lane = filterForm.target_lane
    if (filterForm.shooter_name) params.search = filterForm.shooter_name

    const res = await scoreRecordApi.list(params)
    scoreRecords.value = res.data.results || res.data
    pagination.total = res.data.count || scoreRecords.value.length

    const today = dayjs().format('YYYY-MM-DD')
    todayCount.value = scoreRecords.value.filter(r =>
      dayjs(r.record_time).format('YYYY-MM-DD') === today
    ).length

    if (scoreRecords.value.length > 0) {
      const totalScore = scoreRecords.value.reduce((sum, r) => sum + r.total_score, 0)
      const totalShotsCount = scoreRecords.value.reduce((sum, r) => sum + r.shots_fired, 0)
      avgScore.value = totalShotsCount > 0 ? (totalScore / totalShotsCount).toFixed(2) : 0
      maxScore.value = Math.max(...scoreRecords.value.map(r => r.total_score))
      totalShots.value = totalShotsCount
    }
  } catch (e) {
    console.error(e)
  }
}

const onIssueChange = (val) => {
  const issue = activeIssues.value.find(i => i.id === val)
  if (issue) {
    selectedIssue.value = issue
    scoreForm.shooter = issue.shooter
    scoreForm.target_lane = issue.target_lane
    scoreForm.firearm = issue.firearm
    scoreForm.ammunition = issue.ammunition
    scoreForm.shots_fired = Math.min(10, issue.issue_quantity)
    generateScoreDetail()
  }
}

const generateScoreDetail = () => {
  scoreForm.score_detail = []
  for (let i = 0; i < scoreForm.shots_fired; i++) {
    scoreForm.score_detail.push({ shot: i + 1, score: 0 })
  }
}

const generateRandomScores = () => {
  const weights = [2, 3, 10, 20, 30, 25, 10]
  const scores = [0, 5, 6, 7, 8, 9, 10]

  for (let i = 0; i < scoreForm.shots_fired; i++) {
    const random = Math.random() * 100
    let sum = 0
    for (let j = 0; j < weights.length; j++) {
      sum += weights[j]
      if (random <= sum) {
        scoreForm.score_detail[i].score = scores[j]
        break
      }
    }
  }
  updateStats()
  updateTotalFromDetail()
}

const clearScores = () => {
  for (let i = 0; i < scoreForm.shots_fired; i++) {
    scoreForm.score_detail[i].score = 0
  }
  updateStats()
  updateTotalFromDetail()
}

const updateStats = () => {
  let total = 0
  let ten = 0, nine = 0, eight = 0, seven = 0, six = 0, below = 0, miss = 0

  scoreForm.score_detail.forEach(s => {
    total += s.score
    if (s.score === 10) ten++
    else if (s.score === 9) nine++
    else if (s.score === 8) eight++
    else if (s.score === 7) seven++
    else if (s.score === 6) six++
    else if (s.score > 0) below++
    else miss++
  })

  scoreForm.total_score = total
  scoreForm.ten_ring_count = ten
  scoreForm.nine_ring_count = nine
  scoreForm.eight_ring_count = eight
  scoreForm.seven_ring_count = seven
  scoreForm.six_ring_count = six
  scoreForm.below_six_count = below
  scoreForm.miss_count = miss
  scoreForm.hit_count = scoreForm.shots_fired - miss
}

const updateTotalFromDetail = () => {
  const total =
    scoreForm.ten_ring_count * 10 +
    scoreForm.nine_ring_count * 9 +
    scoreForm.eight_ring_count * 8 +
    scoreForm.seven_ring_count * 7 +
    scoreForm.six_ring_count * 6 +
    scoreForm.below_six_count * 5

  scoreForm.total_score = total
  scoreForm.hit_count = scoreForm.shots_fired - scoreForm.miss_count
}

const viewDetail = (row) => {
  currentScore.value = row
  detailDialogVisible.value = true
}

const submitScore = async () => {
  try {
    await scoreFormRef.value.validate()
    await ElMessageBox.confirm('确认提交成绩吗？', '确认', { type: 'info' })

    submitting.value = true
    await scoreRecordApi.create(scoreForm)
    ElMessage.success('成绩提交成功')
    resetForm()
    loadRecords()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  Object.assign(scoreForm, {
    ammo_issue: null,
    shooter: null,
    target_lane: null,
    firearm: null,
    ammunition: null,
    shots_fired: 10,
    total_score: 0,
    average_score: 0,
    hit_count: 0,
    miss_count: 0,
    ten_ring_count: 0,
    nine_ring_count: 0,
    eight_ring_count: 0,
    seven_ring_count: 0,
    six_ring_count: 0,
    below_six_count: 0,
    score_detail: [],
    recorder: '',
    remarks: ''
  })
  selectedIssue.value = null
  scoreFormRef.value?.resetFields()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadRecords()
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadRecords()
}

const resetFilter = () => {
  filterForm.shooter_name = ''
  filterForm.target_lane = ''
  filterForm.date = ''
  pagination.page = 1
  loadRecords()
}

onMounted(() => {
  loadActiveIssues()
  loadRecords()
})
</script>

<style scoped>
.score-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.score-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px;
  border-radius: 8px;
  min-width: 100px;
}

.score-item.score-ten {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #8a6d00;
}

.score-item.score-nine {
  background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%);
  color: #2e7d32;
}

.score-item.score-eight {
  background: linear-gradient(135deg, #bbdefb 0%, #90caf9 100%);
  color: #1565c0;
}

.score-item.score-normal {
  background: #f5f5f5;
  color: #666;
}

.score-item.score-low {
  background: #ffebee;
  color: #c62828;
}

.score-item.score-miss {
  background: #ef5350;
  color: #fff;
}

.shot-num {
  font-size: 12px;
  margin-bottom: 4px;
}

.shot-score {
  font-size: 24px;
  font-weight: bold;
}

.ring-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.ring-num {
  font-size: 20px;
  font-weight: bold;
}

.ring-count {
  font-size: 16px;
  color: #303133;
  font-weight: 600;
  margin-top: 4px;
}
</style>
