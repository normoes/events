from setuptools import setup, find_packages

from eventhooks._version import __version__


setup(
    name="eventhooks",
    version=__version__,
    author="Norman Moeschter-Schenck",
    author_email="norman.moeschter@gmail.com",
    maintainer="Norman Moeschter-Schenck",
    maintainer_email="<norman.moeschter@gmail.com>",
    url="https://github.com/normoes/events",
    download_url=f"https://github.com/normoes/events/archive/{__version__}.tar.gz",
    description=("Trigger webhooks with events."),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
    ],
    install_requires=["requests>=2.24.0"],
    extras_require={
        "aws": ["boto3>=1.11.14"],
        # "git": ["GitPython==3.1.11"],
        "rabbit": ["pika>=1.2.0"],
    },
)
