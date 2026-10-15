# AstroBuddy (frontend, stage 1)

Next.js 14 (App Router), TypeScript, Tailwind CSS.

## Run locally
```bash
npm install
cp .env.example .env.local     # then set NEXT_PUBLIC_API_BASE_URL
npm run dev                    # http://localhost:3000
npm run typecheck
npm run build && npm start     # production check
```
Requires Node 18.18+.

## What works in stage 1
- Dashboard, grouped sidebar, mobile drawer, profile menu, settings
- Birth form with validation, API client, typed services, loading/error/retry states
- SVG chart wheel that draws only what the API returns
- 13 feature routes exist as "Not built yet" pages listing the services they will use

## What is not connected
No backend ships with this project. Endpoint paths in `src/lib/api/services.ts` are assumptions;
change them to match your API. Nothing is calculated in the browser, and there is no login.
AI-provider keys must stay on the backend. `NEXT_PUBLIC_*` values are visible to every visitor.

## Structure
```
src/app            routes (dashboard, settings, [feature] placeholders)
src/components     layout/, chart/, ui/, forms
src/context        birth details state
src/hooks          useApiAction (loading, error, retry)
src/lib/api        client.ts, types.ts, services.ts
src/lib/nav.ts     the 13 features, grouped
```

## Backend (added in stage 2)
A FastAPI backend lives in `backend/`. See `backend/README.md` for Windows PowerShell setup, tests, the
verification procedure and licensing notes. Set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1`.
