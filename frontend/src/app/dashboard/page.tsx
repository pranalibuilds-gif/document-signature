"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/ui/empty-state"
import {
  Plus,
  FileText,
  CheckCircle2,
  Clock,
  AlertCircle
} from "lucide-react"
import { useAuthStore } from "@/store/use-auth-store"

export default function DashboardPage() {
  const { user } = useAuthStore()

  const stats = [
    { name: "Total Documents", value: "0", icon: FileText, color: "text-blue-600" },
    { name: "Completed", value: "0", icon: CheckCircle2, color: "text-emerald-600" },
    { name: "Pending", value: "0", icon: Clock, color: "text-amber-600" },
    { name: "Needs Attention", value: "0", icon: AlertCircle, color: "text-rose-600" },
  ]

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title={`Welcome back, ${user?.first_name || "User"}`}
            description="Here's what's happening with your documents today."
            actions={
              <Button className="btn-accent">
                <Plus size={18} className="mr-2" />
                New Document
              </Button>
            }
          />

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-10">
            {stats.map((stat) => (
              <Card key={stat.name} className="border-border/50">
                <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {stat.name}
                  </CardTitle>
                  <stat.icon className={stat.color} size={18} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stat.value}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-primary">Recent Documents</h3>
            <EmptyState
              title="No documents yet"
              description="Get started by uploading your first document for signing."
              icon={FileText}
              action={
                <Button variant="outline">
                  Upload PDF
                </Button>
              }
            />
          </div>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
