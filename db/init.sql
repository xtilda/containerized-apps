CREATE TABLE IF NOT EXISTS people (
  id SERIAL PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name  TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(first_name, last_name)
);
