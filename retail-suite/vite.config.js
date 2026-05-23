import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import svgLoader from 'vite-svg-loader'
import vuetify from 'vite-plugin-vuetify'
import fs from 'fs'
import path from 'path'
import Icons from 'unplugin-icons/vite'
import dotenv from 'dotenv'
import { fileURLToPath } from 'url'
import { dirname } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

dotenv.config({ path: path.resolve(__dirname, '.env') })

const FRAPPE_URL = process.env.VITE_API_BASE_URL || process.env.VITE_FRAPPE_URL || process.env.VITE_FRAPPE_URL_LOCAL
const SOCKET_TARGET = process.env.VITE_SOCKET_URL
const SITE_NAME = process.env.VITE_SITE_NAME
const FRAPPE_HOST = process.env.VITE_FRAPPE_HOST
const CERTS_DIR = process.env.VITE_CERTS_DIR
const BUILD_FOR_FRAPPE = process.env.VITE_BUILD_FOR_FRAPPE === 'true'
const USE_FRAPPE_PROXY = process.env.VITE_USE_FRAPPE_PROXY !== 'false' && !!FRAPPE_URL
const CERT_KEY = FRAPPE_HOST && CERTS_DIR ? `${CERTS_DIR}/${FRAPPE_HOST}+1-key.pem` : null
const CERT_PEM = FRAPPE_HOST && CERTS_DIR ? `${CERTS_DIR}/${FRAPPE_HOST}+1.pem` : null
const HAS_CERTS = CERT_KEY && CERT_PEM && fs.existsSync(CERT_KEY) && fs.existsSync(CERT_PEM)

export default defineConfig({
  base: BUILD_FOR_FRAPPE ? '/assets/retail/retail_suite/' : '/',
  optimizeDeps: {
    include: ['feather-icons', 'highlight.js/lib/core', 'interactjs', 'qz-tray'],
    exclude: ['@iconify-json/lucide'],
    esbuildOptions: {
      plugins: [{
        name: 'ignore-icons',
        setup(build) {
          build.onResolve({ filter: /^~icons\// }, args => ({
            path: args.path, namespace: 'ignore-icons',
          }))
          build.onLoad({ filter: /.*/, namespace: 'ignore-icons' }, () => ({
            contents: 'export default {}', loader: 'js',
          }))
        }
      }]
    }
  },
  plugins: [
    vue(),
    vuetify({ autoImport: true }),
    svgLoader(),
    Icons({ compiler: 'vue3', autoInstall: true }),
  ],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
  server: USE_FRAPPE_PROXY ? {
    allowedHosts: true,
    port: 5173,
    host: '0.0.0.0',
    ...(HAS_CERTS ? {
      https: {
        key: fs.readFileSync(CERT_KEY),
        cert: fs.readFileSync(CERT_PEM),
      },
    } : {}),
    proxy: {
      '^/(app|api|assets|files|printview|login|logout)': {
        target: FRAPPE_URL,
        changeOrigin: true,
        ws: true,
        secure: false,
        cookieDomainRewrite: FRAPPE_HOST,
      },
      '/socket.io': {
        target: SOCKET_TARGET || FRAPPE_URL,
        ws: true,
        changeOrigin: true,
        secure: false,
        rewriteWsOrigin: true,
        headers: SITE_NAME ? { 'x-frappe-site-name': SITE_NAME } : undefined,
      },
    },
  } : undefined,
  build: {
    outDir: BUILD_FOR_FRAPPE ? path.resolve(__dirname, '../retail/public/retail_suite') : path.resolve(__dirname, 'dist'),
    emptyOutDir: true,
    assetsDir: 'assets',
    rollupOptions: {
      external: (id) => id.startsWith('~icons/'),
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          utils: ['idb']
        }
      }
    }
  }
})
