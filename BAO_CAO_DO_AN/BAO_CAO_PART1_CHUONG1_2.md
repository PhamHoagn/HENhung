# BÁO CÁO ĐỒ ÁN MÔN HỆ NHÚNG

---

## TRANG BÌA

---

<div align="center">

**BỘ GIÁO DỤC VÀ ĐÀO TẠO**

**[ĐIỀN TÊN TRƯỜNG]**

**KHOA CÔNG NGHỆ THÔNG TIN**

---

*[Logo trường]*

---

### BÁO CÁO ĐỒ ÁN MÔN HỌC

## HỆ NHÚNG

---

### Đề tài:

# THIẾT KẾ VÀ MÔ PHỎNG ROBOCAR 4 BÁNH TỰ HÀNH THEO LỘ TRÌNH ĐỊNH TRƯỚC, TRÁNH VẬT CẢN THÔNG MINH SỬ DỤNG AI NHÚNG

---

**Giảng viên hướng dẫn:** [ĐIỀN TÊN GIẢNG VIÊN]

**Nhóm:** 10

**Lớp:** Hệ Nhúng 1-2-25-N02

**Thành viên nhóm:**

| STT | Họ và tên | MSSV |
|-----|-----------|------|
| 1 | [ĐIỀN TÊN 1] | [ĐIỀN MSSV] |
| 2 | [ĐIỀN TÊN 2] | [ĐIỀN MSSV] |
| 3 | [ĐIỀN TÊN 3] | [ĐIỀN MSSV] |
| 4 | [ĐIỀN TÊN 4] | [ĐIỀN MSSV] |

---

**TP. Hồ Chí Minh, năm 2025**

</div>

---

## LỜI CẢM ƠN

Đề tài "Thiết kế và mô phỏng Robocar 4 bánh tự hành theo lộ trình định trước, tránh vật cản thông minh sử dụng AI nhúng" được thực hiện trong khuôn khổ môn học Hệ Nhúng, học kỳ 2 năm học 2024–2025.

Trước hết, nhóm xin gửi lời cảm ơn chân thành đến [ĐIỀN TÊN GIẢNG VIÊN] – giảng viên hướng dẫn môn Hệ Nhúng – đã tận tình giảng dạy, định hướng và hỗ trợ nhóm trong suốt quá trình thực hiện đồ án. Những kiến thức nền tảng về hệ thống nhúng, vi điều khiển và lập trình thời gian thực mà thầy/cô truyền đạt là cơ sở quan trọng để nhóm hoàn thành đề tài này.

Nhóm cũng xin cảm ơn quý thầy cô trong Khoa Công nghệ Thông tin đã tạo điều kiện về cơ sở vật chất và môi trường học tập thuận lợi.

Cuối cùng, nhóm xin cảm ơn các bạn sinh viên cùng lớp đã đóng góp ý kiến và hỗ trợ trong quá trình kiểm thử, đánh giá hệ thống.

Do thời gian và kiến thức còn hạn chế, báo cáo không tránh khỏi những thiếu sót. Nhóm rất mong nhận được sự góp ý từ quý thầy cô và các bạn để hoàn thiện hơn.

**TP. Hồ Chí Minh, tháng 6 năm 2025**

**Nhóm 10**

---

## MỤC LỤC

- LỜI CẢM ƠN
- MỤC LỤC
- DANH MỤC HÌNH ẢNH
- DANH MỤC BẢNG BIỂU
- DANH MỤC TỪ VIẾT TẮT
- **CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI**
  - 1.1 Đặt vấn đề
  - 1.2 Mục tiêu đề tài
  - 1.3 Phạm vi và giới hạn
  - 1.4 Phương pháp nghiên cứu
  - 1.5 Bố cục báo cáo
- **CHƯƠNG 2: CƠ SỞ LÝ THUYẾT**
  - 2.1 Tổng quan về hệ thống nhúng
  - 2.2 Vi điều khiển ESP32
  - 2.3 Động học Robot – Mô hình Skid-Steer 4 bánh
  - 2.4 Cảm biến siêu âm và mô phỏng Raycast
  - 2.5 Trí tuệ nhân tạo nhúng (Embedded AI)
  - 2.6 Phương pháp HIL (Hardware-in-the-Loop)
  - 2.7 Giao thức truyền thông Serial
  - 2.8 Điều hướng Waypoint
- **CHƯƠNG 3: THIẾT KẾ HỆ THỐNG**
  - 3.1 Kiến trúc tổng quan hệ thống HIL
  - 3.2 Thiết kế module ESP32 Controller
  - 3.3 Thiết kế module Python Simulator
  - 3.4 Thiết kế giao thức truyền thông
  - 3.5 Thiết kế pipeline huấn luyện AI
  - 3.6 Thiết kế thuật toán tránh vật cản thông minh
  - 3.7 Sơ đồ luồng dữ liệu
  - 3.8 Thiết kế scenario (YAML)
- **CHƯƠNG 4: TRIỂN KHAI**
  - 4.1 Môi trường phát triển
  - 4.2 Cấu trúc thư mục dự án
  - 4.3 Triển khai ESP32 Firmware
  - 4.4 Triển khai Python Simulator
  - 4.5 Triển khai AI Training Pipeline
  - 4.6 Cách chạy hệ thống
- **CHƯƠNG 5: KẾT QUẢ VÀ ĐÁNH GIÁ**
  - 5.1 Kết quả mô phỏng
  - 5.2 Đánh giá hiệu năng
  - 5.3 So sánh các phương pháp AI
  - 5.4 Phân tích ưu/nhược điểm
  - 5.5 Kết quả kiểm thử
- **CHƯƠNG 6: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN**
  - 6.1 Kết luận
  - 6.2 Đóng góp của đề tài
  - 6.3 Hướng phát triển
- TÀI LIỆU THAM KHẢO
- PHỤ LỤC

---

## DANH MỤC HÌNH ẢNH

| STT | Hình | Mô tả | Trang |
|-----|------|--------|-------|
| 1 | Hình 1.1 | Robot tự hành Amazon Kiva trong kho hàng | |
| 2 | Hình 1.2 | Sơ đồ phương pháp HIL trong phát triển hệ thống nhúng | |
| 3 | Hình 1.3 | Quy trình phát triển tổng quan của đề tài | |
| 4 | Hình 2.1 | Kiến trúc tổng quan vi điều khiển ESP32 | |
| 5 | Hình 2.2 | Sơ đồ khối chức năng ESP32-DevKitC | |
| 6 | Hình 2.3 | Mô hình 4WD Skid-Steer Differential Drive | |
| 7 | Hình 2.4 | Phương trình động học unicycle approximation | |
| 8 | Hình 2.5 | Nguyên lý hoạt động cảm biến siêu âm HC-SR04 | |
| 9 | Hình 2.6 | Bố trí mảng 9 cảm biến trên robot | |
| 10 | Hình 2.7 | Thuật toán raycast – giao điểm tia với đường tròn | |
| 11 | Hình 2.8 | Cấu trúc cây quyết định (Decision Tree) | |
| 12 | Hình 2.9 | So sánh các phương pháp AI trên vi điều khiển | |
| 13 | Hình 2.10 | Các cấp độ mô phỏng: MIL → SIL → HIL → Field Testing | |
| 14 | Hình 2.11 | Khung truyền dữ liệu UART | |
| 15 | Hình 2.12 | Minh họa heading error trong waypoint navigation | |

---

## DANH MỤC BẢNG BIỂU

| STT | Bảng | Mô tả | Trang |
|-----|------|--------|-------|
| 1 | Bảng 2.1 | Thông số kỹ thuật vi điều khiển ESP32-WROOM-32 | |
| 2 | Bảng 2.2 | Thông số hình học robot 4WD Skid-Steer | |
| 3 | Bảng 2.3 | Cấu hình mảng 9 cảm biến siêu âm | |
| 4 | Bảng 2.4 | So sánh các phương pháp AI trên vi điều khiển nhúng | |
| 5 | Bảng 2.5 | So sánh các phương pháp mô phỏng trong phát triển hệ thống nhúng | |

