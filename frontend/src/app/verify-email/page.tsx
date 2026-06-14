"use client"

import { useEffect, useState, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Loader2, CheckCircle2, XCircle, Mail } from "lucide-react"
import api from "@/lib/api"

function VerifyEmailForm() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const token = searchParams.get("token")

  const [status, setStatus] = useState<"loading" | "success" | "error">("loading")
  const [errorMessage, setError] = useState("")

  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setStatus("error")
        setError("Missing verification token")
        return
      }

      try {
        await api.post("/auth/verify-email", { token })
        setStatus("success")
      } catch (err: any) {
        setStatus("error")
        const detail = err.response?.data?.detail
        if (Array.isArray(detail)) {
          setError(detail[0]?.msg || "Invalid or expired token")
        } else {
          setError(detail || "Invalid or expired token")
        }
      }
    }

    verifyToken()
  }, [token])

  return (
    <Card className="w-full max-w-md text-center shadow-lg border-border/50">
      <CardHeader>
        <div className="flex justify-center mb-4">
          <div className={`rounded-full p-3 ${
            status === "loading" ? "bg-muted text-muted-foreground" :
            status === "success" ? "bg-emerald-100 text-emerald-600" :
            "bg-destructive/10 text-destructive"
          }`}>
            {status === "loading" && <Mail size={32} />}
            {status === "success" && <CheckCircle2 size={32} />}
            {status === "error" && <XCircle size={32} />}
          </div>
        </div>
        <CardTitle className="text-2xl">
          {status === "loading" && "Verifying Email..."}
          {status === "success" && "Verification Successful!"}
          {status === "error" && "Verification Failed"}
        </CardTitle>
        <CardDescription>
          {status === "loading" && "Please wait while we confirm your email address"}
          {status === "success" && "Your email has been verified. You can now use all features."}
          {status === "error" && errorMessage}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {status === "success" && (
          <Button onClick={() => router.push("/login")} className="w-full">
            Go to Sign In
          </Button>
        )}
        {status === "error" && (
          <div className="space-y-4">
            <Button onClick={() => router.push("/register")} variant="outline" className="w-full">
              Back to Registration
            </Button>
            <Button onClick={() => router.refresh()} variant="ghost" className="w-full text-xs">
              Try again
            </Button>
          </div>
        )}
        {status === "loading" && (
          <div className="flex justify-center py-4">
            <Loader2 size={32} className="animate-spin text-muted-foreground" />
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function VerifyEmailPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <Suspense fallback={<Loader2 className="animate-spin text-accent" size={32} />}>
        <VerifyEmailForm />
      </Suspense>
    </div>
  )
}
