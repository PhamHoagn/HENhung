# System Architecture

Complete architectural documentation for the HIL Robocar simulation system.

---

## 🏛️ Overview

The HIL Robocar is a **Hardware-in-the-Loop (HIL) simulation system** that demonstrates true embedded systems development workflow. It separates control logic (ESP32) from the physical plant (Python simulation) using real-time serial communication.

### Key Principles

1. **Separation of Concerns**
   - ESP32: Pure controller (no physics knowledge)
   - Python: Pure plant simulator (no control logic)

2. **Real-Time Communication**
   - Bidirectional serial protocol
   - Fixed update rates (50 Hz)
   - Low latency (< 50ms)

3. **Deterministic Behavior**
   - Fixed time steps for physics
   - Predictable sensor readings
   - Repeatable experiments

---

## 📐 System Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                        HIL ROBOCAR SYSTEM                              │
└───────────────────────────────────────────────────────────────────────┘

 ┌─────────────────────────┐                      ┌─────────────────────────┐
 │   ESP32 Controller      │                      │   Python Simulator      │
 │    (Wokwi / Real HW)    │                      │    (Physics Engine)     │
 └─────────────────────────┘                      └─────────────────────────┘
            │                                                   │
            │              Serial Protocol                      │
            │            (JSON @ 115200 baud)                   │
            │                                                   │
            │◄──────────────────────────────────────────────────┤
            │     {"dF": 1.25, "dL": 0.85, "dR": 2.10}         │
            │           (Sensor Measurements)                   │
            │                                                   │
            │                                                   │
            ├──────────────────────────────────────────────────►│
            │       {"vL": 0.65, "vR": 0.70}                   │
            │         (Motor Commands)                          │
            │                                                   │
            v                                                   v
   ┌─────────────────┐                             ┌─────────────────────┐
   │ Control Logic   │                             │  Simulation World   │
   │ • Obstacle      │                             │  • Physics          │
   │   Avoidance     │                             │  • Sensors          │
   │ • Path Planning │                             │  • Obstacles        │
   │ • Safety Logic  │                             │  • Collision        │
   └─────────────────┘                             └─────────────────────┘
                                                              │
                                                              v
                                                   ┌─────────────────────┐
                                                   │   Visualization     │
                                                   │   (pygame 2D)       │
                                                   │   • Real-time       │
                                                   │   • 60 FPS          │
                                                   │   • HUD/Telemetry   │
                                                   └─────────────────────┘
```

---

## 🔷 Component Architecture

### 1. ESP32 Controller (Firmware)

**Location:** `esp32_wokwi/sketch.ino`

**Responsibilities:**
- ✅ Read sensor data from serial
- ✅ Implement control algorithms
- ✅ Generate motor commands
- ✅ Handle communication timeouts
- ❌ NO physics simulation
- ❌ NO world knowledge

**Architecture:**
```cpp
void loop() {
    readSensorData();              // Parse incoming JSON
    obstacleAvoidanceController(); // Compute motor commands
    sendMotorCommands();           // Output JSON
}
```

**Key Functions:**
- `readSensorData()` - Parses `{"dF": x, "dL": y, "dR": z}`
- `obstacleAvoidanceController()` - Core control logic
- `sendMotorCommands()` - Outputs `{"vL": a, "vR": b}`

**Libraries:**
- ArduinoJson 6.21+ (JSON parsing/generation)

---

### 2. Python Simulation Engine

**Location:** `python_sim/robocar_sim/`

#### 2.1 Simulation Core (`sim/`)

**`world.py` - Simulation World Manager**
```python
class SimulationWorld:
    - car: DifferentialDriveCar
    - sensors: SensorArray
    - obstacles: ObstacleManager
    - collision_detector: CollisionDetector
    
    Methods:
    - update(dt)                  # Update physics
    - get_sensor_data()           # Query sensors
    - set_motor_commands(vL, vR)  # From controller
```

**`physics.py` - Differential Drive Kinematics**
```python
class DifferentialDriveCar:
    - state: CarState (x, y, theta, v_left, v_right)
    - wheel_base: float (distance between wheels)
    
    Methods:
    - update(dt)              # Integrate motion equations
    - set_motor_commands()    # Set wheel velocities
    - get_position()          # Query current pose
```

**Physics Equations:**
```
Linear velocity:    v = (v_right + v_left) / 2
Angular velocity:   ω = (v_right - v_left) / wheel_base
Position update:    x' = x + v * cos(θ) * dt
                    y' = y + v * sin(θ) * dt
