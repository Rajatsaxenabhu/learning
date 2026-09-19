# GeoAgent frontend

Next.js 16 (App Router) + Tailwind v4 + shadcn/base-ui.

```
npm run dev     # http://localhost:3000
npm run build
```

Env (`.env`): `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`.

- `app/` routes (`/` landing, `/chat` chat)
- `features/chat/` chat page, split into components and hooks
- `services/upload.ts` chunked upload (`/api/upload_data_chunk`, `/api/upload/complete`)
- `components/upload/UploadStats.tsx` reusable upload progress card
