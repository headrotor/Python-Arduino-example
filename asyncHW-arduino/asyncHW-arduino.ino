/*
 
 Aysnchronous remote control over the serial line
 
 send "<1>\n" to turn on the LED, "<0>\n" to turn off
 
 Adapted from "SerialEvent," "blink," and "button"
 examples by Tom Igoe
 
 This example code is in the public domain.
 
 http://www.arduino.cc/en/Tutorial/SerialEvent
 
 */

// Pin 13 has an LED connected on most Arduino boards.
// give it a name:
const int led = 13;

const int buttonPin = 2;     // the number of the pushbutton pin
int lastState = LOW;           // use to detect change of button state
int buttonState = LOW;         // variable for reading the pushbutton status

// the following variables are long's because the time, measured in miliseconds,
// will quickly become a bigger number than can be stored in an int.
long lastDebounceTime = 50;  // the last time the output pin was toggled
long debounceDelay = 50;    // the debounce time; increase if the output flickers
long wait = 0;

String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

boolean chflag = false;

void setup() {
  // initialize serial:
  Serial.begin(9600);
  //Serial.println("Hello"); 
  // reserve 200 bytes for the inputString:
  inputString.reserve(20);
  pinMode(led, OUTPUT);
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT_PULLUP);       
  digitalWrite(buttonPin, HIGH);       // turn on pullup resistors
}


void loop() {
  int reading; 
  // print the string when a newline arrives:
  if (stringComplete) {
    if (inputString[0] == '0') {
      //Serial.println("off!"); 
      digitalWrite(led, LOW);
    }
    else {
      //Serial.println("on!"); 
      digitalWrite(led, HIGH);
    }
    // clear the string:
    inputString = "";
    stringComplete = false;
  }

  // poll the button connected to pin
  // for less latency use a hardware interrupt
  reading = digitalRead(buttonPin);

  if ((reading != lastState)) {
    lastDebounceTime = millis();
    chflag = true;
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    buttonState = reading;
    if (chflag) {
      chflag = false;
      if (buttonState == 0)
        Serial.println("0");
      else  
        Serial.println("1");
    }
  }
  lastState = reading;
}

/*
  SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read(); 
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    } 
  }
}













