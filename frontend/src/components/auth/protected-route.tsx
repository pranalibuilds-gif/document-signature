"use client"

import { useEffect } from "react"
import { useRouter, usePathname } from "next/navigation"
import { useAuthStore } from "@/store/use-auth-store"
import { Loader2 } from "lucide-react"

interface ProtectedRouteProps {
  children: React.ReactNode
  requiredRole?: "USER" | "ADMIN"
}

/**
 * ProtectedRoute Component
 * Enforces authentication and optional role-based access control (RBAC) on the frontend.
 * Works in tandem with backend RBAC to ensure a secure user experience.
 */
export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { user, accessToken } = useAuthStore()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // 1. Check if authenticated
    if (!accessToken || !user) {
      // Store the intended path to redirect back after login
      const returnUrl = encodeURIComponent(pathname)
      router.push(`/login?returnUrl=${returnUrl}`)
      return
    }

    // 2. Check Role permissions
    if (requiredRole && user.role !== requiredRole) {
      // User is trying to access a portal they don't belong to
      // Redirect them to their appropriate dashboard instead of just showing blank
      if (user.role === "ADMIN") {
        router.push("/admin")
      } else {
        router.push("/dashboard")
      }
    }
  }, [accessToken, user, requiredRole, router, pathname])

  // Prevent UI flicker by returning a consistent loading state while checking auth
  if (!accessToken || !user || (requiredRole && user.role !== requiredRole)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-stone-50">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="animate-spin text-accent" size={40} />
          <p className="text-sm font-medium text-muted-foreground animate-pulse">
            Verifying identity...
          </p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
