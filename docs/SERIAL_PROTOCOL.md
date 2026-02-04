# Serial Protocol Specification

## Overview

The HIL Robocar uses a simple JSON-based serial protocol for communication between the Python simulation and ESP32 controller.

**Baud Rate:** 115200  
**Format:** JSON messages, one per line, terminated with `\n`  
**Direction:** Bidirectional (full-duplex)

---

## Message Formats

### Python → ESP32 (Sensor Data)

**Purpose:** Send ultrasonic sensor distance measurements to the controller

**Format:**
```json
{"dF": 1.25, "dL": 0.85, "dR": 2.10}
```

**Fields:**
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `dF` | float | meters | Distance from **Front** sensor |
| `dL` | float | meters | Distance from **Left** sensor |
| `dR` | float | meters | Distance from **Right** sensor |

**Range:** `0.02` to `3.0` meters  
**Precision:** 2 decimal places  
**Frequency:** 50 Hz (every 20ms)

**Example:**
```json
{"dF": 0.45, "dL": 1.20, "dR": 0.85}
```
*Interpretation: Obstacle 45cm ahead, 120cm to left, 85cm to right*

---

### ESP32 → Python (Motor Commands)

**Purpose:** Send motor velocity commands from controller to simulator

**Format:**
```json
{"vL": 0.65, "vR": 0.70}
```

**Fields:**
| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `vL` | float | normalized | **Left** wheel velocity |
| `vR` | float | normalized | **Right** wheel velocity |

**Range:** `-1.0` to `1.0`  
- `1.0` = Full speed forward
- `0.0` = Stop
- `-1.0` = Full speed backward

**Precision:** 2 decimal places  
**Frequency:** 50 Hz (every 20ms)

**Example:**
```json
{"vL": 0.60, "vR": 0.60}
```
*Interpretation: Both wheels at 60% forward - straight line motion*

```json
{"vL": -0.40, "vR": 0.70}
```
*Interpretation: Left wheel backward, right wheel forward - sharp left turn*

---

## Comment Lines

Lines starting with `#` are comments and should be ignored by parsers.

**Format:**
```
# This is a comment
```

**Usage:**
- Debugging messages
- Status notifications
- Initialization greetings

**Example:**
```
# ESP32 HIL Controller Ready
# Python Simulator Connected
```

---

## Timing Requirements

### Latency
- **Maximum acceptable latency:** 50ms
- **Typical latency:** 10-20ms

### Timeouts
- **Read timeout:** 50ms (non-blocking)
- **Connection timeout:** 200ms (before stopping motors)

### Update Rates
- **Sensor data (Python → ESP32):** 50 Hz (20ms)
- **Motor commands (ESP32 → Python):** 50 Hz (20ms)

---

## Error Handling

### Invalid JSON
If JSON parsing fails:
- **ESP32:** Use last valid sensor values
- **Python:** Use default motor commands (stop)

### Missing Fields
If required fields are missing:
- **ESP32:** Use default value `999.0` for sensors
- **Python:** Use default value `0.0` for motors

### Connection Loss
If no data received for > 200ms:
- **ESP32:** Stop motors (`vL=0, vR=0`)
- **Python:** Display "DISCONNECTED" status

### Malformed Data
- Skip the line and continue
- Log error if in debug mode
- Do NOT crash the program

---

## Implementation Examples

### Python Encoding (Sensor Data)

```python
import json

def encode_sensor_data(dF: float, dL: float, dR: float) -> str:
    data = {
        "dF": round(dF, 2),
        "dL": round(dL, 2),
        "dR": round(dR, 2)
    }
    return json.dumps(data) + "\n"

# Usage
message = encode_sensor_data(1.25, 0.85, 2.10)
serial.write(message.encode('utf-8'))
```

### Python Decoding (Motor Commands)

```python
import json

def decode_motor_commands(line: str) -> tuple:
    try:
        line = line.strip()
        if line.startswith("#"):
            return None
        
        data = json.loads(line)
        vL = float(data.get("vL", 0.0))
        vR = float(data.get("vR", 0.0))
        
        # Clamp to valid range
        vL = max(-1.0, min(1.0, vL))
        vR = max(-1.0, min(1.0, vR))
        
        return (vL, vR)
    except:
        return None

# Usage
line = serial.readline().decode('utf-8')
motors = decode_motor_commands(line)
if motors:
    vL, vR = motors
    car.set_velocities(vL, vR)
```

### Arduino Parsing (Sensor Data)

