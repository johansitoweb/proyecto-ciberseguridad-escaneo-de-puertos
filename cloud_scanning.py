import json
import requests
import argparse

def scan_ip(target_ip, use_https=False, timeout=5):
    """Escanea la dirección IP objetivo y devuelve información sobre la respuesta HTTP."""
    protocol = 'https' if use_https else 'http'
    url = f'{protocol}://{target_ip}'

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Lanza un error para códigos de estado 4xx/5xx
        return {
            'status_code': response.status_code,
            'content_length': len(response.content),
            'content': response.text
        }
    except requests.exceptions.HTTPError as http_err:
        return {'error': f'HTTP error occurred: {http_err}', 'status_code': http_err.response.status_code}
    except requests.exceptions.ConnectionError:
        return {'error': 'Connection error occurred. Check the target IP.'}
    except requests.exceptions.Timeout:
        return {'error': 'Request timed out.'}
    except requests.exceptions.RequestException as req_err:
        return {'error': f'Request exception occurred: {req_err}'}
    except Exception as err:
        return {'error': f'An unexpected error occurred: {err}'}

def save_results(results, filename='scan_results.json'):
    """Guarda los resultados del escaneo en un archivo JSON."""
    with open(filename, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    print(f'Results saved to {filename}')

def main():
    parser = argparse.ArgumentParser(description='Scan a target IP address for HTTP response.')
    parser.add_argument('target_ip', type=str, help='The target IP address to scan.')
    parser.add_argument('--https', action='store_true', help='Use HTTPS instead of HTTP.')
    parser.add_argument('--timeout', type=int, default=5, help='Timeout for the request in seconds.')

    args = parser.parse_args()

    result = scan_ip(args.target_ip, use_https=args.https, timeout=args.timeout)
    print(json.dumps(result, indent=4))

    # Guardar resultados en un archivo JSON
    save_results(result)

if __name__ == "__main__":
    main()