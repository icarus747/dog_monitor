import adafruit_dht
import board
import smtplib
from email.mime.text import MIMEText
import random
import time
from ruamel.yaml import YAML

# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D23, use_pulseio=False)

critical = False
high = 83  # temp in °F
too_high = 88


def send_email(subject, body, secrets):
    # Enter your smtp Server-Connection
    server = smtplib.SMTP('smtp.gmail.com', 587)  # if your using gmail: smtp.gmail.com
    server.ehlo()
    server.starttls()
    server.ehlo()
    # Login
    user = secrets['account']['user']
    password = secrets['account']['password']
    server.login(user, password)

    recipients = secrets['email']['recipients']
    sender = secrets['email']['sender']
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
            temperature = dhtDevice.temperature
            temp_f = temperature * 9.0 / 5.0 + 32.0
            return round(temp_f)
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error


yaml = YAML(typ='safe')
secrets = yaml.load(open('secrets.yml'))
temp = float(read_temp())  # GPIO temp

# Check if the temperature is ok
if temp < high:
    action = ['bring us a bone', 'find our ball', 'bring us a treat', 'come scratch our back',
              'tell us about the beach', 'take us for a walk', 'bring us a shell']
    kid = ['Kendall', 'Lily']
    subject = f"Everything is working fine! Temp={temp}F"
    body = f"We are fine. Have Fun!!!\n\nTell {random.choice(kid)} to {random.choice(action)} when you get back!!!"
    send_email(subject, body, secrets)
