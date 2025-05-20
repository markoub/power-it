/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Only enable static exports for production builds
  ...(process.env.NODE_ENV === 'production' ? {
    output: 'export',
    distDir: 'build',
  } : {}),
  
  // Webpack customizations removed as pptxgenjs is no longer used client-side
  // webpack: (config, { isServer, webpack }) => {
  //   if (!isServer) {
  //     config.resolve.fallback = {
  //       ...config.resolve.fallback,
  //       fs: false,
  //       net: false,
  //       tls: false,
  //       child_process: false,
  //       async_hooks: false,
  //       'node:fs': false,
  //       'node:fs/promises': false,
  //       'node:path': false,
  //       'node:os': false,
  //       'node:crypto': false,
  //       'node:stream': false,
  //       'node:https': false,
  //       'node:http': false,
  //       'node:url': false,
  //       'node:util': false,
  //       'node:zlib': false,
  //     };
  //   }
  //   config.plugins.push(
  //     new webpack.DefinePlugin({
  //       'process.env.IS_CLIENT': JSON.stringify(true),
  //       'process.env.IS_SERVER': JSON.stringify(false),
  //     })
  //   );
  //   return config;
  // },
}

export default nextConfig
