import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import psycopg2
import requests
from io import BytesIO

# Configuración de PostgreSQL
DATABASE_URL = "postgresql://usuario:contraseña@localhost:5432/tu_basedatos"

def verificar_credenciales(email, password):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email=%s AND password=%s", (email, password))
        usuario = cursor.fetchone()
        conn.close()
        return usuario is not None
    except Exception as e:
        messagebox.showerror("Error", f"Error de conexión: {e}")
        return False

def login():
    email = email_entry.get()
    password = password_entry.get()
    
    if verificar_credenciales(email, password):
        messagebox.showinfo("Éxito", "Inicio de sesión exitoso")
        window.destroy()
        mostrar_vista_principal()
    else:
        messagebox.showerror("Error", "Correo o contraseña incorrectos")

def mostrar_vista_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Panel Principal")
    ventana_principal.geometry("400x300")
    ventana_principal.configure(bg="#1e1e2e")
    
    bienvenida_label = tk.Label(ventana_principal, text="¡Bienvenido!", fg="white", bg="#1e1e2e", font=("Arial", 16, "bold"))
    bienvenida_label.pack(pady=20)
    
    cerrar_sesion_button = tk.Button(ventana_principal, text="Cerrar sesión", command=ventana_principal.destroy, bg="#ff4d4d", fg="white", font=("Arial", 12, "bold"))
    cerrar_sesion_button.pack(pady=20)
    
    ventana_principal.mainloop()

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
email_entry = tk.Entry(login_frame, font=("Arial", 12))
email_entry.grid(row=1, column=0, padx=10, pady=5, ipady=3)

tk.Label(login_frame, text="Contraseña:", fg="white", bg="#2e2e2e", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12))
password_entry.grid(row=3, column=0, padx=10, pady=5, ipady=3)

login_button = tk.Button(login_frame, text="Iniciar Sesión", command=login, bg="#007bff", fg="white", font=("Arial", 12, "bold"))
login_button.grid(row=4, column=0, pady=20, sticky="ew")

window.mainloop()
