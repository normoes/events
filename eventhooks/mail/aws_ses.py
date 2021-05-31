import logging
import sys
from typing import List, Union


from .message import Email
from .environment_variables import REGION_DEFAULT
from .exceptions import EmailException

logger = logging.getLogger("EventHooks.AwsSesEmail")

CHARSET = "UTF-8"


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
        except (ImportError) as e_import:
            logger.critical(f"Please install 'eventhooks[aws]'. Error: '{str(e_import)}'.")
            sys.exit(1)

        config = {"signature_version": "v4", "retries": {"max_attempts": 10, "mode": "standard"}}
        # Use 'boto3' default value when no region is given.
        if region:
            config.update({"region_name": "region"})
        boto_config = Config(**config)
        # Create a new SES resource and specify a region.
        session = boto3.session.Session()
        self.client = session.client("ses", config=boto_config)

    def send_mail(self):
        try:
            from botocore.exceptions import ClientError
        except (ImportError) as e_import:
            logger.critical(f"Please install 'eventhooks[aws]'. Error: '{str(e_import)}'.")
            sys.exit(1)

        try:

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
                    {
                        "ConfigurationSetName": self.configuration_set,
                    }  # noqa: E231
                )

            # Provide the contents of the email.
            response = self.client.send_email(**message)
            logger.info(f"Email sent. Message Id: {response['MessageId']}.")
        except ClientError as e_client:
            raise EmailException(e_client.response["Error"]["Message"]) from e_client
        except Exception as e_general:
            raise EmailException(str(e_general)) from e_general
