#!/usr/bin/env python3
import sys
from scapy.all import IP, ICMP, sr1  # <-- Correction de l'import ici

print("--- Générateur de Paquets ICMP Personnalisés ---")
print("Appuyez sur Ctrl+C pour quitter le script.\n")

while True:
    try:
        # Demande de la cible
        dst_ip = input("Destination (IP ou Nom de domaine) > ").strip()
        if not dst_ip:
            print("[!] La destination ne peut pas être vide.\n")
            continue

        # Optionnel : On peut laisser l'utilisateur choisir une IP source
        # ou appuyer sur Entrée pour la laisser en automatique.
        src_ip = input("Source IP (Optionnel - Entrée pour Auto) > ").strip()

        # Construction intelligente du header IP
        if src_ip:
            ip_head = IP(src=src_ip, dst=dst_ip)
        else:
            ip_head = IP(dst=dst_ip)  # Scapy gère l'IP source tout seul

        # Configuration ICMP (avec l'ID personnalisé à 100 comme sur votre capture)
        icmp_option = ICMP(id=100)

        # Assemblage des couches réseau
        full_packet = ip_head / icmp_option

        print(f"[*] Envoi du paquet vers {dst_ip}...")

        # Envoi et attente d'une réponse (timeout de 2s pour éviter de bloquer indéfiniment)
        packet_sender = sr1(full_packet, timeout=2, verbose=False)

        if packet_sender:
            print("\n[+] Réponse reçue ! Affichage des détails :")
            packet_sender.show()
            print("-" * 50 + "\n")
        else:
            print("[─] Aucune réponse reçue (Délai d'attente dépassé).\n")

    except KeyboardInterrupt:
        print("\n\n[!] Script interrompu. Au revoir !")
        sys.exit(0)
    except Exception as e:
        print(f"[ERREUR] Une erreur est survenue : {e}\n")