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
from .sim.autopilot import SafeStopFallback
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
        world_width: float = 12.0,
        world_height: float = 12.0,
        window_width: int = 1000,
        window_height: int = 1000,
        target_fps: int = 60,
        sim_dt: float = 0.02
    ):
        print("═" * 60)
        print("  HIL ROBOCAR – 4WD SKID-STEER + DT AI")
        print("  Brain: ESP32 Decision-Tree  |  Plant: Python Sim")
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
            self.world.obstacles.clear_obstacles()
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
            print("⚠ WARNING: No ESP32 – Safe-stop fallback (no AI brain)")
            self.serial = None
        
        # Runtime state
        self.running = True
        self.simulation_running = True
        self.waypoint_edit_mode = False
        self.simulation_time = 0.0
        self.frame_count = 0
        self.start_pos = (car_x, car_y, car_heading)
        self.autopilot = SafeStopFallback()  # minimal safe-stop when ESP32 absent
        
        print("\n" + "═" * 60)
        print("  ✓ 4WD HIL SIMULATION READY")
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

                # Process user actions
                actions = self.renderer.consume_actions()
                
                # Toggle pause/start
                if actions.get('toggle_start'):
                    self.simulation_running = not self.simulation_running
                    status = "ĐANG CHẠY" if self.simulation_running else "TẠM DỪNG"
                    print(f"✓ Simulation: {status}")
                
                # Reset simulation
                if actions.get('reset'):
                    print("\n⟲ Đang reset simulation...")
                    self._reset_simulation()
                    print("✓ Đã reset về vị trí ban đầu\n")
                
                # Toggle waypoint edit mode
                if actions.get('toggle_waypoint_mode'):
                    self.waypoint_edit_mode = not self.waypoint_edit_mode
                    mode_status = "BẬT" if self.waypoint_edit_mode else "TẮT"
                    print(f"✓ Chế độ Set Waypoint: {mode_status}")
                    if self.waypoint_edit_mode:
                        print("  → Click vào map để thêm waypoint")
                        print("  → Click vào waypoint để chọn/di chuyển")
                    # Reset selection when exiting edit mode
                    if not self.waypoint_edit_mode:
                        self.renderer.selected_waypoint_index = None
                
                # Delete last waypoint
                if actions.get('delete_last_waypoint'):
                    self._delete_last_waypoint()
                
                # Clear all waypoints
                if actions.get('clear_waypoints'):
                    self._clear_all_waypoints()
                
                # Handle waypoint click operations (only in edit mode)
                if self.waypoint_edit_mode and actions.get('select_waypoint'):
                    screen_x, screen_y = actions['select_waypoint']
                    
                    # Check if clicking on existing waypoint (using cached waypoints in renderer)
                    clicked_wp_idx = self.renderer._find_waypoint_at_position(screen_x, screen_y)
                    
                    if clicked_wp_idx is not None:
                        # Clicking on waypoint
                        if self.renderer.selected_waypoint_index == clicked_wp_idx:
                            # Clicking same waypoint - deselect
                            self.renderer.selected_waypoint_index = None
                            print(f"✓ Đã bỏ chọn waypoint #{clicked_wp_idx + 1}")
                        elif self.renderer.selected_waypoint_index is not None:
                            # Different waypoint selected - move it to clicked position
                            old_idx = self.renderer.selected_waypoint_index
                            self._move_waypoint(old_idx, clicked_wp_idx)
                            self.renderer.selected_waypoint_index = None
                        else:
                            # Select waypoint
                            self.renderer.selected_waypoint_index = clicked_wp_idx
                            print(f"✓ Đã chọn waypoint #{clicked_wp_idx + 1}")
                            print("  → Click vị trí mới để di chuyển, hoặc click lại để bỏ chọn")
                    else:
                        # Not clicking on waypoint - add or move
                        if self.renderer.selected_waypoint_index is not None:
                            # Move selected waypoint to new position
                            wp_pos = actions['add_waypoint']
                            self._move_waypoint_to_position(
                                self.renderer.selected_waypoint_index, 
                                wp_pos
                            )
                            self.renderer.selected_waypoint_index = None
                        else:
                            # Add new waypoint
                            wp_pos = actions['add_waypoint']
                            if self._add_waypoint(wp_pos):
                                wp_count = len(self.waypoint_navigator.waypoints) if self.waypoint_navigator else 1
                                print(f"✓ Đã thêm waypoint #{wp_count} tại ({wp_pos[0]:.2f}, {wp_pos[1]:.2f})")
                
                # Time step
                current_time = time.time()
                real_dt = current_time - last_sim_time
                last_sim_time = current_time
                dt = self.sim_dt
                
                # Get sensor data (9 sensors: 7 forward cone + 2 side)
                sensor_data = self.world.get_sensor_data()
                dC, dLN, dRN, dLM, dRM, dLF, dRF, dLS, dRS = sensor_data
                
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
                    # Gửi sensor + waypoint info + car position
                    if self.waypoint_navigator:
                        current_wp = self.waypoint_navigator.get_current_waypoint()
                        if current_wp:
                            wx, wy = current_wp
                            # Send enhanced data with position (9 sensors)
                            self.serial.send_sensor_data(
                                dC, dLN, dRN, dLM, dRM, dLF, dRF, dLS, dRS,
                                wx, wy, car_heading, car_x, car_y
                            )
                        else:
                            self.serial.send_sensor_data(dC, dLN, dRN, dLM, dRM, dLF, dRF, dLS, dRS)
                    else:
                        self.serial.send_sensor_data(dC, dLN, dRN, dLM, dRM, dLF, dRF, dLS, dRS)
                    
                    serial_connected = True
                
                # Receive motor commands
                motor_commands = None
                if self.serial and self.serial.is_connected:
                    motor_commands = self.serial.receive_motor_commands()

                # Fallback safe-stop if ESP32 is not connected.
                # The ESP32 is the SOLE autonomous brain; Python only
                # provides a minimal creep / stop for debugging visibility.
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
                    'dC': dC,        # Center sensor
                    'dLN': dLN,      # Left near (15°)
                    'dRN': dRN,      # Right near (15°)
                    'dLM': dLM,      # Left mid (35°)
                    'dRM': dRM,      # Right mid (35°)
                    'dLF': dLF,      # Left far (60°)
                    'dRF': dRF,      # Right far (60°)
                    'dLS': dLS,      # Left side (90°)
                    'dRS': dRS,      # Right side (90°)
                    'serial_connected': serial_connected,
                }

                # Attach AI telemetry from the last ESP32 response
                if self.serial and self.serial.last_motor_response:
                    resp = self.serial.last_motor_response
                    telemetry['esp_mode'] = resp.mode
                    telemetry['ai_action'] = resp.ai_action
                    telemetry['ai_speed'] = resp.ai_speed
                    telemetry['ai_ms'] = resp.ai_ms
                
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
                
                # Collision detection — push car back instead of full reset
                # so the ESP32 / fallback can use its recovery logic
                if self.world.is_crashed():
                    self._collision_count = getattr(self, '_collision_count', 0) + 1
                    if self._collision_count == 1:
                        print(f"\n⚠ VA CHẠM tại t={self.simulation_time:.2f}s — pushing back")
                    # Push car backwards along its heading to escape collision
                    cx, cy = car_state['position']
                    push = 0.12  # push back 12 cm
                    new_x = cx - push * math.cos(car_heading)
                    new_y = cy - push * math.sin(car_heading)
                    self.world.car.state.x = max(0.3, min(self.world.width - 0.3, new_x))
                    self.world.car.state.y = max(0.3, min(self.world.height - 0.3, new_y))
                    self.world.is_collision = False
                    # Hard reset only after 30 consecutive collision frames
                    if self._collision_count >= 30:
                        print(f"  ⚠ Stuck! Full reset.\n")
                        self.world.reset(*self.start_pos)
                        if self.waypoint_navigator:
                            self.waypoint_navigator.reset()
                        self.autopilot.reset()
                        self._collision_count = 0
                else:
                    self._collision_count = 0
                
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

    # Minimum safe distance from walls and obstacles for waypoint placement
    WAYPOINT_WALL_MARGIN = 0.80   # metres from map edge
    WAYPOINT_OBS_MARGIN  = 0.50   # metres clearance from obstacle surface

    def _is_waypoint_safe(self, wx: float, wy: float) -> Tuple[bool, str]:
        """Check if a waypoint position is safe (not too close to walls/obstacles)."""
        # Hard bounds: must be inside the map
        if wx < 0 or wx > self.world.width or wy < 0 or wy > self.world.height:
            return False, "Ngoài giới hạn map"
        
        margin = self.WAYPOINT_WALL_MARGIN
        if wx < margin or wx > self.world.width - margin:
            return False, f"Quá gần giới hạn map ngang (cần ≥{margin}m)"
        if wy < margin or wy > self.world.height - margin:
            return False, f"Quá gần giới hạn map dọc (cần ≥{margin}m)"
        
        for obs in self.world.obstacles.get_obstacles():
            ox, oy = obs.position
            dist = math.sqrt((wx - ox)**2 + (wy - oy)**2)
            min_dist = obs.radius + self.WAYPOINT_OBS_MARGIN
            if dist < min_dist:
                return False, f"Quá gần vật cản tại ({ox:.1f},{oy:.1f}), cần ≥{min_dist:.2f}m (hiện {dist:.2f}m)"
        
        return True, ""

    def _add_waypoint(self, waypoint: Tuple[float, float]) -> bool:
        """Append waypoint from UI click — validate distance from walls & obstacles.
        Returns True if waypoint was added successfully."""
        wx, wy = waypoint[0], waypoint[1]
        
        # Validate placement
        safe, reason = self._is_waypoint_safe(wx, wy)
        if not safe:
            print(f"⚠ Không thể đặt waypoint: {reason}")
            return False

        if self.waypoint_navigator is None:
            self.waypoint_navigator = WaypointNavigator(
                waypoints=[(wx, wy)],
                reach_radius=0.3,
                loop=True,
            )
            print(f"  → Khởi tạo WaypointNavigator với waypoint đầu tiên")
        else:
            self.waypoint_navigator.waypoints.append((wx, wy))
        return True
    
    def _delete_last_waypoint(self):
        """Delete the last waypoint from the list."""
        if self.waypoint_navigator and len(self.waypoint_navigator.waypoints) > 0:
            deleted_wp = self.waypoint_navigator.waypoints.pop()
            print(f"✓ Đã xóa waypoint cuối cùng: ({deleted_wp[0]:.2f}, {deleted_wp[1]:.2f})")
            print(f"  → Còn lại {len(self.waypoint_navigator.waypoints)} waypoint(s)")
            
            # Clear navigator if no waypoints left
            if len(self.waypoint_navigator.waypoints) == 0:
                self.waypoint_navigator = None
                print("  → Không còn waypoint nào")
            
            # Reset selection
            self.renderer.selected_waypoint_index = None
        else:
            print("⚠ Không có waypoint nào để xóa")
    
    def _clear_all_waypoints(self):
        """Clear all waypoints."""
        if self.waypoint_navigator and len(self.waypoint_navigator.waypoints) > 0:
            count = len(self.waypoint_navigator.waypoints)
            self.waypoint_navigator = None
            self.renderer.selected_waypoint_index = None
            print(f"✓ Đã xóa tất cả {count} waypoint(s)")
        else:
            print("⚠ Không có waypoint nào để xóa")
    
    def _move_waypoint(self, from_index: int, to_index: int):
        """Swap two waypoints in the list."""
        if not self.waypoint_navigator or len(self.waypoint_navigator.waypoints) <= max(from_index, to_index):
            return
        
        # Swap waypoints
        waypoints = self.waypoint_navigator.waypoints
        waypoints[from_index], waypoints[to_index] = waypoints[to_index], waypoints[from_index]
        
        print(f"✓ Đã hoán đổi waypoint #{from_index + 1} và #{to_index + 1}")
    
    def _move_waypoint_to_position(self, index: int, new_position: Tuple[float, float]):
        """Move a waypoint to a new position — validate distance from walls & obstacles."""
        if not self.waypoint_navigator or index >= len(self.waypoint_navigator.waypoints):
            return
        
        wx, wy = new_position[0], new_position[1]
        
        safe, reason = self._is_waypoint_safe(wx, wy)
        if not safe:
            print(f"⚠ Không thể di chuyển waypoint: {reason}")
            return
        
        old_pos = self.waypoint_navigator.waypoints[index]
        self.waypoint_navigator.waypoints[index] = (wx, wy)
        
        print(f"✓ Đã di chuyển waypoint #{index + 1}")
        print(f"  Từ: ({old_pos[0]:.2f}, {old_pos[1]:.2f})")
        print(f"  Đến: ({wx:.2f}, {wy:.2f})")


def main_waypoint():
    """Entry point for waypoint navigation"""
    import argparse
    parser = argparse.ArgumentParser(description="HIL Robocar 4WD Simulation")
    parser.add_argument("--port", type=str, default=None,
                        help="COM port for ESP32 (e.g. COM7). Default: auto-detect")
    parser.add_argument("--scenario", type=str, default=None,
                        help="Path to scenario YAML file")
    args, _ = parser.parse_known_args()

    # Get scenario file
    scenario_file = args.scenario or os.environ.get('SCENARIO_FILE')
    if not scenario_file:
        # Default scenario
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scenario_file = os.path.join(script_dir, 'scenarios', 'demo_waypoints.yaml')

    serial_port = args.port or os.environ.get('SERIAL_PORT')
    
    # Create simulation
    sim = HILRobocarWaypointSimulation(
        serial_port=serial_port,
        scenario_file=scenario_file,
        world_width=12.0,
        world_height=12.0,
        window_width=1000,
        window_height=1000,
        target_fps=60,
        sim_dt=0.02
    )
    
    sim.run()


if __name__ == "__main__":
    main_waypoint()
