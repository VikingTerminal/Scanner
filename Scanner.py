import os
import requests
import socket
import whois
from colorama import Fore, init
import time
from urllib.request import urlopen
from urllib.error import URLError
from bs4 import BeautifulSoup

init(autoreset=True)

def check_network_connection():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

def get_ip_info(ip_address):
    try:
        response = requests.get(f'https://ipinfo.io/{ip_address}')
        if response.status_code == 200:
            ip_info = response.json()
            return ip_info
        else:
            return f"Errore nella richiesta: {response.status_code}"
    except Exception as e:
        return f"Errore durante la richiesta: {str(e)}"

def nslookup_with_additional_info(ip_address):
    try:
        whois_info = whois.whois(ip_address)
        ip_info = {
            "Indirizzo IP": ip_address,
            "WHOIS": whois_info
        }

        try:
            additional_info = socket.gethostbyaddr(ip_address)
            ip_info["AdditionalInfo"] = additional_info
        except socket.herror as e:
            ip_info["AdditionalInfo"] = f"Errore durante nslookup: {str(e)}"

        return ip_info

    except socket.herror as e:
        return f"Errore durante nslookup: {str(e)}"
    except Exception as e:
        return f"Errore durante nslookup: {str(e)}. Potrebbe non esserci un host associato a questo indirizzo IP o potrebbero esserci delle limitazioni imposte ad alcuni script esterni."

def efficient_nslookup(domain):
    try:
        ip_address = socket.gethostbyname(domain)
        full_info = socket.gethostbyaddr(ip_address)
        return f"Hostname: {full_info[0]}\nIndirizzo IP: {ip_address}\nAlias: {', '.join(full_info[1])}"
    except socket.herror as e:
        return f"Errore durante nslookup: {str(e)}"
    except socket.gaierror as e:
        return f"Errore durante nslookup: {str(e)}"

def clone_website(url, output_folder):
    try:
        response = urlopen(url)
        html_content = response.read()
        soup = BeautifulSoup(html_content, 'html.parser')

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with open(os.path.join(output_folder, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))

        print(f"Sito {url} clonato con successo nella cartella {output_folder}")
    except URLError as e:
        print(f"Errore durante la clonazione del sito: {str(e.reason)}")
    except Exception as e:
        print(f"Errore generico durante la clonazione del sito: {str(e)}")

def print_with_typing_effect(text, color=Fore.RESET):
    inside_escape = False
    for char in text:
        if char == '\033':
            inside_escape = True
        elif inside_escape and char == 'm':
            inside_escape = False
        elif not inside_escape:
            print(color + char, end='', flush=True)
            time.sleep(0.02)
    print()

def scan_open_ports(ip_address, start_port, end_port):
    open_ports = []
    try:
        for port in range(start_port, end_port + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                result = s.connect_ex((ip_address, port))
                if result == 0:
                    open_ports.append(port)
                    print(f"Porta {port} aperta su {ip_address}")
    except Exception as e:
        return f"Errore durante la scansione delle porte: {str(e)}"

    return open_ports

def get_user_choice():
    return input(f"{Fore.GREEN}Scegli un'opzione:\n1. nslookup\n2. Scansione IP\n3. Scansione porte\n4. Clona sito\n\nInserisci il numero corrispondente (scrivi 'exit' per uscire): ")

def get_user_input(message):
    return input(f"{Fore.LIGHTCYAN_EX}{message} (scrivi 'exit' per uscire): ")

user_choice = get_user_choice()

while user_choice.lower() != 'exit':
    if user_choice == '1' or user_choice.lower() == 'nslookup':
        user_input = get_user_input("Inserisci l'indirizzo IP o il dominio per nslookup: ")
        if user_input.lower() == 'exit':
            break
        result = nslookup_with_additional_info(user_input) if user_input.replace('.', '').isdigit() else efficient_nslookup(user_input)
        print_with_typing_effect(result, color=Fore.GREEN if isinstance(result, dict) else Fore.RED)

    elif user_choice == '2' or user_choice.lower() == 'scansione ip':
        user_ip = get_user_input("Inserisci l'indirizzo IP per la scansione: ")
        if user_ip.lower() == 'exit':
            break
        if check_network_connection():
            ip_info = get_ip_info(user_ip)
            print_with_typing_effect(f"Indirizzo IP: {ip_info.get('ip')}", color=Fore.GREEN)
            print_with_typing_effect(f"Posizione: {ip_info.get('city')}, {ip_info.get('region')}, {ip_info.get('country')}", color=Fore.YELLOW)
            print_with_typing_effect(f"ISP: {ip_info.get('org')}", color=Fore.YELLOW)
            print_with_typing_effect(f"Coordinate geografiche: {ip_info.get('loc')}", color=Fore.YELLOW)
        else:
            print_with_typing_effect(f"Nessuna connessione di rete disponibile.", color=Fore.RED)

    elif user_choice == '3' or user_choice.lower() == 'scansione porte':
        user_ip = get_user_input("Inserisci l'indirizzo IP o il dominio per la scansione delle porte:")
        if user_ip.lower() == 'exit':
            break
        start_port = int(input("Inserisci il numero della porta di inizio: "))
        end_port = int(input("Inserisci il numero della porta di fine: "))

        if check_network_connection():
            print_with_typing_effect(f"Inizia la scansione delle porte per {user_ip}...", color=Fore.YELLOW)
            open_ports = scan_open_ports(user_ip, start_port, end_port)
            if open_ports:
                print_with_typing_effect(f"Porte aperte su {user_ip}: {open_ports}", color=Fore.GREEN)
            else:
                print_with_typing_effect(f"Nessuna porta aperta trovata.", color=Fore.RED)
        else:
            print_with_typing_effect(f"Nessuna connessione di rete disponibile.", color=Fore.RED)

    elif user_choice == '4' or user_choice.lower() == 'clona sito':
        user_url = get_user_input("Inserisci l'URL del sito da clonare (includi http:// o https://): ")
        if user_url.lower() == 'exit':
            break
        user_output_folder = get_user_input("Inserisci il percorso della cartella dove vuoi memorizzare il.sito clonato ")
        if user_output_folder.lower() == 'exit':
            break

        clone_website(user_url, user_output_folder)

    else:
        print_with_typing_effect(f"Opzione non valida. Riprova.", color=Fore.RED)

    user_choice = get_user_choice()

print_with_typing_effect(f"Grazie per l'utilizzo di questo tool! Creato da t.me/Rapid85")
