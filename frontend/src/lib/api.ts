import axios from "axios"

const api = axios.create({
  baseURL: "/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
})

// In production, we'll need to handle token refreshes and auth headers
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Global Error Interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Session expired or invalid
      localStorage.removeItem("access_token")
      if (typeof window !== "undefined") {
        window.location.href = "/login?expired=true"
      }
    }
    return Promise.reject(error)
  }
)

export default api
