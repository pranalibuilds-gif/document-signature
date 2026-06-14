"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { History, Clock, FileText, UserCircle, Search, ShieldAlert } from "lucide-react"
import { Input } from "@/components/ui/input"
import api from "@/lib/api"
import { EmptyState } from "@/components/ui/empty-state"

export default function AdminAuditPage() {
  const [logs, setLogs] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState("")

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.get("/admin/audit?limit=100")
        setLogs(res.data)
      } catch (err) {
        console.error("Failed to fetch audit logs", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchLogs()
  }, [])

  const filteredLogs = logs.filter(log =>
    log.event_type.toLowerCase().includes(search.toLowerCase()) ||
    (log.user_id && log.user_id.toLowerCase().includes(search.toLowerCase()))
  )

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title="Audit Trail"
            description="Complete system-wide activity logs for security and compliance."
          />

          <div className="mb-6">
             <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
                <Input
                   placeholder="Filter events..."
                   className="pl-10 h-10"
                   value={search}
                   onChange={(e) => setSearch(e.target.value)}
                />
             </div>
          </div>

          {filteredLogs.length === 0 && !isLoading ? (
            <EmptyState
              title={search ? "No events match your search" : "Audit trail is empty"}
              description={search ? "Try adjusting your filters or searching for a different term." : "System activity will appear here once users begin interacting with the platform."}
              icon={search ? Search : ShieldAlert}
            />
          ) : (
            <Card className="border-border/50 shadow-sm overflow-hidden">
              <CardContent className="p-0">
                 <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                         <tr className="bg-stone-50 border-b">
                            <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Timestamp</th>
                            <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Event</th>
                            <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Actor</th>
                            <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Details</th>
                         </tr>
                      </thead>
                      <tbody className="divide-y">
                         {isLoading ? (
                           [1,2,3,4,5].map(i => (
                             <tr key={i}><td colSpan={4} className="p-0"><Skeleton className="h-16 w-full rounded-none" /></td></tr>
                           ))
                         ) : filteredLogs.map((log) => (
                           <tr key={log.id} className="hover:bg-stone-50/50 transition-colors">
                              <td className="px-6 py-4 text-xs text-muted-foreground whitespace-nowrap">
                                 <div className="flex items-center gap-2">
                                    <Clock size={12} />
                                    {new Date(log.created_at).toLocaleString()}
                                 </div>
                              </td>
                              <td className="px-6 py-4">
                                 <Badge variant="outline" className="uppercase text-[9px] font-bold tracking-wider">
                                    {log.event_type.replace(/_/g, ' ')}
                                 </Badge>
                              </td>
                              <td className="px-6 py-4">
                                 <div className="flex items-center gap-2">
                                    <UserCircle size={16} className="text-stone-300" />
                                    <span className="text-xs font-medium text-primary">
                                       {log.actor_type} {log.user_id ? `(${log.user_id.slice(0, 8)})` : ""}
                                    </span>
                                 </div>
                              </td>
                              <td className="px-6 py-4">
                                 {log.event_data && (
                                   <span className="text-[10px] text-muted-foreground bg-stone-100 px-2 py-1 rounded truncate max-w-[200px] inline-block">
                                      {JSON.stringify(log.event_data)}
                                   </span>
                                 )}
                              </td>
                           </tr>
                         ))}
                      </tbody>
                    </table>
                 </div>
              </CardContent>
            </Card>
          )}
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
