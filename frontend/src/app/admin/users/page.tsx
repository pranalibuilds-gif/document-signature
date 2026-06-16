"use client"

import { useState, useEffect } from "react"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { UserCircle, Mail, ShieldCheck, Calendar, Users as UsersIcon } from "lucide-react"
import api from "@/lib/api"
import { EmptyState } from "@/components/ui/empty-state"

export default function AdminUsersPage() {
  const [users, setUsers] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await api.get("/admin/users")
        setUsers(res.data)
      } catch (err) {
        console.error("Failed to fetch users", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchUsers()
  }, [])

  return (
    <ProtectedRoute requiredRole="ADMIN">
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title="User Management"
            description="View and manage all registered platform users."
          />

          {users.length === 0 && !isLoading ? (
            <EmptyState
              title="No users found"
              description="There are currently no registered users on the platform."
              icon={UsersIcon}
            />
          ) : (
            <Card className="border-border/50 shadow-sm overflow-hidden">
              <CardContent className="p-0">
                 <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                         <tr className="bg-stone-50 border-b">
                            <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">User</th>
                            <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Status</th>
                            <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Role</th>
                            <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Joined</th>
                         </tr>
                      </thead>
                      <tbody className="divide-y">
                         {isLoading ? (
                           [1,2,3,4,5].map(i => (
                             <tr key={i}><td colSpan={4} className="p-0"><Skeleton className="h-16 w-full rounded-none" /></td></tr>
                           ))
                         ) : users.map((user) => (
                           <tr key={user.id} className="hover:bg-stone-50/50 transition-colors">
                              <td className="px-6 py-4">
                                 <div className="flex items-center gap-3">
                                    <UserCircle size={32} className="text-stone-300" />
                                    <div className="min-w-0">
                                       <p className="text-sm font-semibold text-primary truncate">
                                          {user.first_name} {user.last_name}
                                       </p>
                                       <p className="text-xs text-muted-foreground truncate flex items-center gap-1">
                                          <Mail size={10} /> {user.email}
                                       </p>
                                    </div>
                                 </div>
                              </td>
                              <td className="px-6 py-4">
                                 {user.is_verified ? (
                                   <Badge variant="success" className="bg-emerald-50 text-emerald-600 border-emerald-100">Verified</Badge>
                                 ) : (
                                   <Badge variant="secondary" className="bg-stone-100 text-stone-500">Unverified</Badge>
                                 )}
                              </td>
                              <td className="px-6 py-4">
                                 <Badge variant={user.role === 'ADMIN' ? 'accent' : 'outline'} className="uppercase text-[10px]">
                                    {user.role}
                                 </Badge>
                              </td>
                              <td className="px-6 py-4 text-xs text-muted-foreground">
                                 <div className="flex items-center gap-1">
                                    <Calendar size={12} />
                                    {new Date(user.created_at).toLocaleDateString()}
                                 </div>
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
