# ESP32 Improved Firmware - Hướng Dẫn Sử Dụng

## 📋 Tổng Quan

Đây là **firmware ESP32 cải tiến** với các tính năng nâng cao:

### ✨ Cải Tiến So Với Phiên Bản Cũ:

1. **Waypoint Navigation Thực Sự**
   - Tính toán bearing (hướng) đến waypoint
   - Điều khiển differential steering chính xác
   - Giảm tốc khi gần đích

2. **Obstacle Avoidance Thông Minh**
   - **4 mức cảnh báo**: Critical, Danger, Warning, Caution
   - Phản ứng theo gradient (càng gần càng mạnh)
   - Xử lý dead-end (lùi lại và rẽ)
   
3. **Anti-Stuck Mechanism**
   - Phát hiện khi xe bị kẹt
   - Tự động recovery (lùi và rẽ)
   - Ngăn chặn đứng yên vô thời hạn

4. **Smooth Control**
   - Giới hạn tốc độ an toàn
   - Blend mượt giữa waypoint và obstacle avoidance
   - Không bị oscillate (rung lắc)

## 🔧 Cách Sử Dụng

### Bước 1: Upload Code Lên ESP32

#### Sử Dụng Wokwi (Virtual ESP32):
1. Mở https://wokwi.com
2. Tạo new ESP32 project
3. Copy toàn bộ code từ `sketch_improved.ino`
4. Thêm library **ArduinoJson** (v6.21+) trong Library Manager
5. Click **Start Simulation**

#### Sử Dụng ESP32 Thật:
1. Mở Arduino IDE
2. File → Open → chọn `sketch_improved.ino`
3. Tools → Board → chọn ESP32 Dev Module
4. Tools → Port → chọn COM port của ESP32
5. Sketch → Upload

### Bước 2: Chạy Python Simulation

```powershell
cd python_sim
python -c "import sys; sys.path.insert(0, '.'); from robocar_sim import main_waypoint; main_waypoint.main_waypoint()"
```

Python sẽ tự động:
- Detect ESP32 trên COM port
- Gửi sensor data + waypoint + position
- Nhận motor commands từ ESP32
- Hiển thị "🔗 ESP32 Connected" màu xanh

## 📡 Serial Protocol

### Python → ESP32:
```json
{
  "dF": 1.25,    // Front sensor distance (m)
  "dL": 0.85,    // Left sensor distance (m)  
  "dR": 2.10,    // Right sensor distance (m)
  "wx": 5.0,     // Waypoint X coordinate (m)
  "wy": 3.0,     // Waypoint Y coordinate (m)
  "h": 1.57,     // Car heading (radians)
  "x": 2.0,      // Car X position (m)
  "y": 2.0       // Car Y position (m)
}
```

### ESP32 → Python:
```json
{
  "vL": 0.65,    // Left motor velocity [-1.0, 1.0]
  "vR": 0.70     // Right motor velocity [-1.0, 1.0]
}
```

## ⚙️ Tùy Chỉnh Parameters

Trong file `.ino`, bạn có thể điều chỉnh:

```cpp
// Tốc độ
#define MAX_SPEED 0.50          // Tốc độ tối đa
#define BASE_SPEED 0.35         // Tốc độ bình thường
#define SLOW_SPEED 0.20         // Tốc độ chậm

// Khoảng cách cảnh báo
#define CRITICAL_DISTANCE 0.25  // Nguy hiểm tối đa
#define DANGER_DISTANCE 0.40    // Nguy hiểm cao
#define WARNING_DISTANCE 0.60   // Cảnh báo
#define CAUTION_DISTANCE 0.90   // Thận trọng

// Anti-stuck
#define STUCK_THRESHOLD 5       // Số cycles trước khi coi là bị kẹt
#define RECOVERY_DURATION 20    // Thời gian recovery
```

## 🐛 Troubleshooting

### Vấn Đề: ESP32 không kết nối
**Giải pháp:**
- Kiểm tra COM port: `[System.IO.Ports.SerialPort]::GetPortNames()`
- Đóng Arduino Serial Monitor
- Rút và cắm lại USB

### Vấn Đề: Xe vẫn đi thẳng vào vật cản
**Nguyên nhân:** Đang dùng firmware cũ
**Giải pháp:** 
1. Upload `sketch_improved.ino` lên ESP32
2. Reset ESP32
3. Chạy lại Python simulation

### Vấn Đề: Xe rung lắc, không mượt
**Giải pháp:** Giảm tốc độ trong code:
```cpp
#define MAX_SPEED 0.40     // Giảm từ 0.50
#define BASE_SPEED 0.25    // Giảm từ 0.35
```

### Vấn Đề: Xe quá chậm
**Giải pháp:** Tăng tốc độ:
```cpp
#define MAX_SPEED 0.60     // Tăng từ 0.50
#define BASE_SPEED 0.45    // Tăng từ 0.35
```

## 📊 So Sánh Các Phiên Bản

| Tính Năng | sketch.ino (Cũ) | sketch_waypoint.ino | sketch_improved.ino (MỚI) |
|-----------|-----------------|---------------------|---------------------------|
| Tránh vật cản | ✓ Cơ bản | ✓ Cơ bản | ✓✓✓ Thông minh 4 mức |
| Waypoint navigation | ✗ | ~ Chưa hoàn chỉnh | ✓✓✓ Đầy đủ |
| Anti-stuck | ✗ | ✗ | ✓✓✓ Có |
| Smooth control | ✗ | ✗ | ✓✓✓ Có |
| Recovery | ✗ | ✗ | ✓✓✓ Tự động |

## 🎯 Kết Quả Mong Đợi

Với firmware mới:
- ✅ Xe đi theo lộ trình waypoint chính xác
- ✅ Tránh vật cản mượt mà, không va chạm
- ✅ Không bị đứng yên khi gặp vật cản
- ✅ Tự động recovery khi bị kẹt
- ✅ Di chuyển ổn định, không rung

## 📝 Ghi Chú

- Firmware này **tương thích ngược** với Python simulation cũ (nếu không có waypoint, vẫn chạy được)
- Serial baud rate: **115200** (phải khớp với Python)
- Update rate: **50 Hz** (20ms per cycle)

## 🆘 Hỗ Trợ

Nếu còn vấn đề, check console output:
- ESP32: Serial Monitor trong Arduino IDE hoặc Wokwi
- Python: Terminal output khi chạy simulation
