import requests
import time

# Tấn công vào trang có Middleware
URL = "http://127.0.0.1:3000/login-secure"

print("=== BẮT ĐẦU SPAM CỰC MẠNH VÀO MIDDLEWARE ===")
print("Mục tiêu: Bắt ép Fail2Ban phải ra tay chặn.")

while True:
    try:
        # Gửi request liên tục, không ngừng nghỉ
        response = requests.post(URL, data={'username':'admin', 'password':'123'}, timeout=1)
        
        if response.status_code == 429:
            # Vẫn in ra để bạn thấy Middleware đang làm việc
            print(f"\033[93m[!] Bị Middleware chặn (429) - Server đang ghi log [ABUSE]...\033[0m")
        elif response.status_code == 200:
            print(f"\033[92m[+] Request OK\033[0m")
        
        # Chạy nhanh (0.2s / lần) để log tăng nhanh
        time.sleep(0.2)

    except requests.exceptions.ConnectionError:
        # KHI FAIL2BAN CHẶN -> SẼ RƠI VÀO ĐÂY
        print(f"\n\n\033[91m[CRITICAL] ⛔ BÙM! ĐÃ BỊ FAIL2BAN CHẶN CỨNG! (Connection Refused)\033[0m")
        print(">>> Kịch bản thành công: Middleware không chịu nổi -> Fail2Ban đã cứu nguy.")
        break # Dừng chương trình
    except Exception as e:
        print(f"Lỗi: {e}")
        break
