# Retail Suite on Vercel

## Deploy
- Install dependencies: `npm install`
- Build: `npm run build`

## Environment
- `VITE_API_BASE_URL`
- `VITE_SOCKET_URL`
- `VITE_SITE_NAME`
- `VITE_QZ_CERT_URL` when you sign QZ Tray requests
- `VITE_QZ_SIGNATURE_URL` when you sign QZ Tray requests

## Notes
- This is the standalone Vue frontend.
- The app uses source code from GitHub and builds on each Vercel deployment.
- Client routes rewrite to `index.html` through `vercel.json`.
