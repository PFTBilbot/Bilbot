import cv2
from imutils.video.pivideostream import PiVideoStream
import imutils
import time
import numpy as np
from flask import Flask, render_template, request, Response, render_template_string
import os
from picamera import PiCamera
import RPi.GPIO as GPIO
from espeak import espeak
from googletrans import Translator
import pyzbar.pyzbar as pyzbar

##########################################
#########DECLARATION DES VARIABLES########
##########################################

#Valeurs d'angles limites des servos
hauteur_max_yeux = 90
hauteur_min_yeux = 70
hauteur_moyennes_yeux = 85

gauche_max_yeux = 80
droite_max_yeux = 25
centre_x_yeux = 55

bouche_fermee = 60
bouche_ouverte = 20

angle_x = centre_x_yeux
angle_y = hauteur_moyennes_yeux

etat_led_oeil = False
etat_led_socle = False

#Parametres de la voix de base
vitesse = '150'
volume = '300'
langue = 'fr'

#Valeurs de base du masque
lower = np.array([0,0,0])
upper = np.array([255,255,255])

#Dimensions de la fenetre OpenCV
largueur = 640
hauteur = 480
    
#Precision du suiveur avec la camera
precision = 80

#intervalle de temps entre 2 lecture du meme QR code
intervale_QR = 8

#Intervalle entre la detection des personnes
intervale_visage = 8

##########################################
###DECLARATION DES SERVOS ET DE LA LED####
##########################################

#Les servos des yeux sont sur les pins 18 et 32
broche_servo_x_oeil = 18
broche_servo_y_oeil = 32
#Le servo de la bouche est sur la pin 29
broche_bouche = 29
#La led est sur la pin 37
led_broche = 37
#La led du socle est sur la pin
led_socle = 7

#La frequence des servo
frequence = 50

GPIO.setmode(GPIO.BOARD) #Use Board numerotation mode
GPIO.setwarnings(False) #Disable warnings

#Declaration des broches des composants
GPIO.setup(broche_servo_x_oeil, GPIO.OUT)
GPIO.setup(broche_servo_y_oeil, GPIO.OUT)
GPIO.setup(broche_bouche, GPIO.OUT)
GPIO.setup(led_broche, GPIO.OUT)
GPIO.setup(led_socle, GPIO.OUT)

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

##########################################
###################SETUP##################
##########################################

def regard_au_centre():
    #Fermeture de la bouche
    servo_bouche.start(angle_to_percent(bouche_fermee))
    time.sleep(1)
    servo_bouche.ChangeDutyCycle(0)

    #Regard au centre
    servo_x_oeil.start(angle_to_percent(centre_x_yeux))
    servo_y_oeil.start(angle_to_percent(hauteur_moyennes_yeux))
    time.sleep(1)
    servo_x_oeil.ChangeDutyCycle(0)
    servo_y_oeil.ChangeDutyCycle(0)

regard_au_centre()

##########################################
################APPLICATION###############
##########################################

vc = cv2.VideoCapture(0) 

app = Flask(__name__)

@app.route('/',methods = ['GET'])
def show_indexhtml():
    return render_template('index.html')

@app.route('/retour',methods = ['POST'])
def retour_indexhtml():
    return render_template('index.html')

@app.route('/retour_reset',methods = ['POST'])
def retour_reset_indexhtml():
    regard_au_centre()
    return render_template('index.html')

def gen(): 
   while True: 
       rval, frame = vc.read() 
       cv2.imwrite('pic.jpg', frame) 
       yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + open('pic.jpg', 'rb').read() + b'\r\n')
       
@app.route('/video_feed') 
def video_feed(): 
   return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame') 

@app.route("/horizontal", methods=["POST"])
def horizontal():
    # Get slider Values
    slider = request.form["slider"]
    angle_x = int(slider)
            
    #Deplacement des yeux
    servo_x_oeil.start(angle_to_percent(angle_x))
    time.sleep(0.1)
    #Eteignage des servos des yeux (limitation des tremblements)
    servo_x_oeil.ChangeDutyCycle(0)
    return render_template('index.html')

