"""Notification utilities for sending emails and SMS in PyLabPraxis."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from praxis.backend.configure import PraxisConfiguration

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
  "republic": "@text.republicwireless.com",
  "fi": "@msg.fi.google.com",
  "xfinity": "@vtext.com",
  "freedompop": "@txt.freedompop.com",
  "simple": "@smtext.com",
  "truphone": "@tmail.co.uk",
  "mint": "@mailmymobile.net",
  "ultra": "@sms.myultramobile.com",
}


class Notifier:
  """A utility class for sending email and SMS notifications."""

  def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password) -> None:
    """Initialize the Notifier with SMTP server details."""
    self.smtp_server = smtp_server
    self.smtp_port = smtp_port
    self.smtp_username = smtp_username
    self.smtp_password = smtp_password

  def send_email(
    self,
    sender_email: str,
    recipient_email: str,
    subject: str,
    body: str,
  ) -> None:
    """Send an email using the configured SMTP server.

    Args:
        sender_email (str): The sender's email address.
        recipient_email (str): The recipient's email address.
        subject (str): The subject of the email.
        body (str): The body of the email.

    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
      with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
        server.login(self.smtp_username, self.smtp_password)
        server.send_message(message)
    except Exception:
      pass

  def send_text(
    self,
    sender_email: str,
    recipient_phone: str,
    carrier: str,
    subject: str,
    body: str,
  ) -> None:
    """Send a text message via email-to-SMS gateway.

    Args:
        sender_email (str): The sender's email address.
        recipient_phone (str): The recipient's phone number.
        carrier (str): The recipient's carrier name
            (see CELLPHONE_CARRIER_GATEWAYS).
        subject (str): The subject of the message.
        body (str): The body of the message.

    """
    recipient_email = recipient_phone + CELLPHONE_CARRIER_GATEWAYS[carrier]
    self.send_email(sender_email, recipient_email, subject, body)


DEFAULT_NOTIFIER = Notifier(**PraxisConfiguration().smtp_details)
