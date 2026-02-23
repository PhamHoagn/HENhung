# Hướng Dẫn Waypoint Navigation

## 🎯 Tổng Quan

Hệ thống hỗ trợ 2 chế độ:

1. **Waypoint Navigation** - Xe di chuyển theo lộ trình định trước + né vật cản
2. **Free Roam** - Xe tự do di chuyển và né vật cản (chế độ cũ)

---

## 📋 Chế Độ 1: Waypoint Navigation (MỚI)

### Cách chạy:

```bash
cd python_sim
python run_waypoint_demo.py
```

Hoặc:

```bash
cd python_sim
set WAYPOINT_MODE=1
python -m robocar_sim.main
```

### Cấu hình lộ trình:

Edit file: `python_sim/robocar_sim/scenarios/demo_waypoints.yaml`

```yaml
waypoints:
  - [2.0, 2.0]   # Điểm 1
  - [6.0, 2.0]   # Điểm 2
  - [6.0, 6.0]   # Điểm 3
  - [2.0, 6.0]   # Điểm 4
  - [2.0, 2.0]   # Về điểm ban đầu

waypoint_radius: 0.3   # Bán kính coi như đã đến waypoint
loop_waypoints: true    # Lặp lại lộ trình
```

### Flash code mới lên ESP32:

1. Mở Arduino IDE
2. Mở file: `esp32_wokwi/sketch_waypoint.ino`
3. Upload lên ESP32
4. Chạy Python simulation

---

## 📋 Chế Độ 2: Free Roam (CŨ)

### Cách chạy:

```bash
cd python_sim
python -m robocar_sim.main
```

Hoặc sử dụng code ESP32 cũ: `esp32_wokwi/sketch/sketch.ino`

---

## 🎮 Phím điều khiển:

- **ESC** - Thoát chương trình
- **R** - Reset xe về vị trí ban đầu
- **SPACE** - Pause/Resume simulation
- **W** - Nhảy đến waypoint tiếp theo (manual, chỉ ở chế độ waypoint)
- **Mũi tên** - Di chuyển manual (override controller)

---

## 📁 Files quan trọng:

### Scenarios (Cấu hình):
- `scenarios/demo_waypoints.yaml` - Lộ trình waypoint
- `scenarios/demo_avoid.yaml` - Chế độ tránh vật cản thuần túy

### ESP32 Firmware:
- `esp32_wokwi/sketch_waypoint.ino` - Code mới (waypoint + obstacle)
- `esp32_wokwi/sketch/sketch.ino` - Code cũ (chỉ obstacle avoidance)

### Python Code:
- `robocar_sim/sim/waypoints.py` - Waypoint navigation logic
- `run_waypoint_demo.py` - Script chạy demo waypoint

---

## 🔧 Tùy chỉnh hành vi:

### Trong ESP32 (sketch_waypoint.ino):

```cpp
// Tránh vật cản
#define SAFE_DISTANCE 0.35        // Khoảng cách bắt đầu tránh
#define CRITICAL_DISTANCE 0.20    // Khoảng cách dừng khẩn cấp
#define OBSTACLE_WEIGHT 0.7       // Trọng số tránh vật cản (0-1)

// Navigation
#define BASE_SPEED 0.55           // Tốc độ cơ bản
#define TURN_SPEED 0.45           // Tốc độ rẽ
```

### Trong YAML (demo_waypoints.yaml):

```yaml
waypoint_radius: 0.3    # Giảm = khó đến waypoint hơn
loop_waypoints: true    # false = chỉ chạy 1 lần
```

---

## 💡 Tips:

1. **Waypoint quá xa nhau** → Xe có thể bị vật cản chặn
2. **Obstacle_weight cao** (0.7-0.9) → Ưu tiên tránh vật cản
3. **Obstacle_weight thấp** (0.3-0.5) → Ưu tiên đến waypoint
4. **Test với ít vật cản trước** → Rồi thêm dần

---

## 🐛 Troubleshooting:

**Xe không theo waypoint:**
- Kiểm tra file YAML đúng format
- Xem log Python có báo "Waypoint mode enabled" không

**Xe chỉ tránh vật cản, không đi đến waypoint:**
- Kiểm tra đã upload `sketch_waypoint.ino` chưa
- Giảm `OBSTACLE_WEIGHT` trong ESP32 code

**Xe bị kẹt:**
- Tăng `SAFE_DISTANCE`
- Giảm số lượng vật cản
- Điều chỉnh vị trí waypoints xa vật cản hơn

---

**Made with ❤️ for HIL RobotCar Project**
