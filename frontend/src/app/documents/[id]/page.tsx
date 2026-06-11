"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import Link from "next/link"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { DocumentStatusBadge } from "@/components/documents/document-status-badge"
import {
  FileText,
  Users,
  History,
  Download,
  ChevronLeft,
  Mail,
  Clock,
  CheckCircle2,
  XCircle,
  Loader2
} from "lucide-react"
import api from "@/lib/api"
import { cn } from "@/lib/utils"

export default function DocumentDetailPage() {
  const { id } = useParams()
  const router = useRouter()
  const [doc, setDoc] = useState<any>(null)
  const [signers, setSigners] = useState<any[]>([])
  const [auditLogs, setAuditLogs] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const [docRes, signersRes, auditRes] = await Promise.all([
          api.get(`/documents/${id}`),
          api.get(`/documents/${id}/signers`),
          api.get(`/admin/audit?document_id=${id}`) // Reusing admin audit search for detail view
        ])
        setDoc(docRes.data)
        setSigners(signersRes.data)
        setAuditLogs(auditRes.data)
      } catch (err) {
        console.error("Failed to fetch details", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchDetails()
  }, [id])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="animate-spin text-accent" size={32} />
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <PageContainer>
          <div className="mb-6">
            <Button variant="ghost" size="sm" onClick={() => router.push("/documents")}>
              <ChevronLeft size={16} className="mr-1" />
              Back to Documents
            </Button>
          </div>

          <SectionHeader
            title={doc.title}
            description={`Created on ${new Date(doc.created_at).toLocaleDateString()}`}
            actions={
              <div className="flex items-center gap-3">
                {doc.status === 'COMPLETED' && (
                  <Button className="btn-accent" asChild>
                    <a href={`/api/v1/documents/${id}/final-file`} download>
                      <Download size={18} className="mr-2" />
                      Download Signed PDF
                    </a>
                  </Button>
                )}
                {doc.status === 'DRAFT' && (
                   <Button variant="outline" asChild>
                     <Link href={`/documents/${id}/setup`}>Resume Setup</Link>
                   </Button>
                )}
              </div>
            }
          />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Col: Overview & Signers */}
            <div className="lg:col-span-2 space-y-8">
              <Card className="border-border/50 shadow-sm">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg flex items-center gap-2 text-primary font-bold">
                      <Users size={20} className="text-accent" />
                      Signer Status
                    </CardTitle>
                    <DocumentStatusBadge status={doc.status} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="divide-y border rounded-xl overflow-hidden bg-stone-50/20">
                    {signers.map((s) => (
                      <div key={s.id} className="flex items-center justify-between p-4 bg-card">
                        <div className="flex items-center gap-3">
                           <div className="p-2 rounded-full bg-stone-100 border text-stone-500">
                             <Mail size={16} />
                           </div>
                           <div className="min-w-0">
                             <p className="text-sm font-semibold text-primary truncate">{s.email}</p>
                             <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-tight">Signer</p>
                           </div>
                        </div>
                        <div className="flex items-center gap-3">
                           {s.status === 'SIGNED' ? (
                             <div className="flex items-center gap-1.5 text-emerald-600 text-xs font-bold bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
                               <CheckCircle2 size={14} />
                               Signed
                             </div>
                           ) : s.status === 'REJECTED' ? (
                            <div className="flex items-center gap-1.5 text-rose-600 text-xs font-bold bg-rose-50 px-2.5 py-1 rounded-full border border-rose-100">
                              <XCircle size={14} />
                              Rejected
                            </div>
                           ) : (
                            <div className="flex items-center gap-1.5 text-amber-600 text-xs font-bold bg-amber-50 px-2.5 py-1 rounded-full border border-amber-100">
                              <Clock size={14} />
                              Waiting
                            </div>
                           )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-border/50 shadow-sm overflow-hidden">
                 <CardHeader className="bg-stone-50/50 border-b">
                    <CardTitle className="text-base font-bold text-primary flex items-center gap-2">
                       <FileText size={18} className="text-muted-foreground" />
                       Document Details
                    </CardTitle>
                 </CardHeader>
                 <CardContent className="p-0">
                    <div className="grid grid-cols-2 sm:grid-cols-4 divide-x border-b">
                       <DetailItem label="Total Fields" value={doc.fields?.length || "-"} />
                       <DetailItem label="Created" value={new Date(doc.created_at).toLocaleDateString()} />
                       <DetailItem label="Last Update" value={new Date(doc.updated_at).toLocaleDateString()} />
                       <DetailItem label="Type" value="Standard PDF" />
                    </div>
                 </CardContent>
              </Card>
            </div>

            {/* Right Col: Activity Feed */}
            <div className="space-y-8">
               <Card className="border-border/50 shadow-sm h-full max-h-[600px] flex flex-col">
                  <CardHeader className="pb-3 border-b shrink-0">
                    <CardTitle className="text-lg flex items-center gap-2 text-primary font-bold">
                       <History size={20} className="text-accent" />
                       Audit Trail
                    </CardTitle>
                    <CardDescription>All actions taken on this document</CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 overflow-y-auto pt-6 px-6">
                     <div className="space-y-6 relative">
                        <div className="absolute left-[11px] top-2 bottom-2 w-[2px] bg-stone-100" />

                        {auditLogs.map((log, idx) => (
                          <div key={log.id} className="relative pl-8">
                             <div className={cn(
                               "absolute left-0 top-1 w-6 h-6 rounded-full border-4 border-background flex items-center justify-center",
                               idx === 0 ? "bg-accent text-accent-foreground" : "bg-stone-200 text-stone-500"
                             )}>
                                <div className="w-1.5 h-1.5 rounded-full bg-current" />
                             </div>
                             <div className="space-y-1">
                                <p className="text-sm font-semibold text-primary leading-tight">
                                   {log.event_type.replace(/_/g, ' ')}
                                </p>
                                <div className="flex items-center gap-2 text-[10px] text-muted-foreground uppercase font-bold tracking-tight">
                                   <Clock size={10} />
                                   {new Date(log.created_at).toLocaleString()}
                                </div>
                                {log.event_data && (
                                   <p className="text-[11px] text-muted-foreground bg-stone-50 p-2 rounded-lg mt-2 italic">
                                      {Object.entries(log.event_data).map(([k, v]) => `${k}: ${v}`).join(', ')}
                                   </p>
                                )}
                             </div>
                          </div>
                        ))}
                     </div>
                  </CardContent>
               </Card>
            </div>
          </div>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}

function DetailItem({ label, value }: { label: string, value: string }) {
  return (
    <div className="p-5 text-center sm:text-left">
       <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider mb-1">{label}</p>
       <p className="text-sm font-semibold text-primary">{value}</p>
    </div>
  )
}
