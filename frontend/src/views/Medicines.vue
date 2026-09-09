<template>
  <div class="med-container">
    <!-- Sidebar điều hướng -->
    <div class="sidebar">
      <h3>Quản lý Nhà thuốc</h3>

      <div class="user-badge-box">
        <span class="username-text">👤 {{ currentUsername }}</span>
        <span :class="['role-badge', `badge-${userRole}`]">{{ roleLabel }}</span>
      </div>

      <ul>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/dashboard')">Trang chủ</li>
        <li class="active">Quản lý Thuốc</li>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/batches')">Quản lý Lô & HSD</li>
        <li v-if="userRole === 'manager'" @click="$router.push('/suppliers')">Nhà cung cấp</li>
        <li @click="$router.push('/pos')">Bán hàng (POS)</li>
        <li @click="$router.push('/invoices')">Lịch sử Hóa đơn</li>
        <li v-if="['manager', 'pharmacist'].includes(userRole)" @click="$router.push('/ai-chat')">Trợ lý AI</li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <!-- Nội dung chính -->
    <div class="main-content">
      <div class="content-header">
        <div>
          <h2>Quản lý Thuốc & Danh mục GPP</h2>
          <p class="subtitle">Tra cứu, quản lý thông tin dược phẩm và tích hợp AI Vision quét thông tin từ ảnh vỏ hộp.</p>
        </div>
        <button 
          v-if="userRole !== 'cashier'" 
          @click="showForm = !showForm" 
          class="btn-primary"
        >
          {{ showForm ? '✖ Đóng Form' : '➕ Thêm Thuốc Mới' }}
        </button>
      </div>

      <!-- Thẻ thống kê nhanh -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">💊</div>
          <div>
            <div class="stat-value">{{ medicines.length }}</div>
            <div class="stat-label">Tổng loại thuốc</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div>
            <div class="stat-value">{{ totalStock }}</div>
            <div class="stat-label">Tổng tồn kho</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🤖</div>
          <div>
            <div class="stat-value">{{ approvedCount }}</div>
            <div class="stat-label">Đã chuẩn hóa AI</div>
          </div>
        </div>
      </div>

      <!-- Modal / Khu vực Thêm thuốc mới tích hợp AI Vision -->
      <div v-if="showForm && userRole !== 'cashier'" class="form-panel">
        <div class="panel-header">
          <h3>➕ Thêm thuốc mới vào hệ thống</h3>
          <span class="badge-ai-tip">💡 Tải ảnh bao bì để AI tự động điền form</span>
        </div>

        <div class="form-layout">
          <!-- Cột trái: Tải ảnh & AI Vision -->
          <div class="ai-scan-column">
            <div class="image-preview-box">
              <img v-if="previewImageUrl" :src="previewImageUrl" alt="Xem trước ảnh thuốc" class="preview-img" />
              <div v-else class="upload-placeholder">
                <span style="font-size: 36px;">📸</span>
                <p>Chưa có ảnh bao bì</p>
                <small>Hỗ trợ JPG, PNG (tối đa 5MB)</small>
              </div>
            </div>

            <div class="upload-actions">
              <input type="file" ref="fileInput" @change="onFileSelected" accept="image/*" class="file-hidden" id="medicine-file" />
              <label for="medicine-file" class="btn-secondary">📁 Chọn ảnh vỏ hộp</label>
              <button 
                type="button" 
                @click="scanWithAI" 
                class="btn-ai"
                :disabled="!selectedFile || isScanning"
              >
                {{ isScanning ? '⏳ AI Đang đọc ảnh...' : '🤖 AI Quét Vỏ Hộp' }}
              </button>
            </div>

            <div v-if="scanNotice" class="scan-notice">
              {{ scanNotice }}
            </div>
          </div>

          <!-- Cột phải: Form thông tin chi tiết -->
          <form @submit.prevent="createMedicine" class="form-inputs">
            <div class="input-row">
              <div class="form-group flex-2">
                <label>Tên thuốc <span class="required">*</span></label>
                <input type="text" v-model="form.name" placeholder="Ví dụ: Panadol Extra 500mg" required />
              </div>
              <div class="form-group flex-1">
                <label>Số đăng ký (SĐK)</label>
                <input type="text" v-model="form.registration_number" placeholder="VD-25219-16" />
              </div>
            </div>

            <div class="input-row">
              <div class="form-group flex-1">
                <label>Đơn vị tính <span class="required">*</span></label>
                <input type="text" v-model="form.unit" placeholder="Hộp / Vỉ / Viên" required />
              </div>
              <div class="form-group flex-1">
                <label>Giá bán (VNĐ) <span class="required">*</span></label>
                <input type="number" v-model.number="form.price" placeholder="0" min="0" step="500" required />
              </div>
              <div class="form-group flex-1">
                <label>Dạng bào chế</label>
                <input type="text" v-model="form.dosage_form" placeholder="Viên nén bao phim..." />
              </div>
              <div class="form-group flex-1">
                <label>Quy cách đóng gói</label>
                <input type="text" v-model="form.packaging" placeholder="Hộp 15 vỉ x 12 viên" />
              </div>
            </div>

            <div class="input-row">
              <div class="form-group flex-1">
                <label>Nhà sản xuất</label>
                <input type="text" v-model="form.manufacturer" placeholder="Tên công ty sản xuất" />
              </div>
              <div class="form-group flex-1">
                <label>Nước sản xuất</label>
                <input type="text" v-model="form.country" placeholder="Việt Nam, Pháp..." />
              </div>
              <div class="form-group flex-1">
                <label>ID Danh mục</label>
                <input type="number" v-model.number="form.category_id" required />
              </div>
            </div>

            <div class="form-group">
              <label>Thành phần hoạt chất & hàm lượng</label>
              <textarea v-model="form.ingredients" rows="2" placeholder="Ví dụ: Paracetamol 500mg, Caffeine 65mg"></textarea>
            </div>

            <div class="form-group">
              <label>Mô tả / Chỉ định y khoa</label>
              <textarea v-model="form.description" rows="2" placeholder="Công dụng, liều dùng tham khảo..."></textarea>
            </div>

            <div class="form-buttons">
              <button type="button" @click="resetForm" class="btn-cancel">Hủy bỏ</button>
              <button type="submit" class="btn-submit" :disabled="isSubmitting">
                {{ isSubmitting ? 'Đang lưu...' : '💾 Lưu Thuốc Vào Hệ Thống' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Thanh tìm kiếm -->
      <div class="filter-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="🔍 Tìm kiếm theo tên thuốc, số đăng ký hoặc hoạt chất..." 
          class="search-input"
        />
      </div>

      <!-- Bảng danh sách thuốc -->
      <div class="table-container">
        <table class="modern-table">
          <thead>
            <tr>
              <th style="width: 60px;">Ảnh</th>
              <th>Tên thuốc & SĐK</th>
              <th>Hoạt chất & Bào chế</th>
              <th>Quy cách</th>
              <th>Đơn vị</th>
              <th>Giá bán</th>
              <th>Tồn kho</th>
              <th>Nhà SX</th>
              <th v-if="userRole === 'manager'" style="width: 80px;">Thao tác</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="med in filteredMedicines" :key="med.id">
              <td>
                <img 
                  :src="med.image_url ? getFullImageUrl(med.image_url) : 'https://via.placeholder.com/50?text=Thuốc'" 
                  alt="Ảnh" 
                  class="table-thumb" 
                />
              </td>
              <td>
                <div class="med-title">{{ med.name }}</div>
                <small class="med-sdk">SĐK: {{ med.registration_number || 'Chưa có' }}</small>
              </td>
              <td>
                <div class="med-ingre">{{ med.ingredients || med.description || 'Chưa cập nhật' }}</div>
                <small class="badge-form">{{ med.dosage_form || 'Chưa rõ' }}</small>
              </td>
              <td>{{ med.packaging || '-' }}</td>
              <td><span class="badge-unit">{{ med.unit }}</span></td>
              <td><strong class="text-price">{{ formatPrice(med.price) }}</strong></td>
              <td><strong>{{ med.quantity || 0 }}</strong></td>
              <td><small>{{ med.manufacturer || med.country || '-' }}</small></td>
              <td v-if="userRole === 'manager'">
                <button @click="deleteMedicine(med.id)" class="btn-delete" title="Xóa thuốc">🗑️</button>
              </td>
            </tr>
            <tr v-if="filteredMedicines.length === 0">
              <td :colspan="userRole === 'manager' ? 9 : 8" class="empty-state">
                Không tìm thấy loại thuốc nào phù hợp với từ khóa.
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
const searchQuery = ref('');
const showForm = ref(false);
const isScanning = ref(false);
const isSubmitting = ref(false);
const selectedFile = ref(null);
const previewImageUrl = ref('');
const scanNotice = ref('');

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
  registration_number: '',
  unit: 'Hộp',
  price: 0,
  dosage_form: '',
  packaging: '',
  manufacturer: '',
  country: '',
  category_id: 1,
  ingredients: '',
  description: '',
  image_url: '',
  quantity: 0
});

