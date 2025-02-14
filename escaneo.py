import logging
import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext
import customtkinter as ctk
from scapy.all import IP, IPv6, TCP, sr1, RandShort, UDP
import subprocess  # Import the subprocess module
import os


# Configuration of the registry
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


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


# Función para escanear puertos UDP
def scan_udp(host, ports):
    """
    Escanea puertos UDP en un host específico.
    :param host: Dirección IP o dominio del objetivo.
    :param ports: Lista de puertos a escanear.
    :return: Diccionario con los resultados del escaneo.
    """
    results = {}

    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)  # Establecer un tiempo de espera de 1 segundo
            sock.sendto(b"Hello", (host, port))  # Enviar un mensaje al puerto
            sock.recvfrom(1024)  # Esperar una respuesta
            results[port] = f"Puerto UDP {port} abierto"
        except socket.timeout:
            results[port] = f"Puerto UDP {port} filtrado"
        except OSError as e:
            if e.errno == 111:  # Connection refused
                results[port] = f"Puerto UDP {port} cerrado"
            else:
                results[port] = f"Error en el puerto UDP {port}: {e}"
        finally:
            sock.close()  # Asegurarse de cerrar el socket

    return results


# Función para escanear puertos TCP (SYN Scan)
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


# Función para identificar servicios comunes según el puerto
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


# Validar dirección IP (IPv4 o IPv6)
def validate_ip(ip):
    try:
        socket.inet_pton(socket.AF_INET6 if ":" in ip else socket.AF_INET, ip)
        return True
    except socket.error:
        return False


# Función para ejecutar el escaneo y mostrar resultados en el cuadro de texto
def run_scan():
    target = entry_target.get()

    if not validate_ip(target):
        messagebox.showerror("Error", "Dirección IP no válida.")
        return

    scan_type = var_scan_type.get()
    protocol = var_protocol.get()  # Obtener el protocolo seleccionado

    if scan_type == "rápido":
        ports = [22, 53, 80, 443]
    elif scan_type == "completo":
        ports = range(1, 101)  # Escanear los primeros 100 puertos como ejemplo
    elif scan_type == "personalizado":
        ports_input = entry_ports.get()
        try:
            ports = [int(port.strip()) for port in ports_input.split(",")]
        except ValueError:
            messagebox.showerror(
                "Error",
                "Por favor ingresa una lista válida de números de puerto separados por comas.",
            )
            return

    results_text.delete("0.0", tk.END)

    is_ipv6 = ":" in target

    for port in ports:
        results_text.insert(tk.END, f"Escaneando puerto {port}...\n")

        if protocol == "TCP":
            syn_result = syn_scan(target, port, is_ipv6)
            service_name = identify_service(port)
            results_text.insert(
                tk.END,
                f"Puerto {port} - TCP: {syn_result}, Servicio: {service_name}\n",
            )

        elif protocol == "UDP":
            udp_results = scan_udp(target, [port])
            service_name = identify_service(port)
            results_text.insert(
                tk.END,
                f"Puerto {port} - UDP: {udp_results[port]}, Servicio: {service_name}\n",
            )


# --- NEW: Function to close session and re-open login ---
def close_session():
    """
    Closes the current window and re-opens the login application.
    You might need to adjust the path to loginappescritorio.py
    """
    root.destroy()  # Close the current window

    # --- Adjust the path as necessary
    login_script_path = "loginappescritorio.py"  # Relative path, assuming it's in the same directory

    # --- Check if the script exists
    if not os.path.exists(login_script_path):
        messagebox.showerror(
            "Error",
            f"El archivo loginappescritorio.py no se encuentra en la ruta especificada: {login_script_path}",
        )
        return

    try:
        # --- Execute the login script using subprocess
        subprocess.Popen(["python", login_script_path])  # Adapt if you need a different interpreter
    except Exception as e:
        messagebox.showerror(
            "Error", f"Error al iniciar loginappescritorio.py: {e}"
        )


# Crear la ventana principal
root = ctk.CTk()
root.title("Escáner de Puertos")
root.geometry("850x800")  # Adjusted size for better spacing
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Main frame to hold all the input widgets
main_frame = ctk.CTkFrame(root)
main_frame.pack(pady=20, padx=20, fill="x")

