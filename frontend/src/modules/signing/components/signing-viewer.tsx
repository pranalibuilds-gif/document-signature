"use client"

import { useState } from "react"
import { Document, Page, pdfjs } from "react-pdf"
import { Loader2 } from "lucide-react"
import { useSigningStore } from "@/store/use-signing-store"
import { SigningFieldOverlay } from "./signing-field-overlay"

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`

interface SigningViewerProps {
  fileUrl: string
}

export function SigningViewer({ fileUrl }: SigningViewerProps) {
  const [numPages, setNumPages] = useState<number>(0)

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages)
  }

  return (
    <div className="flex flex-col items-center gap-8 py-8 w-full max-w-4xl mx-auto">
      <Document
        file={fileUrl}
        onLoadSuccess={onDocumentLoadSuccess}
        loading={
          <div className="flex items-center justify-center p-12">
            <Loader2 className="animate-spin text-accent" size={32} />
          </div>
        }
        className="flex flex-col items-center gap-8"
      >
        {Array.from(new Array(numPages), (el, index) => (
          <div key={`page_${index + 1}`} className="relative shadow-2xl border bg-white">
            <Page
              pageNumber={index + 1}
              scale={1.2}
              renderAnnotationLayer={false}
              renderTextLayer={false}
            />
            <SigningFieldOverlay pageNumber={index + 1} />
            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] text-muted-foreground font-medium bg-white/80 px-2 py-0.5 rounded-full border">
               PAGE {index + 1} OF {numPages}
            </div>
          </div>
        ))}
      </Document>
    </div>
  )
}
