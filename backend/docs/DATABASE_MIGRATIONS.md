# Database Schema Migrations

The AI Clipping Platform uses [Alembic](https://alembic.sqlalchemy.org/) alongside SQLAlchemy to manage database schema evolutions safely without losing data. 

## When to Create a Migration

Whenever you modify any SQLAlchemy model in `src/infrastructure/models.py` (e.g., adding a column, changing a type, or adding a new table), you MUST generate a new migration. 

If you do not generate a migration, the application will fail to start because of the built-in startup validation in `src/core/bootstrap.py`.

## Developer Commands

### 1. Generating a Migration

To automatically generate a migration based on your changes in `models.py`:

```bash
cd backend
alembic revision --autogenerate -m "description_of_your_changes"
```

**⚠️ CRITICAL WARNING FOR SQLITE:**
Because we use SQLite, Alembic's `--autogenerate` might incorrectly output `op.alter_column` or try to recreate existing tables/constraints (like `NOT NULL`). 
**Always manually inspect the generated script in `alembic/versions/`**.
If your goal was just to add a column, **prune the script** so it ONLY contains `op.add_column()` statements. Remove any generated `op.alter_column()` or `op.drop_table()` commands if they are unintended side-effects of SQLite's limited `ALTER TABLE` support.

### 2. Applying Migrations

To upgrade your local database to the latest schema version:

```bash
cd backend
alembic upgrade head
```

### 3. Rolling Back

If you need to revert the last applied migration:

```bash
cd backend
alembic downgrade -1
```

Or to revert to a specific revision:

```bash
alembic downgrade <revision_id>
```

## How the Application Validates Schema

During the boot sequence (`validate_startup` in `main.py` -> `bootstrap.py`), the backend automatically checks `alembic.config` against the active database. 

If the current database revision (`current_rev`) does not match the latest known script (`head_rev`), the backend will safely raise a `RuntimeError` and halt. This strictly prevents the application from processing API requests with outdated database tables (which would lead to `sqlite3.OperationalError` crashes in production).

You can also check the current schema version and pending status dynamically by polling the `GET /api/v1/health` endpoint.
