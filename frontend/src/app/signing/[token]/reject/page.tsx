"use client"

import { useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { XCircle, Loader2 } from "lucide-react"
import api from "@/lib/api"

export default function SigningRejectionPage() {
  const { token } = useParams()
  const router = useRouter()
  const [reason, setReason] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  const handleReject = async () => {
    if (!reason.trim()) return
    setIsSubmitting(true)
    try {
      await api.post(`/signing/${token}/reject`, { reason })
      setDone(true)
    } catch (err) {
      alert("Failed to reject document")
    } finally {
      setIsSubmitting(false)
    }
  }

  if (done) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-stone-50 px-4">
        <Card className="w-full max-w-md text-center border-border/50">
          <CardHeader>
             <div className="flex justify-center mb-4 text-rose-500">
               <XCircle size={48} />
             </div>
             <CardTitle className="text-2xl font-bold">Document Rejected</CardTitle>
             <CardDescription>
               You have successfully rejected this signing request. The owner has been notified.
             </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button variant="outline" className="w-full" onClick={() => window.close()}>
              Close Window
            </Button>
          </CardFooter>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-stone-50 px-4">
      <Card className="w-full max-w-md border-border/50 shadow-lg">
        <CardHeader>
          <CardTitle className="text-xl">Reject Signing Request</CardTitle>
          <CardDescription>
            Please provide a reason why you are declining to sign this document.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="reason">Rejection Reason</Label>
            <Textarea
              id="reason"
              placeholder="e.g., Error in contract terms, wrong recipient, etc."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="h-32"
            />
          </div>
        </CardContent>
        <CardFooter className="flex gap-3">
          <Button variant="ghost" onClick={() => router.back()} className="flex-1">
            Go Back
          </Button>
          <Button
            variant="destructive"
            onClick={handleReject}
            disabled={!reason.trim() || isSubmitting}
            className="flex-1"
          >
            {isSubmitting ? <Loader2 size={18} className="animate-spin" /> : "Confirm Reject"}
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
