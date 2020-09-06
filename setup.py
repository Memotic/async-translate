import setuptools

with open("requirements.txt") as fh:
    requirements = fh.read().splitlines()


with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async_translate",
    version="0.0.1",
    author="William Hatcher",
    author_email="william@memotic.net",
    description="Multi-provider async translate API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Memotic/async-translate",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
    python_requires='>=3.8',
)