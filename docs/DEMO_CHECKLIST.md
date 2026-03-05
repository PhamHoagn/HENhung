# Checklist Demo / Báo Cáo

Checklist chuẩn bị demo và báo cáo môn Hệ Nhúng – Robocar 4 bánh tự hành.

---

## Trước Buổi Demo (1 ngày)

### Kiểm tra phần mềm
- [ ] Python 3.10+ đã cài đặt
- [ ] Dependencies đã cài: `pip install pygame pyserial pyyaml scikit-learn`
- [ ] Wokwi account hoạt động
- [ ] ESP32 firmware compile OK trên Wokwi (không lỗi)
- [ ] Python simulation chạy được: `python -m robocar_sim.main_waypoint`
- [ ] Kết nối Serial ESP32 ↔ Python thành công

### Test hệ thống
- [ ] Xe di chuyển tự động theo waypoints
- [ ] Obstacle avoidance hoạt động (xe tránh vật cản)
- [ ] HUD hiển thị đúng: mode, speed, waypoint progress
- [ ] 9 sensor rays hiển thị (mã màu xanh/vàng/cam/đỏ)
- [ ] Không có crash/hang trong 2 phút chạy liên tục
- [ ] Quay video backup phòng trường hợp demo live lỗi

### Chuẩn bị tài liệu
- [ ] Báo cáo đồ án in sẵn
- [ ] Slide trình bày (nếu cần)
- [ ] Source code có sẵn trên laptop

---

## Ngày Demo

### Setup (trước 15 phút)
1. Mở laptop, kết nối internet
2. Mở terminal tại `python_sim/`
3. Mở Wokwi → load project ESP32
4. Upload firmware: `sketch_improved.ino` + `decision_tree_model.h`
5. Thêm thư viện ArduinoJson
6. Click "Start Simulation" trên Wokwi
7. Chạy: `python -m robocar_sim.main_waypoint`
8. Kiểm tra HUD hiện "ESP32: CONNECTED"

### Trình bày (10–15 phút)

#### Phần 1: Giới thiệu (2–3 phút)
- Đề tài: Robocar 4 bánh tự hành, waypoint navigation, obstacle avoidance
- Kiến trúc HIL: ESP32 (Brain) ↔ Python (Plant)
- Điểm nổi bật: Decision-Tree AI nhúng, FreeRTOS dual-core

#### Phần 2: Demo Live (5–7 phút)
- Khởi động hệ thống (nếu chưa chạy)
- Giải thích cửa sổ pygame:
  - Robot 4WD + 4 bánh
  - 9 tia sensor (mã màu theo khoảng cách)
  - Waypoint path + markers
  - HUD panel (mode, speed, AI action, waypoint progress)
- Quan sát xe:
  - Di chuyển theo waypoints (FOLLOW mode)
  - Phát hiện vật cản → chuyển AVOID mode
  - Emergency stop khi quá gần (STOP mode)
  - Hoàn thành tất cả waypoints

#### Phần 3: Kỹ thuật (2–3 phút)
- Decision Tree: trained offline → export C header → ESP32
- FreeRTOS: Core 0 (AI @ 5 Hz) + Core 1 (Control @ 50 Hz)
- 9-sensor array: 7 trước (120° FOV) + 2 bên (90°)
- Serial JSON protocol @ 115200 baud
- Safety-first: STOP/REVERSE override khi front < 0.40m

#### Phần 4: Q&A (2–3 phút)

---

## Câu Hỏi Thường Gặp (Q&A)

### Q: Tại sao dùng HIL thay vì phần cứng thật?
**A:** HIL cho phép phát triển và test nhanh hơn, tiết kiệm chi phí. Kiến trúc module cho phép chuyển sang hardware thật mà không đổi firmware. ESP32 firmware là code nhúng thật, không phải simulation.

### Q: Decision Tree có đủ thông minh không? Sao không dùng Deep Learning?
**A:** DT phù hợp embedded systems vì: inference nhanh (< 1ms trên ESP32), không cần ML library, code size nhỏ (C if/else), và đạt 83% accuracy. Deep Learning cần nhiều tài nguyên hơn khả năng ESP32.

### Q: Làm sao ESP32 biết đường đi?
**A:** Python gửi waypoint hiện tại `(wpX, wpY)` + robot position `(x, y, th)` qua serial. ESP32 tính heading error và blend với DT avoidance output.

### Q: Xe có thể chạy offline không?
**A:** ESP32 firmware tự động safe-stop nếu mất kết nối serial > 250ms. Trong thực tế, nếu gắn sensor thật, ESP32 có thể chạy standalone với DT AI.

### Q: 9 sensors bố trí như nào?
**A:** 7 sensors hướng trước trong cone 120° FOV (0°, ±15°, ±35°, ±60°) + 2 sensors hướng ngang (±90°). Cho phép phát hiện vật cản ở nhiều góc khác nhau.

### Q: Tại sao có 4 behavior modes?
**A:** Safety-first design: FOLLOW (bình thường), AVOID (vật cản gần), STOP (nguy hiểm), RECOVERY (bị kẹt). Mỗi mode có chiến lược khác nhau đảm bảo an toàn.

---

## Troubleshooting Khi Demo

| Vấn Đề | Giải Pháp Nhanh |
|---------|-----------------|
| Wokwi không chạy | Refresh browser, check internet |
| Serial không kết nối | Restart Wokwi simulation, kiểm tra COM port |
| Xe đứng yên | Check HUD: "ESP32: CONNECTED", restart Wokwi |
| Pygame crash | `pip install --upgrade pygame` |
| Lag/chậm | Đóng tabs browser khác, đóng apps nặng |
| **Backup plan** | Chiếu video đã quay sẵn |
