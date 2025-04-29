from setuptools import setup, find_packages

setup(
    name="steampipe",
    version="0.0.95-dev",
    description="Remux and upload Steam video clips to YouTube",
    author="onemyndseye",
    author_email="you@example.com",
    packages=find_packages(),
    install_requires=[
        "requests",
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib"
    ],
    entry_points={
        "console_scripts": [
            "steampipe = steampipe.__main__:main"
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux"
    ],
)
