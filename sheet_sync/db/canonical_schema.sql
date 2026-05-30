-- ÖZGÜR RUBBER — ERP-neutral canonical extraction
-- Idempotent DDL. Safe to run repeatedly. NO DROP/DELETE/TRUNCATE.
--
-- Layers:
--   raw_luca   -> raw landing zone (immutable, append-only JSONB records)
--   etl        -> run metadata / checkpoints
--   canonical  -> ERP-neutral, deduplicated reference tables

CREATE SCHEMA IF NOT EXISTS raw_luca;
CREATE SCHEMA IF NOT EXISTS etl;
CREATE SCHEMA IF NOT EXISTS canonical;

-- ---------------------------------------------------------------------------
-- raw landing zone
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS raw_luca.raw_records (
    id           BIGSERIAL PRIMARY KEY,
    batch        TEXT        NOT NULL,
    entity       TEXT        NOT NULL,
    source       TEXT        NOT NULL,
    source_hash  TEXT        NOT NULL,
    payload      JSONB       NOT NULL,
    ingested_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_raw_records_entity
    ON raw_luca.raw_records (entity, ingested_at DESC);

-- ---------------------------------------------------------------------------
-- checkpoints (one row per entity per run)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS etl.checkpoint (
    id           BIGSERIAL PRIMARY KEY,
    batch        TEXT        NOT NULL,
    entity       TEXT        NOT NULL,
    status       TEXT        NOT NULL,
    source       TEXT,
    http_status  INTEGER,
    source_count INTEGER,
    upserted     INTEGER,
    started_at   TIMESTAMPTZ NOT NULL,
    finished_at  TIMESTAMPTZ,
    detail       JSONB
);

CREATE INDEX IF NOT EXISTS ix_checkpoint_batch_entity
    ON etl.checkpoint (batch, entity, started_at DESC);

-- ---------------------------------------------------------------------------
-- canonical.document_types  (seed-driven, ERP-neutral)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS canonical.document_types (
    id              BIGSERIAL PRIMARY KEY,
    code            TEXT        NOT NULL UNIQUE,
    name            TEXT        NOT NULL,
    name_tr         TEXT,
    direction       TEXT,           -- sales | purchase | both | none
    erp_neutral_key TEXT,
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    source          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- canonical.tax_offices  (HTTP-source-driven; GİB vergi daireleri)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS canonical.tax_offices (
    id          BIGSERIAL PRIMARY KEY,
    code        TEXT        NOT NULL UNIQUE,
    name        TEXT        NOT NULL,
    province    TEXT,           -- il
    district    TEXT,           -- ilçe
    source      TEXT,
    source_hash TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