```cpp
#include <ArduinoJson.h>

StaticJsonDocument<128> doc;

void parseSensorData(String line) {
    DeserializationError error = deserializeJson(doc, line);
    
    if (error) {
        // Invalid JSON - use defaults
        return;
    }
    
    float dF = doc["dF"] | 999.0;  // Default to 999.0
    float dL = doc["dL"] | 999.0;
    float dR = doc["dR"] | 999.0;
    
    // Use sensor data...
}
```

### Arduino Encoding (Motor Commands)

```cpp
#include <ArduinoJson.h>

StaticJsonDocument<128> doc;

void sendMotorCommands(float vL, float vR) {
    doc.clear();
    
    // Clamp to valid range
    vL = constrain(vL, -1.0, 1.0);
    vR = constrain(vR, -1.0, 1.0);
    
    doc["vL"] = vL;
    doc["vR"] = vR;
    
    serializeJson(doc, Serial);
    Serial.println();  // Add newline terminator
}
```

---

## Communication Flow

```
Time (ms)    Python Sim                ESP32 Controller
────────────────────────────────────────────────────────
0            [Send sensors]
             {"dF":1.2,"dL":0.8}  →
                                        [Receive & parse]
                                        [Run control logic]
                                        [Send motors]
5                                  ←    {"vL":0.6,"vR":0.7}
             [Receive & parse]
             [Update physics]
             [Render frame]

20           [Send sensors]
             {"dF":1.1,"dL":0.9}  →
                                        ...
```

---

## Testing the Protocol

### Using Python Script
```python
import serial
import json
import time

# Connect to ESP32
ser = serial.Serial('COM4', 115200, timeout=0.05)
time.sleep(1)

# Send test sensor data
for i in range(10):
    data = {"dF": 1.0 + i*0.1, "dL": 0.5, "dR": 0.5}
    message = json.dumps(data) + "\n"
    ser.write(message.encode())
    
    # Read response
    if ser.in_waiting:
        response = ser.readline().decode('utf-8')
        print(f"Sent: {message.strip()}")
        print(f"Recv: {response.strip()}")
    
    time.sleep(0.1)

ser.close()
```

### Using Arduino Serial Monitor
1. Open Wokwi Serial Monitor
2. Send test JSON:
   ```
   {"dF": 0.50, "dL": 1.00, "dR": 1.00}
   ```
3. Observe motor command responses

---

## Protocol Extensions (Future)

Potential extensions for advanced features:

### Battery Status
```json
{"bat": 85}  // Battery percentage
```

### Wheel Encoders
```json
{"encL": 1234, "encR": 1256}  // Encoder ticks
```

### IMU Data
```json
{"ax": 0.1, "ay": 0.0, "gz": 0.05}  // Accelerometer + Gyro
```

### Waypoint Commands
```json
{"wp": [1.5, 2.0]}  // Target waypoint (x, y)
```

---

## Best Practices

1. **Always validate JSON** before parsing
2. **Use timeouts** for non-blocking reads
3. **Clamp values** to valid ranges
4. **Handle errors gracefully** - don't crash
5. **Log protocol errors** for debugging
6. **Keep messages small** (< 128 bytes)
7. **One message per line** - never split JSON across lines
8. **Always terminate with `\n`**

---

## Debugging Tips

### View Raw Serial Data (Python)
```python
ser = serial.Serial('COM4', 115200)
while True:
    if ser.in_waiting:
        raw = ser.read(ser.in_waiting)
        print(f"RAW: {raw}")
```

### View Raw Serial Data (Arduino)
```cpp
void loop() {
    if (Serial.available()) {
        String line = Serial.readStringUntil('\n');
        Serial.print("# RECV: ");
        Serial.println(line);
    }
}
```

### Common Issues
- **Missing newlines:** JSON appears concatenated
- **Wrong encoding:** Use UTF-8 on both sides
- **Buffer overflow:** Keep messages < 128 bytes
- **Race conditions:** Use proper timeouts

---

## Performance Metrics

Typical performance on Windows 10 with Wokwi:

| Metric | Value |
|--------|-------|
| Latency (round-trip) | 15-25ms |
| Throughput | ~100 messages/sec |
| Packet loss | < 0.1% |
| Jitter | ±5ms |

---

## Compliance Checklist

- [ ] JSON format validated
- [ ] Fields within specified ranges
- [ ] Messages terminated with `\n`
- [ ] Baud rate = 115200
- [ ] Timeouts implemented
- [ ] Error handling present
- [ ] Comments ignored properly
- [ ] Non-blocking I/O used
