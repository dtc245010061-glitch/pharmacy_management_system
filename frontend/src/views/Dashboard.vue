<template>
  <div class="dashboard-container">
    <!-- Sidebar điều hướng đồng bộ toàn hệ thống -->
    <div class="sidebar">
      <h3>Nhà Thuốc AI</h3>
      <ul>
        <li class="active">Trang chủ (Dashboard)</li>
        <li @click="$router.push('/medicines')">Quản lý Thuốc</li>
        <li @click="$router.push('/batches')">Quản lý Lô & HSD</li>
        <li @click="$router.push('/suppliers')">Nhà cung cấp</li>
        <li @click="$router.push('/pos')">Bán hàng (POS)</li>
        <li @click="$router.push('/ai-chat')">Trợ lý AI & Guardrail</li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <!-- Nội dung chính Dashboard -->
    <div class="main-content">
      <h2>Tổng quan Hệ thống Nhà thuốc</h2>

      <!-- Các thẻ thống kê nhanh (KPIs) -->
      <div class="stats-grid">
        <div class="stat-card">
          <h4>Tổng loại thuốc</h4>
          <p class="stat-number">{{ stats.totalMedicines }}</p>
        </div>
        <div class="stat-card">
          <h4>Hóa đơn đã bán</h4>
          <p class="stat-number">{{ stats.totalInvoices }}</p>
        </div>
        <div class="stat-card warning-card">
          <h4>Lô cận hạn / Hết hạn</h4>
          <p class="stat-number warning-text">{{ expiringBatches.length }}</p>
        </div>
        <div class="stat-card danger-card">
          <h4>Thuốc sắp hết hàng</h4>
          <p class="stat-number danger-text">{{ lowStockMedicines.length }}</p>
        </div>
      </div>

      <!-- Khu vực chào mừng và lối tắt nhanh -->
      <div class="welcome-card">
        <h3>Chào mừng bạn quay trở lại!</h3>
        <p>Hệ thống Quản lý Nhà thuốc tích hợp AI và thuật toán tự động hóa FEFO đang vận hành ổn định.</p>
        <div class="quick-actions">
          <button @click="$router.push('/pos')">🚀 Mở quầy Bán hàng (POS)</button>
          <button @click="$router.push('/batches')">📦 Nhập Lô Hàng Mới</button>
          <button @click="$router.push('/medicines')">📋 Danh Mục Thuốc</button>
          <button @click="$router.push('/ai-chat')">🤖 Hỏi đáp Trợ lý AI</button>
        </div>
      </div>

      <!-- Khu vực 2 Bảng Cảnh báo -->
      <div class="alerts-grid">
        <!-- 1. BẢNG CẢNH BÁO LÔ CẬN HẠN / QUÁ HẠN -->
        <div class="card alert-box">
          <div class="card-header">
            <h3>⚠️ Cảnh Báo Lô Thuốc Cận Hạn (Dưới 30 ngày)</h3>
            <button @click="$router.push('/batches')" class="btn-link">Xem tất cả lô</button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Số Lô</th>
                <th>Tên Thuốc</th>
                <th>Tồn Lô</th>
                <th>Hạn Sử Dụng</th>
                <th>Tình Trạng</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in expiringBatches" :key="b.id">
                <td><strong>{{ b.batch_number }}</strong></td>
                <td>{{ getMedicineName(b.medicine_id) }}</td>
                <td>{{ b.quantity }}</td>
                <td>{{ b.expiry_date }}</td>
                <td>
                  <span :class="getStatusBadgeClass(b.expiry_date)">
                    {{ getStatusText(b.expiry_date) }}
                  </span>
                </td>
              </tr>
              <tr v-if="expiringBatches.length === 0">
                <td colspan="5" class="empty-state">✅ Không có lô thuốc nào sắp hết hạn trong 30 ngày tới.</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 2. BẢNG CẢNH BÁO THUỐC SẮP HẾT HÀNG -->
        <div class="card alert-box">
          <div class="card-header">
            <h3>📉 Cảnh Báo Thuốc Tồn Kho Thấp (Dưới 10 đơn vị)</h3>
            <button @click="$router.push('/medicines')" class="btn-link">Xem danh mục</button>
          </div>
          <table>
            <thead>
              <tr>
                <th>Mã</th>
                <th>Tên Thuốc</th>
                <th>Đơn Vị</th>
                <th>Tồn Hiện Tại</th>
                <th>Hành Động</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in lowStockMedicines" :key="m.id">
                <td>#{{ m.id }}</td>
                <td><strong>{{ m.name }}</strong></td>
                <td>{{ m.unit }}</td>
                <td>
                  <span class="stock-badge">{{ m.quantity || 0 }}</span>
                </td>
                <td>
                  <button @click="$router.push('/batches')" class="btn-restock">Nhập thêm</button>
                </td>
              </tr>
              <tr v-if="lowStockMedicines.length === 0">
                <td colspan="5" class="empty-state">✅ Tồn kho của tất cả các loại thuốc đều an toàn (≥ 10).</td>
              </tr>
            </tbody>
          </table>
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

