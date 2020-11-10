from setuptools import setup

setup(
    name="phnb",
    version="0.0.1",
    packages=["phnb"],
    entry_points={
        "console_scripts": [
            "phnb = phnb.__main__:main"
        ]
    },
)

