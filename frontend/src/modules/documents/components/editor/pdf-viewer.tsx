"use client"

import { useState } from "react"
import { Document, Page, pdfjs } from "react-pdf"
import { Loader2 } from "lucide-react"
import { useEditorStore } from "@/store/use-editor-store"
import { FieldOverlay } from "./field-overlay"

// Setup the worker for react-pdf
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`

interface PDFViewerProps {
  fileUrl: string
  onFieldPlace: (pageNumber: number, x: number, y: number) => void
}

/**
 * PDFViewer Component
 * Renders an interactive PDF document allowing users to place signature fields.
 * Uses percentage-based coordinates to ensure responsiveness across different screen sizes.
 */
export function PDFViewer({ fileUrl, onFieldPlace }: PDFViewerProps) {
  const [numPages, setNumPages] = useState<number>(0)
  const zoom = useEditorStore((state) => state.zoom)

  /**
   * PDF Load Callback
   * Triggered when the PDF binary is successfully fetched and parsed.
   */
  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages)
  }

  /**
   * Coordinate Calculation
   * Captures the click event on a specific PDF page.
   * Converts the local mouse pixel coordinates into percentage-based (0-100) coordinates.
   * Percentage-based values allow the field to stay correctly positioned regardless of zoom or viewport changes.
   */
  const handlePageClick = (e: React.MouseEvent, pageNumber: number) => {
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()

    // Calculate percentage from top-left (0,0)
    const x = ((e.clientX - rect.left) / rect.width) * 100
    const y = ((e.clientY - rect.top) / rect.height) * 100

    onFieldPlace(pageNumber, x, y)
  }

  return (
    <div className="flex flex-col items-center gap-8 py-8 w-full">
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
        {/* Render each page of the document */}
        {Array.from(new Array(numPages), (el, index) => (
          <div key={`page_${index + 1}`} className="relative shadow-2xl border">
            <div
              className="cursor-crosshair"
              onClick={(e) => handlePageClick(e, index + 1)}
            >
              <Page
                pageNumber={index + 1}
                scale={zoom} // Dynamic scaling based on global editor zoom
                renderAnnotationLayer={false}
                renderTextLayer={false} // Disabled to improve performance during editing
              />
            </div>
            {/* Renders the interactive fields (boxes) on top of the PDF page */}
            <FieldOverlay pageNumber={index + 1} />

            <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] text-muted-foreground font-medium bg-white/80 px-2 py-0.5 rounded-full border">
               PAGE {index + 1} OF {numPages}
            </div>
          </div>
        ))}
      </Document>
    </div>
  )
}
