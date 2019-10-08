import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="phlobo",
    version="0.0.1",
    author="Florian Borchert",
    author_email="florian.borchert@hpi.de",
    description="A simple library for tumor staging from free-text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.hpi.de/florian.borchert/onco-staging-nlp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)