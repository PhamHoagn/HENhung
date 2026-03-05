# ESP32 Firmware – sketch_improved (v7.0)

Firmware AI nhúng cho ESP32 – Decision-Tree obstacle avoidance + waypoint navigation.

---

## Tính Năng

- **Decision-Tree AI**: Trained model (depth 6, ~62 leaves, 83% accuracy) chạy trực tiếp trên ESP32
- **FreeRTOS Dual-Core**: Core 0 (AI inference @ 5 Hz), Core 1 (Control loop @ 50 Hz)
- **4WD Skid-Steer**: Điều khiển 4 bánh (vL, vR normalized)
- **9-Sensor Array**: Xử lý 9 cảm biến siêu âm
- **Waypoint Navigation**: Blend DT avoidance với waypoint heading
- **4 Behavior Modes**: FOLLOW, AVOID, STOP, RECOVERY
- **Safety-First**: Emergency stop/reverse khi front < 0.40m
- **Anti-Stuck**: Phát hiện và recovery khi bị kẹt
- **Standalone-Safe**: Safe stop nếu mất kết nối > 250ms

---

## Files

| File | Mô tả |
|------|-------|
| `sketch_improved.ino` | Main firmware (488 lines) |
| `decision_tree_model.h` | Trained DT model (auto-generated C header) |
| `model_stats.json` | Training statistics |

---

## Sử Dụng với Wokwi

1. Truy cập https://wokwi.com → tạo project ESP32
2. Copy `sketch_improved.ino` → editor
3. Tạo tab mới `decision_tree_model.h` → copy nội dung
4. Load `diagram.json` từ `esp32_wokwi/diagram.json`
5. Cài thư viện **ArduinoJson** (v6.21+)
6. Click **"Start Simulation"**

---

## Serial Protocol

### Nhận từ Python (Input):
```json
{"t": 12345, "x": 2.1, "y": 1.9, "th": 0.52, "wpX": 6.0, "wpY": 4.0, "d": [2.0,1.4,1.2,0.9,0.7,1.0,1.3,1.6,2.2]}
```

| Field | Type | Description |
|-------|------|-------------|
| `t` | int | Timestamp (ms) |
| `x`, `y` | float | Robot position (m) |
| `th` | float | Robot heading (rad) |
| `wpX`, `wpY` | float | Current waypoint (m) |
| `d` | float[9] | 9 ultrasonic distances (m) |

Sensor order: `[LS, LF, LM, LN, C, RN, RM, RF, RS]`

### Gửi về Python (Output):
```json
{"t": 12350, "vL": 0.22, "vR": 0.28, "mode": "FOLLOW", "ai_a": 1, "ai_s": 0.86, "ai_ms": 0.31}
```

| Field | Type | Description |
|-------|------|-------------|
| `t` | int | ESP32 timestamp (ms) |
| `vL`, `vR` | float | Left/right wheel commands (normalized) |
| `mode` | string | FOLLOW / AVOID / STOP / RECOVERY |
| `ai_a` | int | DT action: 0=FWD, 1=FWD-L, 2=FWD-R, 3=TURN-L, 4=TURN-R |
| `ai_s` | float | DT speed scale [0, 1] |
| `ai_ms` | float | Inference time (ms) |

---

## Configuration

Key parameters trong firmware (namespace `cfg` style dùng `constexpr`):

| Parameter | Value | Description |
|-----------|-------|-------------|
| `kMaxWheel` | 0.85 | Max normalized wheel command |
| `kBaseSpeed` | 0.65 | Cruise speed (m/s) |
| `kTrackWidth` | 0.22 | Left↔right wheel distance (m) |
| `kDStop` | 0.40 | Emergency stop distance (m) |
| `kDCritical` | 0.55 | 100% DT override distance (m) |
| `kDDanger` | 0.90 | Switch to AVOID mode (m) |
| `kDWarn` | 1.30 | Blend starts (m) |
| `kDClear` | 1.50 | Exit AVOID hysteresis (m) |
| `kDMax` | 5.50 | Maximum sensor range (m) |
| `kInputTimeoutMs` | 250 | Safe stop timeout (ms) |

---

## Train Lại Model

```cmd
cd python_sim
python train_decision_tree.py
```

Kết quả: cập nhật `decision_tree_model.h` → copy vào Wokwi project.
