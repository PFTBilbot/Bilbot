import speech_recognition as sr  
from espeak import espeak
import RPi.GPIO as GPIO
import time
import os
from googletrans import Translator

#valeurs d'angle d'ouverture et de fermeture de la bouce
ouverte = 20
ferme = 60

#Parametres de la voix
vitesse = '150'
volume = '300'  

GPIO.setmode(GPIO.BOARD) #Utilisation de la numérotation board du GPIO
GPIO.setwarnings(False) #Desactivation des avertissements liés au GPIO

#Fonction convertissant un angle en impulsion pour le servomoteur
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180 #Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent

#Le servo de la bouche est sur la pin 29
pwm_gpio = 29
#La frequence du servo
frequence = 50
#Declaration de la broche du servo
GPIO.setup(pwm_gpio, GPIO.OUT)
#Declaration de la broche PWM pour le servo
pwm = GPIO.PWM(pwm_gpio, frequence)

#Fermeture de la bouche
pwm.start(angle_to_percent(ferme))
time.sleep(0.5)
pwm.ChangeDutyCycle(0)

langue_lecture=input("En quelle langue parlez-vous ? (fr/en) : ")

if langue_lecture == "fr":
    langue_lecture = "fr-FR"
    langue_ecrite = "français"
    langue = "fr"
        
if langue_lecture == "en":
    langue_lecture = "en-EN"
    langue_ecrite = "anglais"
    langue = "en"
        
langue_traduction=input("En quelle langue voulez-vous traduire ? (fr/en) : ")
time.sleep(1)

while True:
    pwm.ChangeDutyCycle(0)
    r  = sr.Recognizer()
    with sr.Microphone() as source:
        print("Dites quelque chose en", langue_ecrite)
        time.sleep(1)
        audio = r.listen(source)
    #Si quelque chose est capté
    try:
        text = r.recognize_google(audio, language = langue_lecture)
        time.sleep(1)
        print("Vous avez dit : " + text)
        
        #declaration du traducteur
        trans= Translator()
        translation = trans.translate(text, src=langue, dest=langue_traduction)
        #traduction du texte
        texte_traduit = translation.text
        
        text_split = texte_traduit.split(' ')
        for i in text_split:
            #ouverture de la bouche
            pwm.ChangeDutyCycle(angle_to_percent(ouverte))
            #Lecture du mot
            os.system('espeak -s '+vitesse+' -a '+volume+' -z -v '+langue_traduction+' "'+i+'"')
            #fermeture de la bouche
            pwm.ChangeDutyCycle(angle_to_percent(ferme))
            time.sleep(0.05)
        
        pwm.ChangeDutyCycle(0)
    
    #Rien n'a été capté
    except sr.UnknownValueError:
        print("Veuillez répeter")
    
    except sr.RequestError as e:
        print("Verifiez votre connexion internet")
