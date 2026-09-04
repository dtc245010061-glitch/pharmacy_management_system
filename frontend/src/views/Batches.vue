<template>
  <div class="layout-container">
    <div class="sidebar">
      <h3>Quản lý Nhà thuốc</h3>
      <ul>
        <li @click="$router.push('/dashboard')">Trang chủ</li>
        <li @click="$router.push('/medicines')">Quản lý Thuốc</li>
        <li class="active">Quản lý Lô & HSD</li>
        <li @click="$router.push('/suppliers')">Nhà cung cấp</li>
        <li @click="$router.push('/pos')">Bán hàng (POS)</li>
        <li @click="$router.push('/ai-chat')">Trợ lý AI</li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <div class="main-content">
      <h2>Quản lý Lô Thuốc & Hạn Sử Dụng (FEFO)</h2>

      <div class="card">
        <h3>Nhập Lô Hàng Mới Vào Kho</h3>
        <form @submit.prevent="createBatch" class="batch-form-grid">
          <div class="form-group">
            <label>Thuốc (*):</label>
            <select v-model.number="form.medicine_id" required>
              <option disabled value="">-- Chọn loại thuốc --</option>
              <option v-for="m in medicines" :key="m.id" :value="m.id">
                {{ m.name }} (Hiện tồn: {{ m.quantity || 0 }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Nhà Cung Cấp:</label>
            <select v-model.number="form.supplier_id">
              <option :value="null">-- Không chọn / NCC vãng lai --</option>
              <option v-for="s in suppliers" :key="s.id" :value="s.id">
                {{ s.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Số Lô Hàng (*):</label>
            <input type="text" v-model="form.batch_number" placeholder="Ví dụ: LO-2026-01" required />
          </div>

          <div class="form-group">
            <label>Số Lượng Nhập (*):</label>
            <input type="number" v-model.number="form.quantity" min="1" required />
          </div>

          <div class="form-group">
            <label>Hạn Sử Dụng (*):</label>
            <input type="date" v-model="form.expiry_date" required />
          </div>

          <div class="form-group">
            <label>Giá Nhập (VNĐ):</label>
            <input type="number" v-model.number="form.import_price" min="0" />
          </div>

          <div class="form-group">
            <label>Giá Bán (VNĐ):</label>
            <input type="number" v-model.number="form.sell_price" min="0" />
          </div>

          <div class="form-group submit-btn-wrapper">
            <button type="submit" class="btn-primary">Nhập Kho</button>
          </div>
        </form>
      </div>

      <div class="card">
        <h3>Danh Sách Các Lô Thuốc (Ưu tiên FEFO)</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Số Lô</th>
              <th>Thuốc</th>
              <th>Tồn Kho Lô</th>
              <th>Hạn Sử Dụng</th>
              <th>Giá Bán</th>
              <th>Trạng Thái Hạn</th>
              <th>Thao Tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="b in batches" :key="b.id">
              <td>{{ b.id }}</td>
              <td><strong>{{ b.batch_number }}</strong></td>
              <td>{{ getMedicineName(b.medicine_id) }}</td>
              <td><strong>{{ b.quantity }}</strong></td>
              <td>{{ b.expiry_date }}</td>
              <td>{{ formatCurrency(b.sell_price) }}</td>
              <td>
                <span :class="getStatusBadgeClass(b.expiry_date)">
                  {{ getStatusText(b.expiry_date) }}
                </span>
              </td>
              <td>
                <button @click="deleteBatch(b.id)" class="btn-delete">Xóa</button>
              </td>
            </tr>
            <tr v-if="batches.length === 0">
              <td colspan="8" style="text-align: center;">Chưa có dữ liệu lô thuốc nào.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const batches = ref([]);
const medicines = ref([]);
const suppliers = ref([]);

const form = ref({
  medicine_id: '',
  supplier_id: null,
  batch_number: '',
  quantity: 100,
  expiry_date: '',
  import_price: 0,
  sell_price: 0
});

const loadInitialData = async () => {
  try {
    const [batchesRes, medsRes, suppsRes] = await Promise.all([
      api.get('/batches/'),
      api.get('/medicines/'),
      api.get('/suppliers/')
    ]);
    batches.value = batchesRes.data;
    medicines.value = medsRes.data;
    suppliers.value = suppsRes.data;
  } catch (error) {
    console.error("Lỗi khi tải dữ liệu:", error);
  }
};

const createBatch = async () => {
  try {
    await api.post('/batches/', form.value);
    alert('Nhập lô thuốc thành công! Số lượng tồn kho thuốc đã được cập nhật.');
    form.value = {
      medicine_id: '',
      supplier_id: null,
      batch_number: '',
      quantity: 100,
      expiry_date: '',
      import_price: 0,
      sell_price: 0
    };
    loadInitialData();
  } catch (error) {
    alert('Lỗi: ' + (error.response?.data?.detail || 'Không thể tạo lô'));
  }
};

const deleteBatch = async (id) => {
  if (confirm('Xóa lô hàng sẽ tự động giảm tồn kho của loại thuốc này. Bạn chắc chắn chứ?')) {
    try {
      await api.delete(`/batches/${id}`);
      loadInitialData();
    } catch (error) {
      alert('Không thể xóa lô này.');
    }
  }
};

const getMedicineName = (id) => {
  const found = medicines.value.find(m => m.id === id);
  return found ? found.name : `Thuốc #${id}`;
};

const formatCurrency = (val) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(val || 0);
};

const getStatusBadgeClass = (expiryDateStr) => {
  const diffDays = Math.ceil((new Date(expiryDateStr) - new Date()) / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return 'badge-expired';
  if (diffDays <= 30) return 'badge-warning';
  return 'badge-good';
};

const getStatusText = (expiryDateStr) => {
  const diffDays = Math.ceil((new Date(expiryDateStr) - new Date()) / (1000 * 60 * 60 * 24));
  if (diffDays < 0) return 'Đã hết hạn';
  if (diffDays <= 30) return `Cận hạn (${diffDays} ngày)`;
  return 'Tốt';
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

onMounted(() => {
  loadInitialData();
});
</script>

<style scoped>
.layout-container { display: flex; height: 100vh; background-color: #f4f7f6; }
.sidebar { width: 250px; background-color: #2c3e50; color: white; padding: 20px; }
.sidebar h3 { text-align: center; margin-bottom: 30px; }
.sidebar ul { list-style: none; padding: 0; }
.sidebar li { padding: 10px 15px; margin-bottom: 10px; border-radius: 4px; cursor: pointer; }
.sidebar li:hover, .sidebar li.active { background-color: #34495e; }
.main-content { flex: 1; padding: 30px; overflow-y: auto; }
.card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
.batch-form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin-top: 15px; }
.form-group { display: flex; flex-direction: column; }
.form-group label { font-weight: bold; margin-bottom: 5px; font-size: 13px; color: #333; }
.form-group input, .form-group select { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.submit-btn-wrapper { justify-content: flex-end; }
.btn-primary { background-color: #42b983; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; height: 38px; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background-color: #f8f9fa; }
.btn-delete { background-color: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
.badge-good { color: #27ae60; font-weight: bold; }
.badge-warning { color: #e67e22; font-weight: bold; }
.badge-expired { color: #e74c3c; font-weight: bold; }
</style>