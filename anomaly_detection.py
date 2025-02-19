import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import smtplib
from email.mime.text import MIMEText

# Función para enviar alertas
def enviar_alerta(mensaje):
    msg = MIMEText(mensaje)
    msg['Subject'] = 'Alerta de Seguridad'
    msg['From'] = 'tu_email@example.com'
    msg['To'] = 'destinatario@example.com'

    try:
        with smtplib.SMTP('smtp.example.com') as server:
            server.login('tu_email@example.com', 'tu_contraseña')
            server.send_message(msg)
        print("Alerta enviada con éxito.")
    except Exception as e:
        print(f"Error al enviar la alerta: {e}")

# Función para detectar vulnerabilidades
def detectar_vulnerabilidades(archivo_csv):
    data = pd.read_csv(archivo_csv)

    # Preprocesamiento
    X = data.drop('vulnerabilidad_detectada', axis=1)
    y = data['vulnerabilidad_detectada']

    # División del conjunto de datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenar el modelo
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Hacer predicciones
    y_pred = model.predict(X_test)

    # Evaluar el modelo
    report = classification_report(y_test, y_pred)
    print(report)

    # Generar alertas si se detectan vulnerabilidades
    if any(y_pred == 1):  # Si se detecta alguna vulnerabilidad
        enviar_alerta("Se ha detectado una vulnerabilidad en los nuevos datos.")
