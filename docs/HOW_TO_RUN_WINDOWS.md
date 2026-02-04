# How to Run - Windows

## Quick Start Guide

This guide will help you run the HIL Robocar simulation on Windows.

---

## Prerequisites

### 1. Python Installation
- **Python 3.10 or higher** required
- Download from: https://www.python.org/downloads/
- ⚠️ During installation, check "Add Python to PATH"

### 2. Verify Python Installation
```cmd
python --version
```
Should output: `Python 3.10.x` or higher

---

## Installation Steps

### Step 1: Install Python Dependencies
Open PowerShell or Command Prompt in the `python_sim` directory:

```cmd
cd python_sim
pip install -r requirements.txt
```

This will install:
- `pygame` - Graphics and rendering
- `pyserial` - Serial communication with ESP32
- `pyyaml` - Configuration files

### Step 2: Setup ESP32 (Wokwi)

1. Open **Wokwi** in your browser: https://wokwi.com/
2. Create a new **ESP32 project**
3. Copy the contents of `esp32_wokwi/sketch.ino` into the Wokwi editor
4. Copy the contents of `esp32_wokwi/diagram.json` as the circuit diagram
5. Install the **ArduinoJson** library in Wokwi

### Step 3: Get the Virtual COM Port

When you run the ESP32 simulation in Wokwi:
1. Click **Start Simulation**
2. Open the **Serial Monitor**
3. Note the **virtual COM port** (e.g., `COM4` or `RFC2217://localhost:4000`)

---

## Running the Simulation

### Method 1: Automated Launch (Recommended)

Simply double-click:
```
python_sim/run_sim.bat
```

The script will:
1. Check Python installation
2. Install dependencies automatically
3. Launch the simulation
4. Auto-detect the ESP32 COM port

### Method 2: Manual Launch

From the `python_sim` directory:

```cmd
python -m robocar_sim.main
```

Or specify a specific COM port:

```cmd
python -m robocar_sim.main COM4
```

---

## What You Should See

### ESP32 (Wokwi) Output:
```
# ESP32 HIL Controller Ready
{"vL": 0.60, "vR": 0.60}
{"vL": 0.60, "vR": 0.40}
...
```

### Python Console Output:
```
════════════════════════════════════════════════════════
  HIL ROBOCAR SIMULATION - Hardware-in-the-Loop
════════════════════════════════════════════════════════

[1/3] Initializing simulation world...
  ✓ Physics engine ready
  ✓ Sensors configured (Front, Left, Right)
  ✓ 7 obstacles loaded

[2/3] Initializing pygame renderer...
  ✓ Renderer ready (800x800 @ 60 FPS)

[3/3] Connecting to ESP32...
✓ Auto-detected ESP32 on COM4: USB-SERIAL CH340
✓ Connected to ESP32 on COM4 @ 115200 baud

════════════════════════════════════════════════════════
  ✓ INITIALIZATION COMPLETE - Press ESC to quit
════════════════════════════════════════════════════════
```

### pygame Window:
- 2D top-down view of the world
- Blue circle = robot car
- Gray circles = obstacles
- Colored lines = sensor rays (green=safe, orange=warning, red=danger)
- Yellow line = heading indicator
- HUD in top-left showing telemetry

---

## Controls

| Key | Action |
|-----|--------|
| `ESC` | Quit simulation |
| `R` | Reset (if implemented) |

---

## Troubleshooting

### ❌ "Python not found"
- Install Python 3.10+
- Make sure "Add to PATH" was checked during installation
- Restart your terminal

### ❌ "Could not auto-detect ESP32 port"
**Solution 1:** Manually specify the port
```cmd
python -m robocar_sim.main COM4
```

**Solution 2:** Check available ports
```python
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

**Solution 3:** For Wokwi virtual port
- Use the RFC2217 URL shown in Wokwi
- Example: `python -m robocar_sim.main rfc2217://localhost:4000`

### ❌ "ModuleNotFoundError: No module named 'pygame'"
```cmd
pip install pygame pyserial pyyaml
```

### ❌ Serial connection fails
1. Make sure Wokwi simulation is **running**
2. Check that the **Serial Monitor is open** in Wokwi
3. Try closing other programs using the COM port
4. Restart both Wokwi and the Python simulation

### ❌ Car doesn't move
- Check if ESP32 is sending motor commands
- Look at Wokwi Serial Monitor - should see `{"vL": ..., "vR": ...}`
- Check Python console for "CONNECTED" status

---

## System Architecture

```
┌─────────────┐          Serial (JSON)           ┌─────────────┐
│   ESP32     │◄──────────────────────────────►  │   Python    │
│  (Wokwi)    │                                  │ Simulation  │
│             │  Receives: {"dF":1.2,"dL":0.8}   │             │
│ Controller  │  Sends:    {"vL":0.6,"vR":0.7}   │ Sim Engine  │
│   Logic     │                                  │   Sensors   │
│             │                                  │   Physics   │
└─────────────┘                                  └─────────────┘
```

---

## Next Steps

Once everything is running:
1. Observe the car navigating obstacles
2. Monitor sensor values in the HUD
3. Watch the control logic respond to obstacles
4. Try modifying the obstacle avoidance algorithm in `sketch.ino`
5. Experiment with different world configurations

---

## File Structure

```
hil-robotcar/
├── esp32_wokwi/
│   ├── sketch.ino          ← ESP32 controller firmware
│   └── diagram.json        ← Wokwi circuit diagram
│
└── python_sim/
    ├── run_sim.bat         ← Windows launcher
    ├── requirements.txt    ← Python dependencies
    └── robocar_sim/
        ├── main.py         ← Main integration loop
        ├── sim/            ← Physics & sensors
        ├── io/             ← Serial communication
        └── render/         ← pygame visualization
```

---

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system design
3. Check [SERIAL_PROTOCOL.md](SERIAL_PROTOCOL.md) for communication details
