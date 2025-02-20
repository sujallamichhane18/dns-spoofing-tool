import streamlit as st

def display_recommendations():
    """
    Function to display recommendations to prevent DNS spoofing.
    """
    try:
        st.subheader("Recommendations to Prevent DNS Spoofing")
        st.write("1. Enable DNSSEC to sign DNS records.")
        st.write("2. Use DNS resolvers that support DNSSEC validation.")
        st.write("3. Implement DNS query randomization.")
        st.write("4. Use firewalls to restrict DNS query sources.")
        st.write("5. Regularly monitor DNS traffic for unusual activity.")
    except Exception as e:
        st.error(f"Error displaying recommendations: {e}")

