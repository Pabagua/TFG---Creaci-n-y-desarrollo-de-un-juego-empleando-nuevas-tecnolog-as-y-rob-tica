//#include <SoftwareSerial.h>

//const int rxPin = P3_4, txPin = P3_3;
//SoftwareSerial bluetooth(rxPin,txPin)
// constants won't change. They're used here to 
// set pin numbers:
const int forwardButton = PUSH1;     // the number of the pushbutton pin
const int backwardButton = PUSH2;     // the number of the pushbutton pin
const int greenLedPin =  GREEN_LED;      // the number of the LED pin
const int redLedPin =  RED_LED;      // the number of the LED pin

const int motor1_f = P1_4;
const int motor1_b = P1_5;
const int motor2_f = P2_4;
const int motor2_b = P2_5;

int motor1ValueF = 0, motor1ValueB = 0;
int motor2ValueF = 0, motor2ValueB = 0;

int button1State = 0, button2State = 0;         // variable for reading the pushbutton status

bool mode = true;

void setup() {
  // inicializo los leds
  pinMode(greenLedPin, OUTPUT);    
  pinMode(redLedPin, OUTPUT);   
  
  // inicializo los botones
  pinMode(forwardButton, INPUT_PULLUP);     
  pinMode(backwardButton, INPUT_PULLUP);  

  // inicializo el motor1
  pinMode(motor1_f, OUTPUT);
  pinMode(motor1_b, OUTPUT);

  /*/ inicializo el motor2
  pinMode(motor2_f, OUTPUT);
  pinMode(motor2_b, OUTPUT);*/

  // inicio el monitor serie para controlar los valores
  Serial.begin(9600);

//  bluetooth.begin(38400);
}

void loop(){
  // read the state of the pushbutton value:
  button1State = digitalRead(forwardButton);
  button2State = digitalRead(backwardButton);

  // check if the pushbutton is pressed.
  // if it is, the buttonState is HIGH:
  if (button1State == HIGH && button2State == HIGH) {   //PARADO - LOS DOS BOTONES SIN PULSAR    
    digitalWrite(greenLedPin, HIGH); 
    digitalWrite(redLedPin, HIGH);  
    motor1ValueF = 0;
    motor1ValueB = 0;
    motor2ValueF = 0;
    motor2ValueB = 0;
  } 
  if(mode == true){ //MODO ADELANTE-ATRAS
    if(button1State == LOW && button2State == HIGH){ //ADELANTE
      digitalWrite(greenLedPin, HIGH); 
      digitalWrite(redLedPin, LOW); 
      motor1ValueF = 2000; // 5000 = rapido -- 3000 = lento
      motor1ValueB = 0;
      motor2ValueF = 0;
      motor2ValueB = 4000; 
    }
    else if(button1State == HIGH && button2State == LOW){ //ATRAS
      digitalWrite(greenLedPin, LOW); 
      digitalWrite(redLedPin, HIGH); 
      motor1ValueF = 0;
      motor1ValueB = 2000; //5000
      motor2ValueF = 4000;
      motor2ValueB = 0; 
    }
  }
  else{ // MODO DERECHA-IZQUIERDA
    if(button1State == LOW && button2State == HIGH){ //DERECHA
      digitalWrite(greenLedPin, HIGH); 
      digitalWrite(redLedPin, LOW); 
      motor1ValueF = 2000; // 5000 = rapido -- 3000 = lento
      motor1ValueB = 0;
      motor2ValueF = 4000;
      motor2ValueB = 0; 
    }
    else if(button1State == HIGH && button2State == LOW){ //IZQUIERDA
      digitalWrite(greenLedPin, LOW); 
      digitalWrite(redLedPin, HIGH); 
      motor1ValueF = 0;
      motor1ValueB = 2000; //5000
      motor2ValueF = 0;
      motor2ValueB = 4000; 
    }
  }

  if(button1State == LOW && button2State == LOW){ // CAMBIO DE MODO
    mode = !mode;
    delay(200);
  }
  
  analogWrite(motor1_f,motor1ValueF);
  analogWrite(motor1_b,motor1ValueB);
  analogWrite(motor2_f,motor2ValueF);
  analogWrite(motor2_b,motor2ValueB);
  Serial.print("Mode ");
  Serial.print(mode);
  Serial.print(" -> M1 F: ");
  Serial.print(motor1ValueF);
  Serial.print(" B: ");
  Serial.print(motor1ValueB);
  Serial.print(" - M2 F: ");
  Serial.print(motor2ValueF);
  Serial.print(" B: ");
  Serial.println(motor2ValueB);
  delay(10);
}
