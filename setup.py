from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='forgts',
    version='0.1.0',
    author='Fernanda Aguirre Ruiz',
    description='A package that extracts formatting from Excel files and applies it to great_tables objects.',
    python_requires='>=3',
    license='MIT License',
    packages=find_packages(),
)