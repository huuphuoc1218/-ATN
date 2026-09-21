import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('@/utils/axios', () => ({
  default: {
    post: vi.fn(),
    put: vi.fn(),
  },
}))

import axiosInstance from '@/utils/axios'
import { useAuthStore } from '@/stores/auth'

const mockedAxios = axiosInstance as unknown as {
  post: ReturnType<typeof vi.fn>
  put: ReturnType<typeof vi.fn>
}

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('login stores token and user on success', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      status: 200,
      data: {
        access_token: 'token-123',
        token_type: 'bearer',
        user: {
          id: 1,
          email: 'user@example.com',
          full_name: 'User Test',
          role: 'user',
          is_active: true,
        },
      },
    })

    const store = useAuthStore()
    const result = await store.login({ email: 'user@example.com', password: '123456' })

    expect(result.success).toBe(true)
    expect(store.token).toBe('token-123')
    expect(store.user?.email).toBe('user@example.com')
    expect(localStorage.getItem('token')).toBe('token-123')
    expect(localStorage.getItem('user')).toContain('user@example.com')
  })

  it('login returns backend error detail for 401', async () => {
    mockedAxios.post.mockRejectedValueOnce({
      response: {
        status: 401,
        data: {
          detail: 'Mật khẩu không chính xác',
        },
      },
    })

    const store = useAuthStore()
    const result = await store.login({ email: 'user@example.com', password: 'wrong' })

    expect(result.success).toBe(false)
    expect(result.error).toBe('Mật khẩu không chính xác')
  })

  it('signup maps duplicate email error message', async () => {
    mockedAxios.post.mockRejectedValueOnce({
      response: {
        status: 400,
        data: {
          detail: 'Email đã được đăng ký',
        },
      },
    })

    const store = useAuthStore()
    const result = await store.signup({
      email: 'dup@example.com',
      password: '123456',
      full_name: 'Dup User',
      role: 'user',
    })

    expect(result.success).toBe(false)
    expect(result.error).toBe('This email is already registered. Please use another email.')
  })

  it('updateProfile updates current user and localStorage', async () => {
    const store = useAuthStore()
    store.user = {
      id: 1,
      email: 'old@example.com',
      full_name: 'Old Name',
      role: 'user',
      is_active: true,
    }

    mockedAxios.put.mockResolvedValueOnce({
      status: 200,
      data: {
        id: 1,
        email: 'new@example.com',
        full_name: 'New Name',
        role: 'user',
        is_active: true,
      },
    })

    const result = await store.updateProfile(1, {
      full_name: 'New Name',
      email: 'new@example.com',
    })

    expect(result.success).toBe(true)
    expect(store.user?.full_name).toBe('New Name')
    expect(localStorage.getItem('user')).toContain('new@example.com')
  })

  it('logout clears auth state and localStorage', () => {
    const store = useAuthStore()
    store.token = 'token-123'
    store.user = {
      id: 1,
      email: 'user@example.com',
      full_name: 'User Test',
      role: 'user',
      is_active: true,
    }
    localStorage.setItem('token', 'token-123')
    localStorage.setItem('user', JSON.stringify(store.user))

    store.logout()

    expect(store.token).toBe('')
    expect(store.user).toBeNull()
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })
})
