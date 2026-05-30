# sheet_sync — Luca → Cloud SQL → ERP-neutral canonical extraction

Greenfield scaffolding for the P0 canonical layer. Discipline:

```
raw_luca.raw_records   append-only JSONB landing
etl.checkpoint         one row per entity per run
canonical.*            idempotent UPSERT (ON CONFLICT DO UPDATE)
```

No `DROP` / `DELETE` / `TRUNCATE` is ever issued. DDL is `CREATE ... IF NOT EXISTS`.

## Setup

```bash
cd sheet_sync
pip install -r requirements.txt
source /tmp/luca_env_exports.sh          # provides PG* env + Cloud SQL proxy
```

Connection uses standard libpq env vars: `PGHOST=127.0.0.1 PGPORT=55435
PGDATABASE=koza PGUSER=koza_etl PGPASSWORD=...` (Cloud SQL proxy on 55435).

## P0 Batch-2 — `canonical.document_types` + `canonical.tax_offices`

```bash
# validate sources without a DB
python p0_batch2_document_taxoffice.py --check --allow-seed

# real run (authoritative tax-office source)
export TAX_OFFICES_SOURCE_URL="https://.../tax_offices.json"
python p0_batch2_document_taxoffice.py

# smoke test against the DB with bundled sample tax offices
python p0_batch2_document_taxoffice.py --allow-seed
```

### Sources

- **document_types** — seed-driven, ERP-neutral (`data/document_types_seed.json`).
- **tax_offices** — HTTP-source-driven via `TAX_OFFICES_SOURCE_URL`. The JSON may be
  a top-level list or `{"tax_offices": [...]}`. Records are normalised on common
  key variants (`code|kod|vergi_dairesi_kodu`, `name|ad|vergi_dairesi_adi`,
  `province|il`, `district|ilce`). The bundled `data/tax_offices_seed.json` is a
  **smoke-test sample only** (codes prefixed `SEED-` are not authoritative GİB
  codes) and is used only with `--allow-seed`.

### Expected output

```
--- P0 BATCH2 VERIFY ---
canonical.document_types = <n>
canonical.tax_offices = <n>
tax_offices_http_status = <code | 0 for seed>
tax_offices_source_count = <n>
tax_offices_upserted = <n>
FINAL_STATUS = OK
```
