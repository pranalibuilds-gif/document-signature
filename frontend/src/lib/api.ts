/**
 * Central Axios instance for API communication.
 * Handles base URL configuration, request authentication, and global error handling.
 */
import axios from "axios"

const api = axios.create({
  baseURL: "/api/v1", // Proxied by next.config.mjs to the backend
  headers: {
    "Content-Type": "application/json",
  },
})

/**
 * Request Interceptor
 * Automatically attaches the JWT access token to every outgoing request
 * if the user is authenticated.
 */
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Response Interceptor (Global Error Handling)
 * Detects 401 Unauthorized errors (session expired) and redirects
 * the user back to the login page.
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid credentials and redirect
      localStorage.removeItem("access_token")
      if (typeof window !== "undefined") {
        window.location.href = "/login?expired=true"
      }
    }
    return Promise.reject(error)
  }
)

export default api
