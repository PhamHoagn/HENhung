/*
 * HIL Robocar - ESP32 TEST VERSION (Super Simple)
 * NO LIBRARY - NO CRASH
 */

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("# ESP32 Ready - Test Version");
  Serial.println("# No library version");
}

void loop() {
  // Simple echo test
  if (Serial.available() > 0) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    
    if (line.length() > 0 && !line.startsWith("#")) {
      // Echo back simple JSON
      Serial.println("{\"vL\":0.5,\"vR\":0.5}");
    }
  }
  
  delay(10);
}
