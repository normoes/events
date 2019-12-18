# Events

This is a module that provides events for:
* mattermost
* dockerhub

Events can trigger webhooks on the previously mentioned web services.

**_Note_**:

Of course, events could do a lot more. If you have an idea, please just create an issue and describe it.

Additionally events can be configured with relams.
Realms provide a context to an event and restrict the event action by caller origin.

Right now, there always needs to be a valid realm.
In the future, this can be optimized so giving no realm will always execute the event action.

## Example

I use this module in the [`github_repo_watcher`](https://github.com/normoes/github_repo_watcher).

To be brief, this `github_repo_watcher` checks a github repository for new commits to `master` and for new tags.

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
