"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Users,
  FileText,
  Settings,
  ShieldCheck,
  Activity,
  Mail,
  CheckCircle2,
  Clock,
  AlertCircle,
  XCircle
} from "lucide-react"
import api from "@/lib/api"

export default function AdminDashboardPage() {
  const [metrics, setMetrics] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const res = await api.get("/admin/dashboard")
        setMetrics(res.data)
      } catch (err) {
        console.error("Failed to fetch admin metrics", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchMetrics()
  }, [])

  const statCards = [
    { name: "Total Users", value: metrics?.users, icon: Users, color: "text-blue-600" },
    { name: "Verified Users", value: metrics?.verified_users, icon: ShieldCheck, color: "text-emerald-600" },
    { name: "Total Documents", value: metrics?.documents_total, icon: FileText, color: "text-indigo-600" },
    { name: "Completed", value: metrics?.completed_documents, icon: CheckCircle2, color: "text-emerald-600" },
  ]

  const statusBreakdown = [
    { name: "Pending", value: metrics?.pending_documents, icon: Clock, color: "bg-amber-100 text-amber-600" },
    { name: "Rejected", value: metrics?.rejected_documents, icon: XCircle, color: "bg-rose-100 text-rose-600" },
    { name: "Expired", value: metrics?.expired_documents, icon: AlertCircle, color: "bg-stone-100 text-stone-600" },
    { name: "Drafts", value: metrics?.draft_documents, icon: Activity, color: "bg-blue-100 text-blue-600" },
  ]

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title="Admin Overview"
            description="System-wide metrics and document status tracking."
          />

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            {isLoading ? (
              [1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 w-full rounded-xl" />)
            ) : statCards.map((stat) => (
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

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
             <Card className="lg:col-span-2 border-border/50 shadow-sm">
                <CardHeader>
                   <CardTitle className="text-lg font-bold">Document Status Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                   <div className="grid grid-cols-2 gap-4">
                      {isLoading ? (
                        [1,2,3,4].map(i => <Skeleton key={i} className="h-20 w-full" />)
                      ) : statusBreakdown.map((item) => (
                        <div key={item.name} className="flex items-center gap-4 p-4 rounded-xl border bg-stone-50/30">
                           <div className={cn("p-3 rounded-lg", item.color)}>
                              <item.icon size={20} />
                           </div>
                           <div>
                              <p className="text-2xl font-bold text-primary">{item.value}</p>
                              <p className="text-xs font-bold text-muted-foreground uppercase tracking-tight">{item.name}</p>
                           </div>
                        </div>
                      ))}
                   </div>
                </CardContent>
             </Card>

             <Card className="border-border/50 shadow-sm">
                <CardHeader>
                   <CardTitle className="text-lg font-bold">System Health</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                   <HealthItem label="Database" status="active" />
                   <HealthItem label="PDF Engine" status="active" />
                   <HealthItem label="Email Service" status="active" />
                   <HealthItem label="Scheduler" status="active" />
                </CardContent>
             </Card>
          </div>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}

function HealthItem({ label, status }: { label: string, status: 'active' | 'warning' | 'down' }) {
    return (
        <div className="flex items-center justify-between p-3 rounded-lg border bg-stone-50/50">
            <span className="text-sm font-medium text-primary">{label}</span>
            <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                <span className="text-[10px] font-bold uppercase text-emerald-600">Online</span>
            </div>
        </div>
    )
}
