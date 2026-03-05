# Hệ Thống Điều Hướng Waypoint

Tài liệu hệ thống waypoint navigation của HIL Robocar.

---

## Tổng Quan

Xe robot di chuyển tự động theo các điểm waypoint được định trước trong file YAML, kết hợp tránh vật cản bằng Decision-Tree AI trên ESP32.

### Luồng hoạt động:
1. Python simulator load waypoints từ YAML scenario
2. Gửi waypoint hiện tại `(wpX, wpY)` + robot state `(x, y, th)` + 9 sensor distances → ESP32
3. ESP32 tính toán motor commands dựa trên DT AI + waypoint heading
4. Khi robot đến gần waypoint (< threshold), chuyển sang waypoint tiếp theo
5. Lặp lại cho đến khi hoàn thành tất cả waypoints

---

## Chạy Waypoint Mode

```cmd
cd python_sim
python -m robocar_sim.main_waypoint
```

Chỉ định COM port:
```cmd
python -m robocar_sim.main_waypoint --port COM7
```

---

## Scenario Files (YAML)

Scenarios nằm trong `python_sim/robocar_sim/scenarios/`:

### `demo_waypoints.yaml` – 5 waypoints hình vuông
Default scenario với 5 điểm waypoint tạo thành đường đi hình vuông quanh bản đồ.

### `demo_avoid.yaml` – Obstacle avoidance demo
Scenario tập trung demo tránh vật cản.

### Format YAML:
```yaml
# Obstacle list
obstacles:
  - x: 3.0
    y: 3.0
    radius: 0.4

# Waypoint list (sẽ đi theo thứ tự)
waypoints:
  - x: 2.0
    y: 2.0
  - x: 8.0
    y: 2.0
  - x: 8.0
    y: 8.0
  - x: 2.0
    y: 8.0
  - x: 2.0
    y: 2.0

# Robot start position
start:
  x: 1.0
  y: 1.0
  theta: 0.0
```

---

## ESP32 Waypoint Handling

Trên ESP32 firmware (`sketch_improved.ino`), waypoint được xử lý như sau:

### Navigation Blending
```
Nếu có waypoint (hasWp = true):
  1. Tính heading error = atan2(wpY - y, wpX - x) - th
  2. Tính waypoint steering correction
  3. Blend với DT avoidance output dựa trên danger level:
     - MODE_FOLLOW: 70% waypoint + 30% DT
     - MODE_AVOID: 20% waypoint + 80% DT
     - MODE_STOP/RECOVERY: 100% safety override
```

### Behavior Modes

| Mode | Điều kiện | Hành vi |
|------|----------|---------|
| `FOLLOW` | front > kDWarn (1.30m) | DT + waypoint blending |
| `AVOID` | front < kDDanger (0.90m) | DT override, giảm speed |
| `STOP` | front < kDStop (0.40m) | Emergency stop/reverse |
| `RECOVERY` | Stuck detected | Reverse + spin |

---

## Waypoint Detection (Python Side)

Class `WaypointNavigator` trong `python_sim/robocar_sim/sim/waypoints.py`:

- **Reach threshold**: ~0.30m – robot coi như "đã đến" waypoint khi cách < threshold
- **Auto-advance**: Tự động chuyển sang waypoint tiếp theo
- **Progress tracking**: HUD hiển thị "WP 2/5", "WP 3/5", ...
- **Completion**: Khi hoàn thành waypoint cuối → hiển thị "COMPLETE"

---

## Visual Feedback

Trên cửa sổ pygame:
- **Waypoint markers**: Hình tròn nhỏ đánh dấu vị trí mỗi waypoint
- **Current waypoint**: Highlight waypoint đang hướng tới
- **Path line**: Đường nối giữa các waypoints
- **HUD info**: Waypoint index, khoảng cách tới waypoint hiện tại

---

## Tuning Tips

| Parameter | File | Mô tả |
|-----------|------|-------|
| Waypoint positions | `scenarios/*.yaml` | Vị trí các điểm waypoint |
| Reach threshold | `waypoints.py` | Khoảng cách coi như "đã đến" |
| Blend ratio | `sketch_improved.ino` | Tỷ lệ waypoint vs avoidance |
| Safety distances | `sketch_improved.ino` | kDStop, kDDanger, kDWarn |
| Base speed | `sketch_improved.ino` | kBaseSpeed (0.65 m/s) |
