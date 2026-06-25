import scapy.all as scapy
def scan(ip_range):
    # 1. Créer une requête ARP pour demander qui possède les IP de la plage
    arp_request = scapy.ARP(pdst=ip_range)
    
    # 2. Créer un paquet Ethernet de Broadcast (diffusion générale)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    
    # 3. Combiner les deux paquets (Ethernet / ARP)
    arp_request_broadcast = broadcast / arp_request
    
    # 4. Envoyer le paquet combiné et attendre les réponses (timeout de 2 secondes)
    # srp() permet d'envoyer et recevoir des paquets au niveau de la couche 2 (Liaison)
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    # 5. Analyser les réponses reçues
    clients_list = []
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(client_dict)
        
    return clients_list

def display_result(results_list):
    print("\n[+] Appareils trouvés sur le réseau :")
    print("-----------------------------------------")
    print("Adresse IP\t\tAdresse MAC")
    print("-----------------------------------------")
    for client in results_list:
        print(f"{client['ip']}\t\t{client['mac']}")
    print("-----------------------------------------\n")



display_result(scan("192.168.1.0/24"))