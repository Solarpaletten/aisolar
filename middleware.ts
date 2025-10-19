// app/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const rateLimit = new Map<string, { count: number; resetTime: number }>()

export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/api/transcribe')) {
    // Получаем IP из headers (работает в Next.js 15)
    const ip = request.headers.get('x-forwarded-for') || 
               request.headers.get('x-real-ip') || 
               'unknown'
    
    const now = Date.now()
    const limit = rateLimit.get(ip)

    if (limit && limit.resetTime > now) {
      if (limit.count >= 10) { // 10 запросов в час
        return NextResponse.json(
          { error: 'Rate limit exceeded' },
          { status: 429 }
        )
      }
      limit.count++
    } else {
      rateLimit.set(ip, { count: 1, resetTime: now + 3600000 }) // 1 час
    }
  }
  
  return NextResponse.next()
}

export const config = {
  matcher: '/api/:path*',
}