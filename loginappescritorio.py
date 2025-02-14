import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import psycopg2
import requests
from io import BytesIO

# Configuración de PostgreSQL
DATABASE_URL = "postgresql://soportetech:aeiou270@localhost:5432/Port-Gadget"

def verificar_credenciales(correo, contraseña):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo=%s AND contraseña=%s", (correo, contraseña))
        usuario = cursor.fetchone()
        conn.close()
        return usuario is not None
    except Exception as e:
        messagebox.showerror("Error", f"Error de conexión: {e}")
        return False

def crear_cuenta(nombre, correo, contraseña):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (nombre, correo, contraseña) VALUES (%s, %s, %s)", (nombre, correo, contraseña))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Cuenta creada exitosamente")
    except Exception as e:
        messagebox.showerror("Error", f"Error al crear la cuenta: {e}")

def login():
    correo = correo_entry.get()
    contraseña = contraseña_entry.get()
    
    if verificar_credenciales(correo, contraseña):
        messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
        window.destroy()  # Cierra la ventana del login
        subprocess.Popen(["python", "escaneo.py"])  # Ejecuta la interfaz del escáner
        
    else:
        messagebox.showerror("Error", "Correo o contraseña incorrectos")


def mostrar_ventana_crear_cuenta():
    ventana_crear_cuenta = tk.Toplevel(window)
    ventana_crear_cuenta.title("Crear Cuenta")
    ventana_crear_cuenta.geometry("400x300")
    ventana_crear_cuenta.configure(bg="#2e2e2e")

    tk.Label(ventana_crear_cuenta, text="Nombre:", fg="white", bg="#2e2e2e", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
    nombre_entry = tk.Entry(ventana_crear_cuenta, font=("Arial", 12))
    nombre_entry.grid(row=1, column=0, padx=10, pady=5, ipady=3)

    tk.Label(ventana_crear_cuenta, text="Correo Electrónico:", fg="white", bg="#2e2e2e", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
    correo_entry_crear = tk.Entry(ventana_crear_cuenta, font=("Arial", 12))
    correo_entry_crear.grid(row=3, column=0, padx=10, pady=5, ipady=3)

    tk.Label(ventana_crear_cuenta, text="Contraseña:", fg="white", bg="#2e2e2e", font=("Arial", 12)).grid(row=4, column=0, sticky="w", pady=5)
    contraseña_entry_crear = tk.Entry(ventana_crear_cuenta, show="*", font=("Arial", 12))
    contraseña_entry_crear.grid(row=5, column=0, padx=10, pady=5, ipady=3)

    crear_cuenta_button = tk.Button(ventana_crear_cuenta, text="Crear Cuenta", command=lambda: crear_cuenta(nombre_entry.get(), correo_entry_crear.get(), contraseña_entry_crear.get()), bg="#007bff", fg="white", font=("Arial", 12, "bold"))
    crear_cuenta_button.grid(row=6, column=0, pady=20, sticky="ew")

# Interfaz de Login
window = tk.Tk()
window.title("Login - Port Gadget")
window.geometry("500x400")
window.configure(bg="#2e2e2e")

# Imagen desde URL
url_imagen = "https://i.pinimg.com/736x/3b/e9/bf/3be9bfb8065fe68708bd7c6abc0ba84c.jpg"  
response = requests.get(url_imagen)
image = Image.open(BytesIO(response.content))
image = image.resize((150, 150))  # Redimensionar sin perder calidad
photo = ImageTk.PhotoImage(image)
image_label = tk.Label(window, image=photo, bg="#2e2e2e")
image_label.pack(pady=10)

# Formulario de Login
login_frame = tk.Frame(window, bg="#2e2e2e")
login_frame.pack()

tk.Label(login_frame, text="Correo Electrónico:", fg="white", bg="#2e2e2e", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
correo_entry = tk.Entry(login_frame, font=("Arial", 12))
correo_entry.grid(row=1, column=0, padx=10, pady=5, ipady=3)

tk.Label(login_frame, text="Contraseña:", fg="white", bg="#2e2e2e", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
contraseña_entry = tk.Entry(login_frame, show="*", font=("Arial", 12))
contraseña_entry.grid(row=3, column=0, padx=10, pady=5, ipady=3)

login_button = tk.Button(login_frame, text="Iniciar Sesión", command=login, bg="#007bff", fg="white", font=("Arial", 12, "bold"))
login_button.grid(row=4, column=0, pady=20, sticky="ew")

crear_cuenta_button = tk.Button(login_frame, text="Crear Cuenta", command=mostrar_ventana_crear_cuenta, bg="#28a745", fg="white", font=("Arial", 12, "bold"))
crear_cuenta_button.grid(row=5, column=0, pady=10, sticky="ew")

window.mainloop()