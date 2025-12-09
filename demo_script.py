import requests
import time
import sys

# --- CẤU HÌNH ---
# Địa chỉ server (Chạy localhost trên máy ảo)
URL = "http://127.0.0.1:3000/login-vulnerable"

# Màu sắc cho đẹp
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def run_demo():
    print(Colors.BOLD + "\n=== KỊCH BẢN DEMO: NGƯỜI DÙNG vs HACKER ===" + Colors.ENDC)
    print("-" * 50)
    time.sleep(1)

    # --- PHẦN 1: NGƯỜI DÙNG HỢP LỆ ---
    print(f"[{Colors.YELLOW}BƯỚC 1{Colors.ENDC}] Giả lập người dùng nhập ĐÚNG mật khẩu...")
    try:
        # Gửi user/pass đúng (admin/123456)
        payload = {'username': 'admin', 'password': '123456'}
        response = requests.post(URL, json=payload, timeout=2)
        
        # Nếu server trả về chuyển hướng (302) hoặc OK (200) thì là thành công
        # Code server trả về 302 khi thành công
        if response.history or response.status_code == 200:
             print(f"   => {Colors.GREEN}✅ ĐĂNG NHẬP THÀNH CÔNG! (Server chào mừng){Colors.ENDC}")
        else:
             # Dự phòng nếu server trả code khác
             print(f"   => {Colors.GREEN}✅ ĐĂNG NHẬP THÀNH CÔNG! (Status: {response.status_code}){Colors.ENDC}")

    except Exception as e:
        print(f"   => ❌ Lỗi kết nối: {e}")

    print("-" * 50)
    time.sleep(2) # Nghỉ 2 giây để khán giả nhìn

    # --- PHẦN 2: HACKER TẤN CÔNG ---
    print(f"[{Colors.YELLOW}BƯỚC 2{Colors.ENDC}] Giả lập Hacker dò mật khẩu (Brute-force)...")
    
    wrong_passwords = ["1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999"]
    
    for i, pwd in enumerate(wrong_passwords):
        try:
            print(f"   Using password: {pwd:<10}", end="")
            
            # Gửi user đúng, pass SAI
            payload = {'username': 'admin', 'password': pwd}
            response = requests.post(URL, json=payload, timeout=2)
            
            # Server trả về 302 chuyển hướng đến trang báo lỗi -> Nghĩa là chưa bị chặn
            print(f" => {Colors.RED}❌ Sai mật khẩu (Server ghi log){Colors.ENDC}")
            
            # Nghỉ 1 chút để Fail2Ban kịp đọc log (Quan trọng)
            time.sleep(0.8) 

        except requests.exceptions.ConnectionError:
            # KHI FAIL2BAN CHẶN -> SẼ RƠI VÀO ĐÂY
            print(f"\n\n{Colors.RED}{Colors.BOLD}>>> [KẾT QUẢ] ⛔ KẾT NỐI BỊ TỪ CHỐI (CONNECTION REFUSED)!{Colors.ENDC}")
            print(f"{Colors.RED}>>> Fail2Ban đã phát hiện và chặn IP này thành công.{Colors.ENDC}")
            print(f"{Colors.GREEN}>>> KỊCH BẢN KẾT THÚC.{Colors.ENDC}")
            return
    
    print("\n⚠️ Cảnh báo: Chạy hết danh sách mà chưa bị chặn? Hãy thử lại lần nữa.")

if __name__ == "__main__":
    run_demo()
