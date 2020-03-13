import os
import sys


# Email connection and message settings.
# AWS Lambda configuration.
if "SERVERTYPE" in os.environ and os.environ["SERVERTYPE"] == "AWS Lambda":
    import boto3
    from base64 import b64decode

    # AWS SES credentials expectedformat: "<user>:<password>"
    ENCRYPTED = os.environ["AWS_SES_CREDENTIALS"]
    AWS_SES_CREDENTIALS = bytes.decode(
        boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))["Plaintext"]
    )

    # Email message options.
    ENCRYPTED = os.environ["SENDER"]
    SENDER = bytes.decode(
        boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))["Plaintext"]
    )
    ENCRYPTED = os.environ["SENDER_NAME"]
    SENDER_NAME = bytes.decode(
        boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))["Plaintext"]
    )
    ENCRYPTED = os.environ["RECIPIENTS"]
    RECIPIENTS = bytes.decode(
        boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))["Plaintext"]
    )
    # [Optional] The name of configuration set to use for this message.
    # Used with '"X-SES-CONFIGURATION-SET' header.
    ENCRYPTED = os.environ["CONFIGURATION_SET"]
    CONFIGURATION_SET = bytes.decode(
        boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))["Plaintext"]
    )
    ENCRYPTED = os.environ["SUBJECT"]
    SUBJECT = bytes.decode(
        boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))["Plaintext"]
    )
    ENCRYPTED = os.environ["BODY_TEXT"]
    BODY_TEXT = bytes.decode(
        boto3.client("kms").decrypt(CiphertextBlob=b64decode(ENCRYPTED))["Plaintext"]
    )
else:
    # AWS SES credentials expectedformat: "<user>:<password>"
    AWS_SES_CREDENTIALS = os.getenv("AWS_SES_CREDENTIALS", "")

    # Email message options.
    SENDER = os.getenv("SENDER", "")
    SENDER_NAME = os.getenv("SENDER_NAME", "")
    # Comma separated list of recipients.
    RECIPIENTS = os.getenv("RECIPIENTS", "")
    # [Optional] The name of configuration set to use for this message.
    # Used with '"X-SES-CONFIGURATION-SET' header.
    CONFIGURATION_SET = os.getenv("CONFIGURATION_SET", None)
    SUBJECT = os.getenv("SUBJECT", "")
    BODY_TEXT = os.getenv("BODY_TEXT", "")


# AWS SES region endpoint.
HOST = os.getenv("HOST", "email-smtp.us-west-2.amazonaws.com")
# AWS SES port.
PORT = int(os.getenv("PORT", 587))
try:
    PORT = int(PORT)
except ValueError:
    print(f"PORT is expected to be of type 'int', but value is '{PORT}'.")
    sys.exit(1)
