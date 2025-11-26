"""
Database configuration implementing CQRS pattern.
Master DB (172.20.0.10) for WRITES
Replica DB (172.20.0.11) for READS
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ============================================
# DATABASE CONNECTION STRINGS
# ============================================
DATABASE_MASTER_URL = "postgresql://admin:root_password@172.20.0.10:5432/crypto_db"
DATABASE_REPLICA_URL = "postgresql://admin:root_password@172.20.0.11:5432/crypto_db"

# ============================================
# ENGINES - CQRS PATTERN
# ============================================
# Engine for WRITE operations (Master)
engine_master = create_engine(
    DATABASE_MASTER_URL,
    pool_pre_ping=True,
    echo=True  # Set to False in production
)

# Engine for READ operations (Replica)
engine_replica = create_engine(
    DATABASE_REPLICA_URL,
    pool_pre_ping=True,
    echo=True  # Set to False in production
)

# ============================================
# SESSION FACTORIES
# ============================================
SessionLocalMaster = sessionmaker(autocommit=False, autoflush=False, bind=engine_master)
SessionLocalReplica = sessionmaker(autocommit=False, autoflush=False, bind=engine_replica)

# ============================================
# BASE MODEL
# ============================================
Base = declarative_base()

# ============================================
# DEPENDENCY INJECTION FUNCTIONS
# ============================================
def get_db_write():
    """
    Dependency for WRITE operations.
    Returns a session connected to the MASTER database.
    Use this for: INSERT, UPDATE, DELETE
    """
    db = SessionLocalMaster()
    try:
        yield db
    finally:
        db.close()


def get_db_read():
    """
    Dependency for READ operations.
    Returns a session connected to the REPLICA database.
    Use this for: SELECT queries
    """
    db = SessionLocalReplica()
    try:
        yield db
    finally:
        db.close()
