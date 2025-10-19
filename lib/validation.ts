// ==========================================
// FILE: lib/validation.ts
// ==========================================
const allowed = [
  'video/mp4',
  'video/avi',
  'video/x-msvideo',
  'video/quicktime',
  'video/x-matroska',
  'video/webm',
  'audio/mpeg',
  'audio/mp3',
  'audio/wav',
  'audio/ogg',
  'audio/m4a',
  'audio/x-m4a',
  'audio/aac'
]

export function validateFile(
  file: File,
  maxMB = 500
): { ok: true } | { ok: false; error: string } {
  const sizeMB = file.size / 1024 / 1024
  if (sizeMB > maxMB) {
    return {
      ok: false,
      error: `Файл слишком большой (${sizeMB.toFixed(1)}MB). Лимит ${maxMB}MB.`
    }
  }
  if (!allowed.includes(file.type) && !file.name.match(/\.(avi|mp4|mov|mkv|webm)$/i)) {
    return {
      ok: false,
      error: `Неподдерживаемый тип: ${file.type || 'unknown'}`
    }
  }
  return { ok: true }
}

