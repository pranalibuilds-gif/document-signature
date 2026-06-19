import { create } from "zustand"

export interface SigningField {
  id: string
  type: "SIGNATURE" | "TEXT" | "DATE"
  pageNumber: number
  x: number
  y: number
  width: number
  height: number
  required: boolean
  value?: string
}

interface SigningState {
  document: any | null
  signer: any | null
  fields: SigningField[]
  values: Record<string, string>

  setSession: (document: any, signer: any, fields: SigningField[]) => void
  updateValue: (fieldId: string, value: string) => void
  isComplete: () => boolean
}

export const useSigningStore = create<SigningState>((set, get) => ({
  document: null,
  signer: null,
  fields: [],
  values: {},

  setSession: (document, signer, fields) => {
    const initialValues: Record<string, string> = {}
    fields.forEach(f => {
      if (f.value) {
        initialValues[f.id] = f.value
      }
    })
    set({ document, signer, fields, values: initialValues })
  },

  updateValue: (fieldId, value) => set((state) => ({
    values: { ...state.values, [fieldId]: value }
  })),

  isComplete: () => {
    const { fields, values } = get()
    return fields.filter(f => f.required).every(f => !!values[f.id]?.trim())
  }
}))
