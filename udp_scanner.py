import socket

def scan_udp(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1)
        sock.sendto(b'', (host, port))
        sock.recvfrom(1024)
        return f"Puerto UDP {port} abierto"
    except socket.timeout:
        return f"Puerto UDP {port} filtrado"
    except Exception as e:
        return f"Error en el puerto UDP {port}: {e}"
