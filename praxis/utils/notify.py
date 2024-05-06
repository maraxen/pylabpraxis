import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Emailer:
  """
  Emailer class to send emails using SMTP server
  """
  def __init__(self, email, password):
    self.email = email
    self.password = password
    self.server = smtplib.SMTP('server', 587)
    self.server.starttls()
    self.server.login(email, password)

  def send(self, to, subject, body):
    msg = MIMEMultipart()
    msg['From'] = self.email
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    self.server.sendmail(self.email, to, msg.as_string())

  def __del__(self):
    self.server.quit()
