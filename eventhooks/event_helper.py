import logging

from . import eventhooks


logger = logging.getLogger("EventHooks.EventhookFactory")


def eventhook_factory(event_name: str, config: dict):
    event_type = config.get("type", "")
    if event_type not in (
        "AwsSesEmailHook",
        "SimpleEmailHook",
        "WebHook",
        "MattermostWebHook",
        "DockerCloudWebHook",
        "RabbitMqHook",
    ):
        logger.warning(f"'eventhooks' type '{event_type}' is unknown.")
        return None

    data = {"name": event_name, "realms": config.get("realms", [])}
    try:
        class_ = getattr(eventhooks, event_type)
    except (AttributeError) as e:
        logger.error(f"Could not import 'eventhooks' type '{event_type}'. Error: {str(e)}.")
        return None
    logger.debug(f"Trying to configure '{event_type}' with '{config}'.")
    if event_type == "AwsSesEmailHook":
        data["sender"] = config.get("sender", "")
        data["sender_name"] = config.get("sender_name", "")
        data["recipients"] = config.get("recipients", [])
    elif event_type == "SimpleEmailHook":
        data["host"] = config.get("host", "")
        data["port"] = config.get("port", 0)
        data["credentials"] = config.get("credentials", "")
        data["sender"] = config.get("sender", "")
        data["sender_name"] = config.get("sender_name", "")
        data["recipients"] = config.get("recipients", [])
        data["tls"] = config.get("tls", True)
    elif event_type == "WebHook":
        data["url"] = config.get("webhook", "")
    elif event_type == "DockerCloudWebHook":
        data["source_branch"] = config.get("source_branch", "master")
        data["source_type"] = config.get("source_type", "Branch")
        data["source"] = config.get("source", "")
        data["trigger"] = config.get("trigger", "")
    elif event_type == "MattermostWebHook":
        data["host"] = config.get("host", "")
        data["token"] = config.get("token", "")
    elif event_type == "RabbitMqHook":
        data["host"] = config.get("host", "")
        data["vhost"] = config.get("vhost", "/")
        data["exchange"] = config.get("exchange", "")
        data["routing_key"] = config.get("routing_key", "example_queue")
        data["user"] = config.get("user", "")
        data["password"] = config.get("password", "")
    else:
        logger.warning(f"To be defined: 'eventhooks' type '{event_type}'.")
        return None

    return class_(**data)
