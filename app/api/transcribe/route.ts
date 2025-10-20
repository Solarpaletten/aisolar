// ==========================================
// FILE: app/api/transcribe/route.ts (WITH CHUNKING)
// ==========================================
import { NextRequest } from 'next/server'
import { tmpdir } from 'os'
import { promises as fs } from 'fs'
import { createReadStream } from 'fs'
import path from 'path'
import { spawn } from 'child_process'
import OpenAI from 'openai'

export const runtime = 'nodejs'
export const preferredRegion = ['fra1', 'arn1', 'ams1']

const MAX_FILE_SIZE_MB = 20
const CHUNK_DURATION_SEC = 300

function ndjson(out: ReadableStreamDefaultController, obj: any) {
  try {
    if (out) {
      out.enqueue(new TextEncoder().encode(JSON.stringify(obj) + '\n'))
    }
  } catch (err) {
    console.warn('Stream closed, skipping enqueue:', err)
  }
}

function formatElapsedTime(ms: number): string {
  const totalSec = Math.floor(ms / 1000)
  const min = Math.floor(totalSec / 60)
  const sec = totalSec % 60
  return `${min}м ${sec}с`
}

async function saveBlobToTmp(file: File): Promise<string> {
  const arrayBuffer = await file.arrayBuffer()
  const buffer = Buffer.from(arrayBuffer)
  const safeName = file.name.replace(/[^a-zA-Z0-9.-]/g, '_')
  const p = path.join(tmpdir(), `${Date.now()}-${safeName}`)
  await fs.writeFile(p, buffer)
  return p
}

async function getAudioDuration(filePath: string): Promise<number> {
  return new Promise((resolve, reject) => {
    const proc = spawn('ffprobe', [
      '-v', 'error',
      '-show_entries', 'format=duration',
      '-of', 'default=noprint_wrappers=1:nokey=1',
      filePath
    ])

    let output = ''
    proc.stdout.on('data', (data) => { output += data.toString() })
    proc.on('close', (code) => {
      if (code === 0) {
        const duration = parseFloat(output.trim())
        resolve(isNaN(duration) ? 0 : duration)
      } else {
        reject(new Error('ffprobe failed'))
      }
    })
  })
}

async function ffmpegToWav(inputPath: string): Promise<string> {
  const out = path.join(tmpdir(), `${path.parse(inputPath).name}.wav`)
  await new Promise<void>((resolve, reject) => {
    const args = ['-i', inputPath, '-vn', '-ac', '1', '-ar', '16000', '-f', 'wav', out]
    const proc = spawn('ffmpeg', args)
    proc.on('error', reject)
    proc.on('close', (code) =>
      code === 0 ? resolve() : reject(new Error(`ffmpeg failed: ${code}`))
    )
  })
  return out
}

async function splitAudioToChunks(inputPath: string, chunkSeconds: number): Promise<string[]> {
  const outDir = path.join(tmpdir(), `chunks-${Date.now()}`)
  await fs.mkdir(outDir, { recursive: true })

  await new Promise<void>((resolve, reject) => {
    const args = [
      '-i', inputPath,
      '-f', 'segment',
      '-segment_time', chunkSeconds.toString(),
      '-c', 'copy',
      path.join(outDir, 'chunk%03d.wav')
    ]
    const proc = spawn('ffmpeg', args)
    proc.on('error', reject)
    proc.on('close', (code) =>
      code === 0 ? resolve() : reject(new Error('ffmpeg split failed'))
    )
  })

  const files = await fs.readdir(outDir)
  return files
    .filter(f => f.endsWith('.wav'))
    .sort()
    .map(f => path.join(outDir, f))
}

async function transcribeOpenAI(
  wavPath: string,
  language?: string
): Promise<{ text: string }> {
  const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
  const resp = await client.audio.transcriptions.create({
    file: createReadStream(wavPath) as any,
    model: 'whisper-1',
    language: language && language !== 'auto' ? language : undefined
  })
  return { text: resp.text }
}

