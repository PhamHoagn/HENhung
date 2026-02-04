# Troubleshooting Guide

Common issues and their solutions for the HIL Robocar simulation.

---

## 🔧 Installation Issues

### ❌ "Python not found" or "python: command not found"

**Symptoms:**
- Running `python --version` shows error
- `pip` command not found

**Solutions:**
1. Install Python 3.10+ from https://python.org
2. During installation, CHECK "Add Python to PATH"
3. Restart your terminal/PowerShell
4. Verify: `python --version`

**Alternative:**
- Try `python3` instead of `python`
- Try `py` on Windows: `py --version`

---

### ❌ "ModuleNotFoundError: No module named 'pygame'"

**Symptoms:**
```
ModuleNotFoundError: No module named 'pygame'
ModuleNotFoundError: No module named 'serial'
ModuleNotFoundError: No module named 'yaml'
```

**Solution:**
```cmd
cd python_sim
pip install -r requirements.txt
```

**If that fails:**
```cmd
pip install pygame pyserial pyyaml --upgrade
```

**Still failing?**
- Check you're using the right Python: `python -m pip install pygame`
- Verify pip is installed: `python -m ensurepip`
- Try with admin privileges

---

### ❌ "Permission denied" when installing packages

**Windows Solution:**
```cmd
pip install --user -r requirements.txt
```

**Or run as Administrator:**
1. Right-click Command Prompt
2. Choose "Run as administrator"
3. Navigate to `python_sim` folder
4. Run `pip install -r requirements.txt`

---

## 🔌 Serial Connection Issues

### ❌ "Could not auto-detect ESP32 port"

**Symptoms:**
```
ERROR: Could not auto-detect ESP32 port
Available COM ports:
```

**Solutions:**

**1. Make sure Wokwi is running**
- Open Wokwi project
- Click "Start Simulation" (green play button)
- Open Serial Monitor in Wokwi
- THEN run Python simulation

**2. Manually specify the port**
```cmd
python -m robocar_sim.main COM4
```
Replace `COM4` with your actual port.

**3. Find the correct port**
```python
python -c "import serial.tools.list_ports; [print(p.device, '-', p.description) for p in serial.tools.list_ports.comports()]"
```

**4. For Wokwi RFC2217 virtual port**
```cmd
python -m robocar_sim.main rfc2217://localhost:4000
```

---

### ❌ "Failed to connect to COM4: PermissionError"

**Symptoms:**
```
ERROR: Failed to connect to COM4: could not open port 'COM4'
[Error 5] Access is denied
```

**Causes:**
- Another program is using the COM port
- Arduino IDE Serial Monitor is open
- Previous simulation didn't close properly

**Solutions:**
1. **Close all programs using the port:**
   - Arduino IDE
   - PuTTY
   - Other terminal programs
   - Other instances of the simulation

2. **Check what's using the port (Windows):**
   - Open Device Manager
   - Expand "Ports (COM & LPT)"
   - Right-click the port → Properties
   - Check which process has it open

3. **Force close the port (Windows PowerShell):**
   ```powershell
   Get-Process | Where-Object {$_.MainWindowTitle -like "*COM4*"} | Stop-Process
   ```

4. **Restart your computer** (last resort)

---

### ❌ Serial connection drops repeatedly

**Symptoms:**
- Connects initially but disconnects after a few seconds
- "ESP32: DISCONNECTED" appears in HUD
- Car stops moving

**Solutions:**

**1. Check Wokwi is still running**
- Wokwi tab still active?
- Simulation still playing?
- Serial Monitor still open?

**2. Increase timeout**
Edit [serial_bridge.py](../python_sim/robocar_sim/io/serial_bridge.py):
```python
timeout: float = 0.1  # Increase from 0.05 to 0.1
```

**3. Check USB cable quality** (if using physical ESP32)
- Try a different USB cable
- Try a different USB port
- Avoid USB hubs

**4. Reduce communication rate**
Edit [main.py](../python_sim/robocar_sim/main.py):
```python
sim_dt: float = 0.04  # Slow down from 0.02 to 0.04 (25 Hz instead of 50 Hz)
```

---

## 🎮 Simulation Issues

### ❌ pygame window doesn't appear

**Symptoms:**
- Python script runs but no window shows
- Console shows "Initializing pygame renderer..."
- Process hangs

**Solutions:**

**1. Check pygame installation:**
```python
python -c "import pygame; print(pygame.version.ver)"
```

**2. Update graphics drivers:**
- Update your GPU drivers (NVIDIA/AMD/Intel)
- Restart computer

