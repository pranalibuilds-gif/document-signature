"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileQuestion, Home, ArrowLeft } from "lucide-react"

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-stone-50 px-4 text-center">
      <div className="rounded-full bg-stone-100 p-6 mb-6">
        <FileQuestion size={64} className="text-stone-300" />
      </div>
      <h1 className="text-4xl font-bold tracking-tight text-primary sm:text-6xl">404</h1>
      <h2 className="mt-4 text-2xl font-semibold text-primary">Page not found</h2>
      <p className="mt-4 text-stone-500 max-w-md">
        Sorry, we couldn't find the page you're looking for. It might have been moved or deleted.
      </p>
      <div className="mt-10 flex flex-col sm:flex-row gap-4">
        <Button variant="outline" onClick={() => window.history.back()}>
          <ArrowLeft size={18} className="mr-2" />
          Go Back
        </Button>
        <Button className="btn-accent" asChild>
          <Link href="/dashboard">
            <Home size={18} className="mr-2" />
            Back to Dashboard
          </Link>
        </Button>
      </div>
    </div>
  )
}
