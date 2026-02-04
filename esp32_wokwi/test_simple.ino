/*
 * ESP32 TEST CODE - Để Kiểm Tra Wokwi Hoạt Động
 * 
 * Code đơn giản nhất - không cần thư viện gì!
 * Dùng code này để test xem Wokwi có chạy được không
 */

void setup() {
  Serial.begin(115200);
  delay(1000);  // Đợi 1 giây
  
  Serial.println("=================================");
  Serial.println("ESP32 TEST - WOKWI CHECK");
  Serial.println("=================================");
  Serial.println("Setup complete!");
  Serial.println("");
}

void loop() {
  Serial.print("Running... Time: ");
  Serial.print(millis() / 1000);
  Serial.println(" seconds");
  
  delay(1000);  // In ra mỗi giây
}
