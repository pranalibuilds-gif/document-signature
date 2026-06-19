"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Trash2, Plus, Users, ArrowRight, Loader2, Mail, UserCheck } from "lucide-react"
import api from "@/lib/api"
import { useAuthStore } from "@/store/use-auth-store"

interface Signer {
  id: string
  email: string
  status: string
}

export default function DocumentSetupPage() {
  const { id } = useParams()
  const router = useRouter()
  const { user } = useAuthStore()
  const [signers, setSigners] = useState<Signer[]>([])
  const [newEmail, setNewEmail] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [isAdding, setIsAdding] = useState(false)

  const isOwnerAlreadySigner = signers.some(s => s.email === user?.email)

  useEffect(() => {
    const fetchSigners = async () => {
      try {
        const res = await api.get(`/documents/${id}/signers`)
        setSigners(res.data)
      } catch (err) {
        console.error("Failed to fetch signers", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchSigners()
  }, [id])

  const handleAddSigner = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newEmail) return
    setIsAdding(true)

    try {
      const res = await api.post(`/documents/${id}/signers`, { email: newEmail })
      setSigners([...signers, res.data])
      setNewEmail("")
    } catch (err) {
      alert("Failed to add signer")
    } finally {
      setIsAdding(false)
    }
  }

  const handleRemoveSigner = async (signerId: string) => {
    try {
      await api.delete(`/documents/${id}/signers/${signerId}`)
      setSigners(signers.filter(s => s.id !== signerId))
    } catch (err) {
      alert("Failed to remove signer")
    }
  }

  const handleAddSelf = async () => {
    if (!user?.email) return
    setIsAdding(true)
    try {
      const res = await api.post(`/documents/${id}/signers`, { email: user.email })
      setSigners([...signers, res.data])
    } catch (err) {
      alert("Failed to add yourself as a signer")
    } finally {
      setIsAdding(false)
    }
  }

  return (
    <ProtectedRoute requiredRole="USER">
      <DashboardLayout>
        <PageContainer size="tight">
          <SectionHeader
            title="Document Setup"
            description="Manage signers and their roles for this document."
          />

          <div className="grid gap-6">
            <Card className="border-border/50 shadow-md">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Users className="text-accent" size={20} />
                  Manage Signers
                </CardTitle>
                <CardDescription>
                  Add the email addresses of all individuals required to sign this document.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col gap-4">
                  {!isOwnerAlreadySigner && (
                    <Button
                      type="button"
                      variant="outline"
                      className="w-full h-12 border-accent/20 text-accent hover:bg-accent/5 font-bold"
                      onClick={handleAddSelf}
                      disabled={isAdding}
                    >
                      <UserCheck size={18} className="mr-2" />
                      Add Me as Signer
                    </Button>
                  )}

                  <form onSubmit={handleAddSigner} className="flex gap-2">
                    <div className="flex-1">
                      <Input
                        placeholder="signer@example.com"
                        type="email"
                        value={newEmail}
                        onChange={(e) => setNewEmail(e.target.value)}
                        required
                        disabled={isAdding}
                      />
                    </div>
                    <Button type="submit" variant="secondary" disabled={isAdding}>
                      {isAdding ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} className="mr-2" />}
                      Add Others
                    </Button>
                  </form>
                </div>

                <div className="space-y-3">
                  {signers.length === 0 ? (
                    <div className="text-center py-8 rounded-xl border border-dashed text-muted-foreground">
                      No signers added yet
                    </div>
                  ) : (
                    <>
                      {signers.map((signer) => (
                        <div
                          key={signer.id}
                          className="flex items-center justify-between p-4 rounded-xl border bg-card shadow-sm hover:shadow-md transition-all group border-stone-200/60"
                        >
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="p-2 rounded-full bg-stone-100 border text-stone-500 group-hover:bg-accent/10 group-hover:text-accent transition-colors shrink-0">
                              <Mail size={16} />
                            </div>
                            <span className="text-sm font-medium text-primary truncate">{signer.email}</span>
                          </div>
                          <button
                            onClick={() => handleRemoveSigner(signer.id)}
                            className="p-2 text-muted-foreground hover:text-destructive transition-colors shrink-0"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      ))}

                      <div className="mt-6 p-4 rounded-xl bg-accent/5 border border-accent/10 flex items-start gap-3 shadow-sm">
                        <div className="p-1 rounded-md bg-accent text-accent-foreground mt-0.5 shadow-sm">
                          <Plus size={14} />
                        </div>
                        <div className="space-y-1 min-w-0">
                          <p className="text-sm font-semibold text-primary">All signers added?</p>
                          <p className="text-xs text-muted-foreground leading-relaxed">
                            The next step is to place signature and text fields on your document in the interactive editor.
                          </p>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </CardContent>
              <CardFooter className="flex justify-between border-t bg-stone-50/30 px-6 py-4">
                <Button variant="ghost" onClick={() => router.push("/documents")}>
                  Cancel
                </Button>
                <Button
                  className="btn-accent px-8"
                  disabled={signers.length === 0}
                  onClick={() => router.push(`/documents/${id}/editor`)}
                >
                  Continue to Editor
                  <ArrowRight size={18} className="ml-2" />
                </Button>
              </CardFooter>
            </Card>
          </div>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
