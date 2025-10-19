// app/api/health/route.ts
import { NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function GET() {
  try {
    // Проверяем ffmpeg
    await execAsync('ffmpeg -version')
    await execAsync('ffprobe -version')
    
    // Проверяем OpenAI API
    const hasApiKey = !!process.env.OPENAI_API_KEY
    
    return NextResponse.json({
      status: 'healthy',
      services: {
        ffmpeg: 'ok',
        ffprobe: 'ok',
        openai: hasApiKey ? 'configured' : 'missing'
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    return NextResponse.json(
      { 
        status: 'unhealthy',
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    )
  }
}