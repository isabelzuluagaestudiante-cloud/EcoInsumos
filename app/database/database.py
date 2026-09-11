from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./ecoinsumos.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def ensure_schema():
    with engine.begin() as conn:
        inspector = inspect(conn)

        if "productos" in inspector.get_table_names():
            columnas = {col["name"] for col in inspector.get_columns("productos")}

            if "usuario_id" not in columnas:
                conn.execute(text("ALTER TABLE productos ADD COLUMN usuario_id INTEGER"))

            if "estado" not in columnas:
                conn.execute(text("ALTER TABLE productos ADD COLUMN estado VARCHAR(50) DEFAULT 'Disponible'"))

            if "tipo_publicacion" not in columnas:
                conn.execute(text("ALTER TABLE productos ADD COLUMN tipo_publicacion VARCHAR(30) DEFAULT 'precio'"))

            if "imagen_url" not in columnas:
                conn.execute(text("ALTER TABLE productos ADD COLUMN imagen_url VARCHAR(255)"))


ensure_schema()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()