@app.route('/led_oeil', methods = ['POST'])
def allumage_led_oeil():
        global etat_led_oeil
        global affichage_led_oeil
        if etat_led_oeil == False:
            etat_led_oeil = True
            GPIO.output(led_broche, GPIO.HIGH)
        else:
            etat_led_oeil = False
            GPIO.output(led_broche, GPIO.LOW)
        return render_template('index.html')
    
@app.route('/led_socle', methods = ['POST'])
def allumage_led_socle():
        global etat_led_socle
        global affichage_led_socle
        if etat_led_socle == False:
            etat_led_socle = True
            GPIO.output(led_socle, GPIO.HIGH)
        else:
            etat_led_socle = False
            GPIO.output(led_socle, GPIO.LOW)
        return render_template('index.html')

@app.route('/message', methods = ['POST'])
def lire_message():
        message = request.form['message']
        
        message_coupe = message.split(' ')
            
        for i in message_coupe:
            #ouverture de la bouche
            servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
            os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
            #fermeture de la bouche
            servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
            time.sleep(0.05)
            
        servo_bouche.ChangeDutyCycle(0)
        
        return render_template('index.html')

@app.route('/traduction', methods = ['POST'])
def traducteur_index():
    print('mode traducteur active')
    return '''
<!DOCTYPE html>
<html>
  <style>
      body {background-color:#202020;}
  </style>

  <body>
     <center><h1><FONT face="Verdana" color="white">BILBOT LE TRADUCTEUR</FONT></h1>
     <FONT face="Verdana" color="#FFF77D">
     
	  <form class="form-inline" method="POST" action="/dire_traduction">
	    <div class="form-group">
	  
	    <p><div class="input-group">
		<span class="input-group-addon">Langue d'entrée :</span>
		    <select name="langue_entree_select" class="selectpicker form-control">
		      <option value="FR">Français</option>
		      <option value="EN">Anglais</option>
		      <option value="PT">Portugais</option>
		      <option value="DE">Allemand</option>
		      <option value="ES">Espagnol</option>
		    </select>
	    </div></p>
	    
	    <p><div class="input-group">
		<span class="input-group-addon">Langue de sortie :</span>
		    <select name="langue_sortie_select" class="selectpicker form-control">
		      <option value="FR">Français</option>
		      <option value="EN">Anglais</option>
		      <option value="PT">Portugais</option>
		      <option value="DE">Allemand</option>
		      <option value="ES">Espagnol</option>
		    </select>
	    </div></p>
	    
	    <p><div class="input-group">
		<span class="input-group-addon">Vitesse :</span>
		    <select name="vitesse_select" class="selectpicker form-control">
		      <option value="rapide">rapide</option>
		      <option value="lente">lente</option>	      
		    </select>
	    </div></p>
	    
	    <input type="text" name = "text">
	    
	    <button type="submit" class="btn btn-default">GO</button>
	  </div>
	</form>
    
    <form method="POST" action="/retour">
        <p><input type="submit" value="Retour" /></p>
    </form>
    
  </body>
</html>
'''

@app.route('/dire_traduction', methods = ['POST'])
def dire_traduction():
    
    langue_entree=request.form['langue_entree_select']
    langue_sortie=request.form['langue_sortie_select']
    vitesse=request.form['vitesse_select']
    text=request.form['text']
    
    #declaration du traducteur
    trans= Translator()
    translation = trans.translate(text, src=langue_entree, dest=langue_sortie)
    #traduction du texte
    texte_traduit = translation.text
                
    #decoupage mot par mot du texte
    parole = texte_traduit.split(' ')
    for i in parole:
        #ouverture de la bouche
        servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
        #lecture du mot en fonction de la vitesse choisie par l'utilisateur
        if vitesse == 'rapide':
            os.system('espeak -s '+'150'+' -a '+volume+' -z -v '+langue_sortie+' "'+i+'"')
        if vitesse == 'lente':
            os.system('espeak -s '+'20'+' -a '+volume+' -v '+langue_sortie+' "'+i+'"')
        #fermeture de la bouche
        servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
        time.sleep(0.05)
    
    servo_bouche.ChangeDutyCycle(0)
    return traducteur_index()

