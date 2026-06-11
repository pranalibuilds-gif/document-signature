import { create } from "zustand"

export type FieldType = "SIGNATURE" | "TEXT" | "DATE"

export interface EditorField {
  id: string
  type: FieldType
  signerId: string
  pageNumber: number
  x: number // percentage 0-100
  y: number // percentage 0-100
  width: number
  height: number
}

interface EditorState {
  currentSignerId: string | null
  activeTool: FieldType | null
  zoom: number
  fields: EditorField[]
  selectedFieldId: string | null

  setCurrentSigner: (id: string) => void
  setActiveTool: (tool: FieldType | null) => void
  setZoom: (zoom: number) => void
  setFields: (fields: EditorField[]) => void
  addField: (field: EditorField) => void
  removeField: (id: string) => void
  updateField: (id: string, updates: Partial<EditorField>) => void
  selectField: (id: string | null) => void
}

export const useEditorStore = create<EditorState>((set) => ({
  currentSignerId: null,
  activeTool: null,
  zoom: 1.0,
  fields: [],
  selectedFieldId: null,

  setCurrentSigner: (id) => set({ currentSignerId: id }),
  setActiveTool: (tool) => set({ activeTool: tool }),
  setZoom: (zoom) => set({ zoom }),
  setFields: (fields) => set({ fields }),
  addField: (field) => set((state) => ({ fields: [...state.fields, field] })),
  removeField: (id) => set((state) => ({
    fields: state.fields.filter((f) => f.id !== id),
    selectedFieldId: state.selectedFieldId === id ? null : state.selectedFieldId
  })),
  updateField: (id, updates) => set((state) => ({
    fields: state.fields.map((f) => f.id === id ? { ...f, ...updates } : f)
  })),
  selectField: (id) => set({ selectedFieldId: id }),
}))
