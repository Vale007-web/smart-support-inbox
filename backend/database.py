from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL del database SQLite (creerà un file chiamato tickets.db dentro la cartella backend)
SQLALCHEMY_DATABASE_URL = "sqlite:///./tickets.db"

# Engine SQLAlchemy (connect_args serve solo per SQLite)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sessione per interagire con il DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base per i modelli della tabella
Base = declarative_base()

# Dependency per ottenere la sessione DB nelle API di FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()