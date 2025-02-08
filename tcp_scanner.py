import socket
# funcion resive el parametro host y port
def scan_tcp(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            return f"Puerto TCP {port} abierto"
        else:
            return f"Puerto TCP {port} cerrado"
    except Exception as e:
        return f"Error en el puerto TCP {port}: {e}"
    finally:
        sock.close()
