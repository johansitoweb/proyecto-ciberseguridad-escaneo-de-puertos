import logging
from scapy.all import IP, IPv6, TCP, sr1, RandShort, UDP
import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


# Configuración del registro 
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
        "CONNECT": "S"
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
    
    response = sr1(ip_layer / TCP(sport=src_port, dport=target_port, flags=flags[scan_type]), timeout=2, verbose=False)
    
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
            sock.sendto(b'Hello', (host, port))  # Enviar un mensaje al puerto
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
    response = sr1(ip_layer/TCP(sport=src_port, dport=target_port, flags="S"), timeout=2, verbose=False)
    
    if response is None:
        return "Filtrado"
    elif response.haslayer(TCP):
        if response.getlayer(TCP).flags == 0x12:  # SYN-ACK
            send_rst = sr1(ip_layer/TCP(sport=src_port, dport=target_port, flags="R"), timeout=2, verbose=False)
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

    if scan_type == 'rápido':
        ports = [22, 53, 80, 443]
    elif scan_type == 'completo':
        ports = range(1, 101)  # Escanear los primeros 100 puertos como ejemplo
    elif scan_type == 'personalizado':
        ports_input = entry_ports.get()
        try:
            ports = [int(port.strip()) for port in ports_input.split(",")]
        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa una lista válida de números de puerto separados por comas.")
            return

    results_text.delete(1.0, tk.END)  
    
    is_ipv6 = ":" in target
    
    for port in ports:
        results_text.insert(tk.END, f"Escaneando puerto {port}...\n")

        if protocol == 'TCP':
            syn_result = syn_scan(target, port, is_ipv6)
            service_name = identify_service(port)
            results_text.insert(tk.END,
                                f"Puerto {port} - TCP: {syn_result}, Servicio: {service_name}\n")
            
        elif protocol == 'UDP':
            udp_results = scan_udp(target, [port])
            service_name = identify_service(port)
            results_text.insert(tk.END,
                                f"Puerto {port} - UDP: {udp_results[port]}, Servicio: {service_name}\n")
            


# Crear la ventana principal
root = tk.Tk()
root.title("Escáner de Puertos")
root.geometry("800x600")
root.configure(bg="#1e1e2e")



# Estilo personalizado para botones y widgets
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", 
                background="#007bff", 
                foreground="white", 
                font=("Arial", 12), 
                borderwidth=0,
                focuscolor="none")
style.map("TButton", 
          background=[("active", "#0056b3")])




# Entrada para la dirección IP del objetivo
tk.Label(root, text="Ingresa la IP del objetivo (IPv4 o IPv6):", bg="#1e1e2e", fg="white", font=("Arial", 12)).pack(pady=10)
entry_target = ttk.Entry(root, font=("Arial", 12))
entry_target.pack(pady=5)



# Selección del tipo de escaneo
var_scan_type = tk.StringVar(value='rápido')
tk.Label(root, text="Selecciona el tipo de escaneo:", bg="#1e1e2e", fg="white", font=("Arial", 12)).pack(pady=10)

frame_radio_buttons = tk.Frame(root, bg="#1e1e2e")
frame_radio_buttons.pack()

ttk.Radiobutton(frame_radio_buttons, text="Rápido", variable=var_scan_type, value='rápido').pack(side=tk.LEFT, padx=10)
ttk.Radiobutton(frame_radio_buttons, text="Completo (primeros 100 puertos)", variable=var_scan_type, value='completo').pack(side=tk.LEFT)
ttk.Radiobutton(frame_radio_buttons, text="Personalizado", variable=var_scan_type, value='personalizado').pack(side=tk.LEFT) 



# Entrada para puertos personalizados
tk.Label(root, text="Puertos personalizados (separados por comas):", bg="#1e1e2e", fg="white", font=("Arial", 12)).pack(pady=5)
entry_ports = ttk.Entry(root, font=("Arial", 12))
entry_ports.pack(pady=5)



# Selección del método de escaneo TCP
var_tcp_method = tk.StringVar(value='SYN')
tk.Label(root, text="Método de escaneo TCP:", bg="#1e1e2e", fg="white", font=("Arial", 12)).pack(pady=10)
frame_tcp_buttons = tk.Frame(root, bg="#1e1e2e")
frame_tcp_buttons.pack()

tcp_methods = ["SYN", "ACK", "FIN", "NULL", "XMAS", "CONNECT"]
for method in tcp_methods:
    ttk.Radiobutton(frame_tcp_buttons, text=method, variable=var_tcp_method, value=method).pack(side=tk.LEFT, padx=5)




# Selección del protocolo (TCP o UDP)
var_protocol = tk.StringVar(value='TCP')
tk.Label(root, text="Selecciona el protocolo:", bg="#1e1e2e", fg="white", font=("Arial", 12)).pack(pady=10)

frame_protocol_buttons = tk.Frame(root, bg="#1e1e2e")
frame_protocol_buttons.pack()

ttk.Radiobutton(frame_protocol_buttons, text="TCP", variable=var_protocol, value='TCP').pack(side=tk.LEFT, padx=10)
ttk.Radiobutton(frame_protocol_buttons, text="UDP", variable=var_protocol, value='UDP').pack(side=tk.LEFT)



# Botón para iniciar el escaneo
scan_button = ttk.Button(root, text="Iniciar Escaneo", command=run_scan)
scan_button.pack(pady=20)



# Cuadro de texto para mostrar resultados
results_text = scrolledtext.ScrolledText(root, width=90, height=20,
                                         bg="#282a36", fg="white", insertbackground="white",
                                         font=("Consolas", 11), relief=tk.FLAT)
results_text.pack(pady=10)



# Iniciar la interfaz gráfica
root.mainloop()
