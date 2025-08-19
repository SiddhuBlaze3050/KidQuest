<!-- User List Component -->
<template>
  <BaseModal v-model="isVisible" title="User Management" subtitle="Manage and monitor user accounts" icon="👥"
    @update:modelValue="$emit('update:modelValue', $event)">
    <!-- Search and Filter Controls -->
    <div class="controls-section">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" v-model="searchQuery" placeholder="Search by name or email..." class="search-input" />
      </div>
      <div class="filter-box">
        <select v-model="selectedRole" class="role-filter">
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="parent">Parent</option>
          <option value="child">Child</option>
        </select>
      </div>
    </div>

    <!-- Table Section -->
    <div class="table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>Role</th>
            <th>User</th>
            <th>Email</th>
            <th>Profile Status</th>
            <th>Details</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id" :class="{ 'admin-row': user.role === 'admin' }">
            <td>
              <span class="role-badge" :class="user.role">
                {{ user.role }}
              </span>
            </td>
            <td class="user-cell">
              <div class="user-avatar" :class="user.role">
                {{ user.username.charAt(0).toUpperCase() }}
              </div>
              <span class="username">{{ user.username }}</span>
            </td>
            <td class="email-cell">{{ user.email }}</td>
            <td>
              <span class="status-badge"
                :class="{ 'complete': user.profile_complete, 'incomplete': !user.profile_complete }">
                {{ user.profile_complete ? 'Complete' : 'Incomplete' }}
              </span>
            </td>
            <td>
              <div v-if="user.role === 'parent' && user.children" class="linked-children">
                <span class="detail-label">Children:</span>
                <div class="children-list">
                  <span v-for="child in user.children" :key="child.id" class="child-tag">
                    {{ child.username }}
                  </span>
                </div>
              </div>
              <div v-if="user.role === 'child'" class="child-details">
                <span v-if="user.grade_level">Grade {{ user.grade_level }}</span>
              </div>
            </td>
            <td class="actions-cell">
              <template v-if="user.role !== 'admin'">
                <button @click="editUser(user)" class="action-btn edit">
                  <span class="btn-icon">✏️</span>
                  Edit
                </button>
                <button @click="confirmDelete(user)" class="action-btn delete">
                  <span class="btn-icon">🗑️</span>
                  Delete
                </button>
              </template>
              <span v-else class="protected-text">Protected</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Delete Confirmation Modal -->
    <BaseModal v-if="showDeleteModal" v-model="showDeleteModal" title="Confirm Delete" icon="⚠️">
      <div class="delete-confirmation">
        <p>Are you sure you want to delete user <strong>{{ selectedUser?.username }}</strong>?</p>
        <p class="warning-text">This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="showDeleteModal = false" class="cancel-btn">
            Cancel
          </button>
          <button @click="deleteUser" class="confirm-btn">
            Delete User
          </button>
        </div>
      </div>
    </BaseModal>
  </BaseModal>
</template>

<script>
import { ref, computed } from 'vue'
import axios from 'axios'
import BaseModal from '@/components/common/BaseModal.vue'

export default {
  name: 'UserList',
  components: {
    BaseModal
  },
  props: {
    modelValue: {
      type: Boolean,
      required: true
    }
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const isVisible = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    })

    const users = ref([])
    const searchQuery = ref('')
    const selectedRole = ref('')
    const showDeleteModal = ref(false)
    const selectedUser = ref(null)

    // Filter users based on search query and selected role
    const filteredUsers = computed(() => {
      return users.value.filter(user => {
        const matchesSearch =
          user.username.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          user.email.toLowerCase().includes(searchQuery.value.toLowerCase())

        const matchesRole = !selectedRole.value || user.role === selectedRole.value

        return matchesSearch && matchesRole
      })
    })

    const fetchUsers = async () => {
      try {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
        const response = await axios.get(`${API_BASE_URL}/api/admin/users`)
        users.value = response.data.users
      } catch (error) {
        console.error('Error fetching users:', error)
      }
    }

    const editUser = (user) => {
      // TODO: Implement edit functionality
      console.log('Edit user:', user)
    }

    const confirmDelete = (user) => {
      selectedUser.value = user
      showDeleteModal.value = true
    }

    const deleteUser = async () => {
      if (!selectedUser.value) return

      try {
        await axios.delete(`${API_BASE_URL}/api/admin/users/${selectedUser.value.id}`)
        users.value = users.value.filter(u => u.id !== selectedUser.value.id)
        showDeleteModal.value = false
        selectedUser.value = null
      } catch (error) {
        console.error('Error deleting user:', error)
      }
    }

    // Fetch users on mount
    fetchUsers()

    return {
      isVisible,
      users,
      searchQuery,
      selectedRole,
      showDeleteModal,
      selectedUser,
      filteredUsers,
      editUser,
      confirmDelete,
      deleteUser
    }
  }
}
</script>

