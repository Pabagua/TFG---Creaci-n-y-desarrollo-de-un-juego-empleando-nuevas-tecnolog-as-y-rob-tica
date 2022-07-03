const int motor1_f = P1_4;
const int motor1_b = P1_5;
const int motor2_f = P2_5;
const int motor2_b = P2_4;

unsigned int CNYizq = 0, CNYcentro = 0, CNYder = 0;
int tOn = 0, tOff = 0, tAux = 0;

void setup() {
  // MOTOR1
  pinMode(motor1_f, OUTPUT);
  pinMode(motor1_b, OUTPUT);

  // MOTOR2
  pinMode(motor2_f, OUTPUT);
  pinMode(motor2_b, OUTPUT);
  
  // SENSORES CNY70
  pinMode(P6_1, INPUT); //BLANCO
  pinMode(P6_2, INPUT); //MARRON
  pinMode(P6_3, INPUT); //ROJO
  
  Serial.begin(9600);
  Serial.println("Empezamos!");
}

void mode_motores(int mode){
  if(mode == 0){
    digitalWrite(motor1_f, LOW); 
    digitalWrite(motor1_b, LOW);
    digitalWrite(motor2_f, LOW); 
    digitalWrite(motor2_b, LOW);
  }
  else if(mode == 1){ //MUCHA DERECHA
    tOff = 600;
    tOn = 1000-tOff;        
     
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_b, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor1_f, LOW);  
    digitalWrite(motor2_b, LOW);
    delayMicroseconds(tOff);   
  }
  else if(mode == 2){ //POCA DERECHA
    tAux = 103;   
    tOff = 680;
    tOn = 1000-tOff-tAux;      
    
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor2_f, LOW);
    delayMicroseconds(tAux); 
    digitalWrite(motor1_f, LOW);  
    delayMicroseconds(tOff);
  }
  else if(mode == 3){ //RECTO
    tAux = 80; // 27-750  
    tOff = 720;
    tOn = 1000-tOff-tAux;      
    
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor2_f, LOW);
    delayMicroseconds(tAux); 
    digitalWrite(motor1_f, LOW);  
    delayMicroseconds(tOff);
  }
  else if(mode == 4){ //POCA IZQUIERDA
    tAux = 130;   
    tOff = 680;
    tOn = 1000-tOff-tAux;      
    
    digitalWrite(motor1_f, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor1_f, LOW);
    delayMicroseconds(tAux); 
    digitalWrite(motor2_f, LOW);  
    delayMicroseconds(tOff);
  }
  else if(mode == 5){ //MUCHA IZQUIERDA
    tOff = 600;
    tOn = 1000-tOff;      
    
    digitalWrite(motor1_b, HIGH);
    digitalWrite(motor2_f, HIGH);
    delayMicroseconds(tOn); 
    digitalWrite(motor1_b, LOW);
    digitalWrite(motor2_f, LOW);  
    delayMicroseconds(tOff);
  }
}

int delayCNY70 = 0, contador_arranque = 0;
bool avisado = false, casillaNueva = true;
int casillasAMover = 0;
char valor;

void loop() {
  if (Serial.available()){//Si hay una caracter en el buffer serial el programa entra aquí.
    valor = Serial.read();// Se lee el valor numérico en el puerto serie.
    if(valor >= '0' && valor <= '9'){
      casillasAMover = valor - '0';
      contador_arranque = 0;
    }
    if (valor == '0'){
      Serial.print('0');
    }
  }
  if(casillasAMover != 0){
    if(contador_arranque >= 90){ 
      if(delayCNY70 == 60){
        CNYizq = analogRead(P6_1);
        CNYcentro = analogRead(P6_2);
        CNYder = analogRead(P6_3);
        delayCNY70 = 0;
        avisado = false;
      }
      
      if(CNYizq > 1500 && CNYizq < 4095 && CNYcentro > 1500 && CNYcentro < 4095 && CNYder > 1500 && CNYder < 4095){ //CASILLA DETECTADA
        if(casillaNueva == true){
          casillasAMover--;
          if(casillasAMover == 0){
            Serial.print('0');
          }
        }
        casillaNueva = false;
      }else{
        casillaNueva = true;
      }
    
      if((CNYizq < 2500 && CNYcentro < 2500 && CNYder < 2500) || casillaNueva == false){ //ESTA CENTRADO
        mode_motores(3);
      }
      else if(CNYizq > 2500 && CNYcentro > 2500 && CNYder < 2500){      //SE SALE POR LA IZQUIERDA MUCHO
        mode_motores(1);
      }
      else if(CNYizq > 2500 && CNYcentro < 2500 && CNYder < 2500){ //SE SALE POR LA IZQUIERDA POCO
        mode_motores(2);
      }
      else if(CNYizq < 2500 && CNYcentro < 2500 && CNYder > 2500){ //SE SALE POR LA DERECHA POCO
        mode_motores(4);
      }
      else if(CNYizq < 2500 && CNYcentro > 2500 && CNYder > 2500){ //SE SALE POR LA DERECHA MUCHO
        mode_motores(5);
      }
      else if(CNYizq > 2500 && CNYcentro > 2500 && CNYder > 2500 && casillaNueva == true){ //TOTALMENTE PERDIDO - AVISAR AL USUARIO
        mode_motores(5);
        if(avisado == false){
          //Serial.println("Perdido - Situame en el circuito");
          avisado = true;
        }
      }
      
      delayCNY70++;
    }
    else{
      tAux = 40;   
      tOff = 500;
      tOn = 1000-tOff-tAux;      
      
      digitalWrite(motor1_f, HIGH);
      digitalWrite(motor2_f, HIGH);
      delayMicroseconds(tOn); 
      digitalWrite(motor2_f, LOW);
      delayMicroseconds(tAux); 
      digitalWrite(motor1_f, LOW);  
      delayMicroseconds(tOff);
      contador_arranque++;
    }
  }
}
