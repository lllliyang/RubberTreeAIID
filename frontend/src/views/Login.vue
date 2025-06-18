<template>
  <div class="login-container">
    <div class="overlay"></div>
    <div class="login-box">
      <h1 class="text-center">RubberAIID</h1>
      <form @submit.prevent="login">
        <div class="mb-3">
          <label for="username" class="form-label">Username</label>
          <input type="text" class="form-control" v-model="username" required />
        </div>
        <div class="mb-3">
          <label for="password" class="form-label">Password</label>
          <input type="password" class="form-control" v-model="password" required />
        </div>
        <button type="submit" class="btn btn-primary btn-block">Login</button>
        <p v-if="errorMessage" class="text-danger mt-2">{{ errorMessage }}</p>
      </form>
      <div class="text-center mt-3">
        <router-link to="/register">Don't have an account? Register</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserLogin',
  data() {
    return {
      username: '',
      password: '',
      errorMessage: '',
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:5000/api/login', {
          username: this.username,
          password: this.password,
        });
        localStorage.setItem('token', response.data.access_token);
        this.$router.push('/process');
      } catch (error) {
        this.errorMessage = error.response.data.msg;
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  position: relative;
  height: 100vh;
  background: url('@/assets/background.png') no-repeat center center/cover; /* 使用本地背景图片 */
  display: flex; /* 使用 Flexbox */
  justify-content: center; /* 水平居中 */
  align-items: center; /* 垂直居中 */
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5); /* 半透明黑色覆盖层 */
}

.login-box {
  position: relative;
  z-index: 1;
  max-width: 400px;
  width: 100%; /* 使登录框宽度自适应 */
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

h1 {
  margin-bottom: 20px;
}
</style>