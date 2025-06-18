<template>
  <div class="app-container">
    <!-- 顶部栏 -->
    <div class="header">
      <img src="@/assets/logo.png" alt="Logo" class="logo" />
      <h2>RubberAIID</h2>
    </div>

    <!-- 主体区域 -->
    <div class="main-content">
      <!-- 侧边导航 -->
      <div class="sidebar">
        <ul>
          <li
            class="nav-item"
            :class="{ active: currentPage === 'home' }"
            @click="currentPage = 'home'"
          >
            Home page
          </li>
          <li class="nav-item" @click="openDashboard">
            Data dashboard
          </li>
          <li
            class="nav-item"
            :class="{ active: currentPage === 'input' }"
            @click="currentPage = 'input'"
          >
            Information input
          </li>
          <li
            class="nav-item"
            :class="{ active: currentPage === 'recognition' }"
            @click="currentPage = 'recognition'"
          >
            Intelligent recognition
          </li>
          <li class="nav-item" @click="goToLogin">
            Exit
          </li>
        </ul>
      </div>

      <!-- 右侧内容区域 -->
      <div class="content">
        <div class="container mt-5">
          <Home v-if="currentPage === 'home'" />
          <InputData v-if="currentPage === 'input'" />
          <FileUpload v-if="currentPage === 'recognition'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Home from '@/views/Home.vue';
import InputData from './InputData.vue';
import FileUpload from './FileUpload.vue';

export default {
  name: 'ProcessPage',
  components: {
    Home,
    InputData,
    FileUpload,
  },
  data() {
    return {
      currentPage: 'home',
    };
  },
  methods: {
    goToLogin() {
      this.$router.push('/login');
    },
    openDashboard() {
      window.open('http://124.220.25.180:3001/#/chart/preview/31635175', '_blank');
    },
  },
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f3f4f6;
}

.header {
  background-color: #2563eb;
  color: white;
  padding: 16px 32px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo {
  width: 48px;
  height: auto;
  margin-right: 15px;
}

.header h2 {
  font-size: 22px;
  font-weight: 600;
  margin: 0;
}

.main-content {
  display: flex;
  flex: 1;
}

.sidebar {
  width: 220px;
  background-color: #ffffff;
  padding: 20px 10px;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 12px 0;
  padding: 12px 18px;
  border-radius: 10px;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-item:hover {
  background-color: #e0e7ff;
  color: #1d4ed8;
}

.nav-item.active {
  background-color: #1d4ed8;
  color: white;
}

.content {
  flex: 1;
  padding: 30px;
  background-color: #f9fafb;
  overflow-y: auto;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  background-color: white;
  border-radius: 12px;
  padding: 24px 32px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
}
</style>
