# 2021-02-26
* Optimized logging.
* Added `eventhooks` factory for more dynamic eventhook creation.
* Add `extras_require` `ImportError`.

# 2021-02-25
* Convert AMQP message to `str` from `dict`.

# 2021-02-23
* Removed environment variables for email configuration, leaving only `EVENT_MAIL_HOST` and `EVENT_MAIL_PORT`.
* Added support for sending emails without TLS.
* Added `RabbitMqHook` (AMQP).
* Moved `eventhooks` into the `eventhooks` package: `from eventhooks import eventhooks`.
* Restructured the code to allow parameterized package installations using `extras_require` in `setup.py`.
* Updated README.
