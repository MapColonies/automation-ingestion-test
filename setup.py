import setuptools

with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mc-ingestion-testing",
    author="MC",
    description="Map colonies automation infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MapColonies/automation-ingestion-test.git",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
