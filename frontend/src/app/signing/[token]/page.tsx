"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { useSigningStore, SigningField } from "@/store/use-signing-store"
import { SigningViewer } from "@/modules/signing/components/signing-viewer"
import { Button } from "@/components/ui/button"
import { Loader2, PenTool, CheckCircle, ShieldCheck, Info, ChevronDown } from "lucide-react"
import api from "@/lib/api"
import { cn } from "@/lib/utils"

export default function SigningPage() {
  const { token } = useParams()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { document, signer, fields, values, setSession, isComplete } = useSigningStore()

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await api.get(`/signing/${token}`)
        const mappedFields: SigningField[] = res.data.fields.map((f: any) => ({
          id: f.id,
          type: f.field_type,
          pageNumber: f.page_number,
          x: f.x_coordinate,
          y: f.y_coordinate,
          width: f.width,
          height: f.height,
          required: f.required,
          value: f.pre_filled_value
        }))
        setSession(res.data.document, res.data.signer, mappedFields)
      } catch (err: any) {
        setError(err.response?.data?.detail || "Invalid or expired signing link")
      } finally {
        setIsLoading(false)
      }
    }
    fetchSession()
  }, [token])

  const handleSubmit = async () => {
    if (!isComplete()) return
    setIsSubmitting(true)

    try {
      const submission = {
        values: Object.entries(values).map(([field_id, value]) => ({
          field_id,
          value
        }))
      }
      await api.post(`/signing/${token}/submit`, submission)
      router.push(`/signing/${token}/success`)
    } catch (err) {
      alert("Failed to submit signature")
    } finally {
      setIsSubmitting(false)
    }
  }

  const scrollToNextField = () => {
    const nextField = fields.find(f => f.required && !values[f.id])
    if (nextField) {
      // Find the field element. We use IDs to find them in the DOM.
      const element = document.getElementById(`field-${nextField.id}`)
      if (element) {
        element.scrollIntoView({ behavior: "smooth", block: "center" })
        // Pulsate it?
      }
    }
  }

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
        <div className="max-w-md w-full text-center space-y-6">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-rose-100 text-rose-600 mb-2">
            <Info size={32} />
          </div>
          <h1 className="text-2xl font-bold text-primary">Access Denied</h1>
          <p className="text-muted-foreground">{error}</p>
          <Button variant="outline" onClick={() => router.push("/")} className="w-full">
            Return Home
          </Button>
        </div>
      </div>
    )
  }

  const completedCount = fields.filter(f => f.required && !!values[f.id]).length
  const requiredCount = fields.filter(f => f.required).length
  const progress = (completedCount / requiredCount) * 100

  return (
    <div className="flex flex-col h-screen bg-stone-100/50 overflow-hidden">
      {/* Signing Header */}
      <header className="flex h-16 items-center justify-between border-b bg-white px-4 md:px-6 shrink-0 shadow-sm z-30">
        <div className="flex items-center gap-2 md:gap-3">
          <div className="rounded-lg bg-accent p-1.5 text-accent-foreground flex-shrink-0">
            <PenTool size={18} className="md:w-5 md:h-5" />
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-xs md:text-sm font-semibold text-primary leading-none truncate">
              {document?.title}
            </span>
            <span className="text-[9px] md:text-[10px] text-muted-foreground mt-0.5 uppercase tracking-wider font-bold truncate">
              Secure Session
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-6">
          <div className="hidden sm:flex flex-col items-end">
            <div className="flex items-center gap-3">
              <div className="w-20 md:w-32 h-1.5 bg-stone-100 rounded-full overflow-hidden border">
                <div
                  className="h-full bg-accent transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <span className="text-[10px] md:text-xs font-bold text-primary">
                {completedCount}/{requiredCount}
              </span>
            </div>
          </div>

          <div className="h-8 w-[1px] bg-border hidden sm:block" />

          <Button
            size="sm"
            className={cn(
              "px-4 md:px-8 font-bold shadow-md transition-all h-9 md:h-10",
              isComplete() ? "btn-accent scale-105" : "bg-stone-200 text-stone-400 pointer-events-none"
            )}
            onClick={handleSubmit}
            disabled={!isComplete() || isSubmitting}
          >
            {isSubmitting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <>
                <CheckCircle size={16} className="mr-1 md:mr-2" />
                <span className="text-xs md:text-sm">Finish</span>
              </>
            )}
          </Button>
        </div>
      </header>

      {/* Mobile Progress Bar (Visible only on mobile) */}
      <div className="sm:hidden w-full h-1 bg-stone-200 shrink-0">
        <div
          className="h-full bg-accent transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-auto flex justify-center pb-16">
        {document && (
          <SigningViewer fileUrl={`/api/v1/signing/${token}/file`} />
        )}

        {/* Floating "Next Field" Button */}
        {!isComplete() && fields.some(f => f.required) && (
          <button
            onClick={scrollToNextField}
            className="fixed bottom-20 right-6 z-40 bg-accent text-accent-foreground rounded-full px-4 py-3 shadow-2xl flex items-center gap-2 font-bold animate-bounce hover:scale-105 transition-transform"
          >
            <span>Next Required Field</span>
            <ChevronDown size={18} />
          </button>
        )}
      </main>

      {/* Footer Info */}
      <footer className="fixed bottom-0 w-full h-12 bg-white/80 backdrop-blur-sm border-t flex items-center justify-center gap-4 px-6 z-20">
         <div className="flex items-center gap-1.5 text-emerald-600">
            <ShieldCheck size={16} />
            <span className="text-[10px] font-bold uppercase tracking-widest">End-to-End Secure</span>
         </div>
         <div className="h-3 w-[1px] bg-stone-300" />
         <span className="text-[10px] text-muted-foreground">
           By signing, you agree to the electronic disclosure terms.
         </span>
      </footer>
    </div>
  )
}
