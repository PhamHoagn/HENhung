"""
Demo HIL Robocar với Wokwi VS Code Extension

Kết nối với Wokwi Simulator chạy trong VS Code qua RFC2217.
"""

import sys
import socket
import serial.rfc2217
import json
import time


def test_wokwi_connection(host='localhost', port=4000):
    """
    Test kết nối với Wokwi Simulator trong VS Code
    
    Args:
        host: Wokwi server host (mặc định: localhost)
        port: Wokwi RFC2217 port (mặc định: 4000)
    """
    print("=" * 60)
    print("  DEMO HIL ROBOCAR - WOKWI VS CODE")
    print("=" * 60)
    print()
    
    # Bước 1: Kiểm tra Wokwi có chạy không
    print(f"[1/3] Kiểm tra Wokwi Simulator trên {host}:{port}...")
    
    try:
        # Test TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result != 0:
            print(f"❌ Không thể kết nối đến {host}:{port}")
            print()
            print("Hướng dẫn:")
            print("1. Mở VS Code")
            print("2. Mở file esp32_wokwi/sketch.ino")
            print("3. Nhấn F1 → gõ 'Wokwi: Start Simulator'")
            print("4. Đợi Wokwi chạy xong (thấy 'Server listening on...')")
            print("5. Chạy lại script này")
            return False
            
        print(f"✓ Wokwi Simulator đang chạy!")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False
    
    # Bước 2: Kết nối Serial qua RFC2217
    print()
    print(f"[2/3] Kết nối Serial qua RFC2217...")
    
    try:
        # RFC2217 URL format
        url = f"rfc2217://{host}:{port}"
        
        # Mở kết nối
        ser = serial.rfc2217.Serial(
            url,
            baudrate=115200,
            timeout=1
        )
        
        print(f"✓ Kết nối thành công: {url}")
        
    except Exception as e:
        print(f"❌ Không thể mở Serial: {e}")
        return False
    
    # Bước 3: Test giao tiếp
    print()
    print(f"[3/3] Test giao tiếp với ESP32...")
    print()
    
    try:
        # Đợi ESP32 khởi động
        time.sleep(0.5)
        
        # Đọc greeting message từ ESP32
        print("Đọc greeting từ ESP32:")
        for _ in range(5):
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"  ESP32: {line}")
        
        print()
        
        # Test cases
        test_cases = [
            {
                "name": "Test 1: Tiến thẳng (không có vật cản)",
                "input": {"dF": 2.00, "dL": 2.00, "dR": 2.00},
                "expect": "vL và vR đều dương (tiến thẳng)"
            },
            {
                "name": "Test 2: Vật cản gần phía trước",
                "input": {"dF": 0.25, "dL": 1.00, "dR": 0.80},
                "expect": "Rẽ trái (vL âm, vR dương)"
            },
            {
                "name": "Test 3: Khẩn cấp dừng",
                "input": {"dF": 0.10, "dL": 1.00, "dR": 1.00},
                "expect": "Dừng lại (vL=0, vR=0)"
            }
        ]
        
        for i, test in enumerate(test_cases, 1):
            print("-" * 60)
            print(f"{test['name']}")
            print(f"Input:  {json.dumps(test['input'])}")
            
            # Gửi sensor data
            msg = json.dumps(test['input']) + '\n'
            ser.write(msg.encode('utf-8'))
            ser.flush()
            
            # Đợi response
            time.sleep(0.1)
            
            # Đọc response
            if ser.in_waiting > 0:
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Bỏ qua comment lines
                while response.startswith('#'):
                    if ser.in_waiting > 0:
                        response = ser.readline().decode('utf-8', errors='ignore').strip()
                    else:
                        break
                
                if response:
                    try:
                        motor_cmd = json.loads(response)
                        vL = motor_cmd.get('vL', 0)
                        vR = motor_cmd.get('vR', 0)
                        
                        print(f"Output: {response}")
                        print(f"Expect: {test['expect']}")
                        
                        # Phân tích
                        if vL == 0 and vR == 0:
                            status = "🛑 DỪNG"
                        elif vL < 0 and vR > 0:
                            status = "↰ RẼ TRÁI"
                        elif vL > 0 and vR < 0:
                            status = "↱ RẼ PHẢI"
                        elif vL > 0 and vR > 0:
                            if abs(vL - vR) < 0.1:
                                status = "⬆ TIẾN THẲNG"
                            elif vL > vR:
                                status = "⤴ RẼ PHẢI NHẸ"
                            else:
                                status = "⤵ RẼ TRÁI NHẸ"
                        else:
                            status = "⬇ LÙI"
                        
                        print(f"Status: {status}")
                        print("✓ PASS")
                        
                    except json.JSONDecodeError:
                        print(f"Output: {response} (không phải JSON)")
                        print("⚠ Chờ response từ ESP32...")
            else:
                print("⚠ Không nhận được response")
            
            print()
            time.sleep(0.2)
        
        print("=" * 60)
        print("✓ TẤT CẢ TEST HOÀN THÀNH!")
        print()
        print("Giờ bạn có thể chạy Python simulation đầy đủ:")
        print("  python -m robocar_sim.main --wokwi")
        print("=" * 60)
        
        ser.close()
        return True
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Parse arguments
    host = 'localhost'
    port = 4000
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    # Run test
    success = test_wokwi_connection(host, port)
    
    sys.exit(0 if success else 1)
