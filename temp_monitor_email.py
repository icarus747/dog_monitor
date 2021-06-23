# coding=utf-8
import os
import smtplib
from email.mime.text import MIMEText
import glob
import time

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

critical = False
high = 80  # temp in °F
too_high = 85


# At First we have to get the current CPU-Temperature with this defined function
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp_string = res.replace("temp=", "").replace("'C\n", "")
    temp_f = float(temp_string) * 9.0 / 5.0 + 32.0
    return temp_f


def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_f


# Now we convert our value into a float number
temp = float(getCPUtemperature()) # CPU temp
print(temp)
# temp = float(read_temp()) # GPIO temp

# Check if the temperature is above 60°C (you can change this value, but it shouldn't be above 70)
if (temp > high):
    if temp > too_high:
        critical = True
        subject = f"Critical warning! The temperature is: {temp} shutting down!!"
        body = f"Critical warning! The actual temperature is: {temp} \n\n Shutting down the pi!"
    else:
        subject = f"Warning! The temperature is: {temp} "
        body = f"Warning! The actual temperature is: {temp} "

    # Enter your smtp Server-Connection
    server = smtplib.SMTP('smtp.gmail.com', 587)  # if your using gmail: smtp.gmail.com
    server.ehlo()
    server.starttls()
    server.ehlo()
    # Login
    user = ""
    password = ""
    server.login(user, password)

    recipients = ""
    sender = ""
    msg = MIMEText(body)
    # print(msg)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ",".join(recipients)

    # Finally send the mail
    server.sendmail(sender, recipients, msg.as_string())
    server.quit()

    # Critical, shut down the pi
    # if critical:
        # os.popen('sudo halt')

# Don't print anything otherwise.
# Cron will send you an email for any command that returns "any" output (so you would get another  email)
# else:
#   print("Everything is working fine!")
