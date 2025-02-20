

```markdown
# DNS Spoof Tool

This tool is designed to demonstrate ARP and DNS spoofing, commonly used in Man-in-the-Middle (MITM) attacks. The tool can be used for educational and ethical hacking purposes only, and it should only be run in a controlled, legal, and authorized environment (e.g., penetration testing lab).

## Disclaimer

By using this tool, you agree that:
- This tool is for educational and ethical purposes only.
- You must have explicit permission from the network owner before running this tool.
- The author is not responsible for any malicious or illegal activity performed using this tool.

Any unauthorized use of this tool is illegal and the sole responsibility of the user.

## Features

- **ARP Spoofing**: The tool continuously sends ARP poison packets to the victim and gateway, positioning the attacker in a Man-in-the-Middle (MITM) position.
- **DNS Spoofing**: The tool forges DNS responses for a specified domain, redirecting the victim to a fake IP address.
- **Graceful Exit**: The tool restores ARP tables and exits cleanly when interrupted (e.g., via `Ctrl+C`).
- **User Input**: Prompts the user to input the victim's IP, the gateway's IP, the domain to spoof, and the fake IP address.
- **Logging**: Detailed logs track ARP poisoning and DNS spoofing actions.
- **Colored Output**: Displays colorful, informative output using `termcolor`.
- **Banner**: The script includes a large banner with a disclaimer and your name using `pyfiglet`.

## Requirements

- Python 3.x
- Scapy: For crafting and sending ARP and DNS packets
- pyfiglet: For generating the banner text
- termcolor: For coloring the output text

You can install the required dependencies by running:

```bash
pip install scapy pyfiglet termcolor
```

## Creating a Virtual Environment

To create a clean, isolated environment for running this tool, follow these steps:

1. **Create a virtual environment:**

```bash
python3 -m venv dns_spoof_env
```

2. **Activate the virtual environment:**

   - On Linux/macOS:

   ```bash
   source dns_spoof_env/bin/activate
   ```

   - On Windows:

   ```bash
   .\dns_spoof_env\Scripts\activate
   ```

3. **Install the required dependencies:**

```bash
pip install scapy pyfiglet termcolor
```

4. **Verify the installation:**

```bash
pip list
```

This will show you a list of installed packages, ensuring that the dependencies are properly installed within the virtual environment.

## Usage

1. Clone the repository or download the script.
2. Run the script in a terminal with root/administrator privileges (required for packet sending).

```bash
sudo python3 main.py
```

3. The script will display a colorful banner and prompt you for the following inputs:
   - **Victim's IP Address**: The IP address of the target machine.
   - **Gateway/DNS Server's IP Address**: The IP address of the gateway or DNS server.
   - **Domain to Spoof**: The domain name (e.g., `www.example.com`) to be redirected.
   - **Fake IP Address**: The IP address to which the domain will be redirected (e.g., `192.168.1.100`).

4. After entering the required information, the tool will start ARP poisoning and DNS spoofing.
5. The attack will run until you interrupt it using `Ctrl+C`.
6. When you stop the attack, the ARP tables will be restored to their original state.

## Example

```bash
Enter Victim's IP Address: 192.168.1.10
Enter Gateway/DNS Server's IP Address: 192.168.1.1
Enter Domain to Spoof (e.g., www.example.com): www.example.com
Enter Fake IP Address to Redirect to (e.g., 192.168.1.100): 192.168.1.100
```

The script will then start ARP and DNS spoofing, showing logs of the actions being taken.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Warning

This tool is intended for use on authorized networks and systems only. Unauthorized use is illegal and punishable by law. Always obtain explicit permission before testing any network or system.

## Contact

If you have any questions or feedback, feel free to contact me:

- Name: Sujal Lamichhane
- Website: [www.sujallamichhane.com.np](https://www.sujallamichhane.com.np)
```
