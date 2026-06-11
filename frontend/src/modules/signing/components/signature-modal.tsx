"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"

interface SignatureModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: (name: string, font: string) => void
  initialName?: string
}

const FONT_STYLES = [
  { name: "Serif", class: "font-serif italic" },
  { name: "Cursive", class: "font-serif tracking-tight font-light italic" }, // Mock cursive with serif
  { name: "Modern", class: "font-sans font-medium italic" },
  { name: "Elegant", class: "font-serif font-extralight tracking-widest italic" },
]

export function SignatureModal({ isOpen, onClose, onConfirm, initialName = "" }: SignatureModalProps) {
  const [name, setName] = useState(initialName)
  const [selectedFont, setSelectedFont] = useState(FONT_STYLES[0].name)

  const handleConfirm = () => {
    if (name.trim()) {
      onConfirm(name, selectedFont)
      onClose()
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create Your Signature</DialogTitle>
          <DialogDescription>
            Type your full name exactly as you wish it to appear on the document.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          <div className="space-y-2">
            <Label htmlFor="sig-name">Full Name</Label>
            <Input
              id="sig-name"
              placeholder="e.g. Pranali More"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>

          <div className="space-y-3">
            <Label>Choose a Style</Label>
            <div className="grid grid-cols-1 gap-2">
              {FONT_STYLES.map((style) => (
                <button
                  key={style.name}
                  onClick={() => setSelectedFont(style.name)}
                  className={cn(
                    "w-full p-4 text-left border rounded-xl transition-all hover:bg-stone-50",
                    selectedFont === style.name
                      ? "border-accent ring-1 ring-accent bg-accent/5"
                      : "border-stone-200"
                  )}
                >
                  <div className="flex justify-between items-center">
                    <span className={cn("text-xl text-primary truncate", style.class)}>
                      {name || "Your Signature"}
                    </span>
                    <span className="text-[10px] text-muted-foreground uppercase font-bold">
                      {style.name}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button
            className="btn-accent"
            onClick={handleConfirm}
            disabled={!name.trim()}
          >
            Adopt and Sign
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
