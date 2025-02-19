from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os
from tkinter import messagebox

# Configuración de la base de datos
DATABASE_URL = "postgresql://soportetech:aeiou270@localhost:5432/Port-Gadget"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Nombre de la tabla correcta
TABLE_NAME = "detalles_escaneo"  # Cambia esto si la tabla se llama diferente

def obtener_datos():
    """Obtiene los datos de la tabla de escaneos."""
    session = SessionLocal()
    try:
        query = text(f"SELECT ip, puerto, estado, servicio FROM {TABLE_NAME}")
        resultados = session.execute(query).fetchall()
        return resultados
    finally:
        session.close()

def generar_reporte_pdf(nombre_archivo="reporte_escaneo.pdf"):
    """Genera un reporte en PDF con los resultados del escaneo."""
    resultados = obtener_datos()

    c = canvas.Canvas(nombre_archivo, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, f"Reporte de Escaneo - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y = 720
    for ip, puerto, estado, servicio in resultados:
        c.drawString(100, y, f"IP: {ip}, Puerto: {puerto}, Estado: {estado}, Servicio: {servicio}")
        y -= 20
        if y < 50:  # Salto de página si es necesario
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750

    c.save()
    print(f"Reporte PDF generado: {nombre_archivo}")

def exportar_csv():
    """Exporta los resultados del escaneo a un archivo CSV y muestra la ruta del archivo generado."""
    resultados = obtener_datos()
    
    if resultados:
        csv_filename = "reporte_escaneo.csv"
        directory = os.path.dirname(__file__)  # Obtiene el directorio del archivo actual
        csv_path = os.path.join(directory, csv_filename)  # Combina la ruta con el nombre del archivo
        
        df = pd.DataFrame(resultados, columns=["IP", "Puerto", "Estado", "Servicio"])
        df.to_csv(csv_path, index=False, encoding="utf-8")  # Evita errores de codificación
        
        # Muestra la ruta del archivo generado
        messagebox.showinfo("Éxito", f"Reporte CSV generado correctamente en:\n{csv_path}")
        print(f"Reporte CSV generado: {csv_path}")
    else:
        messagebox.showwarning("Advertencia", "No hay datos para exportar.")

if __name__ == "__main__":
    generar_reporte_pdf()
    exportar_csv()
