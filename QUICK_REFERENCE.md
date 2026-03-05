# Quick Reference – HIL Robocar

## Quick Start (3 Steps)

### 1. Install Python Dependencies
```cmd
cd python_sim
pip install -r requirements.txt
```

### 2. Setup ESP32 trên Wokwi
- Truy cập https://wokwi.com
- Tạo project ESP32 mới
- Copy `esp32_wokwi/sketch_improved/sketch_improved.ino` → Wokwi editor
- Tạo tab mới, copy `esp32_wokwi/sketch_improved/decision_tree_model.h`
- Copy `esp32_wokwi/diagram.json` → Circuit
- Add thư viện ArduinoJson (v6.21+)
- Click **"Start Simulation"**

### 3. Chạy Simulation
```cmd
cd python_sim
python -m robocar_sim.main_waypoint
```

---

## File Map

| File | Chức năng |
|------|-----------|
| `esp32_wokwi/sketch_improved/sketch_improved.ino` | ESP32 firmware – DT AI + FreeRTOS |
| `esp32_wokwi/sketch_improved/decision_tree_model.h` | Trained Decision Tree (C header) |
| `python_sim/robocar_sim/main_waypoint.py` | Main simulation loop (waypoint mode) |
| `python_sim/robocar_sim/sim/physics.py` | 4WD skid-steer kinematics |
| `python_sim/robocar_sim/sim/sensors.py` | 9-beam raycast ultrasonic sensors |
| `python_sim/robocar_sim/sim/world.py` | World simulation manager |
| `python_sim/robocar_sim/sim/waypoints.py` | Waypoint navigator |
| `python_sim/robocar_sim/io/serial_bridge.py` | Serial communication bridge |
| `python_sim/robocar_sim/render/renderer.py` | pygame 2D visualization |
| `python_sim/train_decision_tree.py` | DT model training script |

---

## Common Commands

```cmd
# Chạy simulation (waypoint mode)
cd python_sim
python -m robocar_sim.main_waypoint

# Chạy với COM port cụ thể
python -m robocar_sim.main_waypoint --port COM7

# Train lại Decision Tree model
python train_decision_tree.py

# List available COM ports
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

---

## Serial Protocol

**Python → ESP32 (State + 9 Sensors):**
```json
{"t": 12345, "x": 2.1, "y": 1.9, "th": 0.52, "wpX": 6.0, "wpY": 4.0, "d": [2.0,1.4,1.2,0.9,0.7,1.0,1.3,1.6,2.2]}
```

**ESP32 → Python (Motor + AI Telemetry):**
```json
{"t": 12350, "vL": 0.22, "vR": 0.28, "mode": "FOLLOW", "ai_a": 1, "ai_s": 0.86, "ai_ms": 0.31}
```

- Baud: 115200
- Format: JSON + `\n`
- Control loop: 50 Hz | AI: 5 Hz

Sensor index order: `[LS, LF, LM, LN, C, RN, RM, RF, RS]`

---

## Keyboard Controls

| Key | Action |
|-----|--------|
| `ESC` | Quit simulation |

---

## Quick Fixes

**Không kết nối được?**
1. Chạy Wokwi simulation trước
2. Mở Serial Monitor trong Wokwi
3. Chạy Python simulation sau

**Xe không di chuyển?**
- Kiểm tra "ESP32: CONNECTED" trên HUD
- Kiểm tra Wokwi Serial Monitor hiển thị JSON data

**Module not found?**
```cmd
pip install pygame pyserial pyyaml scikit-learn
```

---

## Key Parameters

```python
# Vehicle (4WD Skid-Steer)
track_width = 0.22       # m (left↔right)
wheel_base = 0.16        # m (front↔rear)
max_speed = 0.60          # m/s

# Simulation
sim_dt = 0.02             # 50 Hz physics
target_fps = 60           # Rendering rate

# World
world_size = 12.0 × 12.0 # meters

# Safety Distances (ESP32)
kDStop = 0.40             # Full stop/reverse
kDCritical = 0.55         # 100% DT override
kDDanger = 0.90           # Switch to AVOID
kDWarn = 1.30             # Blend starts
```

---

## Documentation

- [README.md](README.md) – Project overview
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) – System design (v2.0)
- [docs/SERIAL_PROTOCOL.md](docs/SERIAL_PROTOCOL.md) – Protocol details
- [docs/HOW_TO_RUN_WINDOWS.md](docs/HOW_TO_RUN_WINDOWS.md) – Setup guide
- [docs/WAYPOINT_NAVIGATION.md](docs/WAYPOINT_NAVIGATION.md) – Waypoint system
- [docs/DEMO_CHECKLIST.md](docs/DEMO_CHECKLIST.md) – Presentation prep
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) – Common issues
