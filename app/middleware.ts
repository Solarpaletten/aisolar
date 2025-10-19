// ==========================================
  // FILE: middleware.ts
  // ==========================================
  import { NextResponse } from 'next/server'
  import type { NextRequest } from 'next/server'
  
  const WINDOW_MS = 10 * 60 * 1000
  const LIMIT = 10
  const bucket = new Map<string, number[]>()
  
  export function middleware(req: NextRequest) {
    if (req.nextUrl.pathname.startsWith('/api/')) {
      const ip = req.ip || req.headers.get('x-forwarded-for') || 'unknown'
      const now = Date.now()
      const arr = bucket.get(ip) || []
      const recent = arr.filter((t) => now - t < WINDOW_MS)
      if (recent.length >= LIMIT) {
        const res = NextResponse.json(
          { error: 'Too many requests. Try again later.' },
          { status: 429 }
        )
        res.headers.set('X-RateLimit-Limit', String(LIMIT))
        res.headers.set('X-RateLimit-Remaining', '0')
        return res
      }
      recent.push(now)
      bucket.set(ip, recent)
      const res = NextResponse.next()
      res.headers.set('X-RateLimit-Limit', String(LIMIT))
      res.headers.set('X-RateLimit-Remaining', String(Math.max(0, LIMIT - recent.length)))
      return res
    }
    return NextResponse.next()
  }
  
  export const config = { matcher: ['/api/:path*'] }
  
 