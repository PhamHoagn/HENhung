# Khắc Phục Lỗi Wokwi Không Chạy

## ❌ Vấn Đề: Wokwi Treo Khi Ấn Start

**Triệu chứng:**
- Click nút "Start Simulation" (play màu xanh)
- Biểu tượng loading xoay xoay
- Sau 5-10 giây không có phản hồi
- Simulation không bắt đầu
- Không có output trong Serial Monitor

---

## ✅ GIẢI PHÁP ĐÃ SỬA (Code Mới)

Tôi đã sửa file `sketch.ino` - **vấn đề đã được khắc phục!**

**Thay đổi chính:**
- ❌ Bỏ `while (!Serial)` - dòng này gây treo Wokwi
- ✅ Thêm `delay(100)` đơn giản
- ✅ Khởi tạo timing variables đúng cách

**Code đã được update tự động!**

---

## 🔄 CÁC BƯỚC TIẾP THEO

### Bước 1: Reload Code Mới

**Nếu đang có Wokwi mở:**
1. Copy lại **TOÀN BỘ** code từ file `sketch.ino` (đã được sửa)
2. Quay lại Wokwi
3. **Xóa hết code cũ** trong Wokwi
4. **Paste code mới** vào
5. Click "Start Simulation"

**Hoặc đơn giản hơn:**
1. Đóng tab Wokwi cũ
2. Mở tab Wokwi mới
3. Tạo project ESP32 mới
4. Copy code mới vào

### Bước 2: Kiểm Tra Thư Viện

**Quan trọng:** Đảm bảo ArduinoJson đã được thêm

1. Trong Wokwi, click **"Library Manager"** (biểu tượng sách)
2. Tìm **"ArduinoJson"**
3. Nếu chưa có, click **"Add to project"**
4. Chọn version **6.21.3** hoặc mới hơn

### Bước 3: Thử Chạy Lại

1. Click nút **"Start Simulation"**
2. Đợi 2-3 giây
3. Mở **Serial Monitor** (Ctrl+Shift+S)

**Kết quả mong đợi:**
```
# ESP32 HIL Controller Ready
# Waiting for sensor data...
```

---

## 🔧 GIẢI PHÁP KHÁC NẾU VẪN LỖI

### Giải Pháp 1: Dùng Code Tối Giản

Nếu vẫn lỗi, dùng code test đơn giản này:

```cpp
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("ESP32 Ready!");
}

void loop() {
  Serial.println("Running...");
  delay(1000);
}
```

**Cách test:**
1. Copy code trên vào Wokwi
2. Click Start
3. Nếu chạy được → Vấn đề ở code phức tạp
4. Nếu vẫn lỗi → Vấn đề ở Wokwi

### Giải Pháp 2: Xóa Cache Wokwi

**Trên Chrome/Edge:**
1. Nhấn `F12` (mở Developer Tools)
2. Click chuột phải vào nút Reload
3. Chọn **"Empty Cache and Hard Reload"**
4. Đóng Developer Tools
5. Thử lại

**Hoặc:**
1. Đóng tất cả tab Wokwi
2. Xóa cache browser (Ctrl+Shift+Delete)
3. Chọn xóa "Cached images and files"
4. Mở Wokwi lại

### Giải Pháp 3: Thử Trình Duyệt Khác

- **Chrome** → Thử **Edge** hoặc **Firefox**
- Wokwi hoạt động tốt nhất trên Chrome/Edge
- Tránh dùng Internet Explorer

### Giải Pháp 4: Kiểm Tra Mạng

Wokwi cần internet ổn định:
1. Kiểm tra kết nối internet
2. Tắt VPN nếu đang bật
3. Thử chuyển sang WiFi khác

### Giải Pháp 5: Tạo Project Mới Hoàn Toàn

1. Đóng tab Wokwi cũ
2. Truy cập https://wokwi.com
3. Click **"New Project"**
4. Chọn **"ESP32"**
5. Chọn template **"Empty ESP32 Project"**
6. Copy code vào
7. Thêm thư viện ArduinoJson
8. Thử Start

---

## 📋 CHECKLIST DEBUG

Kiểm tra từng mục:

### Code
- [ ] Code đã được update (không còn `while (!Serial)`)
- [ ] Không có lỗi đánh máy
- [ ] Có `#include <ArduinoJson.h>` ở đầu file
- [ ] Tất cả dấu ngoặc {} đều khớp

### Wokwi Setup
- [ ] Project type là "ESP32" (không phải Arduino Uno)
- [ ] Board là "ESP32 DevKit V1"
- [ ] Thư viện ArduinoJson đã thêm (version 6.21.3+)

