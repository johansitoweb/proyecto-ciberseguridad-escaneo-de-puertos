# Usa una imagen base de Python con Flet preinstalado
FROM python:3.9-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /proyecto-cirverseguridad-escaneo-de-puetos

# Copia los archivos de requirements si existen
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Expone el puerto en el que Flet correrá la aplicación (5000 por defecto)
EXPOSE 5000

# Comando para ejecutar la aplicación Flet
CMD ["flet", "run", "login.py" , "escaneo.py" , "tcp_scanner.py" , "udp_scanner.py" , "Nmap_versiones.py"]
