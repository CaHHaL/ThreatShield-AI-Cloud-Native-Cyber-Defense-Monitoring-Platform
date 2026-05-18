-- ThreatShield AI — PostgreSQL initialization
-- This script runs once when the container is first created.

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- The application (SQLAlchemy) will create the actual tables via create_all()
-- This file just ensures extensions are available.

-- Optional: create a read-only reporting user
-- CREATE ROLE reporter WITH LOGIN PASSWORD 'reporter_pass' NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
-- GRANT CONNECT ON DATABASE threatshield_db TO reporter;
-- GRANT USAGE ON SCHEMA public TO reporter;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO reporter;
