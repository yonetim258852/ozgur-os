#!/usr/bin/env python3
"""
ÖZGÜR RUBBER — P0 BATCH-2
ERP-neutral canonical extraction:  canonical.document_types + canonical.tax_offices

Discipline (same as P0 Foundation / Batch-1):
    raw_luca.raw_records   -> append-only JSONB landing
    etl.checkpoint         -> one row per entity per run
    canonical.*            -> idempotent UPSERT (INSERT ... ON CONFLICT DO UPDATE)

NO DROP / DELETE / TRUNCATE is ever issued.

Connection comes from standard libpq env vars (PGHOST/PGPORT/PGDATABASE/
PGUSER/PGPASSWORD). Source /tmp/luca_env_exports.sh before running.

tax_offices source:
    TAX_OFFICES_SOURCE_URL   authoritative JSON source (HTTP GET). Required for a
                             real load. Accepts either a top-level list or an
                             object with a "tax_offices" list.
    --allow-seed             permit the bundled SMOKE-TEST sample
                             (data/tax_offices_seed.json) when no URL is set.

Modes:
    (default)   full run against the DB
    --check     validate sources + parsing only, no DB connection
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

try:
    import psycopg
    from psycopg.types.json import Jsonb
except ImportError:  # pragma: no cover
    psycopg = None
    Jsonb = None

BATCH = "p0_batch2"
HERE = Path(__file__).resolve().parent
SCHEMA_SQL = HERE / "db" / "canonical_schema.sql"
DOC_TYPES_SEED = HERE / "data" / "document_types_seed.json"
TAX_OFFICES_SEED = HERE / "data" / "tax_offices_seed.json"
HTTP_TIMEOUT = int(os.environ.get("LUCA_HTTP_TIMEOUT", "30"))


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def now() -> datetime:
    return datetime.now(timezone.utc)


def row_hash(obj: dict) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _first(d: dict, *keys, default=None):
    """Return the first present, non-empty value among candidate keys."""
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default


# --------------------------------------------------------------------------- #
# source loading / normalisation
# --------------------------------------------------------------------------- #
def load_document_types() -> list[dict]:
    raw = json.loads(DOC_TYPES_SEED.read_text(encoding="utf-8"))
    out = []
    for r in raw:
        code = str(_first(r, "code", "kod", default="")).strip()
        if not code:
            continue
        out.append(
            {
                "code": code,
                "name": _first(r, "name", "ad", default=code),
                "name_tr": _first(r, "name_tr", "ad_tr"),
                "direction": _first(r, "direction", default="none"),
                "erp_neutral_key": _first(r, "erp_neutral_key", "key"),
            }
        )
    return out


def normalize_tax_office(r: dict) -> dict | None:
    code = _first(r, "code", "kod", "vergi_dairesi_kodu", "vd_kodu")
    name = _first(r, "name", "ad", "vergi_dairesi", "vergi_dairesi_adi", "vd_adi")
    if not code or not name:
        return None
    return {
        "code": str(code).strip(),
        "name": str(name).strip(),
        "province": _first(r, "province", "il", "sehir"),
        "district": _first(r, "district", "ilce", "ilçe"),
    }


def load_tax_offices(allow_seed: bool) -> tuple[list[dict], str, int | None]:
    """Returns (records, source_label, http_status)."""
    url = os.environ.get("TAX_OFFICES_SOURCE_URL", "").strip()
    if url:
        resp = requests.get(url, timeout=HTTP_TIMEOUT)
        http_status = resp.status_code
        resp.raise_for_status()
        payload = resp.json()
        source = url
    else:
        if not allow_seed:
            raise RuntimeError(
                "TAX_OFFICES_SOURCE_URL is not set. Set it to the authoritative "
                "source, or pass --allow-seed for a smoke test with sample data."
            )
        payload = json.loads(TAX_OFFICES_SEED.read_text(encoding="utf-8"))
        http_status = 0  # local seed, no HTTP
        source = "seed-sample"

    rows = payload.get("tax_offices", payload) if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        raise ValueError("tax_offices source did not yield a list of records")

    records, seen = [], set()
    for r in rows:
        norm = normalize_tax_office(r)
        if norm and norm["code"] not in seen:
            seen.add(norm["code"])
            records.append(norm)
    return records, source, http_status


# --------------------------------------------------------------------------- #
# DB operations
# --------------------------------------------------------------------------- #
def ensure_schema(conn) -> None:
    conn.execute(SCHEMA_SQL.read_text(encoding="utf-8"))


def land_raw(conn, entity: str, source: str, records: list[dict]) -> None:
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO raw_luca.raw_records "
            "(batch, entity, source, source_hash, payload) "
            "VALUES (%s, %s, %s, %s, %s)",
            [(BATCH, entity, source, row_hash(r), Jsonb(r)) for r in records],
        )


def upsert_document_types(conn, records: list[dict], source: str) -> int:
    sql = """
        INSERT INTO canonical.document_types
            (code, name, name_tr, direction, erp_neutral_key, source, updated_at)
        VALUES (%(code)s, %(name)s, %(name_tr)s, %(direction)s,
                %(erp_neutral_key)s, %(source)s, now())
        ON CONFLICT (code) DO UPDATE SET
            name            = EXCLUDED.name,
            name_tr         = EXCLUDED.name_tr,
            direction       = EXCLUDED.direction,
            erp_neutral_key = EXCLUDED.erp_neutral_key,
            source          = EXCLUDED.source,
            updated_at      = now()
    """
    with conn.cursor() as cur:
        cur.executemany(sql, [dict(r, source=source) for r in records])
    return len(records)


def upsert_tax_offices(conn, records: list[dict], source: str) -> int:
    sql = """
        INSERT INTO canonical.tax_offices
            (code, name, province, district, source, source_hash, updated_at)
        VALUES (%(code)s, %(name)s, %(province)s, %(district)s,
                %(source)s, %(source_hash)s, now())
        ON CONFLICT (code) DO UPDATE SET
            name        = EXCLUDED.name,
            province    = EXCLUDED.province,
            district    = EXCLUDED.district,
            source      = EXCLUDED.source,
            source_hash = EXCLUDED.source_hash,
            updated_at  = now()
    """
    with conn.cursor() as cur:
        cur.executemany(
            sql, [dict(r, source=source, source_hash=row_hash(r)) for r in records]
        )
    return len(records)


def write_checkpoint(conn, entity, status, source, http_status,
                     source_count, upserted, started_at, detail=None) -> None:
    conn.execute(
        "INSERT INTO etl.checkpoint "
        "(batch, entity, status, source, http_status, source_count, upserted, "
        " started_at, finished_at, detail) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (BATCH, entity, status, source, http_status, source_count, upserted,
         started_at, now(), Jsonb(detail) if detail else None),
    )


def table_count(conn, table: str) -> int:
    return conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def run_check(allow_seed: bool) -> int:
    dts = load_document_types()
    print(f"document_types seed parsed = {len(dts)}")
    try:
        tos, source, http = load_tax_offices(allow_seed)
        print(f"tax_offices source       = {source}")
        print(f"tax_offices http_status  = {http}")
        print(f"tax_offices parsed       = {len(tos)}")
    except Exception as exc:  # noqa: BLE001
        print(f"tax_offices             = NOT LOADED ({exc})")
        return 1
    print("CHECK_OK")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="validate sources only, no DB")
    ap.add_argument("--allow-seed", action="store_true",
                    help="permit bundled tax_offices smoke-test sample")
    args = ap.parse_args()

    if args.check:
        return run_check(args.allow_seed)

    if psycopg is None:
        print("--- P0 BATCH2 VERIFY ---")
        print("FINAL_STATUS = BLOCKED (psycopg not installed; "
              "pip install -r requirements.txt)")
        return 2

    dsn_ok = any(os.environ.get(v) for v in ("PGHOST", "PGDATABASE", "PGSERVICE"))
    if not dsn_ok:
        print("--- P0 BATCH2 VERIFY ---")
        print("FINAL_STATUS = BLOCKED (no PG* env; source /tmp/luca_env_exports.sh)")
        return 2

    final_status = "OK"
    to_http = to_src_count = to_upserted = None

    try:
        with psycopg.connect(autocommit=False) as conn:
            ensure_schema(conn)

            # ---- document_types (seed-driven) ----
            t0 = now()
            dts = load_document_types()
            land_raw(conn, "document_types", "seed", dts)
            dt_upserted = upsert_document_types(conn, dts, "seed")
            write_checkpoint(conn, "document_types", "OK", "seed", None,
                             len(dts), dt_upserted, t0)

            # ---- tax_offices (HTTP-source-driven) ----
            t1 = now()
            tos, to_source, to_http = load_tax_offices(args.allow_seed)
            to_src_count = len(tos)
            land_raw(conn, "tax_offices", to_source, tos)
            to_upserted = upsert_tax_offices(conn, tos, to_source)
            write_checkpoint(conn, "tax_offices", "OK", to_source, to_http,
                             to_src_count, to_upserted, t1)

            conn.commit()

            dt_count = table_count(conn, "canonical.document_types")
            to_count = table_count(conn, "canonical.tax_offices")

            if dt_count == 0 or to_count == 0:
                final_status = "FAIL (empty canonical table)"
    except Exception as exc:  # noqa: BLE001
        print("--- P0 BATCH2 VERIFY ---")
        print(f"FINAL_STATUS = FAIL ({type(exc).__name__}: {exc})")
        return 1

    print("--- P0 BATCH2 VERIFY ---")
    print(f"canonical.document_types = {dt_count}")
    print(f"canonical.tax_offices = {to_count}")
    print(f"tax_offices_http_status = {to_http}")
    print(f"tax_offices_source_count = {to_src_count}")
    print(f"tax_offices_upserted = {to_upserted}")
    print(f"FINAL_STATUS = {final_status}")
    return 0 if final_status == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
