import logging
from scapy.all import sr, sr1, TCP, RandShort
from scapy.layers.inet import IP
import socket

# Configuración del registro 
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
# funciones y condicionales
def syn_scan(target_ip, target_port):
    src_port = RandShort()
    response = sr1(IP(dst=target_ip)/TCP(sport=src_port, dport=target_port, flags="S"), timeout=2, verbose=False)
    
    if response is None:
        return "Filtrado"
    elif response.haslayer(TCP):
        if response.getlayer(TCP).flags == 0x12:  # SYN-ACK
            send_rst = sr(IP(dst=target_ip)/TCP(sport=src_port, dport=target_port, flags="R"), timeout=2, verbose=False)
            return "Abierto"
        elif response.getlayer(TCP).flags == 0x14:  # RST
            return "Cerrado"

def xmas_scan(target_ip, target_port):
    response = sr1(IP(dst=target_ip)/TCP(dport=target_port, flags="FPU"), timeout=2, verbose=False)
    
    if response is None:
        return "Abierto|Filtrado"
    elif response.haslayer(TCP) and response.getlayer(TCP).flags == 0x14:
        return "Cerrado"

def null_scan(target_ip, target_port):
    response = sr1(IP(dst=target_ip)/TCP(dport=target_port, flags=""), timeout=2, verbose=False)
    
    if response is None:
        return "Abierto|Filtrado"
    elif response.haslayer(TCP) and response.getlayer(TCP).flags == 0x14:
        return "Cerrado"

def fin_scan(target_ip, target_port):
    response = sr1(IP(dst=target_ip)/TCP(dport=target_port, flags="F"), timeout=2, verbose=False)
    
    if response is None:
        return "Abierto|Filtrado"
    elif response.haslayer(TCP) and response.getlayer(TCP).flags == 0x14:
        return "Cerrado"

def identify_service(port):
    if port == 21:  # Puerto FTP
        return "FTP"
    elif port == 80:  # Puerto HTTP
        return "HTTP"
    elif port == 443:  # Puerto HTTPS
        return "HTTPS"
    else:
        return "Desconocido"  # Otros puertos no identificados

def get_ports(scan_type):
    if scan_type == 'rápido':
        return [22, 80, 443]  # Puertos comunes
    elif scan_type == 'completo':
        return range(1, 65536)  # Todos los puertos
    elif scan_type == 'personalizado':
        ports_input = input("Ingresa los puertos a escanear (separados por comas): ")
        return [int(port.strip()) for port in ports_input.split(",")]
    else:
        print("Tipo de escaneo no válido. Usando escaneo rápido por defecto.")
        return [22, 80, 443]

def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

if __name__ == "__main__":
    target = input("Ingresa la IP del objetivo: ")
    
    while not validate_ip(target):
        print("Dirección IP no válida. Inténtalo de nuevo.")
        target = input("Ingresa la IP del objetivo: ")

    print("\nSelecciona el tipo de escaneo:")
    print("1. Rápido")
    print("2. Completo")
    print("3. Personalizado")
    
    choice = input("Ingresa el número de tu elección (1/2/3): ")
    
    if choice == '1':
        scan_type = 'rápido'
    elif choice == '2':
        scan_type = 'completo'
    elif choice == '3':
        scan_type = 'personalizado'
    else:
        print("Opción no válida. Usando escaneo rápido por defecto.")
        scan_type = 'rápido'

    ports = get_ports(scan_type)

    results = []
    
    for port in ports:
        print(f"Escaneando puerto {port}...")
        
        syn_result = syn_scan(target, port)
        xmas_result = xmas_scan(target, port)
        null_result = null_scan(target, port)
        fin_result = fin_scan(target, port)
        
        service_name = identify_service(port)
        
        results.append({
            'port': port,
            'syn_status': syn_result,
            'xmas_status': xmas_result,
            'null_status': null_result,
            'fin_status': fin_result,
            'service': service_name
        })
        
        print(f"Puerto {port} - SYN: {syn_result}, XMAS: {xmas_result}, NULL: {null_result}, FIN: {fin_result}, Servicio: {service_name}")


