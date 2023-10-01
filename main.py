import os
import sys
import socket
import requests
from ipwhois import IPWhois
import ssl
import pyfiglet
from colorama import init, Fore, Style
import webbrowser
import time
import subprocess

def disable_ansi_on_windows():
    if sys.platform.startswith('win'):
        os.system('color')

def print_banner():
    banner = pyfiglet.figlet_format("WICK TOOL", font="slant")
    print(Fore.YELLOW + banner + Style.RESET_ALL)
    print(Fore.CYAN + "Welcome to the IP Information Retrieval Tool" + Style.RESET_ALL)
    print()

def print_contact_info():
    print(Fore.YELLOW + "Contact Information:" + Style.RESET_ALL)
    print("1. Website: https://https://wickdev.xyz/")
    print("2. GitHub: https://github.com/Wickdev077")
    print("3. Instagram: https://www.instagram.com/mik__subhi/")

def resolve_ip(ip_address):
    try:
        host = socket.gethostbyname(ip_address)
        return host
    except socket.gaierror:
        return None

def get_geolocation_info(ip_address):
    try:
        url = f"https://ipinfo.io/{ip_address}/json"
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        print(Fore.RED + f"Sorry, there was an error while retrieving geolocation information {str(e)}" + Style.RESET_ALL)
        return None

def print_colored_info(label, info):
    print(Fore.GREEN + f"{label}: " + Style.RESET_ALL + info)

def open_google_maps_with_delay(latitude, longitude):
    print(Fore.YELLOW + "Opening Google Maps..." + Style.RESET_ALL)
    time.sleep(3)
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
    webbrowser.open(google_maps_url)

def ping_ip(ip_address):
    try:
        result = subprocess.run(['ping', '-c', '4', ip_address], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        if result.returncode == 0:
            print(Fore.GREEN + "\nPing to IP Address:" + Style.RESET_ALL)
            print(result.stdout)
        else:
            print(Fore.RED + "\nPing to IP Address (Failed)" + Style.RESET_ALL)
            print(result.stderr)
    except subprocess.TimeoutExpired:
        print(Fore.RED + "\nPing to IP Address (Timed out)" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An error occurred while pinging the IP address: {str(e)}" + Style.RESET_ALL)

def get_ip_information(ip_address):
    resolved_ip = resolve_ip(ip_address)
    if resolved_ip:
        print_colored_info("Resolved IP Address", resolved_ip)
        try:
            ip_info = IPWhois(resolved_ip).lookup_rdap()
            print_colored_info("IP Range", ip_info['asn_cidr'])
            print_colored_info("Organization", ip_info['asn_description'])
            print_colored_info("Country", ip_info['asn_country_code'])

            geolocation_info = get_geolocation_info(resolved_ip)
            if geolocation_info:
                print(Fore.BLUE + "\nGeolocation Information :" + Style.RESET_ALL)
                print_colored_info("City", geolocation_info['city'])
                print_colored_info("Region", geolocation_info['region'])
                print_colored_info("Country", geolocation_info['country'])
                lat, lon = geolocation_info['loc'].split(',')
                print_colored_info("Latitude", lat)
                print_colored_info("Longitude", lon)

            if 'bogon' in geolocation_info.get('org', '').lower():
                print_colored_info("VPN/Proxy Detected", "Yes")
            else:
                print_colored_info("VPN/Proxy Detected", "No")

            get_ssl_certificate(resolved_ip)

        except Exception as e:
            print(Fore.RED + f"Oops, there was an error while fetching information: {str(e)}" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Sorry, we couldn't resolve the IP address for: {ip_address}" + Style.RESET_ALL)

def get_ssl_certificate(ip_address):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((ip_address, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=ip_address) as ssl_sock:
                cert = ssl_sock.getpeercert()
                print(Fore.BLUE + "\nSSL Certificate Information:" + Style.RESET_ALL)
                print_colored_info("Issuer", cert['issuer'])
                print_colored_info("Subject", cert['subject'])
                print_colored_info("Expiration Date", cert['notAfter'])
    except ssl.SSLError:
        print(Fore.RED + f"Unable to retrieve SSL certificate information for {ip_address}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Sorry, there was an issue connecting to {ip_address}: {str(e)}" + Style.RESET_ALL)

def get_dns_information(ip_address):
    try:
        domain = socket.gethostbyaddr(ip_address)[0]
        print_colored_info("DNS Information for", domain)

        a_records = socket.gethostbyname_ex(domain)
        print_colored_info("A Records", ', '.join(a_records[2]))

        mx_records = []
        try:
            mx_records = [str(record.exchange) for record in dns.resolver.resolve(domain, 'MX')]
        except Exception:
            pass
        print_colored_info("MX Records", ', '.join(mx_records))

        txt_records = []
        try:
            txt_records = [str(record) for record in dns.resolver.resolve(domain, 'TXT')]
        except Exception:
            pass
        print_colored_info("TXT Records", ', '.join(txt_records))

        ns_records = []
        try:
            ns_records = [str(record.target) for record in dns.resolver.resolve(domain, 'NS')]
        except Exception:
            pass
        print_colored_info("NS Records", ', '.join(ns_records))
    except Exception as e:
        print(Fore.RED + f"Sorry, there was an error while retrieving DNS information: {str(e)}" + Style.RESET_ALL)

if __name__ == "__main__":
    init(autoreset=True)
    disable_ansi_on_windows()
    print_banner()
    ip_address = input("Please enter an IP Address or Domain: ")
    geolocation_info = get_geolocation_info(ip_address)
    if geolocation_info:
        latitude, longitude = geolocation_info['loc'].split(',')
    get_ip_information(ip_address)
    get_dns_information(ip_address)
    ping_ip(ip_address)

    if geolocation_info:
        google_maps_url = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
        webbrowser.open(google_maps_url)

    print_contact_info()

    while True:
        choice = input("Type a number to open a contact link (1 for Website, 2 for GitHub, 3 for Instagram, or q to quit): ").strip()
        
        if choice == '1':
            webbrowser.open("https://wickdev.xyz/")
        elif choice == '2':
            webbrowser.open("https://github.com/Wickdev077")
        elif choice == '3':
            webbrowser.open("https://www.instagram.com/mik__subhi/")
        elif choice.lower() == 'q':
            break
        else:
            print(Fore.RED + "Invalid choice. Please select a valid option." + Style.RESET_ALL)
