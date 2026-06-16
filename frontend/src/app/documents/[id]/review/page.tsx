"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { FileText, Users, MapPin, Send, ArrowLeft, Loader2, CheckCircle2 } from "lucide-react"
import api from "@/lib/api"

export default function DocumentReviewPage() {
  const { id } = useParams()
  const router = useRouter()
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isActivating, setIsActivating] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docRes, signersRes, fieldsRes] = await Promise.all([
          api.get(`/documents/${id}`),
          api.get(`/documents/${id}/signers`),
          api.get(`/documents/${id}/fields`)
        ])
        setData({
          doc: docRes.data,
          signers: signersRes.data,
          fields: fieldsRes.data
        })
      } catch (err) {
        console.error("Failed to fetch data", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleActivate = async () => {
    setIsActivating(true)
    try {
      await api.post(`/documents/${id}/activate`)
      router.push("/documents?activated=true")
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to activate document")
    } finally {
      setIsActivating(false)
    }
  }

  if (isLoading) {
     return <div className="flex h-screen items-center justify-center"><Loader2 className="animate-spin text-accent" /></div>
  }

  return (
    <ProtectedRoute requiredRole="USER">
      <DashboardLayout>
        <PageContainer size="tight">
          <SectionHeader
            title="Review & Send"
            description="Final check before sending the document for signatures."
          />

          <div className="space-y-6">
            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">Document Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4 p-4 rounded-xl border bg-stone-50/50">
                  <div className="p-3 rounded-lg bg-white border text-stone-400">
                    <FileText size={24} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-primary">{data.doc.title}</p>
                    <p className="text-xs text-muted-foreground uppercase font-bold tracking-tight">Standard PDF Document</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl border border-stone-100 bg-white shadow-sm">
                    <div className="flex items-center gap-2 mb-2">
                       <Users size={16} className="text-accent" />
                       <span className="text-xs font-bold text-muted-foreground uppercase">Signers</span>
                    </div>
                    <p className="text-2xl font-bold text-primary">{data.signers.length}</p>
                  </div>
                  <div className="p-4 rounded-xl border border-stone-100 bg-white shadow-sm">
                    <div className="flex items-center gap-2 mb-2">
                       <MapPin size={16} className="text-accent" />
                       <span className="text-xs font-bold text-muted-foreground uppercase">Fields Placed</span>
                    </div>
                    <p className="text-2xl font-bold text-primary">{data.fields.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-border/50 shadow-sm">
              <CardHeader>
                <CardTitle className="text-lg">Signing Workflow</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {data.signers.map((s: any, idx: number) => (
                    <div key={s.id} className="flex items-center gap-4">
                      <div className="w-8 h-8 rounded-full bg-stone-100 border flex items-center justify-center text-xs font-bold text-stone-500">
                        {idx + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-primary">{s.email}</p>
                        <p className="text-[10px] text-muted-foreground">Will receive a unique signing link</p>
                      </div>
                      <Badge variant="secondary" className="bg-stone-50 text-stone-500">Pending</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between border-t bg-stone-50/20 py-4 mt-6">
                <Button variant="ghost" onClick={() => router.push(`/documents/${id}/editor`)}>
                  <ArrowLeft size={16} className="mr-2" />
                  Edit Fields
                </Button>
                <Button
                  className="btn-accent px-8"
                  onClick={handleActivate}
                  disabled={data.fields.length === 0 || isActivating}
                >
                  {isActivating ? <Loader2 size={18} className="animate-spin" /> : (
                    <>
                      <Send size={18} className="mr-2" />
                      Activate & Send
                    </>
                  )}
                </Button>
              </CardFooter>
            </Card>

            {data.fields.length === 0 && (
               <div className="p-4 rounded-xl border border-amber-200 bg-amber-50 flex gap-3">
                  <CheckCircle2 size={20} className="text-amber-500 shrink-0" />
                  <p className="text-xs text-amber-800 leading-relaxed">
                    You haven't placed any signature fields yet. You must add at least one field in the <strong>Editor</strong> before you can activate this document.
                  </p>
               </div>
            )}
          </div>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
