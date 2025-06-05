import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    rollupOptions: {
      input: {
        // Global CSS
        main: resolve(__dirname, 'src/style.css'),
        // Per-app JavaScript
        product_data_form: resolve(__dirname, 'product_data_form/static/src/main.ts'),
      },
      output: {
        dir: 'dist',
        entryFileNames: `js/[name].js`,
        assetFileNames: 'css/main.css',
      }
    }
  }
})