def mod_camera_index():
    print('mode cameras active')
    return '''
<!DOCTYPE html>
<html>
  <style>
      body {background-color:#202020;}
  </style>

  <body>
    
    <center><h1><FONT face="Verdana" color="white">DIFFERENTS MODES DISPONIBLES</FONT></h1>
    <FONT face="Verdana" color="#7D7DFF">
	
	<p><img src="/video_feed"></p>
	
	<form method="POST" action="/suiveur">
        <p><input type="submit" value="Suiveur par couleur" /></p>
    </form>
	
	<form method="POST" action="/lecture_qr_code">
        <p><input type="submit" value="Lecture de QR code" /></p>
    </form>
	
	<form method="POST" action="/compteur_personnes">
        <p><input type="submit" value="Compteur de personnes" /></p>
    </form>
	
	<form method="POST" action="/retour">
        <p><input type="submit" value="Retour" /></p>
    </form>
	
  </body>
</html>
'''

@app.route('/mod_camera', methods = ['POST'])
def acceder_mod_camera():
    return mod_camera_index()

def suiveur_index():
    print('mode suiveur active')
    return '''
<!DOCTYPE html>
<html>
  <style>
      body {background-color:#202020;}
  </style>

  <body>
    <center><h1><FONT face="Verdana" color="white">BILBOT LE SUIVEUR</FONT></h1>
    <FONT face="Verdana" color="#7D7DFF">
    <h2>GENERATION DU MASQUE<h2>
	<p><img src="/mask_feed"></p>
    
    <form class="form-inline" method="POST" action="/couleur_predefinie">
	    <div class="form-group">
	  
	    <p><div class="input-group">
		<span class="input-group-addon"><FONT face="Verdana" color="white">Couleur prédéfinies :</span>
		    <select name="couleur_predefinie_select" class="selectpicker form-control">
		      <option value="rouge">Rouge</option>
		      <option value="vert">Vert</option>
		      <option value="bleu">Bleu</option>
		    </select>
	    </div></p>
        <button type="submit" class="btn btn-default">Actualiser</button>
        </div>
	</form>
    
    <form method="POST" action="actualiser_hsv">
        <FONT face="Verdana" color="white">
        <p>
        H minimum
        <input type="range" min="0" max="255" name="hmin" />
        S minimum
        <input type="range" min="0" max="255" name="smin" />
        V minimum
        <input type="range" min="0" max="255" name="vmin" />
        </p>
        
        <p>
        H maximum
        <input type="range" min="0" max="255" name="hmax" />
        S maximum
        <input type="range" min="0" max="255" name="smax" />
        V maximum
        <input type="range" min="0" max="255" name="vmax" />
        </p>
        
        <p><input type="submit" value="Actualiser" /></p>
    </form>
	
	<form method="POST" action="/suiveur_color_go">
        <p><input type="submit" value="GO" /></p>
    </form>
	
	<form method="POST" action="/retour">
        <p><input type="submit" value="Retour" /></p>
    </form>
	
  </body>
</html>
'''

@app.route('/suiveur', methods = ['POST'])
def acceder_suiveur():
    return suiveur_index()

def gen_mask():
   print('generation_mask')
   while True: 
       rval, frame = vc.read()
       resized = cv2.resize(frame, (640, 480))
       hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
       
       mask = cv2.inRange(hsv,lower,upper)
       
       cv2.imwrite('pic_mask.jpg', mask) 
       yield (b'--mask\r\n' b'Content-Type: image/jpeg\r\n\r\n' + open('pic_mask.jpg', 'rb').read() + b'\r\n')
       
@app.route('/mask_feed') 
def mask_feed():
   print('retour video')
   return Response(gen_mask(),mimetype='multipart/x-mixed-replace; boundary=mask')

@app.route('/actualiser_hsv', methods = ['POST'])
def actualiser_hsv():
        global lower
        global upper

        hmin=request.form['hmin']
        smin=request.form['smin']
        vmin=request.form['vmin']

        hmax=request.form['hmax']
        smax=request.form['smax']
        vmax=request.form['vmax']
                
        lower = np.array([int(hmin),int(smin),int(vmin)])
        upper = np.array([int(hmax),int(smax),int(vmax)])
        
        return suiveur_index()

@app.route('/couleur_predefinie', methods = ['POST'])
def selection_couleur_predefinies():
    global lower
    global upper
    couleur=request.form['couleur_predefinie_select']
    
    if couleur == 'rouge':
        lower = np.array([161, 155, 84])
        upper = np.array([179, 255, 255])
    
    if couleur == 'vert':
        lower = np.array([25, 52, 72])
        upper = np.array([102, 255, 255])
        
    if couleur == 'bleu':
        lower = np.array([94, 80, 2])
        upper = np.array([126, 255, 255])

    return suiveur_index()

