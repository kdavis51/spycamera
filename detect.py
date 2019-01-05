import serial
from time import sleep
import os, signal, time, smtplib, socket
import RPi.GPIO as GPIO

try:
        import httplib
except:
        import http.client as httplib

MotionSensor=21  #GPIO 21 pin for Motion detection
MotionSensorLED=16 #GPIO 16 pin for Sensor1 LED
WifiLED=26 #GPIO 26 pin for WIFI- LED will be on if WIFI is not working
Buzzer=2 # GPIO 2 pin for Buzzer
Buzzertoggleswitch=17 #GPIO 17 pin for Buzzer ON/OFF toggle
Emailtoggleswitch=4 #GPIO 4 pin for Buzzer ON/OFF toggle
ProgRunningLED=18 #GPIO 18 pin for Program running status - LED will be on if program is running
emailcount = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(MotionSensor,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(MotionSensorLED,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(Buzzer,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(WifiLED,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(Buzzertoggleswitch,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(Emailtoggleswitch,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ProgRunningLED,GPIO.OUT,initial=GPIO.HIGH)

def getip():
        global IPAddr

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
        IPAddr = s.getsockname()[0]

def sendemail():
        getip()
        print "\n\n SENDING EMAIL...... \n\n"
        date = time.strftime("%m/%d/%Y")
        smtpUser = 'XXXXXXXXXXX@gmail.com'
        smtpPass = 'XXXXXXXXXXXXXXXXXXXXX'
        toAdd    = 'XXXXXXXXXXX@gmail.com'
        fromAdd = smtpUser
        subject = "Alerts!"
        header = 'To: ' + toAdd + '\n' + 'From: ' + fromAdd + '\n' + 'Subject: ' + subject
        body = "Motion Detected:" + str(date) + "\n\nhttp://" + str(IPAddr)+":8000\n"
        print header + '\n' + body
        s = smtplib.SMTP('smtp.gmail.com',587)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(smtpUser, smtpPass)
        s.sendmail(fromAdd, toAdd, header + '\n\n' + body)
        s.quit()
        sleep(2)

def is_connected():

        conn = httplib.HTTPConnection("www.bing.com", timeout=5)
        try:
                conn.request("HEAD","/")
                conn.close()

                return True
        except:
                conn.close()
                return False

def bump(channel):
        #os.system('clear')

        global emailcount

        emailcount = emailcount + 1
        print ("")
        print ("********************")
        print ("* MOTION DETECTED! *")
        print ("********************")
        print ("")
        if (emailcount > 1):

                if (GPIO.input(Emailtoggleswitch)):
                        print (emailcount)
                        emailconnected = is_connected()
                        if (emailconnected==False):
                                print ("NO Email - NO Internet Connection!")
                        else:
                                sendemail()
                else:
                        print ("Email turned off")

                emailcount = 0

        if (GPIO.input(Buzzertoggleswitch)):
                GPIO.output(Buzzer,GPIO.HIGH)
        else:
                print ("Buzzer turned off")

        GPIO.output(MotionSensorLED,GPIO.HIGH)
        sleep(0.3)

        GPIO.output(MotionSensorLED,GPIO.LOW)
        GPIO.output(Buzzer,GPIO.LOW)

        sleep(0.3)

        if (GPIO.input(Buzzertoggleswitch)):
                GPIO.output(Buzzer,GPIO.HIGH)

        GPIO.output(MotionSensorLED,GPIO.HIGH)
        sleep(0.3)

        GPIO.output(MotionSensorLED,GPIO.LOW)
        GPIO.output(Buzzer,GPIO.LOW)

GPIO.add_event_detect(MotionSensor,GPIO.RISING,callback=bump, bouncetime=600)

try:

        while True:
                sleep(10)  # this is very important sleep; otherwise the PI consumes CPU

                connected = is_connected()

                if (connected==False):
                        print ("NO Internet Connection!")
                        GPIO.output(WifiLED,GPIO.HIGH)
                        sleep(0.5)
                        GPIO.output(WifiLED,GPIO.LOW)
                        sleep(0.5)
                        GPIO.output(WifiLED,GPIO.HIGH)
                        sleep(0.5)
                        GPIO.output(WifiLED,GPIO.LOW)
                        sleep(0.5)
                else:
                        GPIO.output(WifiLED,GPIO.LOW)

except (KeyboardInterrupt, SystemExit):
        print ("\nExisting....")

print ("De-Configured & GPIO pins cleaned up!")

GPIO.cleanup()
print ("Bye bye!")
os.kill(os.getpid(),signal.SIGTERM)
