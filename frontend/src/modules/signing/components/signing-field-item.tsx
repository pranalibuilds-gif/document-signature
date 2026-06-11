"use client"

import { useState } from "react"
import { SigningField, useSigningStore } from "@/store/use-signing-store"
import { cn } from "@/lib/utils"
import { PenTool, Type, Calendar, Check } from "lucide-react"

interface SigningFieldItemProps {
  field: SigningField
}

export function SigningFieldItem({ field }: SigningFieldItemProps) {
  const { values, updateValue } = useSigningStore()
  const value = values[field.id] || ""
  const isCompleted = !!value.trim()

  const handleInput = () => {
    if (field.type === "DATE") {
      const today = new Date().toISOString().split('T')[0]
      updateValue(field.id, today)
      return
    }

    const promptText = field.type === "SIGNATURE"
      ? "Type your full name to sign"
      : "Enter text"

    const newVal = prompt(promptText, value)
    if (newVal !== null) {
      updateValue(field.id, newVal)
    }
  }

  return (
    <div
      className={cn(
        "absolute pointer-events-auto cursor-pointer flex flex-col items-center justify-center border-2 transition-all",
        isCompleted
          ? "border-emerald-500 bg-emerald-50/50"
          : "border-accent bg-accent/5 hover:bg-accent/10 shadow-sm"
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
        <div className="flex flex-col items-center px-1 overflow-hidden">
          {field.type === "SIGNATURE" ? (
             <span className="text-sm font-serif italic text-primary truncate w-full text-center">
               {value}
             </span>
          ) : (
            <span className="text-xs text-primary truncate w-full text-center">
              {value}
            </span>
          )}
          <div className="absolute -top-2 -right-2 bg-emerald-500 text-white rounded-full p-0.5">
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
  )
}
