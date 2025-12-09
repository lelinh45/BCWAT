const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

// --- CẤU HÌNH VỊ TRÍ FILE LOG VÀ TÀI KHOẢN ---
const LOG_FILE = path.join(__dirname, 'auth.log');
const VALID_USER = "admin";
const VALID_PASS = "123456";

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// --- 1. GIAO DIỆN (FRONTEND) ---
app.get('/', (req, res) => {
    let clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    if (clientIp.includes('::ffff:')) clientIp = clientIp.replace('::ffff:', '');

    const currentScenario = req.query.scenario || '1';
    const formAction = currentScenario === '2' ? '/login-secure' : '/login-vulnerable';
    const sel1 = currentScenario === '1' ? 'selected' : '';
    const sel2 = currentScenario === '2' ? 'selected' : '';

    res.send(`
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Demo Bảo Mật Web</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }
            body { background-color: #2c3e50; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .login-card { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 400px; text-align: center; }
            h2 { color: #e74c3c; margin-bottom: 5px; text-transform: uppercase; }
            .form-group { margin-bottom: 20px; text-align: left; }
            label { display: block; font-weight: bold; margin-bottom: 8px; color: #333; }
            input, select { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; outline: none; }
            input:focus { border-color: #3498db; }
            button { width: 100%; padding: 12px; background-color: #3498db; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
            button:hover { background-color: #2980b9; }
            .alert-box { margin-top: 20px; padding: 15px; border-radius: 6px; display: none; font-size: 14px;}
            .error { background-color: #fce4e4; border: 1px solid #fcc2c3; color: #cc0000; }
            .success { background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .ip-info { margin-top: 20px; color: #aaa; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>DEMO BẢO MẬT WEB</h2>
            <form id="loginForm" method="POST" action="${formAction}">
                <div class="form-group">
                    <label>Tên đăng nhập</label>
                    <input type="text" name="username" value="admin" required>
                </div>
                <div class="form-group">
                    <label>Mật khẩu</label>
                    <input type="password" name="password" placeholder="Nhập mật khẩu..." required>
                </div>
                <div class="form-group">
                    <label>Chọn kịch bản test:</label>
                    <select id="scenario" name="scenario" onchange="changeAction()">
                        <option value="1" ${sel1}>1. Server thường (Test Fail2Ban)</option>
                        <option value="2" ${sel2}>2. Server an toàn (Test Middleware)</option>
                    </select>
                </div>
                <button type="submit">Đăng Nhập</button>
            </form>

            <div id="blockedMsg" class="alert-box error">
                <strong>⛔ BỊ CHẶN!</strong><br>QUÁ NHIỀU LẦN SAI! Vui lòng chờ.
            </div>
            
            <div id="wrongMsg" class="alert-box error">
                <strong>❌ SAI MẬT KHẨU!</strong><br>Vui lòng thử lại.
            </div>

            <div id="successMsg" class="alert-box success">
                <strong>✅ THÀNH CÔNG!</strong><br>Chào mừng sếp đã quay trở lại.
            </div>

            <div class="ip-info">IP của bạn: ${clientIp}</div>
        </div>

        <script>
            function changeAction() {
                const select = document.getElementById('scenario');
                const form = document.getElementById('loginForm');
                if (select.value === '1') form.action = '/login-vulnerable';
                else form.action = '/login-secure';
            }

            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('blocked')) document.getElementById('blockedMsg').style.display = 'block';
            if (urlParams.has('error')) document.getElementById('wrongMsg').style.display = 'block';
            if (urlParams.has('success')) document.getElementById('successMsg').style.display = 'block';
        </script>
    </body>
    </html>
    `);
});

// --- 2. XỬ LÝ BACKEND ---

// Kịch bản 1: Fail2Ban (Vulnerable)
app.post('/login-vulnerable', (req, res) => {
    let ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    if (ip.includes('::ffff:')) ip = ip.replace('::ffff:', '');
    if (ip === '::1') ip = '127.0.0.1';

    const { username, password } = req.body;

    if (username === VALID_USER && password === VALID_PASS) {
        return res.redirect('/?scenario=1&success=true');
    }

    // Ghi log vào console để Fail2Ban bắt
    const time = new Date().toLocaleString("sv-SE", { timeZone: "Asia/Ho_Chi_Minh" });
    console.log(`${time} [FAILED_LOGIN] IP: ${ip} User: ${username}`); 

    res.redirect('/?scenario=1&error=1'); 
});


// Kịch bản 2: Middleware + Fail2Ban (Secure/Abuse Test)

// Kịch bản 2: Middleware + Fail2Ban
let requestCounts = {};
app.post('/login-secure', (req, res) => {
    let ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    if (ip.includes('::ffff:')) ip = ip.replace('::ffff:', '');
    if (ip === '::1') ip = '127.0.0.1';

    if (!requestCounts[ip]) requestCounts[ip] = 0;
    requestCounts[ip]++; // Tăng số lần thử lên 1 (Tính cả lần này)

    // --- B1: KIỂM TRA ĐÃ VƯỢT QUÁ NGƯỠNG CHẶN CHƯA (Lần thứ 6+) ---
    if (requestCounts[ip] > 5) {
        
        // GHI LOG [ABUSE] MÁCH FAIL2BAN
        const time = new Date().toLocaleString("sv-SE", { timeZone: "Asia/Ho_Chi_Minh" });
        const logLine = `${time} [ABUSE] IP: ${ip} Rate Limit Exceeded\n`;
        
        try {
            fs.appendFileSync(LOG_FILE, logLine);
            console.log(`>>> [LOG 429] IP ${ip} đang spam! Đã mách Fail2Ban.`);
        } catch (e) { console.error(e); }

        // Trả về lỗi 429: BẠN ĐÃ BỊ CHẶN
        return res.status(429).send("BẠN ĐÃ BỊ CHẶN (429)!");
    }
    
    // --- B2: KIỂM TRA ĐĂNG NHẬP THÀNH CÔNG (Nếu chưa bị chặn) ---
    if (req.body.username === VALID_USER && req.body.password === VALID_PASS) {
        requestCounts[ip] = 0; // Reset counter
        return res.redirect('/?scenario=2&success=true');
    }

    // --- B3: ĐĂNG NHẬP THẤT BẠI (Chưa bị chặn) ---
    // Counter đã tăng ở trên. Chỉ cần trả về lỗi.
    res.redirect('/?scenario=2&error=1'); 
});
// --- 3. LẮNG NGHE CỔNG (ĐOẠN CỐT LÕI ĐÃ BỊ MẤT) ---
app.listen(PORT, () => {
    // Đảm bảo file log tồn tại khi server khởi động
    if (!fs.existsSync(LOG_FILE)) {
        fs.writeFileSync(LOG_FILE, '');
    }
    console.log(`✅ Server (FINAL) đang chạy tại http://localhost:${PORT}`);
});
