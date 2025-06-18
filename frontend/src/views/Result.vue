<template>
  <div>
    <h1>结果页面</h1>
    <table class="table">
      <thead>
        <tr>
          <th>经度</th>
          <th>纬度</th>
          <th>高程</th>
          <th>图像名称</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="coord in coordinates" :key="coord.id">
          <td>{{ coord.longitude }}</td>
          <td>{{ coord.latitude }}</td>
          <td>{{ coord.elevation }}</td>
          <td>{{ coord.image_name }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { getCoordinates } from '../api/index.js';

export default {
  name: 'ResultPage',
  data() {
    return {
      coordinates: [],
    };
  },
  async created() {
    try {
      this.coordinates = await getCoordinates();
    } catch (error) {
      console.error('获取坐标失败:', error);
    }
  },
};
</script>

<style scoped>
/* 添加样式 */
</style>