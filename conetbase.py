from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Reemplaza con tus credenciales de PostgreSQL
DATABASE_URL = "postgresql://soportetech:aeiou270@localhost:5432/Port-Gadget"

# Crear la conexión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Probar conexión
try:
    with engine.connect():
        print("Conectado a PostgreSQL correctamente")
except Exception as e:
    print(f"Error conectando a PostgreSQL: {e}")
