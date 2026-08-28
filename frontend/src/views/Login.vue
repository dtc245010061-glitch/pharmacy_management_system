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
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api'; // Đã mở comment để gọi API

const router = useRouter();
const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  
  try {
    // Gọi API login của Backend
    const response = await api.post('/auth/login', { 
      username: username.value, 
      password: password.value 
    });
    
    // Lưu Token và Quyền vào bộ nhớ trình duyệt
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('role', response.data.role);
    
    // Đăng nhập thành công, chuyển hướng sang trang Tổng quan (Dashboard)
    router.push('/dashboard');
    
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
.login-box { background: white; padding: 30px 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
.login-box h2 { text-align: center; margin-bottom: 25px; color: #2c3e50; }
.form-group { margin-bottom: 15px; text-align: left; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #333; }
.form-group input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.form-group input:focus { outline: none; border-color: #42b983; }
button { width: 100%; padding: 12px; background-color: #42b983; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px; }
button:disabled { background-color: #9cdbbf; }
.error-msg { color: #e74c3c; font-size: 14px; margin-bottom: 10px; text-align: center; }
</style>