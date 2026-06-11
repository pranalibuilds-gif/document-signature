import { create } from "zustand"
import { persist } from "zustand/middleware"

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

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setAuth: (user, access, refresh) => {
        localStorage.setItem("access_token", access)
        set({ user, accessToken: access, refreshToken: refresh })
      },
      logout: () => {
        localStorage.removeItem("access_token")
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
    }
  )
)
