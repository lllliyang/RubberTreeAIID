<template>
  <div class="data-dashboard">
    <h1>Data Dashboard</h1>
    <button @click="openDashboard">Open the data dashboard</button>
  </div>
</template>

<script>
export default {
  methods: {
    openDashboard() {
      // 打开新的页面
      window.open('http://124.220.25.180:3001/#/chart/preview/31635175', '_blank');
    }
  }
}
</script>

<style scoped>
.data-dashboard {
  text-align: center;
  margin: 20px;
}

.data-dashboard button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>