@app.route('/suiveur_color_go', methods = ['POST'])
def suiveur_color():
    print('mode suiveur active')
    return '''
<!DOCTYPE html>
<html>
  <style>
      body {background-color:#202020;}
  </style>

  <body>
    <center><h1><FONT face="Verdana" color="white">BILBOT LE SUIVEUR</FONT></h1>
    <FONT face="Verdana" color="#7D7DFF">
    <h2>SUIVEUR DE LA COULEUR<h2>
	<p><img src="/color_feed"></p>
	
	<form method="POST" action="/retour_reset">
        <p><input type="submit" value="Retour" /></p>
    </form>
	
  </body>
</html>
'''

def gen_color():
   print('generation_color')
   
   angle_x = centre_x_yeux
   angle_y = hauteur_moyennes_yeux
   
   while True: 
        rval, frame = vc.read()
        resized = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
       
        mask = cv2.inRange(hsv,lower,upper)
       
        #Detection des contours
        cnts = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        for c in cnts:
             area = cv2.contourArea(c) #Aire des contours
             if area > 5000: #Application d'un filtre pour ne garder que les gros contours
                 
                 #Afficahge des contours
                 cv2.drawContours(resized,[c],-1,(0,255,0), 3)
                 
                 #Recuperation du centre du contour
                 M = cv2.moments(c)
                 cx = int(M["m10"]/ M["m00"])
                 cy = int(M["m01"]/ M["m00"])
                 
                 #tracage d'un cercle au centre du contours
                 cv2.circle(resized,(cx,cy),7,(255,255,255),-1)
                 
                 #Determination de la direction dans laquelle faire tourner les servos pour suivre le contours
                 if cx > (largueur+precision)/2:
                     #print('droite')
                     #print(cx)
                     angle_x = angle_x - 1
                     
                     if angle_x < 25:
                        angle_x = 25
                     #print(angle)
                
                 if cx < (largueur-precision)/2:
                     #print('gauche')
                     #print(cx)
                     angle_x = angle_x + 1
                    
                     if angle_x > 80:
                        angle_x = 80
                     #print(angle)
                
                 if cy > (hauteur+precision)/2:
                     #print('droite')
                     #print(cx)
                     angle_y = angle_y - 1
                     
                     if angle_y < 70:
                        angle_y = 70
                     #print(angle)
                
                 if cy < (hauteur-precision)/2:
                     #print('gauche')
                     #print(cx)
                     angle_y = angle_y + 1
                    
                     if angle_y > 90:
                        angle_y = 90
                     #print(angle)
                 
                 #Deplacement des yeux
                 servo_x_oeil.start(angle_to_percent(angle_x))
                 servo_y_oeil.start(angle_to_percent(angle_y))
                 time.sleep(0.008)
                 #Eteignage des servos des yeux (limitation des tremblements)
                 servo_x_oeil.ChangeDutyCycle(0)
                 servo_y_oeil.ChangeDutyCycle(0)
                 time.sleep(0.008)
                 
        cv2.imwrite('pic_color.jpg', resized) 
        yield (b'--color\r\n' b'Content-Type: image/jpeg\r\n\r\n' + open('pic_color.jpg', 'rb').read() + b'\r\n')
       
@app.route('/color_feed') 
def color_feed():
   print('retour video color')
   return Response(gen_color(),mimetype='multipart/x-mixed-replace; boundary=color')

@app.route('/lecture_qr_code', methods = ['POST'])
def acceder_qr_code():
    return '''
<!DOCTYPE html>
<html>
  <style>
      body {background-color:#202020;}
  </style>

  <body>
    
    <center><h1><FONT face="Verdana" color="white">DIFFERENTS MODES DISPONIBLES</FONT></h1>
    <FONT face="Verdana" color="#7D7DFF">
	
	<p><img src="/qr_feed"></p>
	
	<form method="POST" action="/retour">
        <p><input type="submit" value="Retour" /></p>
    </form>
	
  </body>
</html>
'''

