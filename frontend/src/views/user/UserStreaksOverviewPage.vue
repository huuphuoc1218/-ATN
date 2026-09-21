<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import axiosInstance from '@/utils/axios'
import { useToast } from 'vue-toastification'
import { useAuthStore } from '@/stores/auth'

interface FriendUser {
  id: number
  full_name: string
  email: string
  avatar_url?: string | null
}

interface FriendStreakItem {
  user: FriendUser
  since: string
  current_streak: number
  best_streak: number
}

const toast = useToast()
const authStore = useAuthStore()
const isLoading = ref(false)
const friends = ref<FriendStreakItem[]>([])
const showStreakModal = ref(false)
const selectedFriend = ref<FriendStreakItem | null>(null)

const backendOrigin = computed(() =>
  (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/api\/?$/, ''),
)

const loadFriendStreaks = async () => {
  isLoading.value = true
  try {
    const response = await axiosInstance.get('/friends/me')
    friends.value = response.data.friends || []
  } catch {
    toast.error('Unable to load streak list')
  } finally {
    isLoading.value = false
  }
}

const formatDate = (value: string) => {
  return new Date(value).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
  })
}

const getInitials = (fullName: string) => {
  const parts = fullName.trim().split(' ')
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
}

const getAvatarSrc = (avatarUrl?: string | null) => {
  if (!avatarUrl) return ''
  if (avatarUrl.startsWith('http://') || avatarUrl.startsWith('https://')) return avatarUrl
  if (avatarUrl.startsWith('/')) return `${backendOrigin.value}${avatarUrl}`
  return `${backendOrigin.value}/${avatarUrl}`
}

const currentUserAvatarSrc = computed(() => getAvatarSrc(authStore.user?.avatar_url || null))

const getFirstName = (fullName: string | undefined) => {
  if (!fullName) return 'Friend'
  return fullName.trim().split(' ')[0]
}

const openStreakDetails = (friend: FriendStreakItem) => {
  selectedFriend.value = friend
  showStreakModal.value = true
}

const closeStreakDetails = () => {
  showStreakModal.value = false
  selectedFriend.value = null
}

const handleFriendsUpdated = () => {
  loadFriendStreaks()
}

onMounted(() => {
  loadFriendStreaks()
  window.addEventListener('friends-updated', handleFriendsUpdated)
})

onUnmounted(() => {
  window.removeEventListener('friends-updated', handleFriendsUpdated)
})
</script>

