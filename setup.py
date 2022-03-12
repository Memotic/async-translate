import setuptools
import os
import versioneer

# Setup Optional requirements
extras_require = {}
suffix_len = len("_requirements.txt")
dirs = os.walk("async_translate/providers")
next(dirs)  # ignore the base folder

for provider_dir in dirs:
    name = provider_dir[0].split('/')[-1]
    dependencies = []
    try:
        with open(os.path.join("async_translate/providers", name,
                               "requirements.txt")) as fh:
            dependencies = fh.read().splitlines()
    except FileNotFoundError:
        continue
    extras_require[name] = dependencies

with open("README.md") as fh:
    long_description = fh.read()

setuptools.setup(
    name="async_translate",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="William Hatcher",
    author_email="william@memotic.net",
    description="Multi-provider async translate API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Memotic/async-translate",
    packages=setuptools.find_packages(),
    extras_require=extras_require,
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
    python_requires='>=3.8',
)
