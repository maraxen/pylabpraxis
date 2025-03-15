import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import { fileURLToPath } from 'url'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@features': path.resolve(__dirname, './src/features'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@store': path.resolve(__dirname, './src/store'),
      '@config': path.resolve(__dirname, './src/config'),
      '@assets': path.resolve(__dirname, './src/shared/assets'),
      '@styles': path.resolve(__dirname, './src/styles'),
      '@types': path.resolve(__dirname, './src/shared/types'),
      '@services': path.resolve(__dirname, './src/services'),
      '@hooks': path.resolve(__dirname, './src/shared/hooks'),
      '@recipes': path.resolve(__dirname, './src/shared/recipes'),
      '@praxis-ui': path.resolve(__dirname, './src/shared/components/ui'),
      '@templates': path.resolve(__dirname, './src/shared/components/ui/templates'),
      '@layouts': path.resolve(__dirname, './src/shared/components/ui/layouts'),
      '@pages': path.resolve(__dirname, './src/shared/components/ui/pages'),
      '@shared-styles': path.resolve(__dirname, './src/shared/styles'),
      '@utils': path.resolve(__dirname, './src/shared/utils'),
      '@protocols': path.resolve(__dirname, './src/features/protocols'),
      '@homeDashboard': path.resolve(__dirname, './src/features/homeDashboard'),
      '@settings': path.resolve(__dirname, './src/features/settings'),
      '@users': path.resolve(__dirname, './src/features/users'),
      '@vixn': path.resolve(__dirname, './src/features/vixn'),
      '@labAssets': path.resolve(__dirname, './src/features/labassets'),
      '@docs': path.resolve(__dirname, './src/features/docs'),
    }
  }
})