const totalStock = computed(() => {
  return medicines.value.reduce((sum, m) => sum + (m.quantity || 0), 0);
});

const approvedCount = computed(() => {
  return medicines.value.filter(m => m.registration_number || m.ingredients).length;
});

const filteredMedicines = computed(() => {
  const q = searchQuery.value.toLowerCase().trim();
  if (!q) return medicines.value;
  return medicines.value.filter(m => 
    (m.name && m.name.toLowerCase().includes(q)) ||
    (m.registration_number && m.registration_number.toLowerCase().includes(q)) ||
    (m.ingredients && m.ingredients.toLowerCase().includes(q))
  );
});

const getFullImageUrl = (path) => {
  if (!path) return '';
  if (path.startsWith('http')) return path;
  return `http://localhost:8000${path}`;
};

const formatPrice = (value) => {
  if (!value) return '0 đ';
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
};

const fetchMedicines = async () => {
  try {
    const res = await api.get('/medicines/');
    medicines.value = res.data;
  } catch (error) {
    console.error("Lỗi tải thuốc", error);
  }
};

const onFileSelected = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  selectedFile.value = file;
  previewImageUrl.value = URL.createObjectURL(file);
  scanNotice.value = 'Đã chọn ảnh. Bấm "AI Quét Vỏ Hộp" để tự động điền form.';
};

