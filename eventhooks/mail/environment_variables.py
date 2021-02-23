import os
import sys

HOST_DEFAULT = "email-smtp.us-west-2.amazonaws.com"
PORT_DEFAULT = 587

# AWS SES region endpoint.
HOST = os.getenv("EVENT_MAIL_HOST", HOST_DEFAULT)
# AWS SES port.
PORT = int(os.getenv("EVENT_MAIL_PORT", PORT_DEFAULT))
try:
    PORT = int(PORT)
except ValueError:
    print(f"PORT is expected to be of type 'int', but value is '{PORT}'.")
    sys.exit(1)