**3. Try software rendering (if GPU issues):**
Add before pygame init in [renderer.py](../python_sim/robocar_sim/render/renderer.py):
```python
os.environ['SDL_VIDEODRIVER'] = 'windib'  # Windows
```

**4. Disable hardware acceleration:**
```python
os.environ['SDL_VIDEO_CENTERED'] = '1'
```

---

### ❌ "pygame.error: No available video device"

**Symptoms:**
```
pygame.error: No available video device
```

**Solutions:**

**Windows:**
- Running over Remote Desktop? pygame needs a display
- Use VNC instead of RDP
- Or set: `os.environ['SDL_VIDEODRIVER'] = 'windib'`

**Linux (headless):**
```bash
export SDL_VIDEODRIVER=dummy
```

---

### ❌ Car doesn't move / stays at origin

**Symptoms:**
- Simulation runs
- No errors
- Car (blue circle) doesn't move
- HUD shows position (0.0, 0.0)

**Diagnostics:**

**1. Check ESP32 connection:**
- Look at HUD: "ESP32: CONNECTED" or "DISCONNECTED"?
- If disconnected, see [Serial Connection Issues](#serial-connection-issues)

**2. Check ESP32 is sending commands:**
- Look at Wokwi Serial Monitor
- Should see: `{"vL": 0.60, "vR": 0.60}`
- If not, check ESP32 code compiled correctly

**3. Check sensor data is being sent:**
Add debug print in [main.py](../python_sim/robocar_sim/main.py):
```python
print(f"Sensors: F={dF:.2f} L={dL:.2f} R={dR:.2f}")
```

**4. Check motor commands are received:**
Add debug print in [main.py](../python_sim/robocar_sim/main.py):
```python
if motor_commands:
    print(f"Motors: L={motor_commands[0]:.2f} R={motor_commands[1]:.2f}")
```

---

### ❌ Car moves erratically or spins in place

**Symptoms:**
- Car rotates rapidly
- Unpredictable motion
- Doesn't avoid obstacles properly

**Possible Causes:**

**1. Motor commands out of range:**
Check ESP32 Serial Monitor for values outside [-1.0, 1.0]

**2. Sensor data corrupted:**
Check Python console for JSON parse errors

**3. Physics timestep too large:**
Edit [main.py](../python_sim/robocar_sim/main.py):
```python
sim_dt: float = 0.01  # Smaller timestep = more stable
```

**4. Wheel base misconfigured:**
Check [physics.py](../python_sim/robocar_sim/sim/physics.py):
```python
wheel_base: float = 0.15  # Distance between wheels (meters)
```

---

### ❌ Car immediately collides with obstacles

**Symptoms:**
- "⚠ COLLISION DETECTED" appears immediately
- Car resets continuously
- Simulation restarts in a loop

**Solutions:**

**1. Check initial position:**
Edit [main.py](../python_sim/robocar_sim/main.py):
```python
car_x=0.5,  # Move car to safe starting position
car_y=0.5,
```

**2. Reduce robot radius:**
Edit [physics.py](../python_sim/robocar_sim/sim/physics.py):
```python
robot_radius: float = 0.10  # Smaller radius
```

**3. Change obstacle configuration:**
Edit [obstacles.py](../python_sim/robocar_sim/sim/obstacles.py) to move obstacles away from starting position.

---

## 🐛 ESP32 / Wokwi Issues

### ❌ ESP32 code doesn't compile in Wokwi

**Symptoms:**
```
Compilation error: 'ArduinoJson.h' file not found
```

**Solution:**
1. Click on "Library Manager" in Wokwi
2. Search for "ArduinoJson"
3. Install version 6.21.3 or higher
4. Rebuild

---

### ❌ ESP32 prints "# ESP32 HIL Controller Ready" but nothing else

**Symptoms:**
- Serial Monitor shows greeting
- No sensor data received
- No motor commands sent

**Diagnostics:**

**1. Check Serial communication:**
- Is Python simulation sending data?
- Check Python console for errors

**2. Add debug prints in Arduino:**
```cpp
void readSensorData() {
    if (Serial.available() > 0) {
        String line = Serial.readStringUntil('\n');
        Serial.print("# DEBUG: Received: ");
        Serial.println(line);
        // ... rest of function
    }
}
```

**3. Test with manual input:**
In Wokwi Serial Monitor, type:
```json
{"dF": 1.0, "dL": 0.5, "dR": 0.5}
```
Check if motor commands appear.

---

### ❌ ArduinoJson parsing fails

**Symptoms:**
```cpp
// No response to sensor data
// Motor commands stay at 0
```

**Solutions:**

**1. Check JSON buffer size:**
```cpp
StaticJsonDocument<256> docIn;  // Increase if needed
```

**2. Verify JSON format:**
- Must be valid JSON
- No trailing commas
- Proper quotes

**3. Add error reporting:**
```cpp
DeserializationError error = deserializeJson(docIn, line);
if (error) {
    Serial.print("# JSON Error: ");
    Serial.println(error.c_str());
}
```

---

## 🎨 Rendering Issues

### ❌ Low FPS / Laggy rendering

**Symptoms:**
- HUD shows FPS < 30
- Choppy animation
- Input lag

**Solutions:**

**1. Lower target FPS:**
Edit [main.py](../python_sim/robocar_sim/main.py):
```python
target_fps: int = 30  # Lower from 60
```

**2. Reduce window size:**
```python
window_width: int = 600  # Lower from 800
window_height: int = 600
```

**3. Simplify rendering:**
Comment out grid in [renderer.py](../python_sim/robocar_sim/render/renderer.py):
```python
def _draw_grid(self):
    pass  # Disabled for performance
```

**4. Close other applications:**
- Browser tabs
- Video players
- Other heavy programs

---

### ❌ Sensor rays not visible

**Symptoms:**
- Can't see green/orange/red lines from sensors
- Rays drawn but too short

**Solutions:**

**1. Check sensor ranges:**
Edit [sensors.py](../python_sim/robocar_sim/sim/sensors.py):
```python
max_range: float = 5.0  # Increase detection range
```

**2. Check ray colors:**
Rays might be same color as background. Try different colors in [renderer.py](../python_sim/robocar_sim/render/renderer.py).

---

## 📊 Performance Issues

### ❌ High CPU usage

**Symptoms:**
- CPU usage > 50%
- Laptop fan running loud
- Battery drains quickly

**Solutions:**

**1. Reduce simulation frequency:**
```python
sim_dt: float = 0.04  # 25 Hz instead of 50 Hz
target_fps: int = 30   # 30 FPS instead of 60 FPS
```

**2. Disable debug output:**
Remove print statements from hot loops

**3. Optimize rendering:**
- Reduce window size
- Simplify graphics

---

## 🪟 Windows-Specific Issues

### ❌ "vcruntime140.dll not found"

**Solution:**
Install Visual C++ Redistributable:
https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads

---

### ❌ PowerShell execution policy errors

**Symptoms:**
```
running scripts is disabled on this system
```

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🔍 Debugging Tips

### Enable Verbose Logging

Add to [main.py](../python_sim/robocar_sim/main.py):
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitor Serial Traffic

Add to [serial_bridge.py](../python_sim/robocar_sim/io/serial_bridge.py):
```python
def send_sensor_data(self, ...):
    print(f"TX: {json_str.strip()}")
    # ... send code

def receive_motor_commands(self):
    # ... receive code
    if line:
        print(f"RX: {line.strip()}")
```

### Check Physics Values

Add to [world.py](../python_sim/robocar_sim/sim/world.py):
```python
def update(self, dt):
    print(f"Car pos: {self.car.get_position()}, heading: {self.car.get_heading()}")
    # ... rest of function
```

---

## 📞 Getting Help

If you're still stuck:

1. **Check the documentation:**
   - [HOW_TO_RUN_WINDOWS.md](HOW_TO_RUN_WINDOWS.md)
   - [ARCHITECTURE.md](ARCHITECTURE.md)
   - [SERIAL_PROTOCOL.md](SERIAL_PROTOCOL.md)

2. **Run system test:**
   ```cmd
   cd python_sim
   python test_system.py
   ```

3. **Check GitHub issues:**
   - Search existing issues
   - Create new issue with:
     - Error message (full text)
     - Steps to reproduce
     - System info (Windows version, Python version)

4. **Contact support:**
   - Email: your.email@example.com
   - Include log files from `python_sim/logs/`

---

## ✅ Known Working Configurations

These configurations are tested and working:

**Windows 10/11:**
- Python 3.10.x or 3.11.x
- pygame 2.5.2
- pyserial 3.5
- Wokwi (online, latest version)

**Hardware:**
- CPU: Intel i5 or equivalent
- RAM: 4GB minimum, 8GB recommended
- Display: 1920x1080 or higher

---

**Remember: Most issues are due to:**
1. Wrong Python version (need 3.10+)
2. Missing dependencies (run `pip install -r requirements.txt`)
3. Wokwi not running when connecting
4. COM port already in use

Check these first! 🔍