async function maybeTranslate(text: string, target?: string): Promise<string> {
  if (!target || !target.trim()) return text
  const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
  const r = await client.chat.completions.create({
    model: 'gpt-4o-mini',
    messages: [
      {
        role: 'system',
        content: `Translate the following text to ${target}. Return only the translated text.`
      },
      { role: 'user', content: text }
    ],
    temperature: 0
  })
  return r.choices?.[0]?.message?.content?.toString?.() || text
}

export async function POST(request: NextRequest) {
  const stream = new ReadableStream({
    async start(controller) {
      const startTime = Date.now()
      const tempFiles: string[] = []

      try {
        ndjson(controller, { type: 'progress', message: '⏳ Подготовка файла...' })
        
        const formData = await request.formData()
        const file = formData.get('file') as File
        const engine = (formData.get('engine') as string) || 'openai'
        const language = (formData.get('language') as string) || 'auto'
        const translateTo = (formData.get('translateTo') as string) || ''

        if (!file) {
          ndjson(controller, { type: 'error', message: 'No file provided' })
          controller.close()
          return
        }

        const fileSizeMB = file.size / (1024 * 1024)
        const inputPath = await saveBlobToTmp(file)
        tempFiles.push(inputPath)

        ndjson(controller, { type: 'progress', message: '🔄 Конвертация в WAV...' })
        const wavPath = await ffmpegToWav(inputPath)
        tempFiles.push(wavPath)

        const duration = await getAudioDuration(wavPath)
        const needsChunking = fileSizeMB > 15 || duration > 300

        let wavFiles: string[] = []

        if (needsChunking) {
          ndjson(controller, {
            type: 'progress',
            message: `📦 Разделение на части (файл ${fileSizeMB.toFixed(1)} MB, ${Math.floor(duration / 60)} минут)...`
          })
          wavFiles = await splitAudioToChunks(wavPath, CHUNK_DURATION_SEC)
          tempFiles.push(...wavFiles)
        } else {
          wavFiles = [wavPath]
        }

        if (wavFiles.length > 1) {
          ndjson(controller, {
            type: 'chunk_info',
            totalChunks: wavFiles.length
          })
        }

        ndjson(controller, { type: 'progress', message: '🎙️ Распознавание речи...' })

        // Транскрибация всех чанков
        let fullText = ''
        
        for (let i = 0; i < wavFiles.length; i++) {
          const chunkPath = wavFiles[i]
          
          if (wavFiles.length > 1) {
            ndjson(controller, {
              type: 'chunk_start',
              currentChunk: i + 1,
              totalChunks: wavFiles.length,
              message: `▶️ Обработка чанка ${i + 1}/${wavFiles.length}`
            })
          }
        
          const result = await transcribeOpenAI(chunkPath, language)
          
          if (fullText && result.text) {
            fullText += ' '
          }
          fullText += result.text
          
          if (wavFiles.length > 1) {
            ndjson(controller, { 
              type: 'chunk_complete',
              currentChunk: i + 1,
              totalChunks: wavFiles.length,
              message: `✅ Чанк ${i + 1}/${wavFiles.length} завершён`
            })
          }
          
          ndjson(controller, { type: 'partial', text: fullText })
        }

        if (translateTo) {
          ndjson(controller, { type: 'progress', message: '🌐 Перевод текста...' })
          fullText = await maybeTranslate(fullText, translateTo)
        }

        ndjson(controller, { type: 'final', text: fullText })
        ndjson(controller, {
          type: 'progress',
          message: `✅ Готово! (${formatElapsedTime(Date.now() - startTime)})`
        })

        for (const tmpFile of tempFiles) {
          await fs.unlink(tmpFile).catch(() => {})
        }
        
        if (needsChunking && wavFiles.length > 0) {
          const chunkDir = path.dirname(wavFiles[0])
          await fs.rm(chunkDir, { recursive: true, force: true }).catch(() => {})
        }

        controller.close()
      } catch (error: any) {
        console.error('Transcription error:', error)
        
        ndjson(controller, {
          type: 'error',
          message: error.message || 'Processing failed'
        })
        
        for (const tmpFile of tempFiles) {
          await fs.unlink(tmpFile).catch(() => {})
        }
        
        controller.close()
      }
    }
  })

  return new Response(stream, {
    headers: {
      'Content-Type': 'application/x-ndjson; charset=utf-8',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive'
    }
  })
}