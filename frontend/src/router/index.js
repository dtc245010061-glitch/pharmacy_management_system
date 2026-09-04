import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Medicines from '../views/Medicines.vue'
import POS from '../views/POS.vue'
import AIChat from '../views/AIChat.vue'
import Suppliers from '../views/Suppliers.vue'
import Batches from '../views/Batches.vue'
import Invoices from '../views/Invoices.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true, roles: ['manager', 'pharmacist'] } // Thu ngân bị chặn
  },
  {
    path: '/medicines',
    name: 'Medicines',
    component: Medicines,
    meta: { requiresAuth: true, roles: ['manager', 'pharmacist', 'cashier'] }
  },
  {
    path: '/batches',
    name: 'Batches',
    component: Batches,
    meta: { requiresAuth: true, roles: ['manager', 'pharmacist'] } // Thu ngân bị chặn
  },
  {
    path: '/suppliers',
    name: 'Suppliers',
    component: Suppliers,
    meta: { requiresAuth: true, roles: ['manager'] } // Chỉ Quản lý được quản lý NCC
  },
  {
    path: '/pos',
    name: 'POS',
    component: POS,
    meta: { requiresAuth: true, roles: ['manager', 'pharmacist', 'cashier'] }
  },
  {
    path: '/invoices',
    name: 'Invoices',
    component: Invoices,
    meta: { requiresAuth: true, roles: ['manager', 'pharmacist', 'cashier'] }
  },
  {
    path: '/ai-chat',
    name: 'AIChat',
    component: AIChat,
    meta: { requiresAuth: true, roles: ['manager', 'pharmacist'] }
  },
  {
    path: '/',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guard kiểm tra phiên đăng nhập và quyền vai trò (RBAC)
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else if (to.path === '/login' && token) {
    // Nếu đã đăng nhập mà bấm vào /login thì tự điều hướng theo quyền
    if (role === 'cashier') {
      next('/pos');
    } else {
      next('/dashboard');
    }
  } else if (to.meta.roles && !to.meta.roles.includes(role)) {
    // Nếu vào trang không có quyền truy cập
    alert(`Bạn không có quyền truy cập trang này (Chức vụ hiện tại: ${role})`);
    if (role === 'cashier') {
      next('/pos');
    } else {
      next('/dashboard');
    }
  } else {
    next();
  }
})

export default router