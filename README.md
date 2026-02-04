<<<<<<< HEAD
# HIL Robocar Simulation

**Hardware-in-the-Loop (HIL) Robot Car Simulation for Academic Demonstrations**

A complete HIL system where ESP32 firmware (running on Wokwi) controls a virtual robot car in a Python-based 2D physics simulation.

---

## 🎯 Project Overview

This is a **true Hardware-in-the-Loop (HIL)** system:
- ✅ **ESP32 firmware** acts as the controller (obstacle avoidance logic)
- ✅ **Python simulation** acts as the "real world" (physics, sensors, rendering)
- ✅ **Serial communication** connects them (JSON protocol)
- ✅ **Real-time operation** at 50-60 Hz

### What This Demonstrates
- Embedded systems development workflows
- HIL testing methodology
- Real-time communication protocols
- Differential drive robotics
- Sensor fusion (ultrasonic sensors)
- Control algorithms (obstacle avoidance)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     HIL SYSTEM ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────────┐          Serial/JSON         ┌─────────────────────┐
    │   ESP32 (Wokwi)     │◄────────────────────────────►│   Python Sim        │
    │                     │                               │                     │
    │  ┌───────────────┐  │  {"dF": 1.2, "dL": 0.8}      │  ┌───────────────┐  │
    │  │  Controller   │  │◄─────────────────────────    │  │   Sensors     │  │
    │  │    Logic      │  │                               │  │  (Raycast)    │  │
    │  │  (Obstacle    │  │                               │  └───────────────┘  │
    │  │  Avoidance)   │  │                               │                     │
    │  └───────────────┘  │                               │  ┌───────────────┐  │
    │         │           │                               │  │   Physics     │  │
    │         v           │                               │  │ (Diff Drive)  │  │
    │  ┌───────────────┐  │  {"vL": 0.6, "vR": 0.7}      │  └───────────────┘  │
    │  │ Motor Command │  │─────────────────────────────►│          │          │
    │  │   Generator   │  │                               │          v          │
    │  └───────────────┘  │                               │  ┌───────────────┐  │
    │                     │                               │  │   Renderer    │  │
    │  Pure Controller    │                               │  │   (pygame)    │  │
    │  (No Physics)       │                               │  └───────────────┘  │
    └─────────────────────┘                               └─────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (with pip)
- **Wokwi Account** (free) - https://wokwi.com
- **Windows** (primary), Linux/Mac compatible

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd hil-robotcar
   ```

2. **Install Python dependencies**
   ```cmd
   cd python_sim
   pip install -r requirements.txt
   ```

3. **Setup ESP32 in Wokwi**
   - Go to https://wokwi.com
   - Create new ESP32 project
   - Copy `esp32_wokwi/sketch.ino` into Wokwi editor
   - Copy `esp32_wokwi/diagram.json` as circuit diagram
   - Add **ArduinoJson** library (v6.21+)

4. **Run the simulation**
   ```cmd
   cd python_sim
   run_sim.bat
   ```
   Or manually:
   ```cmd
   python -m robocar_sim.main
   ```

---

## 📁 Project Structure

```
hil-robotcar/
│
├── 📄 README.md                      ← You are here
│
├── 📂 docs/                          ← Documentation
│   ├── ARCHITECTURE.md               ← System design
│   ├── HOW_TO_RUN_WINDOWS.md         ← Setup guide
│   ├── SERIAL_PROTOCOL.md            ← Communication spec
│   ├── TROUBLESHOOTING.md            ← Common issues
│   └── DEMO_CHECKLIST.md             ← Presentation prep
│
├── 📂 esp32_wokwi/                   ← ESP32 Firmware
│   ├── sketch.ino                    ← Controller logic (Arduino C++)
│   ├── diagram.json                  ← Wokwi circuit diagram
│   └── wokwi.toml                    ← Wokwi configuration
│
└── 📂 python_sim/                    ← Python Simulation
    ├── run_sim.bat                   ← Windows launcher
    ├── requirements.txt              ← Python dependencies
    │
    └── robocar_sim/                  ← Main simulation package
        ├── main.py                   ← Main integration loop
        │
        ├── 📂 sim/                   ← Simulation engine
        │   ├── world.py              ← World manager
        │   ├── physics.py            ← Differential drive kinematics
        │   ├── sensors.py            ← Raycast ultrasonic sensors
        │   └── obstacles.py          ← Obstacle management
        │
        ├── 📂 io/                    ← Serial communication
        │   ├── serial_bridge.py      ← Non-blocking serial I/O
        │   └── protocol.py           ← JSON encoding/decoding
        │
        └── 📂 render/                ← Visualization
            └── renderer.py           ← pygame 2D renderer
```

---

## 🎮 How It Works

### 1. **Simulation Loop** (Python - 50 Hz)
```python
while running:
    # 1. Get sensor data from simulation
    dF, dL, dR = world.get_sensor_data()
    
    # 2. Send to ESP32 via Serial
    serial.send_sensor_data(dF, dL, dR)
    
    # 3. Receive motor commands from ESP32
    vL, vR = serial.receive_motor_commands()
    
    # 4. Update physics
    world.set_motor_commands(vL, vR)
    world.update(dt)
    
    # 5. Render frame
    renderer.render_frame(...)
