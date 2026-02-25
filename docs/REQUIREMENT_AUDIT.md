# Requirement Audit - Robocar 4 bánh (ESP32 mô phỏng)

## Cập nhật theo phản hồi mới

Phản hồi: **"không có phần cứng chỉ có esp32 thôi"**.

Vì vậy bản này được chuẩn hoá thành **ESP32-only simulation mode**:
- Không phụ thuộc phần cứng ngoài (L298N, HC-SR04, motor).
- Vẫn giữ đầy đủ kiến trúc module, state machine, `GOTO x y`, điều hướng + tránh vật cản theo dữ liệu mô phỏng.

## Trạng thái đáp ứng yêu cầu

| Hạng mục yêu cầu | Trạng thái hiện tại |
|---|---|
| Setup đích đến + bắt đầu di chuyển | Có `GOTO x y`, `START`, `STOP` |
| Kiến trúc module | Có đầy đủ `motor/sensor/navigation/obstacle/main` |
| State machine | Có `IDLE/NAVIGATING/AVOIDING/ARRIVED` |
| Chạy mô phỏng không phần cứng | Có, dùng Serial command `POSE` + `SENSOR` |
| Wokwi diagram | Chỉ ESP32 + Serial monitor |
| Python serial test | Có `python_sim/send_goto.py` |

## Ghi chú kỹ thuật

- `motor_control` giữ API điều khiển bánh xe nhưng hoạt động virtual (không GPIO).
- `sensor` luôn đọc từ giá trị mô phỏng (`SENSOR dF dS`) để phù hợp chế độ ESP32-only.
- Nếu cần mở rộng về phần cứng thật sau này, có thể bật lại phần GPIO mà không đổi kiến trúc module.
