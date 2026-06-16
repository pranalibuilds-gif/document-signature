"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/ui/empty-state"
import { Card, CardContent } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { DocumentStatusBadge } from "@/components/documents/document-status-badge"
import { FileText, Plus, Search, Filter, Calendar, Users, ChevronRight, FileDown } from "lucide-react"
import { Input } from "@/components/ui/input"
import api from "@/lib/api"

export default function DocumentsPage() {
  const [search, setSearch] = useState("")
  const [documents, setDocuments] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const res = await api.get("/documents")
        setDocuments(res.data)
      } catch (err: any) {
        const detail = err.response?.data?.detail
        setError(typeof detail === "string" ? detail : "Failed to load documents. Please try again.")
      } finally {
        setIsLoading(false)
      }
    }
    fetchDocuments()
  }, [])

  const filteredDocs = documents.filter(doc =>
    doc.title.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <ProtectedRoute requiredRole="USER">
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title="Documents"
            description="Manage your documents and track signing progress."
            actions={
              <Button className="btn-accent" asChild>
                <Link href="/documents/create">
                  <Plus size={18} className="mr-2" />
                  New Document
                </Link>
              </Button>
            }
          />

          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
              <Input
                placeholder="Search by title..."
                className="pl-10 h-11"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Button variant="outline" className="h-11">
              <Filter size={16} className="mr-2" />
              Filter
            </Button>
          </div>

          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <Skeleton key={i} className="h-24 w-full rounded-xl" />
              ))}
            </div>
          ) : error ? (
            <EmptyState
              title="Something went wrong"
              description={error}
              icon={FileText}
              action={<Button onClick={() => window.location.reload()}>Retry</Button>}
            />
          ) : filteredDocs.length === 0 ? (
            <EmptyState
              title={search ? "No results found" : "No documents yet"}
              description={search ? "Try adjusting your search to find what you're looking for." : "Upload your first document to start the signing process."}
              icon={FileText}
              action={!search ? (
                <Button className="btn-accent" asChild>
                  <Link href="/documents/create">Upload PDF</Link>
                </Button>
              ) : undefined}
            />
          ) : (
            <div className="grid gap-4">
              {filteredDocs.map((doc) => (
                <Link
                  key={doc.id}
                  href={doc.status === 'DRAFT' ? `/documents/${doc.id}/setup` : `/documents/${doc.id}`}
                >
                  <Card className="hover:border-accent/40 transition-all group cursor-pointer border-border/50 shadow-sm">
                    <CardContent className="p-0">
                      <div className="flex items-center p-5">
                        <div className="p-3 rounded-lg bg-stone-100 text-stone-500 group-hover:bg-accent/10 group-hover:text-accent transition-colors mr-4">
                          <FileText size={24} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-1">
                            <h4 className="text-sm font-semibold text-primary truncate">{doc.title}</h4>
                            <DocumentStatusBadge status={doc.status} />
                          </div>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center gap-1">
                              <Calendar size={12} />
                              {new Date(doc.created_at).toLocaleDateString()}
                            </div>
                            <div className="flex items-center gap-1">
                              <Users size={12} />
                              Signers assigned
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          {doc.status === 'COMPLETED' && (
                            <Button
                              size="sm"
                              variant="outline"
                              className="h-9 px-4 text-xs font-bold"
                              onClick={(e) => {
                                e.stopPropagation()
                                const downloadUrl = `/api/v1/documents/${doc.id}/final-file`
                                const anchor = document.createElement("a")
                                anchor.href = downloadUrl
                                anchor.download = ""
                                document.body.appendChild(anchor)
                                anchor.click()
                                document.body.removeChild(anchor)
                              }}
                            >
                              <FileDown size={16} className="mr-2" />
                              Download Final PDF
                            </Button>
                          )}
                          <ChevronRight size={20} className="text-stone-300 group-hover:text-accent group-hover:translate-x-1 transition-all" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
