import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,  // ✅ Отключить проверки при билде
  },
  typescript: {
    ignoreBuildErrors: true,  // ✅ Игнорировать TypeScript ошибки
  },
}

export default nextConfig