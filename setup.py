from setuptools import setup

from _version import __version__


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
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
    ],
    install_requires=["requests>=2.22.0"],
    py_modules=["events"],
)
