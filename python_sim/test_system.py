#!/usr/bin/env python3
"""
HIL Robocar - System Verification Test
Tests all components before running the full simulation
"""

import sys
import subprocess


def test_python_version():
    """Test Python version"""
    print("Testing Python version...", end=" ")
    if sys.version_info < (3, 10):
        print("❌ FAILED")
        print(f"  Current: Python {sys.version_info.major}.{sys.version_info.minor}")
        print(f"  Required: Python 3.10+")
        return False
    print(f"✓ OK (Python {sys.version_info.major}.{sys.version_info.minor})")
    return True


def test_dependencies():
    """Test required Python packages"""
    print("\nTesting Python dependencies...")
    
    required = {
        'pygame': '2.5.0',
        'serial': '3.5',  # pyserial
        'yaml': '6.0'     # pyyaml
    }
    
    all_ok = True
    
    for module_name, min_version in required.items():
        try:
            if module_name == 'serial':
                import serial
                print(f"  ✓ pyserial: {serial.VERSION}")
            elif module_name == 'yaml':
                import yaml
                print(f"  ✓ pyyaml: installed")
            elif module_name == 'pygame':
                import pygame
                print(f"  ✓ pygame: {pygame.version.ver}")
        except ImportError:
            print(f"  ❌ {module_name}: NOT FOUND")
            all_ok = False
    
    return all_ok


def test_imports():
    """Test project imports"""
    print("\nTesting project modules...")
    
    modules = [
        'robocar_sim.main',
        'robocar_sim.sim.world',
        'robocar_sim.sim.physics',
        'robocar_sim.sim.sensors',
        'robocar_sim.io.serial_bridge',
        'robocar_sim.io.protocol',
        'robocar_sim.render.renderer'
    ]
    
    all_ok = True
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            all_ok = False
    
    return all_ok


def test_serial_ports():
    """List available serial ports"""
    print("\nDetecting serial ports...")
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            print("  ⚠ No serial ports detected")
            print("  Note: This is OK if you haven't started Wokwi yet")
        else:
            print(f"  Found {len(ports)} port(s):")
            for port in ports:
                print(f"    • {port.device}: {port.description}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    return True


def test_file_structure():
    """Test critical files exist"""
    print("\nChecking file structure...")
    
    import os
    
    critical_files = [
        'robocar_sim/main.py',
        'robocar_sim/sim/world.py',
        'robocar_sim/sim/physics.py',
        'robocar_sim/sim/sensors.py',
        'robocar_sim/io/serial_bridge.py',
        'robocar_sim/render/renderer.py',
        'requirements.txt'
    ]
    
    all_ok = True
    for file in critical_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file}: NOT FOUND")
            all_ok = False
    
    return all_ok


def main():
    """Run all tests"""
    print("=" * 60)
    print("  HIL ROBOCAR - SYSTEM VERIFICATION TEST")
    print("=" * 60)
    
    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_dependencies),
        ("Project Modules", test_imports),
        ("Serial Ports", test_serial_ports),
        ("File Structure", test_file_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print("=" * 60)
    print(f"  Result: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - System ready!")
        print("\nNext steps:")
        print("  1. Start Wokwi ESP32 simulation")
        print("  2. Run: python -m robocar_sim.main")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please fix issues above")
        print("\nTo install dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
