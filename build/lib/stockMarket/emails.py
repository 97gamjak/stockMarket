import smtplib
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def write_email(email_addresses=None, email_body=None, email_subject=None, email_attachment=None):
    if email_addresses is not None:
        receiver_emails = email_addresses
    else:
        raise ValueError("No email addresses given")

    sender_email = "97gamjak@gmail.com"  # Enter your address
    password = "clqk otpq nquh tjmg"
    body = email_body
    attachment = email_attachment

    subject = email_subject

    for receiver_email in receiver_emails:

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message["Bcc"] = receiver_email

        message.attach(MIMEText(body, "plain"))

        with open(attachment, "rb") as to_attach:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(to_attach.read())

        encoders.encode_base64(part)

        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {attachment}",
        )

        message.attach(part)
        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
