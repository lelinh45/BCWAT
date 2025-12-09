import requests
import time
import sys

# CẤU HÌNH IP SERVER
# Dựa trên ảnh của bạn, IP là: 192.168.238.151
TARGET_IP = "192.168.238.151" 
PORT = 3000

print("=============================================")
print("   TOOL TEST BẢO MẬT (BRUTE-FORCE DEMO)      ")
print("=============================================")
print("Chọn mục tiêu tấn công:")
print("1. Tấn công '/login-vulnerable' (Test Fail2Ban chặn IP)")
print("2. Tấn công '/login-secure'     (Test Middleware chặn 429)")
print("---------------------------------------------")
choice = input("Nhập số (1 hoặc 2): ")

if choice == '1':
    url = f"http://{TARGET_IP}:{PORT}/login-vulnerable"
    print(f"\n[MODE 1] Đang tấn công vào: {url}")
    print("=> Kỳ vọng: Sau vài lần sai, Fail2Ban sẽ chặn kết nối (Connection Refused).")
elif choice == '2':
    url = f"http://{TARGET_IP}:{PORT}/login-secure"
    print(f"\n[MODE 2] Đang tấn công vào: {url}")
    print("=> Kỳ vọng: Sau 5 lần, Server trả về lỗi 429 (Too Many Requests).")
else:
    print("Lựa chọn không hợp lệ!")
    sys.exit()

# Danh sách mật khẩu để thử
passwords = ["123456", "password", "admin", "qwerty", "wrongpass", "test", "abc"]

print(f"\n--- BẮT ĐẦU TẤN CÔNG BRUTE-FORCE ---")

for i, pwd in enumerate(passwords):
    try:
        print(f"[Lần thử {i+1}] Đang thử pass: {pwd} ...")
        
        # Timeout 2s để phát hiện Fail2Ban chặn nhanh hơn
        response = requests.post(url, json={"username": "admin", "password": pwd}, timeout=2)
        
        if response.status_code == 200:
            print(">>> ✅ THÀNH CÔNG! Đã tìm thấy mật khẩu.")
            break
        elif response.status_code == 401:
            print("--> ❌ Sai mật khẩu (Server trả về 401).")
        elif response.status_code == 429:
            print("--> 🚫 BỊ CHẶN BỞI MIDDLEWARE (Code Node.js trả về 429).")
            print(">>> KẾT QUẢ: Middleware hoạt động tốt!")
            break
        else:
            print(f"--> Mã phản hồi khác: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n>>> 💀 MẤT KẾT NỐI (CONNECTION REFUSED)!")
        print(">>> CHÚC MỪNG: Fail2Ban đã chặn IP của bạn ở tầng mạng (IPTables).")
        print(">>> KẾT QUẢ: Hệ thống phòng thủ Fail2Ban hoạt động tốt!")
        break
    except Exception as e:
        print(f"Lỗi khác: {e}")

    # Nghỉ xíu để server kịp ghi log
    time.sleep(0.5)
