import argparse
import time
import threading
from scapy.all import IP, TCP, sr1, conf
import json

# Configuración de Scapy
conf.verb = 0  # Desactivar la salida de Scapy
open_ports = []
closed_ports = []

def scan_port(target_ip, port, timeout):
    """Escanea un puerto y determina si está abierto o cerrado."""
    try:
        packet = IP(dst=target_ip) / TCP(dport=port, flags="S")
        response = sr1(packet, timeout=timeout, verbose=0)
        if response and response.haslayer(TCP):
            if response[TCP].flags == 0x12:  # SYN-ACK
                open_ports.append(port)
                print(f"\033[92mPuerto {port} está abierto.\033[0m")  # Verde
            elif response[TCP].flags == 0x14:  # RST
                closed_ports.append(port)
                print(f"Puerto {port} está cerrado.")
        else:
            print(f"No se recibió respuesta del puerto {port}.")
    except Exception as e:
        print(f"Error al escanear el puerto {port}: {e}")

def stealth_scan(target_ip, start_port, end_port, delay, timeout):
    """Realiza un escaneo de puertos en el rango especificado."""
    threads = []
    for port in range(start_port, end_port + 1):
        thread = threading.Thread(target=scan_port, args=(target_ip, port, timeout))
        threads.append(thread)
        thread.start()
        time.sleep(delay)  # Controlar la velocidad del escaneo

    for thread in threads:
        thread.join()  # Esperar a que todos los hilos terminen

def save_results(filename):
    """Guarda los resultados de los escaneos en un archivo JSON."""
    results = {
        "open_ports": open_ports,
        "closed_ports": closed_ports
    }
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Resultados guardados en {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Escanear puertos de una IP objetivo.')
    parser.add_argument('target_ip', type=str, help='La IP objetivo a escanear.')
    parser.add_argument('--start', type=int, default=1, help='Puerto de inicio (por defecto: 1).')
    parser.add_argument('--end', type=int, default=1024, help='Puerto de fin (por defecto: 1024).')
    parser.add_argument('--delay', type=float, default=0.1, help='Retraso entre envíos de paquetes (en segundos).')
    parser.add_argument('--timeout', type=float, default=1, help='Timeout para la respuesta (en segundos).')
    parser.add_argument('--output', type=str, default='scan_results.json', help='Archivo para guardar resultados.')

    args = parser.parse_args()
    stealth_scan(args.target_ip, args.start, args.end, args.delay, args.timeout)
    save_results(args.output)