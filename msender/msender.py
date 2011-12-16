import sys
import smtplib
import email
import re

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendmail(fromAddr, rcptAddr, subject, template, tvars):
  with open(template) as template_file:
    tmpl = template_file.read()
  text = tmpl.format(**tvars)

  msg = MIMEMultipart("alternative")
  msg.set_charset("utf-8")

  msg["Subject"] = subject
  msg["From"] = fromAddr
  msg["To"] = rcptAddr
  msg.attach(MIMEText(text, "plain", "utf-8"))
  
  try:
    server = smtplib.SMTP("smtpout.dmz")
    server.sendmail(fromAddr, [rcptAddr], msg.as_string())
  finally:
    server.quit()

if __name__ == "__main__":
  if len(sys.argv) < 4:
    print 'Usage: msender.py from to subject tempvar1=val tempvar2=val'
    exit(-2)

  tvars = dict([v.split('=',1) for v in sys.argv[4:]])
  sendmail(sys.argv[1], sys.argv[2], sys.argv[3], 'mailtemplate.txt', tvars)

