"""
HIL Robocar - Main Integration Loop
Integrates simulation, rendering, and serial communication
"""

import time
import sys
from typing import Optional

from .sim.world import SimulationWorld
from .render.renderer import SimulationRenderer
from .io.serial_bridge import SerialBridge


class HILRobocarSimulation:
    """
    Main HIL Robocar Simulation Controller
    
    Integrates:
    - Physics simulation
    - Sensor simulation
    - Serial communication with ESP32
    - Real-time rendering
    """
    
    def __init__(
        self,
        serial_port: Optional[str] = None,
        world_width: float = 5.0,
        world_height: float = 5.0,
        window_width: int = 800,
        window_height: int = 800,
        target_fps: int = 60,
        sim_dt: float = 0.02  # 20ms time step (50 Hz physics)
    ):
        """
        Initialize HIL simulation
        
        Args:
            serial_port: COM port for ESP32 (None = auto-detect)
            world_width, world_height: World dimensions in meters
            window_width, window_height: Window dimensions in pixels
            target_fps: Target rendering FPS
            sim_dt: Physics simulation time step (seconds)
        """
        print("═" * 60)
        print("  HIL ROBOCAR SIMULATION - Hardware-in-the-Loop")
        print("═" * 60)
        
        # Simulation parameters
        self.sim_dt = sim_dt
        self.target_fps = target_fps
        
        # Initialize simulation world
        print("\n[1/3] Initializing simulation world...")
        self.world = SimulationWorld(
            width=world_width,
            height=world_height,
            car_x=0.5,
            car_y=0.5,
            car_theta=0.0
        )
        print("  ✓ Physics engine ready")
        print("  ✓ Sensors configured (Front, Left, Right)")
        print(f"  ✓ {len(self.world.obstacles.get_obstacles())} obstacles loaded")
        
        # Initialize renderer
        print("\n[2/3] Initializing pygame renderer...")
        self.renderer = SimulationRenderer(
            window_width=window_width,
            window_height=window_height,
            world_width=world_width,
            world_height=world_height,
            target_fps=target_fps
        )
        print(f"  ✓ Renderer ready ({window_width}x{window_height} @ {target_fps} FPS)")
        
        # Initialize serial bridge
        print("\n[3/3] Connecting to ESP32...")
        self.serial = SerialBridge(
            port=serial_port,
            baudrate=115200,
            timeout=0.05
        )
        
        if not self.serial.connect(auto_detect=True):
            print("\n⚠ WARNING: Failed to connect to ESP32")
            print("  Simulation will run in OPEN-LOOP mode (no controller)")
            self.serial = None
        
        # Runtime state
        self.running = True
        self.paused = False
        self.simulation_time = 0.0
        self.frame_count = 0
        
        # Default motor commands (used if no serial connection)
        self.default_vL = 0.0
        self.default_vR = 0.0
        
        print("\n" + "═" * 60)
        print("  ✓ INITIALIZATION COMPLETE - Press ESC to quit")
        print("═" * 60 + "\n")
    
    def run(self):
        """Main simulation loop"""
        print("Starting main simulation loop...\n")
        
        last_sim_time = time.time()
        
        try:
            while self.running:
                loop_start = time.time()
                
                # Handle pygame events
                if not self.renderer.handle_events():
                    self.running = False
                    break
                
                # Calculate elapsed time for physics
                current_time = time.time()
                real_dt = current_time - last_sim_time
                last_sim_time = current_time
                
                # Use fixed time step for deterministic physics
                dt = self.sim_dt
                
                # STEP 1: Get sensor data from simulation
                sensor_data = self.world.get_sensor_data()
                dF, dL, dR = sensor_data
                
                # STEP 2: Send sensor data to ESP32
                serial_connected = False
                if self.serial and self.serial.is_connected:
                    self.serial.send_sensor_data(dF, dL, dR)
                    serial_connected = True
                
                # STEP 3: Receive motor commands from ESP32
                motor_commands = None
                if self.serial and self.serial.is_connected:
                    motor_commands = self.serial.receive_motor_commands()
                
                # Apply motor commands (or defaults if no connection)
                if motor_commands:
                    vL, vR = motor_commands
                    self.world.set_motor_commands(vL, vR)
                else:
                    # No commands received - use safe defaults (stop)
                    self.world.set_motor_commands(0.0, 0.0)
                
                # STEP 4: Update physics simulation
                if not self.paused:
                    self.world.update(dt)
                    self.simulation_time += dt
                
                # STEP 5: Render frame
                car_state = self.world.get_car_state()
                sensor_rays = self.world.get_sensor_rays()
                
                telemetry = {
                    'time': self.simulation_time,
                    'x': car_state['position'][0],
                    'y': car_state['position'][1],
                    'heading': car_state['heading'],
                    'dF': dF,
                    'dL': dL,
                    'dR': dR,
                    'serial_connected': serial_connected
                }
                
                self.renderer.render_frame(
                    car_pos=car_state['position'],
                    car_heading=car_state['heading'],
                    obstacles=self.world.obstacles.get_obstacles(),
                    sensor_rays=sensor_rays,
                    is_collision=self.world.is_crashed(),
                    telemetry=telemetry
                )
                
                # Check for collision
                if self.world.is_crashed():
                    print(f"\n⚠ COLLISION DETECTED at t={self.simulation_time:.2f}s")
                    self.world.reset(0.5, 0.5, 0.0)
                    print("  ✓ Simulation reset\n")
                
                self.frame_count += 1
                
                # Maintain consistent loop timing
                loop_time = time.time() - loop_start
                sleep_time = max(0, self.sim_dt - loop_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\n⚠ Keyboard interrupt received")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up and close all resources"""
        print("\n" + "═" * 60)
        print("  SHUTTING DOWN")
        print("═" * 60)
        
        # Print statistics
        if self.serial:
            stats = self.serial.get_statistics()
            print(f"\nSerial Statistics:")
            print(f"  Messages sent:     {stats['messages_sent']}")
            print(f"  Messages received: {stats['messages_received']}")
            print(f"  Bytes sent:        {stats['bytes_sent']}")
            print(f"  Bytes received:    {stats['bytes_received']}")
        
        print(f"\nSimulation Statistics:")
        print(f"  Total time:        {self.simulation_time:.2f}s")
        print(f"  Total frames:      {self.frame_count}")
        print(f"  Average FPS:       {self.frame_count / max(self.simulation_time, 0.1):.1f}")
        
        # Close connections
        if self.serial:
            self.serial.disconnect()
        
        self.renderer.close()
        
        print("\n✓ Shutdown complete")
        print("═" * 60 + "\n")


def main():
    """Entry point for HIL Robocar Simulation"""
    # Parse command-line arguments (optional)
    serial_port = None
    if len(sys.argv) > 1:
        serial_port = sys.argv[1]
        print(f"Using specified COM port: {serial_port}")
    
    # Create and run simulation
    sim = HILRobocarSimulation(
        serial_port=serial_port,
        world_width=5.0,
        world_height=5.0,
        window_width=800,
        window_height=800,
        target_fps=60,
        sim_dt=0.02  # 50 Hz physics
    )
    
    sim.run()


if __name__ == "__main__":
    main()
