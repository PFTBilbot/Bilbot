import cv2
import os
import RPi.GPIO as GPIO
import time

#Valeurs d'angles limites des servos
hauteur_max_yeux = 90
hauteur_min_yeux = 70
hauteur_moyennes_yeux = 80

gauche_max_yeux = 80
droite_max_yeux = 25
centre_x_yeux = 55


angle_x = centre_x_yeux
angle_y = hauteur_moyennes_yeux

#Dimensions de la fenetre
largueur = 640
hauteur = 480

#Precision toleree
precision = 80

#Fonction convertissant un angle en impulsion pour le servomoteur
def angle_to_percent (angle) :
    start = 4
    end = 12.5
    ratio = (end - start)/180

    angle_as_percent = angle * ratio

    return start + angle_as_percent

GPIO.setmode(GPIO.BOARD) #Utilisation de la numérotation board du GPIO
GPIO.setwarnings(False) #Desactivation des avertissements liés au GPIO

#Les servos des yeux sont sur les pins 18 et 32
broche_servo_x_oeil = 18
broche_servo_y_oeil = 32
#La led est sur la pin 37
led_broche = 37

#La frequence du servo
frequence = 50

#Declaration des broches des composants
GPIO.setup(broche_servo_x_oeil, GPIO.OUT)
GPIO.setup(broche_servo_y_oeil, GPIO.OUT)
GPIO.setup(led_broche, GPIO.OUT)

#Declaration des broches PWM pour les servo
servo_x_oeil = GPIO.PWM(broche_servo_x_oeil, frequence)
servo_y_oeil = GPIO.PWM(broche_servo_y_oeil, frequence)

#Allumage de la led dans l'oeil
GPIO.output(led_broche, GPIO.HIGH)

#Classifier utilise
cascPath = "/home/pi/Desktop/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
#Capture video
video_capture = cv2.VideoCapture(0)


while True:
    #Retour video
    ret, frame = video_capture.read()
    #Redimensionnement de l'image
    resized = cv2.resize(frame, (largueur, hauteur))
    #Changement de l'image en nuances de gris
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    #Detection des visages
    faces = faceCascade.detectMultiScale(gray,
                                         scaleFactor=1.1,
                                         minNeighbors=5,
                                         minSize=(60, 60),
                                         flags=cv2.CASCADE_SCALE_IMAGE)
    #Pour chaque visage detecte
    for (x,y,w,h) in faces:
        #Affichage d'un cadre autour du visage
        cv2.rectangle(resized, (x, y), (x + w, y + h),(0,255,0), 2)
        
        #Determination de la direction dans laquelle faire tourner les servos pour suivre le visage
        if cx > (largueur+precision)/2:
                 #print('droite')
                 #print(cx)
                 angle_x = angle_x - 1
                 
                 if angle_x < droite_max_yeux:
                    angle_x = droite_max_yeux
                 #print(angle)
            
        if cx < (largueur-precision)/2:
                 #print('gauche')
                 #print(cx)
                 angle_x = angle_x + 1
                
                 if angle_x > gauche_max_yeux:
                    angle_x = gauche_max_yeux
                 #print(angle)
            
        if cy > (hauteur+precision)/2:
                 #print('droite')
                 #print(cx)
                 angle_y = angle_y - 1
                 
                 if angle_y < hauteur_min_yeux:
                    angle_y = hauteur_min_yeux
                 #print(angle)
            
        if cy < (hauteur-precision)/2:
                 #print('gauche')
                 #print(cx)
                 angle_y = angle_y + 1
                
                 if angle_y > hauteur_max_yeux:
                    angle_y = hauteur_max_yeux
                 #print(angle)
        
        #Deplacement des yeux
        servo_x_oeil.start(angle_to_percent(angle_x))
        servo_y_oeil.start(angle_to_percent(angle_y))
        time.sleep(0.008)
        #Eteignage des servos des yeux (limitation des tremblements)
        servo_x_oeil.ChangeDutyCycle(0)
        servo_y_oeil.ChangeDutyCycle(0)
        time.sleep(0.008)
       
    #Affichage de la video
    cv2.imshow('Video', resized)
    
    #Si l'utilisateur appui sur echap le programme se coupe
    k = cv2.waitKey(5)
    if k == 27:
         break
        
#Destruction des fenetres
cv2.destroyAllWindows()
