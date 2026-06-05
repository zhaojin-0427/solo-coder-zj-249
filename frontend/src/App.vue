<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="header-content">
        <div class="logo">
          <el-icon :size="32" color="#409EFF"><Aim /></el-icon>
          <span class="title">靶场实弹射击安全管控与弹药追溯系统</span>
        </div>
        <div class="header-info">
          <el-tag type="success" effect="dark">{{ currentTime }}</el-tag>
        </div>
      </div>
    </el-header>
    
    <el-container>
      <el-aside width="220px" class="aside">
        <el-menu
          :default-active="activeMenu"
          class="menu"
          @select="handleMenuSelect"
          background-color="#001529"
          text-color="#fff"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/checkin">
            <el-icon><User /></el-icon>
            <span>射手登记</span>
          </el-menu-item>
          <el-menu-item index="/training-plan">
            <el-icon><Calendar /></el-icon>
            <span>训练计划</span>
          </el-menu-item>
          <el-menu-item index="/lane-reservation">
            <el-icon><Tickets /></el-icon>
            <span>靶道预约</span>
          </el-menu-item>
          <el-menu-item index="/ammo-issue">
            <el-icon><Box /></el-icon>
            <span>弹药领用</span>
          </el-menu-item>
          <el-menu-item index="/ammo-batch">
            <el-icon><Coin /></el-icon>
            <span>弹药批次</span>
          </el-menu-item>
          <el-menu-item index="/safety">
            <el-icon><Warning /></el-icon>
            <span>安全巡查</span>
          </el-menu-item>
          <el-menu-item index="/violation-disposal">
            <el-icon><CircleCheck /></el-icon>
            <span>违规处置</span>
          </el-menu-item>
          <el-menu-item index="/risk-warning">
            <el-icon><BellFilled /></el-icon>
            <span>风险预警</span>
          </el-menu-item>
          <el-menu-item index="/score">
            <el-icon><Trophy /></el-icon>
            <span>成绩记录</span>
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据统计</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const activeMenu = ref('/checkin')
const currentTime = ref('')

let timer = null

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const handleMenuSelect = (index) => {
  activeMenu.value = index
  router.push(index)
}

onMounted(() => {
  activeMenu.value = route.path || '/checkin'
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.header {
  background: linear-gradient(90deg, #001529 0%, #002140 100%);
  padding: 0;
  height: 64px;
  line-height: 64px;
  border-bottom: 1px solid #1890ff;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 1px;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.aside {
  background-color: #001529;
  overflow: hidden;
}

.menu {
  border-right: none;
  height: calc(100vh - 64px);
}

.menu :deep(.el-menu-item) {
  height: 56px;
  line-height: 56px;
  margin: 4px 0;
}

.menu :deep(.el-menu-item:hover) {
  background-color: rgba(64, 158, 255, 0.1);
}

.menu :deep(.el-menu-item.is-active) {
  background-color: rgba(64, 158, 255, 0.2);
  border-left: 3px solid #409EFF;
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
