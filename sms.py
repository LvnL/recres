import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import requests 
import smtplib

import secrets

carrierGateways = {
    #"at&t": "",
    #"metropcs": "",
    "sprint": "@pm.sprint.com",
    "t-mobile": "@tmomail.net",
    #"uscellular": "",
    "verizon": "@vtext.com"
}

def send_message(phone_number, subject, content):
    email = secrets.email
    password = secrets.email_password
    try:
        to_address = phone_number + get_carrier(phone_number)
    except TypeError as error:
        return False

    server = smtplib.SMTP(secrets.email_smtp_server, 587)

    message = MIMEMultipart()
    message["From"] = secrets.email
    message["To"] = to_address
    message["Subject"] = subject
    message.attach(MIMEText(content))

    server.starttls()
    server.login(email, password)
    server.sendmail(email, to_address, message.as_string())
    server.quit()

    return True

def get_carrier(number):
    url = "https://api.telnyx.com/v1/phone_number/1" + number
    html = requests.get(url).text
    data = json.loads(html)
    carrier = data["carrier"]["name"]

    for key in carrierGateways.keys():
        if key in carrier.lower():
            return carrierGateways.get(key)