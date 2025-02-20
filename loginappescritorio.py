import flet as ft
import psycopg2

# Configuración de PostgreSQL
DATABASE_URL = "postgresql://soportetech:aeiou270@localhost:5432/Port-Gadget"

def verificar_credenciales(correo, contraseña):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE correo=%s AND contraseña=%s",
            (correo, contraseña),
        )
        usuario = cursor.fetchone()
        conn.close()
        return usuario is not None
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False

def crear_cuenta(nombre, correo, contraseña):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contraseña) VALUES (%s, %s, %s)",
            (nombre, correo, contraseña),
        )
        conn.commit()
        conn.close()
        return True, "Cuenta creada exitosamente"
    except Exception as e:
        return False, f"Error al crear la cuenta: {e}"

def main(page: ft.Page):
    page.title = "Port-Gadget"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = ft.colors.WHITE

    # URLs de las imágenes
    imagen_login = "https://images.nintendolife.com/dc28963e01aeb/1280x720.jpg"
    imagen_crear_cuenta = "https://i.pinimg.com/736x/3b/e9/bf/3be9bfb8065fe68708bd7c6abc0ba84c.jpg"

    # Imagen grande a la izquierda
    image = ft.Image(
        src=imagen_login,
        width=400,
        height=600,
        fit=ft.ImageFit.COVER,
        border_radius=ft.border_radius.all(20),
    )

    # Texto de bienvenida (en una sola línea)
    welcome_text = ft.Text(
        "Port-Gadget!",
        size=40,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.BLACK,  # Color inicial del texto
    )

    # Función para crear un TextField con estilo
    def create_text_field(label, password=False):
        return ft.TextField(
            label=label,
            width=300,
            password=password,
            label_style=ft.TextStyle(color=ft.colors.WHITE if page.bgcolor == ft.colors.BLACK else ft.colors.BLACK),
            cursor_color=ft.colors.WHITE if page.bgcolor == ft.colors.BLACK else ft.colors.BLACK,
            text_style=ft.TextStyle(color=ft.colors.WHITE if page.bgcolor == ft.colors.BLACK else ft.colors.BLACK),
            border_color=ft.colors.WHITE if page.bgcolor == ft.colors.BLACK else ft.colors.BLACK,
        )

    # Formulario de Login
    correo_entry = create_text_field("Correo Electrónico")
    contraseña_entry = create_text_field("Contraseña", password=True)
    login_button = ft.ElevatedButton(text="Iniciar Sesión", width=300, bgcolor=ft.colors.BLUE_800, color=ft.colors.WHITE)
    crear_cuenta_button = ft.TextButton(text="Crear Cuenta", on_click=lambda e: toggle_form(e), width=300, style=ft.ButtonStyle(color=ft.colors.GREEN))

    login_column = ft.Column(
        [
            welcome_text,
            correo_entry,
            contraseña_entry,
            login_button,
            crear_cuenta_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    # Formulario de Crear Cuenta
    nombre_entry = create_text_field("Nombre")
    correo_entry_crear = create_text_field("Correo Electrónico")
    contraseña_entry_crear = create_text_field("Contraseña", password=True)
    crear_cuenta_button_confirm = ft.ElevatedButton(text="Crear Cuenta", width=300, bgcolor=ft.colors.BLUE_800, color=ft.colors.WHITE)
    volver_login_button = ft.TextButton(text="Volver al Login", on_click=lambda e: toggle_form(e), width=300, style=ft.ButtonStyle(color=ft.colors.RED))

    crear_cuenta_column = ft.Column(
        [
            welcome_text,
            nombre_entry,
            correo_entry_crear,
            contraseña_entry_crear,
            crear_cuenta_button_confirm,
            volver_login_button,
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )

    # Contenedor animado para alternar entre login y crear cuenta
    animated_switcher = ft.AnimatedSwitcher(
        content=login_column,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=500,
        reverse_duration=500,
        switch_in_curve=ft.AnimationCurve.EASE_IN_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN_OUT,
    )

    # Contenedor principal
    main_container = ft.Row(
        [
            image,
            ft.Container(
                content=animated_switcher,
                padding=20,
                width=400,
                height=600,
                alignment=ft.alignment.center,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=50,
    )

    # Función para alternar entre login y crear cuenta
    def toggle_form(e):
        if animated_switcher.content == login_column:
            # Cambiar a formulario de crear cuenta
            animated_switcher.content = crear_cuenta_column
            page.bgcolor = ft.colors.BLACK
            welcome_text.color = ft.colors.WHITE  # Cambiar el color del texto a blanco
            image.src = imagen_crear_cuenta  # Cambiar la imagen
        else:
            # Cambiar a formulario de login
            animated_switcher.content = login_column
            page.bgcolor = ft.colors.WHITE
            welcome_text.color = ft.colors.BLACK  # Cambiar el color del texto a negro
            image.src = imagen_login  # Cambiar la imagen

        # Actualizar el estilo de los TextField
        for entry in [correo_entry, contraseña_entry, nombre_entry, correo_entry_crear, contraseña_entry_crear]:
            entry.label_style = ft.TextStyle(color=ft.colors.WHITE if page.bgcolor == ft.colors.BLACK else ft.colors.BLACK)
            entry.cursor_color = ft.colors.WHITE if page.bgcolor == ft.colors.BLACK else ft.colors.BLACK
            entry.text_style = ft.TextStyle(color=ft.colors.WHITE if page.bgcolor == ft.colors.BLACK else ft.colors.BLACK)
            entry.border_color = ft.colors.WHITE if page.bgcolor == ft.colors.BLACK else ft.colors.BLACK

        page.update()

    # Función para manejar el inicio de sesión
    def login_click(e):
        correo = correo_entry.value
        contraseña = contraseña_entry.value

        if verificar_credenciales(correo, contraseña):
            page.snack_bar = ft.SnackBar(ft.Text("Inicio de sesión exitoso"))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Correo o contraseña incorrectos"))
            page.snack_bar.open = True
        page.update()

    # Función para manejar la creación de cuenta
    def crear_cuenta_click(e):
        nombre = nombre_entry.value
        correo = correo_entry_crear.value
        contraseña = contraseña_entry_crear.value

        if nombre and correo and contraseña:
            success, message = crear_cuenta(nombre, correo, contraseña)
            page.snack_bar = ft.SnackBar(ft.Text(message))
            page.snack_bar.open = True
            if success:
                toggle_form(e)  # Volver al formulario de login
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, complete todos los campos"))
            page.snack_bar.open = True
        page.update()

    # Asignar las funciones a los botones
    login_button.on_click = login_click
    crear_cuenta_button_confirm.on_click = crear_cuenta_click

    # Añadir el contenedor principal a la página
    page.add(main_container)

ft.app(target=main)