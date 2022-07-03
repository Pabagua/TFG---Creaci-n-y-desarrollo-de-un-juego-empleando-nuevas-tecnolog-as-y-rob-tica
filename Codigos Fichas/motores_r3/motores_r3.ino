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
const int motor2_f = P2_5;
const int motor2_b = P2_4;

int t1 = 0, t2 = 0, taux = 0;
int tOn = 0, tOff = 0;

char valor = '0';

int mode = 0;

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

  // inicializo el motor2
  pinMode(motor2_f, OUTPUT);
  pinMode(motor2_b, OUTPUT);

  // inicio el monitor serie para controlar los valores
  Serial.begin(9600);
  Serial.println("Empezamos");
//  bluetooth.begin(38400);
}

void loop(){
  //motor 1 es el izquierdo y motor 2 el derecho
  if (Serial.available()){//Si hay una caracter en el buffer serial el programa entra aquí.
    valor = Serial.read();// Se lee el valor numérico en el puerto serie.
    if (valor  == '0'){
      mode = 0;
      Serial.print("Apagado\r\n");
    }
    else if(valor == '1'){
      mode = 1;
      Serial.print("Mucha derecha\r\n");
    }
    else if(valor == '2'){
      mode = 2;
      Serial.print("Poca derecha\r\n");
    }
    else if(valor == '3'){
      mode = 3;
      Serial.print("Recto\r\n");
    }
    else if(valor == '4'){
      mode = 4;
      Serial.print("Poca izquierda\r\n");
    }
    else if(valor == '5'){
      mode = 5;
      Serial.print("Mucha izquierda\r\n");
    }
    else if(valor == '6'){
      mode = 6;
      Serial.print("M1 adelante\r\n");
    }
    else if(valor == '7'){
      mode = 7;
      Serial.print("M1 atras\r\n");
    }
    else if(valor == '8'){
      mode = 8;
      Serial.print("M2 adelante\r\n");
    }
    else if(valor == '9'){
      mode = 9;
      Serial.print("M2 atras\r\n");
    }
    else if(valor == '10'){
      mode = 10;
      Serial.print("Adelante general\r\n");
    }
  }
  if(mode == 0){
    digitalWrite(motor1_f, LOW); 
    digitalWrite(motor1_b, LOW);
    digitalWrite(motor2_f, LOW); 
    digitalWrite(motor2_b, LOW);
  }
  else if(mode == 1){ //MUCHA DERECHA
    t2= 650;
    t1= 1000-t2;        
     
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_b, HIGH);
    delayMicroseconds(t1); 
    digitalWrite(motor2_b, LOW);
    digitalWrite(motor1_f, LOW);
    delayMicroseconds(t2);   
  }
  else if(mode == 2){ //POCA DERECHA
    taux = 200;   //130 - 700 bien
    tOff= 650;
    tOn= 1000-tOff-taux;      
    
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor2_f, LOW);
    delayMicroseconds(taux); 
    digitalWrite(motor1_f, LOW);  
    delayMicroseconds(tOff);
  }
  else if(mode == 3){ //RECTO
    tOff= 750;
    tOn= 1000-tOff;      
    
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor1_f, LOW);
    digitalWrite(motor2_f, LOW);  
    delayMicroseconds(tOff);
  }
  else if(mode == 4){ //POCA IZQUIERDA
    taux = 200;   //130 - 700 bien
    tOff= 650;
    tOn= 1000-tOff-taux;      
    
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor1_f, LOW);
    delayMicroseconds(taux); 
    digitalWrite(motor2_f, LOW);  
    delayMicroseconds(tOff);
  }
  else if(mode == 5){ //MUCHA IZQUIERDA
    t2= 650;
    t1= 1000-t2;      
    
    digitalWrite(motor1_b, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(t1); 
    digitalWrite(motor1_b, LOW);  
    digitalWrite(motor2_f, LOW);
    delayMicroseconds(t2);
  }
  
  //PRUEBAS DE CADA RUEDA
  else if(mode == 6){ 
    tOff= 700;
    tOn= 1000-tOff;        
     
    digitalWrite(motor1_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor1_f, LOW);  
    delayMicroseconds(tOff);   
  }
  else if(mode == 7){ 
    tOff= 700;
    tOn= 1000-tOff;        
     
    digitalWrite(motor1_b, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor1_b, LOW);  
    delayMicroseconds(tOff);   
  }
  else if(mode == 8){ 
    tOff= 700;
    tOn= 1000-tOff;        
     
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor2_f, LOW);  
    delayMicroseconds(tOff);   
  }
  else if(mode == 9){ 
    tOff= 700;
    tOn= 1000-tOff;        
     
    digitalWrite(motor2_b, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor2_b, LOW);  
    delayMicroseconds(tOff);   
  }
  else if(mode == 19){ 
    tOff= 700;
    tOn= 1000-tOff;        
     
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor1_f, LOW); 
    digitalWrite(motor2_f, LOW); 
    delayMicroseconds(tOff);   
  }
}
