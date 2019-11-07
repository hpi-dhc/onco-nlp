import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="onconlp",
    version="0.0.1",
    author="Florian Borchert",
    author_email="florian.borchert@hpi.de",
    description="A simple library for medical information extraction from free-text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.hpi.de/florian.borchert/onconlp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'nose2',
        'spacy == 2.1.0',
        'de_core_news_sm @ https://github.com/explosion/spacy-models/releases/download/de_core_news_sm-2.1.0/de_core_news_sm-2.1.0.tar.gz',
        'en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz'
    ],
    python_requires='>=3.6',
)