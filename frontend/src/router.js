// src/router.js
import { createRouter, createWebHistory } from 'vue-router';
import Process from './views/Process.vue';
import Result from './views/Result.vue';
import Login from './views/Login.vue';
import Register from './views/Register.vue';
import TreeDetail from './views/TreeDetail.vue'


const routes = [
    { path: '/', component: Login },
    { path: '/process', component: Process, meta: { requiresAuth: true } },
    { path: '/result', component: Result, meta: { requiresAuth: true } },
    { path: '/login', component: Login },
    { path: '/register', component: Register },
    { path: '/tree/:id', component: TreeDetail },  // ✅ 新增路由
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
    const isLoggedIn = !!localStorage.getItem('token'); // 检查用户是否已登录
    if (to.meta.requiresAuth && !isLoggedIn) {
        next('/login'); // 如果需要身份验证且用户未登录，则重定向到登录页面
    } else {
        next(); // 继续导航
    }
});

export default router;