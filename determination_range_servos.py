import cv2
import RPi.GPIO as GPIO
import time

#Capture video
cap= cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

#Dimensions de la fenetre
largueur = 640
hauteur = 480

#Les servos des yeux sont sur les pins 18 et 32
broche_servo_x_oeil = 18
broche_servo_y_oeil = 32
#Le servo de la bouche est sur la pin 29
broche_bouche = 29

#La frequence des servo
frequence = 50

GPIO.setmode(GPIO.BOARD) #Use Board numerotation mode
GPIO.setwarnings(False) #Disable warnings

#Declaration des broches des composants
GPIO.setup(broche_servo_x_oeil, GPIO.OUT)
GPIO.setup(broche_servo_y_oeil, GPIO.OUT)
GPIO.setup(broche_bouche, GPIO.OUT)

#Declaration des broches PWM pour les servo
servo_x_oeil = GPIO.PWM(broche_servo_x_oeil, frequence)
servo_y_oeil = GPIO.PWM(broche_servo_y_oeil, frequence)
servo_bouche = GPIO.PWM(broche_bouche, frequence)

#Fonction convertissant un angle en impulsion pour le servomoteur
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180

    angle_as_percent = angle * ratio

    return start + angle_as_percent

depart = time.time()
sortie = 0
delais = 3

print('initialisation, veuillez patienter', delais, 'secondes')
while sortie < depart + delais:
    _,frame= cap.read()
    cv2.imshow("affichage",frame)
    k = cv2.waitKey(5)
    if k == 27:
        break
    sortie = time.time()

choix_x = False
while choix_x != True:
    
    angle = 0
    min_x = False
    print('')
    print("\033[91mDetermination de l'angle minimum en X (horizontal) des yeux\033[37m")
    print("L'angle part de 0, déterminer avec le retour caméra la limite du regard à droite")
    while min_x != True:
        
        servo_x_oeil.start(angle_to_percent(angle))
        print('')
        print('\033[32mAngle :', angle, '\033[37m')
        time.sleep(0.5)
        servo_x_oeil.ChangeDutyCycle(0)
        
        print('')
        print("\033[94mAngle minimum X est OK ?\033[37m")
        print("Appuyez sur l'une de ces touches dans la fenêtre du retour caméra")
        print("    + : ajout de 5 degrès")
        print("    - : retrait de 5 degrès")
        print("    Entr (pavé numérique) : Validation de l'angle")
        
        choix = False
        while choix == False:
            _,frame= cap.read()
            cv2.imshow("affichage",frame)
            k = cv2.waitKey(33)
            if k == 171:
                angle = angle + 5
                choix = True
            if k == 173:
                angle = angle - 5
                choix = True
            if k == 141:
                choix = True
                min_x = True
                
    angle_mini_x = angle
    
    #----------------------------------------#
    
    angle = 180
    max_x = False
    print('')
    print("\033[91mDetermination de l'angle maximum en X (horizontal) des yeux\033[37m")
    print("L'angle part de 180, déterminer avec le retour caméra la limite du regard à gauche")
    while max_x != True:
        
        servo_x_oeil.start(angle_to_percent(angle))
        print('')
        print('\033[32mAngle :', angle, '\033[37m')
        time.sleep(0.5)
        servo_x_oeil.ChangeDutyCycle(0)
        
        print('')
        print("\033[94mAngle maximum X est OK ?\033[37m")
        print("Appuyez sur l'une de ces touches dans la fenêtre du retour caméra")
        print("    + : ajout de 5 degrès")
        print("    - : retrait de 5 degrès")
        print("    Entr (pavé numérique) : Validation de l'angle")
        
        choix = False
        while choix == False:
            _,frame= cap.read()
            cv2.imshow("affichage",frame)
            k = cv2.waitKey(33)
            if k == 171:
                angle = angle + 5
                choix = True
            if k == 173:
                angle = angle - 5
                choix = True
            if k == 141:
                choix = True
                max_x = True
                
    angle_maxi_x = angle
    
    print('')
    print('--------------------------------')
    print('Angle minimum des yeux en X :',angle_mini_x)
    print('Angle maximum des yeux en X :',angle_maxi_x)
    print('Angle moyen des yeux en X :', (angle_mini_x+angle_maxi_x)/2)
    print('OK pour les valeurs min, max et moyennes en X ? [o/n]')
    
    choix = False
    while choix == False:
        _,frame= cap.read()
        cv2.imshow("affichage",frame)
        k = cv2.waitKey(33)
        if k == 111:
            choix_x = True
            choix = True
        if k == 110:
            choix_x = False
            choix = True

