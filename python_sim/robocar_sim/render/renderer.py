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
        window_width: int = 1000,
        window_height: int = 1000,
        world_width: float = 12.0,
        world_height: float = 12.0,
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
        
        # Zoom & pan settings
        self.zoom = 1.0
        self.zoom_min = 0.4
        self.zoom_max = 3.0
        self.camera_x = 0.0   # world-space camera offset
        self.camera_y = 0.0
        
        # Calculate base scale (pixels per meter)
        self.base_scale_x = window_width / world_width
        self.base_scale_y = window_height / world_height
        self.scale_x = self.base_scale_x * self.zoom
        self.scale_y = self.base_scale_y * self.zoom
        
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
            'delete_last_waypoint': False,
            'clear_waypoints': False,
            'move_waypoint': None,
            'select_waypoint': None,
        }
        
        # Waypoint editing state
        self.selected_waypoint_index = None
        self.moving_waypoint_mode = False
        self.current_waypoints = None  # Cache for click detection

        # UI button layout - 2 rows
        button_y_top = window_height - 145
        button_y_bottom = window_height - 110
        
        self.button_rects = {
            # Top row
            'toggle_start': pygame.Rect(10, button_y_top, 110, 30),
            'reset': pygame.Rect(130, button_y_top, 100, 30),
            'toggle_waypoint_mode': pygame.Rect(240, button_y_top, 150, 30),
            # Bottom row (waypoint controls)
            'delete_last_waypoint': pygame.Rect(10, button_y_bottom, 120, 30),
            'clear_waypoints': pygame.Rect(140, button_y_bottom, 110, 30),
        }
    
    def _update_scale(self):
        """Recalculate scale after zoom change."""
        self.scale_x = self.base_scale_x * self.zoom
        self.scale_y = self.base_scale_y * self.zoom

    def world_to_screen(self, x: float, y: float) -> Tuple[int, int]:
        """
        Convert world coordinates (meters) to screen coordinates (pixels)
        Applies zoom and camera offset.
        """
        screen_x = int((x - self.camera_x) * self.scale_x)
        screen_y = int(self.window_height - (y - self.camera_y) * self.scale_y)
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
            sensor_rays: Tuple of 7 rays (center, L-near, R-near, L-mid, R-mid, L-far, R-far)
            is_collision: Whether car is in collision
            telemetry: Optional telemetry data for HUD
            waypoints: List of waypoint positions [(x,y), ...]
            current_waypoint_index: Index of current target waypoint
        """
        # Cache waypoints for click detection
        self.current_waypoints = waypoints
        
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
            
            # Highlight selected waypoint
            is_selected = (i == self.selected_waypoint_index)
            
            if i < current_index:
                # Waypoints đã đi qua - hình vuông nhỏ màu xám
                size = 10 if is_selected else 8
                rect = pygame.Rect(screen_pos[0] - size//2, screen_pos[1] - size//2, 
                                  size, size)
                color = Colors.ORANGE if is_selected else Colors.GRAY
                pygame.draw.rect(self.screen, color, rect, 3 if is_selected else 2)
                
            elif i == current_index:
                # Waypoint hiện tại (ĐÍCH) - hình tròn lớn màu vàng
                radius = 18 if is_selected else 15
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
                radius = 15 if is_selected else 12
                color = Colors.ORANGE if is_selected else Colors.GREEN
                pygame.draw.circle(self.screen, color, screen_pos, radius, 0)
                pygame.draw.circle(self.screen, Colors.WHITE, screen_pos, radius, 3 if is_selected else 2)
                
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
        """Draw 9 sensor rays: 7 forward cone + 2 side, color-coded by distance"""
        ray_center, ray_left_near, ray_right_near, ray_left_mid, ray_right_mid, ray_left_far, ray_right_far, ray_left_side, ray_right_side = sensor_rays
        
        # Define colors based on distance thresholds
        def get_ray_color(distance: float) -> Tuple[int, int, int]:
            if distance < 0.3:
                return Colors.RED      # Danger
            elif distance < 0.6:
                return Colors.ORANGE   # Warning
            elif distance < 1.0:
                return Colors.YELLOW   # Caution
            else:
                return Colors.GREEN    # Safe
        
        # Draw each ray (center is brightest/thickest, width decreases with angle)
        rays_with_width = [
            (ray_center, 3),          # Center - thickest
            (ray_left_near, 2),       # Near sensors
            (ray_right_near, 2),
            (ray_left_mid, 2),        # Mid sensors
            (ray_right_mid, 2),
            (ray_left_far, 1),        # Far sensors - thinnest
            (ray_right_far, 1),
            (ray_left_side, 2),       # Side sensors - medium
            (ray_right_side, 2)
        ]
        
        for ray, width in rays_with_width:
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
                    width
                )
                
                # Draw hit point (smaller for far sensors)
                point_radius = 4 if width == 3 else (3 if width == 2 else 2)
                pygame.draw.circle(
                    self.screen,
                    ray_color,
                    end_pos,
                    point_radius,
                    0
                )
    
    def _draw_hud(self, telemetry: dict, 
                  waypoints: Optional[List[Tuple[float, float]]] = None,
                  current_waypoint_index: int = 0):
        """Draw heads-up display with telemetry"""
        hud_x = 10
        hud_y = 10
        line_height = 18
        
        # Semi-transparent background with rounded corners
        hud_width = 340
        hud_height = 400 if waypoints else 320  # Increased for AI telemetry + 9 sensors
        hud_surface = pygame.Surface((hud_width, hud_height), pygame.SRCALPHA)
        pygame.draw.rect(hud_surface, (0, 0, 0, 220), (0, 0, hud_width, hud_height), border_radius=10)
        pygame.draw.rect(hud_surface, (100, 100, 100, 180), (0, 0, hud_width, hud_height), 2, border_radius=10)
        self.screen.blit(hud_surface, (hud_x, hud_y))
        
        # Render text lines with improved formatting
        dC = telemetry.get('dC', 0)       # Center
        dLN = telemetry.get('dLN', 0)     # Left near 15°
        dRN = telemetry.get('dRN', 0)     # Right near 15°
        dLM = telemetry.get('dLM', 0)     # Left mid 35°
        dRM = telemetry.get('dRM', 0)     # Right mid 35°
        dLF = telemetry.get('dLF', 0)     # Left far 60°
        dRF = telemetry.get('dRF', 0)     # Right far 60°
        dLS = telemetry.get('dLS', 0)     # Left side 90°
        dRS = telemetry.get('dRS', 0)     # Right side 90°
        
        lines = [
            ("🚗 4WD SKID-STEER + DT AI", Colors.YELLOW, True),
            ("", Colors.WHITE, False),
            (f"⏱ Time: {telemetry.get('time', 0.0):.1f}s | FPS: {self.actual_fps:.0f}", Colors.WHITE, False),
            (f"📍 Pos: ({telemetry.get('x', 0):.2f}, {telemetry.get('y', 0):.2f})m", Colors.WHITE, False),
            (f"🧭 Head: {math.degrees(telemetry.get('heading', 0)):.0f}°", Colors.WHITE, False),
            ("", Colors.WHITE, False),
            ("🔍 SENSORS (7 FWD + 2 SIDE):", Colors.BLUE, False),
        ]
        
        # Color-coded sensor readings
        def get_sensor_color(distance):
            if distance < 0.3:
                return Colors.RED
            elif distance < 0.5:
                return Colors.ORANGE
            elif distance < 0.8:
                return Colors.YELLOW
            else:
                return Colors.GREEN
        
        lines.append((f"  ⬆  Center:       {dC:.2f}m", get_sensor_color(dC), False))
        lines.append((f"  ↖  L-Near(15°):  {dLN:.2f}m", get_sensor_color(dLN), False))
        lines.append((f"  ↗  R-Near(15°):  {dRN:.2f}m", get_sensor_color(dRN), False))
        lines.append((f"  ⬅  L-Mid(35°):   {dLM:.2f}m", get_sensor_color(dLM), False))
        lines.append((f"  ➡  R-Mid(35°):   {dRM:.2f}m", get_sensor_color(dRM), False))
        lines.append((f"  ↙  L-Far(60°):   {dLF:.2f}m", get_sensor_color(dLF), False))
        lines.append((f"  ↘  R-Far(60°):   {dRF:.2f}m", get_sensor_color(dRF), False))
        lines.append((f"  ⇐  L-Side(90°): {dLS:.2f}m", get_sensor_color(dLS), False))
        lines.append((f"  ⇒  R-Side(90°): {dRS:.2f}m", get_sensor_color(dRS), False))
        
        # Add waypoint info if available
        if waypoints and len(waypoints) > 0:
            lines.append(("", Colors.WHITE, False))
            lines.append(("🎯 WAYPOINT NAV", Colors.GREEN, True))
            lines.append((f"  Point: {current_waypoint_index + 1}/{len(waypoints)}", Colors.WHITE, False))
            
            if current_waypoint_index < len(waypoints):
                wp = waypoints[current_waypoint_index]
                car_x = telemetry.get('x', 0)
                car_y = telemetry.get('y', 0)
                dist = math.sqrt((wp[0] - car_x)**2 + (wp[1] - car_y)**2)
                lines.append((f"  Target: ({wp[0]:.1f}, {wp[1]:.1f})", Colors.YELLOW, False))
                lines.append((f"  Dist: {dist:.2f}m", Colors.YELLOW, False))

        # Add AI telemetry from ESP32
        ai_action = telemetry.get('ai_action', -1)
        esp_mode = telemetry.get('esp_mode', '')
        ai_ms = telemetry.get('ai_ms', 0.0)
        if ai_action >= 0:
            action_names = {0: "FWD", 1: "FWD-L", 2: "FWD-R", 3: "TURN-L", 4: "TURN-R"}
            act_name = action_names.get(ai_action, f"?{ai_action}")
            lines.append(("", Colors.WHITE, False))
            lines.append(("🤖 ESP32 AI (Decision Tree)", Colors.ORANGE, True))
            lines.append((f"  Mode: {esp_mode}  Act: {act_name}", Colors.WHITE, False))
            lines.append((f"  AI infer: {ai_ms:.1f}ms", Colors.WHITE, False))

        lines.append(("", Colors.WHITE, False))
        lines.append(("⌨️  CONTROLS", Colors.PURPLE, True))
        lines.append(("  SPACE=Pause | R=Reset | M=Waypoint", Colors.LIGHT_GRAY, False))
        lines.append(("  BKSP=Del | Ctrl+C=Clear | ESC=Exit", Colors.LIGHT_GRAY, False))
        lines.append((f"  Scroll/+−=Zoom({self.zoom:.1f}x) | 0=Reset view", Colors.LIGHT_GRAY, False))
        
        # Render lines with proper formatting
        y_offset = 10
        for line_data in lines:
            if isinstance(line_data, tuple):
                text, color, is_header = line_data
                if text == "":
                    y_offset += line_height // 2
                    continue
                font = self.font_medium if is_header else self.font_small
                text_surface = font.render(text, True, color)
            else:
                # Fallback for old format
                text_surface = self.font_small.render(line_data, True, Colors.WHITE)
            
            self.screen.blit(text_surface, (hud_x + 15, hud_y + y_offset))
            y_offset += line_height
        
        # Serial status indicator with better styling
        serial_status = telemetry.get('serial_connected', False)
        status_color = Colors.GREEN if serial_status else Colors.ORANGE
        status_icon = "🔗" if serial_status else "🔌"
        status_text = "ESP32 DT-AI Connected" if serial_status else "No ESP32 (Safe-Stop)"
        
        # Background for status
        status_bg = pygame.Surface((200, 24), pygame.SRCALPHA)
        bg_color = (0, 100, 0, 180) if serial_status else (100, 50, 0, 180)
        pygame.draw.rect(status_bg, bg_color, (0, 0, 200, 24), border_radius=5)
        self.screen.blit(status_bg, (hud_x, self.window_height - 32))
        
        status_surface = self.font_small.render(
            f"{status_icon} {status_text}",
            True,
            status_color
        )
        self.screen.blit(status_surface, (hud_x + 8, self.window_height - 28))

    def _draw_control_panel(self, simulation_running: bool, waypoint_edit_mode: bool):
        """Draw bottom control buttons."""
        for action, rect in self.button_rects.items():
            if action == 'toggle_start':
                label = 'Pause' if simulation_running else 'Start'
                color = (80, 170, 80) if not simulation_running else (180, 140, 60)
            elif action == 'reset':
                label = 'Reset'
                color = (180, 80, 80)
            elif action == 'toggle_waypoint_mode':
                label = 'Set Waypoint'
                color = (90, 120, 190) if not waypoint_edit_mode else (210, 170, 70)
            elif action == 'delete_last_waypoint':
                label = 'Delete Last'
                color = (150, 70, 70)
            elif action == 'clear_waypoints':
                label = 'Clear All'
                color = (120, 60, 60)
            else:
                continue

            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, Colors.WHITE, rect, 2, border_radius=5)
            text = self.font_small.render(label, True, Colors.WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        # Hints
        hint_y = self.window_height - 74
        if waypoint_edit_mode:
            if self.selected_waypoint_index is not None:
                hint = self.font_small.render(
                    f"Waypoint #{self.selected_waypoint_index + 1} selected - Click to move, ESC to cancel", 
                    True, Colors.ORANGE
                )
            else:
                hint = self.font_small.render(
                    "Waypoint mode: Click map to add, Click waypoint to select/move", 
                    True, Colors.YELLOW
                )
            self.screen.blit(hint, (10, hint_y))

    def _screen_to_world(self, x: int, y: int) -> Tuple[float, float]:
        world_x = x / self.scale_x + self.camera_x
        world_y = (self.window_height - y) / self.scale_y + self.camera_y
        return world_x, world_y
    
    def _is_click_in_hud(self, x: int, y: int) -> bool:
        """Check if click is within HUD area"""
        # HUD area at top-left
        hud_area = pygame.Rect(10, 10, 320, 350)
        return hud_area.collidepoint(x, y)
    
    def _find_waypoint_at_position(self, x: int, y: int, waypoints: Optional[List[Tuple[float, float]]] = None) -> Optional[int]:
        """Find waypoint index at screen position (within click radius)"""
        if waypoints is None:
            waypoints = self.current_waypoints
        
        if not waypoints:
            return None
        
        world_pos = self._screen_to_world(x, y)
        click_radius = 20 / self.scale_x  # 20 pixels in world units
        
        for i, wp in enumerate(waypoints):
            dx = wp[0] - world_pos[0]
            dy = wp[1] - world_pos[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= click_radius:
                return i
        
        return None

    def consume_actions(self) -> dict:
        actions = self.button_actions.copy()
        self.button_actions = {
            'toggle_start': False,
            'reset': False,
            'toggle_waypoint_mode': False,
            'add_waypoint': None,
            'delete_last_waypoint': False,
            'clear_waypoints': False,
            'move_waypoint': None,
            'select_waypoint': None,
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
                    # Cancel waypoint selection or exit
                    if self.selected_waypoint_index is not None:
                        self.selected_waypoint_index = None
                        print("\n[Action] Hủy chọn waypoint")
                    else:
                        self.running = False
                        return False
                
                elif event.key == pygame.K_r:
                    # Reset simulation
                    self.button_actions['reset'] = True
                    print("\n[Button] Reset được nhấn")
                    
                elif event.key == pygame.K_SPACE:
                    # Toggle pause/start
                    self.button_actions['toggle_start'] = True
                    print("\n[Button] Pause/Start được nhấn")
                    
                elif event.key == pygame.K_m:
                    # Toggle waypoint edit mode
                    self.button_actions['toggle_waypoint_mode'] = True
                    print("\n[Button] Toggle Waypoint Mode được nhấn")
                
                elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    # Delete last waypoint
                    self.button_actions['delete_last_waypoint'] = True
                    print("\n[Button] Delete Last Waypoint được nhấn")
                
                elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Clear all waypoints (Ctrl+C)
                    self.button_actions['clear_waypoints'] = True
                    print("\n[Button] Clear All Waypoints được nhấn")

                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    # Zoom in
                    self.zoom = min(self.zoom * 1.2, self.zoom_max)
                    self._update_scale()
                
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    # Zoom out
                    self.zoom = max(self.zoom / 1.2, self.zoom_min)
                    self._update_scale()
                
                elif event.key == pygame.K_0:
                    # Reset zoom & camera
                    self.zoom = 1.0
                    self.camera_x = 0.0
                    self.camera_y = 0.0
                    self._update_scale()

            elif event.type == pygame.MOUSEWHEEL:
                # Mouse wheel zoom (centered on cursor)
                mx, my = pygame.mouse.get_pos()
                world_before = self._screen_to_world(mx, my)
                
                if event.y > 0:
                    self.zoom = min(self.zoom * 1.15, self.zoom_max)
                elif event.y < 0:
                    self.zoom = max(self.zoom / 1.15, self.zoom_min)
                self._update_scale()
                
                # Adjust camera so the point under cursor stays fixed
                world_after = self._screen_to_world(mx, my)
                self.camera_x += world_before[0] - world_after[0]
                self.camera_y += world_before[1] - world_after[1]

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                
                # Check if click is on a button
                clicked_button = False
                for action, rect in self.button_rects.items():
                    if rect.collidepoint(x, y):
                        self.button_actions[action] = True
                        clicked_button = True
                        
                        # Print feedback
                        button_names = {
                            'toggle_start': 'Pause/Start',
                            'reset': 'Reset',
                            'toggle_waypoint_mode': 'Set Waypoint Mode',
                            'delete_last_waypoint': 'Delete Last Waypoint',
                            'clear_waypoints': 'Clear All Waypoints'
                        }
                        print(f"\n[Button] {button_names.get(action, action)} được nhấn")
                        break
                
                # If not clicking on button and not in HUD area
                if not clicked_button and not self._is_click_in_hud(x, y):
                    # Store click position for waypoint operations
                    self.button_actions['select_waypoint'] = (x, y)
                    self.button_actions['add_waypoint'] = self._screen_to_world(x, y)

        return True
    
    def close(self):
        """Clean up and close pygame"""
        pygame.quit()
        print("✓ Renderer closed")
