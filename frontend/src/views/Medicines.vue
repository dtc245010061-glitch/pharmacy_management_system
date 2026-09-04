<template>
  <div class="med-container">
    <!-- Sidebar điều hướng phân quyền theo vai trò -->
    <div class="sidebar">
      <h3>Quản lý Nhà thuốc</h3>
      
      <!-- Thông tin tài khoản đăng nhập -->
      <div class="user-badge-box">
        <span class="username-text">👤 {{ currentUsername }}</span>
        <span :class="['role-badge', `badge-${userRole}`]">{{ roleLabel }}</span>
      </div>

      <ul>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/dashboard')">
          Trang chủ
        </li>
        <li class="active">Quản lý Thuốc</li>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/batches')">
          Quản lý Lô & HSD
        </li>
        <li v-if="userRole === 'manager'" @click="$router.push('/suppliers')">
          Nhà cung cấp
        </li>
        <li @click="$router.push('/pos')">Bán hàng (POS)</li>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/ai-chat')">
          Trợ lý AI
        </li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <div class="main-content">
      <h2>Danh mục & Quản lý Thuốc</h2>

      <!-- Form thêm thuốc (Ẩn đối với Thu ngân) -->
      <div class="form-card" v-if="userRole !== 'cashier'">
        <h3>Thêm thuốc mới</h3>
        <form @submit.prevent="createMedicine" class="inline-form">
          <input type="text" v-model="form.name" placeholder="Tên thuốc..." required />
          <input type="text" v-model="form.unit" placeholder="Đơn vị tính..." required />
          <input type="number" v-model.number="form.quantity" placeholder="Số lượng..." required min="0" />
          <input type="number" v-model.number="form.category_id" placeholder="ID Danh mục..." required />
          <input type="text" v-model="form.description" placeholder="Mô tả..." />
          <button type="submit">Thêm thuốc</button>
        </form>
      </div>

      <!-- Bảng danh sách thuốc -->
      <div class="table-card">
        <h3>Danh sách kho thuốc</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Tên thuốc</th>
              <th>Đơn vị</th>
              <th>Số lượng</th>
              <th>Mô tả</th>
              <th v-if="userRole !== 'cashier'">Ảnh thuốc</th>
              <th v-if="userRole === 'manager'">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="med in medicines" :key="med.id">
              <td>{{ med.id }}</td>
              <td><strong>{{ med.name }}</strong></td>
              <td>{{ med.unit }}</td>
              <td><strong>{{ med.quantity || 0 }}</strong></td>
              <td>{{ med.description || 'Không có mô tả' }}</td>
              <td v-if="userRole !== 'cashier'">
                <input type="file" @change="(e) => handleFileUpload(e, med.id)" accept="image/*" style="font-size: 12px;" />
              </td>
              <td v-if="userRole === 'manager'">
                <button @click="deleteMedicine(med.id)" class="btn-delete">Xóa</button>
              </td>
            </tr>
            <tr v-if="medicines.length === 0">
              <td :colspan="userRole === 'manager' ? 7 : (userRole === 'cashier' ? 5 : 6)" style="text-align: center;">
                Chưa có dữ liệu thuốc trong hệ thống.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const medicines = ref([]);
const userRole = ref(localStorage.getItem('role') || 'cashier');
const currentUsername = ref(localStorage.getItem('username') || 'Người dùng');

const roleLabel = computed(() => {
  switch (userRole.value) {
    case 'manager': return 'Quản lý';
    case 'pharmacist': return 'Dược sĩ';
    case 'cashier': return 'Thu ngân';
    default: return userRole.value;
  }
});

const form = ref({
  name: '',
  unit: '',
  quantity: 0,
  category_id: 1,
  description: ''
});

const fetchMedicines = async () => {
  try {
    const res = await api.get('/medicines/');
    medicines.value = res.data;
  } catch (error) {
    console.error("Lỗi tải danh sách thuốc", error);
  }
};

const createMedicine = async () => {
  try {
    await api.post('/medicines/', form.value);
    alert('Thêm thuốc thành công!');
    form.value.name = '';
    form.value.unit = '';
    form.value.quantity = 0;
    form.value.description = '';
    fetchMedicines();
  } catch (error) {
    console.error("Lỗi từ server:", error.response);
    let errorMsg = 'Không thể thêm thuốc';
    if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        errorMsg = error.response.data.detail.map(e => `${e.loc[e.loc.length-1]}: ${e.msg}`).join('\n');
      } else {
        errorMsg = error.response.data.detail;
      }
    }
    alert('Lỗi từ máy chủ:\n' + errorMsg);
  }
};

const handleFileUpload = async (event, medicineId) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    await api.post(`/medicines/${medicineId}/upload-image`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    alert('Tải ảnh lên thành công!');
    fetchMedicines();
  } catch (error) {
    alert('Lỗi tải ảnh lên: ' + (error.response?.data?.detail || 'Không xác định'));
  }
};

const deleteMedicine = async (id) => {
  if (confirm('Bạn có chắc chắn muốn xóa loại thuốc này không?')) {
    try {
      await api.delete(`/medicines/${id}`);
      fetchMedicines();
    } catch (error) {
      alert('Lỗi: ' + (error.response?.data?.detail || 'Không thể xóa thuốc này'));
    }
  }
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

onMounted(() => {
  fetchMedicines();
});
</script>

<style scoped>
.med-container { display: flex; height: 100vh; background-color: #f4f7f6; }
.sidebar { width: 250px; background-color: #2c3e50; color: white; padding: 20px; flex-shrink: 0; }
.sidebar h3 { text-align: center; margin-bottom: 15px; }

.user-badge-box { background-color: #1a252f; padding: 10px 12px; border-radius: 6px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.username-text { font-size: 13px; font-weight: 500; }
.role-badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: bold; text-transform: uppercase; }
.badge-manager { background-color: #e74c3c; color: white; }
.badge-pharmacist { background-color: #3498db; color: white; }
.badge-cashier { background-color: #27ae60; color: white; }

.sidebar ul { list-style: none; padding: 0; }
.sidebar li { padding: 10px 15px; margin-bottom: 10px; border-radius: 4px; cursor: pointer; }
.sidebar li:hover, .sidebar li.active { background-color: #34495e; }

.main-content { flex: 1; padding: 30px; overflow-y: auto; }
.form-card, .table-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
.inline-form { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
.inline-form input { flex: 1; min-width: 140px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.inline-form button { background-color: #42b983; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; font-weight: bold; min-width: 120px; }

table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background-color: #f8f9fa; }
.btn-delete { background-color: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
</style>