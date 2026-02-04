# Hướng Dẫn Kết Nối ESP32 với Python Simulation

## 📋 Tổng Quan

Hệ thống HIL Robocar cần 2 thành phần chạy đồng thời:
1. **ESP32** (chạy trên Wokwi) - Bộ điều khiển
2. **Python Simulation** - Mô phỏng vật lý và cảm biến

Chúng giao tiếp với nhau qua **Serial Port** (COM port ảo).

---

## 🔷 PHẦN 1: Thiết Lập ESP32 trên Wokwi

### Bước 1.1: Truy cập Wokwi
1. Mở trình duyệt web (Chrome/Edge khuyên dùng)
2. Truy cập: https://wokwi.com
3. Đăng nhập hoặc dùng chế độ Guest

### Bước 1.2: Tạo Project ESP32 Mới
1. Click nút **"New Project"** (góc trên bên trái)
2. Chọn **"ESP32"** từ danh sách board
3. Chọn template **"Arduino ESP32"**
4. Project mới sẽ được tạo với file `sketch.ino` mặc định

### Bước 1.3: Copy Code ESP32
1. Mở file `esp32_wokwi\sketch.ino` trong project của bạn
2. **Copy TOÀN BỘ nội dung** (Ctrl+A, Ctrl+C)
3. Quay lại Wokwi, **xóa hết code mặc định**
4. **Paste** code đã copy vào (Ctrl+V)

**File cần copy:** `D:\Hệ nhúng\hil-robotcar\esp32_wokwi\sketch.ino`

### Bước 1.4: Thêm Thư Viện ArduinoJson

**Quan trọng:** ESP32 cần thư viện ArduinoJson để xử lý JSON!

1. Click vào tab **"Library Manager"** (biểu tượng sách, bên trái)
2. Tìm kiếm: **"ArduinoJson"**
3. Chọn thư viện **"ArduinoJson"** by Benoit Blanchon
4. Click **"Add to project"**
5. Chọn version **6.21.3** hoặc mới hơn
6. Click **"Add"**

### Bước 1.5: Cấu Hình Circuit (Tùy chọn)

Nếu muốn có circuit diagram:
1. Click tab **"diagram.json"**
2. Mở file `esp32_wokwi\diagram.json` trong project
3. Copy toàn bộ nội dung
4. Paste vào Wokwi

**Lưu ý:** Circuit diagram chỉ để hiển thị, không ảnh hưởng hoạt động.

### Bước 1.6: Compile và Chạy

1. Click nút **"Start Simulation"** (nút play màu xanh lá)
2. Đợi code compile (5-10 giây)
3. Nếu có lỗi compile:
   - Kiểm tra đã thêm ArduinoJson chưa
   - Kiểm tra code đã copy đầy đủ chưa

**Kết quả mong đợi:**
- Simulation chạy (LED nhấp nháy nếu có)
- Không có lỗi compile

---

## 🔷 PHẦN 2: Lấy COM Port từ Wokwi

### Bước 2.1: Mở Serial Monitor

1. Trong Wokwi, click biểu tượng **"Serial Monitor"** (màn hình console)
2. Hoặc nhấn phím tắt: **Ctrl+Shift+S**
3. Cửa sổ Serial Monitor sẽ hiện ra bên dưới

**Bạn sẽ thấy:**
```
# ESP32 HIL Controller Ready
```

### Bước 2.2: Xác Định COM Port

**Cách 1: Wokwi hiển thị COM port**
- Wokwi sẽ tự động tạo một virtual COM port
- Port thường là: **COM3**, **COM4**, hoặc **COM5**
- Wokwi có thể hiển thị port number trong Serial Monitor

**Cách 2: Dùng Python để list ports**
```powershell
python -c "import serial.tools.list_ports; [print(f'{p.device}: {p.description}') for p in serial.tools.list_ports.comports()]"
```

Kết quả mẫu:
```
COM4: USB-SERIAL CH340
COM5: USB Serial Port
```

**Cách 3: Để Python tự động detect**
- Python simulation có chức năng **auto-detect**
- Sẽ tự tìm ESP32 port khi chạy

### Bước 2.3: Giữ Wokwi Chạy

**⚠️ QUAN TRỌNG:**
- **KHÔNG TẮT** Wokwi simulation
- **KHÔNG ĐÓNG** Serial Monitor
- **ĐỂ CHẠ** trong khi chạy Python

---

## 🔷 PHẦN 3: Kết Nối Python với ESP32

### Bước 3.1: Mở Terminal

Mở PowerShell trong thư mục project:
```powershell
cd "D:\Hệ nhúng\hil-robotcar\python_sim"
```

### Bước 3.2: Chạy Python Simulation

**Cách 1 - Auto-detect (Khuyên dùng):**
```powershell
python -m robocar_sim.main
```

Python sẽ tự động tìm ESP32 port.

**Cách 2 - Chỉ định port cụ thể:**
```powershell
python -m robocar_sim.main COM4
```
Thay `COM4` bằng port thực tế của bạn.

