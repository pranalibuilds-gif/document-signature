"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent } from "@/components/ui/card"
import { Users, Mail, Clock } from "lucide-react"

export default function SignersPage() {
  return (
    <ProtectedRoute requiredRole="USER">
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title="Signers Directory"
            description="Manage your list of frequent signers and their contact information."
          />

          <Card className="border-border/50 shadow-sm">
             <CardContent className="flex flex-col items-center justify-center py-20 text-center">
                <div className="p-4 rounded-full bg-stone-100 mb-4">
                   <Users size={48} className="text-stone-300" />
                </div>
                <h3 className="text-lg font-semibold text-primary">Coming Soon</h3>
                <p className="text-sm text-muted-foreground max-w-xs mt-2">
                   We're building a central directory to help you manage and reuse your frequent signers across documents.
                </p>
             </CardContent>
          </Card>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