---

## DANH MỤC TỪ VIẾT TẮT

| Từ viết tắt | Tiếng Anh | Tiếng Việt |
|-------------|-----------|------------|
| AI | Artificial Intelligence | Trí tuệ nhân tạo |
| DT | Decision Tree | Cây quyết định |
| EMA | Exponential Moving Average | Trung bình động hàm mũ |
| ESP | Espressif Systems Platform | Nền tảng Espressif |
| FPS | Frames Per Second | Khung hình trên giây |
| GPIO | General Purpose Input/Output | Cổng vào/ra đa năng |
| HIL | Hardware-in-the-Loop | Phần cứng trong vòng lặp |
| HUD | Head-Up Display | Màn hình hiển thị thông tin |
| I2C | Inter-Integrated Circuit | Giao tiếp liên mạch tích hợp |
| IoT | Internet of Things | Internet vạn vật |
| JSON | JavaScript Object Notation | Ký pháp đối tượng JavaScript |
| MAE | Mean Absolute Error | Sai số tuyệt đối trung bình |
| MIL | Model-in-the-Loop | Mô hình trong vòng lặp |
| PD | Proportional-Derivative | Tỉ lệ - Đạo hàm |
| RTOS | Real-Time Operating System | Hệ điều hành thời gian thực |
| SIL | Software-in-the-Loop | Phần mềm trong vòng lặp |
| SLAM | Simultaneous Localization and Mapping | Định vị và lập bản đồ đồng thời |
| SPI | Serial Peripheral Interface | Giao diện ngoại vi nối tiếp |
| SRAM | Static Random-Access Memory | Bộ nhớ truy cập ngẫu nhiên tĩnh |
| UART | Universal Asynchronous Receiver-Transmitter | Bộ thu phát không đồng bộ vạn năng |
| 4WD | Four-Wheel Drive | Dẫn động bốn bánh |

---

<div style="page-break-before: always;"></div>

# CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI

## 1.1 Đặt vấn đề

### 1.1.1 Bối cảnh và xu hướng phát triển

Trong bối cảnh cuộc cách mạng công nghiệp lần thứ tư (Industry 4.0), robot tự hành (autonomous mobile robot – AMR) đã trở thành một trong những lĩnh vực nghiên cứu và ứng dụng quan trọng nhất của hệ thống nhúng (embedded systems) và Internet vạn vật (IoT). Theo báo cáo của MarketsandMarkets [1], thị trường robot tự hành toàn cầu được dự báo đạt giá trị 13,52 tỷ USD vào năm 2026, với tốc độ tăng trưởng kép hàng năm (CAGR) đạt 19,6%.

Robot tự hành được ứng dụng rộng rãi trong nhiều lĩnh vực khác nhau. Trong lĩnh vực logistics, các hệ thống robot Kiva của Amazon đã được triển khai tại hơn 200 trung tâm phân phối trên toàn cầu, giúp giảm 20% chi phí vận hành và tăng 50% năng suất xử lý đơn hàng [2]. Trong lĩnh vực giao hàng, các startup như Nuro và Starship Technologies đã triển khai xe giao hàng tự lái trên đường phố thực tế. Trong lĩnh vực nông nghiệp, robot tự hành được sử dụng cho việc gieo trồng, phun thuốc và thu hoạch tự động.

[Hình 1.1: Robot tự hành Amazon Kiva trong kho hàng – minh họa ứng dụng thực tế của robot tự hành trong logistics]

### 1.1.2 Thách thức kỹ thuật

Việc phát triển robot tự hành đặt ra nhiều thách thức kỹ thuật đáng kể, đặc biệt khi triển khai trên các vi điều khiển có tài nguyên hạn chế:

**Xử lý thời gian thực (real-time processing):** Robot phải thu thập dữ liệu cảm biến, đưa ra quyết định và thực thi hành động trong khoảng thời gian cực ngắn (thường dưới 20 ms cho mỗi chu kỳ điều khiển) [3]. Bất kỳ độ trễ nào vượt quá ngưỡng cho phép đều có thể dẫn đến va chạm hoặc mất kiểm soát.

**Tài nguyên vi điều khiển hạn hẹp:** Các vi điều khiển nhúng như ESP32, mặc dù sở hữu bộ xử lý dual-core tốc độ 240 MHz, chỉ có 520 KB SRAM và 4 MB Flash [4]. Điều này giới hạn nghiêm trọng khả năng triển khai các mô hình trí tuệ nhân tạo (AI) vốn thường yêu cầu hàng chục đến hàng trăm MB bộ nhớ.

**Tích hợp đa module phức tạp:** Một hệ thống robot tự hành đầy đủ bao gồm nhiều module chức năng: cảm biến (perception), ra quyết định (decision making), điều khiển (control) và truyền thông (communication). Việc tích hợp các module này hoạt động đồng bộ, ổn định trên một nền tảng nhúng đòi hỏi kiến trúc phần mềm được thiết kế cẩn thận.

**Chi phí phát triển và kiểm thử:** Việc phát triển và kiểm thử trực tiếp trên phần cứng thật tốn kém cả về thời gian và chi phí. Mỗi lần thay đổi thuật toán đòi hỏi phải nạp lại firmware, kết nối phần cứng và thực hiện test thực tế – một quy trình có thể mất hàng giờ cho mỗi vòng lặp phát triển.

### 1.1.3 Phương pháp HIL – Giải pháp cho phát triển hệ thống nhúng

Để giải quyết các thách thức trên, phương pháp Hardware-in-the-Loop (HIL) simulation đã được áp dụng rộng rãi trong ngành công nghiệp ô tô, hàng không vũ trụ và robot [5]. HIL là phương pháp mô phỏng trong đó bộ điều khiển thực (real controller) được kết nối với mô hình mô phỏng ảo (virtual plant), cho phép kiểm thử phần mềm nhúng trong môi trường giả lập an toàn nhưng vẫn giữ được tính chân thực của phần cứng điều khiển.

[Hình 1.2: Sơ đồ phương pháp HIL trong phát triển hệ thống nhúng – Controller thực (ESP32) kết nối với Plant ảo (Python Simulator) qua giao tiếp Serial]

Phương pháp HIL mang lại nhiều ưu điểm vượt trội:

- **Giảm chi phí:** Không cần chế tạo robot vật lý trong giai đoạn phát triển thuật toán.
- **Tăng tốc độ phát triển:** Có thể chạy hàng trăm kịch bản test tự động mà không lo hỏng phần cứng.
- **An toàn:** Kiểm thử các tình huống nguy hiểm (va chạm, mất kiểm soát) mà không gây thiệt hại thực tế.
- **Tái tạo lỗi:** Dễ dàng tái tạo và debug các tình huống lỗi cụ thể.
- **Tính chân thực:** Firmware chạy trên vi điều khiển thực, đảm bảo timing và behavior giống với triển khai thực tế.

Xuất phát từ bối cảnh và nhu cầu thực tiễn nêu trên, đề tài **"Thiết kế và mô phỏng Robocar 4 bánh tự hành theo lộ trình định trước, tránh vật cản thông minh sử dụng AI nhúng"** được thực hiện nhằm xây dựng một hệ thống HIL hoàn chỉnh, trong đó firmware AI nhúng chạy trên vi điều khiển ESP32 thực, kết hợp với bộ mô phỏng vật lý 2D viết bằng Python.

---

## 1.2 Mục tiêu đề tài

Đề tài đặt ra các mục tiêu cụ thể sau đây:

### 1.2.1 Mục tiêu tổng quát