**Cách 3 - Dùng batch file:**
```powershell
.\run_sim.bat
```

### Bước 3.3: Xác Nhận Kết Nối Thành Công

**Python Console sẽ hiển thị:**
```
════════════════════════════════════════════════════════
  HIL ROBOCAR SIMULATION - Hardware-in-the-Loop
════════════════════════════════════════════════════════

[1/3] Initializing simulation world...
  ✓ Physics engine ready
  ✓ Sensors configured (Front, Left, Right)
  ✓ 7 obstacles loaded

[2/3] Initializing pygame renderer...
  ✓ Renderer ready (800x800 @ 60 FPS)

[3/3] Connecting to ESP32...
✓ Auto-detected ESP32 on COM4: USB-SERIAL CH340
✓ Connected to ESP32 on COM4 @ 115200 baud

════════════════════════════════════════════════════════
  ✓ INITIALIZATION COMPLETE - Press ESC to quit
════════════════════════════════════════════════════════
```

**Wokwi Serial Monitor sẽ hiển thị:**
```
# ESP32 HIL Controller Ready
# Python Simulator Connected
{"vL": 0.60, "vR": 0.60}
{"vL": 0.60, "vR": 0.40}
{"vL": 0.70, "vR": 0.70}
...
```

**Pygame Window:**
- Cửa sổ 800x800 hiện ra
- Xe robot màu xanh di chuyển
- HUD góc trên trái hiển thị: **"ESP32: CONNECTED"**

---

## 🔷 PHẦN 4: Kiểm Tra Giao Tiếp Serial

### Dữ Liệu Python → ESP32 (Sensor Data)

Python gửi dữ liệu cảm biến:
```json
{"dF": 1.25, "dL": 0.85, "dR": 2.10}
```

- `dF` = khoảng cách cảm biến phía trước (Front)
- `dL` = khoảng cách cảm biến bên trái (Left)
- `dR` = khoảng cách cảm biến bên phải (Right)

### Dữ Liệu ESP32 → Python (Motor Commands)

ESP32 gửi lệnh động cơ:
```json
{"vL": 0.65, "vR": 0.70}
```

- `vL` = tốc độ bánh trái (Left wheel)
- `vR` = tốc độ bánh phải (Right wheel)
- Giá trị: -1.0 (lùi) đến 1.0 (tiến)

### Kiểm Tra Serial Data trong Wokwi

Trong Wokwi Serial Monitor, bạn có thể **test thủ công**:

1. Gõ vào Serial Monitor:
```json
{"dF": 0.50, "dL": 1.00, "dR": 1.00}
```

2. Nhấn Enter

3. ESP32 sẽ xử lý và trả về lệnh động cơ

---

## ❌ XỬ LÝ LỖI

### Lỗi 1: "Could not auto-detect ESP32 port"

**Nguyên nhân:**
- Wokwi chưa chạy
- Serial Monitor chưa mở
- Python không thấy COM port

**Giải pháp:**
```powershell
# Liệt kê các COM port có sẵn
python -c "import serial.tools.list_ports; [print(p.device, '-', p.description) for p in serial.tools.list_ports.comports()]"

# Chỉ định port cụ thể
python -m robocar_sim.main COM4
```

### Lỗi 2: "PermissionError: Access denied to COM4"

**Nguyên nhân:**
- Port đang được chương trình khác sử dụng
- Arduino IDE Serial Monitor đang mở
- Python simulation trước đó chưa đóng đúng

**Giải pháp:**
1. Đóng tất cả chương trình dùng COM port
2. Đóng Arduino IDE Serial Monitor
3. Restart Wokwi simulation
4. Thử lại

### Lỗi 3: Python kết nối nhưng xe không di chuyển

**Kiểm tra:**

1. **Xem HUD trong pygame:**
   - Phải hiển thị "ESP32: CONNECTED" màu xanh lá
   - Nếu "DISCONNECTED" màu đỏ → kết nối bị mất

2. **Xem Wokwi Serial Monitor:**
   - Phải có dòng `{"vL": ..., "vR": ...}` liên tục
   - Nếu không có → ESP32 không gửi lệnh

3. **Xem Python console:**
   - Kiểm tra có lỗi gì in ra không

### Lỗi 4: Kết nối rồi bị ngắt ngay

**Nguyên nhân:**
- Wokwi simulation bị dừng
- Tab Wokwi bị đóng
- Mất kết nối mạng (Wokwi online)

**Giải pháp:**
- Giữ tab Wokwi mở và active
- Giữ simulation chạy liên tục
- Kết nối internet ổn định

### Lỗi 5: "ArduinoJson.h: No such file"

**Nguyên nhân:**
- Chưa thêm thư viện ArduinoJson

**Giải pháp:**
1. Vào Library Manager trong Wokwi
2. Tìm "ArduinoJson"
3. Click "Add to project"
4. Chọn version 6.21.3+
5. Compile lại

---

## ✅ CHECKLIST KẾT NỐI

Dùng checklist này để đảm bảo mọi thứ đã sẵn sàng:

