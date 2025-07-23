from sqlmodel import create_engine, Session
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # .../src/FastApiApp/app
DB_PATH = BASE_DIR / "db/db.sqlite3"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
