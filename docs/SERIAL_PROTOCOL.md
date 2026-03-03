# Serial Protocol Specification (Embedded AI / HIL)

## Overview

JSON line protocol between Python simulator and ESP32 firmware.

- **Baud rate:** `115200`
- **Framing:** 1 JSON object per line (`\n`)
- **Direction:** Full duplex
- **Control loop target:** 50 Hz on ESP32
- **AI loop target:** 2–5 Hz on ESP32

---

## Python → ESP32

### Purpose
Send robot state, waypoint, and **9 ultrasonic distances** for embedded AI + controller.

### Format

```json
{"t": 12345, "x": 2.1, "y": 1.9, "th": 0.52, "wpX": 6.0, "wpY": 4.0, "d": [2.0,1.4,1.2,0.9,0.7,1.0,1.3,1.6,2.2]}
```

### Fields

| Field | Type | Unit | Description |
|---|---|---|---|
| `t` | int | ms | Sender timestamp |
| `x`,`y` | float | m | Robot position |
| `th` | float | rad | Robot heading |
| `wpX`,`wpY` | float | m | Current waypoint |
| `d` | float[9] | m | Ultrasonic vector |

### `d` index order (required)

`[LS, LF, LM, LN, C, RN, RM, RF, RS]`

- `LS`: left side (~90°)
- `LF`: left far (~60°)
- `LM`: left mid (~35°)
- `LN`: left near (~15°)
- `C`: center (0°)
- `RN`: right near (~15°)
- `RM`: right mid (~35°)
- `RF`: right far (~60°)
- `RS`: right side (~90°)

All distances are clamped to `[0, dMax]` in firmware.

---

## ESP32 → Python

### Purpose
Send wheel commands and debug/telemetry from embedded AI.

### Format

```json
{"t": 12350, "vL": 0.22, "vR": 0.28, "mode": "FOLLOW", "ai_a": 1, "ai_s": 0.86, "ai_ms": 0.31}
```

### Fields

| Field | Type | Unit | Description |
|---|---|---|---|
| `t` | int | ms | ESP32 timestamp |
| `vL`,`vR` | float | normalized | Left/right wheel command |
| `mode` | string | - | `FOLLOW | AVOID | STOP | RECOVERY` |
| `ai_a` | int | - | DT action class `{0=FWD,1=FWD-L,2=FWD-R,3=TURN-L,4=TURN-R}` |
| `ai_s` | float | - | DT speed scale in `[0,1]` |
| `ai_ms` | float | ms | Latest inference time |

---

## Safety semantics

- If `front_distance < d_stop` → **STOP/REVERSE overrides AI**.
- If UART timeout or invalid sensor packet → **SAFE STOP**.
- AI is suggestion only (bias + speed scaling), never bypasses safety checks.

---

## Compatibility

Firmware still accepts old key-style packets (`dC`, `dLN`, `dRN`, ...), but `d[]` array format is the primary protocol.
