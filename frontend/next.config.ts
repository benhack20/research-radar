import type { NextConfig } from "next";

/** @type {import('next').NextConfig} */
const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
  // TODO: eslint 配置，后续需要设置为 false 并手动检查所有代码确保没有语法错误
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
