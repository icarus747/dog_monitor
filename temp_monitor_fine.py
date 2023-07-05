import adafruit_dht
import board
import smtplib
from email.mime.text import MIMEText
import random
import time
import os

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.GP28, use_pulseio=False)

critical = False
high = 83  # temp in °F
too_high = 88


def send_email(subject, body):
    # Enter your smtp Server-Connection
    server = smtplib.SMTP('smtp.gmail.com', 587)  # if your using gmail: smtp.gmail.com
    server.ehlo()
    server.starttls()
    server.ehlo()
    # Login
    user = os.getenv('account_user')
    password = os.getenv('account_password')
    server.login(user, password)

    recipients = ['recipient1','recipient2','recipient3']
    sender = user
    msg = MIMEText(body)
    # print(msg)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ",".join(recipients)

    # Finally send the mail
    try:
        server.sendmail(sender, recipients, msg.as_string())
        server.quit()
        print('emails sent!')
    except:
        print('something wrong.')


def read_temp():
    while True:
        try:
            temp_f = dhtDevice.temperature * 9.0 / 5.0 + 32.0
            return round(temp_f)
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error


temp = float(read_temp())  # GPIO temp

# Check if the temperature is ok
if temp < high:
    action = ['bring us a bone', 'find our ball', 'bring us a treat', 'come scratch our back',
              'tell us about the beach', 'take us for a walk', 'bring us a shell']
    kid = ['Kendall', 'Lily']
    subject = f"Everything is working fine! Temp={temp}F"
    body = f"We are fine. Have Fun!!!\n\nTell {random.choice(kid)} to {random.choice(action)} when you get back!!!"
    send_email(subject, body)
