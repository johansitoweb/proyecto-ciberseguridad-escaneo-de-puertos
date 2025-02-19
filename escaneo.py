import logging
import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext, Menu
import customtkinter as ctk
from scapy.all import IP, IPv6, TCP, sr1, RandShort, UDP
import subprocess
import os
import nmap

# Importaciones de las funcionalidades avanzadas
import anomaly_detection
import cloud_scanning
import conetbase
import shodan_integration
import stealth_mode
import Report

# Configuración del registro
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

# --- Funciones para las funcionalidades avanzadas ---
def open_anomaly_detection():
    anomaly_detection.detect_anomalies('../data/network_traffic.csv')

def open_cloud_scanning():
    target_ip = entry_target.get()
    if target_ip:
        cloud_scanning.scan_ip(target_ip)
    else:
        messagebox.showerror("Error", "Por favor ingresa una IP objetivo.")

def open_shodan_integration():
    target_ip = entry_target.get()
    if target_ip:
        shodan_integration.get_shodan_info('YOUR_SHODAN_API_KEY', target_ip, save_to_file=True)
    else:
        messagebox.showerror("Error", "Por favor ingresa una IP objetivo.")

def open_stealth_mode():
    target_ip = entry_target.get()
    if target_ip:
        stealth_mode.stealth_scan(target_ip, start_port=1, end_port=1024, delay=0.1)
    else:
        messagebox.showerror("Error", "Por favor ingresa una IP objetivo.")

# --- Nuevas funciones para generar reportes ---
def generar_reporte_pdf():
    Report.generar_reporte_pdf()
    messagebox.showinfo("Éxito", "Reporte PDF generado correctamente.")

def exportar_csv():
    Report.exportar_csv()
    messagebox.showinfo("Éxito", "Reporte CSV generado correctamente.")

# --- Funciones de escaneo ---
def scan_tcp(target_ip, target_port, scan_type):
    src_port = RandShort()
    ip_layer = IP(dst=target_ip)
    flags = {
        "SYN": "S",
        "ACK": "A",
        "FIN": "F",
        "NULL": "",
        "XMAS": "FPU",
        "CONNECT": "S",
    }

    if scan_type == "CONNECT":
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target_ip, target_port))
            sock.close()
            return "Abierto" if result == 0 else "Cerrado"
        except Exception as e:
            return f"Error: {e}"

    response = sr1(
        ip_layer / TCP(sport=src_port, dport=target_port, flags=flags[scan_type]),
        timeout=2,
        verbose=False,
    )

    if response is None:
        return "Filtrado o no responde"
    elif response.haslayer(TCP):
        if response.getlayer(TCP).flags == 0x12:  # SYN-ACK
            return "Abierto" if scan_type != "FIN" else "Cerrado"
        elif response.getlayer(TCP).flags == 0x14:  # RST
            return "Cerrado"
    return "Indeterminado"

def scan_udp(host, ports):
    results = {}
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            sock.sendto(b"Hello", (host, port))
            sock.recvfrom(1024)
            results[port] = f"Puerto UDP {port} abierto"
        except socket.timeout:
            results[port] = f"Puerto UDP {port} filtrado"
        except OSError as e:
            if e.errno == 111:  # Connection refused
                results[port] = f"Puerto UDP {port} cerrado"
            else:
                results[port] = f"Error en el puerto UDP {port}: {e}"
        finally:
            sock.close()
    return results

def syn_scan(target_ip, target_port, is_ipv6=False):
    src_port = RandShort()
    ip_layer = IPv6(dst=target_ip) if is_ipv6 else IP(dst=target_ip)
    response = sr1(
        ip_layer / TCP(sport=src_port, dport=target_port, flags="S"),
        timeout=2,
        verbose=False,
    )

    if response is None:
        return "Filtrado"
    elif response.haslayer(TCP):
        if response.getlayer(TCP).flags == 0x12:  # SYN-ACK
            send_rst = sr1(
                ip_layer / TCP(sport=src_port, dport=target_port, flags="R"),
                timeout=2,
                verbose=False,
            )
            return "Abierto"
        elif response.getlayer(TCP).flags == 0x14:  # RST
            return "Cerrado"

def identify_service(port):
    services = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        67: "DHCP",
        80: "HTTP",
        110: "POP3",
        123: "NTP",
        143: "IMAP",
        161: "SNMP",
        443: "HTTPS",
        3306: "MySQL",
        3389: "RDP (Remote Desktop Protocol)",
        5432: "PostgreSQL",
        6379: "Redis",
    }
    return services.get(port, "Desconocido")

def validate_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET6 if ":" in ip else socket.AF_INET, ip)
        return True
    except socket.error:
        return False

def run_scan():
    target = entry_target.get()
    if not validate_ip(target):
        messagebox.showerror("Error", "Dirección IP no válida.")
        return

    scan_type = var_scan_type.get()
    protocol = var_protocol.get()

    if scan_type == "rápido":
        ports = [22, 53, 80, 443]
    elif scan_type == "completo":
        ports = range(1, 101)
    elif scan_type == "personalizado":
        ports_input = entry_ports.get()
        try:
            ports = [int(port.strip()) for port in ports_input.split(",")]
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa una lista válida de números de puerto separados por comas.")
            return

    results_text.delete("0.0", tk.END)
    is_ipv6 = ":" in target

    for port in ports:
        results_text.insert(tk.END, f"Escaneando puerto {port}...\n")
        if protocol == "TCP":
            syn_result = syn_scan(target, port, is_ipv6)
            service_name = identify_service(port)
            results_text.insert(tk.END, f"Puerto {port} - TCP: {syn_result}, Servicio: {service_name}\n")
        elif protocol == "UDP":
            udp_results = scan_udp(target, [port])
            service_name = identify_service(port)
            results_text.insert(tk.END, f"Puerto {port} - UDP: {udp_results[port]}, Servicio: {service_name}\n")

