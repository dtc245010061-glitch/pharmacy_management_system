<template>
  <div class="pos-container">
    <!-- Sidebar điều hướng phân quyền theo vai trò -->
    <div class="sidebar">
      <h3>Quản lý Nhà thuốc</h3>

      <!-- Thông tin tài khoản và vai trò đăng nhập -->
      <div class="user-badge-box">
        <span class="username-text">👤 {{ currentUsername }}</span>
        <span :class="['role-badge', `badge-${userRole}`]">{{ roleLabel }}</span>
      </div>

      <ul>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/dashboard')">
          Trang chủ
        </li>
        <li @click="$router.push('/medicines')">
          Quản lý Thuốc
        </li>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/batches')">
          Quản lý Lô & HSD
        </li>
        <li v-if="userRole === 'manager'" @click="$router.push('/suppliers')">
          Nhà cung cấp
        </li>
        <li class="active">Bán hàng (POS)</li>
        <li @click="$router.push('/invoices')">
          Lịch sử Hóa đơn
        </li>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/ai-chat')">
          Trợ lý AI
        </li>
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
              <span><strong>{{ med.name }}</strong> ({{ med.unit }}) - Tồn: {{ med.quantity || 0 }}</span>
              <button class="btn-add">+</button>
            </li>
            <li v-if="filteredMedicines.length === 0" style="padding: 10px; color: #7f8c8d; text-align: center;">
              Không tìm thấy loại thuốc phù hợp.
            </li>
          </ul>
        </div>

        <!-- Giỏ hàng và Thanh toán -->
        <div class="card">
          <div class="cart-header">
            <h3>Hóa đơn hiện tại</h3>
            <button 
              v-if="cart.length >= 2" 
              @click="checkDrugInteractions" 
              class="btn-ai-scan"
              :disabled="isCheckingAI"
            >
              {{ isCheckingAI ? '🤖 Đang kiểm tra AI...' : '🤖 AI Quét Tương Tác' }}
            </button>
          </div>

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

          <!-- Trạng thái đang quét tự động -->
          <div v-if="isCheckingAI" class="ai-alert-box ai-alert-scanning">
            🤖 <strong>AI Guardrail:</strong> Đang phân tích tương tác chéo giữa các loại thuốc trong đơn...
          </div>

          <!-- Khung cảnh báo AI Guardrail khi có kết quả quét -->
          <div v-else-if="interactionResult" :class="['ai-alert-box', `ai-alert-${interactionResult.severity}`]">
            <div class="ai-alert-title">
              <strong>{{ getSeverityTitle(interactionResult.severity) }}</strong>
            </div>
            <p class="ai-alert-summary">{{ interactionResult.summary }}</p>
            <p class="ai-alert-details">{{ interactionResult.details }}</p>
          </div>

          <button @click="checkout" class="btn-checkout" :disabled="cart.length === 0 || isCheckingAI">
            Thanh toán & Trừ kho FEFO
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const medicines = ref([]);
const cart = ref([]);
const searchQuery = ref('');

const isCheckingAI = ref(false);
const interactionResult = ref(null);
let debounceTimer = null;

const userRole = ref(localStorage.getItem('role') || 'cashier');
const currentUsername = ref(localStorage.getItem('username') || 'Thu ngân');

const roleLabel = computed(() => {
  switch (userRole.value) {
    case 'manager': return 'Quản lý';
    case 'pharmacist': return 'Dược sĩ';
    case 'cashier': return 'Thu ngân';
    default: return userRole.value;
  }
});

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

// Tự động quét tương tác thuốc khi danh mục thuốc trong giỏ hàng thay đổi (thêm/bớt)
watch(
  () => cart.value.map(item => item.medicine_id).join(','),
  () => {
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }

    if (cart.value.length < 2) {
      interactionResult.value = null;
      isCheckingAI.value = false;
      return;
    }

    debounceTimer = setTimeout(() => {
      checkDrugInteractions();
    }, 600);
  }
);

const checkDrugInteractions = async () => {
  if (cart.value.length < 2) return;
  isCheckingAI.value = true;
  try {
    const medicineNames = cart.value.map(item => item.name);
    const res = await api.post('/ai/check-interactions', {
      medicines: medicineNames
    });
    interactionResult.value = res.data;
  } catch (error) {
    console.error('Lỗi kiểm tra tương tác thuốc:', error);
  } finally {
    isCheckingAI.value = false;
  }
};

const getSeverityTitle = (severity) => {
  switch (severity) {
    case 'danger': return '⛔ NGUY HIỂM / CHỐNG CHỈ ĐỊNH (AI GUARDRAIL)';
    case 'warning': return '⚠️ CẢNH BÁO TƯƠNG TÁC CẦN LƯU Ý (AI GUARDRAIL)';
    default: return '✅ AN TOÀN - KHÔNG CÓ TƯƠNG TÁC BẤT LỢI';
  }
};

const checkout = async () => {
  if (cart.value.length >= 2 && !interactionResult.value) {
    const shouldCheck = confirm('Đơn hàng có từ 2 loại thuốc trở lên. Bạn có muốn chạy AI Quét tương tác thuốc trước khi thanh toán không?');
    if (shouldCheck) {
      await checkDrugInteractions();
      return;
    }
  }

  if (interactionResult.value && interactionResult.value.severity === 'danger') {
    const proceed = confirm('CẢNH BÁO NGUY HIỂM: Đơn thuốc có tương tác đối kháng nghiêm trọng. Bạn có chắc chắn vẫn muốn xuất hóa đơn?');
    if (!proceed) return;
  }

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
    interactionResult.value = null;
    fetchMedicines();
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

.pos-main { flex: 1; padding: 30px; overflow-y: auto; }
.pos-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
.card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.cart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.cart-header h3 { margin: 0; }

.btn-ai-scan { background-color: #8e44ad; color: white; border: none; padding: 6px 12px; border-radius: 4px; font-size: 13px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
.btn-ai-scan:hover { background-color: #732d91; }
.btn-ai-scan:disabled { background-color: #bdc3c7; cursor: not-allowed; }

.search-input { width: 100%; padding: 8px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
.med-list { list-style: none; padding: 0; max-height: 350px; overflow-y: auto; }
.med-list li { display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
.med-list li:hover { background-color: #f9f9f9; }
.btn-add { background-color: #42b983; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }
.cart-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
.cart-table th, .cart-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background-color: #f8f9fa; }
.btn-remove { background-color: #e74c3c; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; }

.ai-alert-box { padding: 12px 15px; border-radius: 6px; margin-bottom: 15px; font-size: 13px; line-height: 1.5; }
.ai-alert-scanning { background-color: #ebf5fb; border-left: 4px solid #3498db; color: #2980b9; font-style: italic; }
.ai-alert-safe { background-color: #e8f8f5; border-left: 4px solid #27ae60; color: #1e8449; }
.ai-alert-warning { background-color: #fef9e7; border-left: 4px solid #f39c12; color: #b7950b; }
.ai-alert-danger { background-color: #fdedec; border-left: 4px solid #e74c3c; color: #c0392b; }
.ai-alert-title { margin-bottom: 4px; font-size: 13px; }
.ai-alert-summary { margin: 4px 0; font-weight: 600; }
.ai-alert-details { margin: 0; white-space: pre-line; }

.btn-checkout { width: 100%; background-color: #27ae60; color: white; border: none; padding: 12px; border-radius: 4px; font-size: 16px; font-weight: bold; cursor: pointer; }
.btn-checkout:disabled { background-color: #95a5a6; cursor: not-allowed; }
</style>