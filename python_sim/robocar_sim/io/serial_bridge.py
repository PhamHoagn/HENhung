"""
HIL Robocar - Serial Bridge
Non-blocking serial communication with ESP32 (Wokwi)
"""

import serial
import serial.tools.list_ports
import time
from typing import Optional, Tuple, List
from .protocol import SerialProtocol


class SerialBridge:
    """
    Non-blocking serial bridge for HIL communication
    
    Handles:
    - Connection to ESP32 (Wokwi virtual port or physical COM port)
    - Non-blocking read/write operations
    - Timeout management
    - Automatic reconnection
    """
    
    def __init__(
        self,
        port: Optional[str] = None,
        baudrate: int = 115200,
        timeout: float = 0.05  # 50ms timeout
    ):
        """
        Initialize serial bridge
        
        Args:
            port: COM port name (e.g., "COM3"). If None, will auto-detect.
            baudrate: Serial baud rate (must match ESP32 firmware)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: Optional[serial.Serial] = None
        self.protocol = SerialProtocol()
        self.is_connected = False
        
        # Statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.messages_sent = 0
        self.messages_received = 0
        self.last_receive_time = 0.0
    
    def connect(self, auto_detect: bool = True) -> bool:
        """
        Connect to ESP32 via serial port
        
        Args:
            auto_detect: If True and port is None, automatically detect ESP32
        
        Returns:
            True if connection successful
        """
        if self.is_connected:
            return True
        
        # Auto-detect port if not specified
        if self.port is None and auto_detect:
            self.port = self._detect_esp32_port()
            if self.port is None:
                print("ERROR: Could not auto-detect ESP32 port")
                return False
        
        if self.port is None:
            print("ERROR: No serial port specified")
            return False
        
        try:
            # Open serial connection
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                write_timeout=self.timeout
            )
            
            # Wait for connection to stabilize
            time.sleep(0.5)
            
            # Clear any pending data
            self.serial_conn.reset_input_buffer()
            self.serial_conn.reset_output_buffer()
            
            self.is_connected = True
            print(f"✓ Connected to ESP32 on {self.port} @ {self.baudrate} baud")
            
            # Send greeting
            greeting = self.protocol.create_comment("Python Simulator Connected")
            self.serial_conn.write(greeting.encode('utf-8'))
            
            return True
        
        except serial.SerialException as e:
            print(f"ERROR: Failed to connect to {self.port}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.close()
            except:
                pass
        
        self.is_connected = False
        print("✓ Serial connection closed")
    
    def send_sensor_data(
        self,
        d_center: float,
        d_left_near: float,
        d_right_near: float,
        d_left_mid: float,
        d_right_mid: float,
        d_left_far: float,
        d_right_far: float,
        d_left_side: float,
        d_right_side: float,
        waypoint_x: Optional[float] = None,
        waypoint_y: Optional[float] = None,
        car_heading: Optional[float] = None,
        car_x: Optional[float] = None,
        car_y: Optional[float] = None
    ) -> bool:
        """
        Send sensor data (9 sensors: 7 forward + 2 side) and optionally waypoint + position info to ESP32
        
        Args:
            d_center, d_left_near, d_right_near, d_left_mid, d_right_mid, 
            d_left_far, d_right_far: Forward cone sensor distances in meters
            d_left_side, d_right_side: Side sensor (±90°) distances in meters
            waypoint_x, waypoint_y: Target waypoint coordinates (optional)
            car_heading: Car heading in radians (optional)
            car_x, car_y: Car position in meters (optional)
        
        Returns:
            True if sent successfully
        """
        if not self.is_connected or not self.serial_conn:
            return False
        
        try:
            # Encode sensor data as JSON (with or without waypoint)
            if waypoint_x is not None and waypoint_y is not None and car_heading is not None:
                # Enhanced message with waypoint and position
                json_str = self.protocol.encode_sensor_data_with_waypoint(
                    d_center, d_left_near, d_right_near, d_left_mid, d_right_mid,
                    d_left_far, d_right_far, d_left_side, d_right_side,
                    waypoint_x, waypoint_y, car_heading,
                    car_x if car_x is not None else 0.0,
                    car_y if car_y is not None else 0.0
                )
            else:
                # Basic sensor data only
                json_str = self.protocol.encode_sensor_data(
                    d_center, d_left_near, d_right_near, d_left_mid, d_right_mid,
                    d_left_far, d_right_far, d_left_side, d_right_side
                )
            
            # Send to ESP32
            data_bytes = json_str.encode('utf-8')
            self.serial_conn.write(data_bytes)
            
            # Update statistics
            self.bytes_sent += len(data_bytes)
            self.messages_sent += 1
            
            return True
        
        except serial.SerialException as e:
            print(f"ERROR: Failed to send data: {e}")
            self.is_connected = False
            return False
    
    def receive_motor_commands(self) -> Optional[Tuple[float, float]]:
        """
        Receive motor commands from ESP32 (non-blocking)
        
        Returns:
            (v_left, v_right) or None if no valid data available
        """
        if not self.is_connected or not self.serial_conn:
            return None
        
        try:
            # Check if data available
            if self.serial_conn.in_waiting == 0:
                return None
            
            # Read one line (until '\n')
            line = self.serial_conn.readline().decode('utf-8', errors='ignore')
            
            if not line:
                return None
            
            # Update statistics
            self.bytes_received += len(line)
            self.last_receive_time = time.time()
            
            # Decode motor commands
            motor_cmds = self.protocol.decode_motor_commands(line)
            
            if motor_cmds is not None:
                self.messages_received += 1
            
            return motor_cmds
        
        except serial.SerialException as e:
            print(f"ERROR: Failed to receive data: {e}")
            self.is_connected = False
            return None
        except Exception as e:
            # Ignore other errors (malformed data, etc.)
            return None
    
    def check_connection_alive(self, timeout: float = 0.5) -> bool:
        """
        Check if connection is still alive
        
        Args:
            timeout: Maximum time since last receive (seconds)
        
        Returns:
            True if connection appears alive
        """
        if not self.is_connected:
            return False
        
        # Check if we've received data recently
        time_since_receive = time.time() - self.last_receive_time
        
        if time_since_receive > timeout and self.messages_received == 0:
            # No data received yet - connection may not be established
            return False
        
        return True
    
    def get_statistics(self) -> dict:
        """Get communication statistics"""
        return {
            'port': self.port,
            'connected': self.is_connected,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received
        }
    
    def _detect_esp32_port(self) -> Optional[str]:
        """
        Auto-detect ESP32 COM port
        
        Returns:
            Port name or None if not found
        """
        ports = serial.tools.list_ports.comports()
        
        # Look for common ESP32 identifiers
        esp32_keywords = [
            'USB-SERIAL',
            'CP210',
            'CH340',
            'UART',
            'Silicon Labs',
            'USB Serial'
        ]
        
        for port in ports:
            port_desc = (port.description or "").upper()
            port_mfr = (port.manufacturer or "").upper()
            
            for keyword in esp32_keywords:
                if keyword.upper() in port_desc or keyword.upper() in port_mfr:
                    print(f"✓ Auto-detected ESP32 on {port.device}: {port.description}")
                    return port.device
        
        # If auto-detect fails, list available ports
        print("Available COM ports:")
        for port in ports:
            print(f"  - {port.device}: {port.description}")
        
        return None
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
