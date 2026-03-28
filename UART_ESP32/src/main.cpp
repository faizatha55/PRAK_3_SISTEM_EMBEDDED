#include <Arduino.h>

const int led1 = 18;
const int led2 = 19;
const int sw1  = 22;
const int sw2  = 23;

void setup() {
    Serial.begin(115200);
    pinMode(led1, OUTPUT);
    pinMode(led2, OUTPUT);
    pinMode(sw1, INPUT_PULLUP);
    pinMode(sw2, INPUT_PULLUP);
}

void loop() {
    // Monitoring Switch
    static int last1 = HIGH, last2 = HIGH;
    int s1 = digitalRead(sw1);
    int s2 = digitalRead(sw2);

    if (s1 == LOW && last1 == HIGH) Serial.println("Switch 1 Ditekan!");
    if (s2 == LOW && last2 == HIGH) Serial.println("Switch 2 Ditekan!");
    
    last1 = s1; last2 = s2;

    // Control LED dari GUI
    if (Serial.available() > 0) {
        char cmd = Serial.read();
        if (cmd == '1') digitalWrite(led1, !digitalRead(led1));
        if (cmd == '2') digitalWrite(led2, !digitalRead(led2));
    }
}