### Trình Duyệt
- [ ] Dùng Chrome hoặc Edge (mới nhất)
- [ ] Không có lỗi console (F12 để xem)
- [ ] Internet ổn định
- [ ] Đã thử reload hard (Ctrl+Shift+R)

---

## 🎯 CODE MỚI ĐÃ SỬA

File `sketch.ino` đã được cập nhật với những thay đổi này:

**Trước (Gây lỗi):**
```cpp
void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.setTimeout(SERIAL_TIMEOUT);
  
  // Wait for serial connection - GÂY TREO WOKWI!
  while (!Serial) {
    delay(10);
  }
  
  Serial.println("# ESP32 HIL Controller Ready");
  velocityLeft = 0.0;
  velocityRight = 0.0;
}
```

**Sau (Đã sửa):**
```cpp
void setup() {
  Serial.begin(SERIAL_BAUD);
  Serial.setTimeout(SERIAL_TIMEOUT);
  
  // Small delay for serial to initialize (Wokwi compatible)
  delay(100);
  
  Serial.println("# ESP32 HIL Controller Ready");
  Serial.println("# Waiting for sensor data...");
  
  velocityLeft = 0.0;
  velocityRight = 0.0;
  
  // Initialize timing
  lastSerialReceive = millis();
  lastSerialSend = millis();
}
```

---

## ✅ BƯỚC TIẾP THEO SAU KHI WOKWI CHẠY

Khi Wokwi đã chạy thành công:

1. **Kiểm tra Serial Monitor:**
   ```
   # ESP32 HIL Controller Ready
   # Waiting for sensor data...
   ```

2. **Test thủ công:**
   Gõ vào Serial Monitor:
   ```json
   {"dF": 0.50, "dL": 1.00, "dR": 1.00}
   ```
   
   ESP32 phải trả về:
   ```json
   {"vL": -0.40, "vR": 0.70}
   ```

3. **Chạy Python Simulation:**
   ```powershell
   cd "D:\Hệ nhúng\hil-robotcar\python_sim"
   python -m robocar_sim.main
   ```

---

## 🐛 LỖI WOKWI PHỔ BIẾN KHÁC

### Lỗi 1: "Compilation error"

**Dấu hiệu:**
- Có thông báo lỗi compile
- Màu đỏ trong code

**Giải pháp:**
- Đọc message lỗi
- Thường do thiếu thư viện
- Kiểm tra syntax

### Lỗi 2: "Simulator crashed"

**Dấu hiệu:**
- Simulation chạy rồi dừng đột ngột
- Wokwi báo lỗi

**Giải pháp:**
- Reload page
- Kiểm tra vòng lặp vô hạn
- Giảm baud rate nếu quá cao

### Lỗi 3: "Cannot connect to Wokwi"

**Dấu hiệu:**
- Không load được Wokwi
- Trang trắng

**Giải pháp:**
- Kiểm tra internet
- Wokwi server có thể bảo trì
- Thử lại sau 5-10 phút

---

## 📞 NẾU VẪN KHÔNG ĐƯỢC

Nếu thử hết các cách trên mà vẫn không được:

### Lựa Chọn 1: Dùng Code Đơn Giản Hơn

Tôi có thể tạo version đơn giản hơn của code, loại bỏ các tính năng phức tạp.

### Lựa Chọn 2: Dùng ESP32 Thật

Nếu bạn có ESP32 thật:
1. Upload code bằng Arduino IDE
2. Kết nối USB vào máy tính
3. Python sẽ kết nối qua COM port thật
4. Hoạt động giống hệt Wokwi

### Lựa Chọn 3: Báo Cáo Lỗi

Gửi thông tin cho tôi:
- Screenshot Wokwi khi treo
- Browser console log (F12)
- Message lỗi nếu có

---

## ✨ TÓM TẮT

**Vấn đề:** `while (!Serial)` gây treo Wokwi

**Giải pháp:** Đã sửa code, thay bằng `delay(100)`

**Bước tiếp theo:**
1. Copy code mới từ `sketch.ino`
2. Paste vào Wokwi
3. Thêm thư viện ArduinoJson
4. Click Start Simulation
5. Kiểm tra Serial Monitor

**Code mới đã sẵn sàng - thử ngay! 🚀**

---

## 📝 GHI CHÚ KỸ THUẬT

**Tại sao `while (!Serial)` gây lỗi trên Wokwi?**

- `while (!Serial)` chờ Serial port được mở
- Trên Arduino IDE với board thật, Serial mở khi USB kết nối
- Trên Wokwi, Serial hoạt động khác → vòng lặp vô hạn
- `delay(100)` đơn giản và hoạt động trên cả Wokwi và hardware thật

**Best practice:**
- Dùng `delay()` thay vì `while (!Serial)` cho Wokwi
- Hoặc thêm timeout: `while (!Serial && millis() < 5000)`
