create extension if not exists "uuid-ossp";

create table if not exists public.scenarios (
    id uuid primary key default uuid_generate_v4(),
    created_at timestamptz not null default now(),
    mission jsonb not null,
    status text not null default 'generated',
    model text not null
);

create index if not exists scenarios_created_at_idx on public.scenarios (created_at desc);
create index if not exists scenarios_mission_type_idx on public.scenarios ((mission->>'mission_type'));
create index if not exists scenarios_difficulty_idx on public.scenarios ((mission->>'difficulty'));

create table if not exists public.scenario_variants (
    id uuid primary key default uuid_generate_v4(),
    scenario_id uuid not null references public.scenarios(id) on delete cascade,
    language text not null check (language in ('en', 'ar')),
    variant_index int not null check (variant_index >= 0),
    payload jsonb not null,
    validated boolean not null default false,
    unique (scenario_id, language, variant_index)
);

create index if not exists scenario_variants_scenario_idx on public.scenario_variants (scenario_id);

create table if not exists public.audit_log (
    id uuid primary key default uuid_generate_v4(),
    ts timestamptz not null default now(),
    scenario_id uuid references public.scenarios(id) on delete set null,
    event_type text not null,
    detail jsonb not null default '{}'::jsonb
);

create index if not exists audit_log_ts_idx on public.audit_log (ts desc);
create index if not exists audit_log_scenario_idx on public.audit_log (scenario_id);
