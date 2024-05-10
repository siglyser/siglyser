# setup.py

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()


setup(
    name='siglyser',
    version='0.22',
    description='Signal processing library',
    author='Pushkar Sheth',
    author_email='siglyserdev@gmail.com',
    packages=find_packages(),
    install_requires=[
        # Add dependencies here.

        
    ],

    long_description=description,
    long_description_content_type="text/markdown",
)