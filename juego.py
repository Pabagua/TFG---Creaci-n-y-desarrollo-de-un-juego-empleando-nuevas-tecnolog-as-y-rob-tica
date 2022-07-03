#!/usr/bin/python3.4

# Setup Python ----------------------------------------------- #
import pygame, sys
import json, os
import cv2
import numpy as np
import glob
from random import randint
import time 
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('EL JUEGO DE BLAPÍN')
ancho = 1280
alto = 720
screen = pygame.display.set_mode((ancho, alto),0,32)
 
font = pygame.font.SysFont(None, 20)
botonSound = pygame.mixer.Sound("./sonido/boton.mp3")

click = False
pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
controlRaton = False

# ----------------------------------------- CALIBRACION DE LA CAMARA -----------------------------------------
class calibracion():
    def __init__(self):
        self.tablero = (9,6)
        self.tam_frame = (1280,720)
        
        #Criterio para identificar las esquinas
        self.criterio = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        #Puntos del tablero
        self.puntos_obj = np.zeros((self.tablero[0] * self.tablero[1], 3), np.float32)
        self.puntos_obj[:,:2] = np.mgrid[0:self.tablero[0], 0:self.tablero[1]].T.reshape(-1,2)
        
        #Listas para los puntos reales y de la imagen
        self.puntos_3d = []
        self.puntos_img = []
    
    def calibracion_cam(self):
        fotos = glob.glob('./calibrar/*.jpg')
        for foto in fotos:
            #print(foto)
            img = cv2.imread(foto)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            
            #Buscar las esquinas del tablero
            ret, esquinas = cv2.findChessboardCorners(gray, self.tablero, None)
            
            if ret == True:
                self.puntos_3d.append(self.puntos_obj)
                esquinas2 = cv2.cornerSubPix(gray,esquinas, (11,11), (-1,-1), self.criterio)
                self.puntos_img.append(esquinas2)
                #cv2.drawChessboardCorners(img, self.tablero, esquinas2, ret)
                #cv2.imshow("IMAGEN", img)
                #cv2.waitKey(0)
                
        #Calibracion de la camara
        ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(self.puntos_3d, self.puntos_img, self.tam_frame, None, None)
        
        return cameraMatrix, dist, rvecs, tvecs
    
# ----------------------------------------- WEBCAM Y DETECCION ----------------------------------------- 
# -- Inicio arucos -- 
#Inicializar los parámetros del detector de ARUCOS
parametros = cv2.aruco.DetectorParameters_create()

#Cargar los diccionarios de los ARUCOS a utilizar
diccionario = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)

# -- Inicio webcam -- 
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
#Gets fps of your camera
fps = cap.get(cv2.CAP_PROP_FPS)
#If your camera can achieve 60 fps
#Else just have this be 1-30 fps
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(3,ancho)
cap.set(4,alto)
cont = 0
calibracion = calibracion()
matrix, dist, rVec, tVec = calibracion.calibracion_cam()
#print("Matriz de la camara: ", matrix)
#print("Coeficiente de distorsion", dist)

# -- Cargo el fondo del tablero --
tablero1 = cv2.imread("./tableros/tablero1.png")
monedasT1 = [3, 1, 2, 1, 0, 1, 5, 3, 1, 2, -5, 1]
#monedasT1 = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
tablero2 = cv2.imread("./tableros/tablero2.png")
monedasT2 = [1, 2, 1, 3, 0, 1, 5, 1, 3, 1, -5, 2]
tablero3 = cv2.imread("./tableros/tablero3.png")
monedasT3 = [2, 3, 1, 2, 0, 1, 5, 3, 1, 1, -5, 1]

numTablero = 1
imagenFondo = tablero1
monedasT = monedasT1

fondoX = 2420
fondoY = 1480
pointsMarkers = []

# ----------------------------------------- MANDO PS4 ----------------------------------------- 
#Initialize controller
joysticks = []
for i in range(pygame.joystick.get_count()):
    joysticks.append(pygame.joystick.Joystick(i))
for joystick in joysticks:
    joystick.init()
#print(pygame.joystick.get_count())
with open(os.path.join("ps4_keys.json"), 'r+') as file:
    button_keys = json.load(file)
# 0: Left analog horizonal, 1: Left Analog Vertical, 2: Right Analog Horizontal
# 3: Right Analog Vertical 4: Left Trigger, 5: Right Trigger
analog_keys = {0:0, 1:0, 2:0, 3:0, 4:-1, 5: -1 }

