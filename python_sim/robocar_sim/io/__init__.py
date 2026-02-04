"""IO module for serial communication"""

from .serial_bridge import SerialBridge
from .protocol import SerialProtocol

__all__ = ['SerialBridge', 'SerialProtocol']
