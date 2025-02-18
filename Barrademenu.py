import flet as ft
import json
import threading
from flet import (
    AlertDialog,
    ElevatedButton,
    FilePickerResultEvent,
    FilePicker,
    Row,
    Text,
    TextField,
    Column,
    MainAxisAlignment,
    CrossAxisAlignment,
    VerticalAlignment,
    ScrollMode,
    FilePickerUploadFile,
    FilePickerUploadEvent,
    ProgressBar,
    SnackBar,
    IconButton,
    icons,
    padding,
    Checkbox,
    Tabs,
    Tab
)
import os

class ModernMenuBar:
    def __init__(self, page):
        self.page = page
        self.buttons = {}
        self.dropdown_menus = {}
        self.selected_button = None
        self.current_file = None
        self.scan_history = self.load_scan_history()
        self.fast_mode = True
        self.dropdown_menu = None  # Store the current dropdown menu

    def build(self):
        self.menu_row = ft.Row(controls=[], alignment=ft.MainAxisAlignment.START)
        return self.menu_row

    def add_menu(self, label, items):
        menu_button = ft.ElevatedButton(
            text=label,
            style=ft.ButtonStyle(
                color={
                    ft.MaterialState.DEFAULT: ft.colors.WHITE,  # Text color
                    ft.MaterialState.HOVERED: ft.colors.WHITE,
                },
                bgcolor={
                    ft.MaterialState.DEFAULT: ft.colors.TRANSPARENT,  # Background color
                    ft.MaterialState.HOVERED: ft.colors.GREY_700,
                },
                padding=padding.symmetric(horizontal=10, vertical=5),
            ),
            on_click=lambda e, items=items, label=label, menu_button=menu_button: self.show_dropdown(e, items, label, menu_button)
        )
        self.buttons[label] = menu_button
        self.menu_row.controls.append(menu_button)

    def show_dropdown(self, e, items, label, menu_button):
        # Close the previous dropdown menu if it exists
        if self.dropdown_menu and self.dropdown_menu in self.page.overlay:
            self.page.overlay.remove(self.dropdown_menu)
            self.dropdown_menu = None
            self.page.update()

        # Reset background color of previously selected button
        if self.selected_button:
            self.selected_button.style.bgcolor = ft.colors.TRANSPARENT
            self.selected_button.update()

        # Highlight the selected button
        menu_button.style.bgcolor = ft.colors.BLUE_ACCENT_700
        self.selected_button = menu_button
        menu_button.update()

        # Calculate the position of the dropdown menu
        button_index = self.menu_row.controls.index(menu_button)
        x = button_index * 100  # Adjust as needed
        y = 50  # Adjust as needed

        # Build the dropdown menu
        self.dropdown_menu = self.build_dropdown(items, x, y)

        # Add the dropdown menu to the overlay and update the page
        self.page.overlay.append(self.dropdown_menu)
        self.page.update()

    def build_dropdown(self, items, x, y):
        menu_items = []
        for item_label, command in items.items():
            item_button = ft.ElevatedButton(
                content=ft.Text(item_label, color=ft.colors.WHITE),
                style=ft.ButtonStyle(
                    color={
                        ft.MaterialState.DEFAULT: ft.colors.WHITE,
                        ft.MaterialState.HOVERED: ft.colors.WHITE,
                    },
                    bgcolor={
                        ft.MaterialState.DEFAULT: ft.colors.TRANSPARENT,
                        ft.MaterialState.HOVERED: ft.colors.GREY_700,
                    },
                    padding=padding.symmetric(horizontal=10, vertical=5),
                ),
                width=200,
                on_click=lambda e, command=command: self.menu_item_action(e, command)
            )
            menu_items.append(item_button)

        dropdown = ft.Container(
            content=ft.Column(controls=menu_items, tight=True, horizontal_alignment=ft.CrossAxisAlignment.START),
            top=y,
            left=x,
            width=200,
            bgcolor=ft.colors.GREY_800,
            border=ft.border.all(1, ft.colors.GREY_600),
            border_radius=5,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.BLACK54,
                offset=ft.Offset(2, 2),
            ),
            visible=True,
            alignment=ft.alignment.top_left,
            clip_behavior=ft.ClipBehavior.HARD_EDGE
        )
        return dropdown

    def menu_item_action(self, e, command):
         # Reset background of previously selected button
        if self.selected_button:
            self.selected_button.style.bgcolor = ft.colors.TRANSPARENT
            self.selected_button.update()

        # Close the dropdown menu
        if self.dropdown_menu and self.dropdown_menu in self.page.overlay:
            self.page.overlay.remove(self.dropdown_menu)
            self.dropdown_menu = None
            self.page.update()

        # Execute the command
        command()

    def load_scan_history(self):
        """Loads scan history from a JSON file."""
        try:
            with open("scan_history.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_scan_history(self):
        """Saves scan history to a JSON file."""
        with open("scan_history.json", "w") as f:
            json.dump(self.scan_history, f, indent=4)

    def add_scan_to_history(self, scan_type, target, results):
        """Adds a scan to the history."""
        scan_entry = {
            "type": scan_type,
            "target": target,
            "results": results
        }
        self.scan_history.append(scan_entry)
        self.save_scan_history()

# --- Auxiliary Windows and Functions ---
class TermsAndConditionsDialog(ft.AlertDialog):
    def __init__(self):
        super().__init__(
            modal=True,
            title=Text("Terms and Conditions"),
            content=Column([
                Text("Here go the terms and conditions...")
            ], tight=True, scroll=ScrollMode.ADAPTIVE),
            actions=[
                ElevatedButton("OK", on_click=self.close_dlg)
            ],
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )

    def close_dlg(self, e):
        self.open = False
        self.update()

class LicenseDialog(ft.AlertDialog):
    def __init__(self, license_type):
        super().__init__(
            modal=True,
            title=Text(f"License Agreement: {license_type}"),
            content=Column([
                Text(f"Here goes the license agreement for {license_type}...")
            ], tight=True, scroll=ScrollMode.ADAPTIVE),
            actions=[
                ElevatedButton("OK", on_click=self.close_dlg)
            ],
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )

    def close_dlg(self, e):
        self.open = False
        self.update()

class ScanResultsDialog(ft.AlertDialog):
    def __init__(self, scan_type, target, results):
        super().__init__(
            modal=True,
            title=Text(f"Results of {scan_type}"),
            content=Column([
                Text(results)
            ], tight=True, scroll=ScrollMode.ADAPTIVE),
            actions=[
                ElevatedButton("OK", on_click=self.close_dlg)
            ],
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )

    def close_dlg(self, e):
        self.open = False
        self.update()

class ScanHistoryDialog(ft.AlertDialog):
    def __init__(self, scan_history):
        super().__init__(
            modal=True,
            title=Text("Scan History"),
            content=Column([
                Text(self.format_history(scan_history))
            ], tight=True, scroll=ScrollMode.ADAPTIVE),
            actions=[
                ElevatedButton("OK", on_click=self.close_dlg)
            ],
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )
    def format_history(self, scan_history):
        if scan_history:
            history_text = ""
            for entry in scan_history:
                history_text += f"Type: {entry['type']}\n"
                history_text += f"Target: {entry['target']}\n"
                history_text += f"Results: {entry['results']}\n\n"
            return history_text
        else:
            return "No scans in history."

    def close_dlg(self, e):
        self.open = False
        self.update()

class SettingsDialog(ft.AlertDialog):
    def __init__(self):
        super().__init__(
            modal=True,
            title=Text("Settings"),
            content=Column([
                Text("Here go the settings options...")
            ], tight=True, scroll=ScrollMode.ADAPTIVE),
            actions=[
                ElevatedButton("OK", on_click=self.close_dlg)
            ],
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )

    def close_dlg(self, e):
        self.open = False
        self.update()

class HelpDialog(ft.AlertDialog):
    def __init__(self, help_topic):
        super().__init__(
            modal=True,
            title=Text(f"Help: {help_topic}"),
            content=Column([
                Text(f"Here goes the help about {help_topic}...")
            ], tight=True, scroll=ScrollMode.ADAPTIVE),
            actions=[
                ElevatedButton("OK", on_click=self.close_dlg)
            ],
            on_dismiss=lambda e: print("Modal dialog dismissed!")
        )

    def close_dlg(self, e):
        self.open = False
        self.update()

# --- Scanning Functions ---
def perform_scan(page, menu_bar, scan_type):
    """Performs a scan (simulated) and saves the results."""
    def run_scan():
        # Simulation of the scan
        target = "example.com"  # Change this to allow the user to enter the target
        results = f"Scan results {scan_type} in {target}: [SIMULATED]"

        # Add to scan history
        menu_bar.add_scan_to_history(scan_type, target, results)

        # Show results in a dialog
        dlg = ScanResultsDialog(scan_type, target, results)
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Run the scan in a thread to avoid blocking the GUI
    threading.Thread(target=run_scan).start()

# --- File Handling Functions ---
def new_scan(page, menu_bar):
    """Starts a new scan."""
    perform_scan(page, menu_bar, "New Scan")

def open_report(page, menu_bar):
    """Opens a report from a file."""
    def get_file_result(e: FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            try:
                with open(file_path, "r") as file:
                    report_content = file.read()
                    dlg = ScanResultsDialog("Open Report", file_path, report_content)
                    page.dialog = dlg
                    dlg.open = True
                    page.current_file = file_path
                    page.update()
            except Exception as ex:
                page.snack_bar = SnackBar(Text(f"Error opening the file: {ex}"))
                page.snack_bar.open = True
                page.update()
        else:
            print("User cancelled")

    file_picker = FilePicker(on_result=get_file_result)
    page.overlay.append(file_picker)
    page.update()
    file_picker.pick_files(allowed_extensions=["report"])

def save_report(page, menu_bar):
    """Saves the current report."""
    if page.current_file:
        try:
            # Simulation: get content from "report" from history
            last_scan = menu_bar.scan_history[-1] if menu_bar.scan_history else None
            report_content = f"Last Scan:\n{last_scan}" if last_scan else "No data to save."

            with open(page.current_file, "w") as file:
                file.write(report_content)
            page.snack_bar = SnackBar(Text(f"Report saved to {page.current_file}"))
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            page.snack_bar = SnackBar(Text(f"Error saving the file: {e}"))
            page.snack_bar.open = True
            page.update()
    else:
        save_report_as(page, menu_bar)

def save_report_as(page, menu_bar):
    """Saves the current report as a new file."""
    def get_file_result(e: FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            try:
                # Simulation: get content from "report" from history
                last_scan = menu_bar.scan_history[-1] if menu_bar.scan_history else None
                report_content = f"Last Scan:\n{last_scan}" if last_scan else "No data to save."

                with open(file_path, "w") as file:
                    file.write(report_content)
                page.snack_bar = SnackBar(Text(f"Report saved to {file_path}"))
                page.snack_bar.open = True
                page.current_file = file_path
                page.update()
            except Exception as ex:
                page.snack_bar = SnackBar(Text(f"Error saving the file: {ex}"))
                page.snack_bar.open = True
                page.update()
        else:
            print("User cancelled")

    file_picker = FilePicker(on_result=get_file_result)
    page.overlay.append(file_picker)
    page.update()
    file_picker.save_file(file_name="report.report", allowed_extensions=["report"])

def export_results(page):
    """Exports scan results (simulated)."""
    page.snack_bar = SnackBar(Text("Exporting results to CSV/PDF (simulated)..."))
    page.snack_bar.open = True
    page.update()

# --- Other Functions ---
def use_tool(page, tool_name):
    """Simulates the use of a tool."""
    page.snack_bar = SnackBar(Text(f"Using tool: {tool_name} (simulated)..."))
    page.snack_bar.open = True
    page.update()

def send_report_by_email(page):
    """Simulates sending a report by email."""
    page.snack_bar = SnackBar(Text("Sending report by email (simulated)..."))
    page.snack_bar.open = True
    page.update()

def toggle_fast_mode(page, menu_bar):
    """Toggles fast mode."""
    menu_bar.fast_mode = not menu_bar.fast_mode
    page.snack_bar = SnackBar(Text(f"Fast Mode: {'Activated' if menu_bar.fast_mode else 'Deactivated'}"))
    page.snack_bar.open = True
    page.update()

def adjust_settings(page):
    """Shows a settings window (simulated)."""
    dlg = SettingsDialog()
    page.dialog = dlg
    dlg.open = True
    page.update()

def show_terms_and_conditions(page):
    """Shows the terms and conditions."""
    dlg = TermsAndConditionsDialog()
    page.dialog = dlg
    dlg.open = True
    page.update()

def show_license(page, license_type):
    """Shows a license."""
    dlg = LicenseDialog(license_type)
    page.dialog = dlg
    dlg.open = True
    page.update()

def view_scan_history(page, menu_bar):
    """Shows the scan history in a dialog."""
    dlg = ScanHistoryDialog(menu_bar.scan_history)
    page.dialog = dlg
    dlg.open = True
    page.update()

def show_help(page, help_topic):
    """Shows help content."""
    dlg = HelpDialog(help_topic)
    page.dialog = dlg
    dlg.open = True
    page.update()

# --- Main function ---
def main(page: ft.Page):
    page.title = "Main Menu"
    page.window_width = 800
    page.window_height = 600
    page.theme_mode = ft.ThemeMode.DARK
    page.current_file = None

    menu_bar = ModernMenuBar(page)
    page.overlay = []  # Initialize page.overlay as an empty list

    # --- Define menu items and commands ---
    menu_items = {
        "1 Archivo": {
            "🆕 Nuevo Escaneo": lambda: new_scan(page, menu_bar),
            "📂 Abrir Informe": lambda: open_report(page, menu_bar),
            "💾 Guardar Informe": lambda: save_report(page, menu_bar),
            "Guardar Informe Como...": lambda: save_report_as(page, menu_bar),
            "📜 Exportar Resultados (CSV, PDF)": lambda: export_results(page),
            "🚪 Salir": lambda: page.window_close(),
        },
        "2 Escaneo": {
            "🎯 Escaneo Rápido": lambda: perform_scan(page, menu_bar, "Escaneo Rápido"),
            "🔎 Escaneo Completo": lambda: perform_scan(page, menu_bar, "Escaneo Completo"),
            "Escaneo Personalizado": lambda: perform_scan(page, menu_bar, "Escaneo Personalizado"),
            "🌐 Escaneo Avanzado (TCP y UDP)": lambda: perform_scan(page, menu_bar, "Escaneo Avanzado"),
            "🏴‍☠️ Detección de Servicios y SO": lambda: perform_scan(page, menu_bar, "Detección de Servicios y SO"),
        },
        "3 Configuración": {
            "⚡ Modo Rápido / Detallado": lambda: toggle_fast_mode(page, menu_bar),
            "🎨 Personalización de la Interfaz": lambda: adjust_settings(page),
            "🌍 Ajustes de Red": lambda: adjust_settings(page),
            "📡 Definir Puertos por Defecto": lambda: adjust_settings(page),
            "Actualizar Base de Datos de Servicios": lambda: adjust_settings(page),
        },
        "4 Herramientas": {
            "🕵️‍♂️ Análisis de Vulnerabilidades": lambda: use_tool(page, "Análisis de Vulnerabilidades"),
            "🛑 Detección de Firewall": lambda: use_tool(page, "Detección de Firewall"),
            "🔐 Verificación SSL/TLS": lambda: use_tool(page, "Verificación SSL/TLS"),
            "🌐 Búsqueda WHOIS de Dominio/IP": lambda: use_tool(page, "Búsqueda WHOIS de Dominio/IP"),
        },
        "5 Informes": {
            "📊 Ver Historial de Escaneos": lambda: view_scan_history(page, menu_bar),
            "📋 Generar Informe Detallado": lambda: view_scan_history(page, menu_bar),
            "📥 Exportar a CSV / PDF": lambda: view_scan_history(page, menu_bar),
            "📤 Enviar Informe por Correo": lambda: send_report_by_email(page),
        },
        "6 Ayuda": {
            "Guía de Uso": lambda: show_help(page, "Guía de Uso"),
            "🎓 Atajos de Teclado": lambda: show_help(page, "Atajos de Teclado"),
            "❓ Soporte Técnico": lambda: show_help(page, "Soporte Técnico"),
            "🔍 Acerca de Este Software": lambda: show_help(page, "Acerca de Este Software"),
        },
        "7 Licencia": {
            "📜 Términos y Condiciones": lambda: show_terms_and_conditions(page),
            "🏛 Licencia de Uso": lambda: show_license(page, "Licencia de Uso"),
            "⚖ Aviso Legal": lambda: show_license(page, "Aviso Legal"),
            "🛡 Política de Privacidad": lambda: show_license(page, "Política de Privacidad"),
        }
    }

    # --- Add menus to the menu bar ---
    menu_bar.build()
    for label, items in menu_items.items():
        menu_bar.add_menu(label, items)

    page.add(menu_bar.build())

ft.app(target=main)