<template>
  <section class="overview-page">
    <div class="panel-head">
      <h2>Friends Streaks</h2>
      <p>All your friends and their current streak progress.</p>
    </div>

    <div v-if="isLoading" class="state">Loading streak list...</div>
    <div v-else-if="friends.length === 0" class="state">No friends yet.</div>

    <div v-else class="table-shell">
      <table class="friends-streak-table">
        <thead>
          <tr>
            <th>Friend</th>
            <th>Email</th>
            <th>Friends Since</th>
            <th>Current Streak</th>
            <th>Best Streak</th>
            <th>View</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="friend in friends" :key="friend.user.id">
            <td>
              <div class="friend-cell">
                <div class="avatar">
                  <img
                    v-if="getAvatarSrc(friend.user.avatar_url)"
                    :src="getAvatarSrc(friend.user.avatar_url)"
                    :alt="friend.user.full_name"
                    class="avatar-image"
                  />
                  <span v-else>{{ getInitials(friend.user.full_name) }}</span>
                </div>
                <span class="name-cell">{{ friend.user.full_name }}</span>
              </div>
            </td>
            <td class="email-cell">{{ friend.user.email }}</td>
            <td>{{ formatDate(friend.since) }}</td>
            <td>
              <div class="current-streak-wrap">
                <span class="streak-chip current">
                  {{ friend.current_streak }} day{{ friend.current_streak === 1 ? '' : 's' }}
                </span>
                <span v-if="friend.current_streak > 0" class="fire-icon" aria-hidden="true"
                  >🔥</span
                >
              </div>
            </td>
            <td>
              <span class="streak-chip best">
                {{ friend.best_streak }} day{{ friend.best_streak === 1 ? '' : 's' }}
              </span>
            </td>
            <td>
              <button class="view-btn" type="button" @click="openStreakDetails(friend)">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showStreakModal" class="modal-overlay" @click.self="closeStreakDetails">
          <div class="streak-modal" v-if="selectedFriend">
            <button class="close-modal-btn" type="button" @click="closeStreakDetails">×</button>

            <div class="streak-capture-area">
              <div class="modal-head">
                <div
                  class="status-pill"
                  :class="selectedFriend.current_streak > 0 ? 'active' : 'inactive'"
                >
                  {{ selectedFriend.current_streak > 0 ? 'Streak Active' : 'Streak Inactive' }}
                </div>
                <div class="modal-headline">PICKLEBALL PARTNER STREAK</div>
                <div class="modal-subline">
                  {{ authStore.user?.full_name || 'You' }} x {{ selectedFriend.user.full_name }}
                </div>
              </div>

              <template v-if="selectedFriend.current_streak > 0">
                <div class="neon-emblem">
                  <div class="score-ball">
                    <div class="score-days">{{ selectedFriend.current_streak }}</div>
                    <div class="score-label">
                      <span>STREAK</span>
                      <span>DAYS</span>
                    </div>
                  </div>
                </div>

                <div class="players-row">
                  <div class="player-block">
                    <div class="player-avatar-wrap self">
                      <img
                        v-if="currentUserAvatarSrc"
                        :src="currentUserAvatarSrc"
                        :alt="authStore.user?.full_name || 'You'"
                        class="player-avatar-image"
                      />
                      <div v-else class="player-avatar">
                        {{ getInitials(authStore.user?.full_name || 'You') }}
                      </div>
                    </div>
                    <div class="player-name">You</div>
                  </div>

                  <div class="pickleball-mark" aria-hidden="true">
                    <img src="/Logo.png" alt="Pickleball logo" class="pickleball-logo" />
                  </div>

                  <div class="player-block">
                    <div class="player-avatar-wrap friend">
                      <img
                        v-if="getAvatarSrc(selectedFriend.user.avatar_url)"
                        :src="getAvatarSrc(selectedFriend.user.avatar_url)"
                        :alt="selectedFriend.user.full_name"
                        class="player-avatar-image"
                      />
                      <div v-else class="player-avatar">
                        {{ getInitials(selectedFriend.user.full_name) }}
                      </div>
                    </div>
                    <div class="player-name">{{ getFirstName(selectedFriend.user.full_name) }}</div>
                  </div>
                </div>

                <div class="metric-grid">
                  <div class="metric-card">
                    <div class="metric-label">Current</div>
                    <div class="metric-value">{{ selectedFriend.current_streak }} days</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Best</div>
                    <div class="metric-value">{{ selectedFriend.best_streak }} days</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Friends Since</div>
                    <div class="metric-value">{{ formatDate(selectedFriend.since) }}</div>
                  </div>
                </div>

                <div class="modal-note">
                  You and {{ selectedFriend.user.full_name }} are on a great run. Keep the rally
                  alive.
                </div>
              </template>

              <template v-else>
                <div class="no-streak-state" aria-hidden="true">
                  <img src="/Logo.png" alt="Pickleball logo" />
                </div>
                <div class="no-streak-box">
                  <div class="no-streak-title">No active streak right now</div>
                  <p>
                    You and {{ selectedFriend.user.full_name }} currently do not have an active
                    streak. Book a match together to restart the streak.
                  </p>
                </div>

                <div class="metric-grid">
                  <div class="metric-card">
                    <div class="metric-label">Current</div>
                    <div class="metric-value">0 day</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Best</div>
                    <div class="metric-value">{{ selectedFriend.best_streak }} days</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-label">Friends Since</div>
                    <div class="metric-value">{{ formatDate(selectedFriend.since) }}</div>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </section>
</template>

<style scoped>
.overview-page {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  display: grid;
  gap: 16px;
}

.panel-head h2 {
  margin: 0;
  font-size: 1.4rem;
  color: #111827;
}

.panel-head p {
  margin: 8px 0 0;
  color: #64748b;
}

.state {
  border: 1px dashed #cbd5e1;
  border-radius: 12px;
  padding: 20px;
  color: #64748b;
  background: #f8fafc;
}

.table-shell {
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  overflow: auto;
}

.friends-streak-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 760px;
  background: white;
}

.friends-streak-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  text-align: left;
  font-size: 0.8rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  font-weight: 700;
  color: #334155;
  background: #f1f5f9;
  border-bottom: 1px solid #cbd5e1;
  padding: 12px 14px;
}

.friends-streak-table tbody td {
  padding: 14px;
  border-bottom: 1px solid #f1f5f9;
  color: #334155;
  font-size: 0.92rem;
}

.friends-streak-table tbody tr:hover {
  background: #f8fafc;
}

.friend-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: white;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.name-cell {
  font-weight: 700;
  color: #0f172a;
}

.email-cell {
  color: #475569;
}

.streak-chip {
  display: inline-block;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.8rem;
  font-weight: 700;
}

.streak-chip.current {
  background: #dcfce7;
  color: #166534;
}

.current-streak-wrap {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.fire-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transform-origin: 50% 100%;
  animation: flame-flicker 0.9s ease-in-out infinite;
}

