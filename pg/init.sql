-- Create table for links
CREATE TABLE IF NOT EXISTS links (
    url_token TEXT PRIMARY KEY,
    target_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create table for clicks
CREATE TABLE IF NOT EXISTS clicks (
    id BIGSERIAL PRIMARY KEY,
    url_token TEXT NOT NULL,
    clicked_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_agent TEXT
    -- FOREIGN KEY (url_token) this is for later cuz this will force read from links on every write and it will slowdown the clicks writes
    -- REFERENCES links(url_token)
);

CREATE INDEX IF NOT EXISTS clicks_url_token_time ON clicks (url_token, clicked_at DESC);


DO $do$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='replicator') THEN
    CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replpass';
  END IF;
END $do$;