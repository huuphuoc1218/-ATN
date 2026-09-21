import axios from 'axios'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const axiosInstance = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    console.log('📤 Axios Request:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  },
)

// Response interceptor
axiosInstance.interceptors.response.use(
  (response) => {
    console.log('📥 Axios Response:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('❌ Axios Response Error:', error)

    // ✅ LOG CHI TIẾT ERROR
    if (error.response) {
      console.error('   Status:', error.response.status)
      console.error('   Data:', JSON.stringify(error.response.data))
      console.error('   Headers:', error.response.headers)
    } else if (error.request) {
      console.error('   No response received:', error.request)
    } else {
      console.error('   Error:', error.message)
    }
    return Promise.reject(error)
  },
)

export default axiosInstance
