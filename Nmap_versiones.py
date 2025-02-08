import nmap

def nmap_scan(target_ip):
    nm = nmap.PortScanner()
    nm.scan(target_ip)

    for proto in nm[target_ip].all_protocols():
        lport = nm[target_ip][proto].keys()
        for port in sorted(lport):
            state = nm[target_ip][proto][port]['state']
            service = nm[target_ip][proto][port]['name']
            print(f"Puerto: {port} - Estado: {state} - Servicio: {service}")

if __name__ == "__main__":
    target = input("Ingresa la IP del objetivo para Nmap: ")
    nmap_scan(target)
