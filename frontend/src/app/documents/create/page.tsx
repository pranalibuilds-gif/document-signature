"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { DashboardLayout } from "@/components/layout/dashboard-layout"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { PageContainer } from "@/components/layout/page-container"
import { SectionHeader } from "@/components/layout/section-header"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Upload, FileUp, Loader2, ArrowRight, X } from "lucide-react"
import api from "@/lib/api"

export default function CreateDocumentPage() {
  const [title, setTitle] = useState("")
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const router = useRouter()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleCreate = async () => {
    if (!title || !file) return
    setIsUploading(true)

    try {
      // 1. Create document
      const docRes = await api.post("/documents", { title })
      const docId = docRes.data.id

      // 2. Upload file
      const formData = new FormData()
      formData.append("file", file)
      await api.post(`/documents/${docId}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
      })

      // 3. Move to next step (Add Signers)
      router.push(`/documents/${docId}/setup`)
    } catch (err) {
      console.error("Failed to create document", err)
      alert("Failed to create document. Please try again.")
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <PageContainer size="tight">
          <SectionHeader
            title="Create New Document"
            description="Start by naming your document and uploading the PDF."
          />

          <Card className="border-border/50 shadow-md">
            <CardHeader>
              <CardTitle className="text-lg">Document Details</CardTitle>
              <CardDescription>
                Provide a title and upload the file you wish to have signed.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="title">Document Title</Label>
                <Input
                  id="title"
                  placeholder="e.g., Employment Contract - June 2024"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  disabled={isUploading}
                />
              </div>

              <div className="space-y-2">
                <Label>PDF File</Label>
                {!file ? (
                  <label
                    className="flex flex-col items-center justify-center w-full h-48 border-2 border-dashed border-stone-200 rounded-xl bg-stone-50/50 hover:bg-stone-100/50 hover:border-accent/40 cursor-pointer transition-all group"
                  >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <div className="p-3 rounded-full bg-white shadow-sm border border-stone-100 group-hover:scale-110 transition-transform mb-3">
                        <Upload className="h-6 w-6 text-muted-foreground group-hover:text-accent" />
                      </div>
                      <p className="text-sm font-medium text-primary">Click to upload or drag and drop</p>
                      <p className="text-xs text-muted-foreground mt-1">PDF (max. 20MB)</p>
                    </div>
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf"
                      onChange={handleFileChange}
                      disabled={isUploading}
                    />
                  </label>
                ) : (
                  <div className="flex items-center justify-between p-4 rounded-xl border border-accent/20 bg-accent/5">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-white border border-accent/10">
                        <FileUp className="h-5 w-5 text-accent" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-primary truncate max-w-[250px]">{file.name}</p>
                        <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setFile(null)}
                      className="p-1 hover:bg-accent/10 rounded-full transition-colors"
                      disabled={isUploading}
                    >
                      <X size={18} className="text-muted-foreground" />
                    </button>
                  </div>
                )}
              </div>

              <div className="flex justify-end pt-4">
                <Button
                  onClick={handleCreate}
                  disabled={!title || !file || isUploading}
                  className="btn-accent px-8"
                >
                  {isUploading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <>
                      Continue to Setup
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </PageContainer>
      </DashboardLayout>
    </ProtectedRoute>
  )
}
