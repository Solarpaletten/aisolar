// ==========================================
// FILE: lib/exportSRT.ts
// ==========================================
export function textToSRT(text: string, stepSec = 4): string {
    const sentences = text.split(/(?<=[.!?])\s+/).filter(Boolean)
    const toTS = (s: number) => {
      const hh = String(Math.floor(s / 3600)).padStart(2, '0')
      const mm = String(Math.floor((s % 3600) / 60)).padStart(2, '0')
      const ss = String(Math.floor(s % 60)).padStart(2, '0')
      const ms = '000'
      return `${hh}:${mm}:${ss},${ms}`
    }
    let srt = ''
    let t = 0
    sentences.forEach((sent, i) => {
      const start = toTS(t)
      const end = toTS(t + stepSec)
      srt += `${i + 1}\n${start} --> ${end}\n${sent}\n\n`
      t += stepSec
    })
    return srt.trim()
  }
  
  export type Segment = { start: number; end: number; text: string; speaker?: string }
  
  export function segmentsToSRT(segments: Segment[]): string {
    const toTS = (s: number) => {
      const hh = String(Math.floor(s / 3600)).padStart(2, '0')
      const mm = String(Math.floor((s % 3600) / 60)).padStart(2, '0')
      const ss = String(Math.floor(s % 60)).padStart(2, '0')
      const ms = '000'
      return `${hh}:${mm}:${ss},${ms}`
    }
    return segments
      .map((seg, i) => {
        const line = seg.speaker ? `${seg.speaker}: ${seg.text}` : seg.text
        return `${i + 1}\n${toTS(seg.start)} --> ${toTS(seg.end)}\n${line}`
      })
      .join('\n\n')
  }
  
  