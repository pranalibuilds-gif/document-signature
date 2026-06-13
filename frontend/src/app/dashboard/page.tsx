"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/ui/empty-state"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Plus,
  FileText,
  CheckCircle2,
  Clock,
  AlertCircle,
  ChevronRight,
  FileDown
} from "lucide-react"
import { useAuthStore } from "@/store/use-auth-store"
import api from "@/lib/api"
import { DocumentStatusBadge } from "@/components/documents/document-status-badge"

/**
 * DashboardPage Component
 * Provides a high-level overview of the user's documents and system activity.
 * Displays aggregate statistics and a list of the most recent documents.
 */
export default function DashboardPage() {
  const { user } = useAuthStore()
  const [stats, setStats] = useState<any[]>([])
  const [recentDocs, setRecentDocs] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  /**
   * Data Fetching
   * Fetches latest documents and calculates statistics for the summary cards.
   */
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Fetch last 5 documents for the 'Recent' list
        const res = await api.get("/documents?limit=5")
        const docs = res.data
        setRecentDocs(docs)

        // Calculate summary metrics based on status
        const completed = docs.filter((d: any) => d.status === 'COMPLETED').length
        const pending = docs.filter((d: any) => d.status === 'PENDING' || d.status === 'PARTIALLY_SIGNED').length
        const needsAttention = docs.filter((d: any) => d.status === 'REJECTED' || d.status === 'EXPIRED').length

        setStats([
          { name: "Total Documents", value: docs.length.toString(), icon: FileText, color: "text-blue-600" },
          { name: "Completed", value: completed.toString(), icon: CheckCircle2, color: "text-emerald-600" },
          { name: "Pending", value: pending.toString(), icon: Clock, color: "text-amber-600" },
          { name: "Needs Attention", value: needsAttention.toString(), icon: AlertCircle, color: "text-rose-600" },
        ])
      } catch (err) {
        console.error("Failed to fetch dashboard data", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchDashboardData()
  }, [])

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title={`Welcome back, ${user?.first_name || "User"}`}
            description="Here's what's happening with your documents today."
            actions={
              <Button className="btn-accent" asChild>
                <Link href="/documents/create">
                  <Plus size={18} className="mr-2" />
                  New Document
                </Link>
              </Button>
            }
          />

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-10">
            {isLoading ? (
              [1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 w-full rounded-xl" />)
            ) : stats.map((stat) => (
              <Card key={stat.name} className="border-border/50 shadow-sm">
                <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                  <CardTitle className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                    {stat.name}
                  </CardTitle>
                  <stat.icon className={stat.color} size={18} />
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-primary">{stat.value}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-primary">Recent Documents</h3>
              <Button variant="ghost" size="sm" asChild className="text-accent hover:text-accent hover:bg-accent/5">
                <Link href="/documents">View all</Link>
              </Button>
            </div>

            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => <Skeleton key={i} className="h-16 w-full rounded-xl" />)
              }</div>
            ) : recentDocs.length === 0 ? (
              <EmptyState
                title="No documents yet"
                description="Get started by uploading your first document for signing."
                icon={FileText}
                action={
                  <Button variant="outline" asChild>
                    <Link href="/documents/create">Upload PDF</Link>
                  </Button>
                }
              />
            ) : (
              <div className="grid gap-3">
                {recentDocs.map(doc => (
                  <Link
                    key={doc.id}
                    href={doc.status === 'DRAFT' ? `/documents/${doc.id}/setup` : `/documents/${doc.id}`}
                  >
                    <div className="flex items-center justify-between p-4 rounded-xl border border-border/50 bg-card hover:border-accent/40 transition-all group">
                      <div className="flex items-center gap-4">
                        <div className="p-2 rounded-lg bg-stone-100 text-stone-500 group-hover:bg-accent/5 group-hover:text-accent">
                          <FileText size={20} />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-primary leading-tight">{doc.title}</p>
                          <p className="text-[10px] text-muted-foreground mt-1">
                            Added {new Date(doc.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 min-w-0">
                        <DocumentStatusBadge status={doc.status} />
                        {doc.status === 'COMPLETED' ? (
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-8 text-[10px] font-bold uppercase tracking-tight"
                            asChild
                            onClick={(e) => e.stopPropagation()}
                          >
                            <a href={`/api/v1/documents/${doc.id}/final-file`} download>
                              <FileDown size={14} className="mr-1" />
                              Download
                            </a>
                          </Button>
                        ) : (
                          <ChevronRight size={16} className="text-stone-300 group-hover:text-accent group-hover:translate-x-1 transition-all shrink-0" />
                        )}
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
