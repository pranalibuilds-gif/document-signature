/**
 * Central Axios instance for API communication.
 * Handles base URL configuration, request authentication, and global error handling.
 *
 * This wrapper gives the frontend one place to manage auth headers and session
 * expiry behaviour instead of repeating boilerplate across every page or module.
 */
import axios from "axios"
import { useAuthStore } from "@/store/use-auth-store"

const getAccessToken = () => {
  if (typeof window === "undefined") {
    return null
  }

  try {
    return window.localStorage.getItem("access_token")
  } catch {
    return null
  }
}

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
 *
 * The token is read from localStorage because it is persisted across page reloads
 * and is required even before the Zustand store hydrates on the client.
 */
api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/**
 * Response Interceptor (Global Error Handling)
 * Detects 401 Unauthorized errors (session expired) and redirects
 * the user back to the login page.
 *
 * Centralizing this here prevents each component from needing to duplicate
 * logout + redirect logic when an expired token is returned by the API.
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 1. Clear invalid credentials from persistence and memory
      useAuthStore.getState().logout()

      // 2. Redirect to login with expiration context
      if (typeof window !== "undefined") {
        window.location.href = "/login?expired=true"
      }
    }
    return Promise.reject(error)
  }
)

export default api
