import smtplib
import os
import sys
import logging

import mail.message

logging.basicConfig()
logger = logging.getLogger("AWSSESMAIL")
logger.setLevel(logging.INFO)


# Email connection options.
# AWS SES region endpoint.
HOST = os.getenv("HOST", "email-smtp.us-west-2.amazonaws.com")
try:
    PORT = int(os.getenv("PORT", 587))
except ValueError:
    print(f"PORT is expected tobe of type 'int', but value is '{os.getenv('PORT')}'.")
    sys.exit(1)
# AWS SES credentials expectedformat: "<user>:<password>"
AWS_SES_CREDENTIALS = os.getenv("AWS_SES_CREDENTIALS", "")


class AwsSesEmail(mail.message.Email):
    def __init__(
        self,
        host: str = HOST,
        port: int = PORT,
        aws_ses_credentials: str = AWS_SES_CREDENTIALS,
    ):
        super().__init__()
        self.host = host
        logger.info(f"msg: '{self.host}'")
        self.port = port
        logger.info(f"msg: '{self.port}'")
        logger.info(f"creds: '{aws_ses_credentials}'")
        self.user, self.password = aws_ses_credentials.split(":")
        # self.msg = message.Email()
        logger.info(f"msg: '{self.msg}'")

    def send_mail(self):
        # Attach the body to the 'msg'.
        self.attach_body()

        # stmplib docs recommend calling ehlo() before & after starttls()
        server = smtplib.SMTP(host=self.host, port=self.port)
        server.ehlo()
        # (250, 'email-smtp.amazonaws.com\n8BITMIME\nSIZE 10485760\nSTARTTLS\nAUTH PLAIN LOGIN\nOk')
        server.starttls()
        # (220, 'Ready to start TLS')
        server.ehlo()
        # (250, 'email-smtp.amazonaws.com\n8BITMIME\nSIZE 10485760\nSTARTTLS\nAUTH PLAIN LOGIN\nOk')
        server.login(user=self.user, password=self.password)
        # (235, 'Authentication successful.')
        server.send_message(
            from_addr=self.sender, to_addrs=self.recipients, msg=self.msg
        )
        # {}
        server.quit()
