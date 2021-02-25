import smtplib
import logging
from typing import List, Union

from .message import Email
from .environment_variables import (
    HOST,
    PORT,
)
from .exceptions import EmailException

logging.basicConfig()
logger = logging.getLogger("SIMPLEMAIL")
logger.setLevel(logging.INFO)


class SimpleEmail(Email):
    """Send a simple email using smtplib.

    This uses 'smtplib' to send an email and requires a host and port.
    'TLS' is the only option.

    This can be used with AWS SES when using AWS SES SMTP Credentials.
    Credentials are expected in the following format: 'user:password'

    This can also handle a AWS 'ConfigurationSet'.
    """

    def __init__(
        self,
        host: str = HOST,
        port: int = PORT,
        credentials: str = "",
        sender: str = "",
        sender_name: str = "me",
        recipients: Union[List[str], str] = "",
        configuration_set: str = None,
        subject: str = "",
        body_text: str = "",
        tls=True,
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
        self.tls = tls
        self.user = self.password = ""
        credentials_ = credentials
        if ":" in credentials_:
            credentials = credentials_.split(":")
            # self.user = b64encode(credentials[0].encode()).decode()
            # self.password = b64encode(credentials[1].encode()).decode()
            self.user = credentials[0].strip()
            self.password = credentials[1].strip()
        # self.msg = message.Email()
        logger.debug(f"msg: '{self.msg}'")

    def send_mail(self):
        try:
            # Attach the body to the 'msg'.
            self.attach_body()
            # stmplib docs recommend calling ehlo() before & after starttls()
            server = smtplib.SMTP(host=self.host, port=self.port)
            if self.tls:
                server.ehlo()
                # (250, 'email-smtp.amazonaws.com\n8BITMIME\nSIZE 10485760\nSTARTTLS\nAUTH PLAIN LOGIN\nOk')
                server.starttls()
                # (220, 'Ready to start TLS')
                server.ehlo()
                # (250, 'email-smtp.amazonaws.com\n8BITMIME\nSIZE 10485760\nSTARTTLS\nAUTH PLAIN LOGIN\nOk')
                server.login(user=self.user, password=self.password)
                # (235, 'Authentication successful.')
            server.send_message(from_addr=self.sender, to_addrs=self.recipients, msg=self.msg)
            # {}
            server.quit()
            logger.info("Email sent.")
        except Exception as e:
            raise EmailException(str(e))
