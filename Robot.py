#Parties commentées faites par moi
#Source du code vient de: Mauricio Emilio Gomez

from Pyax12_python3 import Ax12
from Nextion_python3 import Nextion
import serial,time
import RPi.GPIO as GPIO
import pymysql

#Lecture des positions de déplacements recuent par la base de données
db = None
db = pymysql.connect(user="user3", passwd = "Bonmotdepasse465", db = "DATASQL", host = "tso-118.synology.me", port=3306)
cur = db.cursor()

s = "SELECT no_voiture FROM TSO.LivraisonH22 WHERE chauffeur = 'Ramtin';"
cur.execute(s)
db.commit()
result = cur.fetchone()
for l in result:
    s1=int(l)
x = "SELECT position_commande FROM TSO.LivraisonH22 WHERE chauffeur = 'Ramtin';"
cur.execute(x)
db.commit()
result1 = cur.fetchone()
for l in result1:
    x1=l
y = "SELECT client FROM TSO.LivraisonH22 WHERE chauffeur = 'Ramtin';"
cur.execute(y)
db.commit()
result2 = cur.fetchone()
for l in result2:
    y1=l
z = "SELECT no_stationnement FROM TSO.LivraisonH22 WHERE chauffeur = 'Ramtin';"
cur.execute(z)
db.commit()
result3 = cur.fetchone()
for l in result3:
    z1 = l
    
print("s: " + str(s1))
print("x: " + str(x1))
print("y: " + str(y1))
print("z: " + str(z1))


ser_arduino = serial.Serial(port='/dev/ttyUSB1',baudrate= 115200, bytesize=8, parity='N', stopbits=1, timeout=0.01, xonxoff=0, rtscts=0)
#ser_Nextion = serial.Serial(port='/dev/ttyUSB1',baudrate= 9600, bytesize=8, parity='N', stopbits=1, timeout=0.01, xonxoff=0, rtscts=0)

ser_Nextion = serial.Serial(port="/dev/ttyUSB0", baudrate=9600  , bytesize=8, parity='N', stopbits=1, timeout=0.01, xonxoff=0, rtscts=0)
#ser_arduino = serial.Serial(port='/dev/ttyUSB0',baudrate= 115200, bytesize=8, parity='N', stopbits=1, timeout=0.01, xonxoff=0, rtscts=0)

Ax12.actualVitesse=115200.0
delay_0=0.001
ax12_Lib = Ax12(Ax12.actualVitesse)
ax12_Lib.direction(Ax12.RPI_DIRECTION_TX)
time.sleep(1)
mot1 = 2
mot2 = 3
ax12_Lib.setAngleLimit(mot1, 0, 0)
time.sleep(0.01)
ax12_Lib.setAngleLimit(mot2, 0, 0)
time.sleep(0.01)

nextion = Nextion()
autorization_to_LEDs=0
autorization_to_motor_on=0
autorization_toute_droite=0
first_time_td = 1

