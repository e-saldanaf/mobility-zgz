-- Move of SQL file into corrected folder
-- Original path: query/posgresql/create/bizi_stations/bizi_stations.sql
-- New path: query/postgresql/create/bizi_stations/bizi_stations.sql

-- This file is a copy of the original for rename purposes.

-- Drop table
DROP TABLE IF EXISTS public.bizi_stations;

-- Create table
CREATE TABLE public.bizi_stations (
	id int4 NOT NULL,
	title text NULL,
	bikes int4 NULL,
	slots int4 NULL,
	api_updated_at timestamptz NULL,
	lon float8 NULL,
	lat float8 NULL,
	created_at timestamptz NULL,
	modified_at timestamptz NULL,
	"action" text NULL,
	CONSTRAINT bizi_stations_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_bizi_modified ON public.bizi_stations USING btree (modified_at DESC);
