"""
HIL Robocar - Main với Waypoint Navigation
"""

import time
import sys
import os
import yaml
import math
from typing import Optional, List, Tuple

from .sim.world import SimulationWorld
from .sim.waypoints import WaypointNavigator
from .sim.autopilot import WaypointAutopilot
from .render.renderer import SimulationRenderer
from .io.serial_bridge import SerialBridge


def load_scenario_waypoints(scenario_file: str) -> dict:
    """Load scenario from YAML file"""
    if os.path.exists(scenario_file):
        with open(scenario_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


class HILRobocarWaypointSimulation:
    """HIL Robocar với Waypoint Navigation"""
    
    def __init__(
        self,
        serial_port: Optional[str] = None,
        scenario_file: Optional[str] = None,
        world_width: float = 8.0,
        world_height: float = 8.0,
        window_width: int = 800,
        window_height: int = 800,
        target_fps: int = 60,
        sim_dt: float = 0.02
    ):
        print("═" * 60)
        print("  HIL ROBOCAR - WAYPOINT NAVIGATION MODE")
        print("═" * 60)
        
        self.sim_dt = sim_dt
        self.target_fps = target_fps
        
        # Load scenario
        scenario = {}
        if scenario_file:
            scenario = load_scenario_waypoints(scenario_file)
            print(f"\n✓ Scenario: {scenario.get('name', 'Unknown')}")
        
        # Waypoint setup
        waypoints = scenario.get('waypoints', [])
        waypoint_radius = scenario.get('waypoint_radius', 0.3)
        loop_waypoints = scenario.get('loop_waypoints', True)
        
        if waypoints:
            self.waypoint_navigator = WaypointNavigator(
                waypoints=waypoints,
                reach_radius=waypoint_radius,
                loop=loop_waypoints
            )
            print(f"✓ Loaded {len(waypoints)} waypoints")
        else:
            self.waypoint_navigator = None
            print("⚠ No waypoints - pure obstacle avoidance mode")
        
        # Car starting position
        car_x = scenario.get('car_start_x', 2.0)
        car_y = scenario.get('car_start_y', 2.0)
        car_heading = math.radians(scenario.get('car_start_heading', 0.0))
        
        # Initialize simulation world
        print("\n[1/3] Initializing simulation world...")
        self.world = SimulationWorld(
            width=world_width,
            height=world_height,
            car_x=car_x,
            car_y=car_y,
            car_theta=car_heading
        )
        
        # Load obstacles from scenario
        obstacles = scenario.get('obstacles', [])
        if obstacles:
            # Clear default obstacles and load scenario obstacles
            self.world.obstacles._obstacles = []  # Clear internal list
            for obs in obstacles:
                if obs.get('type') == 'circle':
                    self.world.obstacles.add_obstacle(
                        obs['x'], obs['y'], obs['radius']
                    )
                elif obs.get('type') == 'box':
                    # Convert box to circle approximation
                    size = max(obs.get('width', 0.5), obs.get('height', 0.5))
                    self.world.obstacles.add_obstacle(
                        obs['x'], obs['y'], size * 0.6
                    )
        
        print("  ✓ Physics engine ready")
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
        print(f"  ✓ Renderer ready ({window_width}x{window_height})")
        
        # Initialize serial
        print("\n[3/3] Connecting to ESP32...")
        self.serial = SerialBridge(port=serial_port, baudrate=115200, timeout=0.05)
        
        if not self.serial.connect(auto_detect=True):
            print("⚠ WARNING: No ESP32 - Open loop mode")
            self.serial = None
        
        # Runtime state
        self.running = True
        self.simulation_running = True
        self.waypoint_edit_mode = False
        self.simulation_time = 0.0
        self.frame_count = 0
        self.start_pos = (car_x, car_y, car_heading)
        self.autopilot = WaypointAutopilot(max_speed=0.8)
        
        print("\n" + "═" * 60)
        print("  ✓ WAYPOINT NAVIGATION READY")
        print("═" * 60 + "\n")
    
    def run(self):
        """Main simulation loop"""
        print("Starting waypoint navigation...\n")
        
        last_sim_time = time.time()
        
        try:
            while self.running:
                loop_start = time.time()
                
                # Handle events
                if not self.renderer.handle_events():
                    self.running = False
                    break

                actions = self.renderer.consume_actions()
                if actions.get('toggle_start'):
                    self.simulation_running = not self.simulation_running
                if actions.get('reset'):
                    self._reset_simulation()
                if actions.get('toggle_waypoint_mode'):
                    self.waypoint_edit_mode = not self.waypoint_edit_mode
                if self.waypoint_edit_mode and actions.get('add_waypoint'):
                    self._add_waypoint(actions['add_waypoint'])
                
                # Time step
                current_time = time.time()
                real_dt = current_time - last_sim_time
                last_sim_time = current_time
                dt = self.sim_dt
                
                # Get sensor data
                sensor_data = self.world.get_sensor_data()
                dF, dL, dR = sensor_data
                
                # Get car state
                car_state = self.world.get_car_state()
                car_x, car_y = car_state['position']
                car_heading = car_state['heading']
                
                # Update waypoint navigator
                if self.waypoint_navigator:
                    reached = self.waypoint_navigator.update(car_x, car_y)
                    if reached:
                        current_wp = self.waypoint_navigator.get_current_waypoint()
                        if current_wp:
                            print(f"✓ Đã đến waypoint {self.waypoint_navigator.current_waypoint_index + 1}")
                
                # Send data to ESP32 (với thông tin waypoint)
                serial_connected = False
                if self.serial and self.serial.is_connected:
                    # Gửi sensor + waypoint info
                    if self.waypoint_navigator:
                        current_wp = self.waypoint_navigator.get_current_waypoint()
                        if current_wp:
                            wx, wy = current_wp
                            # Send enhanced data
                            self.serial.send_sensor_data(dF, dL, dR, wx, wy, car_heading)
                        else:
                            self.serial.send_sensor_data(dF, dL, dR)
                    else:
                        self.serial.send_sensor_data(dF, dL, dR)
                    
                    serial_connected = True
                
                # Receive motor commands
                motor_commands = None
                if self.serial and self.serial.is_connected:
                    motor_commands = self.serial.receive_motor_commands()

                # Fallback autopilot if serial is not connected
                if motor_commands is None:
                    current_wp = None
                    if self.waypoint_navigator:
                        current_wp = self.waypoint_navigator.get_current_waypoint()
                    motor_commands = self.autopilot.compute_commands(
                        (car_x, car_y), car_heading, current_wp, sensor_data
                    )
                
                # Apply commands
                if motor_commands:
                    vL, vR = motor_commands
                    self.world.set_motor_commands(vL, vR)
                else:
                    self.world.set_motor_commands(0.0, 0.0)
                
                # Update physics
                if self.simulation_running:
                    self.world.update(dt)
                    self.simulation_time += dt
                
                # Render
                sensor_rays = self.world.get_sensor_rays()
                
                waypoints_list = None
                current_wp_idx = 0
                if self.waypoint_navigator and self.waypoint_navigator.has_waypoints():
                    waypoints_list = self.waypoint_navigator.waypoints
                    current_wp_idx = self.waypoint_navigator.current_waypoint_index
                
                telemetry = {
                    'time': self.simulation_time,
                    'x': car_x,
                    'y': car_y,
                    'heading': car_heading,
                    'dF': dF,
                    'dL': dL,
                    'dR': dR,
                    'serial_connected': serial_connected
                }
                
                self.renderer.render_frame(
                    car_pos=(car_x, car_y),
                    car_heading=car_heading,
                    obstacles=self.world.obstacles.get_obstacles(),
                    sensor_rays=sensor_rays,
                    is_collision=self.world.is_crashed(),
                    telemetry=telemetry,
                    waypoints=waypoints_list,
                    current_waypoint_index=current_wp_idx,
                    simulation_running=self.simulation_running,
                    waypoint_edit_mode=self.waypoint_edit_mode
                )
                
                # Collision detection
                if self.world.is_crashed():
                    print(f"\n⚠ VA CHẠM tại t={self.simulation_time:.2f}s")
                    self.world.reset(*self.start_pos)
                    if self.waypoint_navigator:
                        self.waypoint_navigator.reset()
                    self.autopilot.reset()
                    print("  ✓ Reset\n")
                
                self.frame_count += 1
                
                # Timing
                loop_time = time.time() - loop_start
                sleep_time = max(0, self.sim_dt - loop_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\n⚠ Dừng bởi người dùng")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup"""
        print("\n" + "═" * 60)
        print("  ĐANG THOÁT")
        print("═" * 60)
        
        if self.serial:
            stats = self.serial.get_statistics()
            print(f"\nSerial: {stats['messages_sent']} sent, {stats['messages_received']} received")
        
        print(f"Simulation: {self.simulation_time:.1f}s, {self.frame_count} frames")
        
        if self.waypoint_navigator:
            print(f"Waypoints reached: {self.waypoint_navigator.total_waypoints_reached}")
        
        if self.serial:
            self.serial.disconnect()
        
        self.renderer.close()
        
        print("\n✓ Đã thoát")
        print("═" * 60 + "\n")

    def _reset_simulation(self):
        """Reset state to starting pose and restart waypoint loop."""
        self.world.reset(*self.start_pos)
        if self.waypoint_navigator:
            self.waypoint_navigator.reset()
        self.autopilot.reset()
        self.simulation_time = 0.0

    def _add_waypoint(self, waypoint: Tuple[float, float]):
        """Append waypoint from UI click and keep within world bounds."""
        wx = min(max(0.2, waypoint[0]), self.world.width - 0.2)
        wy = min(max(0.2, waypoint[1]), self.world.height - 0.2)

        if self.waypoint_navigator is None:
            self.waypoint_navigator = WaypointNavigator(
                waypoints=[(wx, wy)],
                reach_radius=0.3,
                loop=True,
            )
        else:
            self.waypoint_navigator.waypoints.append((wx, wy))


def main_waypoint():
    """Entry point for waypoint navigation"""
    # Get scenario file
    scenario_file = os.environ.get('SCENARIO_FILE')
    if not scenario_file:
        # Default scenario
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scenario_file = os.path.join(script_dir, 'scenarios', 'demo_waypoints.yaml')
    
    # Create simulation
    sim = HILRobocarWaypointSimulation(
        serial_port=None,  # Auto-detect
        scenario_file=scenario_file,
        world_width=8.0,
        world_height=8.0,
        window_width=800,
        window_height=800,
        target_fps=60,
        sim_dt=0.02
    )
    
    sim.run()


if __name__ == "__main__":
    main_waypoint()