.view-btn {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  color: #334155;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: #f8fafc;
  border-color: #94a3b8;
}

.view-btn svg {
  width: 18px;
  height: 18px;
}

.streak-chip.best {
  background: #ecfccb;
  color: #3f6212;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(45, 212, 191, 0.16), transparent 40%),
    radial-gradient(circle at 80% 80%, rgba(56, 189, 248, 0.12), transparent 45%),
    rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow-y: auto;
  overscroll-behavior: contain;
  z-index: 10000;
}

.streak-modal {
  width: 100%;
  max-width: 760px;
  max-height: calc(100dvh - 40px);
  background:
    radial-gradient(circle at 18% 16%, rgba(45, 212, 191, 0.2), transparent 46%),
    radial-gradient(circle at 88% 84%, rgba(14, 165, 233, 0.22), transparent 48%),
    linear-gradient(165deg, #0b1530 0%, #102247 48%, #0a1736 100%);
  border: 1px solid rgba(125, 211, 252, 0.35);
  border-radius: 28px;
  padding: 24px 24px 28px;
  position: relative;
  text-align: center;
  box-shadow:
    0 24px 80px rgba(2, 6, 23, 0.72),
    inset 0 1px 0 rgba(226, 232, 240, 0.18);
  overflow: hidden;
  overflow-y: auto;
}

.streak-modal::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: 28px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}

.close-modal-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 38px;
  height: 38px;
  border: 1px solid rgba(148, 163, 184, 0.45);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.42);
  color: #cbd5e1;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.25s ease;
}

.close-modal-btn:hover {
  color: #f8fafc;
  border-color: rgba(147, 197, 253, 0.9);
  background: rgba(30, 41, 59, 0.85);
}

.modal-head {
  margin: 0 auto 18px;
  width: min(100%, 560px);
  display: grid;
  justify-items: center;
  gap: 8px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border: 1px solid transparent;
}

.status-pill.active {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(74, 222, 128, 0.5);
  color: #86efac;
}

.status-pill.inactive {
  background: rgba(249, 115, 22, 0.16);
  border-color: rgba(251, 146, 60, 0.48);
  color: #fdba74;
}

.modal-headline {
  color: #f8fafc;
  font-size: 1.45rem;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.modal-subline {
  color: #bfdbfe;
  font-size: 0.92rem;
  font-weight: 600;
  letter-spacing: 0.03em;
}

.streak-capture-area {
  display: grid;
  gap: 0;
  min-width: 0;
}

.neon-emblem {
  position: relative;
  width: fit-content;
  margin: 6px auto 0;
}

.score-ball {
  width: 300px;
  height: 300px;
  margin: 0 auto;
  border-radius: 999px;
  position: relative;
  z-index: 1;
  background: radial-gradient(
    circle at 30% 28%,
    #6ee7b7 0%,
    #22c55e 36%,
    #15803d 78%,
    #0f5132 100%
  );
  color: #ffffff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 4px solid rgba(110, 231, 183, 0.9);
  box-shadow:
    0 0 0 7px rgba(16, 185, 129, 0.22),
    0 0 34px rgba(52, 211, 153, 0.72),
    0 16px 38px rgba(15, 118, 110, 0.4);
}

.score-ball::before,
.score-ball::after {
  content: '';
  position: absolute;
  inset: 12px;
  border-radius: 999px;
  pointer-events: none;
}

.score-ball::before {
  border: 2px solid rgba(187, 247, 208, 0.55);
}

.score-ball::after {
  inset: -10px;
  border: 2px solid rgba(134, 239, 172, 0.45);
  box-shadow: 0 0 16px rgba(74, 222, 128, 0.6);
}

.score-days {
  font-size: 7rem;
  font-weight: 900;
  line-height: 1;
  font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
  margin: 0;
  text-shadow: 0 4px 10px rgba(15, 23, 42, 0.65);
}

.score-label {
  font-size: 2.7rem;
  font-weight: 900;
  line-height: 1;
  font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
  text-transform: uppercase;
  text-align: center;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  text-shadow: 0 2px 6px rgba(15, 23, 42, 0.65);
}

.score-label span {
  display: block;
}

.players-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-top: 18px;
}

.player-block {
  display: grid;
  justify-items: center;
  gap: 8px;
}

.player-name {
  color: #e2e8f0;
  font-size: 1rem;
  font-weight: 700;
}

