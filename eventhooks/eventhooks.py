"""
Events

Events is supposed to be an event module which sends webhooks to:
* Mattermost
* Dockerhub
* Emails with AWS SES

"""

import logging
from typing import Tuple, List, Union, Optional
from typing import AnyStr  # TypeVar('AnyStr', str, bytes).
import json
import re

import requests

from .mail import message
from .mail.exceptions import EmailException


logging.basicConfig()
logger = logging.getLogger("EventHooks")
logger.setLevel(logging.INFO)


class WatchEvent:
    """Event base class.
    """

    def __init__(self, name: str = "", description: str = "", realms: Tuple[str] = None):
        self.name = name
        self.description = description
        self.realms = realms

    def allowed(self, realm=None):
        """Check allowed realms.

        If no realms are configured, triggering the webhook is allowed.
        """

        allowed = not self.realms or realm in self.realms
        if not allowed:
            logger.debug(f"Cannot trigger '{str(self)}'. '{realm}' not in '{self.realms}'.")
        return allowed

    def __str__(self):
        result = [f"Event '{self.name}'."]
        if self.description:
            result.append(self.description)
        return " ".join(result)


# class GithubHook(WatchEvent):
#     """Github hook.
#
#     Clones a repository.
#     Checks out a branch/tag.
#     Commits and pushes to a repository.
#     Checks allowed realms.
#
#     """
#
#     HEADERS = {"Content-Type": "application/json"}
#
#     def __init__(self, name="", url="", url_safe="", realms: Tuple[str] = None):
#         self.url = url
#         self.url_safe = url_safe if url_safe else url
#         super().__init__(name=name, description=f"To '{self.url_safe}'.", realms=realms)
#         logger.debug(f"Webhook event URL '{self.url_safe}'.")
#         logger.debug(f"Webhook event REALMS '{self.realms}'.")
#
#     def __str__(self):
#         return f"Webhook: {self.url_safe}"
#
#     def trigger(self, data, realm=None, debug=False):
#         if not self.allowed(realm):
#             return
#         logger.warn(f"Trigger raw webhook: '{str(self)}' with '{data}'.")
#         response = self._trigger(data=data, debug=debug)
#         if response:
#             help_text = re.sub("\n", "", response.text)
#             logger.warn(
#                 f"Raw webhook response: '{response.status_code}', '{help_text[:25]}...{help_text[-25:]}'."
#             )
#
#     def _trigger(self, data=None, debug=False):
#         if debug:
#             logger.debug("[DEBUG]: Not triggering.")
#             return None
#         response = None
#         try:
#             response = requests.post(self.url, json=data, headers=self.HEADERS)
#         except (
#             requests.exceptions.MissingSchema,
#             requests.exceptions.RequestException,
#         ) as e:
#             logger.error(f"Error: '{str(e)}'.")
#         if response is None:
#             logger.error("No response.")
#             return None
#         try:
#             logger.debug(f"[{response.status_code}], {response.json()}")
#         except Exception:
#             logger.debug(f"[{response.status_code}], {response.text}")
#
#         return response


class RabbitMqHook(WatchEvent):
    """RabbitMQ hook base class.

    Publishes messages to RabbitMQ exchanges.
    Checks allowed realms.

    A realm is just a functionality, that allows to restrict events to certain types of triggers.

    Example:
    Though a webhook can be configured to trigger in case of events A and B, event B should not be triggered in case of event A and vice versa.
    """

    def __init__(
        self,
        name: str = "",
        host: str = "",
        vhost: str = "/",
        exchange: str = "",
        routing_key: str = "example_queue",
        user: str = "",
        password: str = "",
        realms: Tuple[str] = None,
    ):
        self.name = name
        self.host = host
        self.vhost = vhost
        self.exchange = exchange
        self.routing_key = routing_key
        self.user = user
        self.password = password
        super().__init__(
            name=name,
            description=f"To '{self.host}' with user '{self.user}' [exchange: '{self.exchange}', vhost: '{self.vhost}'].",
            realms=realms,
        )
        logger.debug(f"RabbitMqHook event URL '{self.host}'.")
        logger.debug(f"RabbitMqHook event REALMS '{self.realms}'.")

        # 'pika' connection parameters
        import pika

        if not self.user or not self.password:
            raise pika.exceptions.ProbableAuthenticationError("Event '{self.name}'. Check RabbitMQ username/password.")
        credentials = pika.PlainCredentials(self.user, self.password)
        self.conn_params = pika.ConnectionParameters(host=self.host, virtual_host=self.vhost, credentials=credentials)

    def trigger(self, data, realm=None, debug=False):
        if not self.allowed(realm):
            return
        logger.info(f"Event '{self.name}'. Trigger RabbitMqHook: '{str(self)}' with '{data}'.")
        self._trigger(data=data, debug=debug)

    def _trigger(self, data: AnyStr, debug=False):
        if debug:
            logger.debug("[DEBUG]: Not triggering.")
            return None
        if not data:
            logger.error(f"Event '{self.name}'. No info for trigger: '{str(self)}'.")
            return
        data_ = ""
        if isinstance(data, dict):
            data_ = json.dumps(data, indent=2)
        else:
            # Assuming 'str' most of the time.
            data_ = str(data)
        import pika

        try:
            # 'pika' connection
            conn = pika.BlockingConnection(self.conn_params)
            try:
                channel = conn.channel()
                channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=data_)
            finally:
                conn.close()
        except (pika.exceptions.AMQPConnectionError) as e:
            logger.error(f"Event '{self.name}'. AMQP connection error with '{str(self)}'. Error: '{str(e)}'.")
        except (pika.exceptions.AMQPError) as e:
            logger.error(f"Event '{self.name}'. AMQP error with '{str(self)}'. Error: '{str(e)}'.")

    def __str__(self):
        return super().__str__()


