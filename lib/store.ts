// lib/store.ts
import { create } from 'zustand'
import { devtools } from 'zustand/middleware'

interface TranscriptionState {
  files: File[]
  status: string
  progress: number
  addFile: (file: File) => void
  setStatus: (status: string) => void
}

export const useTranscriptionStore = create<TranscriptionState>()(
  devtools(
    (set) => ({
      files: [],
      status: 'idle',
      progress: 0,
      addFile: (file) => set((state) => ({ files: [...state.files, file] })),
      setStatus: (status) => set({ status }),
    }),
    { name: 'AISOLAR-Store' }
  )
)