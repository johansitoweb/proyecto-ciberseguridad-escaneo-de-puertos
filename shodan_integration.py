import shodan
import json
import argparse
import socket
import subprocess
import ipaddress

def validate_ip(ip):
    """Valida si la dirección IP es correcta."""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def get_local_info(target_ip, nmap_options):
    """Obtiene información local sobre la IP objetivo usando nmap."""
    local_info = {}
    
    # Obtener el nombre de host local
    try:
        host_name = socket.gethostbyaddr(target_ip)[0]
        local_info['host_name'] = host_name
    except socket.herror:
        local_info['host_name'] = 'N/A'

    # Realizar un escaneo local con nmap
    try:
        nmap_command = ['nmap', *nmap_options.split(), target_ip]
        nmap_output = subprocess.check_output(nmap_command, universal_newlines=True)
        local_info['nmap_output'] = nmap_output
    except subprocess.CalledProcessError as e:
        local_info['nmap_output'] = f'Error al ejecutar nmap: {e}'

    return local_info

def get_shodan_info(api_key, target_ip, nmap_options, save_to_file=False):
    """Obtiene información de Shodan y la combina con información local."""
    api = shodan.Shodan(api_key)  # Inicializar la API de Shodan
    try:
        # Obtener información de la IP objetivo
        ip_info = api.host(target_ip)
        print(f"Información de {target_ip}:")
        print(f"Organización: {ip_info.get('org', 'N/A')}")
        print(f"Ubicación: {ip_info.get('city', 'N/A')}, {ip_info.get('country_name', 'N/A')}")
        print(f"ISP: {ip_info.get('isp', 'N/A')}")
        print(f"Puerto(s) Abierto(s): {[service['port'] for service in ip_info['data']]}")

        # Mostrar información de servicios
        for service in ip_info['data']:
            print(f"\nServicio en el puerto {service['port']}:")
            print(f"  - Protocolo: {service['transport']}")
            print(f"  - Nombre: {service.get('product', 'N/A')}")
            print(f"  - Versión: {service.get('version', 'N/A')}")
            print(f"  - Banner: {service.get('data', 'N/A')}")

        # Obtener información local
        local_info = get_local_info(target_ip, nmap_options)

        # Combinar información de Shodan y local
        combined_info = {
            'shodan_info': ip_info,
            'local_info': local_info
        }

        # Mostrar información combinada
        print("\nInformación combinada:")
        print(json.dumps(combined_info, indent=4))

        # Guardar resultados en un archivo JSON
        if save_to_file:
            with open(f"{target_ip}_info.json", 'w') as json_file:
                json.dump(combined_info, json_file, indent=4)
            print(f"Información guardada en {target_ip}_info.json")

    except shodan.APIError as e:
        print(f"Error de API: {e}")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Obtener información de Shodan para una o más IPs específicas.')
    parser.add_argument('api_key', type=str, help='Tu API Key de Shodan.')
    parser.add_argument('target_ips', type=str, nargs='+', help='Una o más IPs objetivo para escanear.')
    parser.add_argument('--nmap_options', type=str, default='-sV', help='Opciones adicionales para nmap (por defecto: -sV).')
    parser.add_argument('--save', action='store_true', help='Guardar la información en archivos JSON.')

    args = parser.parse_args()

    for target_ip in args.target_ips:
        # Validar la IP
        if not validate_ip(target_ip):
            print(f"La dirección IP {target_ip} no es válida.")
            continue
        # Obtener información de Shodan
        get_shodan_info(args.api_key, target_ip, args.nmap_options, args.save)

if __name__ == "__main__":
    main()