# --- Input Section ---
input_frame = ctk.CTkFrame(main_frame)
input_frame.pack(pady=(0, 15), padx=10, fill="x")  # Reduced padding at the top

# Target IP Address
label_target = ctk.CTkLabel(input_frame, text="IP del objetivo (IPv4 o IPv6):")
label_target.pack(side="left", padx=(0, 5))  # Add some right padding
entry_target = ctk.CTkEntry(input_frame, width=200)
entry_target.pack(side="left", fill="x", expand=True)

# --- Scan Type Selection ---
scan_type_frame = ctk.CTkFrame(main_frame)
scan_type_frame.pack(pady=15, padx=10, fill="x")

label_scan_type = ctk.CTkLabel(scan_type_frame, text="Tipo de escaneo:")
label_scan_type.pack(side="left", padx=(0, 5))  # Add some right padding
var_scan_type = tk.StringVar(value="rápido")

radio_rapido = ctk.CTkRadioButton(
    scan_type_frame, text="Rápido", variable=var_scan_type, value="rápido"
)
radio_rapido.pack(side="left", padx=5)

radio_completo = ctk.CTkRadioButton(
    scan_type_frame,
    text="Completo (primeros 100 puertos)",
    variable=var_scan_type,
    value="completo",
)
radio_completo.pack(side="left", padx=5)

radio_personalizado = ctk.CTkRadioButton(
    scan_type_frame, text="Personalizado", variable=var_scan_type, value="personalizado"
)
radio_personalizado.pack(side="left", padx=5)


# --- Custom Ports Input ---
custom_ports_frame = ctk.CTkFrame(main_frame)
custom_ports_frame.pack(pady=15, padx=10, fill="x")

label_ports = ctk.CTkLabel(
    custom_ports_frame, text="Puertos personalizados (separados por comas):"
)
label_ports.pack(side="left", padx=(0, 5))  # Add some right padding
entry_ports = ctk.CTkEntry(custom_ports_frame, width=200)
entry_ports.pack(side="left", fill="x", expand=True)

# --- TCP Method Selection ---
tcp_method_frame = ctk.CTkFrame(main_frame)
tcp_method_frame.pack(pady=15, padx=10, fill="x")

label_tcp_method = ctk.CTkLabel(tcp_method_frame, text="Método de escaneo TCP:")
label_tcp_method.pack(side="left", padx=(0, 5))  # Add some right padding
var_tcp_method = tk.StringVar(value="SYN")

tcp_methods = ["SYN", "ACK", "FIN", "NULL", "XMAS", "CONNECT"]
for method in tcp_methods:
    radio_tcp = ctk.CTkRadioButton(
        tcp_method_frame, text=method, variable=var_tcp_method, value=method
    )
    radio_tcp.pack(side="left", padx=5)

# --- Protocol Selection ---
protocol_frame = ctk.CTkFrame(main_frame)
protocol_frame.pack(pady=15, padx=10, fill="x")

label_protocol = ctk.CTkLabel(protocol_frame, text="Selecciona el protocolo:")
label_protocol.pack(side="left", padx=(0, 5))  # Add some right padding
var_protocol = tk.StringVar(value="TCP")

radio_tcp = ctk.CTkRadioButton(
    protocol_frame, text="TCP", variable=var_protocol, value="TCP"
)
radio_tcp.pack(side="left", padx=5)
radio_udp = ctk.CTkRadioButton(
    protocol_frame, text="UDP", variable=var_protocol, value="UDP"
)
radio_udp.pack(side="left", padx=5)


# --- Start Scan Button ---
scan_button = ctk.CTkButton(root, text="Iniciar Escaneo", command=run_scan)
scan_button.pack(pady=10)


# --- Results Text Box ---
results_text = scrolledtext.ScrolledText(
    root,
    width=100,  # Wider for better readability
    height=20,
    bg="#282a36",  # Dark background for dark mode
    fg="white",
    insertbackground="white",
    font=("Consolas", 11),
    relief=tk.FLAT,
)
results_text.pack(pady=10, padx=20, fill="both", expand=True)


# --- NEW: Close Session Button ---
close_button = ctk.CTkButton(root, text="Cerrar Sesión", command=close_session)
close_button.pack(pady=20)


# Start the graphical interface
root.mainloop()
