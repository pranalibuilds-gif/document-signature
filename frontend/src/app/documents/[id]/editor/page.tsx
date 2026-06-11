"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ProtectedRoute } from "@/components/auth/protected-route"
import { Button } from "@/components/ui/button"
import {
  ChevronLeft,
  Eye,
  Send,
  Type,
  Calendar,
  PenTool,
  Info,
  Loader2,
  Save
} from "lucide-react"
import api from "@/lib/api"
import { cn } from "@/lib/utils"
import { useEditorStore, FieldType, EditorField } from "@/store/use-editor-store"
import { PDFViewer } from "@/modules/documents/components/editor/pdf-viewer"
import { Label } from "@/components/ui/label"
import { Trash2, Plus, Minus } from "lucide-react"

export default function DocumentEditorPage() {
  const { id } = useParams()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [document, setDocument] = useState<any>(null)
  const [signers, setSigners] = useState<any[]>([])

  const {
    currentSignerId, setCurrentSigner,
    activeTool, setActiveTool,
    fields, setFields, addField,
    selectedFieldId, selectField, removeField, updateField,
    zoom, setZoom
  } = useEditorStore()

  const selectedField = fields.find(f => f.id === selectedFieldId)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [docRes, signersRes, fieldsRes] = await Promise.all([
          api.get(`/documents/${id}`),
          api.get(`/documents/${id}/signers`),
          api.get(`/documents/${id}/fields`)
        ])
        setDocument(docRes.data)
        setSigners(signersRes.data)

        if (signersRes.data.length > 0 && !currentSignerId) {
          setCurrentSigner(signersRes.data[0].id)
        }

        // Map backend fields to editor store format
        const mappedFields: EditorField[] = fieldsRes.data.map((f: any) => ({
          id: f.id,
          type: f.field_type,
          signerId: f.assigned_signer_id,
          pageNumber: f.page_number,
          x: f.x_coordinate,
          y: f.y_coordinate,
          width: f.width,
          height: f.height
        }))
        setFields(mappedFields)

      } catch (err) {
        console.error("Failed to fetch document data", err)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleFieldPlace = (pageNumber: number, x: number, y: number) => {
    if (!activeTool || !currentSignerId) return

    const newField: EditorField = {
      id: `temp_${Date.now()}`,
      type: activeTool,
      signerId: currentSignerId,
      pageNumber,
      x,
      y,
      width: activeTool === "SIGNATURE" ? 150 : 120,
      height: activeTool === "SIGNATURE" ? 50 : 35
    }

    addField(newField)
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      const newFields = fields.filter(f => f.id.startsWith("temp_"))

      for (const f of newFields) {
        await api.post(`/documents/${id}/fields`, {
          assigned_signer_id: f.signerId,
          page_number: f.pageNumber,
          x_coordinate: f.x,
          y_coordinate: f.y,
          width: f.width,
          height: f.height,
          field_type: f.type,
          required: true
        })
      }

      const res = await api.get(`/documents/${id}/fields`)
      setFields(res.data.map((f: any) => ({
        id: f.id,
        type: f.field_type,
        signerId: f.assigned_signer_id,
        pageNumber: f.page_number,
        x: f.x_coordinate,
        y: f.y_coordinate,
        width: f.width,
        height: f.height
      })))

      alert("Fields saved successfully!")
    } catch (err) {
      alert("Failed to save fields")
    } finally {
      setIsSaving(false)
    }
  }

  const handleActivate = async () => {
    try {
      await api.post(`/documents/${id}/activate`)
      router.push("/documents?activated=true")
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to activate document")
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <Loader2 className="animate-spin text-accent" size={32} />
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <div className="flex flex-col h-screen bg-stone-100/50">
        {/* Editor Topbar */}
        <header className="flex h-14 items-center justify-between border-b bg-card px-4 shrink-0">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => router.push(`/documents/${id}/setup`)}>
              <ChevronLeft size={18} className="mr-1" />
              Back
            </Button>
            <div className="h-6 w-[1px] bg-border" />
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-primary leading-none">{document?.title}</span>
              <span className="text-[10px] text-muted-foreground mt-0.5">DRAFT MODE</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center bg-stone-100 rounded-lg p-1 border">
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
              >
                <Minus size={14} />
              </Button>
              <span className="text-[10px] font-bold w-12 text-center">
                {Math.round(zoom * 100)}%
              </span>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0"
                onClick={() => setZoom(Math.min(2, zoom + 0.1))}
              >
                <Plus size={14} />
              </Button>
            </div>
            <div className="h-6 w-[1px] bg-border mx-1" />
            <Button variant="outline" size="sm" onClick={handleSave} disabled={isSaving}>
              {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save size={16} className="mr-2" />}
              Save Progress
            </Button>
            <div className="h-6 w-[1px] bg-border mx-1" />
            <Button variant="outline" size="sm">
              <Eye size={16} className="mr-2" />
              Preview
            </Button>
            <Button size="sm" className="btn-accent" onClick={handleActivate}>
              <Send size={16} className="mr-2" />
              Send for Signing
            </Button>
          </div>
        </header>

        <div className="flex flex-1 overflow-hidden">
          {/* Left Sidebar: Palette */}
          <aside className="w-72 border-r bg-card p-4 space-y-6 flex flex-col shrink-0">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/60">
                1. Select Signer
              </label>
              <select
                className="mt-2 w-full rounded-lg border bg-stone-50 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-accent/20"
                value={currentSignerId || ""}
                onChange={(e) => setCurrentSigner(e.target.value)}
              >
                {signers.map(s => (
                  <option key={s.id} value={s.id}>{s.email}</option>
                ))}
              </select>
            </div>

            <div className="space-y-3">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/60">
                2. Choose Field
              </label>
              <div className="grid gap-2">
                <ToolButton
                  icon={PenTool}
                  label="Signature"
                  type="SIGNATURE"
                  isActive={activeTool === "SIGNATURE"}
                  onClick={() => setActiveTool(activeTool === "SIGNATURE" ? null : "SIGNATURE")}
                />
                <ToolButton
                  icon={Type}
                  label="Text Field"
                  type="TEXT"
                  isActive={activeTool === "TEXT"}
                  onClick={() => setActiveTool(activeTool === "TEXT" ? null : "TEXT")}
                />
                <ToolButton
                  icon={Calendar}
                  label="Date Field"
                  type="DATE"
                  isActive={activeTool === "DATE"}
                  onClick={() => setActiveTool(activeTool === "DATE" ? null : "DATE")}
                />
              </div>
            </div>

            <div className="mt-auto p-4 rounded-xl bg-accent/5 border border-accent/10">
              <div className="flex gap-2 text-accent">
                <Info size={16} className="shrink-0 mt-0.5" />
                <p className="text-[11px] leading-tight">
                  Select a tool, then click anywhere on the document to place a field for the active signer.
                </p>
              </div>
            </div>
          </aside>

          {/* Center: Canvas Area */}
          <main className="flex-1 overflow-auto bg-stone-100/50 flex justify-center">
            {document && (
              <PDFViewer
                fileUrl={`/api/v1/documents/${id}/file`}
                onFieldPlace={handleFieldPlace}
              />
            )}
          </main>

          {/* Right Sidebar: Field Details */}
          <aside className="w-64 border-l bg-card p-4 shrink-0">
             <div className="space-y-6">
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/60">
                  Field Properties
                </label>

                {selectedField ? (
                  <div className="space-y-5">
                    <div className="p-3 rounded-lg bg-stone-50 border space-y-1">
                      <p className="text-[10px] text-muted-foreground uppercase font-bold">Type</p>
                      <p className="text-sm font-semibold text-primary">{selectedField.type}</p>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-[10px] uppercase font-bold text-muted-foreground">Assign To</Label>
                      <select
                        className="w-full rounded-lg border bg-stone-50 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-accent/20"
                        value={selectedField.signerId}
                        onChange={(e) => updateField(selectedField.id, { signerId: e.target.value })}
                      >
                        {signers.map(s => (
                          <option key={s.id} value={s.id}>{s.email}</option>
                        ))}
                      </select>
                    </div>

                    <div className="pt-4 border-t">
                      <Button
                        variant="ghost"
                        className="w-full text-destructive hover:bg-destructive/10 hover:text-destructive flex items-center justify-center gap-2"
                        onClick={() => removeField(selectedField.id)}
                      >
                        <Trash2 size={16} />
                        Delete Field
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <div className="p-3 rounded-full bg-stone-50 mb-3">
                      <Info size={24} className="text-stone-300" />
                    </div>
                    <p className="text-sm text-muted-foreground px-4">
                      Select a placed field on the document to view or edit its properties.
                    </p>
                  </div>
                )}
             </div>
          </aside>
        </div>
      </div>
    </ProtectedRoute>
  )
}

function ToolButton({ icon: Icon, label, isActive, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 w-full p-3 rounded-xl border transition-all group",
        isActive
          ? "bg-accent text-accent-foreground border-accent shadow-md scale-[1.02]"
          : "bg-card border-stone-200 hover:bg-stone-50 hover:border-accent/40 text-primary"
      )}
    >
      <div className={cn(
        "p-2 rounded-lg transition-colors",
        isActive ? "bg-white/20" : "bg-stone-100 group-hover:bg-accent/10 group-hover:text-accent"
      )}>
        <Icon size={18} />
      </div>
      <span className="text-sm font-medium">{label}</span>
    </button>
  )
}
