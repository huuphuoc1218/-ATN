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

const LOGIN_CASES = [
  ...Array.from({ length: 20 }, (_, i) => ({
    name: `401 with detail message ${i + 1}`,
    error: { response: { status: 401, data: { detail: `Invalid credentials ${i + 1}` } } },
    expected: `Invalid credentials ${i + 1}`,
  })),
  ...Array.from({ length: 10 }, (_, i) => ({
    name: `401 without detail ${i + 1}`,
    error: { response: { status: 401, data: {} } },
    expected: 'Login failed',
  })),
  ...Array.from({ length: 10 }, (_, i) => ({
    name: `non-401 keeps default message ${i + 1}`,
    error: { response: { status: 500, data: { detail: `Server issue ${i + 1}` } } },
    expected: 'Login failed',
  })),
]

const SIGNUP_CASES = [
  ...Array.from({ length: 10 }, (_, i) => ({
    name: `duplicate email mapping ${i + 1}`,
    error: { response: { status: 400, data: { detail: `Email đã tồn tại ${i + 1}` } } },
    expected: 'This email is already registered. Please use another email.',
  })),
  ...Array.from({ length: 10 }, (_, i) => ({
    name: `422 validation message ${i + 1}`,
    error: { response: { status: 422, data: { detail: `Validation ${i + 1}` } } },
    expected: 'Invalid data. Please check again.',
  })),
  ...Array.from({ length: 5 }, (_, i) => ({
    name: `custom detail fallback ${i + 1}`,
    error: { response: { status: 500, data: { detail: `Custom detail ${i + 1}` } } },
    expected: `Custom detail ${i + 1}`,
  })),
  ...Array.from({ length: 5 }, (_, i) => ({
    name: `network/default message ${i + 1}`,
    error: { message: `Network error ${i + 1}` },
    expected: 'Registration failed. Please try again.',
  })),
]

const UPDATE_CASES = [
  ...Array.from({ length: 8 }, (_, i) => ({
    name: `404 user not found ${i + 1}`,
    error: { response: { status: 404, data: { detail: `Not found ${i + 1}` } } },
    expected: 'User not found.',
  })),
  ...Array.from({ length: 4 }, (_, i) => ({
    name: `400 email in use mapping ${i + 1}`,
    error: { response: { status: 400, data: { detail: `Email conflict ${i + 1}` } } },
    expected: 'Email is already in use.',
  })),
  ...Array.from({ length: 4 }, (_, i) => ({
    name: `400 detail passthrough ${i + 1}`,
    error: { response: { status: 400, data: { detail: `Invalid update ${i + 1}` } } },
    expected: `Invalid update ${i + 1}`,
  })),
  ...Array.from({ length: 4 }, (_, i) => ({
    name: `400 detail array join ${i + 1}`,
    error: {
      response: {
        status: 400,
        data: {
          detail: [
            { msg: `msg-${i + 1}-A`, type: 'value_error' },
            { msg: `msg-${i + 1}-B`, type: 'value_error' },
          ],
        },
      },
    },
    expected: `msg-${i + 1}-A, msg-${i + 1}-B`,
  })),
  ...Array.from({ length: 4 }, (_, i) => ({
    name: `500 string detail fallback ${i + 1}`,
    error: { response: { status: 500, data: { detail: `Server explode ${i + 1}` } } },
    expected: `Server explode ${i + 1}`,
  })),
]

describe('auth store mass cases', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it.each(LOGIN_CASES)('login error mapping: $name', async ({ error, expected }) => {
    mockedAxios.post.mockRejectedValueOnce(error)
    const store = useAuthStore()

    const result = await store.login({ email: 'u@example.com', password: 'wrong' })

    expect(result.success).toBe(false)
    expect(result.error).toBe(expected)
  })

  it.each(SIGNUP_CASES)('signup error mapping: $name', async ({ error, expected }) => {
    mockedAxios.post.mockRejectedValueOnce(error)
    const store = useAuthStore()

    const result = await store.signup({
      email: 'u@example.com',
      password: '123456',
      full_name: 'User',
      role: 'user',
    })

    expect(result.success).toBe(false)
    expect(result.error).toBe(expected)
  })

  it.each(UPDATE_CASES)('updateProfile error mapping: $name', async ({ error, expected }) => {
    mockedAxios.put.mockRejectedValueOnce(error)
    const store = useAuthStore()

    const result = await store.updateProfile(1, { full_name: 'Next' })

    expect(result.success).toBe(false)
    expect(result.error).toBe(expected)
  })
})