```

### 2. **Controller Loop** (ESP32 - 50 Hz)
```cpp
void loop() {
    // 1. Read sensor data from Serial
    readSensorData();  // {"dF": 1.2, "dL": 0.8, "dR": 2.1}
    
    // 2. Run obstacle avoidance logic
    obstacleAvoidanceController();
    
    // 3. Send motor commands to Serial
    sendMotorCommands();  // {"vL": 0.6, "vR": 0.7}
}
```

### 3. **Serial Protocol** (JSON - 115200 baud)

**Python → ESP32:**
```json
{"dF": 1.25, "dL": 0.85, "dR": 2.10}
```
- `dF` = Front sensor distance (meters)
- `dL` = Left sensor distance (meters)  
- `dR` = Right sensor distance (meters)

**ESP32 → Python:**
```json
{"vL": 0.65, "vR": 0.70}
```
- `vL` = Left wheel velocity (-1.0 to 1.0)
- `vR` = Right wheel velocity (-1.0 to 1.0)

---

## 🎨 Visualization

The pygame window displays:

- 🔵 **Blue circle** - Robot car
- ⚪ **Gray circles** - Obstacles
- 📏 **Green/Orange/Red rays** - Ultrasonic sensors
  - 🟢 Green = Safe distance (> 0.6m)
  - 🟠 Orange = Warning (0.3-0.6m)
  - 🔴 Red = Danger (< 0.3m)
- 🎯 **Yellow line** - Car heading direction
- 📊 **HUD** - Real-time telemetry

---

## 🧪 Testing & Validation

### Obstacle Avoidance Behavior
The ESP32 controller implements:
1. **Emergency stop** if obstacle < 15cm ahead
2. **Turn away** if obstacle < 30cm ahead (toward open space)
3. **Veer left/right** if obstacles on sides
4. **Move forward** if no obstacles

### Expected Results
- ✅ Car navigates through obstacle field
- ✅ No collisions in normal operation
- ✅ Smooth turning behavior
- ✅ Real-time response (< 50ms latency)

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and component details |
| [HOW_TO_RUN_WINDOWS.md](docs/HOW_TO_RUN_WINDOWS.md) | Complete setup guide for Windows |
| [SERIAL_PROTOCOL.md](docs/SERIAL_PROTOCOL.md) | Communication protocol specification |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and solutions |
| [DEMO_CHECKLIST.md](docs/DEMO_CHECKLIST.md) | Presentation preparation checklist |

---

## 🛠️ Technologies Used

### Hardware/Firmware
- **ESP32** - Microcontroller (Wokwi virtual)
- **Arduino IDE** - Firmware development
- **ArduinoJson** - JSON parsing library

### Software
- **Python 3.10+** - Simulation engine
- **pygame 2.5+** - Graphics and rendering
- **pyserial 3.5+** - Serial communication
- **ArduinoJson 6.21+** - JSON protocol

### Concepts
- Hardware-in-the-Loop (HIL) testing
- Differential drive kinematics
- Raycast-based sensor simulation
- Real-time embedded systems
- Serial communication protocols

---

## 🎓 Academic Use

This project is designed for:
- ✅ Embedded systems courses
- ✅ Robotics labs
- ✅ Control systems demonstrations
- ✅ HIL methodology teaching
- ✅ Senior design projects

### Learning Objectives
Students will learn:
1. HIL system architecture
2. Real-time communication protocols
3. Embedded control algorithms
4. Physics simulation techniques
5. System integration and testing

---

## 🐛 Troubleshooting

### Common Issues

**❌ "Could not auto-detect ESP32 port"**
- Run Wokwi simulation first
- Check Serial Monitor is open in Wokwi
- Manually specify port: `python -m robocar_sim.main COM4`

**❌ "ModuleNotFoundError: pygame"**
```cmd
pip install pygame pyserial pyyaml
```

**❌ Car doesn't move**
- Check ESP32 Serial Monitor shows motor commands
- Verify "ESP32: CONNECTED" in Python HUD
- Check Wokwi simulation is running

**❌ High latency / Lag**
- Close other programs using COM port
- Reduce rendering FPS: `target_fps=30`
- Check CPU usage

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more.

---

## 🚧 Future Enhancements

Potential extensions:
- [ ] Waypoint navigation mode
- [ ] Path planning algorithms (A*, RRT)
- [ ] Multiple robot support
- [ ] Configurable obstacle courses
- [ ] Data logging and replay
- [ ] Performance metrics dashboard
- [ ] IMU sensor simulation
- [ ] PID velocity control

---

## 📜 License

This project is open-source for academic and educational purposes.

---

## 👥 Contributors

- **Your Name** - Initial development
- **Your University** - Academic supervision

---

## 🙏 Acknowledgments

- Wokwi team for excellent ESP32 simulation platform
- pygame community for graphics library
- ArduinoJson for efficient JSON parsing

---

## 📞 Contact

For questions or support:
- 📧 Email: your.email@example.com
- 🌐 GitHub: https://github.com/yourusername/hil-robotcar

---

## ⭐ Star this repo if it helped you!

If you use this project for your course or research, please give it a star ⭐ and cite it in your work!

---

**Made with ❤️ for embedded systems education**
=======
# Group10_Hệ Nhúng-1-2-25-N02-_2025
Thiết kế và mô phỏng Robocar 4 bánh tự hành theo lộ trình định trước, tránh vật cản thông minh sử dụng AI nhúng
>>>>>>> abe4479d0f157db015daf3632ce68e56941ee3b7
