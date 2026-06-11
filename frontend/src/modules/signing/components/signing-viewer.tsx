"use client"

import { useState, useEffect, useRef } from "react"
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
  const [containerWidth, setContainerWidth] = useState<number>(0)
  const containerRef = useRef<HTMLDivElement>(null)

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages)
  }

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        // Subtract padding/margins
        const width = containerRef.current.clientWidth - 32
        setContainerWidth(Math.min(width, 1000)) // Max width for readability
      }
    }

    updateWidth()
    window.addEventListener("resize", updateWidth)
    return () => window.removeEventListener("resize", updateWidth)
  }, [])

  return (
    <div ref={containerRef} className="flex flex-col items-center gap-8 py-4 md:py-8 w-full max-w-5xl mx-auto px-4">
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
          <div key={`page_${index + 1}`} className="relative shadow-2xl border bg-white rounded-sm overflow-hidden">
            <Page
              pageNumber={index + 1}
              width={containerWidth || 300}
              renderAnnotationLayer={false}
              renderTextLayer={false}
            />
            <SigningFieldOverlay pageNumber={index + 1} />
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-[9px] text-muted-foreground font-bold bg-white/90 px-2 py-0.5 rounded-full border shadow-sm pointer-events-none">
               {index + 1} / {numPages}
            </div>
          </div>
        ))}
      </Document>
    </div>
  )
}
