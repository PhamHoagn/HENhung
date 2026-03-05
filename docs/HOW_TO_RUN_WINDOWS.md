# Hướng Dẫn Chạy Trên Windows

Hướng dẫn chi tiết cài đặt và chạy hệ thống HIL Robocar trên Windows.

---

## 1. Yêu Cầu Hệ Thống

- **Windows 10/11** (64-bit)
- **Python 3.10+** – https://www.python.org/downloads/
  - Tick "Add Python to PATH" khi cài đặt
- **Trình duyệt web** – Chrome/Edge (cho Wokwi)
- **Wokwi Account** (miễn phí) – https://wokwi.com

---

## 2. Cài Đặt Python Dependencies

```cmd
cd python_sim
pip install -r requirements.txt
```

Hoặc cài thủ công:
```cmd
pip install pygame pyserial pyyaml scikit-learn
```

Kiểm tra cài đặt:
```cmd
python -c "import pygame, serial, yaml; print('OK')"
```

---

## 3. Setup ESP32 Trên Wokwi

### Bước 1: Tạo Project
1. Truy cập https://wokwi.com
2. Đăng nhập (hoặc tạo tài khoản miễn phí)
3. Click **"New Project"** → chọn **ESP32**

### Bước 2: Upload Firmware
1. Xóa code mặc định trong editor
2. Copy toàn bộ nội dung `esp32_wokwi/sketch_improved/sketch_improved.ino` → paste vào editor
3. Click nút **"+"** (Add file) → tạo tab mới tên `decision_tree_model.h`
4. Copy nội dung `esp32_wokwi/sketch_improved/decision_tree_model.h` → paste vào tab mới

### Bước 3: Setup Circuit
1. Click **"diagram.json"** tab trong Wokwi
2. Copy nội dung `esp32_wokwi/diagram.json` → paste vào

### Bước 4: Thêm Thư Viện
1. Click **"Library Manager"** (biểu tượng sách)
2. Tìm **"ArduinoJson"** → cài đặt version 6.21+

### Bước 5: Chạy ESP32
1. Click **"Start Simulation"** (nút play xanh)
2. Chờ ESP32 boot (~2 giây)
3. Mở **Serial Monitor** → kiểm tra output

---

## 4. Chạy Python Simulation

### Cách 1: Command Line
```cmd
cd python_sim
python -m robocar_sim.main_waypoint
```

### Cách 2: Chỉ định COM Port
```cmd
python -m robocar_sim.main_waypoint --port COM7
```

### Cách 3: Batch File
```cmd
cd python_sim
run_sim.bat
```

---

## 5. Xác Nhận Hoạt Động

Khi chạy thành công, bạn sẽ thấy:

### Cửa sổ pygame:
- Robot 4WD hiển thị tại vị trí khởi đầu
- 9 tia sensor phát ra từ robot (mã màu theo khoảng cách)
- Vật cản hình tròn trên bản đồ
- Waypoint markers (đường đi + điểm đích)
- HUD panel hiển thị:
  - ESP32 connection status
  - Mode hiện tại (FOLLOW/AVOID/STOP/RECOVERY)
  - Waypoint progress (ví dụ: "WP 2/5")
  - Speed, heading, AI action

### Console output:
```
HIL Robocar Waypoint Simulation
Connecting to ESP32...
ESP32 connected on COM7
Simulation running...
```

---

## 6. Tìm COM Port

Nếu cần xác định COM port của Wokwi:

```cmd
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

Hoặc:
1. Mở **Device Manager** (Win+X → Device Manager)
2. Mở rộng **"Ports (COM & LPT)"**
3. Tìm port có tên chứa "Wokwi" hoặc "Serial"

---

## 7. Troubleshooting Nhanh

| Vấn Đề | Giải Pháp |
|---------|-----------|
| `ModuleNotFoundError` | `pip install pygame pyserial pyyaml scikit-learn` |
| Không tìm thấy COM port | Chạy Wokwi simulation trước, mở Serial Monitor |
| Xe không di chuyển | Kiểm tra HUD: "ESP32: CONNECTED" |
| Pygame window đen | Chờ ESP32 gửi motor commands (2-3 giây) |
| Lag/chậm | Đóng các chương trình khác sử dụng COM port |

Xem thêm: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
