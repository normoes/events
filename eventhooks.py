"""
Events

Events is supposed to be an event module which sends webhooks to:
* Mattermost
* Dockerhub

"""


import logging

import requests


logging.basicConfig()
log = logging.getLogger("Events")
log.setLevel(logging.INFO)


class WatchEvent:
    """Event base class.
    """

    def __init__(self):
        pass


class WebHook(WatchEvent):
    """Webhook base class.

    Makes the actual webhook trigger request.
    Checks alloweed realms.

    A realm is just a functionality, that allows to restrict events to certain types of triggers.

    Example:
    Though a webhook can be configured to trigger in case of events A and B, event B should not be triggered in case of event A and vice versa.
    """

    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, name="", url="", url_safe="", realms=None):
        self.name = name
        self.url = url
        self.url_safe = url_safe
        self.realms = realms
        log.debug(f"Webhook event URL '{self.url_safe}'.")
        log.debug(f"Webhook event REALMS '{self.realms}'.")
        super().__init__()

    def _trigger(self, data=None, debug=False):
        if debug:
            return None
        response = None
        try:
            response = requests.post(self.url, json=data, headers=self.HEADERS)
        except (requests.exceptions.MissingSchema) as e:
            log.error(f"Error: '{str(e)}'.")
        if not response:
            log.error("No response.")
            return None
        try:
            log.debug(f"[{response.status_code}], {response.json()}")
        except:
            log.debug(f"[{response.status_code}], {response.text}")

        return response

    def allowed(self, realm=None):
        """Check allowed realms.

        If no realms are configured, triggering the webhook is allowed.
        """

        allowed = not self.realms or realm in self.realms
        if not allowed:
            log.warning(f"Cannot trigger '{str(self)}'. '{realm}' not in '{self.realms}'.")
        return allowed

    def __str__(self):
        return self.name + ": " + self.url_safe


class MattermostWebHook(WebHook):
    """Mattermost webhook event.
    """

    URL = "{host}/hooks/{token}"

    def __init__(self, name="", host="", token="", realms=None):
        super().__init__(
            name=name,
            url=self.URL.format(host=host, token=token),
            url_safe=self.URL.format(host=host, token="***"),
            realms=realms,
        )

    def trigger(self, data, realm=None, debug=False):
        if not super().allowed(realm):
            return
        content = data.get("content", None)
        repo = None
        if content:
            repo = content.pop("repo", None)
        if not repo or not content:
            # trigger all builds
            log.error(f"No info for trigger: '{str(self)}'.")
            return
        log.warn(f"Mattermost webhook triggered for repo '{repo}': '{str(self)}'.")
        data_ = {"text": f"'{repo}' was tagged: '{content}'."}
        # trigger specific branch
        response = self._trigger(data=data_, debug=debug)
        if response:
            log.warn(
                f"Mattermost webhook reponse: '{response.status_code}', '{response.text}'."
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
        realms=None,
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
            log.error(f"No info for trigger: '{str(self)}'.")
            return
        log.warn(
            f"Dockercloud webhook triggered for branch '{self.source_branch}': '{str(self)}'."
        )
        data_ = {"source_type": self.source_type, "source_name": self.source_branch}

        response = self._trigger(data=data_, debug=debug)
        if response:
            log.warn(
                f"Dockercloud webhook reponse: '{response.status_code}', '{response.text}'."
            )

