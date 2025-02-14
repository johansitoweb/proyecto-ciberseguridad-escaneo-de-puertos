import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

def login():
    email = email_entry.get()
    password = password_entry.get()

    if email == "usuario@ejemplo.com" and password == "contraseña":
        # Login exitoso
        window.destroy()  # Cierra la ventana de login
        mostrar_vista_principal()
    else:
        # Error en el login
        messagebox.showerror("Error", "Correo electrónico o contraseña incorrectos.")

def mostrar_vista_principal():
    ventana_principal = tk.Tk()
    ventana_principal.title("Vista principal")

    bienvenida_label = tk.Label(ventana_principal, text="¡Bienvenido!")
    bienvenida_label.pack(pady=20)

    cerrar_sesion_button = tk.Button(ventana_principal, text="Cerrar sesión", command=ventana_principal.destroy)
    cerrar_sesion_button.pack()

    ventana_principal.mainloop()

window = tk.Tk()
window.title("Login")

# Imagen desde URL
url_imagen = "https://www.easygifanimator.net/images/samples/video-to-gif-sample.gif"  # Reemplaza con la URL de tu imagen
response = requests.get(url_imagen)
image = Image.open(BytesIO(response.content))
photo = ImageTk.PhotoImage(image)
image_label = tk.Label(window, image=photo)
image_label.grid(row=0, column=1, padx=20, pady=20)
# Formulario de login
login_frame = tk.Frame(window)
login_frame.grid(row=0, column=0, padx=20, pady=20)

email_label = tk.Label(login_frame, text="Correo electrónico:")
email_label.grid(row=0, column=0, sticky="w")

email_entry = tk.Entry(login_frame)
email_entry.grid(row=1, column=0, sticky="ew")

password_label = tk.Label(login_frame, text="Contraseña:")
password_label.grid(row=2, column=0, sticky="w")

password_entry = tk.Entry(login_frame, show="*")
password_entry.grid(row=3, column=0, sticky="ew")

login_button = tk.Button(login_frame, text="Entrar", command=login)
login_button.grid(row=4, column=0, sticky="ew")

window.mainloop()