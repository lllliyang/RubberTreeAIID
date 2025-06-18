<template>
  <div id="app">
    <router-view />
    <div v-if="isLoggedIn" class="logout-container">

    </div>
  </div>
</template>

<script>
export default {
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token'); // 检查用户是否已登录
    },
  },
  methods: {
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    },
  },
};
</script>

<style>
.logout-container {
  position: absolute; /* 可以根据需要调整位置 */
  top: 20px; /* 距离顶部的距离 */
  right: 20px; /* 距离右侧的距离 */
}

button {
  padding: 10px 15px;
  background-color: #f44336; /* 红色背景 */
  color: white; /* 白色文字 */
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #d32f2f; /* 悬停时的颜色 */
}
</style>