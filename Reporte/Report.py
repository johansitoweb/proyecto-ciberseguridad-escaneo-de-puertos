from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import datetime

# Configurar la conexión a PostgreSQL
DATABASE_URL = "postgresql://soportetech:aeiou270@localhost:5432/Port-Gadget"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def generar_reporte_pdf(nombre_archivo="reporte_escaneo.pdf"):
    session = SessionLocal()
    
    # Consulta los datos de la tabla (ajusta esto según tu modelo de base de datos)
    resultados = session.execute("SELECT ip, puerto, estado, servicio FROM escaneos").fetchall()

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

# Ejecutar función
generar_reporte_pdf()
