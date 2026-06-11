"use client"

import { useSigningStore } from "@/store/use-signing-store"
import { SigningFieldItem } from "./signing-field-item"

interface SigningFieldOverlayProps {
  pageNumber: number
}

export function SigningFieldOverlay({ pageNumber }: SigningFieldOverlayProps) {
  const fields = useSigningStore((state) => state.fields)
  const pageFields = fields.filter((f) => f.pageNumber === pageNumber)

  return (
    <div className="absolute inset-0 pointer-events-none">
      {pageFields.map((field) => (
        <SigningFieldItem key={field.id} field={field} />
      ))}
    </div>
  )
}
