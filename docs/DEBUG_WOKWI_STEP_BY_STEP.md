# Debug Wokwi Từng Bước (Step by Step)

## 🎯 Mục Tiêu

Tìm xem vấn đề ở đâu và khắc phục từng bước.

---

## 🔍 BƯỚC 1: Test Wokwi Cơ Bản

### Test 1.1: Code Đơn Giản Nhất

**Mục đích:** Kiểm tra Wokwi có chạy được không

1. Mở https://wokwi.com
2. Tạo project ESP32 mới
3. Copy code này vào:

```cpp
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("ESP32 Works!");
}

void loop() {
  Serial.print("Time: ");
  Serial.print(millis() / 1000);
  Serial.println("s");
  delay(1000);
}
```

4. Click **"Start Simulation"**
5. Mở **Serial Monitor**

**Kết quả mong đợi:**
```
ESP32 Works!
Time: 1s
Time: 2s
Time: 3s
...
```

### ✅ Nếu Test 1.1 Thành Công:

→ Wokwi hoạt động tốt, vấn đề ở code phức tạp  
→ Chuyển sang BƯỚC 2

### ❌ Nếu Test 1.1 Thất Bại:

**Triệu chứng:**
- Loading xoay mãi không dừng
- Không có output trong Serial Monitor
- Wokwi báo lỗi

**Giải pháp:**

**A. Xóa Cache Browser**
```
Chrome/Edge: 
1. Nhấn F12
2. Chuột phải vào nút Reload
3. Chọn "Empty Cache and Hard Reload"
```

**B. Thử Trình Duyệt Khác**
- Chrome → Edge
- Edge → Firefox
- Tắt VPN nếu đang bật

**C. Kiểm Tra Wokwi Status**
- Truy cập: https://status.wokwi.com
- Kiểm tra server có hoạt động không

**D. Kiểm Tra Console Log**
```
1. Nhấn F12 (Developer Tools)
2. Tab "Console"
3. Tìm lỗi màu đỏ
4. Chụp màn hình gửi cho tôi
```

---

## 🔍 BƯỚC 2: Test Với ArduinoJson

### Test 2.1: JSON Đơn Giản

**Mục đích:** Kiểm tra ArduinoJson library

1. Vẫn trong Wokwi
2. Click **"Library Manager"**
3. Tìm **"ArduinoJson"**
4. Click **"Add to project"** → Version **6.21.3**
5. Thay code bằng:

```cpp
#include <ArduinoJson.h>

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("Testing ArduinoJson...");
  
  // Create JSON
  StaticJsonDocument<200> doc;
  doc["test"] = "hello";
  doc["value"] = 123;
  
  // Print JSON
  serializeJson(doc, Serial);
  Serial.println();
  
  Serial.println("ArduinoJson OK!");
}

void loop() {
  delay(1000);
}
```

6. Click **"Start Simulation"**
7. Mở **Serial Monitor**

**Kết quả mong đợi:**
```
Testing ArduinoJson...
{"test":"hello","value":123}
ArduinoJson OK!
```

### ✅ Nếu Test 2.1 Thành Công:

→ ArduinoJson hoạt động tốt  
→ Chuyển sang BƯỚC 3

### ❌ Nếu Test 2.1 Thất Bại:

**Lỗi compile:**
```
ArduinoJson.h: No such file or directory
```

**Giải pháp:**
1. Library Manager → Xóa ArduinoJson cũ
2. Thêm lại ArduinoJson version 6.21.3
3. Refresh page (F5)
4. Thử lại

**Lỗi runtime (treo):**
- Tăng buffer size: `StaticJsonDocument<500>`
- Thử version ArduinoJson khác (6.21.0, 6.20.0)

---

## 🔍 BƯỚC 3: Test Code HIL Đầy Đủ

### Test 3.1: Code HIL Mới (Đã Tối Ưu)

1. Copy **TOÀN BỘ** code từ file `sketch.ino` mới nhất
2. Paste vào Wokwi (xóa code cũ)
3. Đảm bảo ArduinoJson đã thêm
4. Click **"Start Simulation"**
5. Mở **Serial Monitor**

**Kết quả mong đợi:**
```
# ESP32 HIL Controller Ready
# Firmware Version: 1.0
# Waiting for sensor data...
# Setup complete!
```

### Test 3.2: Test Thủ Công

Trong Serial Monitor, gõ:
```json
{"dF": 0.50, "dL": 1.00, "dR": 1.00}
```

Nhấn Enter.

**Kết quả mong đợi:**
```json
{"vL":-0.40,"vR":0.70}
```

### ✅ Nếu Test 3.2 Thành Công:

→ ESP32 hoạt động hoàn hảo!  
→ Chuyển sang kết nối Python

### ❌ Nếu Test 3.2 Thất Bại:

**Không có output:**
- Kiểm tra Serial Monitor có mở không
- Thử baud rate khác (9600, 57600)

**Output sai:**
- Kiểm tra JSON format đúng chưa
- Đảm bảo có dấu `\n` cuối dòng

---

## 🔍 BƯỚC 4: Kết Nối Python

### Test 4.1: List COM Ports

```powershell
python -c "import serial.tools.list_ports; [print(p.device, '-', p.description) for p in serial.tools.list_ports.comports()]"
```

**Kết quả mẫu:**
```
COM3 - USB-SERIAL CH340
COM4 - Bluetooth
```

### Test 4.2: Chạy Python

```powershell
cd "D:\Hệ nhúng\hil-robotcar\python_sim"
python -m robocar_sim.main
```

**Hoặc chỉ định port:**
```powershell
python -m robocar_sim.main COM3
```

