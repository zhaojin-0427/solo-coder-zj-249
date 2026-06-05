<template>
  <div>
    <div class="page-title">
      <el-icon><Coin /></el-icon>
      弹药批次追溯
    </div>

    <div class="card-row">
      <div class="stat-card blue">
        <div class="stat-label">总批次</div>
        <div class="stat-value">{{ totalBatches }}</div>
      </div>
      <div class="stat-card green">
        <div class="stat-label">在库批次</div>
        <div class="stat-value">{{ activeBatches }}</div>
      </div>
      <div class="stat-card orange">
        <div class="stat-label">临期批次</div>
        <div class="stat-value">{{ expiringBatches }}</div>
      </div>
      <div class="stat-card red">
        <div class="stat-label">低库存预警</div>
        <div class="stat-value">{{ lowStockCount }}</div>
      </div>
      <div class="stat-card purple">
        <div class="stat-label">总库存</div>
        <div class="stat-value">{{ totalStock }}发</div>
      </div>
    </div>

    <div class="page-container">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="批次管理" name="batches">
          <div class="section-title">
            <el-icon><List /></el-icon>
            弹药批次列表
          </div>

          <el-form :inline="true" :model="filterForm" style="margin-bottom: 16px">
            <el-form-item label="批次号">
              <el-input v-model="filterForm.batch_number" placeholder="请输入" clearable style="width: 180px" />
            </el-form-item>
            <el-form-item label="弹药类型">
              <el-select v-model="filterForm.ammunition" placeholder="全部" clearable style="width: 150px">
                <el-option
                  v-for="ammo in ammoList"
                  :key="ammo.id"
                  :label="ammo.name"
                  :value="ammo.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 130px">
                <el-option
                  v-for="opt in batchStatusOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="供应商">
              <el-input v-model="filterForm.supplier" placeholder="请输入" clearable style="width: 150px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadBatches">
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
            <el-button type="primary" @click="openBatchDialog">
              <el-icon><Plus /></el-icon>
              新增批次
            </el-button>
            <el-button type="warning" @click="stockIn">
              <el-icon><Bottom /></el-icon>
              入库登记
            </el-button>
            <el-button type="danger" @click="scrapBatch">
              <el-icon><Delete /></el-icon>
              批次报废
            </el-button>
          </div>

          <el-table :data="batchList" style="width: 100%">
            <el-table-column prop="batch_number" label="批次号" width="180" />
            <el-table-column label="弹药类型" width="150">
              <template #default="{ row }">{{ row.ammunition_info?.name }}</template>
            </el-table-column>
            <el-table-column label="规格" width="120">
              <template #default="{ row }">{{ row.ammunition_info?.specification }}</template>
            </el-table-column>
            <el-table-column label="入库数量" width="100" align="center">
              <template #default="{ row }">{{ row.initial_quantity }}发</template>
            </el-table-column>
            <el-table-column label="当前库存" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.current_quantity < row.safety_threshold ? 'danger' : 'success'" effect="dark">
                  {{ row.current_quantity }}发
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="已使用" width="100" align="center">
              <template #default="{ row }">{{ row.initial_quantity - row.current_quantity }}发</template>
            </el-table-column>
            <el-table-column label="安全阈值" width="100" align="center">
              <template #default="{ row }">{{ row.safety_threshold }}发</template>
            </el-table-column>
            <el-table-column label="生产日期" width="120">
              <template #default="{ row }">{{ formatDate(row.production_date) }}</template>
            </el-table-column>
            <el-table-column label="有效期至" width="120">
              <template #default="{ row }">
                <el-tag :type="isExpiring(row.expiry_date) ? 'warning' : 'info'" effect="dark" size="small">
                  {{ formatDate(row.expiry_date) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="供应商" prop="supplier" width="120" />
            <el-table-column label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getBatchStatusType(row.status)" effect="dark" size="small">
                  {{ row.status_display }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewFlow(row)">流向追溯</el-button>
                <el-button size="small" @click="editBatch(row)">编辑</el-button>
                <el-button type="danger" size="small" @click="deleteBatch(row)">删除</el-button>
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
        </el-tab-pane>

        <el-tab-pane label="批次流向" name="flows" v-if="selectedBatch">
          <div class="section-title">
            <el-icon><Connection /></el-icon>
            {{ selectedBatch.batch_number }} - 流向追溯
          </div>

          <el-descriptions :column="3" border style="margin-bottom: 16px">
            <el-descriptions-item label="批次号">{{ selectedBatch.batch_number }}</el-descriptions-item>
            <el-descriptions-item label="弹药类型">{{ selectedBatch.ammunition_info?.name }}</el-descriptions-item>
            <el-descriptions-item label="规格">{{ selectedBatch.ammunition_info?.specification }}</el-descriptions-item>
            <el-descriptions-item label="入库数量">{{ selectedBatch.initial_quantity }}发</el-descriptions-item>
            <el-descriptions-item label="当前库存">{{ selectedBatch.current_quantity }}发</el-descriptions-item>
            <el-descriptions-item label="有效期至">{{ formatDate(selectedBatch.expiry_date) }}</el-descriptions-item>
          </el-descriptions>

          <el-form :inline="true" :model="flowFilter" style="margin-bottom: 16px">
            <el-form-item label="操作类型">
              <el-select v-model="flowFilter.flow_type" placeholder="全部" clearable style="width: 130px">
                <el-option label="入库" value="in" />
                <el-option label="出库" value="out" />
                <el-option label="领用" value="issue" />
                <el-option label="归还" value="return" />
                <el-option label="消耗" value="consume" />
                <el-option label="调整" value="adjust" />
                <el-option label="报废" value="scrap" />
              </el-select>
            </el-form-item>
            <el-form-item label="操作人">
              <el-input v-model="flowFilter.operator" placeholder="请输入" clearable style="width: 120px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadFlows">查询</el-button>
              <el-button @click="resetFlowFilter">重置</el-button>
              <el-button type="success" @click="exportFlows">导出</el-button>
            </el-form-item>
          </el-form>

          <el-timeline>
            <el-timeline-item
              v-for="flow in flowList"
              :key="flow.id"
              :timestamp="formatDateTime(flow.operation_time)"
              :type="getFlowType(flow.flow_type)"
              :color="getFlowColor(flow.flow_type)"
            >
              <el-card shadow="hover">
                <div style="display: flex; justify-content: space-between; align-items: center">
                  <div>
                    <el-tag :type="getFlowType(flow.flow_type)" effect="dark" size="small">
                      {{ flow.flow_type_display }}
                    </el-tag>
                    <span style="margin-left: 12px; font-weight: 600">
                      {{ flow.flow_type === 'in' ? '+' : flow.flow_type === 'out' ? '-' : '' }}
                      {{ flow.quantity }}发
                    </span>
                    <span style="margin-left: 12px; color: #909399">
                      操作人: {{ flow.operator || '系统' }}
                    </span>
                  </div>
                  <el-tag size="small" v-if="flow.related_record">
                    关联: {{ flow.related_record_type }} #{{ flow.related_record }}
                  </el-tag>
                </div>
                <div style="margin-top: 8px; color: #606266; font-size: 13px">
                  {{ flow.remarks || '无备注' }}
                </div>
                <div style="margin-top: 4px; color: #909399; font-size: 12px">
                  操作后库存: {{ flow.balance_after }}发
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>

          <el-pagination
            v-model:current-page="flowPagination.page"
            v-model:page-size="flowPagination.size"
            :total="flowPagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            style="margin-top: 16px; justify-content: flex-end; display: flex"
            @current-change="handleFlowPageChange"
            @size-change="handleFlowSizeChange"
          />
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-dialog v-model="batchDialogVisible" :title="isEditBatch ? '编辑批次' : '新增批次'" width="600px">
      <el-form :model="batchForm" :rules="batchRules" ref="batchFormRef" label-width="120px">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="批次号" prop="batch_number">
              <el-input v-model="batchForm.batch_number" placeholder="请输入批次号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="弹药类型" prop="ammunition">
              <el-select v-model="batchForm.ammunition" filterable placeholder="选择弹药" style="width: 100%">
                <el-option
                  v-for="ammo in ammoList"
                  :key="ammo.id"
                  :label="`${ammo.name} (${ammo.specification})`"
                  :value="ammo.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="入库数量" prop="initial_quantity">
              <el-input-number v-model="batchForm.initial_quantity" :min="1" :max="100000" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安全阈值" prop="safety_threshold">
              <el-input-number v-model="batchForm.safety_threshold" :min="0" :max="10000" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="生产日期" prop="production_date">
              <el-date-picker
                v-model="batchForm.production_date"
                type="date"
                placeholder="选择生产日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="有效期至" prop="expiry_date">
              <el-date-picker
                v-model="batchForm.expiry_date"
                type="date"
                placeholder="选择有效期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="供应商" prop="supplier">
              <el-input v-model="batchForm.supplier" placeholder="请输入供应商" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="batchForm.status" style="width: 100%">
                <el-option label="在库" value="in_stock" />
                <el-option label="部分使用" value="partial" />
                <el-option label="已用完" value="exhausted" />
                <el-option label="已过期" value="expired" />
                <el-option label="已报废" value="scrapped" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注">
          <el-input v-model="batchForm.remarks" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveBatch" :loading="submitting">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ammoBatchApi, ammoBatchFlowApi, ammunitionApi } from '@/api'
import {
  formatDate, formatDateTime, getBatchStatusType,
  getFlowType, getFlowColor, isExpiring, downloadFile
} from '@/utils'
import {
  getFilterOptions, buildFilterParams, buildPaginationParams,
  adaptAmmoBatchFlow
} from '@/adapters'
import dayjs from 'dayjs'

const activeTab = ref('batches')
const batchDialogVisible = ref(false)
const batchFormRef = ref(null)
const submitting = ref(false)
const isEditBatch = ref(false)
const selectedBatch = ref(null)

const batchList = ref([])
const flowList = ref([])
const ammoList = ref([])

const totalBatches = ref(0)
const activeBatches = ref(0)
const expiringBatches = ref(0)
const lowStockCount = ref(0)
const totalStock = ref(0)

const filterForm = reactive({
  batch_number: '',
  ammunition: '',
  status: '',
  supplier: ''
})

const flowFilter = reactive({
  flow_type: '',
  operator: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const flowPagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const batchForm = reactive({
  id: null,
  batch_number: '',
  ammunition: null,
  initial_quantity: 1000,
  current_quantity: 1000,
  safety_threshold: 100,
  production_date: '',
  expiry_date: '',
  supplier: '',
  status: 'in_stock',
  remarks: ''
})

const batchRules = {
  batch_number: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  ammunition: [{ required: true, message: '请选择弹药类型', trigger: 'change' }],
  initial_quantity: [{ required: true, message: '请输入入库数量', trigger: 'blur' }],
  production_date: [{ required: true, message: '请选择生产日期', trigger: 'change' }],
  expiry_date: [{ required: true, message: '请选择有效期', trigger: 'change' }],
  supplier: [{ required: true, message: '请输入供应商', trigger: 'blur' }]
}

const batchStatusOptions = getFilterOptions('ammoBatch', 'quality_status')

const loadAmmoList = async () => {
  try {
    const res = await ammunitionApi.list({ page_size: 10000 })
    ammoList.value = res.data.results || res.data
  } catch (e) {
    console.error(e)
  }
}

const loadBatches = async () => {
  try {
    const params = {
      ...buildPaginationParams(pagination),
      ...buildFilterParams(filterForm, {
        batch_number: 'search',
        supplier: 'manufacturer'
      })
    }

    const res = await ammoBatchApi.list(params)
    batchList.value = res.data.results || res.data
    pagination.total = res.data.count || batchList.value.length

    const all = res.data.results || res.data
    totalBatches.value = pagination.total
    activeBatches.value = all.filter(b => b.status === 'in_stock' || b.status === 'partial').length
    expiringBatches.value = all.filter(b => isExpiring(b.expiry_date) && b.status !== 'expired' && b.status !== 'scrapped').length
    lowStockCount.value = all.filter(b => b.current_quantity < b.safety_threshold && b.status !== 'exhausted').length
    totalStock.value = all.reduce((sum, b) => sum + b.current_quantity, 0)
  } catch (e) {
    console.error(e)
    ElMessage.error('加载批次列表失败')
  }
}

const loadFlows = async () => {
  if (!selectedBatch.value) return
  try {
    const params = {
      ...buildPaginationParams(flowPagination),
      ...buildFilterParams(flowFilter, {
        operator: 'search'
      }),
      ammo_batch: selectedBatch.value.id
    }

    const res = await ammoBatchFlowApi.list(params)
    flowList.value = (res.data.results || res.data)
      .map(f => adaptAmmoBatchFlow(f))
      .sort((a, b) => dayjs(b.operation_time).valueOf() - dayjs(a.operation_time).valueOf())
    flowPagination.total = res.data.count || flowList.value.length
  } catch (e) {
    console.error(e)
  }
}

const handlePageChange = () => loadBatches()
const handleSizeChange = () => {
  pagination.page = 1
  loadBatches()
}

const handleFlowPageChange = () => loadFlows()
const handleFlowSizeChange = () => {
  flowPagination.page = 1
  loadFlows()
}

const resetFilter = () => {
  filterForm.batch_number = ''
  filterForm.ammunition = ''
  filterForm.status = ''
  filterForm.supplier = ''
  pagination.page = 1
  loadBatches()
}

const resetFlowFilter = () => {
  flowFilter.flow_type = ''
  flowFilter.operator = ''
  flowPagination.page = 1
  loadFlows()
}

const openBatchDialog = (row = null) => {
  isEditBatch.value = !!row
  if (row) {
    Object.assign(batchForm, {
      id: row.id,
      batch_number: row.batch_number,
      ammunition: row.ammunition,
      initial_quantity: row.initial_quantity,
      current_quantity: row.current_quantity,
      safety_threshold: row.safety_threshold,
      production_date: row.production_date,
      expiry_date: row.expiry_date,
      supplier: row.supplier,
      status: row.status,
      remarks: row.remarks || ''
    })
  } else {
    Object.assign(batchForm, {
      id: null,
      batch_number: `B${dayjs().format('YYYYMMDDHHmmss')}`,
      ammunition: null,
      initial_quantity: 1000,
      current_quantity: 1000,
      safety_threshold: 100,
      production_date: dayjs().format('YYYY-MM-DD'),
      expiry_date: dayjs().add(3, 'year').format('YYYY-MM-DD'),
      supplier: '',
      status: 'in_stock',
      remarks: ''
    })
  }
  batchDialogVisible.value = true
}

const editBatch = (row) => openBatchDialog(row)

const saveBatch = async () => {
  try {
    await batchFormRef.value.validate()
    submitting.value = true

    if (isEditBatch.value) {
      await ammoBatchApi.update(batchForm.id, batchForm)
      ElMessage.success('更新成功')
    } else {
      await ammoBatchApi.create(batchForm)
      ElMessage.success('创建成功')
    }
    batchDialogVisible.value = false
    loadBatches()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  } finally {
    submitting.value = false
  }
}

const deleteBatch = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该批次吗？删除后相关流向记录也会被清除。', '确认删除', { type: 'warning' })
    await ammoBatchApi.delete(row.id)
    ElMessage.success('删除成功')
    loadBatches()
  } catch (e) {
    if (e !== 'cancel') console.error(e)
  }
}

const viewFlow = (row) => {
  selectedBatch.value = row
  activeTab.value = 'flows'
  flowPagination.page = 1
  loadFlows()
}

const stockIn = () => {
  ElMessage.info('入库登记功能请使用新增批次或调整批次库存')
}

const scrapBatch = () => {
  ElMessage.info('请在批次列表中选择批次进行报废操作')
}

const exportData = async () => {
  try {
    const params = {
      ...buildFilterParams(filterForm, {
        batch_number: 'search',
        supplier: 'manufacturer'
      })
    }

    const res = await ammoBatchApi.export(params)
    downloadFile(res, `弹药批次_${dayjs().format('YYYYMMDD')}.csv`)
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  }
}

const exportFlows = async () => {
  try {
    const params = {
      ...buildFilterParams(flowFilter, {
        operator: 'search'
      }),
      ammo_batch: selectedBatch.value.id
    }

    const res = await ammoBatchFlowApi.export(params)
    downloadFile(res, `批次流向_${dayjs().format('YYYYMMDD')}.csv`)
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadAmmoList()
  loadBatches()
})
</script>
