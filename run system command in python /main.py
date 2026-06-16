import sys
import subprocess
import shlex

while True:
    try:
        # 1. Lecture et nettoyage de l'entrée utilisateur
        com = input("> ").strip()

        # Pas d'action si l'entrée est vide
        if not com:
            continue

        # 2. Condition de sortie
        if com.lower() in ["exit", "quit", "q"]:
            print("Fermeture du terminal.")
            break

        # 3. Découpage sécurisé de la commande et de ses arguments
        args = shlex.split(com)

        # 4. Exécution sécurisée
        subprocess.run(args, check=True)

    except FileNotFoundError:
        print("Erreur : Commande introuvable.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur : La commande a échoué avec le code {e.returncode}.")
    except KeyboardInterrupt:
        # Permet de quitter proprement avec Ctrl+C
        print("\nFermeture du terminal.")
        sys.exit(0)
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")