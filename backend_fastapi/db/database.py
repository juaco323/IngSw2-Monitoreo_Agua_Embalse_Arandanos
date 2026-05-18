import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")
engine = None
SessionLocal = None

if SUPABASE_DB_URL:
    engine = create_engine(SUPABASE_DB_URL, echo=False, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_log_tables() -> None:
    if engine is None:
        return
    import db.log_models  # noqa: F401
    Base.metadata.create_all(bind=engine)