Thiết kế và triển khai một hệ thống mô phỏng HIL hoàn chỉnh cho robocar 4 bánh tự hành, tích hợp trí tuệ nhân tạo nhúng trên vi điều khiển ESP32, có khả năng điều hướng theo lộ trình định trước (waypoint navigation) và tránh vật cản thông minh (obstacle avoidance).

### 1.2.2 Mục tiêu cụ thể

**Mục tiêu 1 – Kiến trúc hệ thống HIL:** Thiết kế kiến trúc hệ thống HIL với sự tách biệt rõ ràng giữa bộ điều khiển (ESP32 Controller) và mô hình mô phỏng (Python Plant), giao tiếp thông qua giao thức Serial JSON ở tốc độ 115200 baud.

**Mục tiêu 2 – AI nhúng trên ESP32:** Phát triển thuật toán trí tuệ nhân tạo nhúng sử dụng mô hình Decision Tree (cây quyết định), bao gồm:
- Decision Tree Classifier (phân loại): dự đoán hành động tránh vật cản (5 lớp hành động).
- Decision Tree Regressor (hồi quy): dự đoán tốc độ tối ưu liên tục [0, 1].
- Mô hình được huấn luyện offline bằng scikit-learn và xuất sang mã C thuần (pure C if/else) để biên dịch trực tiếp vào firmware ESP32.

**Mục tiêu 3 – Mô phỏng vật lý 2D:** Xây dựng engine mô phỏng vật lý 2D bao gồm:
- Mô hình động học skid-steer 4 bánh (4WD skid-steer kinematics).
- Mảng 9 cảm biến siêu âm mô phỏng bằng thuật toán raycast.
- Phát hiện va chạm (collision detection) với vật cản tròn và tường biên.

**Mục tiêu 4 – Điều hướng và tránh vật cản:** Triển khai hệ thống điều hướng tự động kết hợp:
- Waypoint navigation: điều hướng theo các điểm đích định trước.
- Obstacle avoidance: tránh vật cản thông minh với 4 mức phản ứng theo khoảng cách.
- Blending: pha trộn tín hiệu điều hướng và tránh vật cản dựa trên mức độ nguy hiểm.

**Mục tiêu 5 – Giao tiếp real-time:** Đảm bảo giao tiếp hai chiều giữa ESP32 và Python Simulator đạt hiệu năng thời gian thực: vòng lặp điều khiển 50 Hz, AI inference 5 Hz, độ trễ serial dưới 50 ms.

---

## 1.3 Phạm vi và giới hạn

### 1.3.1 Phạm vi thực hiện

Đề tài thực hiện mô phỏng hoàn toàn trên phần mềm theo kiến trúc HIL:

