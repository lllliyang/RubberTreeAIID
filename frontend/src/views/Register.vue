<template>
  <div class="container mt-5">
    <h1 class="text-center">用户注册</h1>
    <form @submit.prevent="register">
      <div class="mb-3">
        <label for="username" class="form-label">用户名</label>
        <input type="text" class="form-control" v-model="username" required />
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">密码</label>
        <input type="password" class="form-control" v-model="password" required />
      </div>
      <button type="submit" class="btn btn-primary">注册</button>
      <p v-if="errorMessage" class="text-danger">{{ errorMessage }}</p>
    </form>
    <router-link to="/login">已有账号？登录</router-link>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserRegister', // 修改为多词名称
  data() {
    return {
      username: '',
      password: '',
      errorMessage: '',
    };
  },
  methods: {
    async register() {
      try {
        await axios.post('http://localhost:5000/api/register', {
          username: this.username,
          password: this.password,
        });
        this.$router.push('/login'); // 注册成功后重定向到登录页面
      } catch (error) {
        this.errorMessage = error.response.data.msg; // 显示错误信息
      }
    },
  },
};
</script>

<style scoped>
/* 添加样式 */
</style>