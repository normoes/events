import os
import sys

CREDENTIALS_DEFAULT = ""
SENDER_DEFAULT = ""
SENDER_NAME_DEFAULT = ""
BODY_TEST_DEFAULT = ""
CONFIGURATION_SET_DEFAULT = None
SUBJECT_DEFAULT = ""
RECIPIENTS_DEFAULT = ""


HOST_DEFAULT = "email-smtp.us-west-2.amazonaws.com"
PORT_DEFAULT = 587


# Email connection and message settings.
# AWS Lambda configuration.
if "SERVERTYPE" in os.environ and os.environ["SERVERTYPE"] == "AWS Lambda":
    import boto3
    from base64 import b64decode

    # AWS SES credentials expectedformat: "<user>:<password>"
    ENCRYPTED = os.getenv("CREDENTIALS", None)
    if ENCRYPTED:
        CREDENTIALS = bytes.decode(
            boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))[
                "Plaintext"
            ]
        )
    else:
        CREDENTIALS = CREDENTIALS_DEFAULT

    # Email message options.
    ENCRYPTED = os.getenv("SENDER", None)
    if ENCRYPTED:
        SENDER = bytes.decode(
            boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))[
                "Plaintext"
            ]
        )
    else:
        SENDER = SENDER_DEFAULT
    ENCRYPTED = os.getenv("SENDER_NAME", None)
    if ENCRYPTED:
        SENDER_NAME = bytes.decode(
            boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))[
                "Plaintext"
            ]
        )
    else:
        SENDER_NAME = SENDER_NAME_DEFAULT
    ENCRYPTED = os.getenv("RECIPIENTS", None)
    if ENCRYPTED:
        RECIPIENTS = bytes.decode(
            boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))[
                "Plaintext"
            ]
        )
    else:
        RECIPIENTS = RECIPIENTS_DEFAULT
    # [Optional] The name of configuration set to use for this message.
    # Used with '"X-SES-CONFIGURATION-SET' header.
    ENCRYPTED = os.getenv("CONFIGURATION_SET", None)
    if ENCRYPTED:
        CONFIGURATION_SET = bytes.decode(
            boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))[
                "Plaintext"
            ]
        )
    else:
        CONFIGURATION_SET = CONFIGURATION_SET_DEFAULT
    ENCRYPTED = os.getenv("SUBJECT", None)
    if ENCRYPTED:
        SUBJECT = bytes.decode(
            boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))[
                "Plaintext"
            ]
        )
    else:
        SUBJECT = SUBJECT_DEFAULT
    ENCRYPTED = os.getenv("BODY_TEXT", None)
    if ENCRYPTED:
        BODY_TEXT = bytes.decode(
            boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))[
                "Plaintext"
            ]
        )
    else:
        BODY_TEXT = BODY_TEST_DEFAULT
else:
    # AWS SES credentials expectedformat: "<user>:<password>"
    CREDENTIALS = os.getenv("CREDENTIALS", CREDENTIALS_DEFAULT)

    # Email message options.
    SENDER = os.getenv("SENDER", SENDER_DEFAULT)
    SENDER_NAME = os.getenv("SENDER_NAME", SENDER_NAME_DEFAULT)
    # Comma separated list of recipients.
    RECIPIENTS = os.getenv("RECIPIENTS", RECIPIENTS_DEFAULT)
    # [Optional] The name of configuration set to use for this message.
    # Used with '"X-SES-CONFIGURATION-SET' header.
    CONFIGURATION_SET = os.getenv("CONFIGURATION_SET", CONFIGURATION_SET_DEFAULT)
    SUBJECT = os.getenv("SUBJECT", SUBJECT_DEFAULT)
    BODY_TEXT = os.getenv("BODY_TEXT", BODY_TEST_DEFAULT)


# AWS SES region endpoint.
HOST = os.getenv("HOST", HOST_DEFAULT)
# AWS SES port.
PORT = int(os.getenv("PORT", PORT_DEFAULT))
try:
    PORT = int(PORT)
except ValueError:
    print(f"PORT is expected to be of type 'int', but value is '{PORT}'.")
    sys.exit(1)
