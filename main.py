import streamlit as st
from spoofing import dns_spoof
from visualization import capture_dns_traffic, visualize_dns_spoof
from recommendations import display_recommendations

def main():
    """
    Main entry point for the DNS spoofing simulation tool.
    """
    st.title("DNS Spoofing Simulation Tool")

    # Input for the simulation
    target_ip = st.text_input("Target DNS Resolver IP", "192.168.1.1")
    spoofed_ip = st.text_input("Malicious IP to Spoof", "123.45.67.89")
    target_domain = st.text_input("Target Domain to Spoof", "example.com")
    
    if st.button("Simulate DNS Spoofing"):
        try:
            # Call the DNS spoofing function
            dns_spoof(target_ip, 53, spoofed_ip, bytes(target_domain, 'utf-8'))
            st.success(f"Spoofed DNS response sent to {target_ip} for domain {target_domain}")
        except Exception as e:
            st.error(f"Error during DNS spoofing: {e}")
    
    # Capture and visualize DNS traffic
    if st.button("Capture and Visualize DNS Traffic"):
        packets = capture_dns_traffic()
        visualize_dns_spoof(packets)
    
    # Display prevention recommendations
    display_recommendations()

if __name__ == "__main__":
    main()

