import subprocess
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import psycopg2
import requests
from io import BytesIO

# Configuración de CustomTkinter
ctk.set_appearance_mode("light")  # Modo claro (como macOS)
ctk.set_default_color_theme("green")  # Tema de colores suaves

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
        window.destroy()
        mostrar_vista_principal()
        subprocess.Popen(["python", "escaneo.py"])  # Ejecuta la interfaz del escáner
    else:
        messagebox.showerror("Error", "Correo o contraseña incorrectos")

def mostrar_vista_principal():
    ventana_principal = ctk.CTk()
    ventana_principal.title("Panel Principal")
    ventana_principal.geometry("1200x600")  # Tamaño más grande para pantalla de PC
    
    bienvenida_label = ctk.CTkLabel(ventana_principal, text="¡Bienvenido!", font=("Helvetica", 24, "bold"))
    bienvenida_label.pack(pady=40)
    
    cerrar_sesion_button = ctk.CTkButton(ventana_principal, text="Cerrar sesión", command=ventana_principal.destroy, fg_color="#ff4d4d", font=("Helvetica", 16))
    cerrar_sesion_button.pack(pady=20)
    
    ventana_principal.mainloop()

def mostrar_ventana_crear_cuenta():
    ventana_crear_cuenta = ctk.CTkToplevel(window)
    ventana_crear_cuenta.title("Crear Cuenta")
    ventana_crear_cuenta.geometry("600x400")  # Tamaño más grande para pantalla de PC

    nombre_label = ctk.CTkLabel(ventana_crear_cuenta, text="Nombre:", font=("Helvetica", 16))
    nombre_label.grid(row=0, column=0, sticky="w", pady=10, padx=20)
    nombre_entry = ctk.CTkEntry(ventana_crear_cuenta, font=("Helvetica", 16))
    nombre_entry.grid(row=1, column=0, padx=20, pady=10)

    correo_label = ctk.CTkLabel(ventana_crear_cuenta, text="Correo Electrónico:", font=("Helvetica", 16))
    correo_label.grid(row=2, column=0, sticky="w", pady=10, padx=20)
    correo_entry_crear = ctk.CTkEntry(ventana_crear_cuenta, font=("Helvetica", 16))
    correo_entry_crear.grid(row=3, column=0, padx=20, pady=10)

    contraseña_label = ctk.CTkLabel(ventana_crear_cuenta, text="Contraseña:", font=("Helvetica", 16))
    contraseña_label.grid(row=4, column=0, sticky="w", pady=10, padx=20)
    contraseña_entry_crear = ctk.CTkEntry(ventana_crear_cuenta, show="*", font=("Helvetica", 16))
    contraseña_entry_crear.grid(row=5, column=0, padx=20, pady=10)

    crear_cuenta_button = ctk.CTkButton(ventana_crear_cuenta, text="Crear Cuenta", command=lambda: crear_cuenta(nombre_entry.get(), correo_entry_crear.get(), contraseña_entry_crear.get()), font=("Helvetica", 16))
    crear_cuenta_button.grid(row=6, column=0, pady=30, padx=20, sticky="ew")

# Interfaz de Login
window = ctk.CTk()
window.title("Login - Port Gadget")
window.geometry("800x500")  # Tamaño más compacto y elegante

# Imagen desde URL
url_imagen = "https://i.pinimg.com/736x/3b/e9/bf/3be9bfb8065fe68708bd7c6abc0ba84c.jpg"  
response = requests.get(url_imagen)
image = Image.open(BytesIO(response.content))
image = image.resize((300, 300))  # Imagen más grande (300x300)
photo = ImageTk.PhotoImage(image)
image_label = ctk.CTkLabel(window, image=photo, text="")
image_label.pack(pady=20)

# Formulario de Login
login_frame = ctk.CTkFrame(window, corner_radius=15)  # Bordes redondeados
login_frame.pack(pady=20, padx=20)

correo_label = ctk.CTkLabel(login_frame, text="Correo Electrónico:", font=("Helvetica", 16))
correo_label.grid(row=0, column=0, sticky="w", pady=10, padx=20)
correo_entry = ctk.CTkEntry(login_frame, font=("Helvetica", 16), width=250, corner_radius=10)
correo_entry.grid(row=1, column=0, padx=20, pady=10)

contraseña_label = ctk.CTkLabel(login_frame, text="Contraseña:", font=("Helvetica", 16))
contraseña_label.grid(row=2, column=0, sticky="w", pady=10, padx=20)
contraseña_entry = ctk.CTkEntry(login_frame, show="*", font=("Helvetica", 16), width=250, corner_radius=10)
contraseña_entry.grid(row=3, column=0, padx=20, pady=10)

login_button = ctk.CTkButton(login_frame, text="Iniciar Sesión", command=login, font=("Helvetica", 16), width=250, corner_radius=10)
login_button.grid(row=4, column=0, pady=20, padx=20, sticky="ew")

crear_cuenta_button = ctk.CTkButton(login_frame, text="Crear Cuenta", command=mostrar_ventana_crear_cuenta, fg_color="#28a745", font=("Helvetica", 16), width=250, corner_radius=10)
crear_cuenta_button.grid(row=5, column=0, pady=10, padx=20, sticky="ew")

window.mainloop()