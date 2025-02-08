import flet as ft
import sqlite3
import hashlib

def crear_conexion():
    conn = sqlite3.connect('usuarios.db')
    return conn

def crear_tabla():
    conn = crear_conexion()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT UNIQUE NOT NULL,
            contrasena TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hashear_contrasena(contrasena):
    return hashlib.sha256(contrasena.encode()).hexdigest()

def crear_cuenta(e):
    nombre_usuario = txt_nombre_usuario.value
    contrasena = txt_contrasena.value

    if nombre_usuario and contrasena:
        contrasena_hasheada = hashear_contrasena(contrasena)
        conn = crear_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (nombre_usuario, contrasena) VALUES (?, ?)", (nombre_usuario, contrasena_hasheada))
            conn.commit()
            lbl_mensaje.text = "Cuenta creada exitosamente."
            lbl_mensaje.color = "green"
            page.update()
        except sqlite3.IntegrityError:
            lbl_mensaje.text = "El nombre de usuario ya existe."
            lbl_mensaje.color = "red"
            page.update()
        finally:
            conn.close()
    else:
        lbl_mensaje.text = "Por favor, complete todos los campos."
        lbl_mensaje.color = "red"
        page.update()

def iniciar_sesion(e):
    nombre_usuario = txt_nombre_usuario.value
    contrasena = txt_contrasena.value

    if nombre_usuario and contrasena:
        contrasena_hasheada = hashear_contrasena(contrasena)
        conn = crear_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = ? AND contrasena = ?", (nombre_usuario, contrasena_hasheada))
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            page.clean()  # Limpia la página actual
            page.add(
                ft.Text(f"Bienvenido, {nombre_usuario}!", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                # Aquí puedes agregar el contenido relacionado con ciberseguridad
            )
        else:
            lbl_mensaje.text = "Nombre de usuario o contraseña incorrectos."
            lbl_mensaje.color = "red"
            page.update()
    else:
        lbl_mensaje.text = "Por favor, complete todos los campos."
        lbl_mensaje.color = "red"
        page.update()

def main(page: ft.Page):
    page.title = "Login"

    crear_tabla()

    global txt_nombre_usuario, txt_contrasena, lbl_mensaje  # Variables globales

    txt_nombre_usuario = ft.TextField(label="Nombre de usuario")
    txt_contrasena = ft.TextField(label="Contraseña", password=True)
    lbl_mensaje = ft.Text("")

    page.add(
        txt_nombre_usuario,
        txt_contrasena,
        ft.ElevatedButton("Crear cuenta", on_click=crear_cuenta),
        ft.ElevatedButton("Iniciar sesión", on_click=iniciar_sesion),
        lbl_mensaje,
    )

ft.app(target=main)