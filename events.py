"""
Events

This is a module that provides events for:
* mattermost
* dockerhub

Events can trigger webhooks on the previously mentioned web services.
"""

import logging

import requests


logging.basicConfig()
log = logging.getLogger("Events")
log.setLevel(logging.INFO)


class WatchEvent:
    def __init__(self, webhook=""):
        pass


class WebHook(WatchEvent):
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, name="", url="", url_safe="", realms=None):
        self.name = name
        self.url = url
        self.url_safe = url_safe
        self.realms = realms
        log.debug("Webhook event URL {}".format(self.url_safe))
        log.debug("Webhook event REALMS {}".format(self.realms))
        super().__init__()

    def _trigger(self, data=None, debug=False):
        if debug:
            return None
        # print(self)
        # return f"post {data} to  {self.url_safe}."
        response = None
        try:
            response = requests.post(self.url, json=data, headers=self.HEADERS)
        except (requests.exceptions.MissingSchema) as e:
            log.error(f"Error: '{str(e)}'")
        if not response:
            log.error("No response.")
            return None
        try:
            log.debug(f"[{response.status_code}], {response.json()}")
        except:
            log.debug(f"[{response.status_code}], {response.text}")

        return response

    def allowed(self, realm=None):
        if not self.realms:
            return False
        allowed = realm in self.realms
        if not allowed:
            log.warning(f"Cannot trigger {str(self)}. {realm} not in {self.realms}")
            return False
        return True

    def __str__(self):
        return self.name + ": " + self.url_safe


class MattermostWebHook(WebHook):
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
            log.error("no info for trigger: {}".format(str(self)))
            return
        log.warn(f"Mattermost webhook triggered for repo {repo}: {str(self)}")
        data_ = {"text": f"{repo} was tagged: {content}"}
        # trigger specific branch
        response = self._trigger(data=data_, debug=debug)
        if response:
            log.warn(
                f"Mattermost webhook reponse: {response.status_code}, {response.text}"
            )


class DockerCloudWebHook(WebHook):
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
            # trigger all builds
            log.error("no info for trigger: {}".format(str(self)))
            return
        log.warn(
            f"Dockercloud webhook triggered for branch {self.source_branch}: {str(self)}"
        )
        data_ = {"source_type": self.source_type, "source_name": self.source_branch}
        # trigger specific branch

        response = self._trigger(data=data_, debug=debug)
        if response:
            log.warn(
                f"Dockercloud webhook reponse: {response.status_code}, {response.text}"
            )