servo_x_oeil.start(angle_to_percent((angle_mini_x+angle_maxi_x)/2))
time.sleep(0.5)
servo_x_oeil.ChangeDutyCycle(0)

#===========================================================================#

choix_y = False
while choix_y != True:
    
    angle = 0
    min_y = False
    print('')
    print("\033[91mDetermination de l'angle minimum en Y (vertical) des yeux\033[37m")
    print("L'angle part de 0, déterminer avec le retour caméra la limite du regard en bas")
    while min_y != True:
        
        servo_y_oeil.start(angle_to_percent(angle))
        print('')
        print('\033[32mAngle :', angle, '\033[37m')
        time.sleep(0.5)
        servo_y_oeil.ChangeDutyCycle(0)
        
        print('')
        print("\033[94mAngle minimum Y est OK ?\033[37m")
        print("Appuyez sur l'une de ces touches dans la fenêtre du retour caméra")
        print("    + : ajout de 5 degrès")
        print("    - : retrait de 5 degrès")
        print("    Entr (pavé numérique) : Validation de l'angle")
        
        choix = False
        while choix == False:
            _,frame= cap.read()
            cv2.imshow("affichage",frame)
            k = cv2.waitKey(33)
            if k == 171:
                angle = angle + 5
                choix = True
            if k == 173:
                angle = angle - 5
                choix = True
            if k == 141:
                choix = True
                min_y = True
                
    angle_mini_y = angle
    
    #----------------------------------------#
    
    angle = 180
    max_y = False
    print('')
    print("\033[91mDetermination de l'angle maximum en Y (vertical) des yeux\033[37m")
    print("L'angle part de 180, déterminer avec le retour caméra la limite du regard en haut")
    while max_y != True:
        
        servo_y_oeil.start(angle_to_percent(angle))
        print('')
        print('\033[32mAngle :', angle, '\033[37m')
        time.sleep(0.5)
        servo_y_oeil.ChangeDutyCycle(0)
        
        print('')
        print("\033[94mAngle maximum Y est OK ?\033[37m")
        print("Appuyez sur l'une de ces touches dans la fenêtre du retour caméra")
        print("    + : ajout de 5 degrès")
        print("    - : retrait de 5 degrès")
        print("    Entr (pavé numérique) : Validation de l'angle")
        
        choix = False
        while choix == False:
            _,frame= cap.read()
            cv2.imshow("affichage",frame)
            k = cv2.waitKey(33)
            if k == 171:
                angle = angle + 5
                choix = True
            if k == 173:
                angle = angle - 5
                choix = True
            if k == 141:
                choix = True
                max_y = True
                
    angle_maxi_y = angle
    
    print('')
    print('--------------------------------')
    print('Angle minimum des yeux en Y :',angle_mini_y)
    print('Angle maximum des yeux en Y :',angle_maxi_y)
    print('Angle moyen des yeux en Y :', (angle_mini_y+angle_maxi_y)/2)
    print('OK pour les valeurs min, max et moyennes en Y ? [o/n]')
    
    choix = False
    while choix == False:
        _,frame= cap.read()
        cv2.imshow("affichage",frame)
        k = cv2.waitKey(33)
        if k == 111:
            choix_y = True
            choix = True
        if k == 110:
            choix_y = False
            choix = True

