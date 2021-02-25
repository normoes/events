# Events

`eventhooks` triggers webhooks for web services:
* `POST` web hook
* Mattermost
* Dockerhub

`eventhooks` sends emails:
* Simple emails (requires host, port, user and password)
    - With or without TLS.
* AWS SES emails (using `boto3`, requires AWS credentials)
    - Needs to be installed with `aws` extra: `pip install eventhooks[aws]`

`eventhooks` publishes to AMQP exchanges:
* AMQP (using `pika`).
    - Needs to be installed with `pika` extra: `pip install eventhooks[pika]`
* Install all dependencies:
   - `pip install eventhooks[pika,aws]`

**_Note_**:

Of course, events could do a lot more. If you have an idea, please just create an issue and describe it.

Additionally, events can be configured with relams.
Realms provide a context to an event and restrict the event action by caller origin.
Have a  look at **Understanding realms**.

## Idea

The idea of `eventhooks` is to have a single library that helps accomplishing certain tasks in case of certain events. The triggers can be anything, in fact - They entirely depend on you.

Examples:
* Send an email in case of a failed servcie on your server.
* Additinoally, push the log of the failed service onto an AMQP exchange.
* Trigger a Dockerhub build of one of your docker images in case a new push to a dependent project happened.
* Have a Mattermost bot send the notification about a finished job to your team members.
* Add the finished job onto a specific statistics queue on RabbtMQ.

## Configuration

For a more detailed configuration see further below.

There is a simple web hook:
* `WeHook`:
    - Uses `requests`.
    - Does a `POST` request to a given URL.
    - Sends `json` data.

There are two,more specific web hooks that require more detailed configuration like setting tokens in the URL:
* `MattermostWebHook`
    - Builds on top of `WebHook`, requires a mattermost `<token>`.
    - Uses URL format: `<host>/hooks/<token>`
* `DockerCloudWebHook`
    - Builds on top of `WebHook`, requires a docker hub `<source>` and `<trigger>`.
    - Uses URL format: `https://hub.docker.com/api/build/v1/source/<source>/trigger/<trigger>/call/`

There are two email hooks:
* `SimpleEmailHook`
    - Uses `smtplib` and requires host, port, user and password.
    - User and password are provided in the following format: `user:password` (see example below).
    - With port `25`, set `tls=False` to skip authentication.
* `AwsSesEmailHook`
    - Needs to be installed with `aws` extra: `pip install eventhooks[aws]`
    - Uses `boto3` and requires AWS credentials (AWS access key ID and AWS secret access key).
    - If not configured otherwise, please set the required AWS region using the environment variable `AWS_DEFAULT_REGION="eu-east-1"`.

There is a AMQP (e.g. RabbitMQ) hook:
* `RabbitMqHook`
    - Uses `pika` and requires host, user and password.
    - The default`vhost` is `/`.
    - The default configuration sends messages directly to queue `example_queue`.


### Web hooks
#### WebHook configuration

A `WebHook` can be configured like this:
```python
    from eventhooks.eventhooks import WebHook
    hit_alarm_endpoint = WebHook(
        name="",
        url="some.server.com",
    )
    # In case of some event:
    threshold = 80
    hit_alarm_endpoint.trigger(data={"event": hit_alarm_endpoint.name, "message": f"Reached '{80}'.", "area": "outside"})
```

#### MattermosWebtHook configuration

A `MattermostWebHook` can be configured like this:
```python
    from eventhooks.eventhooks import MattermostWebHook
    inform_about_job_status = MattermostWebHook(
        name="job_A_last_step",
        host="mattermost.server.com",
        token="<token>",
    )
    # In case of some event:
    job_finished = True
    inform_about_job_status.trigger(data={"event": inform_about_job_status.name, "message": f"Job completed: '{job_finished}'."})
```

#### DockerCloudWebHook configuration

A `DockerCloudWebHook` can be configured like this:
```python
    from eventhooks.eventhooks import DockerCloudWebHook
    dockercloud_trigger = DockerCloudWebHook(
        name="dockercloud_event",
        source_branch="master",
        source_type="Branch",
        source="<source>",
        trigger="<trigger>",
    )
    # In case of some event:
    found_new_tag = True
    if found_new_tag:
        dockercloud_trigger.trigger()
```

### Email hooks

#### SimpleEmailHook configuration

A `SimpleEmailHook` can be configured without TLS:
```python
    from eventhooks.eventhooks import SimpleEmailHook
    failed_service_mail = SimpleEmailHook(
        name="failed_service_checker",
        host="localhost",
        port=25,
        sender="someone@somwhere.com",
        sender_name="someone",
        recipients="mew@xyz.com, you@xyz.com",
        tls=False,
    )
    # In case of some event:
    # The event name ('failed_service_mail.name') will be used as email subject.
    failed_services = ["mongodb.service", "nginx.service", "cron.service"]
    email_body = {
        "name": failed_service_mail.name,
        "failed_services": failed_services,
    }

    failed_service_mail.trigger(data=email_body)
    # or simply
    failed_service_mail.trigger(data=",".join(failed_services))
```

A `SimpleEmailHook` can be configured with TLS:
```python
    from eventhooks.eventhooks import SimpleEmailHook
    simple_email_trigger = SimpleEmailHook(
        name="aws_simple_email_event",
        host="email-smtp.eu-west-1.amazonaws.com",
        port=587,
        credentials="user:password",
        sender="someone@somwhere.com",
        sender_name="someone",
        recipients=["mew@xyz.com", "you@xyz.com"],
    )
```

Some general email connection settings can be configured using environment variables:

