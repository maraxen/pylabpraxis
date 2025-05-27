import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..configure import PraxisConfiguration

CELLPHONE_CARRIER_GATEWAYS = {
    "att": "@txt.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com",
    "boost": "@sms.myboostmobile.com",
    "cricket": "@sms.cricketwireless.net",
    "metropcs": "@mymetropcs.com",
    "tracfone": "@mmst5.tracfone.com",
    "uscellular": "@email.uscc.net",
    "virgin": "@vmobl.com",
    "google": "@msg.fi.google.com",
    "projectfi": "@msg.fi.google.com",
    "ting": "@message.ting.com",
    "consumer": "@cruwireless.net",
    "cspire": "@cspire1.com",
    "pageplus": "@vtext.com",
    "ting": "@message.ting.com",
    "republic": "@text.republicwireless.com",
    "fi": "@msg.fi.google.com",
    "xfinity": "@vtext.com",
    "freedompop": "@txt.freedompop.com",
    "simple": "@smtext.com",
    "fi": "@msg.fi.google.com",
    "truphone": "@tmail.co.uk",
    "mint": "@mailmymobile.net",
    "ultra": "@sms.myultramobile.com",
    "ting": "@message.ting.com",
    "cricket": "@mms.cricketwireless.net",
}


class Notifier:
    def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password

    def send_email(
        self, sender_email: str, recipient_email: str, subject: str, body: str
    ):
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            print("Email sent!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def send_text(
        self,
        sender_email: str,
        recipient_phone: str,
        carrier: str,
        subject: str,
        body: str,
    ):
        recipient_email = recipient_phone + CELLPHONE_CARRIER_GATEWAYS[carrier]
        self.send_email(sender_email, recipient_email, subject, body)


DEFAULT_NOTIFIER = Notifier(**PraxisConfiguration().smtp_details())
