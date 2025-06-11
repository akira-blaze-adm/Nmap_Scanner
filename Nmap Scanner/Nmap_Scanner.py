import platform
import os
import shutil
import subprocess
import sys
import re
def is_valid_ip(ip):
    # Validate IPv4 address: 1.0.0.0 - 255.255.255.255 (no leading zeros)
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        if not 0 <= int(part) <= 255:
            return False
        if part != str(int(part)):  # Prevent leading zeros
            return False
    if int(parts[0]) < 1:
        return False
    return True
def find_and_copy_nmap():
    system = platform.system()
    nmap_executable = "nmap.exe" if system == "Windows" else "nmap"
    # Common alternative locations
    search_paths = [
        "C:\\Program Files (x86)\\Nmap\\",  # Windows default
        "C:\\Program Files\\Nmap\\",
        "/usr/local/bin/",
        "/usr/bin/",
        "/opt/local/bin/",
        "/opt/bin/",
        "/snap/bin/",
        "/bin/"
    ]
    # Check if nmap is in PATH first
    # Check if nmap is in PATH first
    if shutil.which("nmap"):
        return  # Already in PATH
    # Try to find nmap in common locations
    for path in search_paths:
        nmap_path = os.path.join(path, nmap_executable)
        if os.path.isfile(nmap_path):
            # Copy to current directory
            dest_path = os.path.join(os.getcwd(), nmap_executable)
            try:
                shutil.copy2(nmap_path, dest_path)
                print(f"Copied nmap from {nmap_path} to {dest_path}")
                # Optionally, add current directory to PATH for this session
                os.environ["PATH"] = os.getcwd() + os.pathsep + os.environ.get("PATH", "")
            except Exception as e:
                print(f"Failed to copy nmap: {e}")
            break

find_and_copy_nmap()

def check_nmap_installed():
    import shutil
    if shutil.which("nmap") is None:
        print("Nmap is not installed or not found in PATH.")
        choice = input("Do you want to attempt to install nmap? (y/n): ").strip().lower()
        if choice == 'y':
            try:
                import platform
                import subprocess
                system = platform.system()
                if system == "Windows":
                    print("Please install Nmap manually from https://nmap.org/download.html")
                    sys.exit(1)
                elif system == "Linux":
                    print("Attempting to install nmap using apt (requires sudo)...")
                    subprocess.run(["sudo", "apt", "update"], check=True)
                    subprocess.run(["sudo", "apt", "install", "-y", "nmap"], check=True)
                elif system == "Darwin":
                    print("Attempting to install nmap using brew...")
                    subprocess.run(["brew", "install", "nmap"], check=True)
                else:
                    print("Unsupported OS. Please install Nmap manually.")
                    sys.exit(1)
            except Exception as e:
                print(f"Automatic installation failed: {e}")
                print("Please install Nmap manually.")
                sys.exit(1)
        else:
            print("Nmap is required to run this script.")
            sys.exit(1)

check_nmap_installed()


def is_valid_ip(ip):
    # Simple regex for IPv4 validation
    pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    return re.match(pattern, ip) is not None

def is_valid_hostname(hostname):
    # Simple regex for hostname validation
    pattern = r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*\.?$"
    return re.match(pattern, hostname) is not None

def get_scan_type():
    scan_types = {
        "1": ("SYN Scan", "-sS"),
        "2": ("Service Version Detection", "-sV"),
        "3": ("OS Detection", "-O"),
        "4": ("Aggressive Scan", "-A"),
        "5": ("Ping Scan", "-sn")
    }
    print("Select scan type:")
    for key, (desc, flag) in scan_types.items():
        print(f"{key}. {desc} ({flag})")
    choice = input("Enter choice (1-5): ").strip()
    return scan_types.get(choice, (None, None))[1]

def main():
    print("=== Simple Nmap Scanner ===")
    target = input("Enter IP address or host name to scan: ").strip()
    if not (is_valid_ip(target) or is_valid_hostname(target)):
        print("Error: Invalid IP address or host name.")
        sys.exit(1)

    scan_type = get_scan_type()
    if not scan_type:
        print("Error: Invalid scan type selected.")
        sys.exit(1)

    print(f"[*] Starting nmap scan on {target} with scan type {scan_type}...")
    nmap_cmd = ["nmap", scan_type, target]

    try:
        proc = subprocess.run(nmap_cmd, capture_output=True, text=True, check=True)
        output = proc.stdout
        print("[*] Scan completed. Results:\n")
        print(output)
    except FileNotFoundError:
        print("Error: nmap is not installed or not found in PATH.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("Error: Nmap scan failed.")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

     save = input("Do you want to save the output to a file? (y/n): ").strip().lower()
        if save == 'y':
            format_choice = input("Choose file format - txt or json: ").strip().lower()
            filename = input("Enter filename (without extension): ").strip()
            if format_choice == "json":
                json_filename = filename + ".json"
                try:
                    result = {
                        "target": target,
                        "scan_type": scan_type,
                        "output": output
                    }
                    with open(json_filename, "w", encoding="utf-8") as f:
                        json.dump(result, f, indent=2)
                    print(f"[*] Output saved to {json_filename}")
                except Exception as e:
                    print(f"Error saving file: {e}")
            else:
                txt_filename = filename + ".txt"
                try:
                    with open(txt_filename, "w", encoding="utf-8") as f:
                        f.write(output)
                    print(f"[*] Output saved to {txt_filename}")
                except Exception as e:
                    print(f"Error saving file: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user. Exiting.")
        sys.exit(0)
