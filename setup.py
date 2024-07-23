from setuptools import find_packages, setup
from os import path
from codecs import open

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='simple_di_container',
    packages=find_packages(include=['simple_di_container']),
    version='0.1.0',
    description='Simple Dependency Injection Container implementation. Only singleton lifetime and resolve dependencies from constructor',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Klabukov Erik',
    license='MIT'
)
