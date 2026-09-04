<template>
  <div class="invoices-container">
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
        <li @click="$router.push('/medicines')">
          Quản lý Thuốc
        </li>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/batches')">
          Quản lý Lô & HSD
        </li>
        <li v-if="userRole === 'manager'" @click="$router.push('/suppliers')">
          Nhà cung cấp
        </li>
        <li @click="$router.push('/pos')">
          Bán hàng (POS)
        </li>
        <li class="active">
          Lịch sử Hóa đơn
        </li>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/ai-chat')">
          Trợ lý AI
        </li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <!-- Khu vực nội dung chính -->
    <div class="main-content">
      <h2>Lịch sử Bán hàng & Quản lý Hóa đơn</h2>

      <!-- Thẻ thống kê nhanh -->
      <div class="stat-cards">
        <div class="stat-card stat-blue">
          <div class="stat-label">Tổng hóa đơn đã xuất</div>
          <div class="stat-value">{{ invoices.length }}</div>
        </div>
        <div class="stat-card stat-green">
          <div class="stat-label">Tổng doanh thu tích lũy</div>
          <div class="stat-value">{{ formatCurrency(totalRevenue) }}</div>
        </div>
      </div>

      <!-- Bảng danh sách hóa đơn -->
      <div class="table-card">
        <div class="table-header">
          <h3>Danh sách hóa đơn bán lẻ</h3>
          <button @click="fetchInvoices" class="btn-refresh">🔄 Tải lại</button>
        </div>

        <table>
          <thead>
            <tr>
              <th>Mã HĐ</th>
              <th>Thời gian tạo</th>
              <th>Tổng tiền</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inv in invoices" :key="inv.id">
              <td><strong>#{{ inv.id }}</strong></td>
              <td>{{ formatDate(inv.created_at) }}</td>
              <td><span class="price-highlight">{{ formatCurrency(inv.total_amount) }}</span></td>
              <td>
                <button @click="openInvoiceDetail(inv.id)" class="btn-detail">Xem chi tiết</button>
              </td>
            </tr>
            <tr v-if="invoices.length === 0">
              <td colspan="4" style="text-align: center; padding: 20px;">Chưa có hóa đơn nào được lập trong hệ thống.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Xem Chi Tiết Hóa Đơn -->
    <div v-if="selectedInvoice" class="modal-overlay" @click.self="selectedInvoice = null">
      <div class="modal-content" id="printable-invoice">
        <div class="modal-header">
          <h3>Chi tiết Hóa đơn #{{ selectedInvoice.id }}</h3>
          <button class="btn-close" @click="selectedInvoice = null">✕</button>
        </div>

        <p class="invoice-meta"><strong>Thời gian xuất:</strong> {{ selectedInvoice.created_at || 'Không xác định' }}</p>

        <table class="modal-table">
          <thead>
            <tr>
              <th>STT</th>
              <th>Tên thuốc</th>
              <th>ĐVT</th>
              <th>Số lượng</th>
              <th>Đơn giá</th>
              <th>Thành tiền</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in selectedInvoice.items" :key="item.id">
              <td>{{ idx + 1 }}</td>
              <td><strong>{{ item.medicine_name }}</strong></td>
              <td>{{ item.unit }}</td>
              <td>{{ item.quantity }}</td>
              <td>{{ formatCurrency(item.unit_price) }}</td>
              <td>{{ formatCurrency(item.subtotal) }}</td>
            </tr>
          </tbody>
        </table>

        <div class="modal-footer-info">
          <h4>Tổng thanh toán: <span class="total-text">{{ formatCurrency(selectedInvoice.total_amount) }}</span></h4>
        </div>

        <div class="modal-actions">
          <button @click="printInvoice" class="btn-print">🖨️ In hóa đơn</button>
          <button @click="selectedInvoice = null" class="btn-cancel">Đóng</button>
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
const invoices = ref([]);
const selectedInvoice = ref(null);

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

const totalRevenue = computed(() => {
  return invoices.value.reduce((sum, inv) => sum + (inv.total_amount || 0), 0);
});

const fetchInvoices = async () => {
  try {
    const res = await api.get('/invoices/');
    invoices.value = res.data;
  } catch (error) {
    console.error('Lỗi tải danh sách hóa đơn:', error);
  }
};

const openInvoiceDetail = async (invoiceId) => {
  try {
    const res = await api.get(`/invoices/${invoiceId}`);
    selectedInvoice.value = res.data;
  } catch (error) {
    alert('Không thể tải chi tiết hóa đơn: ' + (error.response?.data?.detail || 'Lỗi kết nối'));
  }
};

const formatCurrency = (val) => {
  if (val === undefined || val === null) return '0 đ';
  return Number(val).toLocaleString('vi-VN') + ' đ';
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  const d = new Date(dateStr);
  return isNaN(d.getTime()) ? dateStr : d.toLocaleString('vi-VN');
};

const printInvoice = () => {
  window.print();
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

onMounted(() => {
  fetchInvoices();
});
</script>

<style scoped>
.invoices-container { display: flex; height: 100vh; background-color: #f4f7f6; }
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

.stat-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px; }
.stat-card { padding: 20px; border-radius: 8px; color: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.stat-blue { background: linear-gradient(135deg, #2980b9, #3498db); }
.stat-green { background: linear-gradient(135deg, #27ae60, #2ecc71); }
.stat-label { font-size: 14px; opacity: 0.9; margin-bottom: 8px; }
.stat-value { font-size: 26px; font-weight: bold; }

.table-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.table-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.btn-refresh { background-color: #34495e; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
th { background-color: #f8f9fa; }
.price-highlight { color: #27ae60; font-weight: bold; }
.btn-detail { background-color: #3498db; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; width: 650px; max-width: 90%; max-height: 90vh; overflow-y: auto; border-radius: 8px; padding: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
.modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
.btn-close { background: none; border: none; font-size: 18px; cursor: pointer; }
.invoice-meta { font-size: 14px; color: #555; margin-bottom: 15px; }
.modal-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
.modal-table th, .modal-table td { border: 1px solid #eee; padding: 8px; text-align: left; }
.modal-footer-info { text-align: right; margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 10px; }
.total-text { color: #e74c3c; font-size: 20px; font-weight: bold; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.btn-print { background-color: #27ae60; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; }
.btn-cancel { background-color: #95a5a6; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; }

@media print {
  body * { visibility: hidden; }
  #printable-invoice, #printable-invoice * { visibility: visible; }
  #printable-invoice { position: absolute; left: 0; top: 0; width: 100%; box-shadow: none; padding: 0; }
  .modal-actions, .btn-close { display: none; }
}
</style>