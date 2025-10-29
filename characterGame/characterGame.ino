/*
 * ⚡ NEXUS - Cyberpunk Arduino Bluetooth Joystick Controller ⚡
 * 
 * Advanced 3D Robot Controller with Multi-Input Support
 * 
 * Hardware Configuration:
 * - Joystick Power: Pin 9 (acts as 5V output)
 * - Bluetooth Module: HC-05/HC-06 @ 38400 baud
 * - Joystick: Analog X (A0), Y (A1), Button (D2)
 * - Action Buttons: Jump (D3), Wave (D4), Dance (D5)
 * 
 * Voltage Divider Required for Bluetooth RX!
 * Arduino 5V → 1K Ω → Bluetooth RX → 2K Ω → GND
 */

#include <SoftwareSerial.h>

// ========== PIN DEFINITIONS ==========
// Bluetooth Module (SoftwareSerial)
#define BT_RX 10
#define BT_TX 11

// Analog Input Pins
#define JOY_X A0
#define JOY_Y A1

// Digital Input Pins (Active LOW with pull-up)
#define JOY_BTN 2
#define JUMP_BTN 3
#define WAVE_BTN 4
#define DANCE_BTN 5

// Power and Status
#define JOY_POWER 9
#define STATUS_LED LED_BUILTIN

// ========== CALIBRATION CONSTANTS ==========
#define JOY_CENTER 512           // Mid-point for 0-1023 range
#define JOY_DEADZONE 80          // Ignore small movements
#define JOY_THRESHOLD 250        // Minimum movement to trigger command
#define COMMAND_DELAY 200        // Milliseconds between movement commands
#define DEBOUNCE_DELAY 40        // Debounce time for buttons
#define BAUD_RATE 38400          // Bluetooth baud rate

// ========== DATA STRUCTURES ==========
struct ButtonState {
  int pin;
  bool lastState;
  unsigned long lastPressTime;
  const char* command;
};

struct JoystickState {
  int xRaw;
  int yRaw;
  int xDiff;
  int yDiff;
  String currentCommand;
  String lastCommand;
  unsigned long lastCommandTime;
};

// ========== GLOBAL VARIABLES ==========
SoftwareSerial BTSerial(BT_RX, BT_TX);

ButtonState buttons[] = {
  {JUMP_BTN, HIGH, 0, "jump"},
  {WAVE_BTN, HIGH, 0, "wave"},
  {DANCE_BTN, HIGH, 0, "dance"},
  {JOY_BTN, HIGH, 0, "reset"}
};

const int NUM_BUTTONS = sizeof(buttons) / sizeof(buttons[0]);
JoystickState joystick = {0, 0, 0, 0, "", "", 0};

unsigned long lastDebugOutput = 0;
#define DEBUG_INTERVAL 1000      // Debug output every 1 second

// ========== SETUP ==========
void setup() {
  // Initialize Serial Communications
  Serial.begin(9600);          // Debug serial
  BTSerial.begin(BAUD_RATE);   // Bluetooth communication

  // Configure GPIO Pins
  pinMode(JOY_POWER, OUTPUT);
  digitalWrite(JOY_POWER, HIGH);  // Power the joystick module

  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(buttons[i].pin, INPUT_PULLUP);
  }

  pinMode(STATUS_LED, OUTPUT);

  // Debug Output
  printStartupBanner();

  // Startup LED Pattern
  playStartupAnimation();

  Serial.println("\n✓ System Ready - Waiting for Robot Connection...\n");
}

// ========== MAIN LOOP ==========
void loop() {
  // Read joystick analog values
  readJoystick();

  // Process joystick movement
  processJoystickMovement();

  // Check all button inputs
  for (int i = 0; i < NUM_BUTTONS; i++) {
    processButtonPress(i);
  }

  // Debug output (throttled)
  printDebugInfo();

  delay(50);  // Main loop cycle time
}

// ========== JOYSTICK HANDLING ==========
void readJoystick() {
  joystick.xRaw = analogRead(JOY_X);
  joystick.yRaw = analogRead(JOY_Y);
  joystick.xDiff = joystick.xRaw - JOY_CENTER;
  joystick.yDiff = joystick.yRaw - JOY_CENTER;
}

void processJoystickMovement() {
  joystick.currentCommand = "";

  // Check if joystick is beyond deadzone
  if (abs(joystick.xDiff) > JOY_DEADZONE || abs(joystick.yDiff) > JOY_DEADZONE) {
    
    // Determine primary axis (Y or X)
    if (abs(joystick.yDiff) > abs(joystick.xDiff)) {
      // Vertical movement dominates
      if (joystick.yDiff > JOY_THRESHOLD) {
        joystick.currentCommand = "forward";
      } else if (joystick.yDiff < -JOY_THRESHOLD) {
        joystick.currentCommand = "backward";
      }
    } else {
      // Horizontal movement dominates
      if (joystick.xDiff > JOY_THRESHOLD) {
        joystick.currentCommand = "rotate_right";
      } else if (joystick.xDiff < -JOY_THRESHOLD) {
        joystick.currentCommand = "rotate_left";
      }
    }
  }

  // Send command if different from last and delay has passed
  if (joystick.currentCommand != "" && joystick.currentCommand != joystick.lastCommand) {
    if (millis() - joystick.lastCommandTime >= COMMAND_DELAY) {
      sendCommand(joystick.currentCommand);
      joystick.lastCommand = joystick.currentCommand;
      joystick.lastCommandTime = millis();
    }
  } else if (joystick.currentCommand == "") {
    joystick.lastCommand = "";
  }
}

