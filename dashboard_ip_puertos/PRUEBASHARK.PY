
import nmap
import pyshark

# --- Funciones para la detección de dispositivos con pyshark ---
def capture_and_analyze_packets(interface='eth0', timeout=10):
        """
        Captura paquetes de red y analiza dispositivos conectados.
        :param interface: Interfaz de red (por ejemplo, 'eth0' o 'wlan0').
        :param timeout: Tiempo de captura en segundos.
        """
        print(f"Iniciando captura en la interfaz {interface}...")

        # Configurar la captura de paquetes
        capture = pyshark.LiveCapture(interface=interface)

        # Iniciar la captura
        capture.sniff(timeout=timeout)

        # Analizar los paquetes capturados
        devices = {}
        for packet in capture:
            try:
                if 'IP' in packet:
                    ip = packet.ip.src
                    mac = packet.eth.src if 'ETH' in packet else "Desconocido"
                    protocol = packet.transport_layer if hasattr(packet, 'transport_layer') else "Desconocido"

                    # Detectar sistema operativo (fingerprinting básico)
                    os_type = detect_os(packet)

                    # Almacenar información del dispositivo
                    if ip not in devices:
                        devices[ip] = {
                            'mac': mac,
                            'protocol': protocol,
                            'os': os_type,
                            'hostname': resolve_hostname(ip),
                        }

            except AttributeError:
                continue

        return devices

    def detect_os(packet):
        """
        Intenta detectar el sistema operativo basado en el TTL y otros campos del paquete.
        """
        if 'IP' in packet:
            ttl = int(packet.ip.ttl)
            if ttl <= 64:
                return "Linux/Unix"
            elif ttl <= 128:
                return "Windows"
            elif ttl <= 255:
                return "Cisco/OTROS"
        return "Desconocido"

    def resolve_hostname(ip):
        """
        Intenta resolver el nombre de host a partir de la dirección IP.
        """
        try:
            return socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            return "Desconocido"

    def run_device_discovery(e):
        """
        Ejecuta la detección de dispositivos y muestra los resultados en la interfaz.
        """
        results_text.value = "Detectando dispositivos...\n"
        page.update()

        # Ejecutar la captura en un hilo separado
        threading.Thread(target=start_device_discovery).start()

    def start_device_discovery():
        """
        Inicia la captura y análisis de dispositivos.
        """
        devices = capture_and_analyze_packets(interface='eth0', timeout=30)
        results_text.value = "Dispositivos detectados:\n"
        for ip, info in devices.items():
            results_text.value += f"IP: {ip}, MAC: {info['mac']}, OS: {info['os']}, Hostname: {info['hostname']}\n"
        page.update()