### ✅ Nếu Kết Nối Thành Công:

```
✓ Connected to ESP32 on COM3 @ 115200 baud
```

→ **HOÀN THÀNH! Hệ thống chạy được!**

### ❌ Nếu Không Kết Nối:

**Lỗi "Could not detect":**
1. Đảm bảo Wokwi đang chạy
2. Serial Monitor phải mở
3. Thử port khác: `COM3`, `COM4`, etc.

**Lỗi "Permission denied":**
1. Đóng Arduino IDE
2. Đóng tất cả Serial Monitor khác
3. Restart Wokwi
4. Thử lại

---

## 📊 CHECKLIST TỔNG HỢP

Kiểm tra từng mục:

### Wokwi
- [ ] Test code đơn giản chạy OK
- [ ] ArduinoJson test chạy OK  
- [ ] Code HIL compile không lỗi
- [ ] Serial Monitor hiển thị greeting
- [ ] Test thủ công JSON trả về đúng

### Python
- [ ] Python 3.10+ đã cài
- [ ] `pip install -r requirements.txt` đã chạy
- [ ] `test_system.py` pass
- [ ] COM port đã xác định

### Kết Nối
- [ ] Wokwi chạy trước Python
- [ ] Serial Monitor đã mở
- [ ] Python tìm thấy port
- [ ] pygame window hiện ra

---

## 🆘 CÁC TÌNH HUỐNG CỤ THỂ

### Tình Huống 1: Wokwi Loading Mãi

**Triệu chứng:**
- Click Start → loading xoay
- Không dừng sau 10 giây

**Nguyên nhân có thể:**
1. Code có vòng lặp vô hạn
2. Wokwi server chậm
3. Browser cache lỗi

**Giải pháp:**
```
1. Stop simulation (nếu có nút)
2. F5 (reload page)
3. Xóa code, paste lại code mới
4. Thử Test 1.1 (code đơn giản)
```

### Tình Huống 2: Compile Error

**Triệu chứng:**
- Thông báo lỗi màu đỏ
- "error:" trong message

**Nguyên nhân thường gặp:**
```cpp
// Thiếu thư viện
error: ArduinoJson.h: No such file

// Thiếu dấu ;
error: expected ';' before '}'

// Sai kiểu dữ liệu
error: invalid conversion
```

**Giải pháp:**
1. Đọc kỹ message lỗi
2. Kiểm tra dòng code bị lỗi
3. Đảm bảo ArduinoJson đã thêm
4. Copy lại code từ file gốc

### Tình Huống 3: No Serial Output

**Triệu chứng:**
- Simulation chạy (LED nhấp nháy)
- Serial Monitor trống trơn

**Giải pháp:**
```
1. Kiểm tra Serial Monitor đã mở chưa
2. Kiểm tra baud rate (115200)
3. Click "Restart Simulation"
4. Thêm dòng debug:
   Serial.println("DEBUG: Loop running");
```

### Tình Huống 4: Python Không Kết Nối

**Triệu chứng:**
```
ERROR: Could not auto-detect ESP32 port
```

**Giải pháp từng bước:**

**Bước A: Kiểm tra Wokwi**
```
1. Wokwi có đang chạy không?
2. Serial Monitor có mở không?
3. Có thấy "ESP32 Ready" không?
```

**Bước B: Tìm Port**
```powershell
# List tất cả COM ports
python -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"
```

**Bước C: Chỉ định Port**
```powershell
# Thử từng port
python -m robocar_sim.main COM3
python -m robocar_sim.main COM4
python -m robocar_sim.main COM5
```

---

## 💡 MẸO QUAN TRỌNG

### Mẹo 1: Luôn Test Đơn Giản Trước

Đừng chạy code phức tạp ngay. Test từ đơn giản đến phức tạp:
```
Code trống → Hello World → ArduinoJson → Code HIL
```

### Mẹo 2: Đọc Serial Monitor

Serial Monitor là công cụ debug tốt nhất:
```cpp
Serial.println("DEBUG: Reached line 50");
Serial.print("DEBUG: Distance = ");
Serial.println(distanceFront);
```

### Mẹo 3: Kiểm Tra F12 Console

Nếu Wokwi lỗi, nhấn F12 xem console log.

### Mẹo 4: Screenshot Everything

Chụp màn hình:
- Message lỗi
- Serial Monitor output
- Console log (F12)
- Code đang dùng

### Mẹo 5: Thử Incognito Mode

```
Ctrl+Shift+N (Chrome/Edge)
```
Mở Wokwi trong incognito để loại trừ lỗi cache/extension.

---

## 📞 BÁO CÁO LỖI

Nếu thử hết cách trên mà vẫn lỗi, gửi cho tôi:

**1. Kết quả các test:**
- [ ] Test 1.1: ☐ Pass ☐ Fail
- [ ] Test 2.1: ☐ Pass ☐ Fail
- [ ] Test 3.1: ☐ Pass ☐ Fail
- [ ] Test 3.2: ☐ Pass ☐ Fail

**2. Screenshot:**
- Wokwi khi lỗi
- Serial Monitor output
- F12 Console (nếu có lỗi)

**3. Thông tin:**
- Trình duyệt: Chrome/Edge/Firefox?
- Version: ?
- Hệ điều hành: Windows 10/11?

---

## ✅ KẾT LUẬN

Làm theo từng bước, không bỏ qua! Mỗi test giúp thu hẹp vấn đề.

**Test Pass:** ✓ Chuyển bước tiếp  
**Test Fail:** ✗ Debug ở bước đó

**Good luck! 🚀**