// ========== BUTTON HANDLING ==========
void processButtonPress(int buttonIndex) {
  ButtonState& btn = buttons[buttonIndex];
  bool currentState = digitalRead(btn.pin);

  // Detect falling edge (HIGH → LOW)
  if (currentState == LOW && btn.lastState == HIGH) {
    // Check debounce
    if (millis() - btn.lastPressTime > DEBOUNCE_DELAY) {
      sendCommand(btn.command);
      btn.lastPressTime = millis();
      blinkStatusLED(2);  // Double blink for button press
    }
  }

  btn.lastState = currentState;
}

// ========== COMMUNICATION ==========
void sendCommand(const String& cmd) {
  BTSerial.println(cmd);
  Serial.print("[→ SENT] ");
  Serial.println(cmd);
  blinkStatusLED(1);
}

// ========== LED INDICATORS ==========
void blinkStatusLED(int blinks) {
  for (int i = 0; i < blinks; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(80);
    digitalWrite(STATUS_LED, LOW);
    if (i < blinks - 1) delay(60);
  }
}

void playStartupAnimation() {
  const int pattern[] = {100, 80, 100, 80, 200, 150};
  for (int i = 0; i < 6; i++) {
    digitalWrite(STATUS_LED, HIGH);
    delay(pattern[i]);
    digitalWrite(STATUS_LED, LOW);
    delay(80);
  }
}

// ========== DEBUG OUTPUT ==========
void printStartupBanner() {
  Serial.println("\n╔════════════════════════════════════════╗");
  Serial.println("║  ⚡ NEXUS BLUETOOTH CONTROLLER ⚡    ║");
  Serial.println("║    Cyberpunk Robot Command System    ║");
  Serial.println("╚════════════════════════════════════════╝");
  Serial.println();
  Serial.println("CONFIGURATION:");
  Serial.println("  Bluetooth Baud: 38400");
  Serial.println("  Joystick Deadzone: " + String(JOY_DEADZONE));
  Serial.println("  Joystick Threshold: " + String(JOY_THRESHOLD));
  Serial.println("  Command Delay: " + String(COMMAND_DELAY) + "ms");
  Serial.println();
  Serial.println("PINS:");
  Serial.println("  Joystick: A0 (X), A1 (Y), D2 (BTN)");
  Serial.println("  Buttons: D3 (Jump), D4 (Wave), D5 (Dance)");
  Serial.println("  Power: D9 (5V out), LED: D13");
  Serial.println();
}

void printDebugInfo() {
  unsigned long currentTime = millis();

  if (currentTime - lastDebugOutput >= DEBUG_INTERVAL) {
    Serial.println("\n--- JOYSTICK STATUS ---");
    Serial.print("  Raw: X=");
    Serial.print(joystick.xRaw);
    Serial.print(" Y=");
    Serial.println(joystick.yRaw);
    
    Serial.print("  Diff: X=");
    Serial.print(joystick.xDiff);
    Serial.print(" Y=");
    Serial.println(joystick.yDiff);
    
    if (joystick.lastCommand != "") {
      Serial.print("  Last: ");
      Serial.println(joystick.lastCommand);
    }

    lastDebugOutput = currentTime;
  }
}

/*
 * ========== HARDWARE WIRING GUIDE ==========
 * 
 * BLUETOOTH MODULE (HC-05/HC-06):
 * ├─ VCC    → Arduino 5V (with capacitor 100µF)
 * ├─ GND    → Arduino GND
 * ├─ TX     → Arduino D10 (via voltage divider)
 * └─ RX     → Arduino D11
 * 
 * VOLTAGE DIVIDER (For Bluetooth TX → Arduino RX):
 * ├─ Bluetooth TX → 1kΩ resistor → Arduino D10 → 2kΩ resistor → GND
 * 
 * JOYSTICK MODULE:
 * ├─ +5V    → Arduino D9 (via digitalWrite HIGH)
 * ├─ GND    → Arduino GND
 * ├─ VRx    → Arduino A0
 * ├─ VRy    → Arduino A1
 * └─ SW     → Arduino D2
 * 
 * ACTION BUTTONS (Momentary Switches):
 * ├─ Jump Button  → Arduino D3 (other pin to GND)
 * ├─ Wave Button  → Arduino D4 (other pin to GND)
 * └─ Dance Button → Arduino D5 (other pin to GND)
 * 
 * STATUS LED:
 * ├─ Anode (+)    → Arduino D13 (via 220Ω resistor)
 * └─ Cathode (-)  → Arduino GND
 * 
 * ========== BLUETOOTH PAIRING ==========
 * 
 * 1. Default HC-05/HC-06 PIN: 1234 or 0000
 * 2. Baud Rate: 38400 (already set in code)
 * 3. Once paired, use Python script to send/receive commands
 * 
 */