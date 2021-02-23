from typing import List, Union

import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email:
    def __init__(
        self,
        sender: str,
        sender_name: str = "me",
        recipients: Union[List[str], str] = "",
        configuration_set: str = None,
        subject: str = "",
        body_text: str = "",
    ):
        # This address must be verified with AWS SES.
        # Alternatively the DNS needs to be verified.
        self.sender = sender
        self.sender_name = sender_name
        recipients_ = []
        if recipients:
            if isinstance(recipients, list):
                recipients_ = recipients
            else:
                # Assuming 'str'.
                recipients_ = recipients.split(",")
        self.recipients = []
        for recipient in recipients_:
            self.recipients.append(recipient.strip())
        self.configuration_set = configuration_set
        self._subject = subject
        self._body_text = body_text

        self.msg = MIMEMultipart("alternative")
        self.msg["Subject"] = self._subject
        self.msg["From"] = email.utils.formataddr((self.sender_name, self.sender))
        self.msg["To"] = ", ".join(self.recipients)
        if self.configuration_set:
            self.msg.add_header("X-SES-CONFIGURATION-SET", self.configuration_set)

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self, value):
        self._subject = str(value)
        self.msg.replace_header("Subject", self._subject)

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