const scanWithAI = async () => {
  if (!selectedFile.value) return;
  isScanning.value = true;
  scanNotice.value = '🤖 AI đang phân tích vỏ bao bì thuốc...';

  try {
    const formData = new FormData();
    formData.append('file', selectedFile.value);

    const res = await api.post('/ai/scan-medicine-image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    const d = res.data;
    if (d.name) form.value.name = d.name;
    if (d.registration_number) form.value.registration_number = d.registration_number;
    if (d.unit) form.value.unit = d.unit;
    if (d.estimated_price) form.value.price = d.estimated_price;
    if (d.dosage_form) form.value.dosage_form = d.dosage_form;
    if (d.packaging) form.value.packaging = d.packaging;
    if (d.manufacturer) form.value.manufacturer = d.manufacturer;
    if (d.country) form.value.country = d.country;
    if (d.ingredients) form.value.ingredients = d.ingredients;
    if (d.description) form.value.description = d.description;
    if (d.image_url) {
      form.value.image_url = d.image_url;
      previewImageUrl.value = getFullImageUrl(d.image_url);
    }

    scanNotice.value = '✅ AI đã trích xuất thông tin thành công! Vui lòng kiểm tra lại trước khi lưu.';
  } catch (error) {
    scanNotice.value = '❌ Lỗi quét AI: ' + (error.response?.data?.detail || 'Không thể đọc ảnh');
  } finally {
    isScanning.value = false;
  }
};

const createMedicine = async () => {
  isSubmitting.value = true;
  try {
    await api.post('/medicines/', form.value);
    alert('Thêm thuốc thành công!');
    resetForm();
    showForm.value = false;
    fetchMedicines();
  } catch (error) {
    alert('Lỗi lưu thuốc: ' + (error.response?.data?.detail || 'Không xác định'));
  } finally {
    isSubmitting.value = false;
  }
};

const resetForm = () => {
  form.value = {
    name: '',
    registration_number: '',
    unit: 'Hộp',
    price: 0,
    dosage_form: '',
    packaging: '',
    manufacturer: '',
    country: '',
    category_id: 1,
    ingredients: '',
    description: '',
    image_url: '',
    quantity: 0
  };
  selectedFile.value = null;
  previewImageUrl.value = '';
  scanNotice.value = '';
};

const deleteMedicine = async (id) => {
  if (confirm('Bạn có chắc chắn muốn xóa loại thuốc này khỏi danh mục không?')) {
    try {
      await api.delete(`/medicines/${id}`);
      fetchMedicines();
    } catch (error) {
      alert('Lỗi: ' + (error.response?.data?.detail || 'Không thể xóa'));
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
.med-container { display: flex; height: 100vh; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
.sidebar { width: 250px; background-color: #1e293b; color: white; padding: 20px; flex-shrink: 0; }
.sidebar h3 { text-align: center; margin-bottom: 15px; font-size: 18px; }

.user-badge-box { background-color: #0f172a; padding: 10px 12px; border-radius: 6px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
.username-text { font-size: 13px; font-weight: 500; }
.role-badge { font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: bold; text-transform: uppercase; }
.badge-manager { background-color: #ef4444; color: white; }
.badge-pharmacist { background-color: #3b82f6; color: white; }
.badge-cashier { background-color: #10b981; color: white; }

.sidebar ul { list-style: none; padding: 0; }
.sidebar li { padding: 10px 15px; margin-bottom: 8px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
.sidebar li:hover, .sidebar li.active { background-color: #334155; }

.main-content { flex: 1; padding: 25px 35px; overflow-y: auto; }
.content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.content-header h2 { margin: 0; color: #0f172a; font-size: 24px; }
.subtitle { margin: 4px 0 0 0; color: #64748b; font-size: 14px; }

.btn-primary { background-color: #2563eb; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.2s; }
.btn-primary:hover { background-color: #1d4ed8; }

.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
.stat-card { background: white; padding: 15px 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; align-items: center; gap: 15px; }
.stat-icon { font-size: 28px; background-color: #eff6ff; padding: 10px; border-radius: 8px; }
.stat-value { font-size: 22px; font-weight: bold; color: #1e293b; }
.stat-label { font-size: 13px; color: #64748b; }

.form-panel { background: white; padding: 22px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 25px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px; }
.panel-header h3 { margin: 0; color: #1e293b; font-size: 16px; }
.badge-ai-tip { background-color: #f3e8ff; color: #7e22ce; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }

.form-layout { display: grid; grid-template-columns: 280px 1fr; gap: 20px; }
.ai-scan-column { display: flex; flex-direction: column; align-items: center; background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px dashed #cbd5e1; }
.image-preview-box { width: 100%; height: 200px; background-color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; overflow: hidden; border: 1px solid #e2e8f0; margin-bottom: 12px; }
.preview-img { width: 100%; height: 100%; object-fit: contain; }
.upload-placeholder { text-align: center; color: #94a3b8; }
.upload-placeholder p { margin: 6px 0 2px 0; font-size: 13px; font-weight: 600; }
.file-hidden { display: none; }
.upload-actions { display: flex; flex-direction: column; width: 100%; gap: 8px; }
.btn-secondary { background-color: #e2e8f0; color: #334155; text-align: center; padding: 8px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; }
.btn-ai { background-color: #8b5cf6; color: white; border: none; padding: 9px; border-radius: 6px; font-size: 13px; font-weight: bold; cursor: pointer; }
.btn-ai:hover { background-color: #7c3aed; }
.btn-ai:disabled { background-color: #cbd5e1; cursor: not-allowed; }
.scan-notice { margin-top: 10px; font-size: 12px; color: #475569; text-align: center; line-height: 1.4; }

.form-inputs { display: flex; flex-direction: column; gap: 12px; }
.input-row { display: flex; gap: 12px; }
.flex-1 { flex: 1; }
.flex-2 { flex: 2; }
.form-group { display: flex; flex-direction: column; }
.form-group label { font-size: 12px; font-weight: 600; color: #334155; margin-bottom: 4px; }
.required { color: #ef4444; }
.form-group input, .form-group textarea { padding: 8px 12px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 13px; outline: none; }
.form-group input:focus, .form-group textarea:focus { border-color: #2563eb; }

.form-buttons { display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px; }
.btn-cancel { background: transparent; border: 1px solid #cbd5e1; color: #64748b; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
.btn-submit { background-color: #10b981; color: white; border: none; padding: 8px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }
.btn-submit:hover { background-color: #059669; }

.filter-bar { margin-bottom: 15px; }
.search-input { width: 100%; padding: 10px 15px; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; font-size: 14px; background-color: white; }

.table-container { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); overflow: hidden; }
.modern-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.modern-table th { background-color: #f8fafc; color: #475569; font-weight: 600; text-align: left; padding: 12px 14px; border-bottom: 1px solid #e2e8f0; }
.modern-table td { padding: 12px 14px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
.modern-table tr:hover { background-color: #f8fafc; }

.table-thumb { width: 45px; height: 45px; object-fit: cover; border-radius: 6px; border: 1px solid #e2e8f0; }
.med-title { font-weight: 600; color: #1e293b; }
.med-sdk { color: #64748b; font-size: 11px; }
.med-ingre { font-size: 12px; color: #334155; }
.badge-form { background-color: #f1f5f9; color: #475569; padding: 1px 6px; border-radius: 4px; font-size: 10px; }
.badge-unit { background-color: #e0f2fe; color: #0284c7; padding: 2px 8px; border-radius: 10px; font-weight: 600; font-size: 11px; }
.text-price { color: #059669; font-size: 13px; }
.btn-delete { background: none; border: none; font-size: 16px; cursor: pointer; padding: 4px 8px; border-radius: 4px; }
.btn-delete:hover { background-color: #fee2e2; }
.empty-state { text-align: center; color: #94a3b8; padding: 30px !important; }
</style>