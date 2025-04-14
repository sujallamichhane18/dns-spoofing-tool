```markdown
🔐 DNS Spoofing Tool (Educational & Ethical Use Only)

A Python-based ARP and DNS spoofing tool designed **strictly for educational and authorized penetration testing. This tool demonstrates how DNS spoofing works in local network environments and can be used to study the importance of network-layer security.

> ⚠️ Important: This script must only be used on systems and networks you have explicit permission to test.



📘 Overview

This script provides a hands-on demonstration of ARP poisoning and DNS spoofing in a **controlled lab environment**. It is intended as a learning resource to better understand network vulnerabilities and secure local networks.



✨ Features

- ✅ ARP spoofing with rate-limiting and MAC address caching  
- ✅ Asynchronous DNS sniffing and spoofing with domain filtering  
- ✅ Real-time statistics: ARP sent, DNS spoofed, HTTP RSTs  
- ✅ Optional HTTP spoofing via TCP RST injection  
- ✅ Persistent spoof domain management via `spoof_domains.json`  
- ✅ Ethical use consent prompt with disclaimer  
- ✅ Cross-platform compatible (Linux recommended)



## 📦 Installation

Install dependencies:

bash
pip install scapy pyfiglet termcolor
```

Enable IP forwarding (Linux):

```bash
sudo sysctl -w net.ipv4.ip_forward=1
```

---

## 🚀 Usage

Run the script:

```bash
sudo python3 dns_spoof.py
```

You will be prompted for:

- Network interface (e.g., `eth0`)  
- Victim IP address  
- Gateway/DNS server IP  
- Fake IP to redirect spoofed domains  
- Comma-separated list of domains (or load from saved list)

### 📝 Example Input

```
Interface: eth0  
Victim IP: 192.168.1.10  
Gateway IP: 192.168.1.1  
Fake IP: 192.168.1.99  
Domains: example.com, testsite.local
```

---

## 📁 Project Structure

```
dns_spoof/
├── dns_spoof.py              # Main script
├── spoof_domains.json        # Saved domains list
├── dns_spoof.log             # Log output
└── README.md                 # Project documentation
```

---

## ⚠️ Disclaimer & Legal

```
========================================
This tool is for ethical and educational use only.

❌ Do NOT use on unauthorized systems or networks.
✅ Use only in lab environments or with explicit permission.

The author is not responsible for any misuse.
Violating laws or policies is strictly prohibited.
========================================
```

By using this tool, you confirm that you understand and accept the terms above.

---

## 📚 Learning Resources

- [Scapy Documentation](https://scapy.readthedocs.io/)
- [MIT License Guide](https://opensource.org/licenses/MIT)
- [ARP Spoofing - OWASP](https://owasp.org/)
- [Offensive Security - Kali Linux](https://www.offensive-security.com/)
- [Cloudflare DNS Security](https://www.cloudflare.com/learning/dns/dns-security/)

---

## 👨‍💻 Author

**Sujal Lamichhane**  
Cybersecurity Enthusiast | Penetration Testing | Digital Forensics  
GitHub: [sujallamichhane18](https://github.com/sujallamichhane18)  
Website: [sujallamichhane.com.np](https://sujallamichhane.com.np)

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).
```

Let me know if you want it personalized further, or want to add screenshots, badges, or demo GIFs for a more polished GitHub repo.