class Test_Robot_2022:
    
    reply_int     = [0,0,0,0,0]
    reply_color   = [0,0,0,0,0]
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(25, GPIO.OUT)
        GPIO.setup(8, GPIO.OUT)
        GPIO.setup(7, GPIO.OUT)
        GPIO.setup(12, GPIO.OUT)
        GPIO.setup(16, GPIO.OUT)
        GPIO.setup(20, GPIO.OUT)
        GPIO.setup(21, GPIO.OUT)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(8, GPIO.LOW)
        GPIO.output(7, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        GPIO.output(20, GPIO.LOW)
        GPIO.output(21, GPIO.LOW)
        #Les variables d'ordres aux moteurs
        self.counter=0
        self.s=s1
        self.x=x1
        self.y=y1
        self.z=z1
        self.lines=0
        self.turns=0
#         self.stat_ch = "en attente"
#         self.stat_comm = "pret"
        #envoie de la statut vers la base de données
        statut_chauffeur = "UPDATE TSO.LivraisonH22 SET statut_chauffeur = 'En Attente' WHERE chauffeur = 'Ramtin';"
        cur.execute(statut_chauffeur)
        db.commit()
        statut_commande = "UPDATE TSO.LivraisonH22 SET statut_commande = 'Pret' WHERE chauffeur = 'Ramtin';"
        cur.execute(statut_commande)
        db.commit()


    def SensorColor(self,Sensor):
        if Sensor == 0:
            data='aa\n'
        if Sensor == 1:
            data='ab\n'
        if Sensor == 2:
            data='ac\n'
        if Sensor == 3:
            data='ad\n'
        if Sensor == 4:
            data='ae\n'
        ser_arduino.write(data.encode())
        reply = ser_arduino.readline().decode()
        reply = reply.strip('\n')
        reply = reply.strip('\r')
        try:
            self.reply_int[Sensor] = int(reply)
        except ValueError:
            self.reply_int[Sensor] = 0

           
        if self.reply_int[Sensor] < 650:
            self.reply_color[Sensor] = 0 # noir
        if self.reply_int[Sensor] >= 650:
            self.reply_color[Sensor] = 1 # blanche
        return self.reply_color[Sensor]
 
    
    def Test_Led_and_Sensor(self):
        ser_arduino.flush()
        Sensor1 = self.SensorColor(0)
        Sensor2 = self.SensorColor(1)
        Sensor3 = self.SensorColor(2)
        Sensor4 = self.SensorColor(3)
        Sensor5 = self.SensorColor(4)
        if Sensor1 == 0:
            GPIO.output(25, GPIO.LOW)
        else:
            GPIO.output(25, GPIO.HIGH)
            
        if Sensor2 == 0:
            GPIO.output(8, GPIO.LOW)
        else:
            GPIO.output(8, GPIO.HIGH)
            
        if Sensor3 == 0:
            GPIO.output(7, GPIO.LOW)
        else:
            GPIO.output(7, GPIO.HIGH)
            
        if Sensor4 == 0:
            GPIO.output(12, GPIO.LOW)
        else:
            GPIO.output(12, GPIO.HIGH)
            
        if Sensor5 == 0:
            GPIO.output(16, GPIO.LOW)
            GPIO.output(20, GPIO.LOW)
            GPIO.output(21, GPIO.LOW)
        else:
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(20, GPIO.HIGH)
            GPIO.output(21, GPIO.HIGH)
        
        #Fonction qui met la ligne noire verticale au centre du robot        
        def MotorMove():

            total = self.s + self.x + self.y + self.z
                                     
            if Sensor1 == 1 and Sensor2 ==1 and Sensor3==1 and Sensor4==1 and Sensor5==0:
               ax12_Lib.Speed(mot1, 1024+100)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 350)
               time.sleep(0.01)
            elif Sensor1 == 1 and Sensor2 == 1 and Sensor3 == 1 and Sensor4 == 0 and Sensor5==1:
               ax12_Lib.Speed(mot1, 1024+100)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 350)
               time.sleep(0.01)
            elif Sensor1 == 1 and Sensor2 == 1 and Sensor3 == 1 and Sensor4 == 0 and Sensor5==0:
               ax12_Lib.Speed(mot1, 1024+100)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 350)
               time.sleep(0.01)
            elif Sensor1 == 1 and Sensor2 == 1 and Sensor3 == 0 and Sensor4 == 0 and Sensor5==0:
               ax12_Lib.Speed(mot1, 1024+100)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 350)
               time.sleep(0.01)
            elif Sensor1 == 1 and Sensor2 == 0 and Sensor3 == 1 and Sensor4 == 1 and Sensor5==1:
               ax12_Lib.Speed(mot1, 1024+350)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 0)
               time.sleep(0.01)
            elif Sensor1 == 1 and Sensor2 == 0 and Sensor3 == 0 and Sensor4 == 1 and Sensor5==1:
               ax12_Lib.Speed(mot1, 1024+350)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 0)
               time.sleep(0.01)
            elif Sensor1 == 0 and Sensor2 == 1 and Sensor3 == 1 and Sensor4 == 1 and Sensor5==1:
               ax12_Lib.Speed(mot1, 1024+350)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 0)
               time.sleep(0.01)  
            elif Sensor1 == 0 and Sensor2 == 0 and Sensor3 == 1 and Sensor4 == 1 and Sensor5==1:
               ax12_Lib.Speed(mot1, 1024+350)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 0)
               time.sleep(0.01)
            elif Sensor1 == 1 and Sensor2 == 1 and Sensor3 == 0 and Sensor4 == 1 and Sensor5==1:
               ax12_Lib.Speed(mot1, 1024+350)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 350)
               time.sleep(0.01)
            
            
            #algorithme pour tourner aux moments appropriés 
            elif (Sensor1 == 0 and Sensor2 == 0 and Sensor3 == 0 and Sensor4 == 0 and Sensor5==0):
                self.counter+=1
                time.sleep(0.3)
                if stage1 == True and self.counter == self.x:
                    self.turns = 1
                    TurnLeft()
                    statut_chauffeur = "UPDATE TSO.LivraisonH22 SET statut_chauffeur = 'a la station' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_chauffeur)
                    db.commit()
                    statut_commande = "UPDATE TSO.LivraisonH22 SET statut_commande = 'Picked up' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_commande)
                    db.commit()                    

                elif self.turns == 1 and self.counter == ((self.x + self.y + self.s)-1):
                    self.turns = 2
                    TurnLeft()
                    statut_chauffeur = "UPDATE TSO.LivraisonH22 SET statut_chauffeur = 'au client' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_chauffeur)
                    db.commit()
                    statut_commande = "UPDATE TSO.LivraisonH22 SET statut_commande = 'Livré' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_commande)
                    db.commit()  

                elif (self.turns == 2) and (self.y == self.z) and (self.counter == (total + (3-self.y) + (1-self.x))):
                    statut_chauffeur = "UPDATE TSO.LivraisonH22 SET statut_chauffeur = 'Parking' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_chauffeur)
                    db.commit()
                    statut_commande = "UPDATE TSO.LivraisonH22 SET statut_commande = 'Livré' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_commande)
                    db.commit()  
                    Stopping()

                    

                elif (self.turns == 2) and (self.y < self.z) and (self.counter == (total + (1-self.z) + (1-self.x))):
                    TurnLeft()
                    self.turns = 3

                elif (self.turns == 3) and (self.y < self.z) and (self.counter == (total + (1-self.y) + (1-self.x))) :
                    TurnRight()
                    self.turns = 4
                elif (self.turns == 4) and (self.y < self.z) and (self.counter == (total - (self.y) + (1-self.x) + 3)):
                    statut_chauffeur = "UPDATE TSO.LivraisonH22 SET statut_chauffeur = 'Parking' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_chauffeur)
                    db.commit()
                    statut_commande = "UPDATE TSO.LivraisonH22 SET statut_commande = 'Livré' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_commande)
                    db.commit()  
                    Stopping()

                    
                    
                elif (self.turns == 2) and (self.y > self.z) and (self.counter == (total + (1-self.z) + (1-self.x))):
                    TurnRight()
                    self.turns = 3
                elif (self.turns == 3) and (self.y > self.z) and (self.counter == (total + self.y - (2*self.z)+1 + (1-self.x))):
                    TurnLeft()
                    self.turns = 4
                elif (self.turns == 4) and (self.y > self.z) and (self.counter == (total + self.y + (3-(self.z*2)) + (1-self.x))):
                    statut_chauffeur = "UPDATE TSO.LivraisonH22 SET statut_chauffeur = 'Parking' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_chauffeur)
                    db.commit()
                    statut_commande = "UPDATE TSO.LivraisonH22 SET statut_commande = 'Livré' WHERE chauffeur = 'Ramtin';"
                    cur.execute(statut_commande)
                    db.commit()  
                    Stopping()


                    


            elif Sensor1 == 1 and Sensor2 == 1 and Sensor3==1 and Sensor4==1 and Sensor5==1:
                    Tourner()


                    
                
                
                

            print("counter: " + str(self.counter))
            print("Turns: " + str(self.turns))

                    
                   
            
               

        def Stopping():
            ax12_Lib.Speed(mot1, 0)
            time.sleep(0.01)
            ax12_Lib.Speed(mot2, 0)
            time.sleep(0.01)
            time.sleep(5)
            exit()

        def TurnRight():
            i=0
            while i<35:
               ax12_Lib.Speed(mot1, 200)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 900)
               time.sleep(0.01)
               if Sensor1 == 1 and Sensor2 == 1 and Sensor3 == 0 and Sensor4 == 1 and Sensor5==1:
                   break
               i=i+1

        def TurnLeft():
            i=0
            while i<35:
               ax12_Lib.Speed(mot1, 1024+900)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 1024+200)
               time.sleep(0.01)
               if Sensor1 == 1 and Sensor2 == 1 and Sensor3 == 0 and Sensor4 == 1 and Sensor5==1:
                   break
               i=i+1
               
        def Tourner():
               i = 0
               while i < 10:
                   if Sensor1 == 1 and Sensor2 == 1 and Sensor3 == 0 and Sensor4 == 1 and Sensor5==1:
                       break
                   ax12_Lib.Speed(mot1, 1024+570)
                   time.sleep(0.01)
                   ax12_Lib.Speed(mot2, 1024+500)
                   time.sleep(0.01)

                   i+=1
            
                
               
            
        MotorMove()
            
    

               
