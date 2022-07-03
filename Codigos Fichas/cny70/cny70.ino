const int motor1_f = P1_4;
const int motor1_b = P1_5;
const int motor2_f = P2_5;
const int motor2_b = P2_4;

void setup() {
  /*/motores--> amarillo-naranja-marron-rojo -- 2.5-2.4-1.5-1.4
  // MOTOR1
  pinMode(motor1_f, OUTPUT);
  pinMode(motor1_b, OUTPUT);

  // MOTOR2
  pinMode(motor2_f, OUTPUT);
  pinMode(motor2_b, OUTPUT);*/
  
  // SENSORES CNY70
  pinMode(P6_1, INPUT); //BLANCO - MORADO
  pinMode(P6_2, INPUT); //MARRON - GRIS
  pinMode(P6_3, INPUT); //ROJO - AZUL
  
  Serial.begin(9600);
  Serial.println("Empezamos!");
}

unsigned int CNYizq = 0, CNYcentro = 0, CNYder = 0;
int modo_motores = 0;
int tOn = 0, tOff = 0, tAux = 0;

void loop() {
  // put your main code here, to run repeatedly: 
  CNYizq = analogRead(P6_1);
  CNYcentro = analogRead(P6_2);
  CNYder = analogRead(P6_3);
  Serial.print("Izquierda: ");
  Serial.print(CNYizq);
  Serial.print(" - Centro: ");
  Serial.print(CNYcentro);
  Serial.print(" - Derecha: ");
  Serial.println(CNYder);
  delay(100);
}
