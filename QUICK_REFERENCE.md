# Quick Reference - HIL Robocar

## 🚀 Quick Start (3 Steps)

### 1️⃣ Install Python Dependencies
```cmd
cd python_sim
pip install -r requirements.txt
```

### 2️⃣ Setup ESP32 in Wokwi
- Go to https://wokwi.com
- Copy [sketch.ino](esp32_wokwi/sketch.ino) → Wokwi editor
- Copy [diagram.json](esp32_wokwi/digagram.json) → Circuit
- Add ArduinoJson library (v6.21+)
- Click "Start Simulation"

### 3️⃣ Run Simulation
```cmd
cd python_sim
run_sim.bat
```

---

## 📁 File Map

| File | What It Does |
|------|-------------|
| [sketch.ino](esp32_wokwi/sketch.ino) | ESP32 obstacle avoidance controller |
| [main.py](python_sim/robocar_sim/main.py) | Main simulation loop |
| [physics.py](python_sim/robocar_sim/sim/physics.py) | Differential drive kinematics |
| [sensors.py](python_sim/robocar_sim/sim/sensors.py) | Raycast ultrasonic sensors |
| [serial_bridge.py](python_sim/robocar_sim/io/serial_bridge.py) | Serial communication |
| [renderer.py](python_sim/robocar_sim/render/renderer.py) | pygame visualization |

---

## 🔧 Common Commands

```cmd
# Test system
python test_system.py

# Run simulation
python -m robocar_sim.main

# Run with specific port
python -m robocar_sim.main COM4

# List available ports
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

---

## 📊 Serial Protocol

**Python → ESP32 (Sensors):**
```json
{"dF": 1.25, "dL": 0.85, "dR": 2.10}
```

**ESP32 → Python (Motors):**
```json
{"vL": 0.65, "vR": 0.70}
```

- Baud: 115200
- Format: JSON + `\n`
- Rate: 50 Hz

---

## 🎨 Controls

| Key | Action |
|-----|--------|
| `ESC` | Quit |
| `R` | Reset (future) |

---

## 🐛 Quick Fixes

**No connection?**
1. Start Wokwi simulation first
2. Open Serial Monitor in Wokwi
3. Then run Python

**Car doesn't move?**
- Check "ESP32: CONNECTED" in HUD
- Check Wokwi Serial Monitor shows motor commands

**Module not found?**
```cmd
pip install pygame pyserial pyyaml
```

---

## 📚 Documentation

- [README.md](README.md) - Project overview
- [HOW_TO_RUN_WINDOWS.md](docs/HOW_TO_RUN_WINDOWS.md) - Complete setup
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design
- [SERIAL_PROTOCOL.md](docs/SERIAL_PROTOCOL.md) - Protocol details
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Common issues
- [DEMO_CHECKLIST.md](docs/DEMO_CHECKLIST.md) - Presentation prep

---

## 🎯 Key Parameters

```python
# Simulation
sim_dt = 0.02              # 50 Hz physics
target_fps = 60            # Rendering rate

# World
world_width = 5.0          # meters
world_height = 5.0         # meters

# Car
wheel_base = 0.15          # meters
max_speed = 1.0            # m/s

# Sensors
max_range = 3.0            # meters (front)
```

---

## ✅ Success Checklist

- [ ] Python 3.10+ installed
- [ ] Dependencies installed
- [ ] Wokwi ESP32 running
- [ ] Serial connection OK
- [ ] pygame window shows
- [ ] Car navigates obstacles
- [ ] No collisions

---

**Ready to go! 🚀**