def close_session():
    root.destroy()
    login_script_path = "loginappescritorio.py"
    if not os.path.exists(login_script_path):
        messagebox.showerror("Error", f"El archivo loginappescritorio.py no se encuentra en la ruta especificada: {login_script_path}")
        return
    try:
        subprocess.Popen(["python", login_script_path])
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar loginappescritorio.py: {e}")

# Crear la ventana principal
root = ctk.CTk()
root.title("Escáner de Puertos")
root.geometry("850x800")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Menú de Funcionalidades Avanzadas ---
menu_bar = Menu(root)
root.config(menu=menu_bar)
advanced_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Funcionalidades Avanzadas", menu=advanced_menu)
advanced_menu.add_command(label="Detección de Anomalías", command=open_anomaly_detection)
advanced_menu.add_command(label="Escaneo en la Nube", command=open_cloud_scanning)
advanced_menu.add_command(label="Integración con Shodan", command=open_shodan_integration)
advanced_menu.add_command(label="Modo Sigiloso", command=open_stealth_mode)
advanced_menu.add_separator()  # Separador visual
advanced_menu.add_command(label="Generar Reporte PDF", command=generar_reporte_pdf)
advanced_menu.add_command(label="Exportar Reporte CSV", command=exportar_csv)

# --- Resto de la interfaz gráfica ---
main_frame = ctk.CTkFrame(root)
main_frame.pack(pady=20, padx=20, fill="x")

input_frame = ctk.CTkFrame(main_frame)
input_frame.pack(pady=(0, 15), padx=10, fill="x")

label_target = ctk.CTkLabel(input_frame, text="IP del objetivo (IPv4 o IPv6):")
label_target.pack(side="left", padx=(0, 5))
entry_target = ctk.CTkEntry(input_frame, width=200)
entry_target.pack(side="left", fill="x", expand=True)

scan_type_frame = ctk.CTkFrame(main_frame)
scan_type_frame.pack(pady=15, padx=10, fill="x")

label_scan_type = ctk.CTkLabel(scan_type_frame, text="Tipo de escaneo:")
label_scan_type.pack(side="left", padx=(0, 5))
var_scan_type = tk.StringVar(value="rápido")

radio_rapido = ctk.CTkRadioButton(scan_type_frame, text="Rápido", variable=var_scan_type, value="rápido")
radio_rapido.pack(side="left", padx=5)

radio_completo = ctk.CTkRadioButton(scan_type_frame, text="Completo (primeros 100 puertos)", variable=var_scan_type, value="completo")
radio_completo.pack(side="left", padx=5)

radio_personalizado = ctk.CTkRadioButton(scan_type_frame, text="Personalizado", variable=var_scan_type, value="personalizado")
radio_personalizado.pack(side="left", padx=5)

custom_ports_frame = ctk.CTkFrame(main_frame)
custom_ports_frame.pack(pady=15, padx=10, fill="x")

label_ports = ctk.CTkLabel(custom_ports_frame, text="Puertos personalizados (separados por comas):")
label_ports.pack(side="left", padx=(0, 5))
entry_ports = ctk.CTkEntry(custom_ports_frame, width=200)
entry_ports.pack(side="left", fill="x", expand=True)

tcp_method_frame = ctk.CTkFrame(main_frame)
tcp_method_frame.pack(pady=15, padx=10, fill="x")

label_tcp_method = ctk.CTkLabel(tcp_method_frame, text="Método de escaneo TCP:")
label_tcp_method.pack(side="left", padx=(0, 5))
var_tcp_method = tk.StringVar(value="SYN")

tcp_methods = ["SYN", "ACK", "FIN", "NULL", "XMAS", "CONNECT"]
for method in tcp_methods:
    radio_tcp = ctk.CTkRadioButton(tcp_method_frame, text=method, variable=var_tcp_method, value=method)
    radio_tcp.pack(side="left", padx=5)

protocol_frame = ctk.CTkFrame(main_frame)
protocol_frame.pack(pady=15, padx=10, fill="x")

label_protocol = ctk.CTkLabel(protocol_frame, text="Selecciona el protocolo:")
label_protocol.pack(side="left", padx=(0, 5))
var_protocol = tk.StringVar(value="TCP")

radio_tcp = ctk.CTkRadioButton(protocol_frame, text="TCP", variable=var_protocol, value="TCP")
radio_tcp.pack(side="left", padx=5)
radio_udp = ctk.CTkRadioButton(protocol_frame, text="UDP", variable=var_protocol, value="UDP")
radio_udp.pack(side="left", padx=5)

scan_button = ctk.CTkButton(root, text="Iniciar Escaneo", command=run_scan)
scan_button.pack(pady=10)

results_text = scrolledtext.ScrolledText(root, width=100, height=20, bg="#282a36", fg="white", insertbackground="white", font=("Consolas", 11), relief=tk.FLAT)
results_text.pack(pady=10, padx=20, fill="both", expand=True)

close_button = ctk.CTkButton(root, text="Cerrar Sesión", command=close_session)
close_button.pack(pady=20)

# Iniciar la interfaz gráfica
root.mainloop()