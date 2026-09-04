<template>
  <div class="login-container">
    <div class="login-box">
      <h2>Hệ thống Nhà thuốc</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Tên đăng nhập:</label>
          <input type="text" v-model="username" required placeholder="Nhập tài khoản..." />
        </div>
        <div class="form-group">
          <label>Mật khẩu:</label>
          <input type="password" v-model="password" required placeholder="Nhập mật khẩu..." />
        </div>
        
        <div v-if="errorMessage" class="error-msg">{{ errorMessage }}</div>
        
        <button type="submit" :disabled="isLoading">
          {{ isLoading ? 'Đang xác thực...' : 'Đăng nhập' }}
        </button>
      </form>

      <!-- Bảng gợi ý tài khoản test 3 vai trò -->
      <div class="test-accounts-box">
        <p class="test-title">💡 Tài khoản kiểm thử 3 vai trò (Mật khẩu: <strong>123456</strong>):</p>
        <div class="chips-container">
          <button type="button" @click="quickFill('admin')" class="chip chip-manager">
            👑 Quản lý (admin)
          </button>
          <button type="button" @click="quickFill('duocsi')" class="chip chip-pharmacist">
            💊 Dược sĩ (duocsi)
          </button>
          <button type="button" @click="quickFill('thungan')" class="chip chip-cashier">
            💳 Thu ngân (thungan)
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const quickFill = (user) => {
  username.value = user;
  password.value = '123456';
};

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  
  try {
    const response = await api.post('/auth/login', { 
      username: username.value, 
      password: password.value 
    });
    
    const userRole = response.data.role;

    // Lưu Token, Quyền và Tên người dùng vào bộ nhớ trình duyệt
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('role', userRole);
    localStorage.setItem('username', username.value);
    
    // Phân luồng điều hướng theo vai trò (RBAC)
    if (userRole === 'cashier') {
      router.push('/pos'); // Thu ngân chuyển thẳng vào quầy POS
    } else {
      router.push('/dashboard'); // Quản lý và Dược sĩ vào Dashboard tổng quan
    }
    
  } catch (error) {
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'Sai tên đăng nhập hoặc mật khẩu!';
    } else {
      errorMessage.value = 'Lỗi kết nối đến máy chủ!';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-container { display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f4f7f6; }
.login-box { background: white; padding: 30px 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 420px; }
.login-box h2 { text-align: center; margin-bottom: 25px; color: #2c3e50; }
.form-group { margin-bottom: 15px; text-align: left; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
.form-group input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #42b983; }
button[type="submit"] { width: 100%; padding: 12px; background-color: #42b983; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; }
button[type="submit"]:disabled { background-color: #9cdbbf; }
.error-msg { color: #e74c3c; font-size: 14px; margin-bottom: 10px; text-align: center; }

/* Hộp gợi ý tài khoản test */
.test-accounts-box { margin-top: 25px; padding-top: 15px; border-top: 1px dashed #ddd; text-align: center; }
.test-title { font-size: 13px; color: #666; margin-bottom: 10px; }
.chips-container { display: flex; flex-direction: column; gap: 8px; }
.chip { border: 1px solid #ddd; background: #fafafa; padding: 7px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; text-align: left; transition: all 0.2s; }
.chip:hover { transform: translateY(-1px); box-shadow: 0 2px 5px rgba(0,0,0,0.08); }
.chip-manager:hover { border-color: #e74c3c; background-color: #fdf2f2; }
.chip-pharmacist:hover { border-color: #3498db; background-color: #f0f7fd; }
.chip-cashier:hover { border-color: #27ae60; background-color: #f2faf5; }
</style>