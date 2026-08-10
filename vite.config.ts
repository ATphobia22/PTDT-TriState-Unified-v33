import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // Required for Electron loadFile (relative asset paths)
  base: './',
  build: {
    outDir: 'dist',
    target: 'es2020',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    host: true,
  },
});