Heading update:     θ' = θ + ω * dt
```

**`sensors.py` - Raycast-Based Sensors**
```python
class UltrasonicSensor:
    - max_range: float
    - angle_offset: float
    
    Methods:
    - measure()               # Raycast against obstacles
    - _raycast_circle()       # Ray-circle intersection
    - _raycast_walls()        # Ray-wall intersection

class SensorArray:
    - sensor_front (0°)
    - sensor_left (90°)
    - sensor_right (-90°)
    
    Methods:
    - measure_all()           # All three sensors
    - get_distances()         # Return (dF, dL, dR)
```

**Raycasting Algorithm:**
1. Cast ray from sensor position in sensor direction
2. Check intersection with all obstacles (circles)
3. Check intersection with world boundaries
4. Return nearest intersection distance

**`obstacles.py` - Obstacle Management**
```python
class Obstacle:
    - position: (x, y)
    - radius: float

class ObstacleManager:
    - obstacles: List[Obstacle]
    
    Methods:
    - add_obstacle()
    - clear_obstacles()
    - create_default_scenario()
```

---

#### 2.2 Communication Layer (`io/`)

**`serial_bridge.py` - Serial Communication**
```python
class SerialBridge:
    - serial_conn: serial.Serial
    - protocol: SerialProtocol
    
    Methods:
    - connect()                           # Open COM port
    - send_sensor_data(dF, dL, dR)       # TX to ESP32
    - receive_motor_commands() → (vL, vR) # RX from ESP32
    - check_connection_alive()            # Timeout monitoring
```

**Features:**
- Non-blocking I/O (timeout = 50ms)
- Auto-detection of ESP32 port
- Graceful error handling
- Connection statistics

**`protocol.py` - JSON Protocol**
```python
class SerialProtocol:
    @staticmethod
    encode_sensor_data(dF, dL, dR) → str
        # Returns: {"dF": 1.25, "dL": 0.85, "dR": 2.10}\n
    
    @staticmethod
    decode_motor_commands(json_str) → (vL, vR)
        # Parses: {"vL": 0.65, "vR": 0.70}
```

---

#### 2.3 Rendering Layer (`render/`)

**`renderer.py` - Pygame Visualization**
```python
class SimulationRenderer:
    - screen: pygame.Surface
    - scale_x, scale_y: float (pixels per meter)
    - clock: pygame.time.Clock
    
    Methods:
    - render_frame()          # Complete frame
    - _draw_grid()            # Background grid
    - _draw_car()             # Robot visualization
    - _draw_obstacles()       # Obstacle circles
    - _draw_sensor_rays()     # Colored rays
    - _draw_hud()             # Telemetry overlay
```

**Rendering Pipeline:**
1. Clear screen (dark gray)
2. Draw grid (0.5m spacing)
3. Draw obstacles (gray circles)
4. Draw sensor rays (color-coded by distance)
5. Draw car (blue circle + heading indicator)
6. Draw HUD (top-left, semi-transparent)
7. Flip display buffer
8. Limit to target FPS

**Color Coding:**
- 🟢 Green: Distance > 0.6m (safe)
- 🟠 Orange: 0.3m - 0.6m (warning)
- 🔴 Red: < 0.3m (danger)

---

#### 2.4 Main Integration (`main.py`)

**`main.py` - Main Loop**
```python
class HILRobocarSimulation:
    - world: SimulationWorld
    - renderer: SimulationRenderer
    - serial: SerialBridge
    
    Methods:
    - run()      # Main simulation loop
    - cleanup()  # Graceful shutdown
```

**Main Loop Flow:**
```python
while running:
    # 1. Render events (pygame)
    renderer.handle_events()
    
    # 2. Get sensor data from simulation
    dF, dL, dR = world.get_sensor_data()
    
    # 3. Send to ESP32
    serial.send_sensor_data(dF, dL, dR)
    
    # 4. Receive motor commands from ESP32
    vL, vR = serial.receive_motor_commands()
    
    # 5. Apply to simulation
    world.set_motor_commands(vL, vR)
    
    # 6. Update physics (fixed time step)
    world.update(sim_dt)
    
    # 7. Render frame
    renderer.render_frame(...)
    
    # 8. Maintain loop timing
    sleep(sim_dt - elapsed_time)
```

---

## 🔄 Data Flow

### Sensor Data Flow (Python → ESP32)

```
┌─────────────┐
│   World     │
│  Obstacles  │
└──────┬──────┘
       │
       v
