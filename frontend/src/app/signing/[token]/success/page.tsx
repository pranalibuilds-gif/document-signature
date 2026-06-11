"use client"

import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CheckCircle2, FileDown, PartyPopper } from "lucide-react"

export default function SigningSuccessPage() {
  const router = useRouter()

  return (
    <div className="flex min-h-screen items-center justify-center bg-stone-50 px-4">
      <Card className="w-full max-w-md text-center shadow-xl border-border/50">
        <CardHeader>
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-emerald-100 p-4 text-emerald-600 animate-bounce">
              <CheckCircle2 size={48} />
            </div>
          </div>
          <CardTitle className="text-3xl font-bold text-primary flex items-center justify-center gap-2">
            Completed! <PartyPopper className="text-accent" />
          </CardTitle>
          <CardDescription className="text-lg mt-2">
            You've successfully signed the document.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            The document owner has been notified. Once all signers have completed the workflow, you will receive a copy of the finalized PDF via email.
          </p>
        </CardContent>
        <CardFooter className="flex flex-col gap-3">
          <Button variant="outline" className="w-full" onClick={() => window.close()}>
            You can close this window
          </Button>
          <Button variant="ghost" className="w-full text-xs" onClick={() => router.push("/")}>
            Learn more about DocuSign Mini
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}
