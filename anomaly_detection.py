import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

# Función para mostrar alertas
def mostrar_alerta(vulnerabilidades):
    print("¡Alerta de Seguridad!")
    print("Se han detectado las siguientes vulnerabilidades:")
    print(vulnerabilidades)
    print("Revisa el panel de control para más detalles.")

# Función para entrenar el modelo y detectar vulnerabilidades
def entrenar_modelo(archivo_csv):
    # Cargar datos
    try:
        data = pd.read_csv(archivo_csv)
    except FileNotFoundError:
        print(f"Error: El archivo {archivo_csv} no se encuentra.")
        return
    except pd.errors.EmptyDataError:
        print("Error: El archivo está vacío.")
        return
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return

    # Verificar las columnas en el DataFrame
    print("Columnas en el DataFrame:", data.columns)

    # Asegúrate de que la columna 'vulnerabilidad_detectada' existe
    if 'vulnerabilidad_detectada' not in data.columns:
        raise KeyError("La columna 'vulnerabilidad_detectada' no se encuentra en el archivo CSV.")
    
    # Preprocesamiento
    X = data.drop('vulnerabilidad_detectada', axis=1)
    y = data['vulnerabilidad_detectada']

    # División del conjunto de datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Ajuste de Hiperparámetros con GridSearchCV
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }
    modelo = RandomForestClassifier(class_weight='balanced')  # Manejo de desbalance de clases
    grid_search = GridSearchCV(modelo, param_grid, cv=3)
    grid_search.fit(X_train, y_train)

    # Hacer predicciones
    y_pred = grid_search.predict(X_test)

    # Evaluar el modelo
    report = classification_report(y_test, y_pred)
    print(report)

    # Mostrar matriz de confusión
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=grid_search.best_estimator_.classes_)
    disp.plot(cmap='Blues')
    
    # Generar alertas si se detectan vulnerabilidades
    vulnerabilidades_detectadas = X_test[y_pred == 1]
    if not vulnerabilidades_detectadas.empty:
        mostrar_alerta(vulnerabilidades_detectadas)

# Ejecutar el entrenamiento del modelo
if __name__ == "__main__":
    entrenar_modelo('datos.csv')