┌─────────────┐
│  Raycast    │
│  Sensors    │  measure() → (dF, dL, dR)
└──────┬──────┘
       │
       v
┌─────────────┐
│  Protocol   │  encode() → {"dF": 1.25, ...}
└──────┬──────┘
       │
       v
┌─────────────┐
│Serial Bridge│  write() → COM port
└──────┬──────┘
       │
       v
┌─────────────┐
│   ESP32     │  readStringUntil('\n')
│   Serial    │
└─────────────┘
       │
       v
┌─────────────┐
│ArduinoJson  │  deserializeJson()
│   Parser    │
└──────┬──────┘
       │
       v
┌─────────────┐
│ Controller  │  Use sensor data
│   Logic     │
└─────────────┘
```

### Motor Command Flow (ESP32 → Python)

```
┌─────────────┐
│ Obstacle    │
│ Avoidance   │  Compute (vL, vR)
└──────┬──────┘
       │
       v
┌─────────────┐
│ArduinoJson  │  serializeJson()
│ Generator   │
└──────┬──────┘
       │
       v
┌─────────────┐
│   ESP32     │  Serial.println()
│   Serial    │
└──────┬──────┘
       │
       v
┌─────────────┐
│Serial Bridge│  readline() → COM port
└──────┬──────┘
       │
       v
┌─────────────┐
│  Protocol   │  decode() → (vL, vR)
└──────┬──────┘
       │
       v
┌─────────────┐
│   Physics   │  set_motor_commands()
│   Engine    │
└──────┬──────┘
       │
       v
┌─────────────┐
│ Differential│  Update kinematics
│   Drive     │
└─────────────┘
```

---

## ⏱️ Timing Architecture

### Update Rates

| Component | Rate | Period | Purpose |
|-----------|------|--------|---------|
| Physics simulation | 50 Hz | 20 ms | Deterministic integration |
| Serial TX (Python→ESP32) | 50 Hz | 20 ms | Sensor updates |
| Serial RX (ESP32→Python) | 50 Hz | 20 ms | Motor commands |
| ESP32 control loop | 50 Hz | 20 ms | Control algorithm |
| Rendering | 60 FPS | 16.7 ms | Smooth visualization |

### Timing Diagram

```
Time (ms)  Python                ESP32              Visual
───────────────────────────────────────────────────────────
0          Get sensors
           Send {"dF":...} ───►  
2                                Receive & parse
                                 Run control logic
                                 Send {"vL":...} ◄───
5          Receive & parse
           Update physics
           Render frame      ─────────────────►  [Display]

20         Get sensors
           Send {"dF":...} ───►
...
```

### Latency Budget

| Operation | Time | Notes |
|-----------|------|-------|
| Sensor raycast | 1-2 ms | 3 rays, ~7 obstacles |
| JSON encode | < 0.1 ms | Lightweight |
| Serial TX | 1-2 ms | 115200 baud, ~40 bytes |
| ESP32 processing | 1-2 ms | Simple control logic |
| JSON decode | < 0.1 ms | ArduinoJson |
| Serial RX | 1-2 ms | 115200 baud, ~25 bytes |
| Physics update | 0.5-1 ms | Differential drive math |
| Rendering | 10-15 ms | pygame drawing |
| **Total latency** | **15-25 ms** | Well under 50 ms target |

---

## 🧩 Module Dependencies

```
main.py
├── sim.world
│   ├── sim.physics
│   ├── sim.sensors
│   └── sim.obstacles
├── io.serial_bridge
│   └── io.protocol
└── render.renderer

