import logging
import sys
from typing import List, Union


from .message import Email
from .environment_variables import REGION_DEFAULT
from .exceptions import EmailException

logger = logging.getLogger("EventHooks.AwsSesEmail")


class AwsSesEmail(Email):
    """Send an email from your AWS account.

    This kind of email does not require AWS SES SMTP Crendentials.
    However, the AWS credentials (AWS access key ID and AWS secret access key) have to be set up using 'aws-vault' or a profile in '~/.aws/config' e.g.

    This can also handle a AWS 'ConfigurationSet'.

    Use 'SimpleEmail' in case you would like to configure AWS SES SMTP Credentials.
    """

    def __init__(
        self,
        sender: str = "",
        sender_name: str = "me",
        recipients: Union[List[str], str] = "",
        configuration_set: str = None,
        subject: str = "",
        body_text: str = "",
        region=REGION_DEFAULT,
    ):
        super().__init__(
            sender=sender,
            sender_name=sender_name,
            recipients=recipients,
            configuration_set=configuration_set,
            subject=subject,
            body_text=body_text,
        )
        logger.debug(f"msg: '{self.msg}'")

        try:
            import boto3
            from botocore.config import Config
        except (ImportError) as e:
            logger.critical(f"Please install 'eventhooks[aws]'. Error: '{str(e)}'.")
            sys.exit(1)

        boto_config = Config(
            region_name=region, signature_version="v4", retries={"max_attempts": 10, "mode": "standard"}
        )
        # Create a new SES resource and specify a region.
        session = boto3.session.Session()
        self.client = session.client("ses", config=boto_config)

    def send_mail(self):
        try:
            from botocore.exceptions import ClientError
        except (ImportError) as e:
            logger.critical(f"Please install 'eventhooks[aws]'. Error: '{str(e)}'.")
            sys.exit(1)

        try:
            CHARSET = "UTF-8"

            if self.sender_name:
                source = f"{self.sender_name} <{self.sender}>"
            else:
                source = self.sender

            message = {
                "Destination": {"ToAddresses": self.recipients},
                "Message": {
                    "Body": {"Text": {"Charset": CHARSET, "Data": self.body_text}},
                    "Subject": {"Charset": CHARSET, "Data": self.subject},
                },
                "Source": source,
            }
            if self.configuration_set:
                message.update(
                    {"ConfigurationSetName": self.configuration_set,}  # noqa: E231
                )

            # Provide the contents of the email.
            response = self.client.send_email(**message)
            # if not self.configuration_set:
            #     response = self.client.send_email(
            #         Destination={"ToAddresses": self.recipients},
            #         Message={
            #             "Body": {"Text": {"Charset": CHARSET, "Data": self.body_text}},
            #             "Subject": {"Charset": CHARSET, "Data": self.subject},
            #         },
            #         Source=source,
            #     )
            # else:
            #     response = self.client.send_email(
            #         Destination={"ToAddresses": self.recipients},
            #         Message={
            #             "Body": {"Text": {"Charset": CHARSET, "Data": self.body_text}},
            #             "Subject": {"Charset": CHARSET, "Data": self.subject},
            #         },
            #         Source=source,
            #         # If you are not using a configuration set, comment or delete the
            #         # following line
            #         ConfigurationSetName=self.configuration_set,
            #     )
            logger.info(f"Email sent. Message Id: {response['MessageId']}.")
        except ClientError as e:
            raise EmailException(e.response["Error"]["Message"])
        except Exception as e:
            raise EmailException(str(e))
