import { create } from "zustand"
import { createJSONStorage, persist } from "zustand/middleware"

interface User {
  id: string
  email: string
  first_name?: string
  last_name?: string
  role: "USER" | "ADMIN"
  is_verified: boolean
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  setAuth: (user: User, access: string, refresh: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

const safeStorage = {
  getItem: (key: string) => {
    if (typeof window === "undefined") return null
    try {
      return window.localStorage.getItem(key)
    } catch {
      return null
    }
  },
  setItem: (key: string, value: string) => {
    if (typeof window === "undefined") return
    try {
      window.localStorage.setItem(key, value)
    } catch {
      // Ignore storage write failures so the app remains usable in restricted browsers.
    }
  },
  removeItem: (key: string) => {
    if (typeof window === "undefined") return
    try {
      window.localStorage.removeItem(key)
    } catch {
      // Ignore storage removal failures during restricted or private browsing sessions.
    }
  },
}

// This client-side auth store keeps the user session in sync with browser
// storage so the app can restore authentication across page refreshes without a
// full login flow. It also centralizes session-clearing logic for logout and 401
// handling in the API wrapper.
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setAuth: (user, access, refresh) => {
        // Store the JWT in localStorage so requests can read it even after a
        // browser reload. The Zustand state is also kept in memory for fast UI
        // reads across components.
        safeStorage.setItem("access_token", access)
        set({ user, accessToken: access, refreshToken: refresh })
      },
      logout: () => {
        // Clearing both persisted and in-memory state prevents stale authenticated
        // user data from staying around after token expiration or explicit sign-out.
        safeStorage.removeItem("access_token")
        set({ user: null, accessToken: null, refreshToken: null })
      },
      updateUser: (updates) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null
        }))
      }
    }),
    {
      name: "docusign-auth-storage",
      storage: createJSONStorage(() => safeStorage),
    }
  )
)
