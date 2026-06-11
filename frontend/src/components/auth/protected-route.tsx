"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/store/use-auth-store"

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, accessToken } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (!accessToken || !user) {
      router.push("/login")
    }
  }, [accessToken, user, router])

  if (!accessToken || !user) {
    return null // or a loading spinner
  }

  return <>{children}</>
}