sketch.ino
└── ArduinoJson
```

---

## 🔒 Safety & Error Handling

### ESP32 Safety Features

1. **Timeout Protection**
   - If no sensor data for 200ms → stop motors
   - Prevents runaway if connection lost

2. **Range Clamping**
   - Motor commands clamped to [-1.0, 1.0]
   - Invalid sensor data → use defaults (999.0m)

3. **Emergency Stop**
   - If obstacle < 15cm → vL = vR = 0

### Python Safety Features

1. **Connection Monitoring**
   - Check serial connection alive
   - Display "DISCONNECTED" status
   - Default to zero motors if no commands

2. **Collision Detection**
   - Reset simulation if collision
   - Log collision events

3. **Graceful Shutdown**
   - Close serial port properly
   - Save statistics
   - Clean pygame exit

---

## 🎯 Design Patterns

### 1. Separation of Concerns
- **Controller** (ESP32): Only knows about sensor inputs and motor outputs
- **Plant** (Python): Only knows about physics and sensors
- **Protocol**: Clean interface between them

### 2. Publish-Subscribe
- Simulation publishes sensor data
- Controller subscribes via serial
- Controller publishes motor commands
- Simulation subscribes via serial

### 3. Fixed Time Step
- Physics uses deterministic `dt = 20ms`
- Independent of rendering rate
- Prevents physics-FPS coupling

### 4. Non-Blocking I/O
- Serial read/write with timeouts
- Never blocks main loop
- Continues even if data missing

---

## 📊 Performance Characteristics

### Typical Performance (Windows 10, i5-8250U)

| Metric | Value |
|--------|-------|
| Physics rate | 50.0 Hz ±0.1 Hz |
| Rendering FPS | 58-62 FPS |
| Serial latency | 15-25 ms |
| CPU usage | 20-30% |
| Memory usage | 80-120 MB |
| Serial throughput | ~100 msg/sec |

### Scalability

- **Physics:** O(n) where n = number of obstacles
- **Sensors:** O(n) per sensor (3 sensors total)
- **Rendering:** O(n) for obstacles, O(1) for car
- **Serial:** O(1) constant overhead

### Bottlenecks

1. **Rendering** - Most CPU intensive (60% of time)
2. **Sensor raycasting** - Second most intensive (20%)
3. **Serial I/O** - Minimal overhead (5%)
4. **Physics** - Very efficient (5%)

---

## 🔧 Configuration Parameters

### World Configuration
- `world_width = 5.0` meters
- `world_height = 5.0` meters
- `obstacle_count = 7` default
- `obstacle_radius = 0.15-0.3` meters

### Car Configuration
- `wheel_base = 0.15` meters
- `max_speed = 1.0` m/s
- `robot_radius = 0.15` meters

### Sensor Configuration
- `max_range = 3.0` meters (front), 2.0m (sides)
- `min_range = 0.02` meters
- `sensor_offset = 0.1` meters from center

### Communication Configuration
- `baud_rate = 115200`
- `timeout = 50` ms
- `update_rate = 50` Hz

### Rendering Configuration
- `window_size = 800x800` pixels
- `target_fps = 60`
- `grid_spacing = 0.5` meters

---

## 🚀 Extension Points

The architecture supports easy extensions:

### 1. Additional Sensors
Add to `SensorArray`:
```python
self.sensor_rear = UltrasonicSensor(angle_offset=math.pi)
```

### 2. Multiple Robots
Extend `SimulationWorld`:
```python
self.cars = [DifferentialDriveCar(...) for _ in range(n)]
```

### 3. Different Controllers
Replace obstacle avoidance with:
- PID line following
- A* path planning
- Waypoint navigation
- Neural network control

### 4. Advanced Physics
Extend `DifferentialDriveCar`:
- Wheel slip
- Acceleration limits
- Battery simulation
- Motor dynamics

---

## 📝 Design Decisions & Rationale

### Why JSON for Serial Protocol?
- ✅ Human-readable (debugging)
- ✅ Language-agnostic
- ✅ Easy to extend
- ✅ Standard libraries available
- ❌ Slightly larger than binary
- **Verdict:** Readability > efficiency for this application

### Why 50 Hz Update Rate?
- ✅ Fast enough for real-time control
- ✅ Slow enough for reliable serial
- ✅ Common in embedded systems
- ✅ Divisor of 60 FPS rendering

### Why pygame Instead of Unity/Unreal?
- ✅ Lightweight and fast
- ✅ Easy to install
- ✅ Full control over rendering
- ✅ Python integration
- ✅ Educational value

### Why Wokwi Instead of Real ESP32?
- ✅ No hardware required
- ✅ Reproducible demos
- ✅ Easy to share
- ✅ Virtual COM port
- ✅ Same code works on real HW

---

## 🎓 Learning Outcomes

By studying this architecture, students learn:

1. **HIL System Design** - Separation of controller and plant
2. **Real-Time Systems** - Fixed time steps, latency management
3. **Communication Protocols** - Serial, JSON, error handling
4. **Embedded Development** - Arduino, sensors, actuators
5. **Physics Simulation** - Kinematics, collision detection
6. **Software Engineering** - Modularity, clean interfaces

---

**This architecture demonstrates professional embedded systems development practices suitable for academic and industry applications.**
