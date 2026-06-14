"use client"

import { useState, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { PenTool, Loader2, CheckCircle2 } from "lucide-react"
import api from "@/lib/api"

function ResetPasswordForm() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get("token")

  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token) {
      setError("Missing reset token")
      return
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      await api.post("/auth/reset-password", { token, new_password: password })
      setIsSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to reset password. The link may be expired.")
    } finally {
      setIsLoading(false)
    }
  }

  if (isSuccess) {
    return (
      <Card className="w-full max-w-md text-center shadow-lg border-border/50">
        <CardHeader>
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-emerald-100 p-3 text-emerald-600">
              <CheckCircle2 size={32} />
            </div>
          </div>
          <CardTitle className="text-2xl">Password Reset</CardTitle>
          <CardDescription>
            Your password has been successfully updated.
          </CardDescription>
        </CardHeader>
        <CardFooter>
          <Button className="w-full btn-accent" asChild>
            <Link href="/login">Sign In with New Password</Link>
          </Button>
        </CardFooter>
      </Card>
    )
  }

  return (
    <div className="w-full max-w-md space-y-8">
      <div className="flex flex-col items-center text-center">
        <div className="rounded-xl bg-accent p-3 text-accent-foreground mb-4">
          <PenTool size={32} />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-primary">Reset Password</h1>
        <p className="text-muted-foreground mt-2">Enter your new password below</p>
      </div>

      <Card className="border-border/50 shadow-lg">
        <form onSubmit={handleSubmit}>
          <CardHeader>
            <CardTitle className="text-xl">Set New Password</CardTitle>
            <CardDescription>
              Ensure your password is at least 8 characters long.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            <div className="space-y-2">
              <Label htmlFor="password">New Password</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={isLoading}
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button type="submit" className="w-full h-11 btn-accent" disabled={isLoading}>
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Update Password
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <Suspense fallback={<Loader2 className="animate-spin text-accent" size={32} />}>
        <ResetPasswordForm />
      </Suspense>
    </div>
  )
}