.player-avatar-wrap {
  width: 92px;
  height: 92px;
  border-radius: 999px;
  border: 3px solid #93c5fd;
  overflow: hidden;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.player-avatar {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 800;
  color: #334155;
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
}

.pickleball-mark {
  width: 128px;
  height: 128px;
  animation: ball-bounce 1.2s ease-in-out infinite;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pickleball-logo {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 10px rgba(2, 6, 23, 0.35));
}

.modal-note {
  margin-top: 16px;
  color: #dbeafe;
  font-weight: 600;
  font-size: 0.98rem;
  line-height: 1.45;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(125, 211, 252, 0.24);
}

.metric-grid {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.metric-card {
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.36);
  background: rgba(15, 23, 42, 0.42);
  padding: 11px 10px;
}

.metric-label {
  color: #93c5fd;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 700;
}

.metric-value {
  margin-top: 4px;
  color: #f8fafc;
  font-size: 1rem;
  font-weight: 800;
}

.no-streak-state {
  width: 132px;
  height: 132px;
  margin: 2px auto 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-streak-state img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 8px 16px rgba(2, 6, 23, 0.38));
}

.no-streak-box {
  margin-top: 4px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.58);
  border: 1px solid rgba(251, 146, 60, 0.5);
  padding: 18px;
}

.no-streak-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: #fed7aa;
}

.no-streak-box p {
  margin: 8px 0 0;
  color: #e2e8f0;
  line-height: 1.5;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@keyframes flame-flicker {
  0% {
    transform: rotate(-6deg) scale(1);
    filter: drop-shadow(0 0 0 rgba(249, 115, 22, 0));
  }
  50% {
    transform: rotate(6deg) scale(1.13);
    filter: drop-shadow(0 0 5px rgba(249, 115, 22, 0.55));
  }
  100% {
    transform: rotate(-4deg) scale(1);
    filter: drop-shadow(0 0 0 rgba(249, 115, 22, 0));
  }
}

@keyframes ball-bounce {
  0%,
  100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-6px);
  }
}

@media (max-width: 1024px) {
  .overview-page {
    padding: 16px;
  }

  .friends-streak-table {
    min-width: 680px;
  }

  .friends-streak-table thead th,
  .friends-streak-table tbody td {
    padding: 10px;
    font-size: 0.84rem;
  }

  .modal-overlay {
    align-items: flex-start;
    padding: 12px;
  }

  .streak-modal {
    max-width: 100%;
    max-height: calc(100dvh - 24px);
    padding: 20px 14px 20px;
    border-radius: 20px;
  }

  .modal-headline {
    font-size: 1.12rem;
    letter-spacing: 0.04em;
  }

  .modal-subline {
    font-size: 0.83rem;
  }

  .score-ball {
    width: 220px;
    height: 220px;
  }

  .score-days {
    font-size: 4.8rem;
  }

  .score-label {
    font-size: 1.9rem;
  }

  .players-row {
    gap: 12px;
    margin-top: 14px;
    flex-wrap: wrap;
  }

  .player-avatar-wrap {
    width: 72px;
    height: 72px;
  }

  .player-name {
    font-size: 0.9rem;
  }

  .pickleball-mark {
    width: 96px;
    height: 96px;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }

  .metric-card {
    padding: 10px;
  }

  .no-streak-state {
    width: 100px;
    height: 100px;
  }
}

@media (max-width: 640px), (max-height: 740px) {
  .overview-page {
    padding: 12px;
  }

  .friends-streak-table {
    min-width: 560px;
  }

  .modal-head {
    margin-bottom: 12px;
    gap: 6px;
  }

  .status-pill {
    font-size: 0.7rem;
    padding: 5px 10px;
  }

  .modal-headline {
    font-size: 0.96rem;
    line-height: 1.25;
  }

  .modal-subline {
    font-size: 0.78rem;
  }

  .score-ball {
    width: min(66vw, 190px);
    height: min(66vw, 190px);
  }

  .score-days {
    font-size: clamp(3rem, 11vw, 4.2rem);
  }

  .score-label {
    font-size: clamp(1.2rem, 5.6vw, 1.6rem);
  }

  .players-row {
    gap: 10px;
    margin-top: 12px;
  }

  .player-avatar-wrap {
    width: 64px;
    height: 64px;
  }

  .pickleball-mark {
    width: 76px;
    height: 76px;
  }

  .modal-note {
    margin-top: 12px;
    font-size: 0.88rem;
    line-height: 1.35;
    padding: 10px 12px;
  }

  .metric-grid {
    margin-top: 12px;
    gap: 8px;
  }

  .metric-card {
    padding: 9px;
  }

  .metric-value {
    font-size: 0.92rem;
  }

  .no-streak-box {
    padding: 14px;
  }

  .no-streak-title {
    font-size: 1rem;
  }

  .no-streak-box p {
    font-size: 0.9rem;
    line-height: 1.4;
  }
}
</style>
