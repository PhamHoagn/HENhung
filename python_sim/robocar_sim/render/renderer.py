"""
HIL Robocar - Pygame Renderer
2D top-down visualization of the simulation
"""

import pygame
import math
from typing import Tuple, List, Optional


class Colors:
    """Color palette for rendering"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (50, 50, 50)
    RED = (255, 50, 50)
    GREEN = (50, 255, 50)
    BLUE = (50, 150, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    PURPLE = (200, 50, 200)


class SimulationRenderer:
    """
    2D top-down renderer for HIL Robocar simulation
    
    Renders:
    - Robot car with heading indicator
    - Obstacles
    - Sensor rays (color-coded by distance)
    - Grid background
    - HUD with telemetry
    """
    
    def __init__(
        self,
        window_width: int = 800,
        window_height: int = 800,
        world_width: float = 5.0,
        world_height: float = 5.0,
        target_fps: int = 60
    ):
        """
        Initialize pygame renderer
        
        Args:
            window_width, window_height: Window size in pixels
            world_width, world_height: World size in meters
            target_fps: Target frames per second
        """
        # Initialize pygame
        pygame.init()
        
        # Window settings
        self.window_width = window_width
        self.window_height = window_height
        self.screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("HIL Robocar Simulation")
        
        # World settings
        self.world_width = world_width
        self.world_height = world_height
        
        # Calculate scale (pixels per meter)
        self.scale_x = window_width / world_width
        self.scale_y = window_height / world_height
        
        # FPS control
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.actual_fps = 0
        
        # Fonts
        self.font_small = pygame.font.SysFont('Courier New', 14, bold=True)
        self.font_medium = pygame.font.SysFont('Courier New', 18, bold=True)
        self.font_large = pygame.font.SysFont('Courier New', 24, bold=True)
        
        # Runtime state
        self.running = True
        self.button_actions = {
            'toggle_start': False,
            'reset': False,
            'toggle_waypoint_mode': False,
            'add_waypoint': None,
        }

        # UI button layout
        self.button_rects = {
            'toggle_start': pygame.Rect(10, window_height - 115, 110, 32),
            'reset': pygame.Rect(130, window_height - 115, 100, 32),
            'toggle_waypoint_mode': pygame.Rect(240, window_height - 115, 170, 32),
        }
    
    def world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert world coordinates (meters) to screen coordinates (pixels)
        
        Args:
            x, y: Position in meters
        
        Returns:
            (screen_x, screen_y) in pixels
        """
        screen_x = int(x * self.scale_x)
        screen_y = int(self.window_height - y * self.scale_y)  # Flip Y axis
        return (screen_x, screen_y)
    
    def render_frame(
        self,
        car_pos: Tuple[float, float],
        car_heading: float,
        obstacles: List,
        sensor_rays: Tuple,
        is_collision: bool = False,
        telemetry: Optional[dict] = None,
        waypoints: Optional[List[Tuple[float, float]]] = None,
        current_waypoint_index: int = 0,
        simulation_running: bool = True,
        waypoint_edit_mode: bool = False,
    ):
        """
        Render a complete frame
        
        Args:
            car_pos: Car position (x, y) in meters
            car_heading: Car heading in radians
            obstacles: List of Obstacle objects
            sensor_rays: Tuple of (ray_front, ray_left, ray_right)
            is_collision: Whether car is in collision
            telemetry: Optional telemetry data for HUD
            waypoints: List of waypoint positions [(x,y), ...]
            current_waypoint_index: Index of current target waypoint
        """
        # Clear screen
        self.screen.fill(Colors.DARK_GRAY)
        
        # Draw grid
        self._draw_grid()
        
        # Draw waypoints and path (BEFORE obstacles so they're behind)
        if waypoints and len(waypoints) > 0:
            self._draw_waypoints(waypoints, current_waypoint_index, car_pos)
        
        # Draw obstacles
        self._draw_obstacles(obstacles)
        
        # Draw sensor rays
        self._draw_sensor_rays(sensor_rays)
        
        # Draw car
        self._draw_car(car_pos, car_heading, is_collision)
        
        # Draw HUD
        if telemetry:
            self._draw_hud(telemetry, waypoints, current_waypoint_index)

        self._draw_control_panel(simulation_running, waypoint_edit_mode)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        self.actual_fps = self.clock.get_fps()
        self.clock.tick(self.target_fps)
    
    def _draw_grid(self):
        """Draw background grid"""
        grid_spacing_meters = 0.5  # Grid every 0.5 meters
        
        # Vertical lines
        x_meters = 0.0
        while x_meters <= self.world_width:
            screen_x, _ = self.world_to_screen(x_meters, 0)
            pygame.draw.line(
                self.screen,
                Colors.GRAY,
                (screen_x, 0),
                (screen_x, self.window_height),
                1
            )
            x_meters += grid_spacing_meters
        
        # Horizontal lines
        y_meters = 0.0
        while y_meters <= self.world_height:
            _, screen_y = self.world_to_screen(0, y_meters)
            pygame.draw.line(
                self.screen,
                Colors.GRAY,
                (0, screen_y),
                (self.window_width, screen_y),
                1
            )
            y_meters += grid_spacing_meters
    
    def _draw_car(
        self,
        pos: Tuple[float, float],
        heading: float,
        is_collision: bool
    ):
        """Draw a 4-wheel car with heading indicator"""
        screen_pos = self.world_to_screen(pos[0], pos[1])
        car_length = int(0.34 * self.scale_x)
        car_width = int(0.2 * self.scale_x)
        wheel_length = max(8, int(car_length * 0.24))
        wheel_width = max(4, int(car_width * 0.24))
        car_color = Colors.RED if is_collision else Colors.BLUE

        def transform(local_x: float, local_y: float) -> Tuple[int, int]:
            cos_h = math.cos(heading)
            sin_h = math.sin(heading)
            world_x = screen_pos[0] + local_x * cos_h - local_y * sin_h
            world_y = screen_pos[1] - (local_x * sin_h + local_y * cos_h)
            return int(world_x), int(world_y)

        # Main body polygon
        body_points = [
            transform(car_length / 2, car_width / 2),
            transform(car_length / 2, -car_width / 2),
            transform(-car_length / 2, -car_width / 2),
            transform(-car_length / 2, car_width / 2),
        ]
        pygame.draw.polygon(self.screen, car_color, body_points)
        pygame.draw.polygon(self.screen, Colors.WHITE, body_points, 2)

        # Wheel polygons (4 wheels)
        wheel_offsets = [
            (car_length * 0.28, car_width * 0.58),
            (car_length * 0.28, -car_width * 0.58),
            (-car_length * 0.28, car_width * 0.58),
            (-car_length * 0.28, -car_width * 0.58),
        ]
        for cx, cy in wheel_offsets:
            wheel_poly = [
                transform(cx + wheel_length / 2, cy + wheel_width / 2),
                transform(cx + wheel_length / 2, cy - wheel_width / 2),
                transform(cx - wheel_length / 2, cy - wheel_width / 2),
                transform(cx - wheel_length / 2, cy + wheel_width / 2),
            ]
            pygame.draw.polygon(self.screen, Colors.BLACK, wheel_poly)
            pygame.draw.polygon(self.screen, Colors.LIGHT_GRAY, wheel_poly, 1)

        # Heading indicator
        indicator_length = car_length * 0.65
        end_x = screen_pos[0] + indicator_length * math.cos(heading)
        end_y = screen_pos[1] - indicator_length * math.sin(heading)
        pygame.draw.line(
            self.screen,
            Colors.YELLOW,
            screen_pos,
            (int(end_x), int(end_y)),
            3
        )
    
    def _draw_obstacles(self, obstacles: List):
        """Draw circular obstacles"""
        for obstacle in obstacles:
            screen_pos = self.world_to_screen(
                obstacle.position[0],
                obstacle.position[1]
            )
            radius_pixels = int(obstacle.radius * self.scale_x)
            
            # Filled circle
            pygame.draw.circle(
                self.screen,
                Colors.LIGHT_GRAY,
                screen_pos,
                radius_pixels,
                0
            )
            
            # Outline
            pygame.draw.circle(
                self.screen,
                Colors.WHITE,
                screen_pos,
                radius_pixels,
                2
            )
    
    def _draw_waypoints(self, waypoints: List[Tuple[float, float]], 
                       current_index: int, car_pos: Tuple[float, float]):
        """
        Vẽ waypoints và đường đi
        
        Args:
            waypoints: List of (x, y) waypoint positions
            current_index: Index of current target waypoint
            car_pos: Current car position (x, y)
        """
        if not waypoints or len(waypoints) == 0:
            return
        
        # 1. Vẽ đường nối giữa các waypoints (lộ trình)
        if len(waypoints) > 1:
            for i in range(len(waypoints) - 1):
                start_pos = self.world_to_screen(waypoints[i][0], waypoints[i][1])
                end_pos = self.world_to_screen(waypoints[i+1][0], waypoints[i+1][1])
                
                # Đường đi đã qua (màu xám)
                if i < current_index:
                    pygame.draw.line(self.screen, Colors.GRAY, start_pos, end_pos, 3)
                # Đường đi sắp tới (màu xanh lá)
                else:
                    pygame.draw.line(self.screen, Colors.GREEN, start_pos, end_pos, 3)
        
        # 2. Vẽ đường từ xe đến waypoint hiện tại (màu vàng nét đứt)
        if current_index < len(waypoints):
            car_screen = self.world_to_screen(car_pos[0], car_pos[1])
            wp_screen = self.world_to_screen(waypoints[current_index][0], 
                                            waypoints[current_index][1])
            
            # Vẽ nét đứt
            self._draw_dashed_line(car_screen, wp_screen, Colors.YELLOW, 2, 10)
        
        # 3. Vẽ các waypoints
        for i, wp in enumerate(waypoints):
            screen_pos = self.world_to_screen(wp[0], wp[1])
            
            if i < current_index:
                # Waypoints đã đi qua - hình vuông nhỏ màu xám
                size = 8
                rect = pygame.Rect(screen_pos[0] - size//2, screen_pos[1] - size//2, 
                                  size, size)
                pygame.draw.rect(self.screen, Colors.GRAY, rect, 2)
                
            elif i == current_index:
                # Waypoint hiện tại (ĐÍCH) - hình tròn lớn màu vàng, nhấp nháy
                radius = 15
                # Vẽ viền ngoài lớn
                pygame.draw.circle(self.screen, Colors.YELLOW, screen_pos, radius, 3)
                # Vẽ viền trong
                pygame.draw.circle(self.screen, Colors.YELLOW, screen_pos, radius - 5, 2)
                # Vẽ chữ "ĐÍCH"
                text = self.font_medium.render("ĐÍCH", True, Colors.YELLOW)
                text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 30))
                # Nền đen cho chữ
                bg_rect = text_rect.inflate(10, 5)
                pygame.draw.rect(self.screen, Colors.BLACK, bg_rect)
                pygame.draw.rect(self.screen, Colors.YELLOW, bg_rect, 2)
                self.screen.blit(text, text_rect)
                
            else:
                # Waypoints sắp tới - hình tròn màu xanh lá
                radius = 12
                pygame.draw.circle(self.screen, Colors.GREEN, screen_pos, radius, 0)
                pygame.draw.circle(self.screen, Colors.WHITE, screen_pos, radius, 2)
                
            # Số thứ tự waypoint
            if i != current_index:  # Không vẽ số cho waypoint hiện tại (đã có chữ ĐÍCH)
                num_text = self.font_small.render(str(i + 1), True, Colors.WHITE)
                num_rect = num_text.get_rect(center=screen_pos)
                self.screen.blit(num_text, num_rect)
    
    def _draw_dashed_line(self, start, end, color, width, dash_length):
        """Vẽ đường nét đứt"""
        x1, y1 = start
        x2, y2 = end
        
        # Tính toán độ dài và hướng
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
        
        # Normalize direction
        dx /= distance
        dy /= distance
        
        # Vẽ các đoạn nét đứt
        current_length = 0
        while current_length < distance:
            # Điểm bắt đầu đoạn
            start_x = x1 + dx * current_length
            start_y = y1 + dy * current_length
            
            # Điểm kết thúc đoạn
            end_length = min(current_length + dash_length, distance)
            end_x = x1 + dx * end_length
            end_y = y1 + dy * end_length
            
            pygame.draw.line(self.screen, color, 
                           (int(start_x), int(start_y)), 
                           (int(end_x), int(end_y)), width)
            
            # Nhảy qua khoảng trống
            current_length += dash_length * 2
    
    def _draw_sensor_rays(self, sensor_rays: Tuple):
        """Draw sensor rays color-coded by distance"""
        ray_front, ray_left, ray_right = sensor_rays
        
        # Define colors based on distance thresholds
        def get_ray_color(distance: float) -> Tuple[int, int, int]:
            if distance < 0.3:
                return Colors.RED      # Danger
            elif distance < 0.6:
                return Colors.ORANGE   # Warning
            else:
                return Colors.GREEN    # Safe
        
        # Draw each ray
        for ray in [ray_front, ray_left, ray_right]:
            if ray.hit_point:
                # Ray origin to hit point
                start_pos = self.world_to_screen(ray.origin[0], ray.origin[1])
                end_pos = self.world_to_screen(ray.hit_point[0], ray.hit_point[1])
                
                ray_color = get_ray_color(ray.hit_distance)
                
                # Draw ray line
                pygame.draw.line(
                    self.screen,
                    ray_color,
                    start_pos,
                    end_pos,
                    2
                )
                
                # Draw hit point
                pygame.draw.circle(
                    self.screen,
                    ray_color,
                    end_pos,
                    4,
                    0
                )
    
    def _draw_hud(self, telemetry: dict, 
                  waypoints: Optional[List[Tuple[float, float]]] = None,
                  current_waypoint_index: int = 0):
        """Draw heads-up display with telemetry"""
        hud_x = 10
        hud_y = 10
        line_height = 20
        
        # Semi-transparent background
        hud_width = 320
        hud_height = 320 if waypoints else 240
        hud_surface = pygame.Surface((hud_width, hud_height))
        hud_surface.set_alpha(200)
        hud_surface.fill(Colors.BLACK)
        self.screen.blit(hud_surface, (hud_x, hud_y))
        
        # Render text lines
        lines = [
            f"HIL ROBOCAR SIMULATION",
            f"─────────────────────────────",
            f"FPS: {self.actual_fps:.1f}",
            f"Time: {telemetry.get('time', 0.0):.1f}s",
            f"",
            f"Position: ({telemetry.get('x', 0):.2f}, {telemetry.get('y', 0):.2f})",
            f"Heading: {math.degrees(telemetry.get('heading', 0)):.1f}°",
            f"",
            f"Sensors (m):",
            f"  Front: {telemetry.get('dF', 0):.2f}",
            f"  Left:  {telemetry.get('dL', 0):.2f}",
            f"  Right: {telemetry.get('dR', 0):.2f}",
        ]
        
        # Add waypoint info if available
        if waypoints and len(waypoints) > 0:
            lines.append("")
            lines.append("═══ WAYPOINT NAVIGATION ═══")
            lines.append(f"Điểm hiện tại: {current_waypoint_index + 1}/{len(waypoints)}")
            
            if current_waypoint_index < len(waypoints):
                wp = waypoints[current_waypoint_index]
                lines.append(f"Đích: ({wp[0]:.1f}, {wp[1]:.1f})")
                
                # Tính khoảng cách đến đích
                car_x = telemetry.get('x', 0)
                car_y = telemetry.get('y', 0)
                dist = math.sqrt((wp[0] - car_x)**2 + (wp[1] - car_y)**2)
                lines.append(f"Khoảng cách: {dist:.2f}m")

        lines.append("")
        lines.append("Phím tắt: SPACE(start/pause), R(reset), M(set waypoint)")
        
        for i, line in enumerate(lines):
            if i == 0:
                text_surface = self.font_medium.render(line, True, Colors.YELLOW)
            elif "═══" in line:
                text_surface = self.font_small.render(line, True, Colors.GREEN)
            else:
                text_surface = self.font_small.render(line, True, Colors.WHITE)
            
            self.screen.blit(text_surface, (hud_x + 10, hud_y + 10 + i * line_height))
        
        # Serial status indicator
        serial_status = telemetry.get('serial_connected', False)
        status_color = Colors.GREEN if serial_status else Colors.RED
        status_text = "CONNECTED" if serial_status else "DISCONNECTED"
        
        status_surface = self.font_small.render(
            f"ESP32: {status_text}",
            True,
            status_color
        )
        self.screen.blit(status_surface, (hud_x + 10, self.window_height - 30))

    def _draw_control_panel(self, simulation_running: bool, waypoint_edit_mode: bool):
        """Draw bottom control buttons."""
        for action, rect in self.button_rects.items():
            if action == 'toggle_start':
                label = 'Pause' if simulation_running else 'Start'
                color = (80, 170, 80) if not simulation_running else (180, 140, 60)
            elif action == 'reset':
                label = 'Reset'
                color = (180, 80, 80)
            else:
                label = 'Set Waypoint'
                color = (90, 120, 190) if not waypoint_edit_mode else (210, 170, 70)

            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, Colors.WHITE, rect, 2, border_radius=6)
            text = self.font_small.render(label, True, Colors.WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        if waypoint_edit_mode:
            hint = self.font_small.render(
                "Waypoint mode: click map to add point", True, Colors.YELLOW
            )
            self.screen.blit(hint, (10, self.window_height - 74))

    def _screen_to_world(self, x: int, y: int) -> Tuple[float, float]:
        world_x = x / self.scale_x
        world_y = (self.window_height - y) / self.scale_y
        return world_x, world_y

    def consume_actions(self) -> dict:
        actions = self.button_actions.copy()
        self.button_actions = {
            'toggle_start': False,
            'reset': False,
            'toggle_waypoint_mode': False,
            'add_waypoint': None,
        }
        return actions
    
    def handle_events(self) -> bool:
        """
        Handle pygame events
        
        Returns:
            True if should continue running, False if quit requested
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
                
                elif event.key == pygame.K_r:
                    self.button_actions['reset'] = True
                elif event.key == pygame.K_SPACE:
                    self.button_actions['toggle_start'] = True
                elif event.key == pygame.K_m:
                    self.button_actions['toggle_waypoint_mode'] = True

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                for action, rect in self.button_rects.items():
                    if rect.collidepoint(x, y):
                        self.button_actions[action] = True
                        break
                else:
                    self.button_actions['add_waypoint'] = self._screen_to_world(x, y)

        return True
    
    def close(self):
        """Clean up and close pygame"""
        pygame.quit()
        print("✓ Renderer closed")
