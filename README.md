# Events

This is a module that provides events for:
* mattermost
* dockerhub
* AWS SES emails

Events can trigger webhooks on the previously mentioned web services.

**_Note_**:

Of course, events could do a lot more. If you have an idea, please just create an issue and describe it.

Additionally events can be configured with relams.
Realms provide a context to an event and restrict the event action by caller origin.

Right now, there always needs to be a valid realm.
In the future, this can be optimized so giving no realm will always execute the event action.

## Example webhook

I use this module in the [`github_repo_watcher`](https://github.com/normoes/github_repo_watcher).

To be brief, the `github_repo_watcher` checks a github repository for new commits to `master` and for new tags.

Whenever a new commit or tag is found, 3 things happen:
* The commit and tag are stored in a database.
* A mattermost webhook is triggered (**mattermost event**).
  - **Only for tags.**
* A dockercloud webhook is triggered (**dockercloud event**).
  - **For both commits and tags.**

You can see, the `github_repo_watcher` is configured with 2 events:
* mattermost
* dockerhub

Additionally, the application supports 2 realms to restrict an event's action:
* `GITHUB_COMMIT_REALM = "github_commits"`
* `GITHUB_TAG_REALM = "github_tags"`
```python
    GITHUB_REALMS = {
        GITHUB_TAG_REALM: GITHUB_TAG_REALM,
        GITHUB_COMMIT_REALM: GITHUB_COMMIT_REALM,
    }
```
Here, the realms feature is used to restrict the mattermost event to only trigger the webhook for new tags - like mentioned before.

Imagine a mattermost event configuration like this:
```python
    mattermost_trigger = MattermostWebHook(
        name="mattermost_event",
        host=<some_mattermost_url>,
        token=<some_mattermost_token>,
        realms=(GITHUB_REALMS[GITHUB_TAG_REALM],),
    )
```

**_Note_**:

At this point, I leave out the configuration of other events. Just imagine, the `github_repo_watcher` is configured with a ton of events.

Now, imagine a new tag was found.

Obviously, the function which loops over all the events is called with the realm `GITHUB_TAG_REALM` (new github tag was found).

So, every event (mattermost, "a ton of events", ...) is essentially triggered like this:

```python
    event.trigger(data="Found new tag for repo <some_github_repo>.", realm=GITHUB_TAG_REALM)
```

Since the mattermost event is configured to be triggered in the `GITHUB_TAG_REALM` only, it will trigger the mattermost webhook.

And it won't be triggered if the configuration should look like this (using `GITHUB_COMMIT_REALM`):
```python
    mattermost_trigger = MattermostWebHook(
        ...
        realms=(GITHUB_REALMS[GITHUB_COMMIT_REALM],),
    )
```

## Example email hook

This is used in the [`github_repo_watcher`](https://github.com/normoes/github_repo_watcher) as well.

To get a basic understanding of the `github_repo_watcher` (used as an example) please refer to the point **Example webhook**.

There is only one email hook supported and tested right now:
* `AwsSesEmailHook`

It's possible that this hook is also working for other email servers, but I cannot say for sure, because I did not test it.

The email hook can be configured like this:
```python
    aws_ses_email_trigger = AwsSesEmailHook(
        name="aws_ses_email_event",
        realms=(GITHUB_REALMS[GITHUB_TAG_REALM],),
    )
```
### Configuration

The email connection and message need to be configured using environment variables.

The following configuration options exist;
* Email connection:

| environment variable | description | default value |
|----------------------|-------------|---------------|
| `HOST` | AWS SES server name.. |  `"email-smtp.us-west-2.amazonaws.com"` |
| `PORT` | AWS SES port. | `587` |
| `AWS_SES_CREDENTIALS` | AWS SES credentials (expected format: `user:password`). |  `""` |

* Email message:

| environment variable | description | default value |
|----------------------|-------------|---------------|
| `SENDER` | `From` email address (`someone@somewhere.com`). |  `""` |
| `SENDER_NAME` | `From` real name (`someone`). | `""` |
| `RECIPIENTS` | Comma separated recipients' email addresses (`some@nowhere.com, one@here.org`). |  `""` |
| `CONFIGURATION_SET` | [OPTIONAL] The name of configuration set to use for this message. | `None` |
| `SUBJECT` | Email subject. | `""` |
| `BODY_TEXT` | Email body. | `""` |

**_Note_**:
* So far emails are sent in plain text only.
* `TLS` is used by default.
* If no email subject is configured using the environment variable `SUBJECT`, the  name of the `AwsSesEmailHook` will be used as the email's subject by default. Of course this can be changed later on:
```python
    # Set the email's subject.
    aws_ses_email_trigger.email.subject = "Something else."
```


#### AWS Lambda

Please refer to the file `mail/environment_variables.py`.

With AWS Lambda functions some of the environment variables are expected to be encrypted:
* `AWS_SES_CREDENTIALS`
* `SENDER`
* `SENDER_NAME`
* `RECIPIENTS`
* `CONFIGURATION_SET`
* `SUBJECT`
* `BODY_TEXT`

### Email body

Like mentioned earlier (See **Example webhook**), every event is essentially triggered like this:
```python
    event.trigger(data="Found new tag for repo <some_github_repo>.", realm=GITHUB_TAG_REALM)
```
This is also true for the `AwsSesEmailHook`.

**_Note_**:
* The `data` argument is used as the email's body text.

**_Note_** - The hook accepts `str` and `dict` as body text:
* `event.trigger(data="Some string")` (`str`)
* `event.trigger(data={"error": "Weird error.", "cause": "Human factor."})` (`dict`)
  - In this case, the JSON is indented.
