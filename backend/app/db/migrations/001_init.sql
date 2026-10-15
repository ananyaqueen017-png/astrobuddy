-- AstroBuddy schema for Supabase / PostgreSQL. NOT applied or tested by this project's test suite.
-- Apply in the Supabase SQL editor or with `psql "$DATABASE_URL" -f 001_init.sql`.
-- Birth data is personal data: review retention, backups and your privacy policy before storing it.

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now()
);

create table if not exists public.saved_charts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  label text not null default 'My chart',
  birth jsonb not null,      -- request body as sent to /charts/calculate
  settings jsonb not null,   -- zodiac, ayanamsa, house system, node type
  chart jsonb not null,      -- full ChartResponse, including engine name/version
  created_at timestamptz not null default now()
);
create index if not exists saved_charts_user_idx on public.saved_charts (user_id, created_at desc);

create table if not exists public.journal_entries (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  chart_id uuid references public.saved_charts (id) on delete set null,
  entry_date date not null,
  title text not null,
  body text not null default '',
  tags text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists journal_user_date_idx on public.journal_entries (user_id, entry_date desc);
create index if not exists journal_tags_idx on public.journal_entries using gin (tags);

create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  chart_id uuid references public.saved_charts (id) on delete set null,
  title text,
  created_at timestamptz not null default now()
);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  chart_factors jsonb,       -- supporting facts returned with assistant messages
  created_at timestamptz not null default now()
);
create index if not exists messages_conv_idx on public.messages (conversation_id, created_at);

-- Row-level security: each user can only touch their own rows.
alter table public.profiles enable row level security;
alter table public.saved_charts enable row level security;
alter table public.journal_entries enable row level security;
alter table public.conversations enable row level security;
alter table public.messages enable row level security;

create policy "own profile" on public.profiles for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "own charts" on public.saved_charts for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own journal" on public.journal_entries for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own conversations" on public.conversations for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own messages" on public.messages for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
