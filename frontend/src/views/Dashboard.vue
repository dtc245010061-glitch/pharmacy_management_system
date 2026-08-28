<template>
  <div class="dashboard-container">
    <!-- Sidebar điều hướng -->
    <div class="sidebar">
      <h3>Nhà Thuốc AI</h3>
      <ul>
        <li class="active">Trang chủ (Dashboard)</li>
        <li @click="$router.push('/medicines')">Quản lý Thuốc</li>
        <li @click="$router.push('/pos')">Bán hàng (POS)</li>
        <li @click="$router.push('/ai-chat')">Trợ lý AI & Guardrail</li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <!-- Nội dung chính Dashboard -->
    <div class="main-content">
      <h2>Tổng quan Hệ thống Nhà thuốc</h2>
      
      <!-- Các thẻ thống kê nhanh -->
      <div class="stats-grid">
        <div class="stat-card">
          <h4>Tổng loại thuốc</h4>
          <p class="stat-number">{{ stats.totalMedicines }}</p>
        </div>
        <div class="stat-card">
          <h4>Hóa đơn đã bán</h4>
          <p class="stat-number">{{ stats.totalInvoices }}</p>
        </div>
        <div class="stat-card">
          <h4>Trạng thái AI Guardrail</h4>
          <p class="stat-status">Hoạt động (An toàn)</p>
        </div>
      </div>

      <!-- Khu vực chào mừng và lối tắt -->
      <div class="welcome-card">
        <h3>Chào mừng bạn quay trở lại, Quản lý!</h3>
        <p>Hệ thống Quản lý Nhà thuốc tích hợp AI và tự động hóa FEFO đang vận hành ổn định.</p>
        <div class="quick-actions">
          <button @click="$router.push('/pos')">🚀 Mở quầy Bán hàng (POS)</button>
          <button @click="$router.push('/medicines')">📦 Kiểm tra Kho thuốc</button>
          <button @click="$router.push('/ai-chat')">🤖 Hỏi đáp Trợ lý AI</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const stats = ref({
  totalMedicines: 0,
  totalInvoices: 0
});

const fetchDashboardStats = async () => {
  try {
    // Lấy số liệu thuốc và hóa đơn từ API
    const [medRes, invRes] = await Promise.all([
      api.get('/medicines/'),
      api.get('/invoices/').catch(() => ({ data: [] })) // Fallback nếu chưa gọi được invoice
    ]);
    stats.value.totalMedicines = medRes.data.length;
    stats.value.totalInvoices = invRes.data.length;
  } catch (error) {
    console.error("Lỗi tải thống kê dashboard", error);
  }
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

onMounted(() => {
  fetchDashboardStats();
});
</script>

<style scoped>
.dashboard-container { display: flex; height: 100vh; background-color: #f4f7f6; }
.sidebar { width: 250px; background-color: #2c3e50; color: white; padding: 20px; }
.sidebar h3 { text-align: center; margin-bottom: 30px; }
.sidebar ul { list-style: none; padding: 0; }
.sidebar li { padding: 10px 15px; margin-bottom: 10px; border-radius: 4px; cursor: pointer; }
.sidebar li:hover, .sidebar li.active { background-color: #34495e; }
.main-content { flex: 1; padding: 30px; overflow-y: auto; }
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
.stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }
.stat-card h4 { color: #7f8c8d; margin-bottom: 10px; }
.stat-number { font-size: 28px; font-weight: bold; color: #2c3e50; }
.stat-status { font-size: 18px; font-weight: bold; color: #27ae60; margin-top: 5px; }
.welcome-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.welcome-card h3 { color: #2c3e50; margin-bottom: 10px; }
.welcome-card p { color: #555; margin-bottom: 20px; }
.quick-actions { display: flex; gap: 15px; }
.quick-actions button { background-color: #42b983; color: white; border: none; padding: 10px 20px; border-radius: 4px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
.quick-actions button:hover { background-color: #3aa876; }
</style>