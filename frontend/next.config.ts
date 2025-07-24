import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'static.aminer.cn',
        port: '',
        pathname: '/**',
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `http://backend:8000/api/:path*`,
      },
    ];
  },
  // TODO: eslint 配置，后续需要设置为 false 并手动检查所有代码确保没有语法错误
  eslint: {
    ignoreDuringBuilds: true,
  },
  // TODO: typescript 配置，后续需要设置为 false 并手动检查所有代码确保没有语法错误
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
