"use client"

import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Settings, User, Bell, Shield, Palette } from "lucide-react"

export default function SettingsPage() {
  return (
    <ProtectedRoute requiredRole="USER">
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title="Settings"
            description="Manage your account preferences and system configuration."
          />

          <div className="grid gap-6 max-w-4xl">
             <SettingsItem
                icon={User}
                title="Profile Information"
                description="Update your name, email address, and personal details."
             />
             <SettingsItem
                icon={Bell}
                title="Notifications"
                description="Choose how and when you want to be notified about document status."
             />
             <SettingsItem
                icon={Shield}
                title="Security"
                description="Manage your password, two-factor authentication, and session logs."
             />
             <SettingsItem
                icon={Palette}
                title="Appearance"
                description="Customize the look and feel of your dashboard."
             />
          </div>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}

function SettingsItem({ icon: Icon, title, description }: any) {
    return (
        <Card className="hover:border-accent/40 transition-colors cursor-pointer border-border/50 shadow-sm">
            <CardContent className="flex items-center p-6 gap-6">
                <div className="p-3 rounded-xl bg-stone-100 text-stone-500">
                    <Icon size={24} />
                </div>
                <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-primary mb-1">{title}</h4>
                    <p className="text-xs text-muted-foreground">{description}</p>
                </div>
            </CardContent>
        </Card>
    )
}
