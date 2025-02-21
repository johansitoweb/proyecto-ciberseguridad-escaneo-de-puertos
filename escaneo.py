import flet as ft
import socket
import threading
import logging
from scapy.all import IP, IPv6, TCP, sr1, RandShort, UDP
import subprocess
import os
import nmap
import pyshark

# Importaciones de las funcionalidades avanzadas
import anomaly_detection
import cloud_scanning
import conetbase
import stealth_mode
import Report

# Configuración del registro
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def main(page: ft.Page):
    # Configuración de la página
    page.title = "Panel de Escaneo"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 0  # Eliminar el padding para que la imagen de fondo cubra toda la pantalla
    page.bgcolor = ft.colors.BLACK  # Fondo de respaldo por si la imagen no carga
    # URL de la imagen de fondo
    background_image_url = "https://i.pinimg.com/736x/65/92/b0/6592b033badec6e157457a969305e1b1.jpg"
    # --- Funciones para las funcionalidades avanzadas ---
    def open_anomaly_detection(e):
        csv_path = Report.obtener_ruta_csv()
        anomaly_detection.detect_anomalies(csv_path)
        page.snack_bar = ft.SnackBar(ft.Text("Detección de anomalías completada."))
        page.snack_bar.open = True
        page.update()

    def open_cloud_scanning(e):
        target_ip = entry_target.value
        if target_ip:
            csv_path = Report.obtener_ruta_csv()
            cloud_scanning.scan_ip(target_ip, csv_path)
            page.snack_bar = ft.SnackBar(ft.Text("Escaneo en la nube completado."))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor ingresa una IP objetivo."))
            page.snack_bar.open = True
        page.update()

    def open_stealth_mode(e):
        target_ip = entry_target.value
        if target_ip:
            csv_path = Report.obtener_ruta_csv()
            stealth_mode.stealth_scan(target_ip, start_port=1, end_port=1024, delay=0.1, csv_path=csv_path)
            page.snack_bar = ft.SnackBar(ft.Text("Modo sigiloso completado."))
            page.snack_bar.open = True
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor ingresa una IP objetivo."))
            page.snack_bar.open = True
        page.update()

    def generar_reporte_pdf(e):
        Report.generar_reporte_pdf()
        page.snack_bar = ft.SnackBar(ft.Text("Reporte PDF generado correctamente."))
        page.snack_bar.open = True
        page.update()

    def exportar_csv(e):
        Report.exportar_csv()
        page.snack_bar = ft.SnackBar(ft.Text("Reporte CSV generado correctamente."))
        page.snack_bar.open = True
        page.update()

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

    def run_scan(e):
        target = entry_target.value
        if not validate_ip(target):
            page.snack_bar = ft.SnackBar(ft.Text("Dirección IP no válida."))
            page.snack_bar.open = True
            page.update()
            return

        scan_type = var_scan_type.value
        protocol = var_protocol.value

        if scan_type == "rápido":
            ports = [22, 53, 80, 443]
        elif scan_type == "completo":
            ports = range(1, 101)
        elif scan_type == "personalizado":
            ports_input = entry_ports.value
            try:
                ports = [int(port.strip()) for port in ports_input.split(",")]
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("Por favor ingresa una lista válida de números de puerto separados por comas."))
                page.snack_bar.open = True
                page.update()
                return

        # Lanza el escaneo en un hilo separado para no bloquear la interfaz gráfica
        threading.Thread(target=start_scan, args=(target, ports, protocol)).start()

    def start_scan(target, ports, protocol):
        results_text.value = ""
        progress_bar.value = 0
        num_ports = len(ports)
        progress_step = 100 / num_ports if num_ports > 0 else 0

        for i, port in enumerate(ports):
            results_text.value += f"Escaneando puerto {port}...\n"
            page.update()

            if protocol == "TCP":
                syn_result = syn_scan(target, port, ":" in target)
                service_name = identify_service(port)
                results_text.value += f"Puerto {port} - TCP: {syn_result}, Servicio: {service_name}\n"
            elif protocol == "UDP":
                udp_results = scan_udp(target, [port])
                service_name = identify_service(port)
                results_text.value += f"Puerto {port} - UDP: {udp_results[port]}, Servicio: {service_name}\n"

            progress_bar.value += progress_step
            page.update()

        page.snack_bar = ft.SnackBar(ft.Text("Escaneo completado."))
        page.snack_bar.open = True
        page.update()

    def close_session(e):
        page.window_destroy()
        login_script_path = "loginappescritorio.py"
        if not os.path.exists(login_script_path):
            page.snack_bar = ft.SnackBar(ft.Text(f"El archivo loginappescritorio.py no se encuentra en la ruta especificada: {login_script_path}"))
            page.snack_bar.open = True
            page.update()
            return
        try:
            subprocess.Popen(["python", login_script_path])
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error al iniciar loginappescritorio.py: {e}"))
            page.snack_bar.open = True
            page.update()

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

    # Interfaz Gráfico
    entry_target = ft.TextField(label="IP del objetivo (IPv4 o IPv6):", width=400, border_color=ft.colors.WHITE, color=ft.colors.WHITE, label_style=ft.TextStyle(color=ft.colors.WHITE))
    var_scan_type = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="rápido", label="Rápido", fill_color=ft.colors.BLUE, label_style=ft.TextStyle(color=ft.colors.WHITE)),
                ft.Radio(value="completo", label="Completo (primeros 100 puertos)", fill_color=ft.colors.BLUE, label_style=ft.TextStyle(color=ft.colors.WHITE)),
                ft.Radio(value="personalizado", label="Personalizado", fill_color=ft.colors.BLUE, label_style=ft.TextStyle(color=ft.colors.WHITE)),
            ]
        )
    )
    entry_ports = ft.TextField(label="Puertos personalizados (separados por comas):", label_style=ft.TextStyle(color=ft.colors.WHITE), width=400, color=ft.colors.WHITE, border_color=ft.colors.WHITE)
    var_protocol = ft.RadioGroup(
        content=ft.Column(
            [
                ft.Radio(value="TCP", label="TCP", fill_color=ft.colors.BLUE, label_style=ft.TextStyle(color=ft.colors.WHITE)),
                ft.Radio(value="UDP", label="UDP", fill_color=ft.colors.BLUE, label_style=ft.TextStyle(color=ft.colors.WHITE)),
            ]
        )
    )
    scan_button = ft.ElevatedButton(text="Iniciar Escaneo", on_click=run_scan, color=ft.colors.WHITE, bgcolor=ft.colors.BLUE)
    detect_button = ft.ElevatedButton(text="Detectar Dispositivos", on_click=run_device_discovery, color=ft.colors.WHITE, bgcolor=ft.colors.BLUE)
    progress_bar = ft.ProgressBar(width=600, color=ft.colors.BLUE)
    results_text = ft.TextField( 
        multiline=True,
        read_only=True,
        width=600,
        height=300,
        color=ft.colors.WHITE,
        bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLUE),  # Fondo azul claro
    )
    results_container = ft.Column(
        [results_text],
        scroll=ft.ScrollMode.AUTO,  # Habilitar scroll automático
        width=590,
        height=590,
    )
    close_button = ft.ElevatedButton(text="Cerrar Sesión", on_click=close_session, color=ft.colors.WHITE, bgcolor=ft.colors.RED)  # Botón rojo para cerrar sesión

    # Menú de funcionalidades avanzadas
    advanced_menu = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(text="Detección de Anomalías", on_click=lambda _: open_anomaly_detection()),
            ft.PopupMenuItem(text="Escaneo en la Nube", on_click=lambda _: open_cloud_scanning()),
            ft.PopupMenuItem(text="Modo Sigiloso", on_click=lambda _: open_stealth_mode()),
            ft.PopupMenuItem(text="Generar Reporte PDF", on_click=lambda _: generar_reporte_pdf()),
            ft.PopupMenuItem(text="Exportar Reporte CSV", on_click=lambda _: exportar_csv()),
        ]
    )

    # Encabezado decorado
    header = ft.Text(
        "Panel de Escaneo",
        size=46,
        weight=ft.FontWeight.BOLD,
        color=ft.colors.WHITE,
        text_align=ft.TextAlign.CENTER,
        style=ft.TextStyle(
            shadow=ft.BoxShadow(
                blur_radius=10,
                color=ft.colors.BLUE_800,
                offset=ft.Offset(2, 2),
            )
        )
    )

    # Contenedor con la imagen de fondo y superposición oscura
    background_container = ft.Container(
        width=page.width,  # Usar el ancho de la ventana
        height=page.height,  # Usar la altura de la ventana
        image_src=background_image_url,
        image_fit=ft.ImageFit.COVER,
        content=ft.Container(
            width=page.width,
            height=page.height,
            bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLACK),  # Superposición oscura
            content=ft.Column(
                [
                    header,
                    ft.Divider(color=ft.colors.BLUE, height=40),  # Línea divisoria azul
                    ft.Text("Tipo de escaneo", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                    ft.Row([entry_target, advanced_menu], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    var_scan_type,
                    entry_ports,  # Campo de puertos personalizados
                    ft.Divider(color=ft.colors.BLUE, height=40),  # Línea divisoria azul
                    ft.Text("Selecciona el protocolo", size=28, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                    var_protocol,
                    ft.Divider(color=ft.colors.BLUE, height=40),  # Línea divisoria azul
                    ft.Row([scan_button, detect_button], spacing=20,alignment=ft.MainAxisAlignment.CENTER),  # Botones alineados horizontalmente
                    progress_bar,
                    results_container,  # Usar el Column con scroll
                    close_button,
                ],
                spacing=20,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,  # Habilitar scroll en la columna principal
               
            ),
            padding=30,  # Añadir padding para que el contenido no esté pegado a los bordes
        ),
    )

    # Añadir el contenedor a la página
    page.add(background_container)


# Iniciar la aplicación
ft.app(target=main)