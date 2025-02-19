import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import json  # Para guardar y cargar el historial de escaneos
import threading  # Para evitar bloquear la interfaz gráfica durante los escaneos
import logging
import socket
from scapy.all import IP, IPv6, TCP, sr1, RandShort, UDP
import subprocess
import nmap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importaciones de las funcionalidades avanzadas (Comentadas hasta que se implementen)
#import anomaly_detection
#import cloud_scanning
#import conetbase
#import shodan_integration
#import stealth_mode
#import Report

# Configuración del registro
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# Reemplaza con mis credenciales de PostgreSQL
DATABASE_URL = "postgresql://soportetech:aeiou270@localhost:5432/Port-Gadget"

# Crear la conexión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ModernMenuBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master
        self.buttons = {}
        self.dropdown_menus = {}
        self.configure(fg_color="#2E3440", corner_radius=0)
        self.selected_button = None
        self.current_file = None
        self.scan_history = self.load_scan_history()  # Cargo el historial de escaneos
        self.fast_mode = True  # Modo rápido activado por defecto
        self.default_ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5060, 5900, 8080]

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
        # Restablezco el color del botón previamente seleccionado
        if self.selected_button:
            self.selected_button.configure(fg_color="transparent")
        # Destruyo el menú desplegable
        if hasattr(self, "dropdown_menu") and self.dropdown_menu.winfo_exists():
            self.dropdown_menu.destroy()
        # Ejecuto el comando
        command()

    def load_scan_history(self):
        """Cargo el historial de escaneos desde un archivo JSON."""
        try:
            with open("scan_history.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_scan_history(self):
        """Guardo el historial de escaneos en un archivo JSON."""
        with open("scan_history.json", "w") as f:
            json.dump(self.scan_history, f, indent=4)  # Indentación para legibilidad

    def add_scan_to_history(self, scan_type, target, results):
        """Añado un escaneo al historial."""
        scan_entry = {
            "type": scan_type,
            "target": target,
            "results": results
        }
        self.scan_history.append(scan_entry)
        self.save_scan_history()  # Guardo el historial actualizado

# --- Ventanas y Funciones Auxiliares ---
def show_terms_and_conditions():
    """Muestro los términos y condiciones en una nueva ventana."""
    terms_window = ctk.CTkToplevel(app)
    terms_window.title("Términos y Condiciones")
    text_box = ctk.CTkTextbox(terms_window, wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    terms = """
    Aquí irían los términos y condiciones...
    (Este es solo un ejemplo)
    """
    text_box.insert("0.0", terms)
    text_box.configure(state=tk.DISABLED)  # Hago el texto no editable

def show_license():
    """Muestro la licencia en una nueva ventana."""
    license_window = ctk.CTkToplevel(app)
    license_window.title("Licencia de Uso")
    text_box = ctk.CTkTextbox(license_window, wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # License agreement text
    license_text = """
 LICENCIA DE USO Y DISTRIBUCIÓN

 1. [INFORMACIÓN GENERAL]
*Nombre del Proyecto: Port-Gadget: Escáner de Puertos Profesional  
*Autores: Moisés, Keilin, Johan  
*Tipo de Software: Herramienta de ciberseguridad para escaneo de puertos y auditoría de redes  
*Fecha de Emisión: [10/02/2025]  

 2. [ALCANCE Y PERMISOS]
Esta licencia establece los términos y condiciones bajo los cuales se permite el uso, modificación y distribución del software Port-Gadget.

 2.[1 Permisos Concedidos]
Se permite a los usuarios:
✅ Usar este software con fines educativos, investigativos y de auditoría de seguridad en redes propias o autorizadas.  
✅ Modificar el código fuente para personalización y mejora del software.  
✅ Distribuir versiones modificadas del software, siempre que se incluya esta licencia y se otorgue crédito a los autores originales.  
✅ Integrar este software en sistemas empresariales o gubernamentales bajo cumplimiento legal.  

 2.[2 Restricciones]
🚫 **Prohibido su uso para actividades ilegales o sin autorización del propietario de la red. 
🚫 No se permite eliminar, modificar o alterar créditos de los autores originales sin su consentimiento.  
🚫 No se permite su reventa sin una licencia comercial adquirida de los autores originales.  
🚫 El uso de este software en pruebas de penetración debe contar con autorización expresa del propietario del sistema objetivo.  

 3. [RESPONSABILIDAD Y DESCARGO DE RESPONSABILIDAD]
*Port-Gadget es una herramienta desarrollada con fines educativos y de auditoría de seguridad.

📌 Uso bajo responsabilidad del usuario: Los autores no se hacen responsables de daños directos o indirectos derivados del uso indebido de este software.

📌 Cumplimiento legal: El usuario es responsable de asegurarse de que el uso de Port-Gadget cumpla con las leyes y regulaciones de su jurisdicción.

📌 Garantía limitada: Este software se proporciona "TAL CUAL", sin garantías explícitas o implícitas de funcionamiento o seguridad.

 4. [SEGURIDAD Y PRIVACIDAD]
Para garantizar la seguridad y privacidad en el uso de Port-Gadget, se recomienda:
🔹 No ejecutar el software en redes públicas sin autorización.  
🔹 No compartir datos de escaneo sin consentimiento de los interesados.  
🔹 No almacenar información confidencial en sistemas inseguros.  

 5. [LICENCIAMIENTO Y MODIFICACIONES]
Este software se publica bajo la licencia MIT con restricciones adicionales mencionadas en la sección 2.  
Los usuarios pueden contribuir al desarrollo del software a través de mejoras y correcciones, siempre respetando los términos de esta licencia.  

 6. [CONTACTO]
Para consultas sobre licenciamiento, colaboraciones o adquisición de una licencia comercial, contactar a los desarrolladores:  
📩 [escaneodepuertos27@gmail.com]  

---

*Moisés, Keilin y Johan agradecen tu interés en Port-Gadget y recuerdan que la ciberseguridad es responsabilidad de todos.

🚀 ¡Hack the system, but ethically! 🚀
    """

    text_box.insert("0.0", license_text)
    text_box.configure(state=tk.DISABLED)  # Hago el texto no editable

def adjust_interface():
    """Muestro una ventana para personalizar la interfaz (simulada)."""
    settings_window = ctk.CTkToplevel(app)
    settings_window.title("Personalización de la Interfaz")
    label = ctk.CTkLabel(settings_window, text="Aquí irían las opciones de personalización de la interfaz aquí...")
    label.pack(padx=20, pady=20)

# --- Funciones de Escaneo ---
def perform_scan(scan_type):
    """Realizo un escaneo (simulado) y guardo los resultados."""
    def run_scan():
        # Simulación del escaneo
        target = "example.com"  # Cambiar esto para permitir al usuario ingresar el objetivo
        results = f"Resultados del {scan_type} en {target}: [SIMULADO]"
        # Añado al historial de escaneos
        menu_bar.add_scan_to_history(scan_type, target, results)
        # Muestro los resultados en la consola de la interfaz
        insert_to_console(results)

    # Ejecuto el escaneo en un hilo para no bloquear la interfaz gráfica
    threading.Thread(target=run_scan).start()

def show_scan_results(scan_type, target, results):
    """Muestro los resultados del escaneo en una nueva ventana."""
    results_window = ctk.CTkToplevel(app)
    results_window.title(f"Resultados del {scan_type}")
    text_box = ctk.CTkTextbox(results_window, wrap=tk.WORD)
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    text_box.insert("0.0", results)
    text_box.configure(state=tk.DISABLED)  # Hago el texto no editable

def view_scan_history():
    """Muestro el historial de escaneos en una ventana."""
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
    text_box.configure(state=tk.DISABLED)  # Hago el texto no editable

def toggle_fast_mode():
    """Activo/desactivo el modo rápido."""
    menu_bar.fast_mode = not menu_bar.fast_mode
    messagebox.showinfo("Modo Rápido/Detallado", f"Modo Rápido: {'Activado' if menu_bar.fast_mode else 'Desactivado'}")

def adjust_network_settings():
    """Muestro una ventana para ajustar la configuración de red."""
    settings_window = ctk.CTkToplevel(app)
    settings_window.title("Ajustes de Red Avanzados")

    # Main frame to hold settings
    frame = ctk.CTkFrame(settings_window)
    frame.pack(padx=20, pady=20, fill="both", expand=True)

    # 1. Timeout Configuration
    timeout_label = ctk.CTkLabel(frame, text="Timeout de Escaneo (segundos):")
    timeout_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
    timeout_entry = ctk.CTkEntry(frame)
    timeout_entry.insert(0, "2")  # Default timeout
    timeout_entry.grid(row=0, column=1, padx=5, pady=5, sticky="e")

    # 2. Interface Selection
    interface_label = ctk.CTkLabel(frame, text="Interfaz de Red:")
    interface_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    interface_options = ["eth0", "wlan0", "en0", "auto"]  # Example interfaces, "auto" to let the system decide
    interface_combobox = ctk.CTkComboBox(frame, values=interface_options)
    interface_combobox.set("auto")  # Default selection
    interface_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="e")

    # 3. Packet Fragmentation
    fragmentation_var = tk.BooleanVar(value=False)
    fragmentation_check = ctk.CTkCheckBox(frame, text="Habilitar Fragmentación de Paquetes", variable=fragmentation_var)
    fragmentation_check.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    # 4. Source Port Range
    src_port_label = ctk.CTkLabel(frame, text="Rango de Puertos de Origen (min-max):")
    src_port_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
    src_port_min_entry = ctk.CTkEntry(frame)
    src_port_min_entry.insert(0, "49152")  # Example ephemeral port range start
    src_port_min_entry.grid(row=3, column=1, padx=2, pady=5, sticky="w")
    src_port_max_entry = ctk.CTkEntry(frame)
    src_port_max_entry.insert(0, "65535")  # Example ephemeral port range end
    src_port_max_entry.grid(row=3, column=2, padx=2, pady=5, sticky="e")

    # 5. Number of Retries
    retries_label = ctk.CTkLabel(frame, text="Número de Reintentos:")
    retries_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
    retries_entry = ctk.CTkEntry(frame)
    retries_entry.insert(0, "3")  # Default retries
    retries_entry.grid(row=4, column=1, padx=5, pady=5, sticky="e")

    # 6. TOS (Type of Service) Configuration
    tos_label = ctk.CTkLabel(frame, text="Valor de TOS (0-255):")
    tos_label.grid(row=5, column=0, padx=5, pady=5, sticky="w")
    tos_entry = ctk.CTkEntry(frame)
    tos_entry.insert(0, "0")  # Default TOS value
    tos_entry.grid(row=5, column=1, padx=5, pady=5, sticky="e")

    # Function to save settings
    def save_settings():
        try:
            timeout = int(timeout_entry.get())
            selected_interface = interface_combobox.get()
            fragmentation = fragmentation_var.get()
            src_port_min = int(src_port_min_entry.get())
            src_port_max = int(src_port_max_entry.get())
            retries = int(retries_entry.get())
            tos = int(tos_entry.get())

            # Validation for port range
            if not (0 <= src_port_min <= 65535 and 0 <= src_port_max <= 65535 and src_port_min <= src_port_max):
                raise ValueError("Rango de puertos inválido.")

            # Validation for TOS value
            if not 0 <= tos <= 255:
                raise ValueError("Valor de TOS inválido (0-255).")

            # Save settings or apply them to the scan configuration
            settings = {
                "timeout": timeout,
                "interface": selected_interface,
                "fragmentation": fragmentation,
                "src_port_min": src_port_min,
                "src_port_max": src_port_max,
                "retries": retries,
                "tos": tos
            }

            # Display a confirmation message
            messagebox.showinfo("Ajustes Guardados", f"Ajustes guardados:\n{settings}")
            settings_window.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    # Save Button
    save_button = ctk.CTkButton(frame, text="Guardar", command=save_settings)
    save_button.grid(row=6, column=0, columnspan=3, padx=5, pady=10)

def update_service_database():
    """Muestro una ventana para actualizar la base de datos de servicios (simulada)."""
    settings_window = ctk.CTkToplevel(app)
    settings_window.title("Actualizar Base de Datos de Servicios")

    def update_database():
        # Pruebo conexión
        try:
            with engine.connect():
                print("Conectado a PostgreSQL correctamente")
                messagebox.showinfo("Base de datos", "Conectado a PostgreSQL correctamente")
        except Exception as e:
            print(f"Error conectando a PostgreSQL: {e}")
            messagebox.showerror("Base de datos", f"Error conectando a PostgreSQL: {e}")

    button_save = ctk.CTkButton(settings_window, text="Actualizar", command=update_database)
    button_save.pack(padx=10, pady=10)

def define_default_ports():
    """Permito al usuario definir los puertos por defecto."""
    ports_window = ctk.CTkToplevel(app)
    ports_window.title("Definir Puertos por Defecto")

    label = ctk.CTkLabel(ports_window, text="Ingrese los puertos separados por comas:")
    label.pack(padx=10, pady=5)

    entry_ports = ctk.CTkEntry(ports_window)
    entry_ports.insert(0, ", ".join(map(str, menu_bar.default_ports)))  # Muestro los puertos actuales
    entry_ports.pack(padx=10, pady=5)

    def save_ports():
        try:
            ports = [int(port.strip()) for port in entry_ports.get().split(",")]
            menu_bar.default_ports = ports
            messagebox.showinfo("Éxito", "Puertos por defecto actualizados.")
            ports_window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Ingrese solo números enteros separados por comas.")

    button_save = ctk.CTkButton(ports_window, text="Guardar", command=save_ports)
    button_save.pack(padx=10, pady=10)

def show_help(help_topic):
    """Muestro una ventana de ayuda con información detallada."""
    help_window = ctk.CTkToplevel(app)
    help_window.title(f"Ayuda: {help_topic}")
    help_window.geometry("800x600")  # Tamaño más grande para la ventana de ayuda

    # --- Contenedor principal ---
    main_frame = ctk.CTkFrame(help_window)
    main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # --- Título del tema de ayuda ---
    title_label = ctk.CTkLabel(main_frame, text=help_topic, font=ctk.CTkFont(size=18, weight="bold"))
    title_label.pack(pady=(0, 10))  # Espacio inferior

    # --- Texto de ayuda ---
    help_texts = {
        "Guía de Uso": "Aquí encontrarás instrucciones detalladas sobre cómo utilizar Port-Gadget. Aprenderás a realizar escaneos, interpretar los resultados y personalizar la herramienta para tus necesidades.",
        "Atajos de Teclado": "Lista de atajos de teclado para facilitar la navegación y el uso de las funciones más comunes de Port-Gadget.",
        "Soporte Técnico": "Información sobre cómo contactar al equipo de soporte técnico para resolver cualquier problema o duda que tengas sobre el uso de Port-Gadget.",
        "Acerca de Este Software": "Información sobre la versión actual de Port-Gadget, los autores y la licencia bajo la cual se distribuye."
    }

    help_text = help_texts.get(help_topic, "No hay información disponible para este tema.")
    text_box = ctk.CTkTextbox(main_frame, wrap=tk.WORD, state="normal", height=200)
    text_box.insert("0.0", help_text)
    text_box.configure(state="disabled")
    text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # --- Sección específica para atajos de teclado ---
    if help_topic == "Atajos de Teclado":
        shortcuts = {
            "Nuevo Escaneo": "Ctrl+N",
            "Abrir Informe": "Ctrl+O",
            "Guardar Informe": "Ctrl+S",
            "Salir": "Ctrl+Q"
        }

        shortcuts_text = "\n".join(f"{key}: {value}" for key, value in shortcuts.items())
        shortcuts_label = ctk.CTkLabel(main_frame, text="Atajos de Teclado:", font=ctk.CTkFont(weight="bold"))
        shortcuts_label.pack(pady=(10, 0))

        shortcuts_textbox = ctk.CTkTextbox(main_frame, wrap=tk.WORD, state="normal", height=100)
        shortcuts_textbox.insert("0.0", shortcuts_text)
        shortcuts_textbox.configure(state="disabled")
        shortcuts_textbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # --- Botón de cierre ---
    close_button = ctk.CTkButton(main_frame, text="Cerrar", command=help_window.destroy)
    close_button.pack(pady=10)

# --- Funciones de Manejo de Archivos ---
def new_scan():
    """Inicio un nuevo escaneo."""
    perform_scan("Nuevo Escaneo")

def open_report():
    """Abro un informe desde un archivo."""
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
    """Guardo el informe actual."""
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
    """Guardo el informe actual como un nuevo archivo."""
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
    """Exporto los resultados del escaneo (simulado)."""
    messagebox.showinfo("Exportar Resultados", "Exportando resultados a CSV/PDF (simulado)...")

# --- Funciones para las funcionalidades avanzadas ---
def use_tool(tool_name):
    """Simulo el uso de una herramienta."""
    messagebox.showinfo("Herramienta", f"Usando la herramienta: {tool_name} (simulado)...")

def send_report_by_email():
    """Simulo el envío de un informe por correo electrónico."""
    messagebox.showinfo("Enviar Informe", "Enviando informe por correo electrónico (simulado)...")

def ask_target_and_perform_scan(scan_type):
    """Pido la IP objetivo y luego realizo el escaneo."""
    target_window = ctk.CTkToplevel(app)
    target_window.title("Ingresar IP Objetivo")

    label = ctk.CTkLabel(target_window, text="Dirección IP:")
    label.pack(padx=10, pady=5)

    entry_target = ctk.CTkEntry(target_window)
    entry_target.pack(padx=10, pady=5)

    def start_scan():
        target_ip = entry_target.get()
        target_window.destroy()
        perform_scan(scan_type, target_ip)

    button_start = ctk.CTkButton(target_window, text="Iniciar Escaneo", command=start_scan)
    button_start.pack(padx=10, pady=10)

def insert_to_console(text):
    """Inserto texto en la consola."""
    console.configure(state="normal")
    console.insert(tk.END, text + "\n")
    console.configure(state="disabled")
    console.see(tk.END)  # Auto-scroll to the end

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
        "🎯 Escaneo Rápido": lambda: ask_target_and_perform_scan("Escaneo Rápido"),
        "🔎 Escaneo Completo": lambda: ask_target_and_perform_scan("Escaneo Completo"),
        "Escaneo Personalizado": lambda: ask_target_and_perform_scan("Escaneo Personalizado"),
        "🌐 Escaneo Avanzado (TCP y UDP)": lambda: ask_target_and_perform_scan("Escaneo Avanzado"),
        "🏴☠️ Detección de Servicios y SO": lambda: ask_target_and_perform_scan("Detección de Servicios y SO"),
    },
    "3 Configuración": {
        "⚡ Modo Rápido / Detallado": toggle_fast_mode,
        "🎨 Personalización de la Interfaz": adjust_interface,
        "🌍 Ajustes de Red": adjust_network_settings,
        "📡 Definir Puertos por Defecto": define_default_ports,
        "Actualizar Base de Datos de Servicios": update_service_database,
    },
    "4 Herramientas": {
        "🕵️♂️ Análisis de Vulnerabilidades": lambda: use_tool("Análisis de Vulnerabilidades"),
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
        "📜 Licencia de Uso": show_license,
    }
}

# --- Add menus to the menu bar ---
menu_bar = ModernMenuBar(app)
menu_bar.pack(fill=tk.X)

# --- Create the console ---
console = scrolledtext.ScrolledText(app, wrap=tk.WORD, bg="#343638", fg="#D8DEE9", state="disabled")
console.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

for label, items in menu_items.items():
    menu_bar.add_menu(label, items)

# --- Start the application ---
app.mainloop()
