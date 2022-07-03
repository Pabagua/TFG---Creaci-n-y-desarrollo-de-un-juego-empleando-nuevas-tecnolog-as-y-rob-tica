//////////////////////////////////////
//  Creado por: ALFA                //
//  País: México                    //
//  Página WEB: galfama.blogspot.mx //
//  Fecha: 19/02/2013               //
//////////////////////////////////////

/*  Descripción

Programa que controla el encendido/apagado de los LEDs 
(verde, rojo) usando el módulo serial bluetooth modelo HC-05, 
implementado en el MSP430 Launchpad de Texas Instruments, con el
microcontrolador MSP430G2553 a una frecuencia de reloj de de 16MHz.

Los comandos a recibir son: El 1 -enciende LED rojo, 2 -apaga LED rojo,
3 -enciende LED verde, 4 apaga -LED verde, otro caracter apaga ambos LEDs.

Nota: Para el envío de datos por bluetooth entre el dispositivo
y la tarjeta se utiliza el programa para Android BlueTerm.

*/

// Se inicializa el puerto serie a 9600 bauds
// Y la variable "valor" de tipo caracter.
// Así como los pines de los LEDs (verde, rojo), se definen como salidas.

char valor=0;
unsigned int RxBlue = P6_3;
unsigned char eBlue = 0;

void setup()
{
  Serial.begin(9600);
  pinMode (RED_LED, OUTPUT);
  pinMode (GREEN_LED, OUTPUT);
  digitalWrite(RED_LED, HIGH);//Inicialmente se apagan los LEDs.
  digitalWrite(GREEN_LED, HIGH);
  Serial.println("Empezamos");
}

void loop()  //Bucle infinito
{/*
  eBlue = analogRead(RxBlue);
  Serial.println(eBlue);
  if(eBlue == 1){
    Serial.println(eBlue);
    delay(1000);
  }*/
  if (Serial.available())//Si hay una caracter en el buffer serial
                         //el programa entra aquí.
 { 
  valor = Serial.read();// Se lee el valor numérico en el puerto serie.
  if (valor == '1')//Si el valor es 1.
  {
    digitalWrite(RED_LED, HIGH);  //Se enciende el led rojo.
    Serial.print("Led rojo encendido\r\n");//Se envía el mensaje por el puerto serie,
  }                                        //un retorno y salto de línea.
  
  else if (valor == '2')
  {
    digitalWrite(RED_LED, LOW);  //Se apaga el led rojo.
    Serial.print("Led rojo apagado\r\n");
  }
 
  else if (valor == '3')
  {
    digitalWrite(GREEN_LED, HIGH);  //Se enciende el led verde.
    Serial.print("Led verde encendido\r\n");
  }
  
  else if (valor == '4')
  {
    digitalWrite(GREEN_LED, LOW);  //Se apaga el led verde.
    Serial.print("Led verde apagado\r\n");
  }
  /*
  else // Si se envía un caracter distinto de 1 - 4, los leds se apagan.
  {
    digitalWrite(RED_LED, LOW);  //Se apaga el led rojo.
    digitalWrite(GREEN_LED, LOW);//Se apaga el led verde.
    Serial.print("Ambos leds apagados\r\n");
  }  */
 }
}
