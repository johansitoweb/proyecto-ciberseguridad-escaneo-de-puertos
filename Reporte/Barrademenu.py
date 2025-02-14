import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

class ModernMenuBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.buttons = {}
        self.dropdown_menus = {}  # Almacena los menús desplegables para seguimiento
        self.configure(fg_color="#2E3440", corner_radius=0)  # Color de fondo
        self.selected_button = None  # Botón seleccionado actualmente

    def add_menu(self, label, items):
        menu_button = ctk.CTkButton(
            self,
            text=label,
            fg_color="transparent",  # Fondo transparente
            text_color="#D8DEE9",  # Color del texto
            hover_color="#434C5E",  # Color al pasar el ratón
            command=lambda items=items, label=label: self.show_dropdown(items, label, menu_button),
        )
        menu_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.buttons[label] = menu_button

    def show_dropdown(self, items, label, menu_button):
        # Destruye el menú desplegable anterior si existe
        if hasattr(self, "dropdown_menu") and self.dropdown_menu.winfo_exists():
            self.dropdown_menu.destroy()

        # Restablece el color del botón previamente seleccionado
        if self.selected_button:
            self.selected_button.configure(fg_color="transparent")

        # Resalta el botón seleccionado
        menu_button.configure(fg_color="#007BFF")
        self.selected_button = menu_button

        self.dropdown_menu = ctk.CTkToplevel(self.master)
        self.dropdown_menu.geometry(f"200x{len(items) * 40}")
        self.dropdown_menu.overrideredirect(True)  # Oculta la barra de título
        self.dropdown_menu.configure(bg="#2E3440")  # Color de fondo

        x = self.buttons[label].winfo_rootx()
        y = self.buttons[label].winfo_rooty() + self.buttons[label].winfo_height()
        self.dropdown_menu.geometry(f"+{x}+{y}")

        # Almacena el menú desplegable actual
        self.dropdown_menus[label] = self.dropdown_menu

        for item_label, command in items.items():
            item_button = ctk.CTkButton(
                self.dropdown_menu,
                text=item_label,
                fg_color="transparent",
                text_color="#D8DEE9",
                hover_color="#434C5E",
                command=lambda command=command: self.menu_item_action(command),  # Pasa el comando
                corner_radius=0,  # Ensure buttons are rectangular
                anchor="w",  # Left-align the text
            )
            item_button.pack(fill=tk.X)

    def menu_item_action(self, command):
         # Reset background of previously selected button
        if self.selected_button:
            self.selected_button.configure(fg_color="transparent")
        # Destroy the dropdown menu
        if hasattr(self, "dropdown_menu") and self.dropdown_menu.winfo_exists():
            self.dropdown_menu.destroy()
        # Execute the command
        command()

# Initial window settings
app = ctk.CTk()
app.title("Main Menu")
app.geometry("800x600")

# Theme settings
ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("green")  # Color theme

# Menu action handler
def menu_action(action):
    print(f"Selected action: {action}")

# Create modern menu bar
menu_bar = ModernMenuBar(app)
menu_bar.pack(fill=tk.X)

# Define menu items and commands
menu_items = {
    "1 Archivo": {
        "🆕 Nuevo Escaneo": lambda: menu_action("Nuevo Escaneo"),
        "📂 Abrir Informe": lambda: menu_action("Abrir Informe"),
        "💾 Guardar Informe": lambda: menu_action("Guardar Informe"),
        "📜 Exportar Resultados (CSV, PDF)": lambda: menu_action("Exportar Resultados"),
        "🚪 Salir": app.quit,
    },
    "2 Escaneo": {
        "🎯 Escaneo Rápido": lambda: menu_action("Escaneo Rápido"),
        "🔎 Escaneo Completo": lambda: menu_action("Escaneo Completo"),
        "Escaneo Personalizado": lambda: menu_action("Escaneo Personalizado"),
        "🌐 Escaneo Avanzado (TCP y UDP)": lambda: menu_action("Escaneo Avanzado"),
        "🏴‍☠️ Detección de Servicios y SO": lambda: menu_action("Detección de Servicios y SO"),
    },
    "3 Configuración": {
        "⚡ Modo Rápido / Detallado": lambda: menu_action("Modo Rápido / Detallado"),
        "🎨 Personalización de la Interfaz": lambda: menu_action("Personalización de la Interfaz"),
        "🌍 Ajustes de Red": lambda: menu_action("Ajustes de Red"),
        "📡 Definir Puertos por Defecto": lambda: menu_action("Definir Puertos por Defecto"),
        "Actualizar Base de Datos de Servicios": lambda: menu_action("Actualizar Base de Datos de Servicios"),
    },
    "4 Herramientas": {
        "🕵️‍♂️ Análisis de Vulnerabilidades": lambda: menu_action("Análisis de Vulnerabilidades"),
        "🛑 Detección de Firewall": lambda: menu_action("Detección de Firewall"),
        "🔐 Verificación SSL/TLS": lambda: menu_action("Verificación SSL/TLS"),
        "🌐 Búsqueda WHOIS de Dominio/IP": lambda: menu_action("Búsqueda WHOIS de Dominio/IP"),
    },
    "5 Informes": {
        "📊 Ver Historial de Escaneos": lambda: menu_action("Ver Historial de Escaneos"),
        "📋 Generar Informe Detallado": lambda: menu_action("Generar Informe Detallado"),
        "📥 Exportar a CSV / PDF": lambda: menu_action("Exportar a CSV / PDF"),
        "📤 Enviar Informe por Correo": lambda: menu_action("Enviar Informe por Correo"),
    },
    "6 Ayuda": {
        "Guía de Uso": lambda: menu_action("Guía de Uso"),
        "🎓 Atajos de Teclado": lambda: menu_action("Atajos de Teclado"),
        "❓ Soporte Técnico": lambda: menu_action("Soporte Técnico"),
        "🔍 Acerca de Este Software": lambda: menu_action("Acerca de Este Software"),
    },
    "7 Licencia": {
        "📜 Términos y Condiciones": lambda: menu_action("Términos y Condiciones"),
        "🏛 Licencia de Uso": lambda: menu_action("Licencia de Uso"),
        "⚖ Aviso Legal": lambda: menu_action("Aviso Legal"),
        "🛡 Política de Privacidad": lambda: menu_action("Política de Privacidad"),
    }
}

# Add menus to the menu bar
for label, items in menu_items.items():
    menu_bar.add_menu(label, items)

# Start the application
app.mainloop()
