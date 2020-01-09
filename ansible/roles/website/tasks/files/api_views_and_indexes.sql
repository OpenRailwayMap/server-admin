-- We have to create the indexes on a function because PostgreSQL does not support indexes on views
CREATE OR REPLACE FUNCTION get_tags_hstore(railway TEXT, name TEXT, tags HSTORE)
    RETURNS HSTORE AS $$
BEGIN
  IF railway IS NOT NULL AND name IS NOT NULL THEN
    RETURN hstore(ARRAY['railway', 'name'], ARRAY[railway, name]) || tags;
  END IF;
  IF railway IS NOT NULL THEN
    RETURN hstore('railway', railway) || tags;
  END IF;
  IF name IS NOT NULL THEN
    RETURN hstore('name', name) || tags;
  END IF;
  RETURN tags;
END;
$$ LANGUAGE plpgsql
IMMUTABLE;


CREATE OR REPLACE VIEW openrailwaymap_api_point AS
  SELECT
      osm_id,
      get_tags_hstore(railway, name, tags) AS tags,
      way
    FROM planet_osm_point
    WHERE railway IS NOT NULL;

CREATE OR REPLACE VIEW openrailwaymap_api_line AS
  SELECT
      osm_id,
      get_tags_hstore(railway, name, tags) AS tags,
      way
    FROM planet_osm_line
    WHERE railway IS NOT NULL;

CREATE OR REPLACE VIEW openrailwaymap_api_polygon AS
  SELECT
      osm_id,
      way_area,
      get_tags_hstore(railway, name, tags) AS tags,
      way
    FROM planet_osm_polygon
    WHERE railway IS NOT NULL;

CREATE INDEX IF NOT EXISTS planet_osm_point_hstore_gist_idx
  ON planet_osm_point
  USING GIST(get_tags_hstore(railway, name, tags));
CREATE INDEX IF NOT EXISTS planet_osm_point_hstore_btree_idx
  ON planet_osm_point
  USING BTREE(get_tags_hstore(railway, name, tags));
CREATE INDEX IF NOT EXISTS planet_osm_line_hstore_gist_idx
  ON planet_osm_line
  USING GIST(get_tags_hstore(railway, name, tags));
CREATE INDEX IF NOT EXISTS planet_osm_line_hstore_btree_idx
  ON planet_osm_line
  USING BTREE(get_tags_hstore(railway, name, tags));
CREATE INDEX IF NOT EXISTS planet_osm_polygon_hstore_gist_idx
  ON planet_osm_polygon
  USING GIST(get_tags_hstore(railway, name, tags));
CREATE INDEX IF NOT EXISTS planet_osm_polygon_hstore_btree_idx
  ON planet_osm_polygon
  USING BTREE(get_tags_hstore(railway, name, tags));