class WebHook(WatchEvent):
    """Webhook base class.

    Makes the actual webhook trigger request.
    Checks allowed realms.

    A realm is just a functionality, that allows to restrict events to certain types of triggers.

    Example:
    Though a webhook can be configured to trigger in case of events A and B, event B should not be triggered in case of event A and vice versa.
    """

    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, name="", url="", url_safe="", realms: Tuple[str] = None):
        self.url = url
        self.url_safe = url_safe if url_safe else url
        super().__init__(name=name, description=f"To '{self.url_safe}'.", realms=realms)
        logger.debug(f"Webhook event URL '{self.url_safe}'.")
        logger.debug(f"Webhook event REALMS '{self.realms}'.")

    def trigger(self, data, realm=None, debug=False):
        if not self.allowed(realm):
            return
        logger.info(f"Event '{self.name}'. Trigger raw webhook: '{str(self)}' with '{data}'.")
        response = self._trigger(data=data, debug=debug)
        if response:
            help_text = re.sub("\n", "", response.text)
            logger.warn(
                f"Event '{self.name}'. Raw webhook response: '{response.status_code}', '{help_text[:25]}...{help_text[-25:]}'."
            )

    def __str__(self):
        return super().__str__()

    def _trigger(self, data=None, debug=False):
        if debug:
            logger.debug("[DEBUG]: Not triggering.")
            return None
        response = None
        try:
            response = requests.post(self.url, json=data, headers=self.HEADERS)
        except (requests.exceptions.MissingSchema, requests.exceptions.RequestException,) as e:
            logger.error(f"Event '{self.name}'. Error: '{str(e)}'.")
        if response is None:
            logger.error("Event '{self.name}'. No response.")
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
            logger.error(f"Event '{self.name}'. No info for trigger: '{str(self)}'.")
            return
        logger.info(f"Event '{self.name}'. Trigger mattermost webhook: '{str(self)}' with '{data}'.")
        data_ = {"text": f"{data}"}
        response = self._trigger(data=data_, debug=debug)
        if response is not None:
            help_text = re.sub("\n", "", response.text)
            logger.warn(
                f"Event '{self.name}'. Mattermost webhook response: '{response.status_code}', '{help_text[:25]}...{help_text[-25:]}'."
            )

    def __str__(self):
        return super().__str__()


class DockerCloudWebHook(WebHook):
    """Dockerhub webhook event.
    """

    URL = "https://hub.docker.com/api/build/v1/source/{source}/trigger/{trigger}/call/"

    def __init__(
        self, name="", source_branch="master", source_type="Branch", source="", trigger="", realms: Tuple[str] = None,
    ):
        self.source_branch = source_branch
        self.source_type = source_type
        super().__init__(
            name=name,
            url=self.URL.format(source=source, trigger=trigger),
            url_safe=self.URL.format(source="***", trigger="***"),
            realms=realms,
        )

    def trigger(self, data=None, realm=None, debug=False):
        if not super().allowed(realm):
            return
        if not self.source_branch or not self.source_type:
            logger.error(f"Event '{self.name}'. No info for trigger: '{str(self)}'.")
            return
        logger.info(
            f"Event '{self.name}'. Trigger dockercloud webhook for '{self.source_type}' '{self.source_branch}': '{str(self)}'."
        )
        data_ = {"source_type": self.source_type, "source_name": self.source_branch}

        response = self._trigger(data=data_, debug=debug)
        if response is not None:
            logger.warn(
                f"Event '{self.name}'. Dockercloud webhook response: '{response.status_code}', '{response.text}'."
            )

    def __str__(self):
        return super().__str__()


class EmailHook(WatchEvent):
    def __init__(
        self, name: str = "", email: message.Email = None, realms: Tuple[str] = None,
    ):
        self.email = email

        super().__init__(name=name, realms=realms)

    def _trigger(self, data: Optional[Union[dict, str]], debug=False):
        if debug:
            logger.debug("[DEBUG]: Not triggering.")
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
            logger.error(f"Event '{self.name}'. Error: '{str(e)}'.")
            return

    def __str__(self):
        return super().__str__() + f" With subject '{self.email.subject}' to '{self.email.recipients}'."


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
        tls: bool = True,
        realms: Tuple[str] = None,
    ):
        from .mail import simple

        email = simple.SimpleEmail(
            host=host,
            port=port,
            recipients=recipients,
            sender=sender,
            sender_name=sender_name,
            credentials=credentials,
            tls=tls,
        )
        if not email.subject:
            email.subject = name

        super().__init__(name=name, email=email, realms=realms)

    def trigger(self, data: Union[dict, str], realm=None, debug=False):
        if not super().allowed(realm):
            return
        logger.info(f"Event '{self.name}'. Trigger Simple email hook for: '{str(self)}'.")
        self._trigger(data=data, debug=debug)

    def __str__(self):
        return super().__str__()


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
        from .mail import aws_ses

        email = aws_ses.AwsSesEmail(recipients=recipients, sender=sender, sender_name=sender_name,)
        if not email.subject:
            email.subject = name

        super().__init__(name=name, email=email, realms=realms)

    def trigger(self, data: Union[dict, str], realm=None, debug=False):
        if not super().allowed(realm):
            return
        logger.info(f"Event '{self.name}'. Trigger AWS SES email hook for: '{str(self)}'.")
        self._trigger(data=data, debug=debug)

    def __str__(self):
        return super().__str__()