servo_y_oeil.start(angle_to_percent((angle_mini_y+angle_maxi_y)/2))
time.sleep(0.5)
servo_y_oeil.ChangeDutyCycle(0)

#==========================================================================#

choix_bouche = False
while choix_bouche != True:
    
    angle = 0
    min_bouche = False
    print('')
    print("\033[91mDetermination de l'angle minimum de la bouche\033[37m")
    print("L'angle part de 0, déterminer l'ouverture de la bouche")
    while min_bouche != True:
        
        servo_bouche.start(angle_to_percent(angle))
        print('')
        print('\033[32mAngle :', angle, '\033[37m')
        time.sleep(0.5)
        servo_bouche.ChangeDutyCycle(0)
        
        print('')
        print("\033[94mAngle minimum de la bouche est OK ?\033[37m")
        print("Appuyez sur l'une de ces touches dans la fenêtre du retour caméra")
        print("    + : ajout de 5 degrès")
        print("    - : retrait de 5 degrès")
        print("    Entr (pavé numérique) : Validation de l'angle")
        
        choix = False
        while choix == False:
            _,frame= cap.read()
            cv2.imshow("affichage",frame)
            k = cv2.waitKey(33)
            if k == 171:
                angle = angle + 5
                choix = True
            if k == 173:
                angle = angle - 5
                choix = True
            if k == 141:
                choix = True
                min_bouche = True
                
    angle_mini_bouche = angle
    
    #----------------------------------------#
    
    angle = 180
    max_bouche = False
    print('')
    print("\033[91mDetermination de l'angle maximum de la bouche\033[37m")
    print("L'angle part de 180, déterminer la fermeture de la bouche")
    while max_bouche != True:
        
        servo_bouche.start(angle_to_percent(angle))
        print('')
        print('\033[32mAngle :', angle, '\033[37m')
        time.sleep(0.5)
        servo_bouche.ChangeDutyCycle(0)
        
        print('')
        print("\033[94mAngle maximum de la bouche est OK ?\033[37m")
        print("Appuyez sur l'une de ces touches dans la fenêtre du retour caméra")
        print("    + : ajout de 5 degrès")
        print("    - : retrait de 5 degrès")
        print("    Entr (pavé numérique) : Validation de l'angle")
        
        choix = False
        while choix == False:
            _,frame= cap.read()
            cv2.imshow("affichage",frame)
            k = cv2.waitKey(33)
            if k == 171:
                angle = angle + 5
                choix = True
            if k == 173:
                angle = angle - 5
                choix = True
            if k == 141:
                choix = True
                max_bouche = True
                
    angle_maxi_bouche = angle
    
    print('')
    print('--------------------------------')
    print("Angle d'ouverture :",angle_mini_bouche)
    print("Angle de fermeture :",angle_maxi_bouche)
    print('OK pour les valeurs min et max de la bouche ? [o/n]')
    
    choix = False
    while choix == False:
        _,frame= cap.read()
        cv2.imshow("affichage",frame)
        k = cv2.waitKey(33)
        if k == 111:
            choix_bouche = True
            choix = True
        if k == 110:
            choix_bouche = False
            choix = True

print('')
print('--------------------------------')
print('\033[34mRecapitulatif :\033[37m')
print('Yeux :')
print('    Axe X (horizontal) :')
print('        minimun :', angle_mini_x)
print('        maximum :', angle_maxi_x)
print('        centre :', (angle_maxi_x+angle_mini_x)/2)
print('    Axe Y (vertical) :')
print('        minimun :', angle_mini_y)
print('        maximum :', angle_maxi_y)
print('        centre :', (angle_maxi_y+angle_mini_y)/2)
print('    Bouche :')
print('        minimun :', angle_mini_bouche)
print('        maximum :', angle_maxi_bouche)