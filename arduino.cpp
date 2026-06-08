int buzzerPin = 10;
int red1 = 11;
int greenPin = 12;
int red2 = 13;

int green2 = 9;
int red3 = 8;
int green3 = 7;

bool alarmActive = false;

void setup() {
    Serial.begin(9600);

    pinMode(buzzerPin, OUTPUT);
    pinMode(red1, OUTPUT);
    pinMode(greenPin, OUTPUT);
    pinMode(red2, OUTPUT);
    pinMode(green2, OUTPUT);
    pinMode(red3, OUTPUT);
    pinMode(green3, OUTPUT);

    digitalWrite(greenPin, HIGH);
    digitalWrite(green2, HIGH);
    digitalWrite(green3, HIGH);

    digitalWrite(red1, LOW);
    digitalWrite(red2, LOW);
    digitalWrite(red3, LOW);

    digitalWrite(buzzerPin, LOW);
}

void loop() {
    if (Serial.available() > 0) {
        char command = Serial.read();

        if (command == 'R') {
            alarmActive = true;
            digitalWrite(greenPin, LOW);
            digitalWrite(green2, LOW);
            digitalWrite(green3, LOW);
        }

        else if (command == 'S') {
            alarmActive = false;

            digitalWrite(red1, LOW);
            digitalWrite(red2, LOW);
            digitalWrite(red3, LOW);
            digitalWrite(buzzerPin, LOW);

            digitalWrite(greenPin, HIGH);
            digitalWrite(green2, HIGH);
            digitalWrite(green3, HIGH);
        }
    }

    if (alarmActive == true) {
        digitalWrite(red1, HIGH);
        digitalWrite(red3, HIGH);
        digitalWrite(red2, LOW);
        digitalWrite(buzzerPin, HIGH);
        delay(250);

        digitalWrite(red1, LOW);
        digitalWrite(red3, LOW);
        digitalWrite(red2, HIGH);
        digitalWrite(buzzerPin, LOW);
        delay(250);
    }
}