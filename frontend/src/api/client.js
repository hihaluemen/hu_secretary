import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const timeoutMs = Number(import.meta.env.VITE_API_TIMEOUT_MS || 120000)

const apiClient = axios.create({
  baseURL,
  timeout: Number.isFinite(timeoutMs) ? timeoutMs : 120000,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const responseData = error?.response?.data
    const message =
      responseData?.message ||
      responseData?.detail ||
      error.message ||
      '请求失败'
    return Promise.reject(new Error(message))
  },
)

export default apiClient