### Wokwi (ESP32)
- [ ] Project ESP32 đã tạo
- [ ] Code `sketch.ino` đã copy đầy đủ
- [ ] Thư viện ArduinoJson đã thêm
- [ ] Code compile không lỗi
- [ ] Simulation đang chạy (nút play màu xanh)
- [ ] Serial Monitor đã mở
- [ ] Thấy dòng "# ESP32 HIL Controller Ready"

### Python (Simulation)
- [ ] Python 3.10+ đã cài
- [ ] Dependencies đã cài (`pip install -r requirements.txt`)
- [ ] File test_system.py chạy thành công
- [ ] COM port đã xác định hoặc để auto-detect

### Kết Nối
- [ ] Wokwi chạy TRƯỚC khi chạy Python
- [ ] Python kết nối thành công
- [ ] Pygame window hiện ra
- [ ] HUD hiển thị "ESP32: CONNECTED"
- [ ] Xe di chuyển trong simulation
- [ ] Wokwi Serial Monitor hiển thị lệnh động cơ

---

## 🎯 DEMO NHANH (Quick Test)

### Test 1: Wokwi hoạt động

Trong Wokwi Serial Monitor, gõ:
```json
{"dF": 0.30, "dL": 1.00, "dR": 1.00}
```

ESP32 phải trả về lệnh quay vì phát hiện chướng ngại vật gần.

### Test 2: Python kết nối

```powershell
cd "D:\Hệ nhúng\hil-robotcar\python_sim"
python -m robocar_sim.main
```

Phải thấy:
- Console: "✓ Connected to ESP32..."
- Pygame: Cửa sổ hiện ra
- Wokwi: Dòng "# Python Simulator Connected"

### Test 3: Giao tiếp 2 chiều

Quan sát:
- **Python console:** Sensor data được gửi
- **Wokwi Serial Monitor:** Motor commands được gửi
- **Pygame:** Xe di chuyển tránh chướng ngại vật

---

## 📊 SƠ ĐỒ KẾT NỐI

```
┌─────────────────┐                           ┌─────────────────┐
│   Wokwi ESP32   │                           │  Python Pygame  │
│   (Trình duyệt) │                           │   (Local PC)    │
└────────┬────────┘                           └────────┬────────┘
         │                                              │
         │  Virtual COM Port (COM4)                     │
         │  Baud: 115200                                │
         │  Format: JSON + '\n'                         │
         │                                              │
         │ ◄────────────────────────────────────────────┤
         │   {"dF": 1.25, "dL": 0.85, "dR": 2.10}      │
         │           (Sensor Data)                      │
         │                                              │
         │ ─────────────────────────────────────────────►
         │       {"vL": 0.65, "vR": 0.70}              │
         │         (Motor Commands)                     │
         │                                              │
         ▼                                              ▼
┌─────────────────┐                           ┌─────────────────┐
│   Controller    │                           │   Simulation    │
│    Logic        │                           │     Engine      │
│ • Obstacle      │                           │ • Physics       │
│   Avoidance     │                           │ • Sensors       │
│ • Motor Cmd     │                           │ • Rendering     │
└─────────────────┘                           └─────────────────┘
```

---

## 💡 MẸO VÀ LƯU Ý

### Mẹo 1: Chạy Wokwi trước
Luôn start Wokwi simulation TRƯỚC, sau đó mới chạy Python.

### Mẹo 2: Giữ Serial Monitor mở
Serial Monitor phải mở trong suốt quá trình demo.

### Mẹo 3: Kiểm tra qua HUD
HUD trong pygame là cách nhanh nhất biết kết nối OK không.

### Mẹo 4: Xem output của cả 2
- Wokwi Serial Monitor: Xem motor commands
- Python Console: Xem sensor data và trạng thái kết nối

### Mẹo 5: Test thủ công trước
Trước khi chạy full system, test ESP32 bằng cách gõ JSON thủ công.

---

## 🆘 HỖ TRỢ

Nếu vẫn gặp vấn đề:

1. **Chạy system test:**
   ```powershell
   python test_system.py
   ```

2. **Đọc tài liệu chi tiết:**
   - [HOW_TO_RUN_WINDOWS.md](HOW_TO_RUN_WINDOWS.md)
   - [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - [SERIAL_PROTOCOL.md](SERIAL_PROTOCOL.md)

3. **Kiểm tra log files:**
   - Python logs in `python_sim/logs/`
   - Wokwi Serial Monitor output

---

**Chúc bạn kết nối thành công! 🚀**

---

## 📝 TÓM TẮT NHANH

1. ✅ Mở Wokwi → Tạo project ESP32
2. ✅ Copy code từ `sketch.ino`
3. ✅ Thêm thư viện ArduinoJson
4. ✅ Start simulation + Mở Serial Monitor
5. ✅ Chạy Python: `python -m robocar_sim.main`
6. ✅ Kiểm tra "ESP32: CONNECTED" trong pygame

**Xong! Hệ thống đã sẵn sàng! 🎉**
