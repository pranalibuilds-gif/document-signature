"use client"

import { useState, useRef } from "react"
import { useEditorStore, EditorField } from "@/store/use-editor-store"
import { cn } from "@/lib/utils"
import { Trash2, PenTool, Type, Calendar, Check } from "lucide-react"

interface FieldItemProps {
  field: EditorField
  onInteract?: (fieldId: string) => void
}

export function FieldItem({ field, onInteract }: FieldItemProps) {
  const { selectedFieldId, selectField, removeField, updateField } = useEditorStore()
  const isSelected = selectedFieldId === field.id
  const isFilled = !!field.value
  const [isDragging, setIsDragging] = useState(false)
  const itemRef = useRef<HTMLDivElement>(null)

  const icons = {
    SIGNATURE: PenTool,
    TEXT: Type,
    DATE: Calendar,
  }
  const Icon = icons[field.type]

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    removeField(field.id)
  }

  // Simple drag-to-move implementation
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!isSelected) {
      selectField(field.id)
      return
    }

    setIsDragging(true)

    const startX = e.clientX
    const startY = e.clientY
    const startFieldX = field.x
    const startFieldY = field.y

    const pageElement = itemRef.current?.parentElement
    if (!pageElement) return
    const rect = pageElement.getBoundingClientRect()

    const onMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = ((moveEvent.clientX - startX) / rect.width) * 100
      const deltaY = ((moveEvent.clientY - startY) / rect.height) * 100

      const newX = Math.max(0, Math.min(100, startFieldX + deltaX))
      const newY = Math.max(0, Math.min(100, startFieldY + deltaY))

      updateField(field.id, { x: newX, y: newY })
    }

    const onMouseUp = () => {
      setIsDragging(false)
      document.removeEventListener("mousemove", onMouseMove)
      document.removeEventListener("mouseup", onMouseUp)
    }

    document.addEventListener("mousemove", onMouseMove)
    document.addEventListener("mouseup", onMouseUp)
  }

  return (
    <div
      ref={itemRef}
      className={cn(
        "absolute pointer-events-auto cursor-grab active:cursor-grabbing group flex items-center gap-2 border-2 transition-all",
        isSelected
          ? "border-accent bg-accent/10 shadow-lg z-20"
          : isFilled
            ? "border-emerald-500 bg-emerald-50/30 shadow-sm z-10"
            : "border-primary/40 bg-primary/5 hover:border-primary/60 hover:bg-primary/10 z-10",
        isDragging && "opacity-80 scale-105 shadow-2xl"
      )}
      style={{
        left: `${field.x}%`,
        top: `${field.y}%`,
        width: `${field.width}px`,
        height: `${field.height}px`,
        transform: "translate(-50%, -50%)",
      }}
      onMouseDown={handleMouseDown}
      onClick={(e) => {
        e.stopPropagation();
        if (isSelected && onInteract) {
          onInteract(field.id);
        } else {
          selectField(field.id);
        }
      }}
    >
      <div className="flex h-full w-full items-center justify-center relative select-none">
        {isFilled ? (
          <div className="flex flex-col items-center px-1 overflow-hidden w-full relative">
             <span className={cn(
               "text-xs text-primary truncate w-full text-center px-1",
               field.type === "SIGNATURE" && "font-serif italic"
             )}>
               {field.value}
             </span>
             <div className="absolute -top-3 -right-3 bg-emerald-500 text-white rounded-full p-0.5 shadow-sm border border-white">
                <Check size={8} />
             </div>
          </div>
        ) : (
          <>
            <Icon size={16} className={isSelected ? "text-accent" : "text-primary/60"} />
            <span className="text-[9px] font-bold uppercase truncate px-1 text-primary/80">
              {field.type}
            </span>
          </>
        )}

        {isSelected && !isDragging && (
          <button
            onClick={handleDelete}
            className="absolute -top-3 -right-3 p-1 rounded-full bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90 z-30"
          >
            <Trash2 size={12} />
          </button>
        )}

        {isSelected && (
          <>
            <div className="absolute -top-1 -left-1 w-2 h-2 bg-accent rounded-full" />
            <div className="absolute -top-1 -right-1 w-2 h-2 bg-accent rounded-full" />
            <div className="absolute -bottom-1 -left-1 w-2 h-2 bg-accent rounded-full" />
            <div className="absolute -bottom-1 -right-1 w-2 h-2 bg-accent rounded-full" />
          </>
        )}
      </div>
    </div>
  )
}