LEFT, RIGHT, UP, DOWN = False, False, False, False
        
            
# ----------------------------------------- SPRITES ----------------------------------------- 
class Puntero(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = pygame.image.load("./sprites/puntero.png").convert()
		self.image.set_colorkey([255,255,255])
		self.rect = self.image.get_rect()

puntero = Puntero()
puntero.rect.x = ancho/2
puntero.rect.y = alto/2
punteroList = pygame.sprite.Group()
punteroList.add(puntero)

class Listo(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = pygame.image.load("./sprites/listoJug.png").convert()
		self.image.set_colorkey([0,0,0])
		self.rect = self.image.get_rect()
        
class Comenzar(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.image = pygame.image.load("./sprites/pulsaParaComenzar.png").convert()
		self.image.set_colorkey([0,0,0])
		self.rect = self.image.get_rect()

class Moneda(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		imageAux = pygame.image.load("./sprites/coin.png").convert()
		self.image = pygame.transform.scale(imageAux, (75,75))
		self.image.set_colorkey([0,0,0])
		self.rect = self.image.get_rect()

moneda = Moneda()
moneda.rect.x = 10
moneda.rect.y = 85

spritesJuego = pygame.sprite.Group()
spritesJuego.add(moneda)

class botonX(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.imageOrigen = pygame.image.load("./sprites/botonX.png").convert()
		self.imageOrigen.set_colorkey([6,148,32])
		self.image = pygame.transform.scale(self.imageOrigen, (40,40))
		self.rect = self.image.get_rect()
		self.rect.x = 1100
		self.rect.y = 670
    
botonX = botonX()
spritesCarga = pygame.sprite.Group()
spritesCarga.add(botonX)

class botonX2(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.imageOrigen = pygame.image.load("./sprites/botonX.png").convert()
		self.imageOrigen.set_colorkey([6,148,32])
		self.image = pygame.transform.scale(self.imageOrigen, (100,100))
		self.rect = self.image.get_rect()
		self.rect.x = 307
		self.rect.y = 90

botonX2 = botonX2()
    
class botonTri(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		imagen_aux = pygame.image.load("./sprites/botonTri.png").convert()
		self.image = pygame.transform.scale(imagen_aux, (100,100))
		self.image.set_colorkey([6,148,32])

		self.rect = self.image.get_rect()
		self.rect.x = 420
		self.rect.y = 470

class botonO(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		imagen_aux = pygame.image.load("./sprites/botonO.png").convert()
		self.image = pygame.transform.scale(imagen_aux, (100,100))
		self.image.set_colorkey([6,148,32])

		self.rect = self.image.get_rect()
		self.rect.x = 900
		self.rect.y = 470

class botonCua(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		imagen_aux = pygame.image.load("./sprites/botonCua.png").convert()
		self.image = pygame.transform.scale(imagen_aux, (40,40))
		self.image.set_colorkey([6,148,32])

		self.rect = self.image.get_rect()
		self.rect.x = 50
		self.rect.y = 670
        
botonTri = botonTri()
botonO = botonO()
botonCua = botonCua()
spritesJuego.add(botonCua)

spritesCarcel = pygame.sprite.Group()
spritesCarcel.add(botonTri)
spritesCarcel.add(botonO)


class Tablero(pygame.sprite.Sprite):
	def __init__(self, imagen):
		super().__init__()
		imageAux = pygame.image.load(imagen).convert()
		self.image = pygame.transform.scale(imageAux, (480,270))
		self.image.set_colorkey([0,0,0])
		self.rect = self.image.get_rect()


class Dado(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		self.dado1 = pygame.image.load("./dado/1.png").convert()
		self.dado2 = pygame.image.load("./dado/2.png").convert()
		self.dado3 = pygame.image.load("./dado/3.png").convert()
		self.dado4 = pygame.image.load("./dado/4.png").convert()
		self.dado5 = pygame.image.load("./dado/5.png").convert()
		self.dado6 = pygame.image.load("./dado/6.png").convert()
		self.numero = 1
		
		self.image = pygame.transform.scale(self.dado1, (200,200))
		self.image.set_colorkey([6,148,32])

		self.rect = self.image.get_rect()
		self.rect.x = 540
		self.rect.y = 270
    
	def update(self):
		if self.numero == 1:
			self.image = pygame.transform.scale(self.dado1, (200,200))
		elif self.numero == 2:
			self.image = pygame.transform.scale(self.dado2, (200,200))
		elif self.numero == 3:
			self.image = pygame.transform.scale(self.dado3, (200,200))
		elif self.numero == 4:
			self.image = pygame.transform.scale(self.dado4, (200,200))
		elif self.numero == 5:
			self.image = pygame.transform.scale(self.dado5, (200,200))
		elif self.numero == 6:
			self.image = pygame.transform.scale(self.dado6, (200,200))
		self.image.set_colorkey([6,148,32])
        
# ----------------------------------------- FONDOS ----------------------------------------- 

class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)  #call Sprite initializer
        self.image = pygame.image.load(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location

fondoMenu = Background('./pantallas/menu.png', [0,0])
fondoEsperaJug = Background('./pantallas/espera_jugadores.png', [0,0])
fondoElegirTablero = Background('./pantallas/elegirTablero.png', [0,0])
fondoCreditos = Background('./pantallas/creditos.png', [0,0])


# ----------------------------------------- FUENTES Y COLORES -----------------------------------------
#screen = pygame.display.set_mode((1280, 720))
bigFont = pygame.freetype.SysFont("Jokerman", 120)
mediumFont = pygame.freetype.SysFont("Jokerman", 80)
smallFont = pygame.freetype.SysFont("Jokerman", 50)
xsmallFont = pygame.freetype.SysFont("Jokerman", 40)
xxsmallFont  = pygame.freetype.SysFont("Jokerman", 25)
blanco = (255,255,255)
negro = (0,0,0)
colorJug = [(7,12,174),(225,12,18),(74,195,68),(250,136,249)]

# ----------------------------------------- FUNCIONES ÚTILES ----------------------------------------- 

def createAruco():
    # Load the predefined dictionary
    dictionary = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_100)
    
    # Generate the marker
    markerImage = np.zeros((200, 200), dtype=np.uint8)
    markerImage = cv2.aruco.drawMarker(dictionary, 33, 200, markerImage, 1);
    
    cv2.imwrite("aruco.png", markerImage);
    
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def fadeOut(): 
    fade = pygame.Surface((ancho, alto))
    fade.fill((0,0,0))
    for alpha in range(0, 255):
        fade.set_alpha(alpha)
        screen.blit(fondoMenu.image, fondoMenu.rect)
        screen.blit(puntero.image,puntero.rect)
        screen.blit(fade, (0,0))
        pygame.display.update()
    
def transicion(origen, destino): 
    global LEFT, RIGHT, UP, DOWN
    LEFT, RIGHT, UP, DOWN = False, False, False, False
    fade = pygame.Surface((ancho, alto))
    fade.fill((0,0,0))
    for alpha in range(0, 255):
        fade.set_alpha(alpha)
        if origen == 0:
            screen.blit(fondoMenu.image, fondoMenu.rect)
        elif origen == 1:
            screen.blit(fondoEsperaJug.image, fondoEsperaJug.rect)
        elif origen == 2:
            screen.blit(fondoElegirTablero.image, fondoElegirTablero.rect) 
        elif origen == 3:
            screen.blit(fondoCreditos.image, fondoCreditos.rect)
        screen.blit(puntero.image,puntero.rect)
        screen.blit(fade, (0,0))
        pygame.display.update()
    fade.fill((0,0,0))
    for alpha in range(255,0,-1):
        fade.set_alpha(alpha)
        if destino == 0:
            screen.blit(fondoMenu.image, fondoMenu.rect)
        elif destino == 1:
            screen.blit(fondoEsperaJug.image, fondoEsperaJug.rect)
        elif destino == 2:
            screen.blit(fondoElegirTablero.image, fondoElegirTablero.rect)
        elif destino == 3:
            screen.blit(fondoCreditos.image, fondoCreditos.rect)
        if origen != 1 and destino != 4:
            screen.blit(puntero.image,puntero.rect)
        screen.blit(fade, (0,0))
        pygame.display.update()


def explicarNormas():
    bigFont.render_to(screen, (270, 20), "¡Bienvenido!", blanco)
    mediumFont.render_to(screen, (190, 170), "-:- Reglas del juego -:-", blanco)
    xsmallFont.render_to(screen, (300, 280), "· Podrán jugar hasta 4 jugadores", blanco)
    xsmallFont.render_to(screen, (155, 350), "· Cada jugador lanzará un dado y moverá su ficha", blanco)
    xsmallFont.render_to(screen, (220, 420), "· Existen 9 casillas normales y 3 especiales", blanco)
    xsmallFont.render_to(screen, (155, 490), "· En cada casilla normal conseguirá 1,2 o 3 monedas", blanco)
    xsmallFont.render_to(screen, (160, 560), "· En las especiales ocurren eventos según la casilla", blanco)
    xsmallFont.render_to(screen, (250, 630), "· El primero en llegar a 10 monedas gana ", blanco)
    xxsmallFont.render_to(screen, (1145, 680), "Comenzar", blanco)
    
    spritesCarga.draw(screen)
    
# ----------------------------------------- REDRAW ----------------------------------------- 

def drawMenu():
    # Dibujo el menu
    screen.fill((255,255,255))
    draw_text('main menu', font, (0,0,0), screen, 600, 100)
    boton_juego = pygame.Rect(190,180,920,230)
    boton_mapa = pygame.Rect(190,435,920,115)
    boton_salir = pygame.Rect(190,575,920,115)
    boton_extra = pygame.Rect(30,575,110,110)
    pygame.draw.rect(screen, (255, 0, 0), boton_juego)
    pygame.draw.rect(screen, (0, 255, 0), boton_mapa)
    pygame.draw.rect(screen, (0, 0, 255), boton_salir)
    pygame.draw.rect(screen, (0, 100, 100), boton_extra)
    screen.blit(fondoMenu.image, fondoMenu.rect)
    
# ----------------------------------------- MENUS ----------------------------------------- 
def main_menu():
    global click, LEFT, RIGHT, UP, DOWN, button_keys, analog_keys, controlRaton
    
    musica.play(loops = -1, fade_ms = 1000)
    # Dibujo el menu
    screen.fill((255,255,255))
    draw_text('main menu', font, (0,0,0), screen, 600, 100)
    boton_juego = pygame.Rect(190,180,920,230)
    boton_mapa = pygame.Rect(190,435,920,115)
    boton_salir = pygame.Rect(190,575,920,115)
    boton_extra = pygame.Rect(30,575,110,110)
    pygame.draw.rect(screen, (255, 0, 0), boton_juego)
    pygame.draw.rect(screen, (0, 255, 0), boton_mapa)
    pygame.draw.rect(screen, (0, 0, 255), boton_salir)
    pygame.draw.rect(screen, (0, 100, 100), boton_extra)
    screen.blit(fondoMenu.image, fondoMenu.rect)
    
    
    mandoActivo = False
    
    while True:
        xJoystick = 0
        yJoystick = 0
        # Si se ha pulsado accedo al submenu
        #mx, my = pygame.mouse.get_pos()
        mx = puntero.rect.x
        my = puntero.rect.y
        if boton_juego.collidepoint((mx, my)):
            if click:
                transicion(0,1)
                esperaJug()
                musica.play(loops = -1, fade_ms = 1000)
                drawMenu()
        if boton_mapa.collidepoint((mx, my)):
            if click:
                transicion(0,2)
                mapa()
                drawMenu()
        if boton_salir.collidepoint((mx, my)):
            if click:
                fJuego=open("juegoAbluetooth.txt","w")
                fJuego.write('8')
                fJuego.close()
                fadeOut()
                sys.exit()
        if boton_extra.collidepoint((mx, my)):
            if click:
                transicion(0,3)
                creditos()
                drawMenu()
                
        # Compruebo los eventos del menu
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['PS'] and event.joy == 0):
                fJuego=open("juegoAbluetooth.txt","w")
                fJuego.write('8')
                fJuego.close()
                pygame.quit()
                sys.exit()
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['x'] and event.joy == 0):
                click = True
                botonSound.play()
            if event.type == pygame.MOUSEMOTION:
                controlRaton = True
            
            if event.type == pygame.JOYAXISMOTION  and event.joy == 0:
                controlRaton = False
                analog_keys[event.axis] = event.value
                # Horizontal Analog
                if abs(analog_keys[0]) > .4:
                    if analog_keys[0] < -.7 and puntero.rect.x > 0:
                        LEFT = True
                    else:
                        LEFT = False
                    if analog_keys[0] > .7 and puntero.rect.x < 1280-76:
                        RIGHT = True
                    else:
                        RIGHT = False
                # Vertical Analog
                if abs(analog_keys[1]) > .4:
                    if analog_keys[1] < -.7 and puntero.rect.y > 0:
                        UP = True
                    else:
                        UP = False
                    if analog_keys[1] > .7 and puntero.rect.y < 720-100:
                        DOWN = True
                    else:
                        DOWN = False
                        
        if controlRaton:
            xR,yR = pygame.mouse.get_pos()
            puntero.rect.x =  xR
            puntero.rect.y = yR
        else:
            if LEFT:
                puntero.rect.x -= 5 
            if RIGHT:
                puntero.rect.x += 5 
            if UP:
                puntero.rect.y -= 5
            if DOWN:
                puntero.rect.y += 5
            #puntero.rect.x += xJoystick
            #puntero.rect.y += yJoystick
        screen.blit(fondoMenu.image, fondoMenu.rect)
        screen.blit(puntero.image,puntero.rect)     
        #print("Actualizo puntero \n")
        pygame.display.update()
        mainClock.tick(60)
 
def esperaJug():
    global click, LEFT, RIGHT, UP, DOWN, button_keys, analog_keys, controlRaton, musica
    
    #Preparo los sprites para cuando este listo cada jugador
    listo1 = Listo()
    listo1.rect.x = 210
    listo1.rect.y = 240
    listo2 = Listo()
    listo2.rect.x = 720
    listo2.rect.y = 240
    listo3 = Listo()
    listo3.rect.x = 210
    listo3.rect.y = 530
    listo4 = Listo()
    listo4.rect.x = 720
    listo4.rect.y = 530
    listoList = pygame.sprite.Group()
    
    textoComenzar = Comenzar()
    textoComenzar.rect.x = 80
    textoComenzar.rect.y = 360
    alphaTextoComenzar = 0
    modeAlpha = False
    
    r1Pulsado = False
    l1Pulsado = False
    robot1In = robot2In = robot3In = robot4In = False
                    
    running = True
    
    #Digo al otro código que comience a funcionar
    fJuego=open("juegoAbluetooth.txt","w")
    fJuego.write('7')
    fJuego.close()

    while running:
        screen.fill((255,255,255))
        boton_salir = pygame.Rect(10,610,100,100)
        pygame.draw.rect(screen, (0, 0, 255), boton_salir)
        screen.blit(fondoEsperaJug.image, fondoEsperaJug.rect)
        
        #Leo el otro programa
        fBluetooth = open("bluetoothAjuego.txt")
        datoBJ = fBluetooth.read()
        fBluetooth.close()
    
        # Dibujar los jugadores listos
        test = True
        if datoBJ == '1' or robot1In: # or test:
            listoList.add(listo1)
            robot1In = True
        if datoBJ == '2' or robot2In: # or test:
            listoList.add(listo2)
            robot2In = True
        if datoBJ == '3' or robot3In: # or test:
            listoList.add(listo3)
            robot3In = True
        if datoBJ == '4' or robot4In: # or test:
            listoList.add(listo4)
            robot4In = True
            #Digo al otro código que no haga nada
            fJuego=open("juegoAbluetooth.txt","w")
            fJuego.write('0')
            fJuego.close()
        
        #mx, my = pygame.mouse.get_pos()  
        mx = puntero.rect.x
        my = puntero.rect.y
        if boton_salir.collidepoint((mx, my)):
            if click:
                transicion(1,0)
                break
        if (r1Pulsado and l1Pulsado):
            print("COMENZAR JUEGO")
            musica.fadeout(2000)
            transicion(1,4)
            juegoMain()
            break
            #drawMenu()
        # Compruebo los eventos del menu
        click = False
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['PS'] and event.joy == 0):
                fJuego=open("juegoAbluetooth.txt","w")
                fJuego.write('8')
                fJuego.close()
                pygame.quit()
                sys.exit()
            if (event.type == MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['x'] and event.joy == 0):
                click = True
                botonSound.play()
            if event.type == pygame.JOYAXISMOTION  and event.joy == 0:
                controlRaton = False
                analog_keys[event.axis] = event.value
                # Horizontal Analog
                if abs(analog_keys[0]) > .4:
                    if analog_keys[0] < -.7 and puntero.rect.x > 0:
                        LEFT = True
                    else:
                        LEFT = False
                    if analog_keys[0] > .7 and puntero.rect.x < 1280-76:
                        RIGHT = True
                    else:
                        RIGHT = False
                # Vertical Analog
                if abs(analog_keys[1]) > .4:
                    if analog_keys[1] < -.7 and puntero.rect.y > 0:
                        UP = True
                    else:
                        UP = False
                    if analog_keys[1] > .7 and puntero.rect.y < 720-100:
                        DOWN = True
                    else:
                        DOWN = False
            if event.type == MOUSEMOTION:
                controlRaton = True
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == button_keys['R1']:
                    r1Pulsado = True
                if event.button == button_keys['L1']:
                    l1Pulsado = True
            if event.type == pygame.JOYBUTTONUP:
                if event.button == button_keys['R1']:
                    r1Pulsado = False
                if event.button == button_keys['L1']:
                    l1Pulsado = False
                    
        if controlRaton:
            xR,yR = pygame.mouse.get_pos()
            puntero.rect.x =  xR
            puntero.rect.y = yR
        else:
            if LEFT:
                puntero.rect.x -= 5 
            if RIGHT:
                puntero.rect.x += 5 
            if UP:
                puntero.rect.y -= 5
            if DOWN:
                puntero.rect.y += 5
        
        screen.blit(fondoEsperaJug.image, fondoEsperaJug.rect)
        listoList.draw(screen)
        if datoBJ == '4': # or test:
            if alphaTextoComenzar == 256:
                modeAlpha = True #cuenta hacia abajo
            elif alphaTextoComenzar == 60:
                modeAlpha = False #cuenta hacia arriba
            if modeAlpha:
                alphaTextoComenzar -= 4
            else:
                alphaTextoComenzar += 4
            textoComenzar.image.set_alpha(alphaTextoComenzar)
            screen.blit(textoComenzar.image,textoComenzar.rect)    
        screen.blit(puntero.image,puntero.rect)              
        pygame.display.update()
        mainClock.tick(60)


def juegoMain():
    #Variables pantalla
    global numTablero, monedasT
    coins = [0,0,0,0]
    numTurno = 1
    numPlayer = 1
    dado = 0
    casillaJug = [1,1,1,1]
    pts1 = pts2 = pts3 = pts4 = []
    
    musicaJ.play(loops = -1, fade_ms = 500)

    running = True
    modo_negro = True
    dado = Dado()
    
    alpha = 100
    normasExplicadas = dadoLanzado = turnoJugador = finalizarJuego = False
    xPulsada = oPulsada = triPulsada = False
    cuaPulsada = True
    elegido = puedesSalir = noPuedesSalir = esperarEncarcelado = False
    sinVerDado = True
    ganador = 0
    datoBJ = '77'
    monedasCarcel = [1,1,1,1]
    
    while running:
        # Compruebo si se ha cerrado el juego
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['PS'] and event.joy == 0):
                cap.release()
                musica.fadeout(500)
                fJuego=open("juegoAbluetooth.txt","w")
                fJuego.write('8')
                fJuego.close()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()
            if event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['x']:
                xPulsada = True
            if event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['circle']:
                oPulsada = True
            if event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['triangle']:
                triPulsada = True
            if event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['square']:
                if cuaPulsada == True:
                    cuaPulsada = False
                else: 
                    cuaPulsada = True
        
        if numTablero == 1:
            imagenFondoF = cv2.imread("./tableros/tablero1.png")
        elif numTablero == 2:
            imagenFondoF = cv2.imread("./tableros/tablero2.png")
        elif numTablero == 3:
            imagenFondoF = cv2.imread("./tableros/tablero3.png")
        #imagenFondoF = cv2.resize(imagenFondo,(1280,720))
        cv2.putText(imagenFondoF, text=str(coins[0]), org=(780,780), fontFace=cv2.FONT_HERSHEY_SCRIPT_COMPLEX, fontScale=1.6*2, color= blanco,thickness=4)
        cv2.putText(imagenFondoF, text=str(coins[1]), org=(1070,780), fontFace=cv2.FONT_HERSHEY_SCRIPT_COMPLEX, fontScale=1.6*2, color= blanco,thickness=4)
        cv2.putText(imagenFondoF, text=str(coins[2]), org=(1360,780), fontFace=cv2.FONT_HERSHEY_SCRIPT_COMPLEX, fontScale=1.6*2, color= blanco,thickness=4)
        cv2.putText(imagenFondoF, text=str(coins[3]), org=(1650,780), fontFace=cv2.FONT_HERSHEY_SCRIPT_COMPLEX, fontScale=1.6*2, color= blanco,thickness=4)
        #imagenFondoF = cv2.resize(imagenFondoF,(2420,1480))
        # Cojo frame de la webcam
        ret, frame = cap.read()
        if not ret:
            break
        
        if cuaPulsada:
            gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            #Detectamos los marcadores en la imagen
            #Camera Matrix: calibracion de la camara
            esquinas, ids, candidatos_malos = cv2.aruco.detectMarkers(gray, diccionario, parameters = parametros,
                                                                     cameraMatrix = matrix, distCoeff = dist)
            #Si se han detectado marcadores o algo:
            try:
                #Si hay marcadores detectados por el marcador
                if ids is not None:         
                    #print("Antes: ",ids)
                    marcadores_encontrados = len(ids)
                    
                    #Dibujar un cuadrado alrededor de los marcadores
                    cv2.aruco.drawDetectedMarkers(frame, esquinas)
                    
                    #Puntos para plotear el tablero
                    pointsFondo = []
                    pointsFondo.append((0,fondoY));
                    pointsFondo.append((0,0));
                    pointsFondo.append((fondoX,0));
                    pointsFondo.append((fondoX,fondoY));
                    
                    pointsMarkersWait = []
                    pts = []
                    contadorEsquinas = 0
                    #Iterar en marcadores
                    for i in range(0,marcadores_encontrados):
                        #Estimar la pose de cada marcador y devolver los valores rvec y tvec
                        rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(esquinas[i], 0.02, matrix, dist)
                        #print(len(ids))
                        
                        #Eliminar el error de la matriz de los valores numpy
                        (rvec - tvec).any()
                        
                        #Dibujar los ejes
                        cv2.aruco.drawAxis(frame, matrix, dist, rvec, tvec, 0.01)
                        
                        #Coordenada X del centro del marcador
                        centroX = (esquinas[i][0][0][0] + esquinas[i][0][1][0] + esquinas[i][0][2][0] + esquinas[i][0][3][0]) / 4
                        
                        #Coordenada Y del centro del marcador
                        centroY = (esquinas[i][0][0][1] + esquinas[i][0][1][1] + esquinas[i][0][2][1] + esquinas[i][0][3][1]) / 4
                        
                        if ids[i] == 0:
                            centroX -= 50
                            centroY += 20
                        if ids[i] == 1:
                            centroX -= 20
                            centroY -= 30
                        if ids[i] == 2:
                            centroX += 20
                            centroY -= 30
                        if ids[i] == 3:
                            centroX += 50
                            centroY += 20
                            
                        if ids[i] == 4:
                            pts1 = np.array([(esquinas[i][0][0][0],esquinas[i][0][0][1]),
                                            (esquinas[i][0][1][0],esquinas[i][0][1][1]),
                                            (esquinas[i][0][2][0],esquinas[i][0][2][1]),
                                            (esquinas[i][0][3][0],esquinas[i][0][3][1])], np.int32)
                            pts1 = pts1.reshape((-1,1,2))
                        
                        if ids[i] == 5:
                            pts2 = np.array([(esquinas[i][0][0][0],esquinas[i][0][0][1]),
                                            (esquinas[i][0][1][0],esquinas[i][0][1][1]),
                                            (esquinas[i][0][2][0],esquinas[i][0][2][1]),
                                            (esquinas[i][0][3][0],esquinas[i][0][3][1])], np.int32)
                            pts2 = pts2.reshape((-1,1,2))
                        
                        if ids[i] == 6:
                            pts3 = np.array([(esquinas[i][0][0][0],esquinas[i][0][0][1]),
                                            (esquinas[i][0][1][0],esquinas[i][0][1][1]),
                                            (esquinas[i][0][2][0],esquinas[i][0][2][1]),
                                            (esquinas[i][0][3][0],esquinas[i][0][3][1])], np.int32)
                            pts3 = pts3.reshape((-1,1,2))
                            
                        if ids[i] == 7:
                            pts4 = np.array([(esquinas[i][0][0][0],esquinas[i][0][0][1]),
                                            (esquinas[i][0][1][0],esquinas[i][0][1][1]),
                                            (esquinas[i][0][2][0],esquinas[i][0][2][1]),
                                            (esquinas[i][0][3][0],esquinas[i][0][3][1])], np.int32)
                            pts4 = pts4.reshape((-1,1,2))
                            
                        #Mostrar el ID
                        cv2.putText(frame, "id"+ str(ids[i]), (int(centroX),int(centroY)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50,255,250),2)
        
                        if ids[i] >= 0 and ids[i] <= 3:
                            contadorEsquinas += 1
                            
                        pointsMarkersWait.append([centroX,centroY]) #,0?
                    
                    # Ordenar los marcadores para que siempre se coloque en el mismo orden
                    robotsMarkers = []
                    if contadorEsquinas == 4:
                        pointsMarkers = []
                    for i in range(0,8):
                        for j in range(0,len(pointsMarkersWait)):
                            if ids[j] == i:
                                if ids[j] < 4 and contadorEsquinas == 4:
                                    pointsMarkers.append(pointsMarkersWait[j])
                                elif ids[j] >= 4 and ids[j] < 8:
                                    robotsMarkers.append(pointsMarkersWait[j])
                    
                    pointsFondo = np.float32(pointsFondo).reshape(-1,2)
                    pointsMarkers = np.float32(pointsMarkers).reshape(-1,2)
                    
                    # Calculate Homography
                    h, status = cv2.findHomography(pointsFondo, pointsMarkers)
                    
                    # Warp source image to destination based on homography
                    warped_image = cv2.warpPerspective(imagenFondoF, h, (frame.shape[1],frame.shape[0]))
                    #cv2.imshow("warped_image",warped_image)
                    
                    # Prepare a mask representing region to copy from the warped image into the original frame.
                    mask = np.zeros([frame.shape[0], frame.shape[1]], dtype="uint8");
                    
                    # Erode the mask to not copy the boundary effects from the warping
                    
                    element = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5));
                    mask = cv2.erode(mask, element, iterations=5);
                    
                    pointsMarkersInt = np.int32(pointsMarkers)
                    cv2.fillConvexPoly(mask, pointsMarkersInt, (255, 255, 255), cv2.LINE_AA);
                    #cv2.imshow("mask",mask)
                    #print(pointsMarkers)
                    mask = cv2.bitwise_not(mask)
                    frame = cv2.bitwise_and(frame, frame, mask=mask)
                    frame = cv2.add(warped_image,frame)
                    
                    if pts1 != []:
                        frame = cv2.fillPoly(frame, [pts1], (225,12,18))
                    if pts2 != []:
                        frame = cv2.fillPoly(frame, [pts2], (7,12,174))
                    if pts3 != []:
                        frame = cv2.fillPoly(frame, [pts3], (74,195,68))
                    if pts4 != []:
                        frame = cv2.fillPoly(frame, [pts4], (250,136,249))
                    
            except:
                if ids is None or len(ids) == 0:
                    print("----------------- Markers detection failed -----------------")
                    
        #for some reasons the frames appeared inverted
        frame = np.fliplr(frame)
        frame = np.rot90(frame)
    
        # The video uses BGR colors and PyGame needs RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
        surf = pygame.surfarray.make_surface(frame)
    
        # Show the PyGame surface!
        screen.blit(surf, (0,0))
        
        #Aqui se dibuja la pantalla del juego        
        #Turno
        texto = "Ronda " + str(numTurno)
        mediumFont.render_to(screen, (950, 20), texto, (255,255,255))
        
        #Jugador
        texto = "Jugador " + str(numPlayer)
        smallFont.render_to(screen, (20, 20), texto, colorJug[numPlayer-1])
        
        #Monedas
        texto = str(coins[numPlayer-1])
        smallFont.render_to(screen, (95, 100), texto, (228, 175, 24))
        
        #Vision
        xxsmallFont.render_to(screen, (95, 680), "Poner/quitar visión", blanco)
        spritesJuego.draw(screen)
        
        #Leo el otro programa
        fBluetooth = open("bluetoothAjuego.txt")
        datoBJanterior = datoBJ
        datoBJ = fBluetooth.read()
        fBluetooth.close()
        
        #Compruebo si hay cambio de jugador
        if datoBJanterior == '5' and datoBJ == '0': 
            turnoJugador = dadoLanzado = False
            modo_negro = sinVerDado = True
            fJuego=open("juegoAbluetooth.txt","w")
            fJuego.write('0')
            fJuego.close()
            coins[numPlayer-1] += monedasT[casillaJug[numPlayer-1]-1]
            numPlayer += 1
            if numPlayer > 4: 
                numPlayer = 1
                numTurno += 1
        
        #Compruebo si alguien ha ganado la partida
        for i in range (0,4):
            if coins[i] >= 10:
                ganador = i+1
                finalizarJuego = True
                modo_negro = True
        
        if modo_negro == True:
            if alpha < 200 and dadoLanzado == False:
                    alpha += 10
            fade = pygame.Surface((ancho, alto))
            fade.fill((0,0,0))
            fade.set_alpha(alpha)
            screen.blit(fade, (0,0))
            
            if alpha == 200 and finalizarJuego:
                mediumFont.render_to(screen, (155, 250), "¡Ha ganado el ", blanco)
                texto = "Jugador " + str(ganador)
                mediumFont.render_to(screen, (700, 250), texto, colorJug[ganador-1])
                mediumFont.render_to(screen, (1105, 250), "!", blanco)
                mediumFont.render_to(screen, (375, 400), "¡Felicidades!", blanco)
                xxsmallFont.render_to(screen, (1145, 680), "Salir", blanco)
                spritesCarga.draw(screen)
                if xPulsada:
                   transicion(4,0)
                   musicaJ.fadeout(1000)
                   break
                        
            elif alpha == 200 and dadoLanzado == False:
                if normasExplicadas == False:
                    explicarNormas()
                    if xPulsada:
                        normasExplicadas = True
                        xPulsada = False
                elif turnoJugador == False:
                     mediumFont.render_to(screen, (230, 300), "Turno del ", blanco)
                     texto = "Jugador " + str(numPlayer)
                     mediumFont.render_to(screen, (650, 300), texto, colorJug[numPlayer-1])
                     xxsmallFont.render_to(screen, (1145, 680), "Comenzar", blanco)
                     spritesCarga.draw(screen)
                     if xPulsada:
                        turnoJugador = True
                        xPulsada = False
                elif dadoLanzado == False and ((casillaJug[numPlayer-1] != 5) or (casillaJug[numPlayer-1] == 5 and monedasCarcel[numPlayer-1] == 0)):
                    #Codigo del dado
                    if xPulsada == False and sinVerDado == True:
                        dado.numero = randint(1,6)
                        dado.update()
                    elif xPulsada == True:
                        if sinVerDado == True:
                            print("Te ha salido un ", dado.numero)                            
                            sinVerDado = False
                            xPulsada = False
                        else:
                            monedasCarcel[numPlayer-1] = min(numTurno,3)
                            dadoLanzado = True
                            fJuego=open("juegoAbluetooth.txt","w")
                            fJuego.write(str(dado.numero))
                            fJuego.close()
                            casillaJug[numPlayer-1] += dado.numero
                            if casillaJug[numPlayer-1] >= 13:
                                casillaJug[numPlayer-1] -= 12
                    spritesDado = pygame.sprite.Group()
                    spritesDado.add(dado)
                    spritesDado.add(botonX2)
                    spritesDado.draw(screen)
                    texto = "Pulsa       para lanzar el dado"
                    mediumFont.render_to(screen, (80, 100), texto, blanco)
                    if sinVerDado == False:
                        xxsmallFont.render_to(screen, (1140, 680), "Continuar", blanco)
                        spritesCarga.draw(screen)
                        texto = "Te ha salido un " + str(dado.numero)
                        smallFont.render_to(screen, (420, 550), texto, blanco)           
                elif casillaJug[numPlayer-1] == 5:
                    #Mecanicas de la carcel
                    texto = "¡¡Estás en la cárcel!!"
                    mediumFont.render_to(screen, (250, 100), texto, blanco)
                                        
                    if elegido == False:
                        texto = "Paga " + str(monedasCarcel[numPlayer-1]) + " para salir"
                        mediumFont.render_to(screen, (320, 300), texto, blanco)
                        smallFont.render_to(screen, (320, 500), "Sí", blanco)
                        smallFont.render_to(screen, (800, 500), "No", blanco)
                        spritesCarcel.draw(screen)
                        if triPulsada or oPulsada:
                            elegido = True
                        if oPulsada == True: #CASO PASO Y SIGO ENCARCELADO
                            esperarEncarcelado = True
                        #if (triPulsada == True and coins[numPlayer-1] - monedasCarcel[numPlayer-1] >= 0) or 
                        if (triPulsada == True and coins[numPlayer-1] - monedasCarcel[numPlayer-1] >= 0): #CASO PAGO Y TENGO DINERO
                            coins[numPlayer-1] -= monedasCarcel[numPlayer-1]
                            monedasCarcel[numPlayer-1] = 0
                        if oPulsada and monedasCarcel[numPlayer-1]-1 == 0: #CASO PASO PERO SIG TURNO SALGO GRATIS
                            puedesSalir = True
                            esperarEncarcelado = False
                        if triPulsada == True and coins[numPlayer-1] - monedasCarcel[numPlayer-1] < 0: #CASO PAGO PERO NO HAY DINERO
                            noPuedesSalir = True
                    else: 
                        xxsmallFont.render_to(screen, (1140, 680), "Continuar", blanco)
                        spritesCarga.draw(screen)
                        if puedesSalir:
                            texto = "¡En el siguiente turno sales de la cárcel!"
                            smallFont.render_to(screen, (155, 400), texto, blanco)                            
                        if noPuedesSalir:
                            texto = "No tienes dinero para salir de la cárcel"
                            smallFont.render_to(screen, (157, 300), texto, blanco)
                            texto = "En el siguiente turno costará " + str(monedasCarcel[numPlayer-1] - 1) + " monedas salir"
                            smallFont.render_to(screen, (120, 420), texto, blanco)
                        if esperarEncarcelado:
                            texto = "En el siguiente turno costará " + str(monedasCarcel[numPlayer-1] - 1) + " monedas salir"
                            smallFont.render_to(screen, (120, 400), texto, blanco)
                            
                        if xPulsada == True:
                            '''if puedesSalir:
                                #coins[numPlayer-1] -= monedasCarcel[numPlayer-1]
                                monedasCarcel[numPlayer-1] = 0
                            if noPuedesSalir or esperarEncarcelado:
                            '''
                            monedasCarcel[numPlayer-1] -= 1
                            dadoLanzado = True
                            fJuego=open("juegoAbluetooth.txt","w")
                            fJuego.write('7')
                            fJuego.close()
                            dadoLanzado = True
                            elegido = puedesSalir = noPuedesSalir = esperarEncarcelado = False
                        
            triPulsada = oPulsada = xPulsada = optPulsada = False        
            if dadoLanzado:
                if alpha > 0:
                    alpha -= 10
                else:
                    modo_negro = False
                fade = pygame.Surface((ancho, alto))
                fade.fill((0,0,0))
                fade.set_alpha(alpha)
                screen.blit(fade, (0,0))
                
        
        pygame.display.flip()
    
    
def mapa():     
    global click, LEFT, RIGHT, UP, DOWN, button_keys, analog_keys, controlRaton, imagenFondo, numTablero, monedasT
    
    #Preparo los sprites de los tableros
    t1 = Tablero("./tableros/tablero1.png")
    t1.rect.x = 130
    t1.rect.y = 120
    elegidoX = 130
    elegidoY = 120
    t2 = Tablero("./tableros/tablero2.png")
    t2.rect.x = 670
    t2.rect.y = 120
    t3 = Tablero("./tableros/tablero3.png")
    t3.rect.x = 400
    t3.rect.y = 430
    tableroList = pygame.sprite.Group()
    tableroList.add(t1)
    tableroList.add(t2)
    tableroList.add(t3)
    
    # Dibujo el menu
    screen.fill((255,255,255))
    draw_text('menu mapas', font, (0,0,0), screen, 600, 100)
    boton_tablero1 = pygame.Rect(130,120,480,270)
    boton_tablero2 = pygame.Rect(670,120,480,270)
    boton_tablero3 = pygame.Rect(400,430,480,270)
    boton_salir = pygame.Rect(10,610,100,100)
        
    pygame.draw.rect(screen, (255, 0, 0), boton_tablero1)
    pygame.draw.rect(screen, (0, 255, 0), boton_tablero2)
    pygame.draw.rect(screen, (0, 0, 255), boton_tablero3)
    pygame.draw.rect(screen, (0, 100, 255), boton_salir)
    screen.blit(fondoElegirTablero.image, fondoElegirTablero.rect)
    
    
    mandoActivo = False
    
    while True:
        xJoystick = 0
        yJoystick = 0
        # Si se ha pulsado accedo al submenu
        #mx, my = pygame.mouse.get_pos()
        mx = puntero.rect.x
        my = puntero.rect.y
        
        if click:
            if boton_tablero1.collidepoint((mx, my)):
                imagenFondo = tablero1
                numTablero = 1
                monedasT = monedasT1
                elegidoX = 130
                elegidoY = 120
            if boton_tablero2.collidepoint((mx, my)):
                numTablero = 2
                imagenFondo = tablero2
                monedasT = monedasT2
                elegidoX = 670
                elegidoY = 120
            if boton_tablero3.collidepoint((mx, my)):
                numTablero = 3
                imagenFondo = tablero3
                monedasT = monedasT3
                elegidoX = 400
                elegidoY = 430
            if boton_salir.collidepoint((mx, my)):
                transicion(2,0)
                break
                
        # Compruebo los eventos del menu
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['PS'] and event.joy == 0):
                fJuego=open("juegoAbluetooth.txt","w")
                fJuego.write('8')
                fJuego.close()
                pygame.quit()
                sys.exit()
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['x'] and event.joy == 0):
                click = True
                botonSound.play()
            if event.type == pygame.MOUSEMOTION:
                controlRaton = True
            
            if event.type == pygame.JOYAXISMOTION  and event.joy == 0:
                controlRaton = False
                analog_keys[event.axis] = event.value
                # Horizontal Analog
                if abs(analog_keys[0]) > .4:
                    if analog_keys[0] < -.7 and puntero.rect.x > 0:
                        LEFT = True
                    else:
                        LEFT = False
                    if analog_keys[0] > .7 and puntero.rect.x < 1280-76:
                        RIGHT = True
                    else:
                        RIGHT = False
                # Vertical Analog
                if abs(analog_keys[1]) > .4:
                    if analog_keys[1] < -.7 and puntero.rect.y > 0:
                        UP = True
                    else:
                        UP = False
                    if analog_keys[1] > .7 and puntero.rect.y < 720-100:
                        DOWN = True
                    else:
                        DOWN = False
                        
        if controlRaton:
            xR,yR = pygame.mouse.get_pos()
            puntero.rect.x =  xR
            puntero.rect.y = yR
        else:
            if LEFT:
                puntero.rect.x -= 5 
            if RIGHT:
                puntero.rect.x += 5 
            if UP:
                puntero.rect.y -= 5
            if DOWN:
                puntero.rect.y += 5
            #puntero.rect.x += xJoystick
            #puntero.rect.y += yJoystick
        screen.blit(fondoElegirTablero.image, fondoElegirTablero.rect)
        
        mapaElegido = pygame.Rect(elegidoX-7,elegidoY-7,494,284)
        pygame.draw.rect(screen, (0, 200, 20), mapaElegido)
    
        tableroList.draw(screen)
        screen.blit(puntero.image,puntero.rect)     
        pygame.display.update()
        mainClock.tick(60)
        
        
def creditos():
    global click, LEFT, RIGHT, UP, DOWN, button_keys, analog_keys, controlRaton
    
    boton_salir = pygame.Rect(10,610,100,100)
    pygame.draw.rect(screen, (0, 100, 255), boton_salir)
    screen.blit(fondoCreditos.image, fondoCreditos.rect)
    
    mandoActivo = False
    while True:
        xJoystick = 0
        yJoystick = 0
        # Si se ha pulsado accedo al submenu
        #mx, my = pygame.mouse.get_pos()
        mx = puntero.rect.x
        my = puntero.rect.y
        
        if click:
            if boton_salir.collidepoint((mx, my)):
                transicion(3,0)
                break
                
        # Compruebo los eventos del menu
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['PS'] and event.joy == 0):
                fJuego=open("juegoAbluetooth.txt","w")
                fJuego.write('8')
                fJuego.close()
                pygame.quit()
                sys.exit()
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.JOYBUTTONDOWN and event.button == button_keys['x'] and event.joy == 0):
                click = True
                botonSound.play()
            if event.type == pygame.MOUSEMOTION:
                controlRaton = True
            
            if event.type == pygame.JOYAXISMOTION  and event.joy == 0:
                controlRaton = False
                analog_keys[event.axis] = event.value
                # Horizontal Analog
                if abs(analog_keys[0]) > .4:
                    if analog_keys[0] < -.7 and puntero.rect.x > 0:
                        LEFT = True
                    else:
                        LEFT = False
                    if analog_keys[0] > .7 and puntero.rect.x < 1280-76:
                        RIGHT = True
                    else:
                        RIGHT = False
                # Vertical Analog
                if abs(analog_keys[1]) > .4:
                    if analog_keys[1] < -.7 and puntero.rect.y > 0:
                        UP = True
                    else:
                        UP = False
                    if analog_keys[1] > .7 and puntero.rect.y < 720-100:
                        DOWN = True
                    else:
                        DOWN = False
                        
        if controlRaton:
            xR,yR = pygame.mouse.get_pos()
            puntero.rect.x =  xR
            puntero.rect.y = yR
        else:
            if LEFT:
                puntero.rect.x -= 5 
            if RIGHT:
                puntero.rect.x += 5 
            if UP:
                puntero.rect.y -= 5
            if DOWN:
                puntero.rect.y += 5
            
        screen.blit(fondoCreditos.image, fondoCreditos.rect)
        screen.blit(puntero.image,puntero.rect)     
        pygame.display.update()
        mainClock.tick(60)

### ---------------- INICIO ----------------- ###

#Digo al otro código que se espere
fJuego=open("juegoAbluetooth.txt","w")
fJuego.write('0')
fJuego.close()
    
# Comienza la musica
musica = pygame.mixer.Sound("./sonido/menus.mp3")
musicaJ = pygame.mixer.Sound("./sonido/juego.mp3")

main_menu()
cap.release()
cv2.destroyAllWindows()