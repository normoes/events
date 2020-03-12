import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Email message options.
SENDER = os.getenv("SENDER", "")
SENDER_NAME = os.getenv("SENDER_NAME", "")
# Comma separated list of recipients.
RECIPIENTS = os.getenv("RECIPIENTS", "")
# [Optional] The name of configuration set to use for this message.
# Used with '"X-SES-CONFIGURATION-SET' header.
CONFIGURATION_SET = os.getenv("CONFIGURATION_SET", None)
SUBJECT = os.getenv("SUBJECT", "")
BODY_TEXT = os.getenv("BODY_TEXT", "")


class Email:
    def __init__(
        self,
        sender: str = SENDER,
        sender_name: str = SENDER_NAME,
        recipients: str = RECIPIENTS,
        configuration_set: str = CONFIGURATION_SET,
        subject: str = SUBJECT,
        body_text: str = BODY_TEXT,
    ):
        # This address must be verified with AWS SES.
        # Alternatively the DNS needs to be verified.
        self.sender = sender
        self.sender_name = sender_name
        if isinstance(recipients, list):
            recipients_ = recipients
        else:
            # Assuming 'str'.
            recipients_ = recipients.split(",")
        self.recipients = []
        for recipient in recipients_:
            self.recipients.append(recipient.strip())
        self.configuration_set = configuration_set
        self.subject = subject
        self._body_text = body_text

        self.msg = MIMEMultipart("alternative")
        self.msg["Subject"] = self.subject
        self.msg["From"] = email.utils.formataddr((self.sender_name, self.sender))
        self.msg["To"] = ", ".join(self.recipients)
        if self.configuration_set:
            self.msg.add_header("X-SES-CONFIGURATION-SET", CONFIGURATION_SET)

    @property
    def body_text(self):
        return self._body_text

    @body_text.setter
    def body_text(self, value):
        self._body_text = str(value)

    def attach_body(self):
        # Record the MIME type of the plain text part - text/plain.
        text_part = MIMEText(self._body_text, "plain")

        self.msg.attach(text_part)
