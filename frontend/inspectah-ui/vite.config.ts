import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // Proxy specific backend admin API routes (not React routes)
      '/admin/sources': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin/ingestion': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin/agents': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin/agent-flows': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/admin/copiloto-fontes': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
    globals: true,
    css: true,
  },
});
