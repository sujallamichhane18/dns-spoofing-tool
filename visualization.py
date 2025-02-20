import streamlit as st
from scapy.all import *
import logging

# Set up logging for visualization
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def capture_dns_traffic(interface='eth0'):
    """
    Function to capture DNS traffic using Scapy.
    
    Args:
    interface (str): The network interface to capture packets from (default is 'eth0').
    """
    try:
        packets = sniff(iface=interface, filter="udp port 53", count=10)
        return packets
    except Exception as e:
        logging.error(f"Error capturing DNS traffic: {e}")
        return []

def visualize_dns_spoof(packets):
    """
    Function to visualize DNS spoofed packets using Streamlit.
    
    Args:
    packets (list): A list of captured packets.
    """
    try:
        st.title("DNS Spoofing Visualization")
        
        if packets:
            st.write("Captured DNS Packets:")
            for packet in packets:
                if packet.haslayer(DNSRR):
                    st.write(f"Domain: {packet[DNSRR].rrname.decode()}")
                    st.write(f"Spoofed IP: {packet[DNSRR].rdata}")
                else:
                    st.write(f"Non-DNS Packet: {packet.summary()}")
        else:
            st.write("No DNS packets captured.")
    except Exception as e:
        logging.error(f"Error visualizing DNS packets: {e}")

