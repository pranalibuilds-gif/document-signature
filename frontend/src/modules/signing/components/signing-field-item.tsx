"use client"

import { useState } from "react"
import { SigningField, useSigningStore } from "@/store/use-signing-store"
import { cn } from "@/lib/utils"
import { PenTool, Type, Calendar, Check } from "lucide-react"
import { SignatureModal } from "./signature-modal"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface SigningFieldItemProps {
  field: SigningField
}

export function SigningFieldItem({ field }: SigningFieldItemProps) {
  const { values, updateValue } = useSigningStore()
  const value = values[field.id] || ""
  const isCompleted = !!value.trim()

  const [isSigModalOpen, setIsSigModalOpen] = useState(false)
  const [isTextModalOpen, setIsTextModalOpen] = useState(false)
  const [textInput, setTextValue] = useState(value)

  const handleInput = () => {
    if (field.type === "DATE") {
      const today = new Date().toISOString().split('T')[0]
      updateValue(field.id, today)
      return
    }

    if (field.type === "SIGNATURE") {
      setIsSigModalOpen(true)
      return
    }

    if (field.type === "TEXT") {
      setTextValue(value)
      setIsTextModalOpen(true)
      return
    }
  }

  const onConfirmSignature = (name: string, font: string) => {
    updateValue(field.id, name)
  }

  const onConfirmText = () => {
    updateValue(field.id, textInput)
    setIsTextModalOpen(false)
  }

  return (
    <>
      <div
        className={cn(
          "absolute pointer-events-auto cursor-pointer flex flex-col items-center justify-center border-2 transition-all",
          isCompleted
            ? "border-emerald-500 bg-emerald-50/50"
            : "border-accent bg-accent/5 hover:bg-accent/10 shadow-sm",
          field.required && !isCompleted && "ring-1 ring-accent/20"
        )}
        style={{
          left: `${field.x}%`,
          top: `${field.y}%`,
          width: `${field.width}px`,
          height: `${field.height}px`,
          transform: "translate(-50%, -50%)",
        }}
        onClick={handleInput}
      >
        {isCompleted ? (
          <div className="flex flex-col items-center px-1 overflow-hidden w-full relative">
            {field.type === "SIGNATURE" ? (
               <span className="text-sm font-serif italic text-primary truncate w-full text-center px-2">
                 {value}
               </span>
            ) : (
              <span className="text-xs text-primary truncate w-full text-center px-2">
                {value}
              </span>
            )}
            <div className="absolute -top-3 -right-3 bg-emerald-500 text-white rounded-full p-0.5 shadow-sm border border-white">
              <Check size={10} />
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-0.5 opacity-60">
             {field.type === "SIGNATURE" && <PenTool size={14} className="text-accent" />}
             {field.type === "TEXT" && <Type size={14} className="text-accent" />}
             {field.type === "DATE" && <Calendar size={14} className="text-accent" />}
             <span className="text-[8px] font-bold text-accent uppercase">
               {field.required ? "Required" : "Optional"}
             </span>
          </div>
        )}
      </div>

      <SignatureModal
        isOpen={isSigModalOpen}
        onClose={() => setIsSigModalOpen(false)}
        onConfirm={onConfirmSignature}
        initialName={value}
      />

      <Dialog open={isTextModalOpen} onOpenChange={setIsTextModalOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Enter Information</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="text-input" className="mb-2 block text-xs">Text Field</Label>
            <Input
              id="text-input"
              value={textInput}
              onChange={(e) => setTextValue(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && onConfirmText()}
              autoFocus
            />
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setIsTextModalOpen(false)}>Cancel</Button>
            <Button className="btn-accent" onClick={onConfirmText}>Save</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
