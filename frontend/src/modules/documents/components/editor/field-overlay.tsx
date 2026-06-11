"use client"

import { useEditorStore } from "@/store/use-editor-store"
import { FieldItem } from "./field-item"

interface FieldOverlayProps {
  pageNumber: number
}

export function FieldOverlay({ pageNumber }: FieldOverlayProps) {
  const fields = useEditorStore((state) => state.fields)
  const pageFields = fields.filter((f) => f.pageNumber === pageNumber)

  return (
    <div className="absolute inset-0 pointer-events-none">
      {pageFields.map((field) => (
        <FieldItem key={field.id} field={field} />
      ))}
    </div>
  )
}
