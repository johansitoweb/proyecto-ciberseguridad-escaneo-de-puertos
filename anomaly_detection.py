import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def detect_anomalies(data_path, contamination=0.1):
    """
    Detecta anomalías en los datos de escaneo de puertos.
    """
    try:
        data = pd.read_csv(data_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo {data_path} no se encontró.")
    except pd.errors.EmptyDataError:
        raise ValueError("El archivo está vacío.")
    except Exception as e:
        raise Exception(f"Ocurrió un error al cargar el archivo: {e}")
    
    # Características relevantes para el escaneo de puertos
    required_features = ['port', 'response_time', 'status_code']
    
    for feature in required_features:
        if feature not in data.columns:
            raise ValueError(f"Falta la característica requerida: {feature}")
    
    X = data[required_features]
    
    # Escalar características
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Dividir los datos
    X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)
    
    # Entrenar el modelo Isolation Forest
    model = IsolationForest(contamination=contamination, random_state=42)
    model.fit(X_train)
    
    # Predecir anomalías
    predictions = model.predict(X_test)
    anomalies = X_test[predictions == -1]
    
    # Convertir a DataFrame original
    anomalies_df = pd.DataFrame(scaler.inverse_transform(anomalies), columns=required_features)
    
    # Visualizar anomalías
    visualize_anomalies(X, anomalies_df)
    
    # Guardar resultados
    anomalies_df.to_csv('../resultados/anomalies_detected.csv', index=False)
    print(f"Anomalías guardadas en '../resultados/anomalies_detected.csv'.")
    
    return anomalies_df

def visualize_anomalies(original_data, anomalies):
    plt.figure(figsize=(10, 6))
    plt.scatter(original_data['port'], original_data['response_time'], label='Puertos normales', color='blue', alpha=0.5)
    plt.scatter(anomalies['port'], anomalies['response_time'], label='Anomalías', color='red', marker='x')
    plt.title('Detección de Anomalías en Puertos')
    plt.xlabel('Puerto')
    plt.ylabel('Tiempo de respuesta')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    data_path = '../data/scan_results.csv'  # Ruta ajustada 
    contamination_level = 0.05  # Ajustado a un nivel más fino de detección
    
    anomalies = detect_anomalies(data_path, contamination=contamination_level)
    print("Anomalías detectadas:")
    print(anomalies)
