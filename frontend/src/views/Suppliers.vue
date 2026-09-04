<template>
  <div class="layout-container">
    <div class="sidebar">
      <h3>Quản lý Nhà thuốc</h3>
      <ul>
        <li @click="$router.push('/dashboard')">Trang chủ</li>
        <li @click="$router.push('/medicines')">Quản lý Thuốc</li>
        <li @click="$router.push('/batches')">Quản lý Lô & HSD</li>
        <li class="active">Nhà cung cấp</li>
        <li @click="$router.push('/pos')">Bán hàng (POS)</li>
        <li @click="$router.push('/ai-chat')">Trợ lý AI</li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <div class="main-content">
      <h2>Quản lý Nhà Cung Cấp</h2>

      <div class="card">
        <h3>Thêm Nhà Cung Cấp Mới</h3>
        <form @submit.prevent="createSupplier" class="form-grid">
          <input type="text" v-model="form.name" placeholder="Tên nhà cung cấp (*)" required />
          <input type="text" v-model="form.phone" placeholder="Số điện thoại" />
          <input type="email" v-model="form.email" placeholder="Email" />
          <input type="text" v-model="form.address" placeholder="Địa chỉ" />
          <button type="submit" class="btn-primary">Thêm NCC</button>
        </form>
      </div>

      <div class="card">
        <h3>Danh Sách Nhà Cung Cấp</h3>
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Tên Nhà Cung Cấp</th>
              <th>Số Điện Thoại</th>
              <th>Email</th>
              <th>Địa Chỉ</th>
              <th>Thao Tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in suppliers" :key="item.id">
              <td>{{ item.id }}</td>
              <td><strong>{{ item.name }}</strong></td>
              <td>{{ item.phone || 'Chưa cập nhật' }}</td>
              <td>{{ item.email || 'Chưa cập nhật' }}</td>
              <td>{{ item.address || 'Chưa cập nhật' }}</td>
              <td>
                <button @click="deleteSupplier(item.id)" class="btn-delete">Xóa</button>
              </td>
            </tr>
            <tr v-if="suppliers.length === 0">
              <td colspan="6" style="text-align: center;">Chưa có dữ liệu nhà cung cấp.</td>
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
const suppliers = ref([]);
const form = ref({
  name: '',
  phone: '',
  email: '',
  address: ''
});

const fetchSuppliers = async () => {
  try {
    const res = await api.get('/suppliers/');
    suppliers.value = res.data;
  } catch (error) {
    console.error("Lỗi khi tải nhà cung cấp:", error);
  }
};

const createSupplier = async () => {
  try {
    await api.post('/suppliers/', form.value);
    alert('Thêm nhà cung cấp thành công!');
    form.value = { name: '', phone: '', email: '', address: '' };
    fetchSuppliers();
  } catch (error) {
    alert('Lỗi: ' + (error.response?.data?.detail || 'Không thể thêm'));
  }
};

const deleteSupplier = async (id) => {
  if (confirm('Bạn có chắc muốn xóa nhà cung cấp này?')) {
    try {
      await api.delete(`/suppliers/${id}`);
      fetchSuppliers();
    } catch (error) {
      alert('Không thể xóa nhà cung cấp này.');
    }
  }
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

onMounted(() => {
  fetchSuppliers();
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
.form-grid { display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap; }
.form-grid input { flex: 1; min-width: 150px; padding: 8px; border: 1px solid #ccc; border-radius: 4px; }
.btn-primary { background-color: #42b983; color: white; border: none; padding: 8px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; }
table { width: 100%; border-collapse: collapse; margin-top: 15px; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background-color: #f8f9fa; }
.btn-delete { background-color: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; }
</style>