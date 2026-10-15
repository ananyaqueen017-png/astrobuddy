"""Persistence is not wired up yet.

The schema in migrations/001_init.sql is ready for Supabase/PostgreSQL. The Journal, saved charts and
conversation endpoints stay at 501 until a repository layer (e.g. SQLAlchemy or supabase-py) and
integration tests against a real database exist. Authentication is available via core/auth.py once
SUPABASE_JWT_SECRET is set.
"""