<style scoped>
/* Controls Section */
.controls-section {
  padding: 0 2rem 1rem;
  display: flex;
  gap: 1rem;
}

.search-box {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.8);
}

.search-input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 3rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #FFFFFF;
  font-size: 1rem;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.role-filter {
  padding: 0.8rem 2.5rem 0.8rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: #FFFFFF;
  font-size: 1rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='rgba(255, 255, 255, 0.8)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1rem;
}

/* Table Section */
.table-container {
  flex: 1;
  overflow: auto;
  padding: 0 2rem 2rem;
}

.users-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  color: #FFFFFF;
}

.users-table th {
  background: rgba(0, 0, 0, 0.2);
  padding: 1.25rem 1rem;
  text-align: left;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 10;
}

.users-table th:first-child {
  border-top-left-radius: 12px;
}

.users-table th:last-child {
  border-top-right-radius: 12px;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.users-table tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.admin-row {
  background: rgba(99, 102, 241, 0.05);
}

/* User Cell */
.user-cell {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.user-avatar.admin {
  background: linear-gradient(135deg, #818cf8, #6366f1);
}

.user-avatar.parent {
  background: linear-gradient(135deg, #34d399, #10b981);
}

.user-avatar.child {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
}

.username {
  font-weight: 600;
  color: #FFFFFF;
}

.email-cell {
  color: #F0F0F0;
}

/* Role Badge */
.role-badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: capitalize;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.role-badge.admin {
  background: linear-gradient(135deg, #818cf8, #6366f1);
  color: #FFFFFF;
}

.role-badge.parent {
  background: linear-gradient(135deg, #34d399, #10b981);
  color: #FFFFFF;
}

.role-badge.child {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #FFFFFF;
}

/* Status Badge */
.status-badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.status-badge.complete {
  background: linear-gradient(135deg, #34d399, #10b981);
  color: #FFFFFF;
}

.status-badge.incomplete {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: #FFFFFF;
}

/* Linked Children */
.linked-children {
  font-size: 0.9rem;
}

.detail-label {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.children-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.4rem;
}

.child-tag {
  background: rgba(255, 255, 255, 0.15);
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.85rem;
  color: #FFFFFF;
  font-weight: 500;
}

/* Action Buttons */
.actions-cell {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.action-btn {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  color: #FFFFFF;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-btn.edit {
  background: rgba(99, 102, 241, 0.2);
}

.action-btn.edit:hover {
  background: rgba(99, 102, 241, 0.3);
}

.action-btn.delete {
  background: rgba(239, 68, 68, 0.2);
}

.action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.3);
}

.protected-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  font-style: italic;
}

/* Delete Confirmation */
.delete-confirmation {
  padding: 1rem 2rem 2rem;
  text-align: center;
}

.warning-text {
  color: #fca5a5;
  margin: 1rem 0;
  font-weight: 500;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  justify-content: center;
}

.cancel-btn,
.confirm-btn {
  padding: 0.75rem 2rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #FFFFFF;
}

.cancel-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.confirm-btn {
  background: rgba(239, 68, 68, 0.2);
  color: #FFFFFF;
}

.confirm-btn:hover {
  background: rgba(239, 68, 68, 0.3);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .controls-section {
    flex-direction: column;
    padding: 0 1.5rem 1rem;
  }

  .table-container {
    padding: 0 1.5rem 1.5rem;
  }

  .users-table {
    min-width: 900px;
  }
}
</style>
