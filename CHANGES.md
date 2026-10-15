# Stage 2 changes (frontend)
Modified: .env.example, README.md, src/lib/api/types.ts, src/lib/api/services.ts (getDashas only),
src/context/BirthProfileContext.tsx (ignores saved details that lack settings), src/components/BirthForm.tsx
(calculation settings), src/app/page.tsx (chart details section).
Created: src/lib/api/defaults.ts, src/components/chart/ChartDetails.tsx, src/app/living-kundli/page.tsx,
src/app/dasha-timeline/page.tsx (these two static routes take precedence over the [feature] placeholder).
Unchanged: design, navigation, ChartWheel, API client, other 11 placeholder routes.
Added: backend/ (entire folder).
