import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="role-pattern-nlp",
    version="0.0.3",
    author="Nicholas Morley",
    author_email="nick.morley111@gmail.com",
    description=" Build and match patterns for semantic role labelling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyclecycle/role-pattern-nlp",
    packages=setuptools.find_packages(),
    install_requires=[
        'spacy',
        'spacy-pattern-builder',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
