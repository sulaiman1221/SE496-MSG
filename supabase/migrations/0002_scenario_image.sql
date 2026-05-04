alter table public.scenarios add column if not exists image_url text;

insert into storage.buckets (id, name, public)
values ('scenario-images', 'scenario-images', true)
on conflict (id) do nothing;

create policy "Public read for scenario images"
on storage.objects for select
using (bucket_id = 'scenario-images');

create policy "Service role can upload scenario images"
on storage.objects for insert
to service_role
with check (bucket_id = 'scenario-images');
