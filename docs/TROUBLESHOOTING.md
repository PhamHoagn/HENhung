# Troubleshooting – HIL Robocar

Hướng dẫn xử lý các lỗi thường gặp.

---

## 1. Cài Đặt Python

### ModuleNotFoundError: No module named 'pygame'
```cmd
pip install pygame pyserial pyyaml scikit-learn
```

### Python không nhận lệnh `python`
- Kiểm tra Python đã được thêm vào PATH
- Thử `python3` thay vì `python`
- Cài lại Python, tick **"Add Python to PATH"**

### pip không hoạt động
```cmd
python -m pip install --upgrade pip
python -m pip install pygame pyserial pyyaml
```

---

## 2. Kết Nối Serial (ESP32 ↔ Python)

### Không tìm thấy COM port

**Nguyên nhân:** Wokwi simulation chưa chạy hoặc Serial Monitor chưa mở.

**Giải pháp:**
1. Mở Wokwi → Click **"Start Simulation"**
2. Mở **Serial Monitor** trong Wokwi
3. Chạy Python simulation:
   ```cmd
   python -m robocar_sim.main_waypoint --port COM7
   ```

**Tìm COM port:**
```cmd
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

### Serial timeout / mất kết nối

**Nguyên nhân:** Wokwi bị pause hoặc browser tab bị sleep.

**Giải pháp:**
- Giữ Wokwi tab active (không minimize)
- Restart Wokwi simulation
- Restart Python simulation
- Kiểm tra baud rate là 115200

### Nhận được garbage data

**Nguyên nhân:** Baud rate không khớp hoặc firmware lỗi.

**Giải pháp:**
- Kiểm tra Wokwi Serial Monitor hiển thị JSON hợp lệ:
  ```json
  {"t": 12350, "vL": 0.22, "vR": 0.28, "mode": "FOLLOW"}
  ```
- Nếu thấy ký tự lạ → re-upload firmware, kiểm tra ArduinoJson đã cài

---

## 3. ESP32 / Wokwi

### Firmware không compile

**Giải pháp:**
1. Kiểm tra đã tạo file `decision_tree_model.h` trong Wokwi project
2. Kiểm tra đã cài thư viện **ArduinoJson** (v6.21+)
3. Kiểm tra copy đúng toàn bộ code `sketch_improved.ino`

### Wokwi simulation bị treo

**Giải pháp:**
- Refresh browser (F5)
- Clear browser cache
- Dùng Chrome/Edge (tránh Firefox nếu gặp lỗi)
- Kiểm tra internet ổn định

### ESP32 boot nhưng không gửi data

**Nguyên nhân:** ESP32 chờ input từ Python trước khi gửi motor commands.

**Giải pháp:**
- Đây là hành vi bình thường – ESP32 chờ sensor data từ Python
- Chạy Python simulation → ESP32 sẽ bắt đầu respond
- Kiểm tra Wokwi Serial Monitor: Nếu thấy `{"t":...}` từ Python → ESP32 đang nhận data

---

## 4. Python Simulation

### Xe không di chuyển

**Checklist:**
1. HUD hiện "ESP32: CONNECTED"? → Nếu không, kiểm tra serial connection
2. HUD hiện mode "FOLLOW" hoặc "AVOID"? → Nếu "STOP", kiểm tra vật cản quá gần
3. Motor values (vL, vR) có khác 0? → Nếu 0, ESP32 firmware có vấn đề
4. Restart cả Wokwi + Python

### Pygame window không hiện

**Giải pháp:**
```cmd
pip install --upgrade pygame
```
- Trên Windows: Kiểm tra không có phần mềm block pygame (antivirus)
- Thử: `python -c "import pygame; pygame.init(); print('OK')"`

### Simulation quá chậm / lag

**Giải pháp:**
- Đóng browser tabs không cần thiết
- Đóng apps nặng (video call, etc.)
- Giảm cửa sổ: sửa `window_width`/`window_height` trong `main_waypoint.py`

### Robot bị kẹt / chạy vòng vòng

**Nguyên nhân:** Waypoint nằm quá gần vật cản hoặc trong khu vực hẹp.

**Giải pháp:**
- Sửa vị trí waypoints trong file YAML scenario
- Đảm bảo waypoints cách vật cản > 1.0m
- ESP32 có RECOVERY mode tự động: reverse + spin khi stuck

---

## 5. Decision Tree / AI

### Train lại DT model

```cmd
cd python_sim
python train_decision_tree.py
```

Kết quả sẽ tạo/cập nhật `decision_tree_model.h` → copy vào Wokwi project.

### AI action không hợp lý

**Kiểm tra trên HUD:**
- `ai_a`: Action class (0=FWD, 1=FWD-L, 2=FWD-R, 3=TURN-L, 4=TURN-R)
- `ai_s`: Speed scale (0–1)
- `ai_ms`: Inference time

Nếu AI luôn ra cùng 1 action → kiểm tra sensor data có thay đổi theo vị trí robot.

---

## 6. Lỗi Windows Cụ Thể

### Permission denied / Access denied
- Chạy CMD/PowerShell với **Run as Administrator**
- Kiểm tra antivirus không block Python/pygame

### Long path issues
- Di chuyển project vào folder ngắn hơn (ví dụ: `D:\HENhung\`)

### Encoding errors (tiếng Việt)
- Sử dụng PowerShell thay CMD
- Set encoding: `chcp 65001` (UTF-8)
