<template>
  <div class="pos-container">
    <!-- Sidebar điều hướng -->
    <div class="sidebar">
      <h3>Nhà Thuốc AI</h3>
      <ul>
        <li @click="$router.push('/dashboard')">Quản lý Thuốc</li>
        <li class="active">Bán hàng (POS)</li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <!-- Khu vực chính POS -->
    <div class="pos-main">
      <h2>Màn hình Bán hàng (POS - FEFO Engine)</h2>

      <div class="pos-grid">
        <!-- Danh sách thuốc có thể chọn -->
        <div class="card">
          <h3>Danh mục Thuốc sẵn có</h3>
          <input type="text" v-model="searchQuery" placeholder="Tìm kiếm thuốc..." class="search-input" />
          <ul class="med-list">
            <li v-for="med in filteredMedicines" :key="med.id" @click="addToCart(med)">
              <span><strong>{{ med.name }}</strong> ({{ med.unit }})</span>
              <button class="btn-add">+</button>
            </li>
          </ul>
        </div>

        <!-- Giỏ hàng và Thanh toán -->
        <div class="card">
          <h3>Hóa đơn hiện tại</h3>
          <table class="cart-table">
            <thead>
              <tr>
                <th>Tên thuốc</th>
                <th>SL</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in cart" :key="index">
                <td>{{ item.name }}</td>
                <td>
                  <input type="number" v-model.number="item.quantity" min="1" style="width: 50px;" />
                </td>
                <td>
                  <button @click="removeFromCart(index)" class="btn-remove">Xóa</button>
                </td>
              </tr>
              <tr v-if="cart.length === 0">
                <td colspan="3" style="text-align: center;">Chưa có sản phẩm trong giỏ hàng</td>
              </tr>
            </tbody>
          </table>

          <button @click="checkout" class="btn-checkout" :disabled="cart.length === 0">
            Thanh toán & Trừ kho FEFO
          </button>
        </div>
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
const cart = ref([]);
const searchQuery = ref('');

const fetchMedicines = async () => {
  try {
    const res = await api.get('/medicines/');
    medicines.value = res.data;
  } catch (e) {
    console.error("Lỗi tải thuốc", e);
  }
};

const filteredMedicines = computed(() => {
  return medicines.value.filter(m => m.name.toLowerCase().includes(searchQuery.value.toLowerCase()));
});

const addToCart = (med) => {
  const existing = cart.value.find(item => item.medicine_id === med.id);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.value.push({
      medicine_id: med.id,
      name: med.name,
      quantity: 1
    });
  }
};

const removeFromCart = (index) => {
  cart.value.splice(index, 1);
};

const checkout = async () => {
  try {
    const payload = {
      items: cart.value.map(item => ({
        medicine_id: item.medicine_id,
        quantity: item.quantity
      }))
    };

    await api.post('/invoices/', payload);
    alert('Thanh toán thành công! Hệ thống đã tự động trừ tồn kho theo chuẩn FEFO.');
    cart.value = [];
  } catch (error) {
    alert('Lỗi thanh toán: ' + (error.response?.data?.detail || 'Không xác định'));
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
.pos-container { display: flex; height: 100vh; background-color: #f4f7f6; }
.sidebar { width: 250px; background-color: #2c3e50; color: white; padding: 20px; }
.sidebar h3 { text-align: center; margin-bottom: 30px; }
.sidebar ul { list-style: none; padding: 0; }
.sidebar li { padding: 10px 15px; margin-bottom: 10px; border-radius: 4px; cursor: pointer; }
.sidebar li:hover, .sidebar li.active { background-color: #34495e; }
.pos-main { flex: 1; padding: 30px; overflow-y: auto; }
.pos-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
.card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.search-input { width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.med-list { list-style: none; padding: 0; max-height: 350px; overflow-y: auto; }
.med-list li { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
.med-list li:hover { background-color: #f9f9f9; }
.btn-add { background-color: #42b983; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }
.cart-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
.cart-table th, .cart-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
.cart-table th { background-color: #f8f9fa; }
.btn-remove { background-color: #e74c3c; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; }
.btn-checkout { width: 100%; background-color: #27ae60; color: white; border: none; padding: 12px; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; }
.btn-checkout:disabled { background-color: #95a5a6; }
</style>