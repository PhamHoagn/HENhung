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
        telemetry: Optional[dict] = None
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
        """
        # Clear screen
        self.screen.fill(Colors.DARK_GRAY)
        
        # Draw grid
        self._draw_grid()
        
        # Draw obstacles
        self._draw_obstacles(obstacles)
        
        # Draw sensor rays
        self._draw_sensor_rays(sensor_rays)
        
        # Draw car
        self._draw_car(car_pos, car_heading, is_collision)
        
        # Draw HUD
        if telemetry:
            self._draw_hud(telemetry)
        
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
        """Draw robot car with heading indicator"""
        screen_pos = self.world_to_screen(pos[0], pos[1])
        
        # Car body (circle)
        car_radius_pixels = int(0.15 * self.scale_x)  # 15cm robot radius
        car_color = Colors.RED if is_collision else Colors.BLUE
        
        pygame.draw.circle(
            self.screen,
            car_color,
            screen_pos,
            car_radius_pixels,
            0  # Filled
        )
        
        # Heading indicator (line from center)
        indicator_length = car_radius_pixels * 1.5
        end_x = screen_pos[0] + indicator_length * math.cos(heading)
        end_y = screen_pos[1] - indicator_length * math.sin(heading)  # Flip Y
        
        pygame.draw.line(
            self.screen,
            Colors.YELLOW,
            screen_pos,
            (int(end_x), int(end_y)),
            3
        )
        
        # Car outline
        pygame.draw.circle(
            self.screen,
            Colors.WHITE,
            screen_pos,
            car_radius_pixels,
            2  # Outline only
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
    
    def _draw_hud(self, telemetry: dict):
        """Draw heads-up display with telemetry"""
        hud_x = 10
        hud_y = 10
        line_height = 20
        
        # Semi-transparent background
        hud_width = 300
        hud_height = 200
        hud_surface = pygame.Surface((hud_width, hud_height))
        hud_surface.set_alpha(200)
        hud_surface.fill(Colors.BLACK)
        self.screen.blit(hud_surface, (hud_x, hud_y))
        
        # Render text lines
        lines = [
            f"HIL ROBOCAR SIMULATION",
            f"─────────────────────────",
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
        
        for i, line in enumerate(lines):
            if i == 0:
                text_surface = self.font_medium.render(line, True, Colors.YELLOW)
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
                    # Reset signal (handled by main loop)
                    pass
        
        return True
    
    def close(self):
        """Clean up and close pygame"""
        pygame.quit()
        print("✓ Renderer closed")
