"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { AlertTriangle, RefreshCcw, Home } from "lucide-react"
import Link from "next/link"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-stone-50 px-4 text-center">
      <div className="rounded-full bg-rose-50 p-6 mb-6">
        <AlertTriangle size={64} className="text-rose-500" />
      </div>
      <h1 className="text-2xl font-bold tracking-tight text-primary sm:text-3xl">Something went wrong</h1>
      <p className="mt-4 text-stone-500 max-w-md">
        An unexpected error occurred while processing your request. Our team has been notified.
      </p>
      <div className="mt-10 flex flex-col sm:flex-row gap-4">
        <Button variant="outline" onClick={() => reset()}>
          <RefreshCcw size={18} className="mr-2" />
          Try Again
        </Button>
        <Button className="btn-accent" asChild>
          <Link href="/dashboard">
            <Home size={18} className="mr-2" />
            Return to Dashboard
          </Link>
        </Button>
      </div>
    </div>
  )
}
