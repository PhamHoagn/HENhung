"""
HIL RobotCar - Waypoint Navigation Demo

Chạy simulation với waypoint navigation + obstacle avoidance
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from robocar_sim.main_waypoint import main_waypoint
import yaml


def load_scenario(scenario_file):
    """Load scenario from YAML file"""
    with open(scenario_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def run_waypoint_demo():
    """
    Chạy demo với waypoint navigation
    
    Sử dụng file: scenarios/demo_waypoints.yaml
    """
    print("=" * 70)
    print("  HIL ROBOCAR - WAYPOINT NAVIGATION DEMO")
    print("=" * 70)
    print()
    print("Chế độ: Di chuyển theo lộ trình + Né vật cản")
    print()
    print("Điều khiển:")
    print("  ESC   - Thoát")
    print("  R     - Reset về điểm bắt đầu")
    print("  SPACE - Pause/Resume")
    print("  W     - Chuyển waypoint tiếp theo (manual)")
    print()
    print("=" * 70)
    print()
    
    # Load scenario
    scenario_path = os.path.join(
        os.path.dirname(__file__),
        'robocar_sim', 'scenarios', 'demo_waypoints.yaml'
    )
    
    if os.path.exists(scenario_path):
        scenario = load_scenario(scenario_path)
        print(f"✓ Loaded scenario: {scenario.get('name', 'Unknown')}")
        print(f"  {scenario.get('description', '')}")
        print(f"  Waypoints: {len(scenario.get('waypoints', []))}")
        print()
    
    # Set scenario file
    os.environ['SCENARIO_FILE'] = scenario_path
    
    # Run waypoint navigation
    main_waypoint()


if __name__ == "__main__":
    run_waypoint_demo()
