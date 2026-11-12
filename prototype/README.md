# IRMSD Prototype (v0.2.0-idempotency)

This directory contains the prototype backend and regression tests. The test suite uses an in-memory SQLite database; PostgreSQL DDL is provided separately and still requires integration testing against the intended PostgreSQL version.

## Contents
- `app/models.py`: SQLAlchemy ORM models and partial unique index for active risk identity.
- `app/irmsd_engine.py`: risk scoring, effort adjustment, deterministic workflow gating, and idempotent risk registration.
- `app/api.py`: FastAPI validation endpoint.
- `sql/schema.sql`: PostgreSQL schema.
- `tests/`: smoke and regression tests.

## Test

From this directory:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

The package was checked in the authoring environment with 10 passing tests. Re-run the tests in your own clean environment and retain the execution log before citing this verification.

## Important implementation boundary

An active risk is defined as `Open` or `Mitigating`. At most one active record is allowed per `(task_id, category_code)`. Closed or verified risks remain historical and do not block a later lifecycle. The database index protects the invariant against concurrent inserts, but PostgreSQL concurrency behavior has not been integration-tested here.

Before applying the partial unique index to an existing database, reconcile duplicate active rows. This prototype does not implement an audit-alias table for merged risk IDs.

The tests verify deterministic software behavior; they do not validate classifier accuracy, prediction validity, mitigation effectiveness, or industrial impact.
