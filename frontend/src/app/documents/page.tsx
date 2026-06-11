"use client"

import { useState } from "react"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Button } from "@/components/ui/button"
import { EmptyState } from "@/components/ui/empty-state"
import { FileText, Plus, Search, Filter } from "lucide-react"
import { Input } from "@/components/ui/input"

export default function DocumentsPage() {
  const [search, setSearch] = useState("")

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title="Documents"
            description="Manage your documents and track signing progress."
            actions={
              <Button className="btn-accent">
                <Plus size={18} className="mr-2" />
                New Document
              </Button>
            }
          />

          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" size={16} />
              <Input
                placeholder="Search by title or email..."
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

          <EmptyState
            title="No results found"
            description="Try adjusting your search or filters to find what you're looking for."
            icon={FileText}
          />
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
