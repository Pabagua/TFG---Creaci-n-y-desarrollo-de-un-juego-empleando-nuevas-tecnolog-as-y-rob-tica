import serial
import time

def retrieveData():
    data = ser.readline().decode('ascii')
    return data

def esperar():
    esperaJuego = True
    while esperaJuego == True:
        fJuego = open("juegoAbluetooth.txt")
        datoJB = fJuego.read()
        fJuego.close()
        if datoJB == '7':
            esperaJuego = False
    
pruebas = jugando = True
enviado = False
numPlayer = uInput =  1
turno = 1
#ser = serial.Serial("COM15", 9600, timeout = 1)

#Antes de empezar informo de que no esta haciendo nada
fBluetooth=open("bluetoothAjuego.txt","w")
fBluetooth.write('0')
fBluetooth.close()

esperar()
print("Comprobando la conexion de los robots...")

while(pruebas):
    #Puertos 6-15-27-25
    if numPlayer == 1:
        ser = serial.Serial("COM15", 9600, timeout = 1)
    elif numPlayer == 2:
        ser = serial.Serial("COM6", 9600, timeout = 1)
    elif numPlayer == 3:
        ser = serial.Serial("COM27", 9600, timeout = 1)
    elif numPlayer == 4:
        ser = serial.Serial("COM22", 9600, timeout = 1)
        
    if enviado == False:
        send = bytes('0', encoding= 'utf-8')
        ser.write(send)
        enviado = True
    
    while ser.inWaiting and pruebas: 
        data = retrieveData()
        if data == '0':
            print("Robot ",numPlayer," conectado!")
            enviado = False
            numPlayer += 1
            fBluetooth=open("bluetoothAjuego.txt","w")
            fBluetooth.write(str(numPlayer-1))
            fBluetooth.close()
            if numPlayer == 5:  
                print("Todos estan conectados!")
                pruebas = False
                enviado = False
                numPlayer = 1
                time.sleep(4)
            break

#esperar()
print("Empezando el juego...")
fBluetooth=open("bluetoothAjuego.txt","w")
fBluetooth.write('0')
fBluetooth.close()

while(jugando):
    fJuego = open("juegoAbluetooth.txt")
    datoJB = fJuego.read()
    fJuego.close()
    
    if datoJB == '0':
        fBluetooth=open("bluetoothAjuego.txt","w")
        fBluetooth.write('0')
        fBluetooth.close()
    elif datoJB >= '1' and datoJB <= '7':
        #Informar al juego de que quite el modo negro
        fBluetooth=open("bluetoothAjuego.txt","w")
        fBluetooth.write('5')
        fBluetooth.close()
            
        if numPlayer == 1: # and turno != 1:
            ser = serial.Serial("COM15", 9600, timeout = 1)
        elif numPlayer == 2:
            ser = serial.Serial("COM6", 9600, timeout = 1)
        elif numPlayer == 3:
            ser = serial.Serial("COM27", 9600, timeout = 1)
        elif numPlayer == 4:
            ser = serial.Serial("COM22", 9600, timeout = 1)
            
        print("Turno ", turno, " - Jugador ", numPlayer)
        
        if enviado == False:
            if datoJB == '7':
                datoJB = '0'
            print("Mover ",datoJB," casillas")
            send = bytes(datoJB, encoding= 'utf-8')
            ser.write(send)
            enviado = True
        
        while ser.inWaiting and jugando: 
            data = retrieveData()
            if data == '0':
                print("Movimiento finalizado!")
                enviado = False
                numPlayer += 1
                if numPlayer == 5:
                    numPlayer = 1
                    turno += 1
                fBluetooth=open("bluetoothAjuego.txt","w")
                fBluetooth.write('0')
                fBluetooth.close()
                time.sleep(5)
                break
    elif datoJB == '8':
        jugando = False