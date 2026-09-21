import { ref } from 'vue'
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'

interface User {
  id: number
  email: string
  full_name: string
  role: string
  phone_number?: string | null
  avatar_url?: string | null
  is_active: boolean

  // Bank account fields (for owners)
  bank_account_number?: string | null
  bank_account_name?: string | null
  bank_name?: string | null
  bank_code?: string | null
}

interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

interface GoogleLoginResponse extends LoginResponse {}

interface SignupData {
  email: string
  password: string
  full_name: string
  phone_number?: string
  role: string
}

type AuthRole = 'user' | 'owner' | 'enterprise'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Initialize from localStorage
  const initAuth = () => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      try {
        token.value = storedToken
        user.value = JSON.parse(storedUser)
        console.log('✅ Auth initialized:', user.value)
      } catch (e) {
        console.error('❌ Failed to parse user:', e)
        logout()
      }
    }
  }

  // Signup
  const signup = async (userData: SignupData) => {
    console.log('📝 AUTH STORE - Signup called')
    console.log('   Email:', userData.email)
    console.log('   Full name:', userData.full_name)
    console.log('   Role:', userData.role)

    isLoading.value = true
    error.value = null

    try {
      console.log('📤 Sending POST request to /auth/register')

      const response = await axiosInstance.post<LoginResponse>('/auth/register', userData)

      console.log('📥 Response received:', response.status)

      if (response.data) {
        user.value = response.data.user
        token.value = response.data.access_token

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        console.log('✅ Signup successful!')

        return { success: true, data: response.data }
      }

      return { success: false, error: 'Registration failed' }
    } catch (err: unknown) {
      console.error('❌ Signup error:', err)

      let errorMessage = 'Registration failed. Please try again.'

      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as {
          response?: {
            status?: number
            data?: { detail?: string }
          }
        }

        const detail = error.response?.data?.detail
        const status = error.response?.status

        console.log('   Error status:', status)
        console.log('   Error detail:', detail)

        if (status === 400 && detail?.includes('đã')) {
          errorMessage = 'This email is already registered. Please use another email.'
        } else if (status === 422) {
          errorMessage = 'Invalid data. Please check again.'
        } else if (detail) {
          errorMessage = detail
        }
      }

      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Login
  const login = async (credentials: { email: string; password: string }) => {
    console.log('🔐 AUTH STORE - Login called')
    console.log('   Email:', credentials.email)

    isLoading.value = true
    error.value = null

    try {
      console.log('📤 Sending POST request to /auth/login')

      const response = await axiosInstance.post<LoginResponse>('/auth/login', credentials)

      console.log('📥 Response received:', response.status)

      if (response.data) {
        user.value = response.data.user
        token.value = response.data.access_token

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        console.log('✅ Login successful!')

        return { success: true }
      }

      return { success: false, error: 'Login failed' }
    } catch (err: unknown) {
      console.error('❌ Login error:', err)

      let errorMessage = 'Login failed'

      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as {
          response?: {
            status?: number
            data?: { detail?: string }
          }
        }

        const status = error.response?.status
        const detail = error.response?.data?.detail

        console.log('   Error status:', status)
        console.log('   Error detail:', detail)

        if (status === 401) {
          if (detail) {
            errorMessage = detail
          }
        }
      }

      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Login or register with Google
  const loginWithGoogle = async (credential: string, role?: AuthRole) => {
    console.log('🔐 AUTH STORE - Google login called')

    isLoading.value = true
    error.value = null

    try {
      console.log('📤 Sending POST request to /auth/google')

      const response = await axiosInstance.post<GoogleLoginResponse>('/auth/google', {
        credential,
        role,
      })

      console.log('📥 Response received:', response.status)

      if (response.data) {
        user.value = response.data.user
        token.value = response.data.access_token

        localStorage.setItem('token', token.value)
        localStorage.setItem('user', JSON.stringify(user.value))

        console.log('✅ Google login successful!')

        return { success: true }
      }

      return { success: false, error: 'Google login failed' }
    } catch (err: unknown) {
      console.error('❌ Google login error:', err)

      let errorMessage = 'Google login failed. Please try again.'

      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as {
          response?: {
            status?: number
            data?: { detail?: string }
          }
        }

        const detail = error.response?.data?.detail

        if (detail) {
          errorMessage = detail
        }
      }

      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Update Profile
  const updateProfile = async (
    userId: number,
    profileData: {
      full_name?: string
      phone_number?: string
      email?: string
      password?: string
    },
  ) => {
    console.log('✏️ AUTH STORE - Update profile called')
    console.log('   User ID:', userId)
    console.log('   Profile Data:', profileData)

    isLoading.value = true
    error.value = null

    try {
      console.log('📤 Sending PUT request to /users/' + userId)
      console.log('   Request payload:', JSON.stringify(profileData))

      const response = await axiosInstance.put<User>(`/users/${userId}`, profileData)

      console.log('📥 Response received:', response.status)
      console.log('   Response data:', response.data)

      if (response.data) {
        // Update user in store
        user.value = response.data
        localStorage.setItem('user', JSON.stringify(user.value))

        console.log('✅ Profile update successful!')

        return { success: true, data: response.data }
      }

      return { success: false, error: 'Update failed' }
    } catch (err: unknown) {
      console.error('❌ Update profile error:', err)

      let errorMessage = 'Update failed. Please try again.'

      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as {
          response?: {
            status?: number
            data?: { detail?: string | Array<{ msg: string; type: string }> }
          }
        }

        const detail = error.response?.data?.detail
        const status = error.response?.status

        console.log('   Error status:', status)
        console.log('   Error detail:', detail)
        console.log('   Full error response:', error.response?.data)

        if (status === 404) {
          errorMessage = 'User not found.'
        } else if (status === 400) {
          if (typeof detail === 'string' && detail.includes('Email')) {
            errorMessage = 'Email is already in use.'
          } else if (typeof detail === 'string') {
            errorMessage = detail
          } else if (Array.isArray(detail)) {
            errorMessage = detail.map((d) => d.msg).join(', ')
          }
        } else if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((d) => d.msg).join(', ')
        }
      }

      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Logout
  const logout = () => {
    console.log('🚪 Logout')
    const google = (
      window as Window & {
        google?: { accounts?: { id?: { disableAutoSelect?: () => void } } }
      }
    ).google
    google?.accounts?.id?.disableAutoSelect?.()
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Initialize on store creation
  initAuth()

  return {
    user,
    token,
    isLoading,
    error,
    signup,
    login,
    loginWithGoogle,
    logout,
    updateProfile,
    initAuth,
  }
})
