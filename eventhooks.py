"""
Events

Events is supposed to be an event module which sends webhooks to:
* Mattermost
* Dockerhub
* Emails with AWS SES

"""

import logging
from typing import Tuple, List, Union
import json

import requests

import mail.aws_ses
import mail.simple
import mail.message
from mail.exceptions import EmailException


logging.basicConfig()
logger = logging.getLogger("EventHooks")
logger.setLevel(logging.INFO)


class WatchEvent:
    """Event base class.
    """

    def __init__(
        self, name: str = "", description: str = "", realms: Tuple[str] = None
    ):
        self.name = name
        self.description = description
        self.realms = realms

    def allowed(self, realm=None):
        """Check allowed realms.

        If no realms are configured, triggering the webhook is allowed.
        """

        allowed = not self.realms or realm in self.realms
        if not allowed:
            logger.warning(
                f"Cannot trigger '{str(self)}'. '{realm}' not in '{self.realms}'."
            )
        return allowed

    def __str__(self):
        result = [f"Event '{self.name}'."]
        if self.description:
            result.append(self.description)
        return " ".join(result)


class EmailHook(WatchEvent):
    def __init__(
        self,
        name: str = "",
        email: mail.message.Email = None,
        realms: Tuple[str] = None,
    ):
        self.email = email

        super().__init__(name=name, realms=realms)

    def _trigger(self, data=None, debug=False):
        if debug:
            return None
        try:
            data_ = ""
            if data:
                if isinstance(data, dict):
                    data_ = json.dumps(data, indent=2)
                else:
                    # Assuming 'str' most of the time.
                    data_ = str(data)
            self.email.body_text = data_
            self.email.send_mail()
        except EmailException as e:
            logger.error(f"Error: '{str(e)}'.")
            return

    def __str__(self):
        return (
            super().__str__()
            + f" With subject '{self.email.subject}' to '{self.email.recipients}'."
        )


class WebHook(WatchEvent):
    """Webhook base class.

    Makes the actual webhook trigger request.
    Checks alloweed realms.

    A realm is just a functionality, that allows to restrict events to certain types of triggers.

    Example:
    Though a webhook can be configured to trigger in case of events A and B, event B should not be triggered in case of event A and vice versa.
    """

    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, name="", url="", url_safe="", realms: Tuple[str] = None):
        self.url = url
        self.url_safe = url_safe
        super().__init__(name=name, description=f"To '{self.url_safe}'.", realms=realms)
        logger.debug(f"Webhook event URL '{self.url_safe}'.")
        logger.debug(f"Webhook event REALMS '{self.realms}'.")

    def _trigger(self, data=None, debug=False):
        if debug:
            return None
        response = None
        try:
            response = requests.post(self.url, json=data, headers=self.HEADERS)
        except (
            requests.exceptions.MissingSchema,
            requests.exceptions.RequestException,
        ) as e:
            logger.error(f"Error: '{str(e)}'.")
        if not response:
            logger.error("No response.")
            return None
        try:
            logger.debug(f"[{response.status_code}], {response.json()}")
        except Exception:
            logger.debug(f"[{response.status_code}], {response.text}")

        return response


class MattermostWebHook(WebHook):
    """Mattermost webhook event.
    """

    URL = "{host}/hooks/{token}"

    def __init__(self, name="", host="", token="", realms: Tuple[str] = None):
        super().__init__(
            name=name,
            url=self.URL.format(host=host, token=token),
            url_safe=self.URL.format(host=host, token="***"),
            realms=realms,
        )

    def trigger(self, data=None, realm=None, debug=False):
        if not super().allowed(realm):
            return
        if not data:
            logger.error(f"No info for trigger: '{str(self)}'.")
            return
        logger.warn(f"Trigger mattermost webhook: '{str(self)}' with '{data}'.")
        data_ = {"text": f"{data}"}
        response = self._trigger(data=data_, debug=debug)
        if response:
            logger.warn(
                f"Mattermost webhook response: '{response.status_code}', '{response.text}'."
            )


class DockerCloudWebHook(WebHook):
    """Dockerhub webhook event.
    """

    URL = "https://hub.docker.com/api/build/v1/source/{source}/trigger/{token}/call/"

    def __init__(
        self,
        name="",
        source_branch="master",
        source_type="Branch",
        source="",
        token="",
        realms: Tuple[str] = None,
    ):
        self.source_branch = source_branch
        self.source_type = source_type
        super().__init__(
            name=name,
            url=self.URL.format(source=source, token=token),
            url_safe=self.URL.format(source="***", token="***"),
            realms=realms,
        )

    def trigger(self, data, realm=None, debug=False):
        if not super().allowed(realm):
            return
        if not self.source_branch or not self.source_type:
            logger.error(f"No info for trigger: '{str(self)}'.")
            return
        logger.warn(
            f"Trigger dockercloud webhook for '{self.source_type}' '{self.source_branch}': '{str(self)}'."
        )
        data_ = {"source_type": self.source_type, "source_name": self.source_branch}

        response = self._trigger(data=data_, debug=debug)
        if response:
            logger.warn(
                f"Dockercloud webhook response: '{response.status_code}', '{response.text}'."
            )


class SimpleEmailHook(EmailHook):
    """Simple email hook event.

    Needs host and portas well as user credentials (user,password).
    User credentials are expected to come in the following format: 'user:password'.

    This can also be used with AWS SES.
    Existing AWS SES SMTP Credentials should be used.
    """

    def __init__(
        self,
        name="",
        host: str = "",
        port: int = 0,
        credentials: str = "",
        sender: str = "",
        sender_name: str = "",
        recipients: Union[List[str], str] = None,
        realms: Tuple[str] = None,
    ):
        email = mail.simple.SimpleEmail(
            host=host,
            port=port,
            recipients=recipients,
            sender=sender,
            sender_name=sender_name,
            credentials=credentials,
        )
        if not email.subject:
            email.subject = name

        super().__init__(name=name, email=email, realms=realms)

    def trigger(self, data, realm=None, debug=False):
        if not super().allowed(realm):
            return
        logger.warn(f"Trigger Simple email hook for: '{str(self)}'.")
        self._trigger(data=data, debug=debug)


class AwsSesEmailHook(EmailHook):
    """AWS SES email hook event.

    This requires an existing AWS profile or AWS credentials (AWS access key ID and AWS secret access key).
    It does not require AWS SES SMTP Credentials.

    No roles or policies are created.
    """

    def __init__(
        self,
        name="",
        sender: str = "",
        sender_name: str = "",
        recipients: Union[List[str], str] = None,
        realms: Tuple[str] = None,
    ):
        email = mail.aws_ses.AwsSesEmail(
            recipients=recipients, sender=sender, sender_name=sender_name,
        )
        if not email.subject:
            email.subject = name

        super().__init__(name=name, email=email, realms=realms)

    def trigger(self, data, realm=None, debug=False):
        if not super().allowed(realm):
            return
        logger.warn(f"Trigger AWS SES email hook for: '{str(self)}'.")
        self._trigger(data=data, debug=debug)