test_robot_2022 = Test_Robot_2022()

print("Hello")

if ser_arduino.isOpen():
   ser_arduino.close()
   ser_arduino.open()
   print("Serial Arduino is open avant:"+str(ser_arduino.isOpen()))

if ser_Nextion.isOpen():
   ser_Nextion.close()
   ser_Nextion.open()
   print("Serial is open avant:"+str(ser_Nextion.isOpen()))



   while True:
       if autorization_to_LEDs == 1:
           autorization_to_motor_on = 0
           test_robot_2022.Test_Led_and_Sensor()
           #test_robot_2022.MotorMove()
           N_txt = 0
           while N_txt <= 4:
               nextion.write_Nx_Val(N_txt,test_robot_2022.reply_color[N_txt],ser_Nextion)
               N_txt = N_txt + 1
           time.sleep(0.05)


       if ser_Nextion.inWaiting() > 0:
           recu=bytearray()
           recu=ser_Nextion.read(7)
           print(recu)
           print(recu[2])
           ser_Nextion.flush()
           bouton = recu[2]

           if bouton == 6:#LEDs
               time.sleep(1.5)
               autorization_to_LEDs = 1
               print("Testing Leds ")
               
           
           elif bouton == 8:#Moteurs
               autorization_to_LEDs = 0
               print("Starting moteur ")
               #NouvelVitesse = int(input("Vitesse >> "))
               ax12_Lib.Speed(mot1, 1024+870)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 800)
               time.sleep(0.01)
                   
           elif bouton == 9:#Arret
               autorization_to_LEDs = 0
               print("Stop")

               ax12_Lib.Speed(mot1, 1024+0)
               time.sleep(0.01)
               ax12_Lib.Speed(mot2, 0)
               time.sleep(0.01)
               



ser_Nextion.close()
ser_arduino.close()
cur.close()
db.close()
