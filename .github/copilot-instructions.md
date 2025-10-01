# AI contributor guide for tcc_rastreamento_back

Use this as your quick-start map to be productive in this repo. Keep changes small, follow the established patterns, and prefer absolute imports under `tcc_rastreamento_back.*`.

## Big picture
- Stack: FastAPI + async SQLAlchemy (postgresql+asyncpg), Pydantic Settings, passlib, jose JWT, Alembic (declared, not wired), SQLAlchemy-Continuum (versioning hooks present but partially integrated).
- Architecture pattern: Controller → Service → Repository → DB session.
  - Controller: defines routes and wraps responses with `utils/response_model.py`.
  - Service: orchestrates operations, handles commit/rollback, shapes data (`AbstractService`).
  - Repository: builds SQLAlchemy Core/ORM queries, serializes rows (`AbstractRepository`).
- Data model conventions:
  - `utils/base.py` defines `Base` (DeclarativeBase). Models typically mix in `core/abstract/abstract_model.py` fields: `id`, `tenant_id`, `is_active`, `name`, `created_at`, `updated_at` and enable versioning.
  - Soft-deletes via `is_active`; endpoints exist to activate/deactivate.
- Multi-tenant: `utils/context_vars.py` manages `tenant_id`; `ConnectionPool` has a tenant-aware query hook (partially applied). Prefer explicit filters on `tenant_id` until this is unified.
- Auth: JWT via `middleware/jwt_middleware.py` using `OAuth2PasswordBearer`; expects a `UserRepository` and `Usuario` model (currently stubs).

## Run, build, env
- Python 3.13. Dependencies in `pyproject.toml`. Poetry lock present; you can use Poetry or pip.
- Required env (.env supported by `utils/settings.py`):
  - `DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>`
  - `SECRET_KEY`, `ALGORITHM` (HS256), `ACCESS_TOKEN_EXPIRE_MINUTES`
- Start server (needs uvicorn installed):
  - Module: `tcc_rastreamento_back.main:app`
  - Windows PowerShell: install uvicorn if missing; run with reload.
- Alembic is declared but no config is present in the repo; schema is created via `Base.metadata.create_all` in `main.py`.

## Key files and patterns
- App entry: `tcc_rastreamento_back/main.py` creates tables and mounts routers. Ensure routers are imported and included here.
- Settings: prefer `tcc_rastreamento_back.utils.settings.Settings`. `utils/config.py` appears legacy; avoid mixing both.
- DB access: `utils/connection_pool.py`
  - Engine: async `postgresql+asyncpg` with `create_async_engine`.
  - Sessions: use `ConnectionPool.get_db_session()` (async contextmanager). For optional session parameters, use `utils/contexts.conditional_session`.
- Responses: wrap all route returns with `utils/response_model.ResponseModel(...).model_response()`.
- Filtering: dynamic filters via `utils/format.apply_dynamic_filters` and `utils/filter_model.py`.
  - Example payload for POST /all or /all/paginated:
    `{ "filters": [{ "attribute": "name", "operator": "CONTAINS", "primary_value": "JOAO", "condition": "AND" }] }`
- Serialization: use `utils/format.serialize_model(model_instance)` for ORM objects.

## Implementing a new domain module
1) Create folder `core/<domain>/` with: `<domain>_model.py`, `<domain>_repository.py`, `<domain>_service.py`, `<domain>_controller.py`.
2) Model: subclass `Base` and include fields per `AbstractModel` (id, tenant_id, timestamps, is_active).
3) Repository: extend patterns from `core/abstract/abstract_repository.py` (use async `select`, return serialized models when responding to controllers).
4) Service: follow `core/abstract/abstract_service.py` methods: commit/rollback in service layer; use `conditional_session` when session may be provided.
5) Controller: subclass-like usage of `AbstractController` to register routes (`get_all`, `save`, `update_by_id`, etc.) and return `ResponseModel`.
6) Register router in `main.py` with an appropriate prefix and tag.

## Auth and protection
- Token creation: `create_access_token(data)` in `middleware/jwt_middleware.py`.
- Protect routes: inject `Depends(get_current_user)` from the same file.
- Note: `get_db` used in `jwt_middleware` is not defined; provide a dependency wrapper around `ConnectionPool.get_db_session()` or adjust to async session usage.

## Gotchas and current gaps
- Imports are inconsistent: use absolute `tcc_rastreamento_back.*` to avoid runtime path issues.
- `main.py` references `engine` and `usuario.router`; ensure these are imported or fix to use `ConnectionPool.get_engine()` and real routers.
- `user`, `role`, `tracker`, `vehicle` modules are mostly empty; endpoints won’t work until implemented.
- `logging.yaml` is referenced in exceptions code but not present.
- Alembic not initialized in-repo; migrations require setup.

## Useful snippets
- DB dependency for FastAPI:
  """
  async def get_db():
      async with ConnectionPool.get_db_session() as session:
          yield session
  """
- Start server (PowerShell):
  """
  # create venv and install
  py -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -e . uvicorn
  # run
  uvicorn tcc_rastreamento_back.main:app --reload --host 0.0.0.0 --port 8000
  """

---
Questions to clarify for better automation:
- Should we consolidate settings to `utils/settings.py` and remove `utils/config.py`? Which keys are authoritative?
- Do you want Alembic migrations wired, or keep `create_all` on startup?
- Where should `tenant_id` be set per request (header, token claim)?
- Can we add `logging.yaml` and unify error handling around it?
