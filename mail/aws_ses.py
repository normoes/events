import smtplib
import logging
from typing import List, Union

import mail.message
from mail.environment_variables import (
    HOST,
    PORT,
    AWS_SES_CREDENTIALS,
    SENDER,
    SENDER_NAME,
    RECIPIENTS,
    CONFIGURATION_SET,
    SUBJECT,
    BODY_TEXT,
)
from mail.exceptions import EmailException

logging.basicConfig()
logger = logging.getLogger("AWSSESMAIL")
logger.setLevel(logging.INFO)


class AwsSesEmail(mail.message.Email):
    def __init__(
        self,
        host: str = HOST,
        port: int = PORT,
        aws_ses_credentials: str = AWS_SES_CREDENTIALS,
        sender: str = SENDER,
        sender_name: str = SENDER_NAME,
        recipients: Union[List[str], str] = RECIPIENTS,
        configuration_set: str = CONFIGURATION_SET,
        subject: str = SUBJECT,
        body_text: str = BODY_TEXT,
    ):
        super().__init__(
            sender=sender,
            sender_name=sender_name,
            recipients=recipients,
            configuration_set=configuration_set,
            subject=subject,
            body_text=body_text,
        )
        self.host = host if host else HOST
        logger.debug(f"msg: '{self.host}'")
        self.port = port if port else PORT
        logger.debug(f"msg: '{self.port}'")
        self.user = self.password = ""
        aws_ses_credentials_ = (
            aws_ses_credentials if aws_ses_credentials else AWS_SES_CREDENTIALS
        )
        if ":" in aws_ses_credentials_:
            self.user, self.password = aws_ses_credentials_.split(":")
        # self.msg = message.Email()
        logger.debug(f"msg: '{self.msg}'")

    def send_mail(self):
        try:
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
            logger.info("Email sent.")
        except Exception as e:
            raise EmailException(str(e))
