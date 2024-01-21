# SPDX-FileCopyrightText: 2022 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# KP 11:14 PM 7/6/2023

import wifi
import ssl
import socketpool
import time
# Time lib
import adafruit_ntp
import rtc
# Email
import os
import umail
from adafruit_dht import DHT22
import board
import microcontroller
import adafruit_requests as requests

SPLUNK = True
STARTUP_WAIT = 5
mailserver = 'smtp.gmail.com'
PORT = 587
# Initial the dht device, with data pin connected to:
dhtDevice = DHT22(board.GP28)

print()
print("short wait for startup")
time.sleep(STARTUP_WAIT)

pool = socketpool.SocketPool(wifi.radio)
wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
if SPLUNK:
    req = requests.Session(pool)  # Needed for Splunk
print(f"local address {wifi.radio.ipv4_address}")

ntp = adafruit_ntp.NTP(pool, tz_offset=-5)
try:
    rtc.RTC().datetime = ntp.datetime
except:
    print("RTC fail")
    datetime = time.localtime()


# def connect():
#    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
#    while wifi.radio.ipv4_address == None:
#        print("Waiting for connection...")
#        time.sleep(1)
#    print(f"local address {wifi.radio.ipv4_address}")
#    pool = socketpool.SocketPool(wifi.radio)
#    ssl_context = ssl.create_default_context()

def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )


def read_temp():
    while True:
        try:
            temp_f = dhtDevice.temperature * 9.0 / 5.0 + 32.0
            return temp_f
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error


def read_humidity():
    while True:
        try:
            humidity = dhtDevice.humidity
            return humidity
        except RuntimeError as error:
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error


def send_mail(pool, temp, current_date):
    smtp = umail.SMTP(mailserver, 587, ssl=False, username=os.getenv('from'), password=os.getenv('account_password'),
                      pool=pool)
    print("\r\nSending to", os.getenv('recipient2'))
    smtp.to([os.getenv('recipient2'), os.getenv('recipient3')])  # , os.getenv('recipient1')])
    smtp.write(f"Subject: Temperature is {temp}.\r\n")
    smtp.send(f"At {current_date}, the temperature is {temp}F.")
    smtp.quit()


def send_splunk(current_date, temp, humidity):
    fqdn = os.getenv('SPLUNK_FQDN')
    url = f'http://{fqdn}:8088/services/collector/event'
    token = os.getenv('SPLUNK_TOKEN')
    authHeader = {'Authorization': 'Splunk ' + token}
    jsonDict = {"index": "main", "event": {'message': f"{current_date} - temperature={temp}, humidity={humidity}"}}
    print(jsonDict)

    r = req.post(url, headers=authHeader, json=jsonDict)
    print(r)


while True:
    # TODO: Temp range for alerts
    try:
        current_date = "{}".format(_format_datetime(time.localtime()))
        if time.localtime().tm_min:  # == 08 or time.localtime().tm_min == 30:
            print(current_date)
            temp = float(read_temp())
            humidity = read_humidity()
            print(temp)
            if SPLUNK:
                print("Splunk!")
                send_splunk(current_date, temp, humidity)
            if not SPLUNK:
                send_mail(pool, temp, current_date)
                print('Email Sent!')
            time.sleep(10)
        print(f"waiting again...{current_date}")
        time.sleep(50)
        # print(temp)
        # send_mail(pool, temp)
        # print('Email Sent!')
        # time.sleep(1800)
    except KeyboardInterrupt:
        microcontroller.reset()
