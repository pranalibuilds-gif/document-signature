"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { PenTool, Loader2 } from "lucide-react"
import api from "@/lib/api"
import { useAuthStore } from "@/store/use-auth-store"

import { useSearchParams } from "next/navigation"

/**
 * LoginPage Component
 * Handles user authentication by exchanging credentials for JWT tokens.
 * On success, it fetches the user profile and persists the session in Zustand store.
 */
export default function LoginPage() {
  const searchParams = useSearchParams()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  // Display a message if redirected from an expired session
  const [error, setError] = useState<string | null>(
    searchParams.get("expired") ? "Your session has expired. Please sign in again." : null
  )
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()
  const setAuth = useAuthStore((state) => state.setAuth)
  const [loginRole, setLoginRole] = useState<"USER" | "ADMIN">("USER")

  /**
   * Form Submission Handler
   * Orchestrates the 2-step login process:
   * 1. Exchange credentials for Access & Refresh tokens.
   * 2. Use Access token to fetch the current user's profile metadata.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)

    try {
      // Step 1: Authentication
      const response = await api.post("/auth/login", { email, password })
      const { access_token, refresh_token } = response.data

      // Step 2: Fetch Profile
      const userResponse = await api.get("/users/me", {
        headers: { Authorization: `Bearer ${access_token}` }
      })

      const userData = userResponse.data

      // Check if user is logging into the correct portal
      if (loginRole === "ADMIN" && userData.role !== "ADMIN") {
        throw new Error("This account does not have administrator privileges.")
      }

      // Update global state and navigate
      setAuth(userData, access_token, refresh_token)
      router.push(userData.role === "ADMIN" ? "/admin" : "/dashboard")
    } catch (err: any) {
      const message = err.message || err.response?.data?.detail
      if (Array.isArray(message)) {
        setError(message[0]?.msg || "Invalid data provided.")
      } else if (typeof message === "string") {
        setError(message)
      } else {
        setError("Failed to sign in. Please check your credentials.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="flex flex-col items-center text-center">
          <div className="rounded-xl bg-accent p-3 text-accent-foreground mb-4">
            <PenTool size={32} />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">
            {loginRole === "ADMIN" ? "Admin Console" : "Welcome back"}
          </h1>
          <p className="text-muted-foreground mt-2">
            {loginRole === "ADMIN"
              ? "Access the system management dashboard"
              : "Enter your credentials to access your account"}
          </p>
        </div>

        <Card className="border-border/50 shadow-lg overflow-hidden">
          <div className="flex border-b">
            <button
              onClick={() => { setLoginRole("USER"); setError(null); }}
              className={cn(
                "flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors",
                loginRole === "USER" ? "bg-accent/5 text-accent border-b-2 border-accent" : "text-muted-foreground hover:bg-stone-50"
              )}
            >
              Signer Portal
            </button>
            <button
              onClick={() => { setLoginRole("ADMIN"); setError(null); }}
              className={cn(
                "flex-1 py-3 text-xs font-bold uppercase tracking-wider transition-colors",
                loginRole === "ADMIN" ? "bg-primary/5 text-primary border-b-2 border-primary" : "text-muted-foreground hover:bg-stone-50"
              )}
            >
              Admin Portal
            </button>
          </div>
          <form onSubmit={handleSubmit}>
            <CardHeader className="space-y-1">
              <CardTitle className="text-xl">Sign In</CardTitle>
              <CardDescription>
                Login to your {loginRole === "ADMIN" ? "administrator" : "user"} account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  <Link
                    href="/forgot-password"
                    className="text-xs text-accent hover:underline font-medium"
                  >
                    Forgot password?
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button type="submit" className="w-full h-11" disabled={isLoading}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Sign In
              </Button>
              <div className="text-center text-sm text-muted-foreground">
                Don't have an account?{" "}
                <Link href="/register" className="text-accent hover:underline font-medium">
                  Create an account
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  )
}
