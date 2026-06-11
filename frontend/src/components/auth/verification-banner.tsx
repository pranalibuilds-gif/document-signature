"use client"

import { useState } from "react"
import { AlertCircle, Loader2, MailCheck } from "lucide-react"
import { useAuthStore } from "@/store/use-auth-store"
import { Button } from "@/components/ui/button"
import api from "@/lib/api"
import { cn } from "@/lib/utils"

export function VerificationBanner() {
  const { user, updateUser } = useAuthStore()
  const [isResending, setIsResending] = useState(false)
  const [resent, setResent] = useState(false)

  if (!user || user.is_verified) return null

  const handleResend = async () => {
    setIsResending(true)
    try {
      await api.post("/auth/resend-verification")
      setResent(true)
      setTimeout(() => setResent(false), 5000)
    } catch (err) {
      alert("Failed to resend verification email.")
    } finally {
      setIsResending(false)
    }
  }

  return (
    <div className="bg-amber-50 border-b border-amber-200 px-4 py-3 sm:px-6 lg:px-8">
      <div className="flex items-center justify-between flex-wrap gap-y-2">
        <div className="flex items-center min-w-0">
          <span className="flex p-2 rounded-lg bg-amber-100 text-amber-600 mr-3">
            <AlertCircle size={20} />
          </span>
          <p className="text-sm font-medium text-amber-800 truncate">
            <span className="hidden md:inline">Please verify your email address to enable all features, including document activation.</span>
            <span className="md:hidden">Email verification required.</span>
          </p>
        </div>
        <div className="flex items-center gap-3">
          {resent ? (
            <div className="flex items-center gap-1.5 text-xs font-bold text-amber-700 bg-amber-100/50 px-3 py-1.5 rounded-full border border-amber-200">
               <MailCheck size={14} />
               Email Sent!
            </div>
          ) : (
            <Button
              size="sm"
              variant="outline"
              className="h-8 border-amber-300 text-amber-800 hover:bg-amber-100"
              onClick={handleResend}
              disabled={isResending}
            >
              {isResending ? <Loader2 size={14} className="animate-spin mr-2" /> : null}
              Resend Link
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