def gen_qr():
   print('generation_qr')
   
   #Initialisation de l'ancien data (permettant de ne pas lire 2 fois a la suite le meme QR code
   old_data = ''
   font = cv2.FONT_HERSHEY_PLAIN
   
   while True:
       #Eteignage du servo de la bouche (pour limiter la nuisance sonore
       servo_bouche.ChangeDutyCycle(0)
       #Recuperation de l'image
       rval, frame = vc.read()
       
       decodedObjects = pyzbar.decode(frame)
       
       for obj in decodedObjects:
            #Prise du temps
            actual_time = time.time()
            #Recuperation du texte
            data = obj.data
            #Conversion du message en byte en string
            data = data.decode('UTF-8')
            #Affichage du texte du QR code sur l'image
            cv2.putText(frame, str(data), (50, 50), font, 2,(255, 0, 0), 3)
            
            #On verifie que soit le QR code n'est pas le meme que l'ancien, soit l'intervalle de temps est passee
            if data != old_data or start_time + intervale_QR < actual_time :
                #L'ancien QR code devient le nouveau
                old_data = data
                #Reset du temps
                start_time = time.time()
                #Coupage du texte du QR code en mot par mot
                data_spit = data.split(' ')
                for i in data_spit:
                    #ouverture de la bouche
                    servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
                    #Lecture du mot
                    os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
                    #fermeture de la bouche
                    servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
                    time.sleep(0.05)
       
       cv2.imwrite('pic_qr.jpg', frame) 
       yield (b'--qr\r\n' b'Content-Type: image/jpeg\r\n\r\n' + open('pic_qr.jpg', 'rb').read() + b'\r\n')
       
@app.route('/qr_feed')  
def qr_feed():
   print('retour video qr')
   return Response(gen_qr(),mimetype='multipart/x-mixed-replace; boundary=qr')

@app.route('/compteur_personnes', methods = ['POST'])
def acceder_compteur_personnes():
    return '''
<!DOCTYPE html>
<html>
  <style>
      body {background-color:#202020;}
  </style>

  <body>
    
    <center><h1><FONT face="Verdana" color="white">DIFFERENTS MODES DISPONIBLES</FONT></h1>
    <FONT face="Verdana" color="#7D7DFF">
	
	<p><img src="/compteur_personnes_feed"></p>
	
	<form method="POST" action="/retour">
        <p><input type="submit" value="Retour" /></p>
    </form>
	
  </body>
</html>
'''

def gen_compteur_personnes():
   print('generation_compteur_personnes')
   
   cascPath = "/home/pi/Desktop/haarcascade_frontalface_default.xml"
   faceCascade = cv2.CascadeClassifier(cascPath)
   
   #Initialisation de l'ancien data (permettant de ne pas lire 2 fois a la suite le meme QR code
   old_data = ''
   start_time = time.time()
   
   while True:
       #Recuperation de l'image
       rval, frame = vc.read()
       gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
       faces = faceCascade.detectMultiScale(gray,
                                             scaleFactor=1.1,
                                             minNeighbors=5,
                                             minSize=(60, 60),
                                             flags=cv2.CASCADE_SCALE_IMAGE)
       for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h),(0,255,0), 2)
            # Display the resulting frame
        
       actual_time = time.time()
        
       if actual_time > start_time + intervale_visage:
            text = "je vois "+str(len(faces))+" personnes"
            print(text)
            text_coupe = text.split(' ')
            
            for i in text_coupe:
                #ouverture de la bouche
                servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_ouverte))
                os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue+' "'+i+'"')
                #fermeture de la bouche
                servo_bouche.ChangeDutyCycle(angle_to_percent(bouche_fermee))
                time.sleep(0.05)
            
            servo_bouche.ChangeDutyCycle(0)
            start_time = time.time()
       
       cv2.imwrite('pic_compteur_personnes.jpg', frame) 
       yield (b'--compteur_personnes\r\n' b'Content-Type: image/jpeg\r\n\r\n' + open('pic_compteur_personnes.jpg', 'rb').read() + b'\r\n')
       
@app.route('/compteur_personnes_feed')  
def compteur_personnes_feed():
   print('retour video compteur')
   return Response(gen_compteur_personnes(),mimetype='multipart/x-mixed-replace; boundary=compteur_personnes')

if __name__ == '__main__':
    app.run(host="172.16.5.114", port=5000)