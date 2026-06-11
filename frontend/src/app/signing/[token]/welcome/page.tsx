"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ShieldCheck, PenTool, ArrowRight, Loader2, Info } from "lucide-react"
import api from "@/lib/api"

export default function SigningWelcomePage() {
  const { token } = useParams()
  const router = useRouter()
  const [session, setSession] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchBasicInfo = async () => {
      try {
        const res = await api.get(`/signing/${token}`)
        setSession(res.data)
      } catch (err: any) {
        setError(err.response?.data?.detail || "Invalid or expired signing link")
      } finally {
        setIsLoading(false)
      }
    }
    fetchBasicInfo()
  }, [token])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="animate-spin text-accent" size={32} />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-stone-50 px-4">
        <Card className="max-w-md w-full text-center p-6 border-border/50">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-rose-100 text-rose-600 mb-4">
            <Info size={32} />
          </div>
          <h1 className="text-xl font-bold text-primary mb-2">Link Unavailable</h1>
          <p className="text-sm text-muted-foreground mb-6">{error}</p>
          <Button variant="outline" onClick={() => router.push("/")} className="w-full">
            Return Home
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-stone-50 px-4">
      <Card className="w-full max-w-lg shadow-xl border-border/50 overflow-hidden">
        <div className="h-2 bg-accent" />
        <CardHeader className="text-center pt-8">
          <div className="flex justify-center mb-4">
            <div className="rounded-xl bg-accent p-3 text-accent-foreground shadow-lg">
              <PenTool size={32} />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-primary">Invitation to Sign</CardTitle>
          <CardDescription className="text-base mt-2">
            You have been invited to sign <strong>{session?.document?.title}</strong>
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6 px-8">
          <div className="grid grid-cols-1 gap-4">
            <FeatureItem
              icon={ShieldCheck}
              title="Secure Session"
              description="This is a secure, encrypted signing session tied to your email."
            />
            <FeatureItem
              icon={PenTool}
              title="Legal Compliance"
              description="Signatures captured are legally binding and recorded in a permanent audit trail."
            />
          </div>

          <div className="p-4 rounded-xl bg-stone-50 border text-xs text-muted-foreground leading-relaxed">
            By clicking "Start Signing", you agree that your electronic signature will have the same legal effect as a handwritten signature.
          </div>
        </CardContent>

        <CardFooter className="p-8 pt-0">
          <Button
            className="w-full h-12 btn-accent text-base font-bold shadow-lg hover:scale-[1.02] transition-transform"
            onClick={() => router.push(`/signing/${token}`)}
          >
            Start Signing
            <ArrowRight size={20} className="ml-2" />
          </Button>
        </CardFooter>
      </Card>
    </div>
  )
}

function FeatureItem({ icon: Icon, title, description }: any) {
  return (
    <div className="flex gap-4">
      <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600 h-fit">
        <Icon size={20} />
      </div>
      <div>
        <p className="text-sm font-bold text-primary">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
    </div>
  )
}