const medicinesList = ref([]);
const expiringBatches = ref([]);
const lowStockMedicines = ref([]);

const fetchDashboardData = async () => {
  try {
    const [medRes, invRes, expRes] = await Promise.all([
      api.get('/medicines/'),
      api.get('/invoices/').catch(() => ({ data: [] })),
      api.get('/batches/expiring-soon?days=30').catch(() => ({ data: [] }))
    ]);

    // 1. Thống kê tổng số
    medicinesList.value = medRes.data || [];
    stats.value.totalMedicines = medicinesList.value.length;
    stats.value.totalInvoices = (invRes.data || []).length;

    // 2. Danh sách lô cận hạn
    expiringBatches.value = expRes.data || [];

    // 3. Danh sách thuốc tồn kho thấp (dưới 10 đơn vị)
    lowStockMedicines.value = medicinesList.value.filter(
      (m) => (m.quantity || 0) < 10
    );
  } catch (error) {
    console.error("Lỗi khi tải dữ liệu trang Dashboard:", error);
  }
};

const getMedicineName = (id) => {
  const found = medicinesList.value.find((m) => m.id === id);
  return found ? found.name : `Thuốc #${id}`;
};

const getDaysDifference = (expiryDateStr) => {
  return Math.ceil((new Date(expiryDateStr) - new Date()) / (1000 * 60 * 60 * 24));
};

const getStatusBadgeClass = (expiryDateStr) => {
  const diffDays = getDaysDifference(expiryDateStr);
  if (diffDays < 0) return 'badge-expired';
  return 'badge-warning';
};

const getStatusText = (expiryDateStr) => {
  const diffDays = getDaysDifference(expiryDateStr);
  if (diffDays < 0) return 'Đã hết hạn';
  if (diffDays === 0) return 'Hôm nay hết hạn';
  return `Còn ${diffDays} ngày`;
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

onMounted(() => {
  fetchDashboardData();
});
</script>

<style scoped>
.dashboard-container { display: flex; height: 100vh; background-color: #f4f7f6; }
.sidebar { width: 250px; background-color: #2c3e50; color: white; padding: 20px; flex-shrink: 0; }
.sidebar h3 { text-align: center; margin-bottom: 30px; }
.sidebar ul { list-style: none; padding: 0; }
.sidebar li { padding: 10px 15px; margin-bottom: 10px; border-radius: 4px; cursor: pointer; }
.sidebar li:hover, .sidebar li.active { background-color: #34495e; }

.main-content { flex: 1; padding: 30px; overflow-y: auto; }

/* Grid 4 Thẻ thống kê */
.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 25px; }
.stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }
.stat-card h4 { color: #7f8c8d; margin-bottom: 10px; font-size: 14px; }
.stat-number { font-size: 26px; font-weight: bold; color: #2c3e50; margin: 0; }

.warning-card { border-top: 4px solid #e67e22; }
.warning-text { color: #e67e22; }
.danger-card { border-top: 4px solid #e74c3c; }
.danger-text { color: #e74c3c; }

/* Welcome Card */
.welcome-card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 25px; }
.welcome-card h3 { color: #2c3e50; margin-bottom: 8px; }
.welcome-card p { color: #555; margin-bottom: 18px; }
.quick-actions { display: flex; gap: 12px; flex-wrap: wrap; }
.quick-actions button { background-color: #42b983; color: white; border: none; padding: 10px 16px; border-radius: 4px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
.quick-actions button:hover { background-color: #3aa876; }

/* Khu vực Bảng Cảnh báo */
.alerts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.alert-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-header h3 { font-size: 16px; color: #2c3e50; margin: 0; }
.btn-link { background: none; border: none; color: #3498db; cursor: pointer; font-size: 13px; text-decoration: underline; }

table { width: 100%; border-collapse: collapse; margin-top: 5px; font-size: 14px; }
th, td { border: 1px solid #edf2f7; padding: 10px 12px; text-align: left; }
th { background-color: #f8fafc; color: #475569; font-weight: 600; }
.empty-state { text-align: center; color: #27ae60; padding: 20px !important; font-weight: 500; }

.badge-warning { background-color: #fef3c7; color: #d97706; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.badge-expired { background-color: #fee2e2; color: #dc2626; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.stock-badge { background-color: #fee2e2; color: #dc2626; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 13px; }
.btn-restock { background-color: #3498db; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px; }
.btn-restock:hover { background-color: #2980b9; }

@media (max-width: 1200px) {
  .alerts-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>