from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
from sqlalchemy import create_engine, text  # Importar text desde sqlalchemy
from sqlalchemy.orm import sessionmaker
import pandas as pd

DATABASE_URL = "postgresql://soportetech:aeiou270@localhost:5432/Port-Gadget"
engine = create_engine(DATABASE_URL)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def generar_reporte_pdf(nombre_archivo="reporte_escaneo.pdf"):
    session = SessionLocal()
    try:
        # Usar text() para envolver la consulta SQL
        resultados = session.execute(text("SELECT ip, puerto, estado, servicio FROM escaneos")).fetchall()
    finally:
        session.close()

    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Reporte de Escaneo - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = 720
    for ip, puerto, estado, servicio in resultados:
        c.drawString(100, y, f"IP: {ip}, Puerto: {puerto}, Estado: {estado}, Servicio: {servicio}")
        y -= 20

    c.save()
    print(f"✅ Reporte PDF generado: {nombre_archivo}")

def exportar_csv(nombre_archivo="reporte_escaneo.csv"):
    session = SessionLocal()
    try:
        # Usar text() para envolver la consulta SQL
        resultados = session.execute(text("SELECT ip, puerto, estado, servicio FROM escaneos")).fetchall()
    finally:
        session.close()

    df = pd.DataFrame(resultados, columns=["IP", "Puerto", "Estado", "Servicio"])
    df.to_csv(nombre_archivo, index=False)
    print(f"✅ Reporte CSV generado: {nombre_archivo}")

if __name__ == "__main__":
    generar_reporte_pdf()
    exportar_csv()