<template>
  <div class="ai-container">
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
        <li @click="$router.push('/pos')">
          Bán hàng (POS)
        </li>
        <li class="active">
          Trợ lý AI & Guardrail
        </li>
        <li @click="logout" style="color: #e74c3c; cursor: pointer;">Đăng xuất</li>
      </ul>
    </div>

    <!-- Khu vực Chat AI -->
    <div class="chat-main">
      <h2>Trợ lý Dược học AI & Kiểm duyệt Tương tác</h2>
      
      <div class="chat-box">
        <div v-for="(msg, index) in messages" :key="index" :class="['message', msg.sender]">
          <div class="msg-content">
            <strong>{{ msg.sender === 'user' ? `${roleLabel}:` : 'AI Assistant:' }}</strong>
            <p>{{ msg.text }}</p>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <input 
          type="text" 
          v-model="inputMessage" 
          @keyup.enter="sendMessage" 
          placeholder="Nhập câu hỏi tra cứu thuốc, liều dùng hoặc kiểm tra tương tác..." 
        />
        <button @click="sendMessage" :disabled="isLoading">
          {{ isLoading ? 'Đang phân tích...' : 'Gửi hỏi AI' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();

const userRole = ref(localStorage.getItem('role') || 'pharmacist');
const currentUsername = ref(localStorage.getItem('username') || 'Dược sĩ');

const roleLabel = computed(() => {
  switch (userRole.value) {
    case 'manager': return 'Quản lý';
    case 'pharmacist': return 'Dược sĩ';
    case 'cashier': return 'Thu ngân';
    default: return userRole.value;
  }
});

const messages = ref([
  { sender: 'ai', text: 'Xin chào! Tôi là trợ lý AI tích hợp bộ rào chắn (Guardrail). Tôi có thể giúp gì cho bạn trong việc tra cứu thuốc hoặc kiểm tra tương tác hôm nay?' }
]);
const inputMessage = ref('');
const isLoading = ref(false);

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return;

  const userText = inputMessage.value;
  messages.value.push({ sender: 'user', text: userText });
  inputMessage.value = '';
  isLoading.value = true;

  try {
    const res = await api.post('/ai/consult', { prompt: userText });
    messages.value.push({ sender: 'ai', text: res.data.response });
  } catch (error) {
    messages.value.push({ sender: 'ai', text: 'Xin lỗi, hiện tại hệ thống AI không phản hồi được. Vui lòng kiểm tra lại kết nối.' });
  } finally {
    isLoading.value = false;
  }
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};
</script>

<style scoped>
.ai-container { display: flex; height: 100vh; background-color: #f4f7f6; }
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

.chat-main { flex: 1; display: flex; flex-direction: column; padding: 30px; height: 100vh; box-sizing: border-box; }
.chat-box { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow-y: auto; margin-bottom: 20px; display: flex; flex-direction: column; gap: 15px; }
.message { display: flex; max-width: 75%; }
.message.user { align-self: flex-end; }
.message.ai { align-self: flex-start; }
.msg-content { padding: 12px 16px; border-radius: 8px; line-height: 1.4; }
.message.user .msg-content { background-color: #dcf8c6; color: #333; }
.message.ai .msg-content { background-color: #f1f0f0; color: #333; }
.chat-input-area { display: flex; gap: 10px; }
.chat-input-area input { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 15px; }
.chat-input-area button { background-color: #42b983; color: white; border: none; padding: 0 20px; border-radius: 4px; font-weight: bold; cursor: pointer; }
.chat-input-area button:disabled { background-color: #9cdbbf; }
</style>