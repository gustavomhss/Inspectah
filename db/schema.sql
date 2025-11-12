-- Inspectah schema stub
CREATE TABLE sources (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE items (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL REFERENCES sources(id)
);