- **ESP32 Controller:** Firmware chạy trên ESP32 thông qua nền tảng mô phỏng Wokwi (https://wokwi.com), sử dụng Arduino framework. ESP32 đóng vai trò là bộ não duy nhất (sole autonomous brain) của robot, thực hiện toàn bộ logic cảm nhận (perception), ra quyết định (decision making) và điều khiển (control).

- **Python Simulator:** Chương trình Python đóng vai trò là mô hình plant ảo, cung cấp mô phỏng vật lý (physics simulation), cảm biến ảo (virtual sensors) và hiển thị đồ họa 2D (visualization). Python Simulator không chứa bất kỳ logic điều khiển nào – chỉ mô phỏng môi trường và phản hồi trạng thái.

- **Giao tiếp:** Hai thành phần giao tiếp qua cổng serial ảo (virtual serial port) với giao thức JSON line protocol, đảm bảo tính tương thích khi chuyển sang phần cứng thật.

### 1.3.2 Giới hạn

- **Không sử dụng phần cứng thật:** Đề tài không triển khai trên robot vật lý. Không có module L298N (driver motor), HC-SR04 (cảm biến siêu âm) hay motor DC vật lý. Tuy nhiên, kiến trúc module hóa cho phép chuyển đổi sang phần cứng thật với tối thiểu thay đổi.

- **Mô phỏng 2D:** Hệ thống mô phỏng giới hạn ở không gian 2 chiều (top-down view), chưa hỗ trợ mô phỏng 3D với địa hình, độ nghiêng hay yếu tố trọng lực phức tạp.

- **Mô hình AI đơn giản:** Sử dụng Decision Tree thay vì các mô hình Deep Learning phức tạp hơn (CNN, RNN). Đây là lựa chọn có chủ đích nhằm đảm bảo khả năng triển khai trên vi điều khiển ESP32 mà không cần thư viện bên ngoài.

- **Vật cản tĩnh:** Hệ thống hiện chỉ xử lý vật cản tĩnh dạng hình tròn (circular obstacles) và tường biên (boundary walls). Chưa hỗ trợ vật cản động (moving obstacles).

---

## 1.4 Phương pháp nghiên cứu

Đề tài áp dụng phương pháp nghiên cứu kết hợp giữa thiết kế hệ thống top-down và phát triển phần mềm iterative (lặp lại):

### 1.4.1 Thiết kế top-down

Quy trình thiết kế tuân theo mô hình top-down (từ tổng quan đến chi tiết):

1. **Kiến trúc HIL:** Xác định kiến trúc tổng thể với hai thành phần chính (Controller và Plant) và giao thức truyền thông.
2. **Phân rã module:** Chia hệ thống thành các module chức năng độc lập: physics, sensors, obstacles, waypoints, protocol, serial\_bridge, renderer.
3. **Triển khai từng module:** Phát triển, kiểm thử và tích hợp từng module theo thứ tự ưu tiên.

### 1.4.2 Phương pháp mô phỏng HIL

Hệ thống áp dụng mô hình HIL nghiêm ngặt (strict HIL separation):

- **Controller (ESP32):** Chứa toàn bộ logic điều khiển – thu nhận dữ liệu cảm biến, chạy AI inference, tính toán heading error, pha trộn (blend) tín hiệu tránh vật cản và đi theo waypoint, xuất lệnh motor.
- **Plant (Python):** Chỉ chứa mô phỏng vật lý – cập nhật vị trí robot, tính toán cảm biến raycast, phát hiện va chạm, hiển thị đồ họa.
- **Giao tiếp:** Dữ liệu trao đổi hoàn toàn qua giao thức Serial JSON, không có shared memory hay direct function call giữa hai thành phần.

### 1.4.3 AI Pipeline

Quy trình phát triển mô hình AI nhúng bao gồm 5 bước:

1. **Expert Policy:** Xây dựng hàm chính sách chuyên gia (expert policy) dựa trên luật if/else, ánh xạ 9 giá trị cảm biến sang (action\_class, speed\_scale).
2. **Synthetic Dataset:** Sinh bộ dữ liệu huấn luyện tổng hợp (40.000 mẫu) bằng cách tạo ngẫu nhiên các cấu hình cảm biến và gán nhãn bằng expert policy.
3. **Decision Tree Training:** Huấn luyện DecisionTreeClassifier (max\_depth=8) và DecisionTreeRegressor (max\_depth=6) bằng thư viện scikit-learn.
4. **C Code Export:** Chuyển đổi mô hình Decision Tree sang mã C thuần (pure C if/else) bằng hàm `tree_to_c()` tự viết.
5. **ESP32 Firmware Integration:** Biên dịch file header `decision_tree_model.h` chứa mô hình C vào firmware ESP32.

[Hình 1.3: Quy trình phát triển tổng quan của đề tài – từ thiết kế kiến trúc đến triển khai và kiểm thử]

### 1.4.4 Kiểm thử iterative

Quy trình kiểm thử được thực hiện lặp đi lặp lại:

1. Chạy mô phỏng với kịch bản (scenario) cụ thể.
2. Quan sát hành vi robot qua giao diện đồ họa pygame.
3. Phân tích telemetry (mode, AI action, inference latency, sensor distances).
4. Điều chỉnh tham số (thresholds, blending weights, PD gains).
5. Lặp lại cho đến khi robot hoàn thành lộ trình mà không va chạm.

---

## 1.5 Bố cục báo cáo

Báo cáo được tổ chức thành 6 chương với nội dung tóm tắt như sau:

**Chương 1 – Tổng quan đề tài:** Trình bày bối cảnh, đặt vấn đề, mục tiêu, phạm vi, phương pháp nghiên cứu và bố cục báo cáo.

**Chương 2 – Cơ sở lý thuyết:** Trình bày nền tảng lý thuyết liên quan: hệ thống nhúng, vi điều khiển ESP32, động học robot skid-steer, cảm biến siêu âm và thuật toán raycast, trí tuệ nhân tạo nhúng (Decision Tree), phương pháp HIL, giao thức Serial, và điều hướng waypoint.

**Chương 3 – Thiết kế hệ thống:** Trình bày chi tiết thiết kế kiến trúc HIL, các module ESP32 firmware và Python simulator, giao thức truyền thông, pipeline huấn luyện AI, thuật toán tránh vật cản, luồng dữ liệu và thiết kế scenario.

**Chương 4 – Triển khai:** Trình bày chi tiết quá trình triển khai: môi trường phát triển, cấu trúc thư mục, mã nguồn ESP32 firmware, mã nguồn Python simulator, AI training pipeline, và hướng dẫn chạy hệ thống.

**Chương 5 – Kết quả và đánh giá:** Trình bày kết quả mô phỏng (waypoint navigation, obstacle avoidance, AI performance), đánh giá hiệu năng (timing, serial communication), so sánh các phương pháp AI, phân tích ưu/nhược điểm và kết quả kiểm thử.

**Chương 6 – Kết luận và hướng phát triển:** Tổng kết kết quả đạt được, đóng góp của đề tài, và đề xuất hướng phát triển trong tương lai (phần cứng thật, path planning, deep learning, 3D simulation, multi-robot, SLAM).

---

<div style="page-break-before: always;"></div>

# CHƯƠNG 2: CƠ SỞ LÝ THUYẾT

## 2.1 Tổng quan về hệ thống nhúng

### 2.1.1 Định nghĩa

Hệ thống nhúng (embedded system) là một hệ thống máy tính chuyên dụng được thiết kế để thực hiện một hoặc một số chức năng cụ thể, thường hoạt động như một phần của một hệ thống lớn hơn [6]. Khác với máy tính đa năng (general-purpose computer), hệ thống nhúng được tối ưu về kích thước, năng lượng tiêu thụ và chi phí, đồng thời đáp ứng các yêu cầu về hiệu năng và độ tin cậy cho ứng dụng mục tiêu.

Theo định nghĩa của IEEE, hệ thống nhúng là "a computer system that is part of a larger system and performs some of the requirements of that system" [7]. Một cách đơn giản, hệ thống nhúng là sự kết hợp giữa phần cứng (vi điều khiển, cảm biến, cơ cấu chấp hành) và phần mềm (firmware) được thiết kế cho một nhiệm vụ cụ thể.

### 2.1.2 Đặc điểm

Hệ thống nhúng sở hữu một số đặc điểm nổi bật so với máy tính đa năng:

**Xử lý thời gian thực (real-time processing):** Nhiều hệ thống nhúng phải đáp ứng các ràng buộc thời gian nghiêm ngặt (hard real-time constraints). Trong đề tài này, vòng lặp điều khiển của ESP32 phải đảm bảo tần suất 50 Hz (20 ms/chu kỳ), nghĩa là mỗi chu kỳ phải hoàn thành toàn bộ pipeline từ đọc cảm biến đến xuất lệnh motor trong vòng 20 ms.

**Tài nguyên hạn hẹp (resource-constrained):** Vi điều khiển nhúng thường có bộ nhớ RAM từ vài KB đến vài trăm KB, tốc độ xử lý từ vài MHz đến vài trăm MHz. Đặc điểm này đòi hỏi phần mềm nhúng phải được tối ưu cẩn thận về mặt bộ nhớ và thời gian thực thi.

**Chuyên biệt hóa (specialization):** Mỗi hệ thống nhúng được thiết kế cho một mục đích cụ thể. Firmware của hệ thống robot tự hành trong đề tài này chỉ thực hiện các nhiệm vụ: đọc dữ liệu cảm biến, chạy AI inference, tính toán điều khiển và xuất lệnh motor.

**Độ tin cậy cao (high reliability):** Hệ thống nhúng thường phải hoạt động liên tục trong thời gian dài mà không cần can thiệp của người dùng. Trong đề tài, firmware ESP32 được thiết kế với nhiều cơ chế an toàn: UART timeout → SAFE STOP, emergency stop khi cảm biến phát hiện vật cản quá gần, recovery mode khi bị kẹt.

### 2.1.3 Ứng dụng trong robot tự hành

Robot tự hành là một trong những ứng dụng tiêu biểu nhất của hệ thống nhúng, kết hợp nhiều lĩnh vực:

- **Cảm nhận (Perception):** Thu thập dữ liệu từ cảm biến (siêu âm, laser, camera) để nhận biết môi trường xung quanh.
- **Ra quyết định (Decision Making):** Sử dụng thuật toán AI/ML để phân tích dữ liệu cảm biến và đưa ra quyết định hành động.
- **Điều khiển (Control):** Chuyển đổi quyết định thành lệnh điều khiển cụ thể cho motor (vận tốc, hướng).
- **Truyền thông (Communication):** Trao đổi dữ liệu giữa các module nội bộ hoặc với hệ thống bên ngoài.

Trong đề tài này, toàn bộ pipeline perception → decision → control được triển khai trên vi điều khiển ESP32, minh họa khả năng tích hợp đầy đủ một hệ thống robot tự hành trên nền tảng nhúng.

---

## 2.2 Vi điều khiển ESP32

### 2.2.1 Tổng quan

ESP32 là dòng vi điều khiển hiệu năng cao do công ty Espressif Systems (Thượng Hải, Trung Quốc) phát triển [4]. Ra mắt lần đầu vào năm 2016, ESP32 nhanh chóng trở thành một trong những vi điều khiển phổ biến nhất cho các ứng dụng IoT và hệ thống nhúng nhờ sự kết hợp giữa hiệu năng mạnh mẽ, kết nối không dây tích hợp và giá thành hợp lý.

[Hình 2.1: Kiến trúc tổng quan vi điều khiển ESP32 – sơ đồ khối các thành phần chính bao gồm dual-core CPU, bộ nhớ, ngoại vi và module không dây]

### 2.2.2 Kiến trúc phần cứng

ESP32 được xây dựng trên kiến trúc Xtensa LX6, một kiến trúc 32-bit của Cadence Design Systems, được tối ưu cho các ứng dụng nhúng hiệu năng cao [4].

**Bảng 2.1: Thông số kỹ thuật vi điều khiển ESP32-WROOM-32**

| Thông số | Giá trị |
|----------|---------|
| CPU | Xtensa LX6 dual-core @ 240 MHz |
| Kiến trúc | 32-bit RISC |
| SRAM | 520 KB |
| Flash | 4 MB (ngoài) |
| ROM | 448 KB |
| Wi-Fi | 802.11 b/g/n (2.4 GHz) |
| Bluetooth | v4.2 BR/EDR + BLE |
| GPIO | 34 chân (đa chức năng) |
| UART | 3 bộ |
| SPI | 4 bộ |
| I2C | 2 bộ |
| ADC | 18 kênh (12-bit) |
| DAC | 2 kênh (8-bit) |
| PWM | 16 kênh |
| Điện áp hoạt động | 2.2V – 3.6V |
| Nhiệt độ hoạt động | −40°C ~ +85°C |

### 2.2.3 Bộ xử lý Dual-Core

Một trong những ưu điểm nổi bật của ESP32 là kiến trúc dual-core, cho phép chia tải công việc giữa hai lõi xử lý [4]:

- **Core 0 (PRO\_CPU):** Trong đề tài này được sử dụng cho tác vụ AI inference – chạy mô hình Decision Tree ở tần suất 5 Hz (200 ms/chu kỳ).
- **Core 1 (APP\_CPU):** Được sử dụng cho tác vụ control loop – vòng lặp điều khiển chính ở tần suất 50 Hz (20 ms/chu kỳ).

Việc phân chia này cho phép AI inference (tốn nhiều tài nguyên tính toán hơn) chạy song song với vòng lặp điều khiển mà không gây ảnh hưởng đến tính thời gian thực của hệ thống điều khiển.

### 2.2.4 FreeRTOS – Hệ điều hành thời gian thực

ESP32 tích hợp sẵn FreeRTOS (Free Real-Time Operating System) – một hệ điều hành thời gian thực mã nguồn mở được sử dụng rộng rãi trong các hệ thống nhúng [8]. FreeRTOS cung cấp các cơ chế:

- **Task management:** Tạo và quản lý các tác vụ (task) với mức ưu tiên (priority) khác nhau. Trong đề tài, `controlTask` được gán priority 2 (cao hơn) và `aiTask` được gán priority 1.
- **Task scheduling:** Lập lịch preemptive – tác vụ có priority cao hơn sẽ được ưu tiên thực thi.
- **Synchronization:** Cung cấp mutex, semaphore cho đồng bộ dữ liệu giữa các task. Trong đề tài, `portMUX_TYPE` được sử dụng để bảo vệ vùng dữ liệu chia sẻ giữa controlTask và aiTask.
- **Core pinning:** Cho phép gán task vào core cụ thể thông qua `xTaskCreatePinnedToCore()`.

[Hình 2.2: Sơ đồ khối chức năng ESP32-DevKitC – minh họa các thành phần phần cứng và kết nối]

### 2.2.5 Giao diện ngoại vi (Peripheral Interfaces)

ESP32 cung cấp nhiều giao diện ngoại vi phong phú [4]:

- **UART (Universal Asynchronous Receiver-Transmitter):** 3 bộ UART phần cứng. Trong đề tài, UART0 được sử dụng để giao tiếp với Python Simulator ở tốc độ 115200 baud.
- **GPIO (General Purpose Input/Output):** 34 chân GPIO đa chức năng, hỗ trợ cả digital và analog.
- **SPI (Serial Peripheral Interface):** 4 bộ SPI cho giao tiếp tốc độ cao với ngoại vi.
- **I2C (Inter-Integrated Circuit):** 2 bộ I2C cho giao tiếp với cảm biến và module mở rộng.
- **PWM (Pulse Width Modulation):** 16 kênh PWM, phù hợp cho điều khiển motor DC.

### 2.2.6 Wokwi – Nền tảng mô phỏng ESP32 online

Wokwi (https://wokwi.com) là nền tảng mô phỏng vi điều khiển online, hỗ trợ Arduino, ESP32, Raspberry Pi Pico và nhiều board khác [9]. Wokwi cho phép:

- Viết và biên dịch firmware trực tiếp trên trình duyệt web.
- Mô phỏng ESP32 với đầy đủ tính năng: GPIO, UART, SPI, I2C, Wi-Fi.
- Kết nối serial monitor để debug và giao tiếp với firmware.
- Sử dụng cổng serial ảo cho phép ứng dụng bên ngoài (Python) giao tiếp với firmware đang chạy.

Trong đề tài, ESP32 firmware được triển khai và chạy trên Wokwi, giao tiếp với Python Simulator thông qua cổng serial ảo.

---

## 2.3 Động học Robot – Mô hình Skid-Steer 4 bánh

### 2.3.1 Giới thiệu mô hình

Mô hình skid-steer (lái trượt) là một trong những mô hình phổ biến nhất cho robot 4 bánh có dẫn động độc lập (independent drive) ở mỗi bên [10]. Khác với mô hình Ackermann steering (lái Ackermann) sử dụng trong ô tô thông thường, robot skid-steer thực hiện việc rẽ hướng bằng cách tạo ra chênh lệch vận tốc giữa bánh bên trái và bánh bên phải.

[Hình 2.3: Mô hình 4WD Skid-Steer Differential Drive – minh họa bố trí 4 bánh FL, FR, RL, RR với track width và wheel base]

### 2.3.2 Cấu hình 4WD

Robot trong đề tài sử dụng cấu hình 4WD (Four-Wheel Drive) skid-steer với đặc điểm:

- **4 bánh độc lập:** Front-Left (FL), Front-Right (FR), Rear-Left (RL), Rear-Right (RR).
- **Nhóm bên trái:** FL và RL chia sẻ cùng vận tốc $v_L$ (left-side velocity).
- **Nhóm bên phải:** FR và RR chia sẻ cùng vận tốc $v_R$ (right-side velocity).

**Bảng 2.2: Thông số hình học robot 4WD Skid-Steer**

| Thông số | Ký hiệu | Giá trị | Đơn vị |
|----------|---------|---------|--------|
| Khoảng cách hai bên bánh (track width) | $W$ | 0.22 | m |
| Khoảng cách hai trục bánh (wheel base) | $L$ | 0.16 | m |
| Bán kính bánh xe | $r$ | 0.033 | m |
| Vận tốc tối đa | $v_{max}$ | 0.60 | m/s |
| Bán kính robot (collision) | $R_{robot}$ | 0.18 | m |
| Hệ số ma sát ngang | $\mu_{lat}$ | 0.85 | - |

### 2.3.3 Phương trình động học – Xấp xỉ Unicycle

Mô hình skid-steer 4 bánh có thể được xấp xỉ bằng mô hình unicycle (xe đạp một bánh) [10], [11]. Xấp xỉ này giả định robot là một chất điểm có hướng (oriented point), đơn giản hóa việc tính toán mà vẫn đủ chính xác cho mục đích điều khiển.

**Vận tốc tịnh tiến (linear velocity):**

$$v = \frac{v_R + v_L}{2}$$

Trong đó $v_R$ và $v_L$ lần lượt là vận tốc tuyến tính (m/s) của nhóm bánh bên phải và bên trái.

**Vận tốc góc (angular velocity):**

$$\omega = \frac{v_R - v_L}{W}$$

Trong đó $W$ là track width (khoảng cách giữa hai bên bánh).

[Hình 2.4: Phương trình động học unicycle approximation – minh họa mối quan hệ giữa (vL, vR) và (v, ω)]

**Hệ số ma sát ngang (lateral friction):**

Trong thực tế, robot skid-steer khi quay sẽ xảy ra hiện tượng trượt ngang của bánh xe (tyre scrubbing), làm giảm hiệu quả quay. Hiện tượng này được mô phỏng bằng hệ số ma sát ngang $\mu_{lat}$ [10]:

$$\omega_{eff} = \omega \times \mu_{lat}$$

Với $\mu_{lat} = 0.85$, nghĩa là vận tốc góc thực tế chỉ đạt 85% giá trị lý thuyết do ma sát trượt ngang.

**Phương trình cập nhật trạng thái (Euler integration):**

$$x_{k+1} = x_k + v \cdot \cos(\theta_k) \cdot \Delta t$$

$$y_{k+1} = y_k + v \cdot \sin(\theta_k) \cdot \Delta t$$

$$\theta_{k+1} = \theta_k + \omega_{eff} \cdot \Delta t$$

Trong đó:
- $(x_k, y_k)$ là vị trí robot tại thời điểm $k$ (mét).
- $\theta_k$ là hướng (heading) của robot tại thời điểm $k$ (radian, 0 = hướng Đông, ngược chiều kim đồng hồ là dương).
- $\Delta t$ là bước thời gian mô phỏng (trong đề tài: $\Delta t = 0.02$ s, tương ứng 50 Hz).

### 2.3.4 Chuyển đổi lệnh điều khiển

Firmware ESP32 sử dụng biến đổi ngược từ $(v, \omega)$ sang $(v_L, v_R)$ để xuất lệnh motor:

$$v_L = v - \frac{W}{2} \cdot \omega$$

$$v_R = v + \frac{W}{2} \cdot \omega$$

Giá trị $v_L$ và $v_R$ được chuẩn hóa (normalize) về khoảng $[-1, 1]$ trước khi gửi sang Python Simulator, với $\pm 1$ tương ứng $\pm v_{max}$.

---

## 2.4 Cảm biến siêu âm và mô phỏng Raycast

### 2.4.1 Nguyên lý hoạt động cảm biến siêu âm HC-SR04

Cảm biến siêu âm HC-SR04 là loại cảm biến đo khoảng cách phổ biến nhất trong các dự án robot [12]. Nguyên lý hoạt động dựa trên phương pháp TOF (Time of Flight – Thời gian bay):

1. Cảm biến phát ra xung siêu âm (ultrasonic pulse) ở tần số 40 kHz qua bộ phát (transmitter).
2. Xung siêu âm truyền đi với tốc độ âm thanh ($v_{sound} \approx 343$ m/s ở 20°C), gặp vật thể và phản xạ lại.
3. Bộ thu (receiver) nhận sóng phản xạ và đo thời gian truyền đi - phản xạ về ($\Delta t_{echo}$).
4. Khoảng cách được tính theo công thức:

$$d = \frac{v_{sound} \times \Delta t_{echo}}{2}$$

[Hình 2.5: Nguyên lý hoạt động cảm biến siêu âm HC-SR04 – minh họa quá trình phát xung, phản xạ và đo thời gian]

HC-SR04 có tầm đo từ 2 cm đến 400 cm, với góc phát hiện khoảng 15° [12]. Trong đề tài, cảm biến siêu âm được mô phỏng hoàn toàn bằng phần mềm thông qua thuật toán raycast.

### 2.4.2 Mảng 9 cảm biến

Robot trong đề tài được trang bị mảng 9 cảm biến siêu âm (ultrasonic sensor array), bao gồm 7 cảm biến hướng trước (forward cone) và 2 cảm biến bên (side sensors), tạo thành vùng phủ 180° [13]:

**Bảng 2.3: Cấu hình mảng 9 cảm biến siêu âm**

| Index | Ký hiệu | Góc lệch | Tầm đo (m) | Vị trí |
|-------|---------|-----------|-------------|--------|
| 0 | LS (Left Side) | +90° | 2.5 | Bên trái |
| 1 | LF (Left Far) | +60° | 4.0 | Trước-trái xa |
| 2 | LM (Left Mid) | +35° | 4.5 | Trước-trái giữa |
| 3 | LN (Left Near) | +15° | 5.0 | Trước-trái gần |
| 4 | C (Center) | 0° | 5.5 | Phía trước (trung tâm) |
| 5 | RN (Right Near) | −15° | 5.0 | Trước-phải gần |
| 6 | RM (Right Mid) | −35° | 4.5 | Trước-phải giữa |
| 7 | RF (Right Far) | −60° | 4.0 | Trước-phải xa |
| 8 | RS (Right Side) | −90° | 2.5 | Bên phải |

[Hình 2.6: Bố trí mảng 9 cảm biến trên robot – minh họa 7 tia hướng trước (cone 120°) và 2 tia bên (±90°)]

Thiết kế mảng cảm biến tuân theo nguyên tắc:
- **Vùng trước (forward cone):** 7 cảm biến phân bố trong cone 120° (từ −60° đến +60°) với tầm đo dài hơn (4.0–5.5 m), đảm bảo phát hiện sớm vật cản phía trước.
- **Hai bên (side sensors):** 2 cảm biến ở ±90° với tầm đo ngắn hơn (2.5 m), phục vụ phát hiện vật cản bên cạnh khi đi dọc tường hoặc qua lối hẹp.
- **Mật độ cao hơn ở trung tâm:** Khoảng cách góc giữa các cảm biến nhỏ hơn ở vùng trung tâm (15°) và lớn hơn ở rìa (25°), tăng độ phân giải cho vùng nguy hiểm nhất.

### 2.4.3 Thuật toán Raycast

Thuật toán raycast (bắn tia) là phương pháp mô phỏng cảm biến khoảng cách bằng cách phát ra một tia thẳng (ray) từ vị trí cảm biến theo hướng xác định, rồi tính toán giao điểm với các đối tượng trong môi trường [14].

**Ray-Circle Intersection (giao điểm tia – đường tròn):**

Cho tia $\mathbf{r}(t) = \mathbf{O} + t \cdot \mathbf{d}$ với gốc $\mathbf{O} = (o_x, o_y)$ và hướng $\mathbf{d} = (\cos\alpha, \sin\alpha)$; vật cản tròn có tâm $\mathbf{C} = (c_x, c_y)$ và bán kính $R$.

Đặt $\mathbf{f} = \mathbf{C} - \mathbf{O}$, phương trình giao điểm quy về phương trình bậc hai:

$$at^2 + bt + c = 0$$

Trong đó:
$$a = d_x^2 + d_y^2 = 1$$
$$b = -2(f_x \cdot d_x + f_y \cdot d_y)$$
$$c = f_x^2 + f_y^2 - R^2$$

Discriminant: $\Delta = b^2 - 4ac$

- Nếu $\Delta < 0$: Không có giao điểm (tia không chạm vật cản).
- Nếu $\Delta \geq 0$: Giao điểm gần nhất tại $t_1 = \frac{-b - \sqrt{\Delta}}{2a}$ (nếu $t_1 > 0$).

[Hình 2.7: Thuật toán raycast – giao điểm tia với đường tròn (vật cản) và đường thẳng (tường)]

**Ray-Wall Intersection (giao điểm tia – tường biên):**

Tường biên được mô hình hóa bằng 4 đoạn thẳng tương ứng 4 cạnh của vùng mô phỏng (world boundary):
- Tường trái: $x = 0$
- Tường phải: $x = W_{world}$
- Tường dưới: $y = 0$
- Tường trên: $y = H_{world}$

Với mỗi tường, tham số $t$ của giao điểm được tính đơn giản. Ví dụ, cho tường phải ($x = W_{world}$):

$$t = \frac{W_{world} - o_x}{d_x} \quad (\text{nếu } d_x > 0)$$

Sau đó kiểm tra giao điểm có nằm trong phạm vi tường không (kiểm tra tọa độ $y$ của giao điểm).

**Khoảng cách đo được:** Tại mỗi cảm biến, khoảng cách trả về là giá trị $t_{min}$ (min trên tất cả giao điểm hợp lệ với vật cản tròn và tường biên), được giới hạn trong khoảng $[d_{min}, d_{max}]$ của cảm biến.

---

## 2.5 Trí tuệ nhân tạo nhúng (Embedded AI)

### 2.5.1 Thách thức triển khai AI trên vi điều khiển

Triển khai trí tuệ nhân tạo trên vi điều khiển nhúng (embedded AI / TinyML) đặt ra nhiều thách thức khác biệt so với triển khai trên máy tính hoặc server [15]:

- **Bộ nhớ hạn chế:** ESP32 chỉ có 520 KB SRAM – trong khi một mạng neural đơn giản (MLP) có thể yêu cầu hàng MB tham số.
- **Tốc độ xử lý:** 240 MHz Xtensa LX6 mạnh hơn nhiều vi điều khiển 8-bit nhưng vẫn chậm hơn GPU/TPU hàng nghìn lần.
- **Không có floating-point unit (FPU) mạnh:** ESP32 hỗ trợ tính toán float32 nhưng không có hardware accelerator cho tensor operations.
- **Không có runtime ML:** Không có Python, NumPy, TensorFlow hay PyTorch chạy trực tiếp trên ESP32.
- **Yêu cầu deterministic:** Inference phải có thời gian thực thi ổn định, không biến thiên lớn giữa các lần gọi.

### 2.5.2 Decision Tree – Cây quyết định

Decision Tree (cây quyết định) là một thuật toán học máy thuộc nhóm supervised learning (học có giám sát), sử dụng cấu trúc cây để biểu diễn quy tắc phân loại hoặc hồi quy [16]. Thuật toán chia không gian đặc trưng (feature space) thành các vùng con (partition) bằng cách đặt các ngưỡng (threshold) lên từng đặc trưng.

[Hình 2.8: Cấu trúc cây quyết định (Decision Tree) – minh họa các node phân chia, lá (leaf) và đường đi từ root đến leaf]

**Cấu trúc:**

- **Internal node (node phân chia):** Chứa điều kiện so sánh dạng `if feature[i] <= threshold`.
- **Leaf node (node lá):** Chứa kết quả phân loại (class) hoặc giá trị hồi quy (value).
- **Depth (độ sâu):** Số cạnh từ root đến leaf xa nhất. Depth lớn hơn → mô hình phức tạp hơn → dễ overfitting.

**Ưu điểm trên embedded:**

1. **Export sang pure C:** Decision Tree có thể được biểu diễn hoàn toàn bằng chuỗi if/else lồng nhau trong ngôn ngữ C, không cần thư viện bên ngoài. Đây là ưu điểm quyết định cho triển khai trên vi điều khiển.
2. **Inference nhanh:** Thời gian inference chỉ phụ thuộc vào depth của cây (O(depth)). Với depth = 8, mỗi lần inference chỉ cần tối đa 8 phép so sánh float.
3. **Bộ nhớ nhỏ:** Mô hình Decision Tree trong đề tài chỉ chiếm khoảng 5 KB mã C sau khi biên dịch.
4. **Deterministic:** Thời gian inference ổn định, không phụ thuộc vào giá trị input – phù hợp cho hệ thống real-time.

**Trong đề tài:**

Hai mô hình Decision Tree được huấn luyện:

- **Classifier (phân loại):** Dự đoán hành động tránh vật cản từ 9 giá trị cảm biến.
  - Input: `float f[9]` – vector 9 khoảng cách cảm biến.
  - Output: `int class ∈ {0, 1, 2, 3, 4}` – 5 lớp hành động.
  - Cấu hình: max\_depth = 8, 199 leaves, 5 classes.
  - Accuracy: 86.52% trên tập test.

- **Regressor (hồi quy):** Dự đoán hệ số tốc độ tối ưu.
  - Input: `float f[9]` – vector 9 khoảng cách cảm biến.
  - Output: `float speed ∈ [0, 1]` – hệ số tốc độ.
  - Cấu hình: max\_depth = 6, 44 leaves.
  - MAE: 0.0478 trên tập test.

### 2.5.3 So sánh với các phương pháp AI khác trên embedded

**Bảng 2.4: So sánh các phương pháp AI trên vi điều khiển nhúng**

| Tiêu chí | Decision Tree | Neural Network (MLP) | Random Forest | SVM | Rule-based |
|----------|--------------|---------------------|---------------|-----|------------|
| Accuracy | 83–87% | ~90% | ~88% | ~85% | ~75% |
| Kích thước mô hình | ~5 KB C | ~50 KB | ~50 KB | ~20 KB | ~2 KB |
| Thời gian inference | < 1 ms | ~10 ms | ~5 ms | ~3 ms | < 0.5 ms |
| Bộ nhớ RAM | < 1 KB | ~10 KB | ~10 KB | ~5 KB | < 1 KB |
| Dependencies | Không | TFLite Micro | Custom | Custom | Không |
| Export sang C | Dễ (if/else) | Khó | Trung bình | Trung bình | Dễ |
| Khả năng generalize | Trung bình | Cao | Cao | Cao | Thấp |
| Dễ giải thích | Cao | Thấp | Trung bình | Thấp | Cao |

[Hình 2.9: So sánh các phương pháp AI trên vi điều khiển – biểu đồ radar so sánh accuracy, speed, size, explainability]

Decision Tree được lựa chọn cho đề tài dựa trên phân tích trade-off:
- **vs. Neural Network:** NN có accuracy cao hơn nhưng yêu cầu TFLite Micro runtime (~50 KB), inference chậm hơn 10× và khó debug.
- **vs. Random Forest:** RF là ensemble của nhiều DT, accuracy cao hơn nhưng kích thước lớn hơn 10× và inference chậm hơn.
- **vs. Rule-based:** Rule-based nhỏ gọn và nhanh nhất nhưng accuracy thấp và khó mở rộng cho các tình huống phức tạp.

---

## 2.6 Phương pháp HIL (Hardware-in-the-Loop)

### 2.6.1 Định nghĩa

Hardware-in-the-Loop (HIL) simulation là phương pháp kiểm thử trong đó bộ điều khiển thực (real controller hardware) được kết nối với mô hình toán học (mathematical model) của đối tượng được điều khiển (plant), chạy trên máy tính thời gian thực [5]. Mục đích của HIL là kiểm tra chức năng và hiệu năng của bộ điều khiển nhúng trong môi trường giả lập trước khi triển khai thực tế.

### 2.6.2 Các cấp độ mô phỏng

Trong quy trình phát triển hệ thống nhúng theo tiêu chuẩn V-Model, có 4 cấp độ mô phỏng từ trừu tượng đến cụ thể [5], [17]:

**Bảng 2.5: So sánh các phương pháp mô phỏng trong phát triển hệ thống nhúng**

| Cấp độ | Controller | Plant | Giao tiếp | Mục đích |
|--------|-----------|-------|-----------|----------|
| MIL (Model-in-the-Loop) | Mô hình | Mô hình | Nội bộ | Kiểm tra thuật toán |
| SIL (Software-in-the-Loop) | Code C/C++ | Mô hình | Nội bộ | Kiểm tra code logic |
| **HIL (Hardware-in-the-Loop)** | **Phần cứng** | **Mô hình** | **I/O thực** | **Kiểm tra firmware** |
| Field Testing | Phần cứng | Thực tế | I/O thực | Kiểm tra toàn hệ thống |

[Hình 2.10: Các cấp độ mô phỏng: MIL → SIL → HIL → Field Testing – minh họa mức độ chân thực tăng dần]

### 2.6.3 Ưu điểm của HIL

So với các phương pháp khác, HIL mang lại sự cân bằng tối ưu giữa tính chân thực và chi phí [5]:

1. **Kiểm thử firmware thực:** Code chạy trên phần cứng thực (ESP32) với đầy đủ ràng buộc về timing, memory, và interrupt handling. Điều này đảm bảo firmware sẽ hoạt động tương tự khi triển khai thực tế.
2. **Phát hiện lỗi sớm:** Nhiều lỗi về timing, race condition, buffer overflow chỉ xuất hiện khi code chạy trên phần cứng thực, không thể phát hiện bằng SIL hoặc MIL.
3. **Kiểm thử an toàn:** Có thể mô phỏng các tình huống nguy hiểm (va chạm tốc độ cao, mất tín hiệu cảm biến, lỗi giao tiếp) mà không lo hỏng thiết bị.
4. **Tái tạo điều kiện test:** Mỗi kịch bản test có thể được lặp lại chính xác, hỗ trợ regression testing.

### 2.6.4 HIL trong đề tài

Trong đề tài này, kiến trúc HIL được triển khai với:

- **Controller (Brain):** ESP32 firmware chạy trên Wokwi simulator, chứa toàn bộ logic: perception (xác nhận và nhóm cảm biến), AI inference (Decision Tree), navigation (waypoint heading error), control (PD steering + blending), và communication (Serial JSON I/O).
- **Plant:** Python application chứa: physics engine (động học skid-steer 4 bánh), sensor simulation (9-beam raycast), obstacle management (phát hiện va chạm), waypoint management (quản lý điểm đích), và renderer (hiển thị đồ họa 2D).
- **Interface:** Giao tiếp qua Serial JSON @ 115200 baud, với dữ liệu trao đổi bao gồm: sensor distances, robot position, waypoint coordinates, motor commands, và AI telemetry.

---

## 2.7 Giao thức truyền thông Serial

### 2.7.1 UART – Universal Asynchronous Receiver-Transmitter

UART là giao thức truyền thông nối tiếp không đồng bộ, một trong những phương thức truyền dữ liệu cơ bản nhất trong hệ thống nhúng [18]. UART truyền dữ liệu theo từng byte, mỗi byte được đóng gói trong một khung (frame) bao gồm:

- **Start bit (1 bit):** Mức thấp (LOW), báo hiệu bắt đầu truyền.
- **Data bits (8 bit):** Dữ liệu truyền, bit thấp truyền trước (LSB first).
- **Parity bit (0 hoặc 1 bit):** Bit kiểm tra chẵn lẻ (tùy chọn, thường không sử dụng).
- **Stop bit (1 hoặc 2 bit):** Mức cao (HIGH), báo hiệu kết thúc.

[Hình 2.11: Khung truyền dữ liệu UART – minh họa cấu trúc start bit, data bits, và stop bit]

Tốc độ truyền được quy định bằng baud rate – số bit truyền trong 1 giây. Trong đề tài sử dụng baud rate 115200, nghĩa là truyền được khoảng 11.520 byte/giây (115200 / 10, với 10 = 1 start + 8 data + 1 stop).

### 2.7.2 JSON Line Protocol

Đề tài sử dụng giao thức JSON line protocol – mỗi dòng (kết thúc bằng ký tự `\n`) là một đối tượng JSON hoàn chỉnh [19]. Ưu điểm của giao thức này:

**Human-readable:** Dữ liệu ở dạng text, dễ đọc và debug. Ví dụ:
```json
{"t":12345,"x":2.1,"y":1.9,"th":0.52,"wpX":6.0,"wpY":4.0,"d":[2.0,1.4,1.2,0.9,0.7,1.0,1.3,1.6,2.2]}
```

**Self-describing:** Mỗi field có tên rõ ràng (`t` = timestamp, `x` = position X, `d` = distances), không cần tài liệu riêng để hiểu cấu trúc.

**Dễ mở rộng:** Có thể thêm field mới mà không ảnh hưởng đến parser cũ (backward compatible).

**Hỗ trợ rộng:** JSON được hỗ trợ bởi hầu hết ngôn ngữ lập trình. Trên ESP32, thư viện ArduinoJson (v6.21+) cung cấp API mạnh mẽ cho việc serialize/deserialize JSON [20].

**Trade-off về bandwidth:** So với binary protocol, JSON tốn nhiều bandwidth hơn do overhead của tên field và ký tự text. Tuy nhiên, với baud rate 115200 và kích thước packet ~120 byte, throughput vẫn đủ cho tần suất 50 Hz:
- Kích thước packet trung bình: ~120 byte (sensor) + ~80 byte (motor) = ~200 byte/chu kỳ.
- Bandwidth yêu cầu: 200 byte × 50 Hz × 10 bit/byte = 100.000 bit/s < 115.200 bit/s.

### 2.7.3 ArduinoJson

ArduinoJson là thư viện C++ mã nguồn mở cho việc xử lý JSON trên nền tảng Arduino/ESP32 [20]. Thư viện cung cấp:

- **StaticJsonDocument:** Cấp phát bộ nhớ tĩnh (trên stack), không sử dụng dynamic allocation – phù hợp cho hệ thống nhúng. Trong đề tài, `StaticJsonDocument<512>` được sử dụng cho input và `StaticJsonDocument<256>` cho output.
- **deserializeJson():** Parse JSON string thành document object.
- **serializeJson():** Serialize document object thành JSON string.
- **Zero-copy design:** Tối thiểu copy data, giảm overhead bộ nhớ.

---

## 2.8 Điều hướng Waypoint

### 2.8.1 Khái niệm

Waypoint navigation (điều hướng theo điểm đích) là phương pháp điều hướng robot bằng cách xác định một chuỗi các điểm đích (waypoints) trên bản đồ, robot sẽ tuần tự di chuyển đến từng điểm [21]. Đây là phương pháp điều hướng đơn giản nhưng hiệu quả, được sử dụng rộng rãi trong robot tự hành, drone và tàu biển.

Hệ thống điều hướng waypoint bao gồm ba thành phần chính:

1. **Waypoint list:** Danh sách các tọa độ $(x_i, y_i)$ theo thứ tự cần đi qua.
2. **Heading controller:** Bộ điều khiển hướng (heading), điều chỉnh hướng robot về phía waypoint hiện tại.
3. **Waypoint switcher:** Logic chuyển đổi giữa các waypoint khi robot đã đến đủ gần waypoint hiện tại.

### 2.8.2 Heading Error Calculation

Heading error (sai số hướng) là góc lệch giữa hướng hiện tại của robot và hướng đến waypoint mục tiêu [21]:

$$e_{\theta} = \text{atan2}(y_{wp} - y, \; x_{wp} - x) - \theta$$

[Hình 2.12: Minh họa heading error trong waypoint navigation – góc giữa hướng robot và hướng đến waypoint]

Trong đó:
- $(x, y)$ là vị trí hiện tại của robot.
- $(x_{wp}, y_{wp})$ là vị trí waypoint mục tiêu.
- $\theta$ là hướng (heading) hiện tại của robot.
- $\text{atan2}(dy, dx)$ trả về góc trong khoảng $(-\pi, \pi]$.

Giá trị $e_{\theta}$ sau đó được chuẩn hóa về khoảng $[-\pi, \pi]$ bằng phép modulo:

```
while (e_θ > π):  e_θ -= 2π
while (e_θ < −π): e_θ += 2π
```

### 2.8.3 PD Controller cho Steering

Trong firmware ESP32, bộ điều khiển PD (Proportional-Derivative) được sử dụng để chuyển đổi heading error thành vận tốc góc (angular velocity) $\omega$ [22]:

$$\omega_{wp} = K_p \cdot e_{\theta}$$

Trong đề tài, bộ điều khiển sử dụng hệ số $K_p = 2.0$ (proportional gain) với giới hạn output $|\omega_{wp}| \leq 2.5$ rad/s. Hệ số này được tinh chỉnh qua thực nghiệm để đạt sự cân bằng giữa tốc độ phản ứng (responsiveness) và ổn định (stability).

Ngoài ra, vận tốc tịnh tiến $v_{wp}$ cũng được điều chỉnh theo khoảng cách đến waypoint:

$$v_{wp} = \text{clamp}\left(v_{base} \times (0.60 + 0.40 \times \min(d_{wp}, 2.5)), \; 0.30, \; v_{base}\right)$$

Trong đó $d_{wp}$ là khoảng cách Euclidean đến waypoint hiện tại và $v_{base} = 0.65$ m/s.

### 2.8.4 Waypoint Reached Detection

Robot được coi là đã đến waypoint khi khoảng cách Euclidean giữa vị trí robot và waypoint nhỏ hơn ngưỡng reach\_radius [21]:

$$d_{wp} = \sqrt{(x_{wp} - x)^2 + (y_{wp} - y)^2} \leq r_{reach}$$

Trong đề tài, $r_{reach} = 0.40$ m (cấu hình trong file YAML). Khi điều kiện trên được thỏa mãn, hệ thống chuyển sang waypoint tiếp theo. Nếu đã hoàn thành tất cả waypoints và chế độ loop được bật (loop\_waypoints = true), robot sẽ quay lại waypoint đầu tiên và tiếp tục lặp.

---

*Hết Chương 2. Chương 3 sẽ trình bày chi tiết thiết kế hệ thống.*

---
