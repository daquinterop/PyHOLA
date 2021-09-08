from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PyHOLA",
    version= '21.09',
    packages=find_packages(),
    description='A Python implementation to download sensor data using HOLOGRAM API',
    url='https://github.com/daquinterop/PyHOLA',
    author='Diego Quintero',
    author_email='dquintero@nevada.unr.edu',
    licence='MIT',
    long_description_content_type="text/markdown",
    long_description=long_description
)