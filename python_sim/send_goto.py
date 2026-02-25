"""Simple serial helper to send GOTO command to ESP32/Wokwi."""

import argparse
import time

import serial


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="COM5")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--x", type=float, required=True)
    parser.add_argument("--y", type=float, required=True)
    args = parser.parse_args()

    with serial.Serial(args.port, args.baud, timeout=0.2) as ser:
        time.sleep(1.0)
        cmd = f"GOTO {args.x:.2f} {args.y:.2f}\n"
        ser.write(cmd.encode("utf-8"))
        print(f"Sent: {cmd.strip()}")

        t0 = time.time()
        while time.time() - t0 < 5.0:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                print(line)


if __name__ == "__main__":
    main()