| environment variable | description | default value |
|----------------------|-------------|---------------|
| `EVENT_MAIL_HOST` | Email server host. |  `"email-smtp.us-west-2.amazonaws.com"` |
| `EVENT_MAIL_PORT` | Email server port. | `587` |

**_Note_**:
* So far emails are sent in plain text only, no option for HTML.
* `TLS` is used by default and can be disabled using `tls=False` when initialising the `SimpleEmailHook`.
* If no email subject is configured using the environment variable `SUBJECT`, the `name` of the `SimpleEmailHook` will be used as the email's subject by default. Of course this can be changed later on:
```python
    # Set the email's subject.
    simple_email_trigger.email.subject = "Something else."
```

#### AwsSesEmailHook configuration

The `AwsSesEmailHook` can be configured like this:
```python
    from eventhooks.eventhooks import AwsSesEmailHook
    aws_ses_email_trigger = AwsSesEmailHook(
        name="aws_ses_email_event",
        sender="someone@somwhere.com",
        sender_name="someone",
        recipients=["me@peer.xyz"],
    )
```

Some general email connection settings can be configured using environment variables:

| environment variable | description | default value |
|----------------------|-------------|---------------|
| `EVENT_MAIL_HOST` | Email server host. |  `"email-smtp.us-west-2.amazonaws.com"` |
| `EVENT_MAIL_PORT` | Email server port. | `587` |

**_Note_**:
* So far emails are sent in plain text only, no option for HTML.
* If no email subject is configured using the environment variable `SUBJECT`, the `name` of the `AwsSesEmailHook` will be used as the email's subject by default. Of course this can be changed later on:
```python
    # Set the email's subject.
    aws_ses_email_trigger.email.subject = "Something else."
```

#### Email body

Like mentioned earlier (See example configurations above), every event is essentially triggered like this:
```python
    event.trigger(data="Found new tag for repo <some_github_repo>.")
```
This is also true for the `SimpleEmailHook` as well as `AwsSesEmailHook`.

**_Note_**:
* The `data` argument is used as the email's body text.

**_Note_** - The hook accepts `str` and `dict` as body text:
* `event.trigger(data="Some string")` (`str`)
* `event.trigger(data={"error": "Weird error.", "cause": "Human factor."})` (`dict`)
  - In this case, the JSON is indented.

Internally it works like this (simplified):
```python
    from typing import Union
    def trigger(data: Union[dict,str]):
        ...
        # Set the email body with the 'data' argument.
        email.body_text = data
        email.send_mail()
        ...
```

### RabbitMqHook configuration

The `RabbitMqHook` can be configured like this:
```python
    from eventhooks.eventhooks import RabbitMqHook
    rabbitmq_trigger = RabbitMqHook(
        name="failed_services_event",
        host="rabbitmq.company.com",
        user="username",
        password="secur3_!Password!",
        exchange="amqp.topic",
        routing_key='company.dep2.failed_services.serverA',
    )
```

## Understanding realm

Realms provide a context to an event and restrict the event action by caller origin.
* A realm can be a simple string, which is set on initialization of an event.
* Specifying a realm with an event, requires the realm to be passed with the `trigger()` to actually trigger the event.
* Not defining any realms will ignore the feature entirely.

**_Example_**:
All the examples given above have been defined without using realms.
Now, let's imagine, you have built a project that watches a github repository:
* In case of new pushes to `master`:
    - Trigger a dockerhub build.
* In case of a new tag:
    - Trigger a dockerhub build.
    - Notify team members by mail.

You can now define 3 events:
* `DockerCloudHook` (as can be seen above) to trigger the build of the `latest` docker image based on `master` of the github repository you watch.
* `DockerCloudHook` (as can be seen above) to trigger the build of a tagged docker image based on new tags of the github repository you watch.
* `SimpleEmailHook` (as can be seen above) in case of new tags in the github repository.
```python
    from eventhooks.eventhooks import DockerCloudWebHook
    from eventhooks.eventhooks import SimpleEmailHook

    latest_build= DockerCloudWebHook(
        ...,
    )
    tag_build= DockerCloudWebHook(
        ...,
    )
    email_team = SimpleEmailHook(
        ...,
        recipients=["developers@company.com", "head_of_devs@company.com"],
    )
    events = [latest_build, tag_build, email_team]
```

If you now just looped over the list of events in case of a new push to `master`, you would end up triggering the events defined for new tags as well.
```python
    # Loop over the list of events.
    def trigger_events(data: str=""):
        for event in events:
            event.trigger(data=data)

    trigger_events(data={"msg": "Push to master found."})
```

This is not what we want,

When using realms, the realm passed to an event's `trigger()` method is compared against the realms given on initialization. Only if the given realm is found in the list of realms the event is actually triggered.

```python
    from eventhooks.eventhooks import DockerCloudWebHook
    from eventhooks.eventhooks import SimpleEmailHook

    latest_build= DockerCloudWebHook(
        ...,
        realms = ["GITHUB_MASTER"],
    )
    tag_build= DockerCloudWebHook(
        ...,
        realms = ["GITHUB_TAG"],
    )
    email_team = SimpleEmailHook(
        ...,
        recipients=["developers@company.com", "head_of_devs@company.com"],
        realms = ["GITHUB_TAG"],
    )
    events = [latest_build, tag_build, email_team]
```

Now, when a new push to `master` is found, you would pass the configured realm `GITHUB_MASTER` as well. The 2 events preserved for new github repository tags are ignored - They do not support the given realm `GITHUB_MASTER`, only `GITHUB_TAG`.
```python
    # Loop over the list of events and pass realms.
    def trigger_events(data: str="", realm=None):
        for event in events:
            event.trigger(data=data, realm=realm)


    trigger_events(data={"msg": "Push to master found."}, realm="GITHUB_MASTER")
```
