
import email
import smtplib
from email.mime.text import MIMEText
from flask_test import UserRegistration

def get_mails():
    emails = UserRegistration()
    get_mail_ids = emails.get_user_emails()
    for i in get_mail_ids:
        print(i)
    subject = 'New Expense Notification'
    body = f"You have been added to a new expense. You owe {participant['amount_owed']} for this expense."
    sender = "sender@gmail.com"
    recipients = ["recipient1@gmail.com", "recipient2@gmail.com"]
    password = "smtp password"

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")

send_email(subject, body, sender, recipients, password)
