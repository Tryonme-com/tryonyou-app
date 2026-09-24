create extension if not exists pgcrypto;

create table if not exists public.core_engine_events (
  event_id uuid primary key default gen_random_uuid(),
  session_id text not null,
  event_type text not null,
  account_scope text not null,
  actor_id text not null default 'anonymous',
  client_ip text not null default 'unknown',
  source text not null,
  route text not null,
  commission_rate numeric(6,4) not null default 0.0800,
  commission_basis_eur numeric(12,2) not null default 0.00,
  commission_audit_eur numeric(12,2) not null default 0.00,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  protocol text not null
);

create index if not exists idx_core_engine_events_session_id
  on public.core_engine_events (session_id, created_at desc);

create index if not exists idx_core_engine_events_event_type
  on public.core_engine_events (event_type, created_at desc);

create table if not exists public.core_engine_sessions (
  session_id text primary key,
  account_scope text not null,
  actor_id text not null default 'anonymous',
  last_event_type text not null,
  last_route text not null,
  last_seen_at timestamptz not null default timezone('utc', now()),
  source text not null,
  payload jsonb not null default '{}'::jsonb,
  protocol text not null
);

create index if not exists idx_core_engine_sessions_last_seen_at
  on public.core_engine_sessions (last_seen_at desc);

create table if not exists public.core_engine_control (
  control_key text primary key,
  state text not null,
  updated_at timestamptz not null default timezone('utc', now()),
  updated_by text not null default 'system',
  account_scope text not null default 'admin',
  note text not null default '',
  protocol text not null
);

insert into public.core_engine_control (
  control_key,
  state,
  updated_at,
  updated_by,
  account_scope,
  note,
  protocol
)
values (
  'mirror_power_state',
  'on',
  timezone('utc', now()),
  'bootstrap',
  'admin',
  '',
  'jules_core_engine_v11'
)
on conflict (control_key) do nothing;
