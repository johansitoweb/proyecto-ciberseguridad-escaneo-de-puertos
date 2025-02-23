import json
import requests
import argparse
import re
import logging

# Configuración del registro
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_ip(ip):
    """Verifica si la dirección IP es válida."""
    pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
    return pattern.match(ip) is not None

def scan_ip(target_ip, use_https=False, timeout=5):
    """Escanea la dirección IP objetivo y devuelve información sobre la respuesta HTTP."""
    protocol = 'https' if use_https else 'http'
    url = f'{protocol}://{target_ip}'

    headers = {'User-Agent': 'MyScanner/1.0'}

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()  # Lanza un error para códigos de estado 4xx/5xx
        logging.info(f"Successful scan on {target_ip}.")
        return {
            'status_code': response.status_code,
            'content_length': len(response.content),
            'content': response.text
        }
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error for {target_ip}: {http_err}')
        return {'error': f'HTTP error occurred: {http_err}', 'status_code': http_err.response.status_code}
    except requests.exceptions.ConnectionError:
        logging.error(f'Connection error for {target_ip}.')
        return {'error': 'Connection error occurred. Check the target IP.'}
    except requests.exceptions.Timeout:
        logging.warning(f'Request timed out for {target_ip}.')
        return {'error': 'Request timed out.'}
    except requests.exceptions.RequestException as req_err:
        logging.error(f'Request exception for {target_ip}: {req_err}')
        return {'error': f'Request exception occurred: {req_err}'}
    except Exception as cerr:
        logging.critical(f'Unexpected error for {target_ip}: {cerr}')
        return {'error': f'An unexpected error occurred: {cerr}'}

def save_results(results, filename='scan_results.json'):
    """Guarda los resultados del escaneo en un archivo JSON."""
    with open(filename, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    logging.info(f'Results saved to {filename}')

def main():
    parser = argparse.ArgumentParser(description='Scan target IP addresses for HTTP responses.')
    parser.add_argument('target_ips', type=str, nargs='+', help='The target IP addresses to scan.')
    parser.add_argument('--https', action='store_true', help='Use HTTPS instead of HTTP.')
    parser.add_argument('--timeout', type=int, default=5, help='Default timeout for requests in seconds.')
    parser.add_argument('--output', type=str, default='scan_results.json', help='Output filename for the results.')

    args = parser.parse_args()

    results = {}
    
    for ip in args.target_ips:
        if not is_valid_ip(ip):
            logging.error(f"Invalid IP address provided: {ip}. Skipping.")
            continue

        result = scan_ip(ip, use_https=args.https, timeout=args.timeout)
        results[ip] = result
        print(json.dumps(result, indent=4))

    # Guardar resultados en un archivo JSON
    save_results(results, filename=args.output)

if __name__ == "__main__":
    main()