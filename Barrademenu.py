import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json  # Para guardar y cargar el historial de escaneos
import threading  # Para evitar bloquear la interfaz gráfica durante los escaneos

class ModernMenuBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.buttons = {}
        self.dropdown_menus = {}
        self.configure(fg_color="#2E3440", corner_radius=0)
        self.selected_button = None
        self.current_file = None
        self.scan_history = self.load_scan_history()  # Cargar el historial de escaneos
        self.fast_mode = True  # Modo rápido activado por defecto

    def add_menu(self, label, items):
        menu_button = ctk.CTkButton(
            self,
            text=label,
            fg_color="transparent",
            text_color="#D8DEE9",
            hover_color="#434C5E",
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

    def load_scan_history(self):
        """Carga el historial de escaneos desde un archivo JSON."""
        try:
            with open("scan_history.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_scan_history(self):
        """Guarda el historial de escaneos en un archivo JSON."""
        with open("scan_history.json", "w") as f:
            json.dump(self.scan_history, f, indent=4)  # Indentación para legibilidad

    def add_scan_to_history(self, scan_type, target, results):
        """Añade un escaneo al historial."""
        scan_entry = {
            "type": scan_type,
            "target": target,
            "results": results
        }
        self.scan_history.append(scan_entry)
        self.save_scan_history()  # Guardar el historial actualizado

# --- Ventanas y Funciones Auxiliares ---
def show_terms_and_conditions():
    """Muestra los términos y condiciones en una nueva ventana."""
    terms_window = ctk.CTkToplevel(app)
    terms_window.title("Términos y Condiciones")
    text_box = ctk.CTkTextbox(terms_window, wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    terms = """
    Aquí irían los términos y condiciones...
    (Este es solo un ejemplo)
    """
    text_box.insert("0.0", terms)
    text_box.configure(state=tk.DISABLED)  # Hacer el texto no editable

def show_license(license_type):
    """Muestra la licencia en una nueva ventana."""
    license_window = ctk.CTkToplevel(app)
    license_window.title(f"Licencia de Uso: {license_type}")
    text_box = ctk.CTkTextbox(license_window, wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    license_text = f"""
    Aquí iría la licencia de uso para {license_type}...
    (Este es solo un ejemplo)
    """
    text_box.insert("0.0", license_text)
    text_box.configure(state=tk.DISABLED)  # Hacer el texto no editable

# --- Funciones de Escaneo ---
def perform_scan(scan_type):
    """Realiza un escaneo (simulado) y guarda los resultados."""
    def run_scan():
        # Simulación del escaneo
        target = "example.com"  # Cambiar esto para permitir al usuario ingresar el objetivo
        results = f"Resultados del {scan_type} en {target}: [SIMULADO]"

        # Añadir al historial de escaneos
        menu_bar.add_scan_to_history(scan_type, target, results)

        # Mostrar los resultados en una ventana
        show_scan_results(scan_type, target, results)

    # Ejecutar el escaneo en un hilo para no bloquear la interfaz gráfica
    threading.Thread(target=run_scan).start()

def show_scan_results(scan_type, target, results):
    """Muestra los resultados del escaneo en una nueva ventana."""
    results_window = ctk.CTkToplevel(app)
    results_window.title(f"Resultados del {scan_type}")
    text_box = ctk.CTkTextbox(results_window, wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    text_box.insert("0.0", results)
    text_box.configure(state=tk.DISABLED)  # Hacer el texto no editable

def view_scan_history():
    """Muestra el historial de escaneos en una ventana."""
    history_window = ctk.CTkToplevel(app)
    history_window.title("Historial de Escaneos")
    text_box = ctk.CTkTextbox(history_window, wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    if menu_bar.scan_history:
        history_text = ""
        for entry in menu_bar.scan_history:
            history_text += f"Tipo: {entry['type']}\n"
            history_text += f"Objetivo: {entry['target']}\n"
            history_text += f"Resultados: {entry['results']}\n\n"
        text_box.insert("0.0", history_text)
    else:
        text_box.insert("0.0", "No hay escaneos en el historial.")
    text_box.configure(state=tk.DISABLED)  # Hacer el texto no editable

def toggle_fast_mode():
    """Activa/desactiva el modo rápido."""
    menu_bar.fast_mode = not menu_bar.fast_mode
    messagebox.showinfo("Modo Rápido/Detallado", f"Modo Rápido: {'Activado' if menu_bar.fast_mode else 'Desactivado'}")

def adjust_settings():
    """Muestra una ventana de configuración (simulada)."""
    settings_window = ctk.CTkToplevel(app)
    settings_window.title("Configuración")
    label = ctk.CTkLabel(settings_window, text="Aquí irían las opciones de configuración...")
    label.pack(padx=20, pady=20)

def show_help(help_topic):
    """Muestra una ventana de ayuda."""
    help_window = ctk.CTkToplevel(app)
    help_window.title(f"Ayuda: {help_topic}")
    text_box = ctk.CTkTextbox(help_window, wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    help_text = f"""
    Aquí iría la ayuda sobre {help_topic}...
    (Este es solo un ejemplo)
    """
    text_box.insert("0.0", help_text)
    text_box.configure(state=tk.DISABLED)  # Hacer el texto no editable

# --- Funciones de Manejo de Archivos ---
def new_scan():
    """Inicia un nuevo escaneo."""
    perform_scan("Nuevo Escaneo")

def open_report():
    """Abre un informe desde un archivo."""
    file_path = filedialog.askopenfilename(
        title="Abrir Informe",
        filetypes=[("Archivos de Informe", "*.report")]
    )
    if file_path:
        try:
            with open(file_path, "r") as file:
                report_content = file.read()
                show_scan_results("Informe Abierto", file_path, report_content)
                app.current_file = file_path
        except Exception as e:
            messagebox.showerror("Error al abrir el archivo", str(e))

def save_report():
    """Guarda el informe actual."""
    if app.current_file:
        try:
            # Simulación: obtener contenido del "informe" desde el historial
            last_scan = menu_bar.scan_history[-1] if menu_bar.scan_history else None
            report_content = f"Último Escaneo:\n{last_scan}" if last_scan else "No hay datos para guardar."

            with open(app.current_file, "w") as file:
                file.write(report_content)
            messagebox.showinfo("Guardar Informe", f"Informe guardado en {app.current_file}")
        except Exception as e:
            messagebox.showerror("Error al guardar el archivo", str(e))
    else:
        save_report_as()

def save_report_as():
    """Guarda el informe actual como un nuevo archivo."""
    file_path = filedialog.asksaveasfilename(
        title="Guardar Informe Como",
        defaultextension=".report",
        filetypes=[("Archivos de Informe", "*.report")]
    )
    if file_path:
        try:
            # Simulación: obtener contenido del "informe" desde el historial
            last_scan = menu_bar.scan_history[-1] if menu_bar.scan_history else None
            report_content = f"Último Escaneo:\n{last_scan}" if last_scan else "No hay datos para guardar."

            with open(file_path, "w") as file:
                file.write(report_content)
            messagebox.showinfo("Guardar Informe", f"Informe guardado en {file_path}")
            app.current_file = file_path
        except Exception as e:
            messagebox.showerror("Error al guardar el archivo", str(e))

def export_results():
    """Exporta los resultados del escaneo (simulado)."""
    messagebox.showinfo("Exportar Resultados", "Exportando resultados a CSV/PDF (simulado)...")

def use_tool(tool_name):
    """Simula el uso de una herramienta."""
    messagebox.showinfo("Herramienta", f"Usando la herramienta: {tool_name} (simulado)...")

def send_report_by_email():
    """Simula el envío de un informe por correo electrónico."""
    messagebox.showinfo("Enviar Informe", "Enviando informe por correo electrónico (simulado)...")

# --- Initial window settings ---
app = ctk.CTk()
app.title("Main Menu")
app.geometry("800x600")

# --- Theme settings ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# --- Define menu items and commands ---
menu_items = {
    "1 Archivo": {
        "🆕 Nuevo Escaneo": new_scan,
        "📂 Abrir Informe": open_report,
        "💾 Guardar Informe": save_report,
        "Guardar Informe Como...": save_report_as,
        "📜 Exportar Resultados (CSV, PDF)": export_results,
        "🚪 Salir": app.quit,
    },
    "2 Escaneo": {
        "🎯 Escaneo Rápido": lambda: perform_scan("Escaneo Rápido"),
        "🔎 Escaneo Completo": lambda: perform_scan("Escaneo Completo"),
        "Escaneo Personalizado": lambda: perform_scan("Escaneo Personalizado"),
        "🌐 Escaneo Avanzado (TCP y UDP)": lambda: perform_scan("Escaneo Avanzado"),
        "🏴‍☠️ Detección de Servicios y SO": lambda: perform_scan("Detección de Servicios y SO"),
    },
    "3 Configuración": {
        "⚡ Modo Rápido / Detallado": toggle_fast_mode,
        "🎨 Personalización de la Interfaz": adjust_settings,
        "🌍 Ajustes de Red": adjust_settings,
        "📡 Definir Puertos por Defecto": adjust_settings,
        "Actualizar Base de Datos de Servicios": adjust_settings,
    },
    "4 Herramientas": {
        "🕵️‍♂️ Análisis de Vulnerabilidades": lambda: use_tool("Análisis de Vulnerabilidades"),
        "🛑 Detección de Firewall": lambda: use_tool("Detección de Firewall"),
        "🔐 Verificación SSL/TLS": lambda: use_tool("Verificación SSL/TLS"),
        "🌐 Búsqueda WHOIS de Dominio/IP": lambda: use_tool("Búsqueda WHOIS de Dominio/IP"),
    },
    "5 Informes": {
        "📊 Ver Historial de Escaneos": view_scan_history,
        "📋 Generar Informe Detallado": view_scan_history,
        "📥 Exportar a CSV / PDF": view_scan_history,
        "📤 Enviar Informe por Correo": send_report_by_email,
    },
    "6 Ayuda": {
        "Guía de Uso": lambda: show_help("Guía de Uso"),
        "🎓 Atajos de Teclado": lambda: show_help("Atajos de Teclado"),
        "❓ Soporte Técnico": lambda: show_help("Soporte Técnico"),
        "🔍 Acerca de Este Software": lambda: show_help("Acerca de Este Software"),
    },
    "7 Licencia": {
        "📜 Términos y Condiciones": show_terms_and_conditions,
        "🏛 Licencia de Uso": show_license,
        "⚖ Aviso Legal": lambda: show_license("Aviso Legal"),
        "🛡 Política de Privacidad": lambda: show_license("Política de Privacidad"),
    }
}

# --- Add menus to the menu bar ---
menu_bar = ModernMenuBar(app)
menu_bar.pack(fill=tk.X)

for label, items in menu_items.items():
    menu_bar.add_menu(label, items)

# --- Start the application ---
app.mainloop()
