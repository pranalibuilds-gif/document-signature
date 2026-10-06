"use client"

import { useEffect, useMemo, useState } from "react"
import Link from "next/link"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Mail, Search, UserPlus, Users, Loader2, FileText } from "lucide-react"
import api from "@/lib/api"

interface SignerContact {
  email: string
  document_count: number
  last_used_at: string
}

interface DraftDocument {
  id: string
  title: string
  status: string
}

export default function SignersPage() {
  const [contacts, setContacts] = useState<SignerContact[]>([])
  const [drafts, setDrafts] = useState<DraftDocument[]>([])
  const [selectedDraftByEmail, setSelectedDraftByEmail] = useState<Record<string, string>>({})
  const [search, setSearch] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [addingEmail, setAddingEmail] = useState<string | null>(null)
  const [addedEmails, setAddedEmails] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    const loadDirectory = async () => {
      try {
        const [directoryResponse, documentsResponse] = await Promise.all([
          api.get<SignerContact[]>("/signers/directory"),
          api.get<DraftDocument[]>("/documents?skip=0&limit=100"),
        ])
        if (cancelled) return

        const draftDocuments = documentsResponse.data.filter((document) => document.status === "DRAFT")
        setContacts(directoryResponse.data)
        setDrafts(draftDocuments)
        if (draftDocuments.length > 0) {
          setSelectedDraftByEmail(
            Object.fromEntries(directoryResponse.data.map((contact) => [contact.email, draftDocuments[0].id]))
          )
        }
      } catch {
        if (!cancelled) {
          setError("Unable to load your signer directory. Please try again.")
        }
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    void loadDirectory()
    return () => {
      cancelled = true
    }
  }, [])

  const filteredContacts = useMemo(() => {
    const query = search.trim().toLowerCase()
    if (!query) return contacts
    return contacts.filter((contact) => contact.email.toLowerCase().includes(query))
  }, [contacts, search])

  const addSignerToDraft = async (contact: SignerContact) => {
    const documentId = selectedDraftByEmail[contact.email]
    if (!documentId) return

    setAddingEmail(contact.email)
    setActionError(null)
    try {
      await api.post(`/documents/${documentId}/signers`, { email: contact.email })
      setAddedEmails((current) => [...current, contact.email])
    } catch {
      setActionError(`Could not add ${contact.email}. It may already be on that document.`)
    } finally {
      setAddingEmail(null)
    }
  }

  return (
    <ProtectedRoute requiredRole="USER">
      <DashboardLayout>
        <PageContainer>
          <SectionHeader
            title="Signers Directory"
            description="Reuse people you have invited before. Contacts are scoped to documents you own."
          />

          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {actionError && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{actionError}</AlertDescription>
            </Alert>
          )}

          <Card className="border-border/50 shadow-sm">
            <CardContent className="space-y-5 p-6">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="flex items-center gap-2 text-lg font-semibold text-primary">
                    <Users size={20} className="text-accent" />
                    Previous signers
                  </h2>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {contacts.length} {contacts.length === 1 ? "contact" : "contacts"} from your documents
                  </p>
                </div>
                <div className="relative w-full sm:max-w-xs">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    aria-label="Search signers"
                    className="pl-9"
                    placeholder="Search by email..."
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                  />
                </div>
              </div>

              {isLoading ? (
                <div className="flex justify-center py-12" role="status" aria-label="Loading signers">
                  <Loader2 className="animate-spin text-accent" />
                </div>
              ) : filteredContacts.length === 0 ? (
                <div className="flex flex-col items-center rounded-xl border border-dashed py-12 text-center">
                  <div className="mb-4 rounded-full bg-stone-100 p-4">
                    <Users size={36} className="text-stone-400" />
                  </div>
                  <h3 className="font-semibold text-primary">
                    {contacts.length === 0 ? "No previous signers" : "No matching signers"}
                  </h3>
                  <p className="mt-2 max-w-sm text-sm text-muted-foreground">
                    {contacts.length === 0
                      ? "Signers you invite on your documents will appear here so you can reuse them."
                      : "Try a different email search."}
                  </p>
                  {contacts.length === 0 && (
                    <Button asChild variant="outline" className="mt-5">
                      <Link href="/documents/create">
                        <FileText size={16} className="mr-2" />
                        Create a document
                      </Link>
                    </Button>
                  )}
                </div>
              ) : (
                <ul className="divide-y rounded-xl border">
                  {filteredContacts.map((contact) => {
                    const added = addedEmails.includes(contact.email)
                    return (
                      <li
                        key={contact.email}
                        className="flex flex-col gap-4 p-4 md:flex-row md:items-center md:justify-between"
                      >
                        <div className="flex min-w-0 items-center gap-3">
                          <div className="shrink-0 rounded-full bg-accent/10 p-2 text-accent">
                            <Mail size={18} />
                          </div>
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium text-primary">{contact.email}</p>
                            <p className="text-xs text-muted-foreground">
                              Invited on {contact.document_count}{" "}
                              {contact.document_count === 1 ? "document" : "documents"} · Last used{" "}
                              {new Date(contact.last_used_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>

                        <div className="flex flex-col gap-2 sm:flex-row">
                          {drafts.length > 0 ? (
                            <>
                              <select
                                aria-label={`Choose a draft for ${contact.email}`}
                                className="h-10 min-w-0 rounded-lg border border-input bg-background px-3 text-sm sm:min-w-52"
                                value={selectedDraftByEmail[contact.email] ?? ""}
                                onChange={(event) =>
                                  setSelectedDraftByEmail((current) => ({
                                    ...current,
                                    [contact.email]: event.target.value,
                                  }))
                                }
                                disabled={added}
                              >
                                {drafts.map((draft) => (
                                  <option key={draft.id} value={draft.id}>
                                    {draft.title}
                                  </option>
                                ))}
                              </select>
                              <Button
                                type="button"
                                size="sm"
                                variant={added ? "outline" : "accent"}
                                onClick={() => void addSignerToDraft(contact)}
                                disabled={added || addingEmail === contact.email}
                              >
                                {addingEmail === contact.email ? (
                                  <Loader2 size={16} className="mr-2 animate-spin" />
                                ) : (
                                  <UserPlus size={16} className="mr-2" />
                                )}
                                {added ? "Added" : "Add to draft"}
                              </Button>
                            </>
                          ) : (
                            <Button asChild size="sm" variant="outline">
                              <Link href="/documents/create">Create a draft to reuse</Link>
                            </Button>
                          )}
                        </div>
                      </li>
                    )
                  })}
                </ul>
              )}
            </CardContent>
          </Card>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
